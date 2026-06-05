from __future__ import annotations

import argparse
from pathlib import Path

from deep_research_agent.workflow import ResearchWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deep Research Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Generate a research report")
    run_parser.add_argument("topic", help="Research topic")
    run_parser.add_argument("--output-dir", default="outputs", help="Directory for markdown reports")
    run_parser.add_argument("--provider", default="demo", choices=["demo", "deepseek", "qwen"], help="LLM provider")
    run_parser.add_argument("--demo", action="store_true", help="Use deterministic local demo mode")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        workflow = ResearchWorkflow(
            output_dir=Path(args.output_dir),
            provider=args.provider,
            demo=args.demo or args.provider == "demo",
        )
        result = workflow.run(args.topic)
        print(f"报告已生成: {result.report_path}")
