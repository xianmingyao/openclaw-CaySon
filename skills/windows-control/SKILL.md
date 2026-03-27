---
name: windows-control
description: Windows UI Automation CLI 技能 - 通过 CLI-Anything 架构封装 jingmai-agent action 系统，实现生产级 Windows 自动化控制。pip install 后可用 cli-windows-control 命令，支持 mouse/keyboard/window/ui/system/file 全操作。
category: automation
version: 2.0.0
author: jingmai-agent + CLI-Anything
---

# Windows Control Skill v2.0

通过 **CLI-Anything** 架构封装 jingmai-agent action 系统，打造真正的生产级 Windows 自动化 CLI。

## 核心改进（相比 v1）

| 问题 | 解决方案 |
|------|----------|
| Action 是 Pydantic 模型，无法 dict.get | 内部 `_run_action()` 统一转换为 dict |
| emoji 在 Windows 控制台报错 | 使用 ASCII 字符（`[OK]`/`[FAIL]`） |
| 需要手动写 Python 代码调用 | 一条命令直接执行：`cli-windows-control mouse click --x 100 --y 200` |
| 输出格式不统一 | JSON 模式 + 人类可读模式 |

## 安装

```bash
cd E:\workspace\skills\windows-control\agent-harness
pip install -e .
```

## 使用方式

### 方式 1：CLI 命令（推荐）

```bash
# 鼠标操作
cli-windows-control mouse click --x 100 --y 200
cli-windows-control mouse double-click --x 500 --y 300
cli-windows-control mouse move --x 400 --y 200
cli-windows-control mouse drag --start-x 100 --start-y 100 --end-x 400 --end-y 300

# 键盘操作
cli-windows-control keyboard type --text "Hello World{ENTER}"
cli-windows-control keyboard press --keys enter
cli-windows-control keyboard hotkey --keys ctrl+c

# 滚动操作
cli-windows-control scroll scroll --scroll-y -3
cli-windows-control scroll wheel --amount 5

# 窗口操作
cli-windows-control window list
cli-windows-control window info
cli-windows-control window open --name notepad

# UI 采集
cli-windows-control ui screenshot
cli-windows-control ui screenshot --full
cli-windows-control ui tree --depth 10
cli-windows-control ui controls --depth 8

# 系统操作
cli-windows-control system info
cli-windows-control system run --command "dir" --shell cmd
cli-windows-control system process --name python
cli-windows-control system wait --seconds 2

# 文件操作
cli-windows-control file list --path . --pattern "*.py"
cli-windows-control file read --path test.txt
cli-windows-control file write --path output.txt --content "Hello"
```

### 方式 2：JSON 输出（AI Agent 专用）

```bash
cli-windows-control --json mouse click --x 100 --y 200
cli-windows-control --json window list
cli-windows-control --json system info
```

### 方式 3：交互式 REPL

```bash
cli-windows-control
# 进入交互模式
windows-control> mouse click --x 100 --y 200
windows-control> keyboard type --text "Hello"
windows-control> quit
```

### 方式 4：Python 模块调用

```python
import sys
sys.path.insert(0, r"E:\PY\jingmai-agent")

import asyncio
from app.service.actions.mouse_actions import ClickAction

action = ClickAction()
action.set_context(1.0, (1920, 1080))
result = asyncio.run(action.execute(x=100, y=200, button="left"))
print(result.success, result.data, result.metadata)
```

## 命令分类索引

| 分类 | 命令数 | 核心命令 |
|------|--------|----------|
| 🖱️ 鼠标 | 7 | click, double-click, move, drag, click-input, click-fraction, drag-fraction |
| ⌨️ 键盘 | 4 | type, set-text, press, hotkey |
| 📜 滚动 | 2 | scroll, wheel |
| 🖥️ 窗口 | 3 | list, info, open |
| 🖼️ UI采集 | 4 | screenshot, tree, controls, targets |
| ⏱️ 系统 | 4 | info, run, process, wait |
| 📁 文件 | 4 | list, read, write, exists |

## CLI-Anything 架构说明

本技能基于 [CLI-Anything](https://github.com/HKUDS/CLI-Anything) 架构设计：

```
agent-harness/
├── setup.py                          # pip install 入口
├── cli_anything/windows_control/
│   ├── __init__.py                   # 包初始化
│   ├── __main__.py                   # python -m 入口
│   ├── windows_control_cli.py        # Click CLI 主程序
│   ├── README.md                     # 使用文档
│   ├── utils/
│   │   └── repl_skin.py             # REPL 样式皮肤
│   ├── skills/
│   │   └── SKILL.md                  # AI Agent 发现文件
│   └── tests/
│       └── test_cli.py               # 测试套件
```

**关键设计**：
- 所有操作通过 `exec(command="cli-windows-control ...")` 调用
- JSON 输出模式确保 AI 可解析
- REPL 模式支持交互式调试
- 兼容 jingmai-agent 的所有 action

## 依赖说明

```txt
click>=8.0.0          # CLI 框架
prompt-toolkit>=3.0.0 # REPL 支持
pyautogui>=0.9.54     # 鼠标/键盘
pyperclip>=1.8.2      # 剪贴板
Pillow>=10.0.0        # 截图
psutil>=5.9.0         # 系统信息
```

## 通过 exec 调用完整示例

### 打开记事本并输入文字

```python
# 1. 打开记事本
exec(command="cli-windows-control window open --name notepad")

# 2. 等待窗口出现
exec(command="cli-windows-control system wait --seconds 2")

# 3. 输入文字
exec(command="cli-windows-control keyboard type --text \"Hello from CLI!{ENTER}\"")

# 4. 全选并复制
exec(command="cli-windows-control keyboard hotkey --keys ctrl+a")
exec(command="cli-windows-control keyboard hotkey --keys ctrl+c")
```

### 获取窗口信息并点击

```python
# 1. 列出所有窗口
exec(command="cli-windows-control --json window list")
# 返回 JSON: {"success": true, "data": {"apps": [...]}}

# 2. 获取 UI 控件
exec(command="cli-windows-control --json ui controls --depth 8")

# 3. 点击指定坐标
exec(command="cli-windows-control mouse click --x 400 --y 300")
```

## 参考资源

- **jingmai-agent actions**: `E:\PY\jingmai-agent\app\service\actions/`
- **CLI-Anything 源码**: `E:\PY\CLI-Anything/`
- **HARNESS.md**: `E:\PY\CLI-Anything\cli-anything-plugin/HARNESS.md`
