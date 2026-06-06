from __future__ import annotations

import time
import json
from urllib import error, request
from typing import Callable, TypeVar

from deep_research_agent.config import Settings

T = TypeVar("T")


def retry_call(func: Callable[[], T], retries: int, delay_seconds: float) -> T:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return func()
        except (TimeoutError, OSError, ValueError) as exc:
            last_error = exc
            if attempt == retries:
                break
            if delay_seconds > 0:
                time.sleep(delay_seconds)
    assert last_error is not None
    raise last_error


class BaseLLMClient:
    provider = "demo"
    model_name = "demo-local"

    def complete(self, topic: str, section_title: str, source_snippets: list[str]) -> str:
        raise NotImplementedError

    def complete_json(self, task: str, topic: str, **kwargs) -> str:
        raise NotImplementedError


class DemoLLMClient(BaseLLMClient):
    provider = "demo"
    model_name = "demo-local"

    def complete(self, topic: str, section_title: str, source_snippets: list[str]) -> str:
        evidence = "；".join(source_snippets[:2]) if source_snippets else "暂无外部资料，使用内置行业分析框架。"
        return (
            f"围绕“{topic}”的“{section_title}”部分，可以从市场背景、关键参与者、"
            f"技术路线和落地风险四个维度展开。参考资料显示：{evidence} "
            "因此，本节建议先明确行业问题，再拆解供给侧能力、需求侧变化和商业化路径，"
            "最后给出可验证的判断指标。"
        )

    def complete_json(self, task: str, topic: str, **kwargs) -> str:
        if task == "outline":
            return json.dumps(
                {
                    "topic": topic,
                    "sections": [
                        {"title": "研究背景与问题定义", "description": "说明主题背景、核心问题和分析边界。", "keywords": ["背景", "问题"]},
                        {"title": "市场现状与关键趋势", "description": "梳理市场规模、技术演进和用户需求变化。", "keywords": ["市场", "趋势"]},
                        {"title": "竞争格局与典型玩家", "description": "分析主要参与者、差异化能力和竞争壁垒。", "keywords": ["竞争", "玩家"]},
                        {"title": "机会风险与落地路径", "description": "总结机会窗口、潜在风险和实施建议。", "keywords": ["机会", "风险"]},
                    ],
                },
                ensure_ascii=False,
            )
        section_title = kwargs["section_title"]
        source_snippets = kwargs.get("source_snippets", [])
        return json.dumps(
            {
                "title": section_title,
                "content": self.complete(topic, section_title, source_snippets),
            },
            ensure_ascii=False,
        )


class HTTPChatLLMClient(BaseLLMClient):
    def __init__(self, provider: str, api_key: str, settings: Settings):
        self.provider = provider
        self.model_name = "deepseek-chat" if provider == "deepseek" else "qwen-plus"
        self.api_key = api_key
        self.settings = settings

    def complete(self, topic: str, section_title: str, source_snippets: list[str]) -> str:
        prompt = (
            f"请为调研主题《{topic}》撰写章节《{section_title}》。"
            f"要求结构清晰、中文输出、结合资料：{source_snippets}"
        )
        return self._chat(prompt)

    def complete_json(self, task: str, topic: str, **kwargs) -> str:
        feedback = kwargs.get("feedback")
        if task == "outline":
            prompt = (
                f"请为调研主题《{topic}》生成研究大纲。"
                "只返回 JSON，格式为："
                '{"topic":"主题","sections":[{"title":"章节标题","description":"章节说明","keywords":["关键词"]}]}。'
                "sections 至少 4 项。"
            )
        else:
            prompt = (
                f"请为调研主题《{topic}》撰写章节《{kwargs['section_title']}》。"
                f"资料：{kwargs.get('source_snippets', [])}。"
                '只返回 JSON，格式为：{"title":"章节标题","content":"章节正文"}。'
            )
        if feedback:
            prompt = f"{prompt}\n修正要求：{feedback}"
        return self._chat(prompt)

    def _chat(self, prompt: str) -> str:
        def request_once() -> str:
            body = json.dumps(
                {"model": self._model(), "messages": [{"role": "user", "content": prompt}]},
                ensure_ascii=False,
            ).encode("utf-8")
            http_request = request.Request(
                self._endpoint(),
                data=body,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with request.urlopen(http_request, timeout=self.settings.api_timeout_seconds) as response:
                    raw_body = response.read()
            except error.HTTPError as exc:
                raise ValueError(f"LLM provider returned HTTP {exc.code}") from exc

            if not raw_body:
                raise ValueError("LLM provider returned empty response")

            try:
                payload = json.loads(raw_body.decode("utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError("LLM provider returned invalid JSON response") from exc

            choices = payload.get("choices") if isinstance(payload, dict) else None
            if not isinstance(choices, list) or not choices:
                raise ValueError("LLM provider response missing choices")

            first_choice = choices[0]
            message = first_choice.get("message") if isinstance(first_choice, dict) else None
            content = message.get("content") if isinstance(message, dict) else None
            if not isinstance(content, str) or not content.strip():
                raise ValueError("LLM provider response missing message content")

            return content.strip()

        return retry_call(request_once, retries=max(1, self.settings.api_retries), delay_seconds=0.5)

    def _endpoint(self) -> str:
        if self.provider == "deepseek":
            return "https://api.deepseek.com/chat/completions"
        return "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    def _model(self) -> str:
        return self.model_name


def build_llm_client(provider: str, settings: Settings, demo: bool) -> BaseLLMClient:
    selected = provider.lower()
    if demo or selected == "demo":
        return DemoLLMClient()
    if selected == "deepseek" and settings.deepseek_api_key:
        return HTTPChatLLMClient("deepseek", settings.deepseek_api_key, settings)
    if selected == "qwen" and settings.qwen_api_key:
        return HTTPChatLLMClient("qwen", settings.qwen_api_key, settings)
    return DemoLLMClient()
