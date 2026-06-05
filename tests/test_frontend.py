from fastapi.testclient import TestClient

from deep_research_agent.api import app


client = TestClient(app)


def test_home_page_serves_frontend_shell():
    response = client.get("/")

    assert response.status_code == 200
    assert "Deep Research Agent" in response.text
    assert "research-form" in response.text
    assert "生成报告" in response.text


def test_frontend_assets_are_served():
    css = client.get("/static/styles.css")
    js = client.get("/static/app.js")

    assert css.status_code == 200
    assert "dashboard-shell" in css.text
    assert js.status_code == 200
    assert "fetch('/api/research'" in js.text
