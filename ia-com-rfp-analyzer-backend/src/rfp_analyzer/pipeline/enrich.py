"""Etapa 2 — Enriquecimento estratégico por LLM em lotes, com validação de schema item a item.

O LLM é tratado como fonte não confiável: código desconhecido é ignorado, item inválido cai
para heurística, e o texto/código do requisito NUNCA é sobrescrito pelo modelo.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import ValidationError

from ..config import Settings
from ..domain.models import Enrichment, Requirement
from ..llm.gateway import LLMGateway, LLMUnavailableError
from ..llm.prompts import load_prompt
from ..security.pii import neutralize_delimiters
from .heuristics import heuristic_enrichment

logger = logging.getLogger(__name__)


def _batches(items: list[Requirement], size: int) -> list[list[Requirement]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def _coerce_levels(item: dict[str, Any]) -> dict[str, Any]:
    for key in ("criticality", "risk_level", "cost_impact"):
        value = str(item.get(key, "")).upper().replace("MÉDIA", "MEDIA").replace("ALTO", "ALTA")
        item[key] = value.replace("BAIXO", "BAIXA").replace("MEDIO", "MEDIA")
    for key in ("risks", "ambiguities", "clarification_questions", "proposal_evidence"):
        items = item.get(key)
        if isinstance(items, list):
            limit = 3 if key == "clarification_questions" else 4 if key == "proposal_evidence" else 5
            item[key] = [str(v)[:300] for v in items][:limit]
    if isinstance(item.get("summary"), str):
        item["summary"] = str(item["summary"])[:400]
    return item


def enrich_requirements(
    requirements: list[Requirement], gateway: LLMGateway | None, settings: Settings, redacted_lookup: dict[str, str],
    title: str,
) -> list[Requirement]:
    """`redacted_lookup` mapeia código → texto com PII mascarada (o que efetivamente vai ao LLM)."""
    llm_results: dict[str, Enrichment] = {}
    if gateway is not None and requirements:
        prompt = load_prompt(settings.prompts_dir, "enrich_requirements")
        for batch in _batches(requirements, settings.llm_batch_size):
            payload = [{"code": r.code, "category": r.category.value, "obligation": r.obligation.value,
                        "text": redacted_lookup.get(r.code, r.text),
                        "metrics": [m.raw for m in r.metrics]} for r in batch]
            system, user = prompt.render(
                title=neutralize_delimiters(title),
                requirements_json=neutralize_delimiters(json.dumps(payload, ensure_ascii=False, indent=1)),
            )
            try:
                data = gateway.complete_json(system=system, user=user, task="enrich_requirements")
            except LLMUnavailableError:
                gateway.usage.degraded_mode = True
                break  # sem LLM → restante segue heurístico
            valid_codes = {r.code for r in batch}
            for raw in data.get("items", []):
                if not isinstance(raw, dict) or raw.get("code") not in valid_codes:
                    continue
                try:
                    llm_results[str(raw["code"])] = Enrichment.model_validate({**_coerce_levels(dict(raw)), "source": "llm"})
                except (ValidationError, TypeError) as exc:
                    logger.warning("invalid_llm_item", extra={"extra_fields": {"code": raw.get("code"),
                                                                                "error": str(exc)[:200]}})

    enriched: list[Requirement] = []
    for req in requirements:
        enrichment = llm_results.get(req.code) or heuristic_enrichment(req)
        enriched.append(req.model_copy(update={"enrichment": enrichment}))
    return enriched
