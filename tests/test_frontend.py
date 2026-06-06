from fastapi.testclient import TestClient

from deep_research_agent.api import app


client = TestClient(app)


def test_home_page_serves_frontend_shell():
    response = client.get("/")

    assert response.status_code == 200
    assert "Deep Research Agent" in response.text
    assert "research-form" in response.text
    assert "生成报告" in response.text
    assert "示例主题" in response.text
    assert "复制报告" in response.text
    assert "下载 Markdown" in response.text
    assert "交付演示步骤" in response.text
    assert "模型状态" in response.text
    assert "Fallback" in response.text
    assert "Schema 尝试" in response.text


def test_frontend_assets_are_served():
    css = client.get("/static/styles.css")
    js = client.get("/static/app.js")

    assert css.status_code == 200
    assert "dashboard-shell" in css.text
    assert "example-grid" in css.text
    assert "copy-action" in css.text
    assert js.status_code == 200
    assert "fetch('/api/research'" in js.text
    assert "downloadMarkdown" in js.text
    assert "document.execCommand(\"copy\")" in js.text
    assert "payload.runtime" in js.text


def test_status_grid_uses_responsive_metric_layout():
    css = client.get("/static/styles.css")

    assert css.status_code == 200
    assert ".status-grid" in css.text
    assert "repeat(auto-fit" in css.text
    assert "minmax(140px" in css.text
