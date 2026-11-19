"""Gateway LLM (Ports & Adapters).

- Porta `LLMGateway`: o pipeline só conhece esta interface → testes usam fakes, provider é trocável.
- Adapter `LiteLLMGateway`: Groq como primário via LiteLLM (router obrigatório da stack), com
  retry + backoff, fallback de modelo, cache em disco, self-correction de JSON e circuit breaker
  de custo por análise.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from pathlib import Path
from typing import Any, Protocol

from ..config import Settings
from ..domain.models import LLMUsage
from ..observability import log_event

logger = logging.getLogger(__name__)

NON_RETRYABLE = ("Authentication", "PermissionDenied", "BadRequest", "NotFound", "ContentPolicy")


class LLMUnavailableError(RuntimeError):
    """Todos os modelos falharam — pipeline cai para modo heurístico (degradação graciosa)."""


class BudgetExceededError(LLMUnavailableError):
    """Circuit breaker de custo: limite de tokens por análise atingido."""


class LLMGateway(Protocol):
    usage: LLMUsage

    def complete_json(self, *, system: str, user: str, task: str) -> dict[str, Any]: ...


def parse_json_payload(content: str) -> dict[str, Any]:
    cleaned = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.MULTILINE).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Resposta sem objeto JSON")
    data = json.loads(cleaned[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError("JSON raiz não é objeto")
    return data


class _DiskCache:
    def __init__(self, directory: Path, enabled: bool) -> None:
        self.directory, self.enabled = directory, enabled
        if enabled:
            directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def key(*parts: str) -> str:
        return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()

    def get(self, key: str) -> dict[str, Any] | None:
        path = self.directory / f"{key}.json"
        if self.enabled and path.exists():
            return json.loads(path.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
        return None

    def set(self, key: str, value: dict[str, Any]) -> None:
        if self.enabled:
            (self.directory / f"{key}.json").write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


class LiteLLMGateway:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.usage = LLMUsage()
        self.cache = _DiskCache(settings.llm_cache_dir, settings.llm_cache_enabled)
        self.models = [m for m in (settings.llm_primary_model, settings.llm_fallback_model) if m]

    # ------------------------------------------------------------------ API pública
    def complete_json(self, *, system: str, user: str, task: str) -> dict[str, Any]:
        cache_key = self.cache.key(self.settings.llm_primary_model, system, user)
        if (cached := self.cache.get(cache_key)) is not None:
            self.usage.cached_calls += 1
            return cached

        if self.usage.total_tokens >= self.settings.llm_max_tokens_per_analysis:
            raise BudgetExceededError(f"Orçamento de {self.settings.llm_max_tokens_per_analysis} tokens atingido")

        messages: list[dict[str, str]] = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        for index, model in enumerate(self.models):
            try:
                result = self._complete_with_self_correction(model, messages, task)
                if index > 0:
                    self.usage.fallback_used = True
                self.cache.set(cache_key, result)
                return result
            except Exception as exc:
                self.usage.errors.append(f"{task}:{model}:{type(exc).__name__}")
                logger.warning("llm_model_failed", extra={"extra_fields": {"model": model, "task": task,
                                                                             "error": type(exc).__name__}})
        raise LLMUnavailableError(f"Nenhum modelo disponível para a tarefa '{task}'")

    # ------------------------------------------------------------------ internos
    def _complete_with_self_correction(
        self, model: str, messages: list[dict[str, str]], task: str
    ) -> dict[str, Any]:
        content = self._call(model, messages, task)
        try:
            return parse_json_payload(content)
        except (ValueError, json.JSONDecodeError) as err:
            # Self-correction: devolve o erro ao modelo uma única vez
            retry_messages = [*messages, {"role": "assistant", "content": content},
                              {"role": "user", "content": f"JSON inválido ({err}). Responda SOMENTE o JSON corrigido."}]
            return parse_json_payload(self._call(model, retry_messages, f"{task}:self_correction"))

    def _call(self, model: str, messages: list[dict[str, str]], task: str) -> str:
        import litellm  # import tardio: testes e modo offline não carregam a lib

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": self.settings.llm_temperature,
            "timeout": self.settings.llm_timeout_seconds,
            "response_format": {"type": "json_object"},
            "metadata": {"task": task},
        }
        if model.startswith("groq/") and self.settings.groq_api_key is not None:
            kwargs["api_key"] = self.settings.groq_api_key.get_secret_value()

        attempts = self.settings.llm_max_retries + 1
        for attempt in range(attempts):
            start = time.perf_counter()
            try:
                response = litellm.completion(**kwargs)
            except Exception as exc:
                if any(tag in type(exc).__name__ for tag in NON_RETRYABLE) or attempt == attempts - 1:
                    raise
                time.sleep(2**attempt)  # backoff exponencial: 1s, 2s, 4s...
                continue
            usage = getattr(response, "usage", None)
            self.usage.calls += 1
            self.usage.prompt_tokens += int(getattr(usage, "prompt_tokens", 0) or 0)
            self.usage.completion_tokens += int(getattr(usage, "completion_tokens", 0) or 0)
            if model not in self.usage.models_used:
                self.usage.models_used.append(model)
            log_event(logger, "llm_call", task=task, model=model, attempt=attempt + 1,
                      latency_ms=round((time.perf_counter() - start) * 1000),
                      prompt_tokens=getattr(usage, "prompt_tokens", None),
                      completion_tokens=getattr(usage, "completion_tokens", None))
            return str(response.choices[0].message.content or "")
        raise LLMUnavailableError("unreachable")  # pragma: no cover
