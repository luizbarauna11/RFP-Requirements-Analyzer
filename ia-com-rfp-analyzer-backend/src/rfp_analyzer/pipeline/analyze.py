"""Etapa 3 — Análise estratégica DETERMINÍSTICA (regras de negócio explícitas e auditáveis).

- Lacunas: tópicos que toda RFP de serviços deveria cobrir e esta não cobre (ou deixou como pendência).
- Riscos cruzados: combinações de requisitos que, juntas, criam risco de entrega ou de preço.
- Perguntas de esclarecimento consolidadas e priorizadas.
- KPIs para o painel executivo.

Regras ficam em código (e não no LLM) porque precisam ser reprodutíveis e revisáveis por humanos.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass

from ..domain.models import (
    Category,
    ClarificationQuestion,
    CrossRisk,
    Gap,
    Level,
    Obligation,
    Requirement,
)
from ..ingestion.segmenter import normalize


@dataclass(frozen=True)
class CoverageTopic:
    topic: str
    keywords: tuple[str, ...]
    severity: Level
    why: str
    question: str


COVERAGE_CHECKLIST: tuple[CoverageTopic, ...] = (
    CoverageTopic("Volumetria (usuários e chamados)",
                  ("quantidade de usuarios", "numero de usuarios", "volume medio", "volume mensal",
                   "chamados por mes", "quantos usuarios"), Level.ALTA,
                  "Sem volumetria não há base para dimensionar equipe nem precificar.",
                  "Qual a volumetria histórica (12 meses) de usuários e chamados por localidade, categoria e prioridade?"),
    CoverageTopic("Horário de cobertura do serviço",
                  ("horario comercial", "24x7", "8x5", "horario de atendimento", "horario de cobertura"), Level.ALTA,
                  "SLAs e disponibilidade dependem da janela de cobertura (8x5, 12x6, 24x7).",
                  "Qual a janela de cobertura contratada (dias e horários) por localidade?"),
    CoverageTopic("SLA de solução (tempo de resolução)",
                  ("tempo de solucao", "prazo de solucao", "tempo de resolucao", "prazo de resolucao",
                   "resolvido em", "restabelecimento"), Level.MEDIA,
                  "Medir apenas o início do atendimento abre espaço para disputas sobre a qualidade da entrega.",
                  "Haverá metas de tempo de solução por prioridade? Como serão medidas e pausadas?"),
    CoverageTopic("Penalidades / glosas por descumprimento",
                  ("multa", "penalidade", "glosa", "redutor", "desconto por descumprimento"), Level.ALTA,
                  "Exposição financeira desconhecida impede precificar o risco.",
                  "Quais penalidades/glosas se aplicam ao descumprimento de SLA e qual o teto mensal?"),
    CoverageTopic("Critérios de julgamento das propostas",
                  ("criterio de julgamento", "avaliacao das propostas", "pontuacao", "tecnica e preco",
                   "menor preco", "criterios de avaliacao"), Level.MEDIA,
                  "Sem critérios de julgamento não é possível calibrar o posicionamento técnico vs. preço.",
                  "Quais os critérios e pesos de avaliação técnica e comercial?"),
    CoverageTopic("Cronograma do processo de RFP",
                  ("data limite", "prazo para envio", "envio das propostas", "cronograma do processo",
                   "entrega da proposta"), Level.MEDIA,
                  "Datas do processo (perguntas, entrega, apresentação) não informadas.",
                  "Qual o cronograma do processo (prazo de perguntas, entrega da proposta e decisão)?"),
    CoverageTopic("Reajuste contratual",
                  ("reajuste", "ipca", "igp-m", "igpm", "repactuacao", "dissidio"), Level.MEDIA,
                  "Contrato de mão de obra intensiva exige regra de reajuste (dissídio/índice).",
                  "Qual o índice e a periodicidade de reajuste, inclusive em caso de prorrogação?"),
    CoverageTopic("LGPD / tratamento de dados pessoais",
                  ("lgpd", "dados pessoais", "13.709", "operador de dados", "encarregado"), Level.MEDIA,
                  "Técnicos acessam equipamentos com dados pessoais; papéis LGPD precisam estar claros.",
                  "A contratada atuará como operadora de dados pessoais? Haverá DPA/aditivo LGPD?"),
    CoverageTopic("Matriz de escalonamento",
                  ("escalonamento", "escalacao", "matriz de contato", "nivel 3", "terceiro nivel"), Level.BAIXA,
                  "Fronteira entre N2 da contratada e N1/N3 da contratante não está definida.",
                  "Qual a fronteira de responsabilidade e o fluxo de escalonamento entre N1, N2 e N3?"),
    CoverageTopic("Plano de saída (desmobilização)",
                  ("plano de saida", "desmobilizacao", "transicao final", "repasse de conhecimento",
                   "termino do contrato"), Level.BAIXA,
                  "Obrigações de repasse no encerramento podem gerar custo não previsto.",
                  "Há obrigações de transição de saída ao término do contrato? Por quanto tempo?"),
    CoverageTopic("Garantias contratuais / seguros",
                  ("garantia contratual", "seguro garantia", "caucao", "seguro de responsabilidade"), Level.BAIXA,
                  "Garantias exigidas impactam custo financeiro da proposta.",
                  "Será exigida garantia contratual ou seguro? Em que percentual?"),
    CoverageTopic("Subcontratação",
                  ("subcontrat", "terceirizacao parcial", "parceiros locais"), Level.BAIXA,
                  "Cobertura nacional pode exigir parceiros locais; a RFP não diz se é permitido.",
                  "É permitida subcontratação/parceiros para atendimento em localidades remotas?"),
)


def _matches(text_norm: str, keywords: tuple[str, ...]) -> bool:
    return any(k in text_norm for k in keywords)


def find_gaps(requirements: list[Requirement], full_text: str) -> list[Gap]:
    pending = [r for r in requirements if r.category is Category.PENDENCIA]
    pending_codes_text = [(r.code, normalize(r.text)) for r in pending]
    pending_set = {normalize(r.text) for r in pending}
    # texto "efetivo" = documento sem as perguntas em aberto (elas indicam ausência, não cobertura)
    effective = normalize(full_text)
    for p in pending_set:
        effective = effective.replace(p, " ")

    gaps: list[Gap] = []
    for topic in COVERAGE_CHECKLIST:
        if _matches(effective, topic.keywords):
            continue
        related = [code for code, t in pending_codes_text if _matches(t, topic.keywords)]
        gaps.append(Gap(
            topic=topic.topic, description=topic.why, severity=topic.severity,
            status="PENDENTE_NA_RFP" if related else "AUSENTE", related_codes=related,
            suggested_question=topic.question,
        ))
    order = {Level.ALTA: 0, Level.MEDIA: 1, Level.BAIXA: 2}
    return sorted(gaps, key=lambda g: order[g.severity])


# ------------------------------------------------------------------------------- riscos cruzados
RiskRule = Callable[[list[Requirement], list[Gap]], CrossRisk | None]


def _codes(reqs: list[Requirement], pred: Callable[[Requirement], bool]) -> list[str]:
    return [r.code for r in reqs if pred(r)]


def _metric_span(reqs: list[Requirement], codes: list[str], unit_prefix: str) -> str:
    values = sorted({m.value for r in reqs if r.code in codes for m in r.metrics if m.unit.startswith(unit_prefix)})
    if not values:
        return ""
    fmt = [f"{v:g}" for v in (values[0], values[-1])]
    return fmt[0] if fmt[0] == fmt[1] else f"{fmt[0]}–{fmt[1]}"


def _gap(gaps: list[Gap], prefix: str) -> Gap | None:
    return next((g for g in gaps if g.topic.startswith(prefix)), None)


def rule_pricing_without_volumetry(reqs: list[Requirement], gaps: list[Gap]) -> CrossRisk | None:
    price = _codes(reqs, lambda r: r.category is Category.COMERCIAL and
                   bool(re.search(r"valor|preco|custo", normalize(r.text))))
    gap = _gap(gaps, "Volumetria")
    if price and gap:
        return CrossRisk(
            id="RX-01", title="Preço fixo sem volumetria definida", severity=Level.ALTA,
            related_codes=price + gap.related_codes,
            description="A RFP exige valor mensal fechado com todos os custos inclusos, mas não informa "
                        "quantidade de usuários nem volume de chamados.",
            mitigation="Precificar com premissas explícitas de volumetria e banda de variação (ex.: ±15%), "
                       "com cláusula de repactuação fora da banda.")
    return None


def rule_aggressive_sla_onsite(reqs: list[Requirement], gaps: list[Gap]) -> CrossRisk | None:
    fast = _codes(reqs, lambda r: r.category is Category.SLA and
                  any(m.unit.startswith("minuto") and m.value <= 30 for m in r.metrics))
    onsite = _codes(reqs, lambda r: r.category is Category.LOCALIDADE and "presencial" in normalize(r.text))
    if fast and onsite:
        return CrossRisk(
            id="RX-02", title="SLA de início agressivo com atendimento presencial multi-site",
            severity=Level.ALTA, related_codes=fast + onsite,
            description=f"Início de atendimento em até {_metric_span(reqs, fast, 'minuto')} minutos combinado com "
                        "presença física em várias localidades exige técnico residente por site ou início remoto.",
            mitigation="Propor que 'início de atendimento' seja contabilizado pelo primeiro contato remoto "
                       "(registro no ITSM) e dimensionar ao menos um técnico residente por unidade.")
    return None


def rule_availability_without_window(reqs: list[Requirement], gaps: list[Gap]) -> CrossRisk | None:
    avail = _codes(reqs, lambda r: r.category is Category.SLA and
                   any(m.unit == "%" and m.value >= 99 for m in r.metrics))
    gap = _gap(gaps, "Horário de cobertura")
    if avail and gap:
        return CrossRisk(
            id="RX-03", title="Meta de disponibilidade sem janela de cobertura", severity=Level.MEDIA,
            related_codes=avail + gap.related_codes,
            description="A disponibilidade é exigida 'durante o horário contratado', que não é definido na RFP.",
            mitigation="Explicitar na proposta a janela assumida e a fórmula de cálculo da disponibilidade.")
    return None


def rule_response_only_sla(reqs: list[Requirement], gaps: list[Gap]) -> CrossRisk | None:
    response = _codes(reqs, lambda r: r.category is Category.SLA and "inicio de atendimento" in normalize(r.text))
    if response and _gap(gaps, "SLA de solução"):
        return CrossRisk(
            id="RX-04", title="SLAs medem apenas o início do atendimento", severity=Level.MEDIA,
            related_codes=response,
            description="Não há meta de solução: o cliente pode, durante a execução, cobrar resolução com "
                        "expectativa implícita não precificada.",
            mitigation="Propor metas de solução como indicador de acompanhamento (não penalizável) ou "
                       "precificá-las explicitamente.")
    return None


def rule_tight_ramp_up(reqs: list[Requirement], gaps: list[Gap]) -> CrossRisk | None:
    ramp = _codes(reqs, lambda r: r.category is Category.PRAZO and
                  bool(re.search(r"implantad|operacao|mobiliza", normalize(r.text))) and
                  any(m.unit.startswith("dia") and m.value <= 45 for m in r.metrics))
    profiles = _codes(reqs, lambda r: r.category is Category.PERFIL and r.obligation is Obligation.OBRIGATORIO)
    if ramp and profiles:
        return CrossRisk(
            id="RX-05", title="Ramp-up curto com exigência de perfis experientes", severity=Level.MEDIA,
            related_codes=ramp + profiles,
            description=f"Implantação total em até {_metric_span(reqs, ramp, 'dia')} dias exige recrutar perfis com "
                        "experiência mínima comprovada em paralelo à transição.",
            mitigation="Iniciar pipeline de recrutamento na fase de proposta e prever operação assistida "
                       "(hypercare) com metas de SLA escalonadas nos primeiros 60 dias.")
    return None


def rule_all_inclusive_travel(reqs: list[Requirement], gaps: list[Gap]) -> CrossRisk | None:
    travel = _codes(reqs, lambda r: r.category is Category.COMERCIAL and "deslocamento" in normalize(r.text))
    multi = _codes(reqs, lambda r: r.category is Category.LOCALIDADE)
    if travel and len(multi) >= 2:
        return CrossRisk(
            id="RX-06", title="Deslocamentos embutidos no preço sem volumetria de visitas",
            severity=Level.MEDIA, related_codes=travel + multi,
            description="Custos de deslocamento devem estar no preço fixo, mas a frequência de visitas e os "
                        "deslocamentos extraordinários não são estimados.",
            mitigation="Separar deslocamentos ordinários (no preço) de extraordinários (reembolso sob aprovação).")
    return None


def rule_cash_flow(reqs: list[Requirement], gaps: list[Gap]) -> CrossRisk | None:
    pay = _codes(reqs, lambda r: r.category is Category.COMERCIAL and "pagamento" in normalize(r.text) and
                 any(m.unit.startswith("dia") and m.value >= 30 for m in r.metrics))
    accept = _codes(reqs, lambda r: r.category is Category.COMERCIAL and
                    bool(re.search(r"validacao|aceite", normalize(r.text))))
    if pay and accept:
        return CrossRisk(
            id="RX-07", title="Fluxo de caixa: pagamento condicionado a validação e aceite",
            severity=Level.BAIXA, related_codes=sorted(set(pay + accept)),
            description=f"Folha é paga mensalmente, mas o recebimento ocorre {_metric_span(reqs, pay, 'dia')} dias "
                        "após validação e aceite, sem prazo máximo de validação — exige capital de giro.",
            mitigation="Incluir custo financeiro no preço e propor prazo máximo para validação (aceite tácito).")
    return None


RISK_RULES: tuple[RiskRule, ...] = (
    rule_pricing_without_volumetry, rule_aggressive_sla_onsite, rule_availability_without_window,
    rule_response_only_sla, rule_tight_ramp_up, rule_all_inclusive_travel, rule_cash_flow,
)


def find_cross_risks(requirements: list[Requirement], gaps: list[Gap]) -> list[CrossRisk]:
    return [risk for rule in RISK_RULES if (risk := rule(requirements, gaps)) is not None]


# ------------------------------------------------------------------------------- perguntas
def consolidate_questions(requirements: list[Requirement], gaps: list[Gap]) -> list[ClarificationQuestion]:
    questions: list[ClarificationQuestion] = []
    seen: set[str] = set()

    def add(q: str, codes: list[str], origin: str, priority: Level) -> None:
        key = normalize(q)[:90]
        if key and key not in seen:
            seen.add(key)
            questions.append(ClarificationQuestion(question=q, related_codes=codes, origin=origin,  # type: ignore[arg-type]
                                                   priority=priority))

    for r in requirements:
        if r.category is Category.PENDENCIA:
            add(r.text, [r.code], "rfp", Level.ALTA)
    for g in gaps:
        if g.status == "AUSENTE":
            add(g.suggested_question, g.related_codes, "gap", g.severity)
    for r in requirements:
        if r.enrichment and r.category is not Category.PENDENCIA:
            prio = r.enrichment.criticality
            for q in r.enrichment.clarification_questions:
                add(q, [r.code], r.enrichment.source, prio)

    order = {Level.ALTA: 0, Level.MEDIA: 1, Level.BAIXA: 2}
    return sorted(questions, key=lambda q: order[q.priority])


# ------------------------------------------------------------------------------- KPIs
def compute_kpis(requirements: list[Requirement], gaps: list[Gap], risks: list[CrossRisk]) -> dict[str, object]:
    enriched = [r.enrichment for r in requirements if r.enrichment]
    ambiguities = sum(len(e.ambiguities) for e in enriched)
    gap_weight = {Level.ALTA: 8, Level.MEDIA: 4, Level.BAIXA: 2}
    # Índice de Clareza (0–100): penaliza lacunas ponderadas e ambiguidades. Fórmula documentada no README.
    clarity = max(0, 100 - sum(gap_weight[g.severity] for g in gaps) - 2 * ambiguities)
    return {
        "total_requisitos": len(requirements),
        "por_categoria": dict(Counter(r.category.value for r in requirements)),
        "por_obrigatoriedade": dict(Counter(r.obligation.value for r in requirements)),
        "criticidade_alta": sum(1 for e in enriched if e.criticality is Level.ALTA),
        "risco_alto": sum(1 for e in enriched if e.risk_level is Level.ALTA),
        "metricas_quantitativas": sum(len(r.metrics) for r in requirements),
        "ambiguidades": ambiguities,
        "lacunas": len(gaps),
        "lacunas_alta": sum(1 for g in gaps if g.severity is Level.ALTA),
        "riscos_cruzados": len(risks),
        "riscos_cruzados_alta": sum(1 for r in risks if r.severity is Level.ALTA),
        "indice_clareza": clarity,
        "cobertura_llm_pct": round(100 * sum(1 for e in enriched if e.source == "llm") / len(enriched), 1)
        if enriched else 0.0,
    }
