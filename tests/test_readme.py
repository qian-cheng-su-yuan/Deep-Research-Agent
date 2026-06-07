from pathlib import Path


def test_readme_contains_delivery_and_runtime_docs():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "## \u5feb\u901f\u5f00\u59cb" in readme
    assert "docs/DELIVERY.md" in readme
    assert "\u672c\u5730\u6a21\u5f0f" in readme
    assert "\u771f\u5b9e\u6a21\u578b" in readme
    assert "\u9700\u8981\u586b\u5199\u7684\u4fe1\u606f" in readme
    assert "\u9a8c\u6536\u6807\u51c6" in readme
    assert "`outline`" in readme
    assert "`sections_count`" in readme
    assert "`sources_count`" in readme
    assert "`runtime`" in readme
    assert "non-pure JSON" in readme
    assert "Markdown code fence" in readme
    assert "\u9762\u8bd5\u6f14\u793a\u7248" not in readme


def test_delivery_doc_explains_real_project_handoff():
    delivery = Path("docs/DELIVERY.md").read_text(encoding="utf-8")

    assert "\u4ea4\u4ed8\u8fd0\u884c\u624b\u518c" in delivery
    assert "\u9700\u8981\u586b\u5199\u7684\u4fe1\u606f" in delivery
    assert ".env" in delivery
    assert "DEEPSEEK_API_KEY" in delivery
    assert "QWEN_API_KEY" in delivery
    assert "python -m uvicorn deep_research_agent.api:app" in delivery
    assert "python -m deep_research_agent run" in delivery
    assert "python -m pytest" in delivery
    assert "\u524d\u7aef\u64cd\u4f5c" in delivery
    assert "\u9a8c\u6536\u6807\u51c6" in delivery
    assert "\u9762\u8bd5\u6f14\u793a\u7248" not in delivery
