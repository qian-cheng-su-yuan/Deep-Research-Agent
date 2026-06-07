# Deep Research Agent 自动化深度调研与长文生成智能体

Deep Research Agent 是一个面向行业调研、竞品分析和市场分析的 AI 研究工作台。项目采用 `FastAPI + CLI + Web UI` 三入口，模拟 LangGraph 状态图思想，将长文生成拆成 `Planner -> Searcher -> Writer -> Reviewer -> Exporter` 多节点工作流，避免单轮 Prompt 生成时常见的结构混乱、内容遗漏和上下文遗忘问题。

项目默认提供本地模式，无 API Key 也可以完整生成结构化 Markdown 报告；配置 DeepSeek 或 Qwen Key 后，可以切换到真实模型。完整交付运行手册见 [docs/DELIVERY.md](docs/DELIVERY.md)。

## 核心功能

- 根据输入主题自动生成研究大纲和章节结构。
- 使用可替换检索接口聚合章节资料，默认提供本地检索实现。
- 按章节生成长文草稿，并将资料片段纳入报告内容。
- 使用 Pydantic 对请求、状态、大纲、检索结果和响应做结构化校验。
- 对大模型 JSON 输出进行解析、Schema 校验、错误反馈、自动重试和 fallback。
- 支持从 non-pure JSON、解释文本和 Markdown code fence 中提取结构化 JSON 对象。
- 对报告完整性进行基础审核，检查大纲、章节、引用和结论是否齐备。
- 导出标准 Markdown 文件，适合继续人工修改、发布或转成其他格式。
- 提供浏览器研究工作台，可直接输入主题、生成报告、预览结果并下载交付文件。

## 技术栈

- Python 3.10+
- FastAPI
- Pydantic v2
- Uvicorn
- Pytest
- DeepSeek / Qwen 兼容接口设计

## 项目结构

```text
Deep-Research-Agent/
├── deep_research_agent/
│   ├── api.py          # FastAPI 服务入口
│   ├── cli.py          # CLI 命令行入口
│   ├── config.py       # 环境变量与运行配置
│   ├── exporter.py     # Markdown 导出
│   ├── llm.py          # 本地模式 / DeepSeek / Qwen LLM 客户端
│   ├── models.py       # Pydantic 数据结构
│   ├── search.py       # 可替换检索器
│   ├── structured_output.py # JSON 提取、Schema 校验、重试与 fallback
│   └── workflow.py     # 多节点 Agent 工作流
├── docs/
│   └── DELIVERY.md     # 交付运行手册
├── examples/
│   └── sample_report.md
├── tests/
├── web/
│   ├── index.html      # 前端研究工作台
│   ├── styles.css      # 页面样式
│   └── app.js          # 前端交互逻辑
├── .env.example
├── pyproject.toml
└── README.md
```

## 快速开始

### 1. 创建环境

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

### 2. 启动服务

```bash
python -m uvicorn deep_research_agent.api:app --host 127.0.0.1 --port 8000 --reload
```

浏览器访问：

```text
http://127.0.0.1:8000
```

### 3. 前端生成报告

需要填写的信息：

- 研究主题：例如“新能源汽车行业竞争格局分析”。
- 模型提供商：无 Key 时选择“本地模式”，有 Key 时选择 DeepSeek 或 Qwen。
- 输出目录：默认 `outputs`。

点击“生成报告”后，页面会展示工作流节点、报告路径、审核状态、章节数量、资料卡片、模型状态、Fallback 状态、Schema 尝试次数和 Markdown 预览。

### 4. CLI 生成报告

```bash
python -m deep_research_agent run "新能源汽车行业竞争格局分析" --demo
```

指定输出目录：

```bash
python -m deep_research_agent run "AI Agent 在企业客服中的应用" --demo --output-dir outputs
```

### 5. API 调用

```bash
curl -X POST http://127.0.0.1:8000/api/research ^
  -H "Content-Type: application/json" ^
  -d "{\"topic\":\"新能源汽车行业竞争格局分析\",\"provider\":\"demo\",\"demo\":true,\"output_dir\":\"outputs\"}"
```

## 配置说明

复制 `.env.example` 为 `.env`：

```env
LLM_PROVIDER=demo
DEEPSEEK_API_KEY=
QWEN_API_KEY=
LLM_TIMEOUT_SECONDS=30
LLM_RETRIES=2
REPORT_OUTPUT_DIR=outputs
```

运行模式：

- 本地模式：`LLM_PROVIDER=demo`，不需要 Key，适合本地开发、测试和无外网环境。
- 真实模型：配置 `DEEPSEEK_API_KEY` 或 `QWEN_API_KEY` 后，在前端选择对应模型并关闭“强制使用本地模式”。

如果选择真实模型但没有配置对应 Key，系统会自动回退到本地模式，保证流程不中断。API Key 不在前端输入，避免敏感信息暴露在浏览器。

## 工作流设计

1. `Planner`：根据主题生成结构化研究大纲。
2. `Searcher`：围绕每个章节生成资料卡片，后续可替换为搜索 API、RAG 或向量库。
3. `Writer`：调用本地模式或真实模型，为每个章节生成草稿。
4. `Reviewer`：检查章节数量、草稿覆盖、引用资料和结论章节。
5. `Exporter`：将最终状态渲染为 Markdown 并写入文件。

核心状态对象是 `ResearchState`，它贯穿整个流程，保存主题、大纲、检索结果、章节草稿、最终报告和运行元信息，便于调试、扩展和接入更复杂的状态图框架。

## 结构化输出稳定性

真实 DeepSeek / Qwen 调用时，模型不一定只返回纯 JSON，也可能返回 non-pure JSON，例如在 JSON 外层包一段说明文字，或者用 Markdown code fence 包裹 `json` 内容。项目的 `structured_output.py` 会先从返回文本中提取第一个完整 JSON 对象，再交给 Pydantic Schema 校验。

如果提取失败、JSON 解析失败、字段缺失或类型不匹配，系统会把校验错误作为 feedback 传回模型并自动重试；连续失败后回退到本地模式，保证 CLI、API 和前端流程不会中断。

## API 接口

### `GET /health`

返回服务健康状态：

```json
{"status":"ok"}
```

### `POST /api/research`

请求示例：

```json
{
  "topic": "新能源汽车行业竞争格局分析",
  "provider": "demo",
  "demo": true,
  "output_dir": "outputs"
}
```

响应字段：

- `topic`：标准化后的研究主题。
- `markdown`：完整 Markdown 报告内容。
- `report_path`：本地报告文件路径。
- `review`：审核结果与问题列表。
- `outline`：结构化大纲标题列表。
- `sections_count`：最终生成的章节数量。
- `sources_count`：检索资料卡片数量。
- `created_at`：报告生成时间。
- `runtime`：运行元信息，包含 `provider`、`model_name`、`fallback_used`、`structured_retries`、`structured_errors` 和 `workflow_steps`。

响应示例：

```json
{
  "topic": "新能源汽车行业竞争格局分析",
  "report_path": "outputs/新能源汽车行业竞争格局分析.md",
  "sections_count": 4,
  "sources_count": 8,
  "runtime": {
    "provider": "demo",
    "model_name": "demo-local",
    "fallback_used": false,
    "structured_retries": 5,
    "workflow_steps": ["Planner", "Searcher", "Writer", "Reviewer", "Exporter"]
  }
}
```

## 测试

```bash
python -m pytest
```

测试覆盖：

- FastAPI `/health` 和 `/api/research`。
- CLI 报告生成。
- Pydantic Schema 校验。
- LLM 客户端异常重试。
- 结构化 JSON 提取、校验、失败重试和 fallback。
- 前端页面、静态资源和响应式指标区。
- README 与 `docs/DELIVERY.md` 运行步骤。

## 验收标准

- 前端页面可以打开，并展示专业的研究工作台界面。
- 填写必要信息后可以成功生成报告。
- 无 API Key 时，本地模式可以完整跑通。
- 配置真实模型 Key 后，可以切换 DeepSeek 或 Qwen。
- 报告包含标题、目录、研究大纲、章节正文、参考资料和结论建议。
- `outputs/` 目录下生成 Markdown 文件。
- `python -m pytest` 全部通过。

## 与简历第二项目的对应关系

本仓库对应简历中的“Deep Research Agent 自动化深度调研与长文生成智能体”项目：

- 多节点工作流：代码中明确拆分 Planner、Searcher、Writer、Reviewer、Exporter。
- 状态管理机制：`ResearchState` 在节点之间传递主题、大纲、检索结果、草稿和报告。
- 结构化数据校验：使用 Pydantic 定义请求、状态、大纲、章节、结构化模型输出和响应 Schema。
- 异常处理与稳定性：LLM 客户端和结构化输出层提供重试封装；当 JSON 解析失败、字段缺失、类型错误或缺少 Key 时，系统会自动重试或回退本地模式。
- 项目产出：输入主题后自动生成结构化 Markdown 报告，并可通过 Web UI、API 或 CLI 获取结果。

## 后续扩展方向

- 将 `LocalSearchProvider` 替换为真实搜索 API 或 RAG 检索模块。
- 引入 LangGraph，将当前顺序流程升级为可视化状态图。
- 增加任务队列和异步任务状态查询。
- 增加引用评分、事实一致性检查和人工审核节点。
- 支持导出 DOCX、PDF 或 HTML 报告。
