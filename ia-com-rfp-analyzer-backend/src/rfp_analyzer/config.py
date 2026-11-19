"""Configuração 12-factor: tudo via variáveis de ambiente (ConfigMap/Secret em K8s, .env em dev)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PACKAGE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Aplicação -----------------------------------------------------------------------------
    app_env: str = "development"  # development | qa | production
    log_level: str = "INFO"
    max_upload_mb: int = 10

    # --- LLM (Groq via LiteLLM) ----------------------------------------------------------------
    llm_enabled: bool = True
    llm_primary_model: str = "groq/llama-3.3-70b-versatile"
    llm_fallback_model: str | None = "groq/llama-3.1-8b-instant"
    llm_timeout_seconds: int = 25  # < timeout do ingress, para o fallback ter tempo de rodar
    llm_temperature: float = 0.1
    llm_max_retries: int = 2  # tentativas extras por modelo (backoff 1s, 2s)
    llm_batch_size: int = 8  # requisitos por chamada de enriquecimento
    llm_max_tokens_per_analysis: int = 120_000  # circuit breaker de custo (FinOps)
    llm_cache_enabled: bool = True
    llm_cache_dir: Path = Path(".cache/llm")
    groq_api_key: SecretStr | None = None  # Secret K8s — nunca em ConfigMap/repo

    # --- Pipeline ------------------------------------------------------------------------------
    min_coded_requirements: int = 3  # abaixo disso, ativa extração por LLM (RFP sem códigos)
    extraction_chunk_chars: int = 6_000
    grounding_min_ratio: float = 0.85  # anti-alucinação: % do trecho que precisa existir no doc

    # --- Segurança -----------------------------------------------------------------------------
    pii_redaction_enabled: bool = True

    # --- Observabilidade -----------------------------------------------------------------------
    otel_service_name: str = "rfp-analyzer-v1"
    otel_exporter_otlp_endpoint: str | None = None

    prompts_dir: Path = PACKAGE_DIR / "prompts"

    @property
    def llm_ready(self) -> bool:
        """LLM só é usado se habilitado E com credencial (ou provider não-Groq configurado)."""
        if not self.llm_enabled:
            return False
        uses_groq = self.llm_primary_model.startswith("groq/")
        return (not uses_groq) or self.groq_api_key is not None


@lru_cache
def get_settings() -> Settings:
    return Settings()
