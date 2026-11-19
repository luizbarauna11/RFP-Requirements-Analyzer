"""Logs estruturados (JSON) com trace_id + inicialização opcional do OpenLIT (padrão corporativo)."""

from __future__ import annotations

import contextvars
import json
import logging
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from .config import Settings

trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "trace_id": trace_id_var.get(),
        }
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            payload.update(extra)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())
    for noisy in ("LiteLLM", "litellm", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def log_event(logger: logging.Logger, msg: str, **fields: Any) -> None:
    logger.info(msg, extra={"extra_fields": fields})


@contextmanager
def timed_step(logger: logging.Logger, step: str) -> Iterator[None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        log_event(logger, "pipeline_step", step=step, duration_ms=round((time.perf_counter() - start) * 1000, 1))


def setup_tracing(settings: Settings) -> bool:
    """Inicializa OpenLIT ANTES de qualquer chamada LLM (instrumenta LiteLLM automaticamente).

    Só ativa quando há endpoint OTLP configurado e o extra `obs` está instalado.
    """
    if not settings.otel_exporter_otlp_endpoint:
        return False
    try:
        import openlit
    except ImportError:
        logging.getLogger(__name__).warning("openlit não instalado — tracing LLM desativado")
        return False
    openlit.init(
        application_name=settings.otel_service_name.rsplit("-v", 1)[0],
        environment=settings.app_env,
        disable_batch=settings.app_env == "development",
    )
    return True
