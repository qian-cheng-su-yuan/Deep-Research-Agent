from deep_research_agent.workflow import ResearchWorkflow


class BrokenStructuredClient:
    provider = "demo"
    model_name = "broken-json"

    def complete_json(self, task: str, topic: str, **kwargs):
        return "not json"

    def complete(self, topic: str, section_title: str, source_snippets: list[str]) -> str:
        return f"{topic} - {section_title}"


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
    assert result.state.runtime.workflow_steps == ["Planner", "Searcher", "Writer", "Reviewer", "Exporter"]
    assert result.state.runtime.model_name == "demo-local"
    assert result.state.runtime.fallback_used is False


def test_workflow_falls_back_when_structured_json_keeps_failing(tmp_path):
    workflow = ResearchWorkflow(output_dir=tmp_path, demo=True, llm_client=BrokenStructuredClient())

    result = workflow.run("AI Agent 在企业客服中的应用")

    assert result.review.passed is True
    assert result.state.runtime.fallback_used is True
    assert result.state.runtime.structured_retries >= 2
    assert result.state.runtime.model_name == "broken-json"


def test_workflow_rejects_empty_topic(tmp_path):
    workflow = ResearchWorkflow(output_dir=tmp_path, demo=True)

    try:
        workflow.run("  ")
    except ValueError as exc:
        assert "topic" in str(exc).lower()
    else:
        raise AssertionError("empty topic should fail")
