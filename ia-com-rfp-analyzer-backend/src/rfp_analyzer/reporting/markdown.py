"""Relatório executivo em Markdown (pronto para Wiki, GitLab, Teams ou conversão em PDF)."""

from __future__ import annotations

from ..domain.models import AnalysisResult, Level

ICON = {Level.ALTA: "🔴", Level.MEDIA: "🟠", Level.BAIXA: "🟢"}
SIGNAL = {"GO": "🟢 GO", "GO_COM_RESSALVAS": "🟠 GO COM RESSALVAS", "NO_GO": "🔴 NO-GO",
          "INDEFINIDO": "⚪ INDEFINIDO (faltam dados para decidir)"}


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def render_markdown(result: AnalysisResult) -> str:
    k, s, u = result.kpis, result.summary, result.usage
    lines: list[str] = [
        f"# Análise de RFP — {result.title}",
        "",
        f"> Documento: `{result.document_name}` · Análise `{result.analysis_id}` · "
        f"{result.generated_at:%d/%m/%Y %H:%M} UTC · trace `{result.trace_id}`",
        "",
        "## 1. Resumo executivo",
        "",
        f"**Sinal indicativo de bid:** {SIGNAL.get(s.bid_signal, s.bid_signal)}",
        "",
        s.overview,
        "",
        f"**Justificativa:** {s.rationale}",
        "",
        f"_{s.disclaimer}_",
        "",
        "| Indicador | Valor |",
        "|---|---|",
        f"| Requisitos analisados | {k['total_requisitos']} |",
        f"| Criticidade alta | {k['criticidade_alta']} |",
        f"| Risco alto (por requisito) | {k['risco_alto']} |",
        f"| Lacunas de informação | {k['lacunas']} ({k['lacunas_alta']} de severidade alta) |",
        f"| Riscos cruzados | {k['riscos_cruzados']} ({k['riscos_cruzados_alta']} de severidade alta) |",
        f"| Ambiguidades detectadas | {k['ambiguidades']} |",
        f"| Índice de clareza da RFP | {k['indice_clareza']}/100 |",
        "",
    ]
    if s.key_risks:
        lines += ["**Principais riscos**", "", *[f"- {r}" for r in s.key_risks], ""]
    if s.next_steps:
        lines += ["**Próximos passos**", "", *[f"{i}. {n}" for i, n in enumerate(s.next_steps, 1)], ""]

    lines += ["## 2. Riscos cruzados entre requisitos", ""]
    if result.cross_risks:
        lines += ["| ID | Sev. | Risco | Requisitos | Mitigação sugerida |", "|---|---|---|---|---|"]
        lines += [f"| {r.id} | {ICON[r.severity]} {r.severity} | **{_cell(r.title)}** — {_cell(r.description)} | "
                  f"{', '.join(r.related_codes)} | {_cell(r.mitigation)} |" for r in result.cross_risks]
    else:
        lines.append("Nenhum risco cruzado identificado pelas regras.")
    lines.append("")

    lines += ["## 3. Lacunas de informação", "", "| Sev. | Tópico | Status | Por que importa |", "|---|---|---|---|"]
    for g in result.gaps:
        status = "Pendente na RFP (" + ", ".join(g.related_codes) + ")" if g.status == "PENDENTE_NA_RFP" else "Ausente"
        lines.append(f"| {ICON[g.severity]} {g.severity} | {g.topic} | {status} | {_cell(g.description)} |")
    lines.append("")

    lines += ["## 4. Perguntas de esclarecimento (priorizadas)", ""]
    for i, q in enumerate(result.questions, 1):
        ref = f" _(ref.: {', '.join(q.related_codes)})_" if q.related_codes else ""
        lines.append(f"{i}. {ICON[q.priority]} {q.question}{ref}")
    lines.append("")

    lines += ["## 5. Matriz de requisitos", "",
              "| Código | Categoria | Obrig. | Critic. | Risco | Custo | Área | Resumo |",
              "|---|---|---|---|---|---|---|---|"]
    for r in result.requirements:
        e = r.enrichment
        if e is None:
            continue
        lines.append(f"| {r.code} | {r.category} | {r.obligation} | {ICON[e.criticality]} | {ICON[e.risk_level]} | "
                     f"{ICON[e.cost_impact]} | {e.owner_area} | {_cell(e.summary)} |")
    lines.append("")

    lines += ["## 6. Rastreabilidade e uso de IA", "",
              f"- Modelos utilizados: {', '.join(u.models_used) or 'nenhum (modo determinístico)'}",
              f"- Chamadas LLM: {u.calls} (cache: {u.cached_calls}) · tokens: {u.total_tokens}",
              f"- Fallback de modelo acionado: {'sim' if u.fallback_used else 'não'}",
              f"- Modo degradado (heurístico): {'sim' if u.degraded_mode else 'não'}",
              f"- Cobertura de enriquecimento por LLM: {k['cobertura_llm_pct']}%",
              f"- Alertas de segurança: {', '.join(result.security_flags) or 'nenhum'}",
              f"- Versões de prompt: {', '.join(f'{n}@{v}' for n, v in result.prompt_versions.items())}",
              f"- SHA-256 do documento: `{result.document_sha256}`", ""]
    return "\n".join(lines)
