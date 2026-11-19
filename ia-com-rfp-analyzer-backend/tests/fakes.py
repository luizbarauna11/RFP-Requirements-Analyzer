"""Dublês de teste."""

from __future__ import annotations

from typing import Any

from rfp_analyzer.domain.models import LLMUsage
from rfp_analyzer.llm.gateway import LLMUnavailableError


class FakeGateway:
    """Dublê do LLM: responde por tarefa com função configurável e registra os prompts recebidos."""

    def __init__(self, handlers: dict[str, Any]) -> None:
        self.handlers = handlers
        self.usage = LLMUsage()
        self.prompts: list[tuple[str, str]] = []

    def complete_json(self, *, system: str, user: str, task: str) -> dict[str, Any]:
        self.prompts.append((task, user))
        handler = self.handlers.get(task)
        if handler is None or handler == "fail":
            raise LLMUnavailableError(task)
        self.usage.calls += 1
        self.usage.prompt_tokens += 100
        result: dict[str, Any] = handler(user) if callable(handler) else handler
        return result
