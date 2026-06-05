from __future__ import annotations

from deep_research_agent.models import ResearchSection, SearchResult


class LocalSearchProvider:
    def search(self, topic: str, section: ResearchSection) -> list[SearchResult]:
        keyword_text = "、".join(section.keywords) or section.title
        return [
            SearchResult(
                title=f"{topic} - {section.title}资料卡片",
                url=f"local://research/{section.title}",
                snippet=f"{section.description} 重点关注关键词：{keyword_text}。",
            ),
            SearchResult(
                title=f"{section.title}分析框架",
                url="local://research/framework",
                snippet="建议从背景、现状、机会、风险和行动建议五个层次组织分析。",
            ),
        ]
