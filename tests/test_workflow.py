from deep_research_agent.workflow import ResearchWorkflow


def test_workflow_generates_structured_markdown_report(tmp_path):
    workflow = ResearchWorkflow(output_dir=tmp_path, demo=True)

    result = workflow.run("新能源汽车行业竞争格局分析")

    assert result.state.topic == "新能源汽车行业竞争格局分析"
    assert len(result.state.outline.sections) >= 4
    assert result.report_path.exists()
    assert "# 新能源汽车行业竞争格局分析" in result.markdown
    assert "## 目录" in result.markdown
    assert "## 结论与建议" in result.markdown
    assert result.review.passed is True


def test_workflow_rejects_empty_topic(tmp_path):
    workflow = ResearchWorkflow(output_dir=tmp_path, demo=True)

    try:
        workflow.run("  ")
    except ValueError as exc:
        assert "topic" in str(exc).lower()
    else:
        raise AssertionError("empty topic should fail")
