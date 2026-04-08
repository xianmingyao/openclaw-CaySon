---
name: jingmai-agent-cli
description: Windows 桌面自动化 Agent CLI 工具，模拟京麦 UFO 智能体的命令行接口。支持任务执行（run/interactive/batch）、记忆管理（memory CRUD）、RAG 知识库查询、技能管理、系统状态查看等核心功能。当用户需要： (1) 通过 CLI 执行 Windows 自动化任务 (2) 管理短期/长期/工作记忆 (3) 查询 RAG 知识库 (4) 查看系统状态 (5) 批量执行自动化任务 时使用此技能。
---

# Jingmai Agent CLI - Windows 桌面自动化命令行工具

## 概述

Jingmai Agent CLI 是一个强大的 Windows 桌面自动化系统命令行接口，源自京麦 UFO 智能体项目。支持任务执行、记忆管理、RAG 检索、技能管理等功能。

## 核心命令

### 1. 任务执行

#### run - 运行单个任务
```bash
jingmai run "任务描述" [选项]
```

**选项:**
- `-t, --title`: 任务标题
- `-c, --complexity`: 复杂度 (simple/medium/complex)
- `-p, --priority`: 优先级 (1-10)
- `-a, --agent`: Agent 类型 (ufo_agent/rag_agent/planner_agent)
- `-s, --max-steps`: 最大执行步数

**示例:**
```bash
jingmai run "打开记事本并输入Hello World"
jingmai run "整理桌面文件" -t "文件整理" -c simple -p 3
```

#### interactive - 交互式模式
```bash
jingmai interactive [选项]
```

**示例:**
```bash
jingmai interactive
jingmai interactive -a rag_agent
```

#### batch - 批量执行
```bash
jingmai batch <file> [选项]
```

**选项:**
- `-f, --format`: 文件格式 (json/txt/csv)

**示例:**
```bash
jingmai batch tasks.txt
jingmai batch -f json tasks.json
```

---

### 2. 记忆管理

记忆类型: `short`(短期) / `long`(长期) / `working`(工作)

#### 创建记忆
```bash
jingmai memory create "记忆内容" [选项]
```

**选项:**
- `-t, --type`: 记忆类型 (short/long/working)
- `-k, --key`: 记忆键
- `-p, --priority`: 优先级 (low/medium/high/critical)
- `-g, --tags`: 标签
- `--ttl`: 过期时间（秒）

**示例:**
```bash
jingmai memory create "用户偏好深色模式" -t long -p high
```

#### 搜索记忆
```bash
jingmai memory search "查询关键词" [选项]
```

**选项:**
- `-t, --type`: 记忆类型过滤
- `-k, --top-k`: 返回结果数量
- `-g, --tags`: 标签过滤

**示例:**
```bash
jingmai memory search "用户偏好" -t long -k 5
```

#### 记忆统计
```bash
jingmai memory stats
```

#### 清空记忆
```bash
jingmai memory clear [选项]
```

---

### 3. RAG 知识库

#### 查询知识库
```bash
jingmai rag query "查询问题" [选项]
```

**选项:**
- `-k, --top-k`: 返回结果数量
- `-r, --rerank`: 启用重排序

**示例:**
```bash
jingmai rag query "如何配置系统" -k 10
```

#### 知识库统计
```bash
jingmai rag stats
```

---

### 4. 技能管理

#### 列出技能
```bash
jingmai skills list [选项]
```

**选项:**
- `-c, --category`: 按类别筛选
- `-v, --verbose`: 显示详细信息

**示例:**
```bash
jingmai skills list -c automation -v
```

#### 搜索技能
```bash
jingmai skills search "关键词" [选项]
```

**选项:**
- `-k, --top-k`: 返回结果数量

---

### 5. 系统状态

```bash
jingmai status [选项]
```

**选项:**
- `-v, --verbose`: 显示详细信息
- `-j, --json`: JSON 格式输出

---

## UFO Windows UI 自动化操作

CLI 底层依赖 UFO 框架进行 Windows UI 自动化，核心操作见 [references/ufo-actions.md](references/ufo-actions.md)

### 常用操作模式

**模式1: 点击 → 输入 → 回车**
```
click(x, y)           # 点击搜索框
type("搜索词{ENTER}")  # 输入并回车
```

**模式2: 清空 → 输入**
```
click(x, y)                              # 点击输入框
set_edit_text("新内容", clear_current_text=true)
```

**模式3: 复制粘贴**
```
keyboard_input("Ctrl+A")  # 全选
keyboard_input("Ctrl+C")  # 复制
click(target_x, target_y) # 点击目标
keyboard_input("Ctrl+V")  # 粘贴
```

**模式4: 启动应用并操作（推荐）**
```
open_app(app_name="notepad", search_keyword="记事本")
wait(3)  # 等待加载
click(search_x, search_y)
type("内容")
```

---

## 配置

CLI 使用 `.env` 文件配置：

```env
# 应用配置
APP_NAME=京麦智能体系统
APP_VERSION=v1.0.0
DEBUG=True

# 数据库配置
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=jingmai_agent

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379

# Milvus 配置
MILVUS_HOST=localhost
MILVUS_PORT=19530

# LLM 配置
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5
```

---

## 参考文档

- [UFO 操作指南](references/ufo-actions.md) - 完整的 UI 自动化操作列表
- [系统架构](references/architecture.md) - CLI 架构设计

