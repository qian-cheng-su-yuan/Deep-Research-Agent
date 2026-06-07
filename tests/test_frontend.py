from fastapi.testclient import TestClient

from deep_research_agent.api import app


client = TestClient(app)


def test_home_page_serves_real_research_workspace():
    response = client.get("/")

    assert response.status_code == 200
    assert "Deep Research Agent" in response.text
    assert "research-form" in response.text
    assert "\u7814\u7a76\u5de5\u4f5c\u53f0" in response.text
    assert "\u672c\u5730\u6a21\u5f0f" in response.text
    assert "\u771f\u5b9e\u6a21\u578b" in response.text
    assert "\u9700\u8981\u586b\u5199\u7684\u4fe1\u606f" in response.text
    assert "\u670d\u52a1\u68c0\u67e5\u4e2d" in response.text
    assert "\u590d\u5236\u62a5\u544a" in response.text
    assert "\u4e0b\u8f7d Markdown" in response.text
    assert "Schema \u5c1d\u8bd5" in response.text
    assert "\u9762\u8bd5\u6f14\u793a\u7248" not in response.text


def test_frontend_assets_are_served():
    css = client.get("/static/styles.css")
    js = client.get("/static/app.js")

    assert css.status_code == 200
    assert "dashboard-shell" in css.text
    assert "hero-badges" in css.text
    assert "config-note" in css.text
    assert "copy-action" in css.text
    assert js.status_code == 200
    assert "fetch(\"/health\")" in js.text
    assert "fetch('/api/research'" in js.text
    assert "\u670d\u52a1\u5728\u7ebf" in js.text
    assert "downloadMarkdown" in js.text
    assert "document.execCommand(\"copy\")" in js.text
    assert "payload.runtime" in js.text


def test_status_grid_uses_responsive_metric_layout():
    css = client.get("/static/styles.css")

    assert css.status_code == 200
    assert ".status-grid" in css.text
    assert "repeat(auto-fit" in css.text
    assert "minmax(140px" in css.text
