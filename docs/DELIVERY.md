# Deep Research Agent 交付运行手册

这份手册用于交付验收、项目复现和面试沟通。项目是一个可运行的 AI 研究工作台，提供 FastAPI、CLI 和浏览器前端三种入口。默认本地模式不需要 API Key，可以完整生成 Markdown 调研报告；配置 DeepSeek 或 Qwen 后可切换到真实模型。

## 需要填写的信息

前端页面只需要填写三类信息：

- 研究主题：例如 `新能源汽车行业竞争格局分析`。
- 模型提供商：选择 `本地模式`、`DeepSeek 真实模型` 或 `Qwen 真实模型`。
- 输出目录：默认 `outputs`，用于保存生成的 Markdown 报告。

真实模型 API Key 不在前端输入。请在项目根目录创建 `.env` 文件，并按需填写：

```env
LLM_PROVIDER=demo
DEEPSEEK_API_KEY=
QWEN_API_KEY=
LLM_TIMEOUT_SECONDS=30
LLM_RETRIES=2
REPORT_OUTPUT_DIR=outputs
```

无 API Key 时保持 `LLM_PROVIDER=demo`，并在前端勾选本地模式。需要调用真实模型时，填写对应 Key，并在前端关闭“强制使用本地模式”。

## 安装与启动

在项目根目录执行：

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

启动 FastAPI 服务：

```bash
python -m uvicorn deep_research_agent.api:app --host 127.0.0.1 --port 8000 --reload
```

如果 8000 端口被占用，可以改用 8001：

```bash
python -m uvicorn deep_research_agent.api:app --host 127.0.0.1 --port 8001 --reload
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

期望返回：

```json
{"status":"ok"}
```

## 前端操作

浏览器访问：

```text
http://127.0.0.1:8000
```

页面打开后应看到研究工作台、服务状态、调研任务表单、工作流节点、运行指标、复制报告和下载 Markdown 按钮。

操作步骤：

1. 在“研究主题”中输入明确的问题。
2. 无 Key 时选择“本地模式”，有 Key 时选择 DeepSeek 或 Qwen。
3. 保持输出目录为 `outputs`，或填写其他本地目录。
4. 点击“生成报告”。
5. 等待 `Planner -> Searcher -> Writer -> Reviewer -> Exporter` 节点完成。
6. 检查报告路径、审核状态、章节数量、资料卡片和 Markdown 预览。
7. 点击“复制报告”或“下载 Markdown”交付结果。

## CLI 运行

无需启动 Web 服务，也可以通过 CLI 生成报告：

```bash
python -m deep_research_agent run "新能源汽车行业竞争格局分析" --demo
```

指定输出目录：

```bash
python -m deep_research_agent run "AI Agent 在企业客服中的应用" --demo --output-dir outputs
```

## API 调用

创建研究任务：

```bash
curl -X POST http://127.0.0.1:8000/api/research ^
  -H "Content-Type: application/json" ^
  -d "{\"topic\":\"新能源汽车行业竞争格局分析\",\"provider\":\"demo\",\"demo\":true,\"output_dir\":\"outputs\"}"
```

关键响应字段：

- `markdown`：完整 Markdown 报告。
- `report_path`：本地报告文件路径。
- `review`：结构审核结果。
- `outline`：研究大纲标题列表。
- `sections_count`：章节数量。
- `sources_count`：资料卡片数量。
- `runtime`：模型、fallback、Schema 尝试次数和工作流节点。

## 测试

运行全量测试：

```bash
python -m pytest
```

测试覆盖：

- FastAPI 健康检查和研究任务接口。
- CLI 报告生成。
- Pydantic Schema 校验。
- 结构化 JSON 解析、Markdown code fence 提取、失败重试和 fallback。
- 前端页面、静态资源和真实交付文案。
- README 与本交付手册的运行步骤。

## 验收标准

项目达到可交付状态时应满足：

- 前端可以打开，并展示专业的研究工作台界面。
- 无 API Key 时，本地模式可以完整生成报告。
- 配置 DeepSeek 或 Qwen Key 后，可以切换真实模型。
- 生成报告包含标题、目录、研究大纲、章节正文、参考资料和结论建议。
- `outputs/` 目录生成 Markdown 文件。
- `/api/research` 返回报告内容、运行元信息和审核结果。
- `python -m pytest` 全部通过。

## 项目讲解要点

可以按下面顺序介绍项目：

1. 项目解决长文本调研生成中的结构混乱、内容遗漏和上下文遗忘问题。
2. 工作流拆成 `Planner -> Searcher -> Writer -> Reviewer -> Exporter`，避免一次性生成整篇文章。
3. `ResearchState` 贯穿节点，保存主题、大纲、检索结果、草稿、报告和运行元信息。
4. 大模型输出先经过 JSON 提取和 Pydantic 校验，解析失败或字段缺失会自动重试。
5. 多次失败后 fallback 到本地模式，保证项目在无 Key 或模型异常时仍能完整运行。
6. 前端工作台提供从输入主题到下载报告的完整闭环。
