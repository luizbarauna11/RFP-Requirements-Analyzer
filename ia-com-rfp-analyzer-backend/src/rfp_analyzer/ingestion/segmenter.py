"""Segmentação DETERMINÍSTICA (sem LLM) de RFPs com requisitos codificados (ex.: RT-01, SLA-03).

Por que determinístico primeiro (ADR-002): RFPs corporativas quase sempre numeram requisitos.
Regex é gratuito, instantâneo, auditável e 100% fiel ao texto — o LLM entra só para ENRIQUECER.
"""

from __future__ import annotations

import re
import unicodedata

from ..domain.models import Category, Metric, Obligation, Requirement

REQ_LINE = re.compile(r"^\s*(?P<code>[A-Z]{2,6}-\d{1,4})\s*[–—:\-]\s*(?P<text>.+?)\s*$")
SECTION_LINE = re.compile(r"^\s*(?P<num>\d{1,2})\.\s+(?P<title>[A-ZÁÉÍÓÚÂÊÔÃÕÇ].{2,80})\s*$")

PREFIX_CATEGORY: dict[str, Category] = {
    "RT": Category.TECNICO, "RF": Category.TECNICO, "RNF": Category.TECNICO, "TEC": Category.TECNICO,
    "RC": Category.COMERCIAL, "COM": Category.COMERCIAL,
    "SLA": Category.SLA, "NS": Category.SLA,
    "SEG": Category.SEGURANCA, "SI": Category.SEGURANCA,
    "LOC": Category.LOCALIDADE,
    "PRZ": Category.PRAZO, "PZ": Category.PRAZO,
    "PP": Category.PERFIL, "PERF": Category.PERFIL,
    "GOV": Category.GOVERNANCA, "REL": Category.GOVERNANCA,
    "PEN": Category.PENDENCIA, "DUV": Category.PENDENCIA,
}

SECTION_KEYWORDS: list[tuple[str, Category]] = [
    ("tecnic", Category.TECNICO), ("comercia", Category.COMERCIAL), ("preco", Category.COMERCIAL),
    ("nivel de servico", Category.SLA), ("sla", Category.SLA), ("seguranca", Category.SEGURANCA),
    ("localidade", Category.LOCALIDADE), ("cobertura", Category.LOCALIDADE), ("prazo", Category.PRAZO),
    ("cronograma", Category.PRAZO), ("perfi", Category.PERFIL), ("equipe", Category.PERFIL),
    ("governanca", Category.GOVERNANCA), ("relatorio", Category.GOVERNANCA),
    ("esclarec", Category.PENDENCIA), ("duvida", Category.PENDENCIA),
]

METRIC = re.compile(
    r"(?P<num>\d+(?:[.,]\d+)?)\s*(?P<unit>%|minutos?|horas?|dias\s+úteis|dias\s+corridos|dias|meses|anos)",
    re.IGNORECASE,
)


def normalize(text: str) -> str:
    """Minúsculas, sem acento, espaços colapsados — usado para matching robusto."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text).strip().lower()


def classify_obligation(text: str, category: Category) -> Obligation:
    t = normalize(text)
    if category is Category.PENDENCIA or t.endswith("?"):
        return Obligation.INFORMATIVO
    if "desejavel" in t or "preferencialmente" in t:
        return Obligation.DESEJAVEL
    if re.search(r"\bnao (podera|poderao|pode|devera|deverao)\b|\b(proibid|vedad)", t):
        return Obligation.OBRIGATORIO  # proibições são obrigações

    if re.search(r"\b(podera|poderao|pode)\b", t) and not re.search(r"\b(devera|deverao|deve)\b", t):
        return Obligation.INFORMATIVO
    return Obligation.OBRIGATORIO


def extract_metrics(text: str) -> list[Metric]:
    metrics: list[Metric] = []
    for m in METRIC.finditer(text):
        unit = re.sub(r"\s+", " ", m.group("unit").lower())
        metrics.append(Metric(value=float(m.group("num").replace(",", ".")), unit=unit, raw=m.group(0)))
    return metrics


def category_for(code: str, section: str | None) -> Category:
    prefix = code.split("-", 1)[0]
    if prefix in PREFIX_CATEGORY:
        return PREFIX_CATEGORY[prefix]
    if section:
        ns = normalize(section)
        for kw, cat in SECTION_KEYWORDS:
            if kw in ns:
                return cat
    return Category.OUTRO


def extract_title(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()[:200]
    return "Documento sem título"


def segment_coded_requirements(text: str) -> list[Requirement]:
    """Extrai requisitos codificados; linhas de continuação são anexadas ao requisito anterior."""
    requirements: list[Requirement] = []
    section: str | None = None
    current: dict[str, str] | None = None

    def flush() -> None:
        if current is None:
            return
        cat = category_for(current["code"], current["section"] or None)
        body = current["text"].strip()
        requirements.append(
            Requirement(
                code=current["code"], category=cat, section=current["section"] or None, text=body,
                obligation=classify_obligation(body, cat), metrics=extract_metrics(body),
            )
        )

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if (m := REQ_LINE.match(line)) is not None:
            flush()
            current = {"code": m.group("code"), "text": m.group("text"), "section": section or ""}
            continue
        if (s := SECTION_LINE.match(line)) is not None:
            flush()
            current = None
            section = f"{s.group('num')}. {s.group('title').strip()}"
            continue
        if not line.strip():
            flush()
            current = None
            continue
        if current is not None:  # continuação de requisito quebrado em várias linhas
            current["text"] += " " + line.strip()

    flush()
    seen: set[str] = set()
    unique = [r for r in requirements if not (r.code in seen or seen.add(r.code))]  # type: ignore[func-returns-value]
    return unique
