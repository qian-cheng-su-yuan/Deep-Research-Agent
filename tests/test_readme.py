from pathlib import Path


def test_readme_contains_delivery_steps():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "## \u4ea4\u4ed8\u6f14\u793a\u6b65\u9aa4" in readme
    assert "\u6b65\u9aa4 1" in readme
    assert "\u6b65\u9aa4 2" in readme
    assert "\u6b65\u9aa4 3" in readme
    assert "\u6b65\u9aa4 4" in readme
    assert "\u6b65\u9aa4 5" in readme
    assert "`outline`" in readme
    assert "`sections_count`" in readme
    assert "`sources_count`" in readme
    assert "`runtime`" in readme
    assert "non-pure JSON" in readme
    assert "Markdown code fence" in readme
    assert "\u9762\u8bd5\u6f14\u793a\u8bdd\u672f" in readme
    assert "JSON \u89e3\u6790\u5931\u8d25" in readme
