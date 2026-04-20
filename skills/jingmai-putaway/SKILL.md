# jingmai - 京麦智能体

**描述:** 京麦智能体 - 当用户询问商品上架、RAG检索、工作流执行、记忆管理、CLI使用时使用。支持多轮对话、RAG增强检索、工作流执行和自我进化能力。触发词：京麦上架、RAG检索、工作流系统、记忆管理
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
- Poetry（如未安装：`curl -sSL https://install.python-poetry.org | python3 -`）
- Redis（可选）
- Milvus（可选）

### 安装

```bash
# 1. 安装依赖
cd jingmai-cli
poetry install

# 2. 配置环境变量
cp .env.example .env

# 3. 获取 API Key
# 访问 https://console.anthropic.com/settings/keys
# 创建新 API Key 并填入 .env 文件
```

### 快速验证

```bash
# 查看系统状态
poetry run jingmai status
# 输出:
# ✅ 京麦智能体状态
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖 LLM: Claude Sonnet 4 (anthropic)
# 💾 短期记忆: Redis (已连接)
# 🧠 长期记忆: Milvus (已连接)
# 📚 RAG 索引: 15 个文档

# 交互式聊天
poetry run jingmai chat
# 输出: 进入交互模式 (输入 /exit 退出)
# 你: 

# 单次查询
poetry run jingmai chat "你好"
# 输出: 你好！我是京麦智能体，可以帮助你...
```

---

## 📚 典型使用场景

### 场景 1: 商品上架（完整流程）

```bash
# 1. 查看可用工作流
poetry run jingmai workflow list
# 输出:
# 📋 可用工作流 (3)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [1] 商品上架流程 - 14步完整上架
# [2] 价格更新流程 - 批量调价
# [3] 库存同步流程 - 多平台同步

# 2. 查看工作流详情
poetry run jingmai workflow info 1
# 输出:
# 📖 工作流: 商品上架流程
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 步骤数: 14 | 预计时长: 5-10分钟
# 输入: product_id (必需)
#     shop_id (可选)
# 输出: execution_id, 上架结果链接

# 3. 执行商品上架流程
# ⚠️ 执行前会提示确认，使用 --yes 跳过确认
poetry run jingmai workflow execute 1 --context '{"product_id": "12345"}'
# 输出:
# ✅ 工作流已启动
# 📝 Execution ID: exec_abc123
# 进度: [准备中] 0/14 步骤

# 4. 查看执行状态
poetry run jingmai workflow status exec_abc123
# 输出:
# 📊 执行状态: 进行中
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 当前进度: 8/14 步骤
# ✅ 1.准备 2.验证 3.图片上传 4.规格设置
# 🔄 5.价格计算 (当前)
# ⏳ 6.库存配置 7.描述生成...

# 5. 如需恢复执行
poetry run jingmai workflow resume exec_abc123
# 输出:
# ✅ 已从步骤 8 继续执行
```

### 场景 2: RAG 智能检索

```bash
# 1. 索引文档
poetry run jingmai rag index ./docs
# 输出: ✅ 索引完成，共处理 15 个文档

# 2. 语义检索
poetry run jingmai rag search "商品上架流程"
# 输出:
# 📊 检索结果 (3 条)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [相关度 0.92] 商品上架工作流.md
#    1. 准备商品信息 → 2. 验证数据 → 3. 调用API...
#
# [相关度 0.85] 上架检查清单.md
#    □ SKU编码 □ 价格设置 □ 库存配置...
#
# [相关度 0.78] 常见问题.md
#    Q: 上架失败如何处理？

# 3. 查看 RAG 统计
poetry run jingmai rag stats
# 输出:
# 📈 RAG 统计
# 文档数: 15 | 向量数: 3247 | 平均检索时间: 120ms
```

### 场景 3: 记忆管理

```bash
# 1. 添加短期记忆
poetry run jingmai memory short-term "用户偏好简洁输出"
# 输出: ✅ 短期记忆已添加

# 2. 添加长期记忆（实体-类型-内容-描述）
poetry run jingmai memory long-term \
  --entity "用户A" \
  --type "preference" \
  --content "喜欢简洁输出" \
  --description "用户交互偏好"
# 输出: ✅ 长期记忆已存储 (实体: 用户A, 类型: preference)

# 3. 检索记忆
poetry run jingmai memory retrieve "用户偏好"
# 输出:
# 🔍 检索结果 (2 条)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [短期] 用户偏好简洁输出
# [长期] 实体: 用户A | 类型: preference | 内容: 喜欢简洁输出

# 4. 查看记忆统计
poetry run jingmai memory stats
# 输出:
# 📊 记忆统计
# 短期记忆: 12 条 | 长期记忆: 8 个实体
# Redis: ✅ 连接 | Milvus: ✅ 连接

# 5. 导出记忆（⚠️ 涉及文件操作，会提示确认）
poetry run jingmai memory export memory_backup.json
# 输出: ⚠️ 即将导出 20 条记忆到 memory_backup.json，确认？[y/N]

# 6. 导入记忆（⚠️ 会覆盖现有数据，会提示确认）
poetry run jingmai memory import memory_backup.json
# 输出: ⚠️ 警告：导入将覆盖现有记忆，确认？[y/N]
```

### 场景 4: 自定义对话配置

```bash
# 使用特定模型
poetry run jingmai chat --model claude-opus-4-7
# 输出: 🤖 模型已切换到 claude-opus-4-7

# 使用不同提供商
poetry run jingmai chat --provider openai
# 输出: 🔄 提供商已切换到 openai

# 自定义系统提示
poetry run jingmai chat --system-prompt "你是一个商品上架助手"
# 输出: ✅ 系统提示已更新

# 选择输出样式
poetry run jingmai chat --style minimal
# 输出: 📝 输出样式: minimal (简洁模式)

# 保存会话
poetry run jingmai chat --save
# 输出: 💾 会话已保存 | Session ID: sess_xyz789

# 恢复历史会话
poetry run jingmai chat --resume sess_xyz789
# 输出: ✅ 已恢复会话 sess_xyz789 (包含 15 条历史消息)
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

## 🛡️ 系统级 Fallback

当依赖服务不可用时，系统会自动降级：

### Redis 不可用
- **自动降级**: 短期记忆使用内存存储
- **影响**: 进程重启后短期记忆丢失
- **恢复**: Redis 恢复后自动重新连接

### Milvus 不可用
- **自动降级**: 仅使用 BM25 关键词检索
- **影响**: 语义检索精度下降
- **恢复**: Milvus 恢复后自动启用向量检索

### API 限流/错误
- **自动重试**: 指数退避重试 3 次
- **降级策略**: 切换到备用模型（如配置）
- **错误处理**: 返回友好错误提示

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
