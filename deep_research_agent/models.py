from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="Research topic")
    provider: Literal["demo", "deepseek", "qwen"] = "demo"
    demo: bool = True
    output_dir: str | None = None

    @field_validator("topic")
    @classmethod
    def topic_must_not_be_blank(cls, value: str) -> str:
        topic = value.strip()
        if not topic:
            raise ValueError("topic must not be blank")
        return topic


class ResearchSection(BaseModel):
    title: str
    description: str
    keywords: list[str] = Field(default_factory=list)


class ResearchOutline(BaseModel):
    topic: str
    sections: list[ResearchSection]


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class SectionDraft(BaseModel):
    title: str
    content: str
    sources: list[SearchResult] = Field(default_factory=list)


class SectionContent(BaseModel):
    title: str
    content: str


class ReviewResult(BaseModel):
    passed: bool
    issues: list[str] = Field(default_factory=list)


class WorkflowRuntime(BaseModel):
    provider: str = "demo"
    model_name: str = "demo-local"
    fallback_used: bool = False
    structured_retries: int = 0
    structured_errors: list[str] = Field(default_factory=list)
    workflow_steps: list[str] = Field(default_factory=list)


class ResearchState(BaseModel):
    topic: str
    outline: ResearchOutline | None = None
    search_results: dict[str, list[SearchResult]] = Field(default_factory=dict)
    drafts: list[SectionDraft] = Field(default_factory=list)
    markdown: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    runtime: WorkflowRuntime = Field(default_factory=WorkflowRuntime)


class WorkflowResult(BaseModel):
    state: ResearchState
    review: ReviewResult
    markdown: str
    report_path: Path

    model_config = {"arbitrary_types_allowed": True}


class ResearchResponse(BaseModel):
    topic: str
    markdown: str
    report_path: str
    review: ReviewResult
    outline: list[str] = Field(default_factory=list)
    sections_count: int = 0
    sources_count: int = 0
    created_at: str
    runtime: WorkflowRuntime
