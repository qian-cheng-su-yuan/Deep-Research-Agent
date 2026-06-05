import subprocess
import sys


def test_cli_run_generates_report(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "deep_research_agent",
            "run",
            "新能源汽车行业竞争格局分析",
            "--demo",
            "--output-dir",
            str(tmp_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "报告已生成" in completed.stdout
    reports = list(tmp_path.glob("*.md"))
    assert len(reports) == 1
    content = reports[0].read_text(encoding="utf-8")
    assert "# 新能源汽车行业竞争格局分析" in content
    assert "## 结论与建议" in content
