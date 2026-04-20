# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

荆漫智能 Agent V2 是基于 Claude API 的新一代智能对话系统，采用**插件化架构**设计，核心由四个主要插件组成：

- **jingmai_workflow**: 基于 LangGraph 的工作流引擎（14步商品上架流程）
- **jingmai_evolution**: 自我进化引擎（基于性能反馈的自动优化）
- **jingmai_memory**: 双层记忆系统（Redis短期 + Milvus长期）
- **jingmai_rag**: RAG增强检索（向量+BM25+实体+图谱四路召回）

---

## 开发命令

### 环境管理

```bash
# 安装依赖
poetry install

# 激活虚拟环境
poetry shell

# 运行 CLI 工具
poetry run jingmai <command>
```

### 测试

```bash
# 运行所有测试
poetry run pytest

# 运行特定测试文件
poetry run pytest tests/unit/test_workflow/

# 查看测试覆盖率（生成HTML报告）
poetry run pytest --cov=plugins --cov-report=html

# 运行测试并显示详细输出
poetry run pytest -v

# 运行单个测试
poetry run pytest tests/unit/test_workflow/test_manager.py::test_execute_workflow
```

### 代码质量

```bash
# 格式化代码
poetry run black .

# 检查代码规范
poetry run ruff check .

# 自动修复可修复的问题
poetry run ruff check --fix .

# 类型检查
poetry run mypy .
```

### CLI 命令

```bash
# 交互式聊天
poetry run jingmai chat

# 单次查询
poetry run jingmai chat "你好"

# 查看系统状态
poetry run jingmai status

# 工作流管理
poetry run jingmai workflow list
poetry run jingmai workflow execute jingmai_product_publish --context '{"key": "value"}'
poetry run jingmai workflow status <execution_id>

# 记忆管理
poetry run jingmai memory short-term "用户偏好"
poetry run jingmai memory retrieve "用户偏好"
poetry run jingmai memory stats

# RAG 检索
poetry run jingmai rag search "查询内容"
poetry run jingmai rag index ./docs
```

---

## 核心架构

### 插件系统

所有插件位于 `plugins/` 目录，每个插件都是独立的 Python 包：

```
plugins/
├── jingmai_workflow/     # 工作流引擎
│   ├── core/            # 核心逻辑（WorkflowManager, StateGraph）
│   ├── checkpoints/     # 检查点管理
│   └── config.py        # 工作流配置
├── jingmai_evolution/   # 进化引擎
│   ├── core/            # SkillEvolver, PerformanceTracker
│   └── triggers/        # 三种触发机制
├── jingmai_memory/      # 记忆系统
│   ├── short_term/      # Redis 短期记忆
│   ├── long_term/       # Milvus 长期记忆
│   └── router.py        # 智能路由
└── jingmai_rag/         # RAG 检索
    ├── recall/          # 多路召回
    ├── rerank/          # 重排序
    └── compression/     # 上下文压缩
```

**关键原则**：
- 插件之间通过**接口**而非直接依赖进行交互
- 每个插件都有自己的 `config.py` 定义配置项
- 使用 `__init__.py` 导出公共 API

### 核心模块

位于 `core/` 目录，提供基础能力：

```
core/
├── agent/              # Agent 实现（多代理系统）
├── cache/              # 缓存层（LLM缓存、RAG缓存、技能缓存）
├── config/             # 配置管理（loader, validator）
├── engine/             # 查询引擎（QueryEngine）
├── hooks/              # 钩子系统（HookManager）
├── llm/                # LLM 抽象层（支持多提供商）
├── permissions/        # 权限检查
└── tools/              # 工具注册表（ToolRegistry）
```

**重要设计决策**：

1. **LLM 抽象层** (`core/llm/`)：
   - 使用 `LLMProvider` 枚举支持多个提供商
   - 通过 `create_llm_client()` 工厂方法创建客户端
   - 配置优先级：环境变量 > .env 文件 > 默认值

2. **缓存策略** (`core/cache/`)：
   - LLM 响应缓存：基于 prompt 的哈希值
   - RAG 查询缓存：基于查询向量
   - 技能加载缓存：避免重复解析 SKILL.md
   - 支持多级缓存（内存 → Redis）

3. **钩子系统** (`core/hooks/`)：
   - 四种钩子类型：`BEFORE_TOOL_EXECUTION`, `AFTER_TOOL_EXECUTION`, `BEFORE_QUERY`, `AFTER_QUERY`
   - 使用 `HookManager` 注册和执行钩子
   - 钩子执行失败不会中断系统

4. **权限检查** (`core/permissions/`)：
   - 三种模式：`default`, `safe`, `dangerous`
   - 在 `core/permissions/checker.py` 中定义危险命令列表
   - 工具执行前自动检查权限

### CLI 入口

主入口在 `cli/main.py`，使用 Click 框架：

```python
@click.group()
@click.pass_context
def cli(ctx):
    """荆漫智能 Agent CLI"""
    # 初始化查询引擎
    engine = create_query_engine(cwd=Path.cwd())
    ctx.obj = engine
```

**CLI 命令分组**：
- `cli/workflow_cli.py`: 工作流命令
- `cli/memory_cli.py`: 记忆管理命令
- `cli/rag_cli.py`: RAG 检索命令
- `cli/config_cli.py`: 配置管理命令

---

## 关键配置

### 环境变量

复制 `.env.example` 到 `.env` 并配置关键选项：

```bash
# LLM 配置（必需）
LLM_PROVIDER=anthropic  # anthropic | openai | ollama
LLM_MODEL=claude-sonnet-4-20250514
ANTHROPIC_API_KEY=your_key_here

# RAG 配置
RAG_ENABLED=true
RAG_INDEX_PATH=./data/rag/index
RAG_TOP_K=5

# 记忆配置
MEMORY_SHORT_TERM_BACKEND=redis
MEMORY_SHORT_TERM_REDIS_URL=redis://localhost:6379/0
MEMORY_LONG_TERM_BACKEND=milvus
MEMORY_LONG_TERM_MILVUS_HOST=localhost
MEMORY_LONG_TERM_MILVUS_PORT=19530

# 工作流配置
WORKFLOW_ENABLED=true
WORKFLOW_DIR=./workflows
WORKFLOW_MAX_EXECUTION_TIME=600
```

### 配置加载器

位于 `core/config/loader.py`，支持：
1. 从 `.env` 文件加载
2. 使用 Pydantic Settings 进行验证
3. 环境变量覆盖文件配置

---

## 工作流系统

基于 LangGraph 的工作流引擎，核心概念：

### WorkflowManager

位于 `plugins/jingmai_workflow/core/workflow_manager.py`：

```python
from plugins.jingmai_workflow import workflow_manager

# 初始化工作流
workflow_manager.initialize_workflows()

# 执行工作流
execution = workflow_manager.execute_workflow(
    workflow_id="jingmai_product_publish",
    context={"product_category": "工业品→货架"}
)

# 查看状态
status = workflow_manager.get_execution_status(execution.execution_id)
```

### 工作流定义

工作流在 `plugins/jingmai_workflow/config.py` 中定义，使用 LangGraph 的 StateGraph：

```python
from langgraph.graph import StateGraph

# 创建状态图
workflow = StateGraph(WorkflowState)

# 添加节点
workflow.add_node("prepare", prepare_node)
workflow.add_node("validate", validate_node)

# 添加边
workflow.add_edge("prepare", "validate")
workflow.set_entry_point("prepare")

# 编译
app = workflow.compile()
```

### 检查点管理

位于 `plugins/jingmai_workflow/core/checkpoint_manager.py`：

```python
from plugins.jingmai_workflow.core.checkpoint_manager import CheckpointManager

# 保存检查点
checkpoint_manager.save_checkpoint(
    execution_id="exec_123",
    node_id="validate",
    state={"data": "value"}
)

# 加载检查点
state = checkpoint_manager.load_checkpoint("exec_123")
```

---

## RAG 系统

四路召回机制：向量检索 + BM25 + 实体检索 + 图谱检索

### 多路召回

位于 `plugins/jingmai_rag/recall/`：

```python
from plugins.jingmai_rag.recall import MultiPathRecall

# 创建召回器
recall = MultiPathRecall()

# 执行召回
results = recall.recall(
    query="商品上架流程",
    top_k=50,
    paths=["vector", "bm25", "entity", "graph"]
)
```

### 重排序

位于 `plugins/jingmai_rag/rerank/`：

使用 Cross-Encoder 模型进行重排序：

```python
from plugins.jingmai_rag.rerank import Reranker

reranker = Reranker()
reranked_results = reranker.rerank(
    query="商品上架流程",
    documents=recalled_docs,
    top_n=10
)
```

### 上下文压缩

当上下文超过阈值时自动压缩：

```python
from plugins.jingmai_rag.compression import ContextCompressor

compressor = ContextCompressor(
    trigger_tokens=8000,
    compression_ratio=0.3,
    method="summary"
)

compressed = compressor.compress(context)
```

---

## 记忆系统

双层架构：短期记忆（Redis）+ 长期记忆（Milvus）

### 记忆路由器

位于 `plugins/jingmai_memory/router.py`：

```python
from plugins.jingmai_memory import MemoryRouter

router = MemoryRouter()

# 自动选择存储后端
router.store(
    content="用户偏好",
    metadata={"type": "preference"}
)

# 检索记忆
memories = router.retrieve("用户偏好", limit=5)
```

### 短期记忆

使用 Redis，适合会话级数据：

```python
from plugins.jingmai_memory.short_term import ShortTermMemory

memory = ShortTermMemory()
memory.add("用户偏好", session_id="session_123")
retrieved = memory.get("用户偏好", session_id="session_123")
```

### 长期记忆

使用 Milvus，支持语义检索：

```python
from plugins.jingmai_memory.long_term import LongTermMemory

memory = LongTermMemory()
memory.add(
    entity="用户A",
    entity_type="user",
    content="喜欢Python",
    description="编程语言偏好"
)

# 语义检索
results = memory.search("编程语言偏好", top_k=10)
```

---

## 进化引擎

基于性能反馈的自动优化系统

### 进化触发器

三种触发机制（`plugins/jingmai_evolution/triggers/`）：

1. **分析触发**: 成功率 < 70% 或执行时间 > 300秒
2. **工具退化触发**: 准确率 < 80% 或召回率 < 75%
3. **指标监控触发**: 系统健康度 < 85% 或用户满意度 < 80%

### 进化执行

```python
from plugins.jingmai_evolution import SkillEvolver

evolver = SkillEvolver()

# 检查是否需要进化
should_evolve = evolver.check_evolution_triggers()

if should_evolve:
    # 执行进化
    evolver.evolve_skills()
```

---

## 开发指南

### 添加新插件

1. 在 `plugins/` 创建新目录
2. 创建 `__init__.py` 导出公共 API
3. 创建 `config.py` 定义配置
4. 在 `core/config/loader.py` 中注册配置

### 添加新工具

1. 在 `core/tools/` 创建工具类
2. 继承 `BaseTool` 并实现 `execute()` 方法
3. 在 `core/tools/registry.py` 中注册工具

### 添加新 CLI 命令

1. 在 `cli/` 创建新的命令文件
2. 使用 Click 装饰器定义命令
3. 在 `cli/main.py` 中导入并注册命令

### 测试新功能

1. 在 `tests/unit/` 或 `tests/integration/` 创建测试文件
2. 使用 pytest 和 pytest-asyncio 编写测试
3. 运行 `poetry run pytest` 验证

---

## 常见问题

### Q: 如何切换 LLM 提供商？

A: 在 `.env` 中修改 `LLM_PROVIDER` 和相应配置：

```bash
# 使用 OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
OPENAI_API_KEY=your_key

# 使用 Ollama
LLM_PROVIDER=ollama
LLM_MODEL=llama2
LLM_BASE_URL=http://localhost:11434
```

### Q: 如何调试工作流执行？

A: 使用 CLI 命令查看详细日志：

```bash
# 查看工作流状态
poetry run jingmai workflow status <execution_id>

# 启用详细日志
LOG_LEVEL=DEBUG poetry run jingmai workflow execute jingmai_product_publish
```

### Q: 如何清理缓存？

A: 使用 Redis CLI 或直接删除缓存文件：

```bash
# 清理 Redis 缓存
redis-cli FLUSHDB

# 清理本地缓存
rm -rf ./data/cache/*
```

---

## 性能优化

### 缓存预热

使用 `core/cache/warmer.py` 预热缓存：

```python
from core.cache.warmer import CacheWarmer

warmer = CacheWarmer()
warmer.warm_llm_cache(["常见问题1", "常见问题2"])
warmer.warm_rag_cache(["常见查询"])
```

### 并发配置

在 `.env` 中调整并发参数：

```bash
MAX_CONCURRENT_TASKS=20
MAX_PARALLEL_RECALL=4
```

---

## 依赖关系

```
CLI (cli/main.py)
  ↓
QueryEngine (core/engine/query.py)
  ↓
Agent + Plugins + Tools + Hooks
  ↓
LLM Client (core/llm/factory.py)
```

**核心依赖流程**：
1. CLI 接收用户输入
2. QueryEngine 协调各个组件
3. Agent 处理对话逻辑
4. Plugins 提供特定功能
5. Tools 执行具体操作
6. Hooks 在关键点执行自定义逻辑
