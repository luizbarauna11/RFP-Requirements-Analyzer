"""Testa o adapter LiteLLM sem rede: litellm.completion é substituído por um dublê."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import litellm
import pytest
from pydantic import SecretStr

from rfp_analyzer.config import Settings
from rfp_analyzer.llm.gateway import BudgetExceededError, LiteLLMGateway, LLMUnavailableError, parse_json_payload


class RateLimitError(Exception):
    pass


class AuthenticationError(Exception):
    pass


def _response(content: str) -> Any:
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
                           usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5))


@pytest.fixture
def gw_settings(tmp_path: Path) -> Settings:
    return Settings(_env_file=None, groq_api_key=SecretStr("gsk_test"), llm_cache_dir=tmp_path / "c",
                    llm_max_retries=1)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("rfp_analyzer.llm.gateway.time.sleep", lambda _: None)


def test_parse_json_strips_markdown_fences() -> None:
    assert parse_json_payload('```json\n{"a": 1}\n```') == {"a": 1}


def test_retry_then_fallback_then_cache(monkeypatch: pytest.MonkeyPatch, gw_settings: Settings) -> None:
    calls: list[str] = []

    def fake_completion(**kwargs: Any) -> Any:
        calls.append(kwargs["model"])
        assert kwargs["api_key"] == "gsk_test"
        assert kwargs["response_format"] == {"type": "json_object"}
        if kwargs["model"] == gw_settings.llm_primary_model:
            raise RateLimitError("429")
        return _response('{"ok": true}')

    monkeypatch.setattr(litellm, "completion", fake_completion)
    gw = LiteLLMGateway(gw_settings)
    assert gw.complete_json(system="s", user="u", task="t") == {"ok": True}
    assert calls == [gw_settings.llm_primary_model] * 2 + [gw_settings.llm_fallback_model]  # 1 retry + fallback
    assert gw.usage.fallback_used and gw.usage.calls == 1 and gw.usage.total_tokens == 15

    assert gw.complete_json(system="s", user="u", task="t") == {"ok": True}  # cache
    assert gw.usage.cached_calls == 1 and len(calls) == 3


def test_auth_error_is_not_retried(monkeypatch: pytest.MonkeyPatch, gw_settings: Settings) -> None:
    calls: list[str] = []

    def fake_completion(**kwargs: Any) -> Any:
        calls.append(kwargs["model"])
        raise AuthenticationError("401")

    monkeypatch.setattr(litellm, "completion", fake_completion)
    with pytest.raises(LLMUnavailableError):
        LiteLLMGateway(gw_settings).complete_json(system="s", user="u", task="t")
    assert len(calls) == 2  # uma por modelo, sem retry


def test_self_correction_of_invalid_json(monkeypatch: pytest.MonkeyPatch, gw_settings: Settings) -> None:
    answers = iter(["isto não é json", '{"fixed": 1}'])
    monkeypatch.setattr(litellm, "completion", lambda **_: _response(next(answers)))
    assert LiteLLMGateway(gw_settings).complete_json(system="s", user="u", task="t") == {"fixed": 1}


def test_budget_circuit_breaker(monkeypatch: pytest.MonkeyPatch, gw_settings: Settings) -> None:
    monkeypatch.setattr(litellm, "completion", lambda **_: _response('{"a": 1}'))
    gw = LiteLLMGateway(gw_settings.model_copy(update={"llm_max_tokens_per_analysis": 10}))
    gw.complete_json(system="s", user="u1", task="t")
    with pytest.raises(BudgetExceededError):
        gw.complete_json(system="s", user="u2", task="t")
