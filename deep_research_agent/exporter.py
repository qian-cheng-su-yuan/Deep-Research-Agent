from __future__ import annotations

import re
from pathlib import Path

from deep_research_agent.models import ResearchState


def slugify_topic(topic: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff]+", "-", topic.strip(), flags=re.UNICODE)
    return slug.strip("-") or "research-report"


class MarkdownExporter:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def export(self, state: ResearchState) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{slugify_topic(state.topic)}.md"
        path.write_text(state.markdown, encoding="utf-8")
        return path
