"""Matriz de conformidade em Excel — a ferramenta de trabalho do time de proposta.

Colunas 'Status de aderência', 'Responsável' e 'Comentário da proposta' são para preenchimento humano.
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.worksheet import Worksheet

from ..domain.models import AnalysisResult

HEADER_FILL = PatternFill("solid", fgColor="1F3864")
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
FONT = "Arial"
LEVEL_FILLS = {"ALTA": "F8CBAD", "MEDIA": "FFE699", "BAIXA": "C6EFCE"}


def _sheet(ws: Worksheet, headers: list[str], rows: list[list[object]], widths: list[int],
           level_colors: bool = True) -> None:
    ws.append(headers)
    for row in rows:
        ws.append(row)
    for i, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width
    for cell in ws[1]:
        cell.font = Font(name=FONT, bold=True, color="FFFFFF")
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.font = Font(name=FONT, size=10)
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws.freeze_panes = "B2"
    if rows:
        ws.auto_filter.ref = ws.dimensions
    last = ws.max_row
    for level, color in (LEVEL_FILLS.items() if level_colors else ()):
        ws.conditional_formatting.add(
            f"A2:{get_column_letter(len(headers))}{max(last, 2)}",
            CellIsRule(operator="equal", formula=[f'"{level}"'], fill=PatternFill("solid", fgColor=color)),
        )


def export_excel(result: AnalysisResult, path: Path) -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "Matriz de Requisitos"
    headers = ["Código", "Categoria", "Seção", "Requisito (texto original)", "Obrigatoriedade", "Criticidade",
               "Risco", "Impacto em custo", "Área responsável", "Resumo", "Riscos", "Ambiguidades",
               "Evidências sugeridas", "Fonte da análise", "Status de aderência", "Responsável", "Comentário da proposta"]
    rows: list[list[object]] = []
    for r in result.requirements:
        e = r.enrichment
        rows.append([
            r.code, r.category.value, r.section or "", r.text, r.obligation.value,
            e.criticality.value if e else "", e.risk_level.value if e else "", e.cost_impact.value if e else "",
            e.owner_area if e else "", e.summary if e else "", "\n".join(e.risks) if e else "",
            "\n".join(e.ambiguities) if e else "", "\n".join(e.proposal_evidence) if e else "",
            e.source if e else "", r.compliance_status.value, "", "",
        ])
    _sheet(ws, headers, rows, [10, 13, 22, 60, 15, 12, 10, 14, 24, 45, 45, 40, 40, 12, 18, 18, 40])
    status_col = get_column_letter(headers.index("Status de aderência") + 1)
    dv = DataValidation(type="list", formula1='"A_AVALIAR,ATENDE,ATENDE_PARCIAL,NAO_ATENDE"', allow_blank=False)
    ws.add_data_validation(dv)
    if rows:
        dv.add(f"{status_col}2:{status_col}{len(rows) + 1}")
        for col in ("Status de aderência", "Responsável", "Comentário da proposta"):
            letter = get_column_letter(headers.index(col) + 1)
            for row_idx in range(2, len(rows) + 2):
                ws[f"{letter}{row_idx}"].fill = INPUT_FILL

    ws2 = wb.create_sheet("Riscos Cruzados")
    _sheet(ws2, ["ID", "Severidade", "Título", "Descrição", "Requisitos", "Mitigação"],
           [[r.id, r.severity.value, r.title, r.description, ", ".join(r.related_codes), r.mitigation]
            for r in result.cross_risks], [8, 12, 40, 60, 25, 60])

    ws3 = wb.create_sheet("Lacunas")
    _sheet(ws3, ["Severidade", "Tópico", "Status", "Por que importa", "Pergunta sugerida", "Requisitos"],
           [[g.severity.value, g.topic, g.status, g.description, g.suggested_question, ", ".join(g.related_codes)]
            for g in result.gaps], [12, 35, 18, 55, 60, 15])

    ws4 = wb.create_sheet("Perguntas")
    _sheet(ws4, ["#", "Prioridade", "Pergunta", "Requisitos", "Origem", "Resposta do cliente"],
           [[i, q.priority.value, q.question, ", ".join(q.related_codes), q.origin, ""]
            for i, q in enumerate(result.questions, 1)], [5, 12, 80, 15, 12, 50])

    ws5 = wb.create_sheet("Resumo")
    k = result.kpis
    n = len(result.requirements) + 1  # última linha de dados da matriz
    m = "'Matriz de Requisitos'"
    summary_rows: list[list[object]] = [
        ["RFP", result.title],                                                      # linha 2
        ["Sinal indicativo de bid", result.summary.bid_signal],                     # 3
        ["Justificativa", result.summary.rationale],                                # 4
        ["Visão geral", result.summary.overview],                                   # 5
        ["Aviso", result.summary.disclaimer],                                       # 6
        ["Total de requisitos", f"=COUNTA({m}!A2:A{n})"],                           # 7
        ["Criticidade ALTA", f'=COUNTIF({m}!F2:F{n},"ALTA")'],                      # 8
        ["Risco ALTO", f'=COUNTIF({m}!G2:G{n},"ALTA")'],                            # 9
        ["Requisitos já avaliados (aderência)", f'=B7-COUNTIF({m}!O2:O{n},"A_AVALIAR")'],  # 10
        ["% de avaliação concluída", "=IFERROR(B10/B7,0)"],                         # 11
        ["Lacunas", len(result.gaps)],
        ["Riscos cruzados", len(result.cross_risks)],
        ["Índice de clareza (0-100)", k.get("indice_clareza")],
        ["Modelos LLM", ", ".join(result.usage.models_used) or "nenhum (modo determinístico)"],
        ["Análise / trace", f"{result.analysis_id} / {result.trace_id}"],
    ]
    _sheet(ws5, ["Indicador", "Valor"], summary_rows, [38, 100], level_colors=False)
    ws5["B11"].number_format = "0.0%"
    wb.move_sheet("Resumo", offset=-4)
    wb.active = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return path
