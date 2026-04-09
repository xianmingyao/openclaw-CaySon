# jingmai-cli 技能修复报告

## 📅 日期
2026-04-09

## 问题分析

### 原始问题
jingmai-cli 技能目录 `E:\workspace\skills\jingmai-cli\` 缺少根目录的 `SKILL.md` 文件，导致 OpenClaw 无法正确识别该技能。

### 目录结构
```
E:\workspace\skills\jingmai-cli\
├── SKILL.md           ← 【新增】根级别 SKILL.md
├── jingmai-cli.exe    (156MB)
├── README.md
├── version.json
├── .env
├── logs/
└── resources/
    └── ufo_actions/
        └── SKILL.md   (已有)
```

## 解决方案

### 1. 创建根级别 SKILL.md
按照 OpenClaw skill 规范创建 `SKILL.md`，包含：
- YAML frontmatter（name, description, category, version, author）
- 核心文件位置说明
- 依赖服务配置（MySQL/Redis/Milvus/Ollama）
- CLI 命令调用方式（run/status/memory/rag/skills）
- UFO Actions 引用
- 故障排除指南
- 配置文件说明

### 2. 关键配置
| 服务 | 地址 | 端口 |
|------|------|------|
| MySQL | 8.137.122.11 | 3306 |
| Redis | 8.137.122.11 | 6379 |
| Milvus | 8.137.122.11 | 19530 |
| Ollama | localhost | 11434 |

## 修复后状态

| 项目 | 状态 |
|------|------|
| SKILL.md 创建 | ✅ 已创建 (3389 bytes) |
| OpenClaw 识别 | ✅ ready |
| 技能描述 | ✅ 京麦 UFO 智能体自动化 CLI |

## 核心命令速查

```bash
# 执行任务
jingmai-cli.exe run "打开记事本并输入Hello"

# 系统状态
jingmai-cli.exe status --json

# 记忆管理
jingmai-cli.exe memory create "内容" --type long
jingmai-cli.exe memory search "关键词"

# RAG 查询
jingmai-cli.exe rag query "问题" --rerank
```

## OpenClaw Skill 规范要点

1. **必须文件**：`SKILL.md`（根目录）
2. **YAML frontmatter**：name + description（必需）
3. **description** 要包含触发场景关键词
4. **可选**：scripts/、references/、assets/ 目录

## 验证命令

```bash
openclaw skills list | Select-String "jingmai"
```

输出：`✅ ready | 📦 jingmai-cli | 京麦 UFO | openclaw-workspace`
