import pytest

from deep_research_agent.config import Settings
from deep_research_agent.llm import DemoLLMClient, HTTPChatLLMClient, retry_call


def test_demo_llm_returns_deterministic_text():
    client = DemoLLMClient()

    first = client.complete("topic", "section", ["source"])
    second = client.complete("topic", "section", ["source"])

    assert first == second
    assert "topic" in first
    assert "section" in first


def test_retry_call_retries_transient_failures():
    attempts = {"count": 0}

    def flaky():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise TimeoutError("temporary")
        return "ok"

    assert retry_call(flaky, retries=3, delay_seconds=0) == "ok"
    assert attempts["count"] == 3


class FakeResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self) -> bytes:
        return self.body


def test_http_llm_retries_malformed_provider_response(monkeypatch):
    attempts = {"count": 0}

    def fake_urlopen(http_request, timeout):
        attempts["count"] += 1
        if attempts["count"] == 1:
            return FakeResponse(b'{"unexpected":[]}')
        return FakeResponse(b'{"choices":[{"message":{"content":"ok"}}]}')

    monkeypatch.setattr("deep_research_agent.llm.request.urlopen", fake_urlopen)
    client = HTTPChatLLMClient("deepseek", "test-key", Settings(api_retries=2))

    assert client.complete("topic", "section", []) == "ok"
    assert attempts["count"] == 2


def test_http_llm_raises_after_empty_provider_responses(monkeypatch):
    def fake_urlopen(http_request, timeout):
        return FakeResponse(b"")

    monkeypatch.setattr("deep_research_agent.llm.request.urlopen", fake_urlopen)
    client = HTTPChatLLMClient("deepseek", "test-key", Settings(api_retries=2))

    with pytest.raises(ValueError, match="empty response"):
        client.complete("topic", "section", [])
