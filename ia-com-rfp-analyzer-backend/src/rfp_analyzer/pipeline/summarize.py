"""Etapa 4 — Resumo executivo + sinal INDICATIVO de bid (human-in-the-loop: decisão é do comitê)."""

from __future__ import annotations

import json
import logging

from pydantic import ValidationError

from ..config import Settings
from ..domain.models import CrossRisk, ExecutiveSummary, Gap, Level, Requirement
from ..llm.gateway import LLMGateway, LLMUnavailableError
from ..llm.prompts import load_prompt
from ..security.pii import neutralize_delimiters

logger = logging.getLogger(__name__)


def heuristic_summary(title: str, reqs: list[Requirement], gaps: list[Gap], risks: list[CrossRisk],
                      kpis: dict[str, object]) -> ExecutiveSummary:
    high_gaps = [g for g in gaps if g.severity is Level.ALTA]
    high_risks = [r for r in risks if r.severity is Level.ALTA]
    if len(high_gaps) >= 2 and any(g.topic.startswith("Volumetria") for g in high_gaps):
        signal, why = "INDEFINIDO", "faltam dados essenciais para precificar (volumetria e/ou penalidades)"
    elif high_risks:
        signal, why = "GO_COM_RESSALVAS", "o escopo é aderente a serviços gerenciados, mas há riscos altos a mitigar"
    else:
        signal, why = "GO", "não foram identificados riscos altos nas regras de análise"
    cats = kpis.get("por_categoria", {})
    return ExecutiveSummary(
        overview=(f"A RFP '{title}' contém {len(reqs)} itens analisados, distribuídos em "
                  f"{len(cats) if isinstance(cats, dict) else 0} categorias. Foram identificadas {len(gaps)} lacunas "
                  f"de informação e {len(risks)} riscos cruzados entre requisitos. "
                  f"Índice de clareza: {kpis.get('indice_clareza')}/100."),
        bid_signal=signal,  # type: ignore[arg-type]
        rationale=f"Sinal calculado por regras determinísticas: {why}.",
        key_risks=[r.title for r in sorted(risks, key=lambda r: r.severity != Level.ALTA)][:5],
        next_steps=[
            "Enviar ao cliente as perguntas de esclarecimento de prioridade ALTA",
            "Montar premissas de precificação explícitas para cada lacuna de prioridade ALTA",
            "Validar a matriz de requisitos com as áreas responsáveis (coluna 'Área')",
            "Preencher o status de aderência (Atende/Parcial/Não atende) na matriz",
            "Levar o sinal de bid ao comitê de pré-vendas com os riscos mitigados",
        ],
        source="heuristic",
    )


def build_summary(title: str, reqs: list[Requirement], gaps: list[Gap], risks: list[CrossRisk],
                  kpis: dict[str, object], gateway: LLMGateway | None, settings: Settings) -> ExecutiveSummary:
    fallback = heuristic_summary(title, reqs, gaps, risks, kpis)
    if gateway is None:
        return fallback
    digest = {
        "kpis": kpis,
        "lacunas": [{"topico": g.topic, "severidade": g.severity, "status": g.status} for g in gaps],
        "riscos_cruzados": [{"titulo": r.title, "severidade": r.severity, "descricao": r.description} for r in risks],
        "requisitos_criticos": [{"codigo": r.code, "texto": r.text} for r in reqs
                                if r.enrichment and r.enrichment.criticality is Level.ALTA][:20],
        "sinal_por_regras": fallback.bid_signal,
    }
    prompt = load_prompt(settings.prompts_dir, "executive_summary")
    system, user = prompt.render(title=neutralize_delimiters(title),
                                 analysis_json=neutralize_delimiters(json.dumps(digest, ensure_ascii=False, default=str)))
    try:
        data = gateway.complete_json(system=system, user=user, task="executive_summary")
        return ExecutiveSummary(**{**data, "source": "llm"})
    except LLMUnavailableError:
        gateway.usage.degraded_mode = True
    except (ValidationError, TypeError) as exc:
        logger.warning("invalid_summary", extra={"extra_fields": {"error": str(exc)[:200]}})
    return fallback
