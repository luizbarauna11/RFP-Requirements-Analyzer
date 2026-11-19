from rfp_analyzer.domain.models import Category, Obligation
from rfp_analyzer.ingestion.segmenter import extract_title, segment_coded_requirements


def test_extracts_all_coded_requirements(rfp_text: str) -> None:
    reqs = segment_coded_requirements(rfp_text)
    assert len(reqs) == 41
    counts = {c: sum(1 for r in reqs if r.category is c) for c in Category}
    assert counts[Category.TECNICO] == 5
    assert counts[Category.SLA] == 6
    assert counts[Category.PENDENCIA] == 6
    assert counts[Category.OUTRO] == 0


def test_obligation_classification(rfp_text: str) -> None:
    reqs = {r.code: r for r in segment_coded_requirements(rfp_text)}
    assert reqs["PP-03"].obligation is Obligation.DESEJAVEL
    assert reqs["PEN-01"].obligation is Obligation.INFORMATIVO
    assert reqs["LOC-02"].obligation is Obligation.INFORMATIVO  # "poderão"
    assert reqs["SLA-01"].obligation is Obligation.OBRIGATORIO
    assert reqs["SEG-05"].obligation is Obligation.OBRIGATORIO  # proibição ("não poderão")


def test_metrics_and_sections(rfp_text: str) -> None:
    reqs = {r.code: r for r in segment_coded_requirements(rfp_text)}
    assert reqs["SLA-01"].metrics[0].value == 15 and reqs["SLA-01"].metrics[0].unit == "minutos"
    assert reqs["SLA-06"].metrics[0].value == 99.5
    assert reqs["PRZ-01"].metrics[0].unit == "dias úteis"
    assert reqs["RT-01"].section == "2. REQUISITOS TÉCNICOS"


def test_multiline_requirement_is_joined() -> None:
    text = "1. ESCOPO\nRT-01 – A contratada deverá\nprestar suporte em 24 horas.\n\nRT-02 – Outro.\nRT-03 – Mais um."
    reqs = segment_coded_requirements(text)
    assert reqs[0].text == "A contratada deverá prestar suporte em 24 horas."
    assert reqs[0].metrics[0].value == 24


def test_title(rfp_text: str) -> None:
    assert extract_title(rfp_text).startswith("RFP FICTÍCIA")
