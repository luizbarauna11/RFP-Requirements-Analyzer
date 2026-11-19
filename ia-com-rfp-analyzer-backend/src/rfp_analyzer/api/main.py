"""API REST (FastAPI). Exposta internamente atrás do Kong (rate limit + auth SSO) — ver docs/02-arquitetura.md."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import PlainTextResponse

from .. import __version__
from ..config import get_settings
from ..domain.models import AnalysisResult
from ..ingestion.loaders import UnsupportedDocumentError, load_bytes
from ..observability import setup_logging, setup_tracing
from ..pipeline.orchestrator import analyze_text
from ..reporting import render_markdown

settings = get_settings()
setup_logging(settings.log_level)
setup_tracing(settings)  # OpenLIT antes de qualquer chamada LLM

app = FastAPI(
    title="RFP Requirements Analyzer",
    version=__version__,
    description="Extração, classificação e análise estratégica de requisitos de RFP com IA (Groq via LiteLLM).",
    docs_url="/docs",
)


@app.get("/health", tags=["ops"])
def health() -> dict[str, str]:
    """Liveness: o processo está de pé."""
    return {"status": "ok", "version": __version__}


@app.get("/ready", tags=["ops"])
def ready(deep: bool = False) -> dict[str, Any]:
    """Readiness. `deep=true` faz um ping real (poucos tokens) no LLM — chave configurada ≠ provider respondendo."""
    info: dict[str, Any] = {"status": "ready", "llm_configured": settings.llm_ready,
                            "primary_model": settings.llm_primary_model, "fallback_model": settings.llm_fallback_model}
    if deep and settings.llm_ready:
        from ..llm.gateway import LiteLLMGateway, LLMUnavailableError

        gw = LiteLLMGateway(settings.model_copy(update={"llm_cache_enabled": False}))
        try:
            gw.complete_json(system="Responda apenas JSON.", user='Responda {"pong": true}', task="healthcheck")
            info["llm_reachable"] = True
        except LLMUnavailableError:
            info["llm_reachable"] = False
            info["status"] = "degraded"  # serviço continua útil em modo determinístico
    return info


async def _read_upload(file: UploadFile) -> tuple[str, str]:
    content = await file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"Arquivo excede {settings.max_upload_mb} MB")
    filename = file.filename or "documento.txt"
    try:
        return load_bytes(content, filename), filename
    except UnsupportedDocumentError as exc:
        raise HTTPException(415, str(exc)) from exc


@app.post("/v1/analyses", response_model=AnalysisResult, tags=["análise"])
async def create_analysis(
    file: Annotated[UploadFile, File(description="RFP em .txt, .md, .pdf ou .docx")],
    use_llm: Annotated[bool, Query(description="false = modo determinístico, sem custo de tokens")] = True,
) -> AnalysisResult:
    text, filename = await _read_upload(file)
    if not text.strip():
        raise HTTPException(422, "Documento sem texto extraível (PDF escaneado? use OCR antes).")
    return await run_in_threadpool(analyze_text, text, filename, settings=settings, use_llm=use_llm)


@app.post("/v1/analyses/report", response_class=PlainTextResponse, tags=["análise"])
async def create_report(
    file: Annotated[UploadFile, File()],
    use_llm: Annotated[bool, Query()] = True,
) -> str:
    result = await create_analysis(file, use_llm)
    return render_markdown(result)
