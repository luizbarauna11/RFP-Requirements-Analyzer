"""Modelo de domínio. É o CONTRATO do sistema: API, relatórios e LLM convergem para estes schemas."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class Category(StrEnum):
    TECNICO = "TECNICO"
    COMERCIAL = "COMERCIAL"
    SLA = "SLA"
    SEGURANCA = "SEGURANCA"
    LOCALIDADE = "LOCALIDADE"
    PRAZO = "PRAZO"
    PERFIL = "PERFIL"
    GOVERNANCA = "GOVERNANCA"
    PENDENCIA = "PENDENCIA"
    OUTRO = "OUTRO"


class Obligation(StrEnum):
    OBRIGATORIO = "OBRIGATORIO"
    DESEJAVEL = "DESEJAVEL"
    INFORMATIVO = "INFORMATIVO"


class Level(StrEnum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAIXA = "BAIXA"


class ComplianceStatus(StrEnum):
    """Preenchido pelo time de pré-vendas — a IA nunca declara aderência sozinha."""

    A_AVALIAR = "A_AVALIAR"
    ATENDE = "ATENDE"
    ATENDE_PARCIAL = "ATENDE_PARCIAL"
    NAO_ATENDE = "NAO_ATENDE"


class Metric(BaseModel):
    value: float
    unit: str
    raw: str


class Enrichment(BaseModel):
    summary: str = Field(max_length=400)
    criticality: Level
    risk_level: Level
    cost_impact: Level
    owner_area: str = Field(max_length=80)
    risks: list[str] = Field(default_factory=list, max_length=5)
    ambiguities: list[str] = Field(default_factory=list, max_length=5)
    clarification_questions: list[str] = Field(default_factory=list, max_length=3)
    proposal_evidence: list[str] = Field(default_factory=list, max_length=4)
    source: Literal["llm", "heuristic"] = "heuristic"


class Requirement(BaseModel):
    code: str
    category: Category
    section: str | None = None
    text: str
    obligation: Obligation
    metrics: list[Metric] = Field(default_factory=list)
    enrichment: Enrichment | None = None
    compliance_status: ComplianceStatus = ComplianceStatus.A_AVALIAR
    extraction: Literal["deterministic", "llm", "heuristic"] = "deterministic"


class Gap(BaseModel):
    topic: str
    description: str
    severity: Level
    status: Literal["AUSENTE", "PENDENTE_NA_RFP"]
    related_codes: list[str] = Field(default_factory=list)
    suggested_question: str


class CrossRisk(BaseModel):
    id: str
    title: str
    description: str
    severity: Level
    related_codes: list[str]
    mitigation: str


class ClarificationQuestion(BaseModel):
    question: str
    related_codes: list[str] = Field(default_factory=list)
    origin: Literal["rfp", "gap", "llm", "heuristic"]
    priority: Level


BidSignal = Literal["GO", "GO_COM_RESSALVAS", "NO_GO", "INDEFINIDO"]


class ExecutiveSummary(BaseModel):
    overview: str
    bid_signal: BidSignal
    rationale: str
    key_risks: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    source: Literal["llm", "heuristic"] = "heuristic"
    disclaimer: str = (
        "Sinal INDICATIVO gerado automaticamente. A decisão de bid/no-bid e a declaração de aderência "
        "são responsabilidade do comitê de pré-vendas."
    )


class LLMUsage(BaseModel):
    calls: int = 0
    cached_calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    models_used: list[str] = Field(default_factory=list)
    fallback_used: bool = False
    degraded_mode: bool = False
    errors: list[str] = Field(default_factory=list)

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class AnalysisResult(BaseModel):
    analysis_id: str
    trace_id: str
    generated_at: datetime
    document_name: str
    document_sha256: str
    title: str
    requirements: list[Requirement]
    gaps: list[Gap]
    cross_risks: list[CrossRisk]
    questions: list[ClarificationQuestion]
    summary: ExecutiveSummary
    kpis: dict[str, object]
    usage: LLMUsage
    security_flags: list[str] = Field(default_factory=list)
    prompt_versions: dict[str, str] = Field(default_factory=dict)
