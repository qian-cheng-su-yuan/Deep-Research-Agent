from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Callable, Generic, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

_CODE_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)


@dataclass
class StructuredOutputResult(Generic[T]):
    value: T
    attempts: int
    used_fallback: bool
    errors: list[str] = field(default_factory=list)


class StructuredOutputRunner:
    def __init__(self, retries: int = 2):
        self.retries = max(1, retries)

    def generate(
        self,
        generator: Callable[[str | None], str],
        schema: type[T],
        fallback: Callable[[], T],
    ) -> StructuredOutputResult[T]:
        errors: list[str] = []
        feedback: str | None = None
        for attempt in range(1, self.retries + 1):
            try:
                raw = generator(feedback)
                value = schema.model_validate_json(extract_json_object(raw))
                return StructuredOutputResult(value=value, attempts=attempt, used_fallback=False, errors=errors)
            except (ValueError, ValidationError) as exc:
                errors.append(str(exc))
                feedback = (
                    "上一次输出无法通过 JSON/Pydantic 校验。"
                    "请只返回符合 Schema 的 JSON，不要输出解释文本。"
                )
        return StructuredOutputResult(
            value=fallback(),
            attempts=self.retries,
            used_fallback=True,
            errors=errors,
        )


def extract_json_object(raw: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("LLM returned empty structured output")

    text = raw.strip()
    fence_match = _CODE_FENCE_RE.search(text)
    if fence_match:
        text = fence_match.group(1).strip()

    start = text.find("{")
    if start < 0:
        return text

    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1].strip()

    return text
