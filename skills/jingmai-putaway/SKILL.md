# jingmai - 京麦智能体

**描述:** 基于 Claude API 的智能对话系统，支持多轮对话、RAG 增强检索、工作流执行和自我进化能力。
**版本:** 0.1.0
**标签:** `agent` `workflow` `memory` `rag` `ecommerce`

---

## 🎯 触发场景

当用户询问以下问题时使用本技能：

### 核心场景
- "如何使用京麦？" / "京麦怎么用？"
- "京麦上架流程" / "商品上架工作流"
- "如何配置 RAG？" / "RAG 检索怎么用"
- "工作流系统" / "如何执行工作流"
- "记忆系统" / "如何使用记忆"

### CLI 操作
- "如何查看工作流？"
- "京麦支持哪些命令？"
- "如何配置环境变量？"

### 架构问题
- "Redis 和 Milvus 的作用"
- "京麦的系统架构"
- "如何部署京麦？"

---

## 核心功能

- **智能对话**: 多轮对话、上下文感知
- **RAG 检索**: 向量 + BM25 + 实体 + 图谱 四路召回
- **工作流引擎**: 14 步商品上架流程
- **自我进化**: 性能追踪 + 技能进化
- **双层记忆**: 短期 (Redis) + 长期 (Milvus)

---

## 🚀 5 分钟上手

### 前置要求

- Python 3.10+
- Poetry
- Redis（可选）
- Milvus（可选）

### 安装

```bash
cd jingmai-cli
poetry install
cp .env.example .env
# 编辑 .env，填写 ANTHROPIC_API_KEY
```

### 快速验证

```bash
# 查看系统状态
poetry run jingmai status

# 交互式聊天
poetry run jingmai chat

# 单次查询
poetry run jingmai chat "你好"
```

---

## 📚 典型使用场景

### 场景 1: 商品上架（完整流程）

```bash
# 1. 查看可用工作流
poetry run jingmai workflow list

# 2. 查看工作流详情
poetry run jingmai workflow info 1

# 3. 执行商品上架流程
poetry run jingmai workflow execute 1 --context '{"product_id": "12345"}'

# 4. 查看执行状态
poetry run jingmai workflow status <execution_id>

# 5. 如需恢复执行
poetry run jingmai workflow resume <execution_id>
```

### 场景 2: RAG 智能检索

```bash
# 1. 索引文档
poetry run jingmai rag index ./docs

# 2. 语义检索
poetry run jingmai rag search "商品上架流程"

# 3. 查看 RAG 统计
poetry run jingmai rag stats
```

### 场景 3: 记忆管理

```bash
# 1. 添加短期记忆
poetry run jingmai memory short-term "用户偏好简洁输出"

# 2. 添加长期记忆（实体-类型-内容-描述）
poetry run jingmai memory long-term \
  --entity "用户A" \
  --type "preference" \
  --content "喜欢简洁输出" \
  --description "用户交互偏好"

# 3. 检索记忆
poetry run jingmai memory retrieve "用户偏好"

# 4. 查看记忆统计
poetry run jingmai memory stats
```

### 场景 4: 自定义对话配置

```bash
# 使用特定模型
poetry run jingmai chat --model claude-opus-4-7

# 使用不同提供商
poetry run jingmai chat --provider openai

# 自定义系统提示
poetry run jingmai chat --system-prompt "你是一个商品上架助手"

# 选择输出样式
poetry run jingmai chat --style minimal

# 保存会话
poetry run jingmai chat --save

# 恢复历史会话
poetry run jingmai chat --resume <session_id>
```

---

## 🔧 CLI 命令完整列表

### 全局命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `jingmai chat [PROMPT]` | 交互式聊天 / 单次查询 | `jingmai chat "你好"` |
| `jingmai query [PROMPT]` | 单次查询，返回结果 | `jingmai query "帮助"` |
| `jingmai run <TASK>` | 执行预定义任务 | `jingmai run test` |
| `jingmai status` | 查看系统状态 | `jingmai status` |
| `jingmai info` | 系统信息 | `jingmai info` |
| `jingmai test` | 运行测试 | `jingmai test` |
| `jingmai examples` | 使用示例 | `jingmai examples` |

### 工作流命令

| 命令 | 说明 |
|------|------|
| `jingmai workflow list` | 列出所有工作流 |
| `jingmai workflow info <id>` | 查看工作流详情 |
| `jingmai workflow execute <id>` | 执行工作流 |
| `jingmai workflow status <id>` | 查看执行状态 |
| `jingmai workflow resume <id>` | 恢复执行 |

### 记忆命令

| 命令 | 说明 |
|------|------|
| `jingmai memory short-term <content>` | 添加短期记忆 |
| `jingmai memory long-term <e> <t> <c> <d>` | 添加长期记忆 |
| `jingmai memory retrieve <query>` | 检索记忆 |
| `jingmai memory stats` | 查看统计 |
| `jingmai memory export <file>` | 导出记忆 |
| `jingmai memory import <file>` | 导入记忆 |

### RAG 命令

| 命令 | 说明 |
|------|------|
| `jingmai rag search <query>` | 语义检索 |
| `jingmai rag index <path>` | 索引文档 |
| `jingmai rag stats` | RAG 统计 |

### 配置命令

| 命令 | 说明 |
|------|------|
| `jingmai config show` | 显示配置 |
| `jingmai config get <key>` | 获取配置值 |
| `jingmai config set <key> <value>` | 设置配置值 |
| `jingmai config validate` | 验证配置 |

---

## ⚙️ 配置说明

### 环境变量 (.env)

```bash
# ========================================
# 必需配置
# ========================================
ANTHROPIC_API_KEY=your_key_here

# ========================================
# 可选配置 - LLM
# ========================================
LLM_PROVIDER=anthropic        # 提供商: anthropic/openai/ollama
LLM_MODEL=claude-sonnet-4-20250514

# ========================================
# 可选配置 - 存储
# ========================================
REDIS_URL=redis://localhost:6379      # 短期记忆
MILVUS_HOST=localhost                # 长期记忆向量库
MILVUS_PORT=19530

# ========================================
# 可选配置 - 系统
# ========================================
LOG_LEVEL=INFO                       # 日志级别
```

### 配置说明

- **ANTHROPIC_API_KEY**: 必需，从 [Anthropic Console](https://console.anthropic.com/) 获取
- **LLM_PROVIDER**: 可选，支持 `anthropic`（默认）、`openai`、`ollama`
- **LLM_MODEL**: 可选，默认使用 Claude Sonnet 4
- **REDIS_URL**: 可选，用于短期记忆存储，不配置则使用内存
- **MILVUS_HOST/PORT**: 可选，用于长期记忆向量存储

---

## 🏗️ 项目结构

```
jingmai-putaway/
├── SKILL.md              # 本文件
├── darwin-evaluation.md  # 达尔文评估报告
├── test-prompts.json     # 测试集
└── jingmai-cli/          # CLI 主目录
    ├── cli/              # 命令行入口 (main.py)
    ├── core/             # 核心模块
    │   ├── agent/        # Agent 实现
    │   ├── engine/       # 查询引擎
    │   ├── skills/       # 技能系统
    │   └── tools/        # 工具定义
    └── plugins/          # 插件
        ├── jingmai_workflow/
        ├── jingmai_evolution/
        ├── jingmai_memory/
        └── jingmai_rag/
```

---

## 🎭 Skill 控制模式

基于 [skill-writing-guide](https://github.com/anthropics/claude-code-skills)，本系统支持三种控制模式：

### 1. Pipeline 模式（工作流关卡）

适用于：需要按顺序执行的多步骤任务

**流程**: 准备 → 验证 → 执行 → 检查 → 完成

**示例**: 商品上架工作流
```
1. 准备：收集商品信息
2. 验证：检查数据完整性
3. 执行：调用上架 API
4. 检查：验证上架结果
5. 完成：记录操作日志
```

### 2. Rever 模式（检查清单）

适用于：需要确保多项条件的操作

**检查项**: 权限 → 参数 → 依赖 → 状态

**示例**: 工作流执行前检查
```
□ 检查用户权限
□ 验证输入参数
□ 确认依赖服务可用
□ 检查系统状态
```

### 3. Inversion 模式（阶段提问）

适用于：需要收集信息的复杂任务

**流程**: 确认类型 → 收集信息 → 验证假设 → 执行

**示例**: 故障排查
```
1. 确认问题类型（连接/性能/功能）
2. 收集相关信息（日志/配置/环境）
3. 验证问题假设
4. 执行修复方案
```

---

## ❓ 常见问题

### Q: 连接 Redis 失败？

**A**: 检查以下几点：
1. 确认 Redis 服务已启动：`redis-cli ping`
2. 检查 `.env` 中的 `REDIS_URL` 配置
3. 如果不需要 Redis，可以不配置（系统会使用内存存储）

### Q: Milvus 索引失败？

**A**: 确保以下几点：
1. Milvus 服务已启动：`docker ps | grep milvus`
2. 检查 `.env` 中的 `MILVUS_HOST` 和 `MILVUS_PORT` 配置
3. 确保网络连接正常

### Q: 如何切换 LLM 提供商？

**A**: 在 `.env` 中配置：
```bash
# 使用 OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4

# 使用 Ollama
LLM_PROVIDER=ollama
LLM_MODEL=llama2
```

### Q: 工作流执行失败如何恢复？

**A**: 使用 resume 命令：
```bash
# 1. 查看失败的工作流状态
poetry run jingmai workflow status <execution_id>

# 2. 恢复执行
poetry run jingmai workflow resume <execution_id>
```

---

## 📖 相关资源

- [Anthropic Claude 文档](https://docs.anthropic.com/)
- [Redis 官方文档](https://redis.io/docs/)
- [Milvus 官方文档](https://milvus.io/docs/)
- [Poetry 文档](https://python-poetry.org/docs/)

---

**最后更新**: 2026-04-20  
**评估版本**: 达尔文.skill v0.1.0
