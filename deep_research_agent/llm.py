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
    def complete(self, topic: str, section_title: str, source_snippets: list[str]) -> str:
        raise NotImplementedError


class DemoLLMClient(BaseLLMClient):
    def complete(self, topic: str, section_title: str, source_snippets: list[str]) -> str:
        evidence = "；".join(source_snippets[:2]) if source_snippets else "暂无外部资料，使用内置行业分析框架。"
        return (
            f"围绕“{topic}”的“{section_title}”部分，可以从市场背景、关键参与者、"
            f"技术路线和落地风险四个维度展开。参考资料显示：{evidence} "
            "因此，本节建议先明确行业问题，再拆解供给侧能力、需求侧变化和商业化路径，"
            "最后给出可验证的判断指标。"
        )


class HTTPChatLLMClient(BaseLLMClient):
    def __init__(self, provider: str, api_key: str, settings: Settings):
        self.provider = provider
        self.api_key = api_key
        self.settings = settings

    def complete(self, topic: str, section_title: str, source_snippets: list[str]) -> str:
        def request_once() -> str:
            prompt = (
                f"请为调研主题《{topic}》撰写章节《{section_title}》。"
                f"要求结构清晰、中文输出、结合资料：{source_snippets}"
            )
            # The real providers can be wired here without changing workflow code.
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
                    payload = json.loads(response.read().decode("utf-8"))
            except error.HTTPError as exc:
                raise ValueError(f"LLM provider returned HTTP {exc.code}") from exc
            return payload["choices"][0]["message"]["content"].strip()

        return retry_call(request_once, retries=max(1, self.settings.api_retries), delay_seconds=0.5)

    def _endpoint(self) -> str:
        if self.provider == "deepseek":
            return "https://api.deepseek.com/chat/completions"
        return "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    def _model(self) -> str:
        if self.provider == "deepseek":
            return "deepseek-chat"
        return "qwen-plus"


def build_llm_client(provider: str, settings: Settings, demo: bool) -> BaseLLMClient:
    selected = provider.lower()
    if demo or selected == "demo":
        return DemoLLMClient()
    if selected == "deepseek" and settings.deepseek_api_key:
        return HTTPChatLLMClient("deepseek", settings.deepseek_api_key, settings)
    if selected == "qwen" and settings.qwen_api_key:
        return HTTPChatLLMClient("qwen", settings.qwen_api_key, settings)
    return DemoLLMClient()
