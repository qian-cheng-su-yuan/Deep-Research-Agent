from pathlib import Path


def test_readme_contains_delivery_steps():
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "## 交付演示步骤" in readme
    assert "步骤 1：准备环境" in readme
    assert "步骤 2：启动服务" in readme
    assert "步骤 3：打开前端工作台" in readme
    assert "步骤 4：填写必要信息并生成报告" in readme
    assert "步骤 5：运行测试" in readme
    assert "`outline`" in readme
    assert "`sections_count`" in readme
    assert "`sources_count`" in readme
    assert "`runtime`" in readme
    assert "面试演示话术" in readme
    assert "JSON 解析失败" in readme
