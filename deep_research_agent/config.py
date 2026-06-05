from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    provider: str = "demo"
    deepseek_api_key: str | None = None
    qwen_api_key: str | None = None
    api_timeout_seconds: float = 30.0
    api_retries: int = 2
    output_dir: Path = Path("outputs")


def load_settings() -> Settings:
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    return Settings(
        provider=os.getenv("LLM_PROVIDER", "demo").lower(),
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY") or None,
        qwen_api_key=os.getenv("QWEN_API_KEY") or None,
        api_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
        api_retries=int(os.getenv("LLM_RETRIES", "2")),
        output_dir=Path(os.getenv("REPORT_OUTPUT_DIR", "outputs")),
    )
