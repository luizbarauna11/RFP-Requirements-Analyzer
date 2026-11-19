"""Enriquecimento heurístico: modo degradado quando o LLM está indisponível/desligado/sem orçamento.

Também serve de 'piso' de qualidade: o LLM complementa, mas o sistema nunca entrega vazio.
"""

from __future__ import annotations

from ..domain.models import Category, Enrichment, Level, Obligation, Requirement
from ..ingestion.segmenter import normalize

OWNER_AREA: dict[Category, str] = {
    Category.TECNICO: "Engenharia de Soluções",
    Category.COMERCIAL: "Comercial/Financeiro",
    Category.SLA: "Operações/Service Delivery",
    Category.SEGURANCA: "Segurança da Informação",
    Category.LOCALIDADE: "Operações/Service Delivery",
    Category.PRAZO: "PMO/Transição",
    Category.PERFIL: "RH/Recrutamento",
    Category.GOVERNANCA: "Operações/Service Delivery",
    Category.PENDENCIA: "Pré-vendas",
    Category.OUTRO: "Pré-vendas",
}

BASE_CRITICALITY: dict[Category, Level] = {
    Category.SLA: Level.ALTA, Category.COMERCIAL: Level.ALTA, Category.SEGURANCA: Level.ALTA,
    Category.PRAZO: Level.ALTA, Category.TECNICO: Level.MEDIA, Category.LOCALIDADE: Level.MEDIA,
    Category.PERFIL: Level.MEDIA, Category.GOVERNANCA: Level.MEDIA, Category.PENDENCIA: Level.MEDIA,
    Category.OUTRO: Level.BAIXA,
}

COST_IMPACT: dict[Category, Level] = {
    Category.SLA: Level.ALTA, Category.COMERCIAL: Level.ALTA, Category.LOCALIDADE: Level.ALTA,
    Category.PERFIL: Level.ALTA, Category.PRAZO: Level.MEDIA, Category.TECNICO: Level.MEDIA,
    Category.GOVERNANCA: Level.BAIXA, Category.SEGURANCA: Level.BAIXA, Category.PENDENCIA: Level.MEDIA,
    Category.OUTRO: Level.BAIXA,
}

# Léxico de termos vagos (comuns em RFPs) → ambiguidade + pergunta sugerida
VAGUE_TERMS: dict[str, tuple[str, str]] = {
    "imediatamente": ("'Imediatamente' sem prazo objetivo", "Qual o prazo máximo (em minutos) para a comunicação?"),
    "quando tecnicamente possivel": ("Critério 'tecnicamente possível' é subjetivo",
                                     "Quais critérios definem a viabilidade do atendimento remoto?"),
    "boa comunicacao": ("Competência comportamental sem critério de avaliação",
                        "Como a competência será avaliada (entrevista, certificação)?"),
    "atualizada": ("Periodicidade de atualização não definida", "Qual a periodicidade mínima de atualização?"),
    "horario contratado": ("Horário contratado não definido na RFP", "Qual o horário de cobertura contratado?"),
    "previamente aprovad": ("Fluxo e prazo de aprovação não definidos", "Qual o fluxo e SLA de aprovação?"),
    "politicas de seguranca": ("Políticas não anexadas à RFP", "As políticas podem ser enviadas antes da proposta?"),
    "todos os": ("Escopo universal ('todos') pode gerar custo não previsto", "Existe limite de volume/escopo?"),
    "periferico": ("Lista de periféricos não detalhada", "Qual o inventário de periféricos suportados?"),
}

EVIDENCE: dict[Category, list[str]] = {
    Category.TECNICO: ["Matriz de serviços e catálogo técnico", "Atestados de capacidade técnica"],
    Category.COMERCIAL: ["Planilha de formação de preço", "Premissas comerciais explícitas"],
    Category.SLA: ["Modelo de dimensionamento da equipe", "Histórico de SLA em contratos similares"],
    Category.SEGURANCA: ["Políticas de SI da contratada", "Modelo de termo de confidencialidade"],
    Category.LOCALIDADE: ["Mapa de cobertura e base de técnicos", "Plano de deslocamento"],
    Category.PRAZO: ["Cronograma de transição (Gantt)", "Plano de mobilização de equipe"],
    Category.PERFIL: ["Currículos/perfis-modelo", "Política de recrutamento e retenção"],
    Category.GOVERNANCA: ["Modelo de relatório mensal", "Rito de governança (RACI)"],
    Category.PENDENCIA: [],
    Category.OUTRO: [],
}


def _risk_from_metrics(req: Requirement) -> Level | None:
    for m in req.metrics:
        if m.unit.startswith("minuto") and m.value <= 30:
            return Level.ALTA
        if m.unit == "%" and m.value >= 99:
            return Level.ALTA
        if m.unit == "%" and m.value >= 95:
            return Level.MEDIA
        if m.unit.startswith("dia") and m.value <= 15:
            return Level.MEDIA
    return None


def heuristic_enrichment(req: Requirement) -> Enrichment:
    t = normalize(req.text)
    ambiguities: list[str] = []
    questions: list[str] = []
    for term, (amb, question) in VAGUE_TERMS.items():
        if term in t and len(ambiguities) < 3:
            ambiguities.append(amb)
            questions.append(question)

    criticality = BASE_CRITICALITY[req.category]
    if req.obligation is Obligation.DESEJAVEL:
        criticality = Level.BAIXA
    risk = _risk_from_metrics(req) or (Level.MEDIA if ambiguities else Level.BAIXA)
    risks: list[str] = []
    if risk is Level.ALTA:
        risks.append("Meta agressiva: exige dimensionamento e contingência específicos")
    if ambiguities:
        risks.append("Ambiguidade pode gerar divergência de interpretação na medição/aceite")

    summary = req.text if len(req.text) <= 200 else req.text[:197] + "..."
    return Enrichment(
        summary=summary, criticality=criticality, risk_level=risk, cost_impact=COST_IMPACT[req.category],
        owner_area=OWNER_AREA[req.category], risks=risks[:5], ambiguities=ambiguities[:5],
        clarification_questions=questions[:3], proposal_evidence=EVIDENCE[req.category][:4], source="heuristic",
    )
