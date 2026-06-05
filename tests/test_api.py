from fastapi.testclient import TestClient

from deep_research_agent.api import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_research_endpoint_generates_report(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORT_OUTPUT_DIR", str(tmp_path))

    response = client.post(
        "/api/research",
        json={"topic": "AI Agent 在企业客服中的应用", "demo": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["topic"] == "AI Agent 在企业客服中的应用"
    assert payload["report_path"].endswith(".md")
    assert "# AI Agent 在企业客服中的应用" in payload["markdown"]


def test_research_endpoint_rejects_blank_topic():
    response = client.post("/api/research", json={"topic": "   ", "demo": True})

    assert response.status_code == 422
