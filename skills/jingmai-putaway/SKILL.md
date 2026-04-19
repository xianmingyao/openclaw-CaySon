# jingmai-putaway - 京麦智能体

**描述:** 基于 Claude API 的智能对话系统，支持多轮对话、RAG 增强检索、工作流执行和自我进化能力。
**版本:** 0.1.0
**作者:** 京麦团队
**标签:** `agent` `workflow` `memory` `rag` `ecommerce`

---

## 核心功能

- **智能对话管理**: 支持多轮对话和上下文感知
- **RAG 增强检索**: 向量数据库、多路召回、重排序
- **京麦工作流**: 14 步商品上架流程
- **自我进化引擎**: 基于性能反馈的自动优化
- **双层记忆系统**: 短期（Redis）+ 长期（Milvus）

---

## 快速开始

```bash
cd jingmai-cli

# 安装依赖
poetry install

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入 ANTHROPIC_API_KEY

# 启动交互式聊天
poetry run jingmai chat

# 单次查询
poetry run jingmai chat "你好"

# 列出所有工作流
poetry run jingmai workflow list

# 查看记忆统计
poetry run jingmai memory stats
```

---

## CLI 命令

| 命令 | 说明 |
|------|------|
| `jingmai chat [PROMPT]` | 交互式聊天 / 单次查询 |
| `jingmai query [PROMPT]` | 单次查询并返回结果 |
| `jingmai run <TASK>` | 执行预定义任务 |
| `jingmai workflow list` | 列出所有工作流 |
| `jingmai workflow info <id>` | 查看工作流详情 |
| `jingmai workflow execute <id>` | 执行工作流 |
| `jingmai workflow status <id>` | 查看执行状态 |
| `jingmai memory short-term <content>` | 添加短期记忆 |
| `jingmai memory long-term <entity> <type> <content> <desc>` | 添加长期记忆 |
| `jingmai memory retrieve <query>` | 检索记忆 |
| `jingmai memory stats` | 查看记忆统计 |
| `jingmai memory export <file>` | 导出记忆 |
| `jingmai memory import <file>` | 导入记忆 |
| `jingmai rag search <query>` | RAG 语义检索 |
| `jingmai rag index <path>` | 索引文档 |
| `jingmai config show` | 显示配置 |
| `jingmai config set <key> <value>` | 设置配置 |
| `jingmai status` | 查看系统状态 |
| `jingmai info` | 显示系统信息 |
| `jingmai test` | 运行测试 |
| `jingmai examples` | 显示使用示例 |

---

## 环境配置

```bash
# .env 文件
ANTHROPIC_API_KEY=your_api_key_here
REDIS_URL=redis://localhost:6379
MILVUS_HOST=localhost
MILVUS_PORT=19530
LOG_LEVEL=INFO
```

---

## 详细文档

完整命令文档和架构设计请参阅：
- [jingmai-cli/SKILL.md](jingmai-cli/SKILL.md)

---

## 项目结构

```
jingmai-putaway/
├── SKILL.md              # 本文件（技能入口）
└── jingmai-cli/          # CLI 主目录
    ├── SKILL.md          # 完整技能文档
    ├── cli/              # 命令行工具
    ├── core/             # 核心模块
    │   ├── agent/        # Agent 实现
    │   ├── context/      # 上下文管理
    │   ├── engine/       # 查询引擎
    │   ├── skills/       # 技能系统
    │   └── tools/        # 工具定义
    ├── plugins/          # 插件系统
    │   ├── jingmai_workflow/
    │   ├── jingmai_evolution/
    │   ├── jingmai_memory/
    │   └── jingmai_rag/
    ├── tests/            # 测试文件
    └── pyproject.toml    # 项目配置
```

---

**最后更新**: 2026-04-19
