from __future__ import annotations

from pathlib import Path

from deep_research_agent.config import load_settings
from deep_research_agent.exporter import MarkdownExporter
from deep_research_agent.llm import build_llm_client
from deep_research_agent.models import (
    ResearchOutline,
    ResearchSection,
    ResearchState,
    ReviewResult,
    SectionContent,
    SectionDraft,
    WorkflowRuntime,
    WorkflowResult,
)
from deep_research_agent.search import LocalSearchProvider
from deep_research_agent.structured_output import StructuredOutputRunner


class Planner:
    def __init__(self, client, runner: StructuredOutputRunner):
        self.client = client
        self.runner = runner

    def plan(self, topic: str):
        return self.runner.generate(
            lambda feedback: self.client.complete_json("outline", topic, feedback=feedback),
            ResearchOutline,
            lambda: self.fallback_outline(topic),
        )

    @staticmethod
    def fallback_outline(topic: str) -> ResearchOutline:
        return ResearchOutline(
            topic=topic,
            sections=[
                ResearchSection(title="研究背景与问题定义", description="说明主题背景、核心问题和分析边界。", keywords=["背景", "问题"]),
                ResearchSection(title="市场现状与关键趋势", description="梳理市场规模、技术演进和用户需求变化。", keywords=["市场", "趋势"]),
                ResearchSection(title="竞争格局与典型玩家", description="分析主要参与者、差异化能力和竞争壁垒。", keywords=["竞争", "玩家"]),
                ResearchSection(title="机会风险与落地路径", description="总结机会窗口、潜在风险和实施建议。", keywords=["机会", "风险"]),
            ],
        )


class Writer:
    def __init__(self, client, runner: StructuredOutputRunner):
        self.client = client
        self.runner = runner

    def write(self, topic: str, section: ResearchSection, sources: list[str]):
        return self.runner.generate(
            lambda feedback: self.client.complete_json(
                "section",
                topic,
                section_title=section.title,
                source_snippets=sources,
                feedback=feedback,
            ),
            SectionContent,
            lambda: SectionContent(title=section.title, content=self.client.complete(topic, section.title, sources)),
        )


class Reviewer:
    def review(self, state: ResearchState) -> ReviewResult:
        issues: list[str] = []
        if not state.outline or len(state.outline.sections) < 3:
            issues.append("outline should contain at least three sections")
        if len(state.drafts) != len(state.outline.sections if state.outline else []):
            issues.append("every outline section should have a draft")
        if "## 结论与建议" not in state.markdown:
            issues.append("report should include conclusion section")
        if any(not draft.sources for draft in state.drafts):
            issues.append("every section should include sources")
        return ReviewResult(passed=not issues, issues=issues)


class ResearchWorkflow:
    def __init__(
        self,
        output_dir: str | Path | None = None,
        provider: str = "demo",
        demo: bool = True,
        llm_client=None,
    ):
        settings = load_settings()
        self.output_dir = Path(output_dir) if output_dir else settings.output_dir
        self.provider = provider
        self.demo = demo
        self.client = llm_client or build_llm_client(provider, settings, demo)
        self.runner = StructuredOutputRunner(retries=max(1, settings.api_retries))
        self.planner = Planner(self.client, self.runner)
        self.searcher = LocalSearchProvider()
        self.writer = Writer(self.client, self.runner)
        self.reviewer = Reviewer()
        self.exporter = MarkdownExporter(self.output_dir)

    def run(self, topic: str) -> WorkflowResult:
        normalized_topic = topic.strip()
        if not normalized_topic:
            raise ValueError("topic must not be blank")

        state = ResearchState(topic=normalized_topic)
        state.runtime = WorkflowRuntime(
            provider=getattr(self.client, "provider", self.provider),
            model_name=getattr(self.client, "model_name", "unknown"),
            workflow_steps=["Planner"],
        )
        outline_result = self.planner.plan(normalized_topic)
        self._record_structured_result(state, outline_result)
        state.outline = outline_result.value

        state.runtime.workflow_steps.append("Searcher")
        for section in state.outline.sections:
            results = self.searcher.search(normalized_topic, section)
            state.search_results[section.title] = results
            snippets = [item.snippet for item in results]
            if "Writer" not in state.runtime.workflow_steps:
                state.runtime.workflow_steps.append("Writer")
            content_result = self.writer.write(normalized_topic, section, snippets)
            self._record_structured_result(state, content_result)
            state.drafts.append(
                SectionDraft(title=content_result.value.title, content=content_result.value.content, sources=results)
            )

        state.markdown = self._render_markdown(state)
        state.runtime.workflow_steps.append("Reviewer")
        review = self.reviewer.review(state)
        state.runtime.workflow_steps.append("Exporter")
        report_path = self.exporter.export(state)
        return WorkflowResult(state=state, review=review, markdown=state.markdown, report_path=report_path)

    def _record_structured_result(self, state: ResearchState, result) -> None:
        if result.used_fallback:
            state.runtime.fallback_used = True
        state.runtime.structured_retries += result.attempts
        state.runtime.structured_errors.extend(result.errors)

    def _render_markdown(self, state: ResearchState) -> str:
        assert state.outline is not None
        lines = [
            f"# {state.topic}",
            "",
            "> 本报告由 Deep Research Agent 自动生成，采用 Planner -> Searcher -> Writer -> Reviewer -> Exporter 工作流。",
            "",
            "## 目录",
        ]
        for index, section in enumerate(state.outline.sections, 1):
            lines.append(f"{index}. {section.title}")
        lines.extend(["", "## 研究大纲"])
        for section in state.outline.sections:
            lines.append(f"- **{section.title}**：{section.description}")
        for draft in state.drafts:
            lines.extend(["", f"## {draft.title}", "", draft.content, "", "参考资料："])
            for source in draft.sources:
                lines.append(f"- [{source.title}]({source.url})：{source.snippet}")
        lines.extend(
            [
                "",
                "## 结论与建议",
                "",
                "建议将本报告作为初步调研材料，再结合真实数据、专家访谈和业务指标进行二次校验。",
            ]
        )
        return "\n".join(lines).strip() + "\n"
