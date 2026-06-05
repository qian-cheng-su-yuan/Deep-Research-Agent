from deep_research_agent.llm import DemoLLMClient, retry_call


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
