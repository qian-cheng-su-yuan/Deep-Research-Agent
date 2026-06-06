from deep_research_agent.models import ResearchOutline, ResearchSection
from deep_research_agent.structured_output import StructuredOutputRunner


def fallback_outline() -> ResearchOutline:
    return ResearchOutline(
        topic="topic",
        sections=[
            ResearchSection(title="Fallback", description="Fallback section", keywords=["fallback"]),
        ],
    )


def test_structured_output_parses_valid_json():
    runner = StructuredOutputRunner(retries=2)

    result = runner.generate(
        lambda feedback: '{"topic":"topic","sections":[{"title":"A","description":"B","keywords":["k"]}]}',
        ResearchOutline,
        fallback_outline,
    )

    assert result.value.sections[0].title == "A"
    assert result.used_fallback is False
    assert result.attempts == 1
    assert result.errors == []


def test_structured_output_retries_invalid_json_then_succeeds():
    runner = StructuredOutputRunner(retries=2)
    responses = iter(
        [
            "not json",
            '{"topic":"topic","sections":[{"title":"A","description":"B","keywords":["k"]}]}',
        ]
    )

    result = runner.generate(lambda feedback: next(responses), ResearchOutline, fallback_outline)

    assert result.value.sections[0].title == "A"
    assert result.used_fallback is False
    assert result.attempts == 2
    assert result.errors


def test_structured_output_extracts_json_from_code_fence():
    runner = StructuredOutputRunner(retries=2)

    result = runner.generate(
        lambda feedback: """```json
{"topic":"topic","sections":[{"title":"A","description":"B","keywords":["k"]}]}
```""",
        ResearchOutline,
        fallback_outline,
    )

    assert result.value.sections[0].title == "A"
    assert result.used_fallback is False
    assert result.attempts == 1


def test_structured_output_extracts_json_from_explanatory_text():
    runner = StructuredOutputRunner(retries=2)

    result = runner.generate(
        lambda feedback: (
            "Here is the JSON you requested:\n"
            '{"topic":"topic","sections":[{"title":"A","description":"B","keywords":["k"]}]}\n'
            "This follows the schema."
        ),
        ResearchOutline,
        fallback_outline,
    )

    assert result.value.sections[0].title == "A"
    assert result.used_fallback is False
    assert result.attempts == 1


def test_structured_output_falls_back_after_validation_failures():
    runner = StructuredOutputRunner(retries=2)

    result = runner.generate(lambda feedback: '{"topic":"topic"}', ResearchOutline, fallback_outline)

    assert result.value.sections[0].title == "Fallback"
    assert result.used_fallback is True
    assert result.attempts == 2
    assert len(result.errors) == 2
