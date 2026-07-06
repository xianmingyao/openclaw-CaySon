# 京麦 UFO Agent 复刻学习报告

## 📅 学习日期

2026-04-09

## 📂 原始项目信息

| 项目 | 信息 |

|------|------|

| 原始路径 | `E:\PY\jingmai-agent\release` |

| 类型 | Windows UI 自动化 CLI 工具 |

| 核心文件 | jingmai-cli.exe (156MB) + SKILL.md |

## 🔍 原始项目核心功能

### 1. jingmai-cli 任务执行

jingmai-cli run "任务" [选项]

jingmai-cli interactive

jingmai-cli batch [文件]

### 2. 记忆管理

jingmai-cli memory create/search/stats/clear

### 3. RAG 知识库

jingmai-cli rag query/stats

## 🎯 复刻技能：windows-ufo-automation

### 技能信息

| 项目 | 信息 |

|------|------|

| 名称 | windows-ufo-automation |

| 版本 | 1.0.0 |

| 作者 | CaySon (复刻) |

| 路径 | `E:\workspace\skills\windows-ufo-automation` |

### 核心操作分类（12类）

| # | 类别 | 操作数 | 说明 |

|---|------|--------|------|

| 1 | 鼠标点击 | 2 | click, double_click |

| 2 | 文本输入 | 4 | type, set_edit_text, keyboard_input, keypress |

| 3 | 滚动 | 2 | scroll, wheel_mouse_input |

| 4 | 鼠标移动 | 1 | move |

| 5 | 拖拽 | 2 | drag, drag_on_coordinates |

| 6 | 等待 | 1 | wait |

| 7 | 控件级点击 | 2 | click_input, click_on_coordinates |

| 8 | 信息获取 | 3 | texts, summary, annotation |

| 9 | 无操作 | 1 | no_action |

| 10 | 系统级操作 | 3 | run_command, check_process, open_app |

**总计**: 21 个原子操作

### 操作组合模式（10种）

1. 点击 → 输入 → 回车

2. 清空 → 输入

3. 复制粘贴

4. 滚动查找

5. 启动应用并操作（推荐）

6. 分数坐标精确点击（推荐）

7. 检查进程状态后再决定

8. Shift 拖拽选择区域

9. 读取文本内容

10. Ctrl+点击多选

## 📊 复刻差异分析

| 项目 | 原始 jingmai-agent | 复刻版本 |

|------|-------------------|----------|

| 定位 | 独立 CLI 工具 | OpenClaw Skill |

| 调用方式 | 命令行 jingmai-cli | /windows-ufo-automation |

| 记忆管理 | 集成在 CLI 中 | 依赖 OpenClaw 记忆系统 |

| RAG 知识库 | 独立 RAG 模块 | 依赖 OpenClaw RAG |

## 🔑 核心学习点

### 1. UFO 操作设计哲学

- 原子化操作：每个操作职责单一

- 坐标抽象：截图坐标自动转换为屏幕坐标

- 分数坐标：支持归一化坐标，适配不同分辨率

- 智能应用启动：open_app 自动检测进程/托盘/启动

### 2. 操作组合模式

- 预定义组合降低使用复杂度

- 推荐模式帮助用户快速上手

### 3. 与 windows-control skill 对比

| 特性 | windows-control | windows-ufo-automation |

|------|---------------|----------------------|

| 操作数 | ~30 | 21 |

| 分数坐标 | ❌ | ✅ |

| 控件级点击 | ❌ | ✅ |

| 进程检查 | ❌ | ✅ |

| 智能启动 | ❌ | ✅ |

## 📦 技能结构

windows-ufo-automation/

├── SKILL.md (8139 bytes)

├── YAML frontmatter (name, description, category, version, author)

└── Markdown body

├── 坐标系统

├── 12类操作定义

├── 10种组合模式

├── 重要规则

└── 特殊键速查表

## ✅ 验证状态

- [x] 技能创建完成

- [x] SKILL.md 编写完成 (8139 bytes)

- [x] OpenClaw 技能列表验证通过

- [x] 状态：ready

## 🚀 使用方式

/windows-ufo-automation

在对话中触发后，系统会加载 SKILL.md 中的操作定义。