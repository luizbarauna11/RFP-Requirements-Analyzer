"""Orquestrador do pipeline (cada etapa com responsabilidade única — sem 'God Agent').

    Ingestão → Guardrails (PII + injection) → Extração → Enriquecimento → Análise → Resumo → Resultado
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import UTC, datetime

from ..config import Settings, get_settings
from ..domain.models import AnalysisResult, LLMUsage
from ..ingestion.segmenter import extract_title
from ..llm.gateway import LiteLLMGateway, LLMGateway
from ..observability import log_event, timed_step, trace_id_var
from ..security.pii import detect_prompt_injection, redact_pii
from .analyze import compute_kpis, consolidate_questions, find_cross_risks, find_gaps
from .enrich import enrich_requirements
from .extract import extract_requirements
from .summarize import build_summary

logger = logging.getLogger(__name__)


def build_gateway(settings: Settings, use_llm: bool = True) -> LLMGateway | None:
    if not use_llm or not settings.llm_ready:
        return None
    return LiteLLMGateway(settings)


def analyze_text(text: str, document_name: str, *, settings: Settings | None = None,
                 gateway: LLMGateway | None = None, use_llm: bool = True) -> AnalysisResult:
    settings = settings or get_settings()
    if gateway is None and use_llm:
        gateway = build_gateway(settings, use_llm)
    trace_id = uuid.uuid4().hex
    token = trace_id_var.set(trace_id)
    try:
        title = extract_title(text)
        security_flags: list[str] = []

        with timed_step(logger, "guardrails"):
            injections = detect_prompt_injection(text)
            if injections:
                security_flags.append(f"possivel_prompt_injection:{len(injections)}_padroes")
            llm_text = text
            if settings.pii_redaction_enabled:
                llm_text, report = redact_pii(text)
                if report.total:
                    security_flags.append(f"pii_mascarada:{report.counts}")

        with timed_step(logger, "extract"):
            # Extração usa o texto mascarado; requisitos determinísticos mantêm o texto original.
            requirements = extract_requirements(llm_text if gateway else text, gateway, settings)
            redacted_lookup = {r.code: redact_pii(r.text)[0] if settings.pii_redaction_enabled else r.text
                               for r in requirements}

        with timed_step(logger, "enrich"):
            requirements = enrich_requirements(requirements, gateway, settings, redacted_lookup, title)

        with timed_step(logger, "analyze"):
            gaps = find_gaps(requirements, text)
            risks = find_cross_risks(requirements, gaps)
            questions = consolidate_questions(requirements, gaps)
            kpis = compute_kpis(requirements, gaps, risks)

        with timed_step(logger, "summarize"):
            summary = build_summary(title, requirements, gaps, risks, kpis, gateway, settings)

        usage = gateway.usage if gateway is not None else LLMUsage(degraded_mode=True)
        if gateway is None:
            usage.errors.append("llm_desativado_ou_sem_credencial")

        result = AnalysisResult(
            analysis_id=uuid.uuid4().hex[:12], trace_id=trace_id, generated_at=datetime.now(UTC),
            document_name=document_name, document_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            title=title, requirements=requirements, gaps=gaps, cross_risks=risks, questions=questions,
            summary=summary, kpis=kpis, usage=usage, security_flags=security_flags,
            prompt_versions={"enrich_requirements": "1.0.0", "extract_requirements": "1.0.0",
                             "executive_summary": "1.0.0"},
        )
        log_event(logger, "analysis_completed", analysis_id=result.analysis_id, requirements=len(requirements),
                  gaps=len(gaps), risks=len(risks), tokens=usage.total_tokens, degraded=usage.degraded_mode)
        return result
    finally:
        trace_id_var.reset(token)
