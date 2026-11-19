from pathlib import Path

from fastapi.testclient import TestClient

from rfp_analyzer.api.main import app

client = TestClient(app)
FIXTURE = Path(__file__).parent / "fixtures" / "rfp_ficticia_field_services.txt"


def test_health() -> None:
    assert client.get("/health").json()["status"] == "ok"


def test_analysis_endpoint_offline() -> None:
    with FIXTURE.open("rb") as f:
        resp = client.post("/v1/analyses?use_llm=false", files={"file": ("rfp.txt", f, "text/plain")})
    assert resp.status_code == 200
    body = resp.json()
    assert body["kpis"]["total_requisitos"] == 41
    assert body["summary"]["bid_signal"] in {"GO", "GO_COM_RESSALVAS", "NO_GO", "INDEFINIDO"}


def test_rejects_unsupported_extension() -> None:
    resp = client.post("/v1/analyses?use_llm=false", files={"file": ("x.exe", b"MZ", "application/octet-stream")})
    assert resp.status_code == 415
