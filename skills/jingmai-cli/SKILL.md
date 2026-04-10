---
name: jingmai-cli
description: 京麦 UFO 智能体自动化 CLI 工具。触发场景：Windows 应用自动化控制、任务执行、记忆管理、RAG 检索。jingmai-cli.exe 是核心可执行文件，支持 run/interactive/batch/status/memory/rag/skills 等命令。依赖 MySQL/Redis/Milvus 服务。
category: automation
version: 1.0.0
author: jingmai-agent
---

# 京麦 UFO 智能体 CLI 工具 v1.0

京麦 UFO 智能体命令行工具提供了强大的智能体自动化系统接口。

## 核心文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| 可执行文件 | `E:\workspace\skills\jingmai-cli\jingmai-cli.exe` | 主程序 |
| 配置文件 | `E:\workspace\skills\jingmai-cli\.env` | 环境配置 |
| UFO Actions | `resources/ufo_actions/SKILL.md` | UI 自动化操作定义 |

## 依赖服务（必须先启动）

| 服务 | 配置 | 说明 |
|------|------|------|
| MySQL | `8.137.122.11:3306` | 数据库 |
| Redis | `8.137.122.11:6379` | 缓存/记忆 |
| Milvus | `8.137.122.11:19530` | 向量数据库 |
| Ollama | `localhost:11434` | LLM 服务 |

## CLI 命令调用

### 1. 任务执行（最常用）

```bash
# 简单任务
jingmai-cli.exe run "打开记事本并输入Hello World"

# 完整参数
jingmai-cli.exe run "任务描述" --title "标题" --complexity simple --priority 5 --agent ufo_agent --max-steps 20

# 进入交互模式
jingmai-cli.exe interactive

# 批量执行
jingmai-cli.exe batch tasks.txt
```

**参数说明**：
| 参数 | 缩写 | 可选值 | 说明 |
|------|------|--------|------|
| `--title` | `-t` | 字符串 | 任务标题 |
| `--complexity` | `-c` | `simple/medium/complex` | 任务复杂度 |
| `--priority` | `-p` | 1-10 | 优先级 |
| `--agent` | `-a` | `ufo_agent/rag_agent/planner_agent` | Agent 类型 |
| `--max-steps` | `-s` | 数字 | 最大执行步数 |

### 2. 系统状态

```bash
# 基本状态
jingmai-cli.exe status

# 详细信息
jingmai-cli.exe status --verbose

# JSON 格式输出
jingmai-cli.exe status --json
```

### 3. 记忆管理

```bash
# 创建记忆
jingmai-cli.exe memory create "记忆内容" --type long --priority high --tags "标签1,标签2"

# 搜索记忆
jingmai-cli.exe memory search "查询关键词" --top-k 5

# 记忆统计
jingmai-cli.exe memory stats

# 清空记忆
jingmai-cli.exe memory clear
```

### 4. RAG 知识库

```bash
# 查询知识库
jingmai-cli.exe rag query "查询问题" --top-k 5 --rerank

# 知识库统计
jingmai-cli.exe rag stats
```

### 5. 技能管理

```bash
# 列出技能
jingmai-cli.exe skills list --category automation

# 搜索技能
jingmai-cli.exe skills search "关键词" --top-k 10
```

## UFO Actions（UI 自动化）

jingmai-cli 内置 UFO Actions，定义在 `resources/ufo_actions/SKILL.md`，包含：

| 类别 | 操作 |
|------|------|
| 鼠标点击 | click, double_click |
| 文本输入 | type, set_edit_text, keyboard_input, keypress |
| 滚动 | scroll, wheel_mouse_input |
| 鼠标移动 | move |
| 拖拽 | drag, drag_on_coordinates |
| 控件级点击 | click_input, click_on_coordinates |
| 信息获取 | texts, summary, annotation |
| 系统操作 | run_command, check_process, open_app |

详细操作定义见 `resources/ufo_actions/SKILL.md`

## 执行任务流程

```
1. 检查依赖服务是否运行
   - MySQL: 8.137.122.11:3306
   - Redis: 8.137.122.11:6379
   - Milvus: 8.137.122.11:19530
   - Ollama: localhost:11434

2. 执行任务命令
   jingmai-cli.exe run "任务描述"

3. 任务会自动：
   - 连接 LLM (Ollama)
   - 截取屏幕
   - 分析 UI
   - 执行操作
   - 返回结果
```

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `Can't connect to MySQL` | MySQL 未运行 | 检查 `8.137.122.11:3306` |
| `Redis connection failed` | Redis 未运行 | 检查 `8.137.122.11:6379` |
| `Agent 初始化失败` | Ollama 未运行 | 启动 Ollama 服务 |
| `任务超时` | 网络或服务慢 | 增加 `--max-steps` |

## 配置编辑

配置文件：`E:\workspace\skills\jingmai-cli\.env`

关键配置项：
```env
# LLM 配置
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=qwen3-vl:32b-instruct

# MySQL 配置
MYSQL_HOST=8.137.122.11
MYSQL_PORT=3306
MYSQL_DATABASE=jingmai_agent

# Redis 配置
REDIS_HOST=8.137.122.11
REDIS_PORT=6379

# Milvus 配置
MILVUS_HOST=8.137.122.11
MILVUS_PORT=19530
```

### 使用技能时候行为准则，必须遵守的

```
在使用jingmai-cli技能执行脚本操作完成后，必须严格按照以下步骤立即执行操作：

1. 系统检查与分析：全面扫描并分析"resources\\screenshots"目录下的所有截图文件，确保完整捕获执行过程中的界面状态、错误提示及关键操作节点，截图分析需包含时间戳验证、界面元素识别及异常状态标记。

2. 日志审查流程：详细审查"logs\\app.log"和"logs\\main.log"两个日志文件中的完整运行记录，重点关注错误信息、警告提示、性能指标及关键执行步骤的时间序列，需建立日志异常识别机制，对ERROR、WARNING级别日志进行重点标记与分析。

3. 报告生成标准：基于截图分析结果与日志审查结论，编制结构化的运行终结报告与专业指导建议。报告内容必须体现"老师一把手带实现学生"的教学架构理念，包含：执行过程复盘、问题诊断分析、优化建议、知识点提炼及实操指导等模块，确保内容兼具专业性与教学指导性。

4. 文件管理规范：将总结报告与指导建议完整保存至"resources\\harness\\opinion.md"文件。保存前必须执行文件内容彻底清空操作，确保每次写入均为全新的总结意见，避免历史内容残留影响报告准确性。文件编码格式统一为UTF-8，排版需符合Markdown标准规范。

5. 特殊规则处理机制：若执行过程中出现特殊场景需要进行规则总结时，必须首先完整读取"resources\\harness\\special.md"文件内容，基于现有规则框架添加新的特殊场景处理规则，整合更新后重新保存至原文件路径，确保特殊规则库的持续迭代与完善。
```
