# jingmai - 京麦智能体

**描述:** 基于 Claude API 的智能对话系统，支持多轮对话、RAG 增强检索、工作流执行和自我进化能力。
**版本:** 0.1.0
**标签:** `agent` `workflow` `memory` `rag` `ecommerce`

## 核心功能

- **智能对话**: 多轮对话、上下文感知
- **RAG 检索**: 向量 + BM25 + 实体 + 图谱 四路召回
- **工作流引擎**: 14 步商品上架流程
- **自我进化**: 性能追踪 + 技能进化
- **双层记忆**: 短期 (Redis) + 长期 (Milvus)

---

## 环境安装

```bash
cd jingmai-cli
poetry install
cp .env.example .env
# 填写 ANTHROPIC_API_KEY
```

---

## 快速开始

```bash
poetry run jingmai chat                    # 交互式聊天
poetry run jingmai chat "你好"            # 单次查询
poetry run jingmai status                  # 系统状态
poetry run jingmai workflow list           # 工作流列表
```

---

## CLI 命令

### 全局命令

| 命令 | 说明 |
|------|------|
| `jingmai chat [PROMPT]` | 交互式聊天 / 单次查询 |
| `jingmai query [PROMPT]` | 单次查询，返回结果 |
| `jingmai run <TASK>` | 执行预定义任务 |
| `jingmai status` | 查看系统状态 |
| `jingmai info` | 系统信息 |
| `jingmai test` | 运行测试 |
| `jingmai examples` | 使用示例 |

### 工作流

```bash
jingmai workflow list                        # 列出所有工作流
jingmai workflow info <id>                  # 查看详情
jingmai workflow execute <id> --context '{}' # 执行
jingmai workflow status <id>                 # 查看状态
jingmai workflow resume <id>                # 恢复执行
```

### 记忆

```bash
jingmai memory short-term <content>         # 添加短期记忆
jingmai memory long-term <e> <t> <c> <d>  # 添加长期记忆
jingmai memory retrieve <query>            # 检索记忆
jingmai memory stats                        # 查看统计
jingmai memory export <file>                # 导出
jingmai memory import <file>                # 导入
```

### RAG

```bash
jingmai rag search <query>                 # 语义检索
jingmai rag index <path>                   # 索引文档
jingmai rag stats                          # RAG 统计
```

### 配置

```bash
jingmai config show                         # 显示配置
jingmai config get <key>                    # 获取值
jingmai config set <key> <value>           # 设置值
jingmai config validate                     # 验证配置
```

---

## chat 命令选项

| 选项 | 说明 |
|------|------|
| `--model <name>` | 指定模型 |
| `--provider <name>` | 提供商: anthropic/openai/ollama |
| `--system-prompt <text>` | 自定义系统提示 |
| `--style <mode>` | 输出样式: minimal/normal/verbose |
| `--resume <session_id>` | 恢复历史会话 |
| `--save` | 退出时保存会话 |
| `--list-sessions` | 列出所有会话 |

---

## 配置 (.env)

```bash
# 必需
ANTHROPIC_API_KEY=your_key_here

# 可选
LLM_PROVIDER=anthropic        # anthropic/openai/ollama
LLM_MODEL=claude-sonnet-4-20250514
REDIS_URL=redis://localhost:6379
MILVUS_HOST=localhost
MILVUS_PORT=19530
LOG_LEVEL=INFO
```

---

## 项目结构

```
jingmai-putaway/
├── SKILL.md              # 本文件
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

## Skill 模式

基于 skill-writing-guide，三种控制模式：

1. **Pipeline**: 工作流关卡（准备→验证→执行→检查→完成）
2. **Revere**: 检查清单（权限→参数→依赖→状态）
3. **Inversion**: 阶段提问（确认类型→收集信息→验证假设→执行）

---

**最后更新**: 2026-04-19
