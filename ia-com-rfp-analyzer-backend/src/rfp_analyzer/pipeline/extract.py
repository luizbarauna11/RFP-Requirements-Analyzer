"""Etapa 1 — Extração de requisitos (estratégia híbrida, ADR-002).

1) Determinística (regex) quando a RFP tem códigos → custo zero, fidelidade 100%.
2) LLM por chunks quando não tem → cada item é validado por GROUNDING contra o texto (ADR-003).
3) Heurística por sentenças normativas quando o LLM está indisponível.
"""

from __future__ import annotations

import logging
import re
from difflib import SequenceMatcher

from ..config import Settings
from ..domain.models import Category, Requirement
from ..ingestion.segmenter import (
    classify_obligation,
    extract_metrics,
    normalize,
    segment_coded_requirements,
)
from ..llm.gateway import LLMGateway, LLMUnavailableError
from ..llm.prompts import load_prompt
from ..security.pii import neutralize_delimiters

logger = logging.getLogger(__name__)

NORMATIVE = re.compile(r"\b(devera|deverao|deve|devem|obrigatori[oa]|sera necessario|desejavel|e vedad[oa])\b")


def chunk_text(text: str, max_chars: int) -> list[str]:
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, current = [], ""
    for p in paragraphs:
        if current and len(current) + len(p) > max_chars:
            chunks.append(current)
            current = ""
        current += p + "\n\n"
    if current.strip():
        chunks.append(current)
    return chunks


def is_grounded(candidate: str, document_norm: str, min_ratio: float) -> bool:
    cand = normalize(candidate)
    if not cand:
        return False
    if cand in document_norm:
        return True
    match = SequenceMatcher(None, cand, document_norm, autojunk=False).find_longest_match(
        0, len(cand), 0, len(document_norm)
    )
    return match.size / len(cand) >= min_ratio


def _heuristic_sentences(text: str) -> list[Requirement]:
    sentences = re.split(r"(?<=[.;?])\s+|\n", text)
    reqs: list[Requirement] = []
    for s in sentences:
        s = s.strip()
        if len(s) > 25 and (NORMATIVE.search(normalize(s)) or s.endswith("?")):
            cat = Category.PENDENCIA if s.endswith("?") else Category.OUTRO
            reqs.append(Requirement(code=f"REQ-{len(reqs) + 1:03d}", category=cat, text=s,
                                    obligation=classify_obligation(s, cat), metrics=extract_metrics(s),
                                    extraction="heuristic"))
    return reqs


def _llm_extract(text: str, gateway: LLMGateway, settings: Settings) -> list[Requirement]:
    prompt = load_prompt(settings.prompts_dir, "extract_requirements")
    doc_norm = normalize(text)
    reqs: list[Requirement] = []
    seen: set[str] = set()
    dropped = 0
    for chunk in chunk_text(text, settings.extraction_chunk_chars):
        system, user = prompt.render(chunk=neutralize_delimiters(chunk))
        data = gateway.complete_json(system=system, user=user, task="extract_requirements")
        for item in data.get("items", []):
            source = str(item.get("source_text", "")).strip()
            key = normalize(source)
            if not source or key in seen:
                continue
            if not is_grounded(source, doc_norm, settings.grounding_min_ratio):
                dropped += 1  # alucinação/paráfrase descartada
                continue
            seen.add(key)
            try:
                cat = Category(str(item.get("category", "OUTRO")).upper())
            except ValueError:
                cat = Category.OUTRO
            reqs.append(Requirement(code=f"REQ-{len(reqs) + 1:03d}", category=cat, text=source,
                                    obligation=classify_obligation(source, cat), metrics=extract_metrics(source),
                                    extraction="llm"))
    logger.info("llm_extraction", extra={"extra_fields": {"kept": len(reqs), "dropped_ungrounded": dropped}})
    return reqs


def extract_requirements(text: str, gateway: LLMGateway | None, settings: Settings) -> list[Requirement]:
    coded = segment_coded_requirements(text)
    if len(coded) >= settings.min_coded_requirements:
        return coded
    if gateway is not None:
        try:
            extracted = _llm_extract(text, gateway, settings)
            if extracted:
                return extracted
        except LLMUnavailableError:
            gateway.usage.degraded_mode = True
    return coded or _heuristic_sentences(text)

