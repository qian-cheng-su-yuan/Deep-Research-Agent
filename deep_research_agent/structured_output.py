from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Generic, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


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
                value = schema.model_validate_json(raw)
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
