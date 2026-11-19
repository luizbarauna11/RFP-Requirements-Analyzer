"""Guardrails de entrada: mascaramento de PII (LGPD) e detecção de prompt injection.

A RFP é conteúdo NÃO CONFIÁVEL vindo de terceiros. Tudo que vai ao LLM público (Groq) passa aqui.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

PII_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("CNPJ", re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")),
    ("CPF", re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")),
    ("CARTAO", re.compile(r"\b(?:\d{4}[\s-]?){3}\d{4}\b")),
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")),
    ("TELEFONE", re.compile(r"(?:\+55\s?)?\(?\b\d{2}\)?\s?9?\d{4}-?\d{4}\b")),
]

INJECTION_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"ignore\s+(all\s+)?(the\s+)?(previous|prior|above)\s+instructions",
        r"ignore\s+(as\s+)?instru[cç][oõ]es\s+(anteriores|acima)",
        r"desconsidere\s+(as\s+)?instru[cç][oõ]es",
        r"you\s+are\s+now\s+",
        r"voc[eê]\s+agora\s+[eé]\s+",
        r"system\s*prompt",
        r"</?\s*(system|assistant|documento)\s*>",
    )
]


@dataclass
class RedactionReport:
    counts: dict[str, int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(self.counts.values())


def redact_pii(text: str) -> tuple[str, RedactionReport]:
    report = RedactionReport()
    for label, pattern in PII_PATTERNS:
        text, n = pattern.subn(f"[{label}]", text)
        if n:
            report.counts[label] = report.counts.get(label, 0) + n
    return text, report


def detect_prompt_injection(text: str) -> list[str]:
    return [p.pattern for p in INJECTION_PATTERNS if p.search(text)]


def neutralize_delimiters(text: str) -> str:
    """Impede que o documento 'feche' o delimitador <documento> usado nos prompts."""
    return re.sub(r"</?\s*documento\s*>", "[tag removida]", text, flags=re.IGNORECASE)
