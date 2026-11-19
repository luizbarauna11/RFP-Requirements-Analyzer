from fakes import FakeGateway

from rfp_analyzer.config import Settings
from rfp_analyzer.ingestion.segmenter import normalize
from rfp_analyzer.pipeline.extract import extract_requirements, is_grounded

UNCODED = (
    "Edital de Serviços\n\n"
    "A empresa contratada deverá manter equipe técnica residente na sede durante o horário comercial.\n\n"
    "O pagamento será efetuado em até 45 dias após o aceite.\n\n"
    "Qual o volume de chamados atual?\n"
)


def test_grounding_rejects_hallucinations(settings: Settings) -> None:
    gw = FakeGateway({"extract_requirements": {"items": [
        {"category": "PERFIL", "source_text": "A empresa contratada deverá manter equipe técnica residente na sede"},
        {"category": "SLA", "source_text": "Disponibilidade mínima de 99,9% em regime 24x7"},  # inventado
        {"category": "PENDENCIA", "source_text": "Qual o volume de chamados atual?"},
    ]}})
    reqs = extract_requirements(UNCODED, gw, settings)
    texts = [r.text for r in reqs]
    assert len(reqs) == 2
    assert not any("99,9%" in t for t in texts)
    assert all(r.extraction == "llm" for r in reqs)


def test_heuristic_extraction_without_llm(settings: Settings) -> None:
    reqs = extract_requirements(UNCODED, None, settings)
    assert any("deverá manter" in r.text for r in reqs)
    assert any(r.text.endswith("?") for r in reqs)


def test_is_grounded_tolerates_whitespace_and_accents() -> None:
    doc = normalize("Cláusula 3: A   CONTRATADA deverá\nmanter equipe residente.")
    assert is_grounded("a contratada deverá manter equipe", doc, 0.85)
    assert not is_grounded("a contratada deverá manter estoque de peças", doc, 0.85)
