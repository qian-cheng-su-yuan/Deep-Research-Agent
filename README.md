# Deep Research Agent 自动化深度调研与长文生成智能体

Deep Research Agent 是一个面向行业调研、竞品分析和市场分析的 AI Agent 原型项目。项目采用 `FastAPI + CLI` 双入口，模拟 LangGraph 状态图思想，将长文生成拆成 `Planner -> Searcher -> Writer -> Reviewer -> Exporter` 多节点工作流，避免单轮 Prompt 生成时常见的结构混乱、内容遗漏和上下文遗忘问题。

项目默认支持无 API Key 的 `demo` 模式，可以在本地稳定生成结构化 Markdown 报告；配置 DeepSeek 或 Qwen Key 后，也可以切换到真实大模型调用。

## 核心功能

- 根据输入主题自动生成研究大纲和章节结构。
- 使用可替换检索接口聚合章节资料，默认提供本地模拟检索。
- 按章节生成长文草稿，并将资料片段纳入报告内容。
- 使用 Pydantic 对请求、状态、大纲、检索结果和输出响应做结构化校验。
- 对大模型 JSON 输出进行解析、Schema 校验、错误反馈、自动重试和 fallback。
- 对报告完整性进行基础审核，检查大纲、章节、引用和结论是否齐备。
- 导出标准 Markdown 文件，适合继续人工修改、发布或转成其他格式。
- 同时提供命令行和 FastAPI 接口，便于本地演示和后端集成。
- 提供浏览器前端工作台，可直接输入主题、生成报告并预览结果。

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
│   ├── llm.py          # Demo / DeepSeek / Qwen LLM 客户端
│   ├── models.py       # Pydantic 数据结构
│   ├── search.py       # 可替换检索器
│   ├── structured_output.py # JSON 解析、Schema 校验、重试与 fallback
│   └── workflow.py     # 多节点 Agent 工作流
├── examples/
│   └── sample_report.md
├── tests/
│   ├── test_api.py
│   ├── test_cli.py
│   ├── test_frontend.py
│   ├── test_llm.py
│   ├── test_readme.py
│   ├── test_structured_output.py
│   └── test_workflow.py
├── web/
│   ├── index.html      # 前端工作台
│   ├── styles.css      # 页面样式
│   └── app.js          # 前端交互逻辑
├── .env.example
├── pyproject.toml
└── README.md
```

## 快速开始

### 1. 创建虚拟环境

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. 安装依赖

```bash
python -m pip install -e ".[dev]"
```

### 3. 使用 CLI 生成报告

```bash
python -m deep_research_agent run "新能源汽车行业竞争格局分析" --demo
```

默认输出到 `outputs/` 目录。也可以指定输出目录：

```bash
python -m deep_research_agent run "AI Agent 在企业客服中的应用" --demo --output-dir outputs
```

### 4. 启动 FastAPI 服务

```bash
python -m uvicorn deep_research_agent.api:app --reload
```

浏览器访问：

```text
http://127.0.0.1:8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
```

创建调研任务：

```bash
curl -X POST http://127.0.0.1:8000/api/research ^
  -H "Content-Type: application/json" ^
  -d "{\"topic\":\"新能源汽车行业竞争格局分析\",\"demo\":true}"
```

## 交付演示步骤

下面是一套从零开始的完整交付流程，适合面试、项目答辩或给他人验收时使用。

### 步骤 1：准备环境

确认本机安装 Python 3.10 或更高版本，然后在项目根目录创建并激活虚拟环境：

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

如需使用真实大模型，将 `.env.example` 复制为 `.env`，填写 DeepSeek 或 Qwen Key。没有 Key 时保持 `LLM_PROVIDER=demo` 即可完整跑通。

### 步骤 2：启动服务

```bash
python -m uvicorn deep_research_agent.api:app --host 127.0.0.1 --port 8000 --reload
```

如果 8000 端口被占用，可以改用 8001：

```bash
python -m uvicorn deep_research_agent.api:app --host 127.0.0.1 --port 8001 --reload
```

### 步骤 3：打开前端工作台

浏览器访问：

```text
http://127.0.0.1:8000
```

如果使用 8001 端口，则访问：

```text
http://127.0.0.1:8001
```

页面打开后应看到调研任务表单、示例主题、工作流节点、运行结果面板和报告预览区。

### 步骤 4：填写必要信息并生成报告

在前端工作台中填写或选择以下信息：

- 研究主题：例如“新能源汽车行业竞争格局分析”。
- 模型提供商：无 API Key 时选择 `Demo 本地模式`。
- 输出目录：默认 `outputs`。
- Demo 模式：本地演示时保持勾选。

点击“生成报告”后，等待 `Planner -> Searcher -> Writer -> Reviewer -> Exporter` 节点全部点亮。生成完成后，页面会展示：

- 报告路径
- 审核状态
- 章节数量
- 资料卡片数量
- Markdown 报告预览

此时可以点击“复制报告”复制 Markdown，也可以点击“下载 Markdown”保存为本地文件。

### 步骤 5：运行测试

```bash
python -m pytest
```

测试通过后，说明 CLI、API、前端静态资源、工作流、报告导出和文档交付步骤均处于可验收状态。

### 验收标准

- 前端页面可以打开并展示优美的工作台界面。
- 填写必要信息后可以成功生成报告。
- 报告包含标题、目录、研究大纲、四个正文章节和结论建议。
- `outputs/` 目录下生成 Markdown 文件。
- `python -m pytest` 全部通过。

## 配置说明

复制 `.env.example` 为 `.env`，按需填写：

```env
LLM_PROVIDER=demo
DEEPSEEK_API_KEY=
QWEN_API_KEY=
LLM_TIMEOUT_SECONDS=30
LLM_RETRIES=2
REPORT_OUTPUT_DIR=outputs
```

运行模式说明：

- `demo`：默认模式，不需要 Key，适合面试演示和本地测试。
- `deepseek`：配置 `DEEPSEEK_API_KEY` 后可调用 DeepSeek 兼容接口。
- `qwen`：配置 `QWEN_API_KEY` 后可调用 Qwen 兼容接口。

如果选择真实模型但没有配置对应 Key，系统会自动回退到 demo 模式，保证流程不中断。

### 真实模型 JSON 鲁棒性

真实 DeepSeek / Qwen 调用时，模型不一定只返回纯 JSON，也可能返回 non-pure JSON，例如在 JSON 外层包一段说明文字，或者用 Markdown code fence 包裹 `json` 内容。项目的 `structured_output.py` 会先从返回文本中提取第一个完整 JSON 对象，再交给 Pydantic Schema 校验。

如果提取失败、JSON 解析失败、字段缺失或类型不匹配，系统会把校验错误作为 feedback 传回模型并自动重试；连续失败后回退到本地 demo 输出，保证 CLI、API 和前端演示不会中断。这个机制对应简历中“结构化输出校验 + JSON 解析失败重试”的核心能力。

## 工作流设计

1. `Planner`：根据主题生成结构化研究大纲。
2. `Searcher`：围绕每个章节生成资料卡片，后续可替换为搜索 API、RAG 或向量库。
3. `Writer`：调用 Demo LLM 或真实模型，为每个章节生成草稿。
4. `Reviewer`：检查章节数量、草稿覆盖、引用资料和结论章节。
5. `Exporter`：将最终状态渲染为 Markdown 并写入文件。

核心状态对象是 `ResearchState`，它贯穿整个流程，保存主题、大纲、检索结果、章节草稿和最终报告，便于调试、扩展和接入更复杂的状态图框架。

## API 接口

### `GET /health`

返回服务健康状态。

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
- `sources_count`：本地检索资料卡片数量。
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

- 工作流能生成结构化 Markdown 报告。
- 空主题会被拒绝。
- `/health` 和 `/api/research` 接口可用。
- `/` 前端页面和静态资源可访问。
- CLI 能生成报告文件。
- Demo LLM 输出稳定。
- API 调用重试逻辑可处理临时失败。
- 结构化 JSON 输出能完成解析、Pydantic 校验、失败重试和 fallback。

## 面试演示话术

可以按下面顺序向面试官介绍：

1. 这个项目解决的是长文本调研生成中的结构混乱、内容遗漏和上下文遗忘问题。
2. 我没有让模型一次性生成整篇文章，而是拆成 `Planner -> Searcher -> Writer -> Reviewer -> Exporter` 多节点工作流。
3. `ResearchState` 是共享状态，负责在节点之间传递主题、大纲、检索结果、章节草稿和最终报告。
4. 大模型输出不是直接信任，而是先要求 JSON，再从可能带有说明文字或 Markdown code fence 的 non-pure JSON 中提取结构化对象，并用 Pydantic 做 Schema 校验；如果出现 JSON 解析失败、字段缺失或类型错误，会把错误反馈给模型并自动重试。
5. 如果连续失败，系统会 fallback 到本地 demo 输出，保证面试演示和本地运行不中断。
6. 前端工作台用于演示完整闭环：填写主题、选择模型模式、生成报告、查看节点状态、复制或下载 Markdown。

## 与简历项目的对应关系

本仓库对应简历中的“Deep Research Agent 自动化深度调研与长文生成智能体”项目：

- 多节点工作流：代码中明确拆分 Planner、Searcher、Writer、Reviewer、Exporter。
- 状态管理机制：`ResearchState` 在节点之间传递主题、大纲、检索结果、草稿和报告。
- 结构化数据校验：使用 Pydantic 定义请求、状态、大纲、章节、结构化模型输出和响应 Schema。
- 异常处理与稳定性：LLM 客户端和结构化输出层提供重试封装；当 JSON 解析失败、字段缺失、类型错误或缺少 Key 时，系统会自动重试或回退 demo 模式。
- 项目产出：输入主题后自动生成结构化 Markdown 报告。

## 后续扩展方向

- 将 `LocalSearchProvider` 替换为真实搜索 API 或 RAG 检索模块。
- 引入 LangGraph，将当前顺序流程升级为可视化状态图。
- 增加任务队列和异步任务状态查询。
- 增加引用评分、事实一致性检查和人工审核节点。
- 支持导出 DOCX、PDF 或 HTML 报告。
