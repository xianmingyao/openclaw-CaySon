# 今日学习总结 2026-03-30

> 整理时间：2026-03-30 08:10

> 核心主题：Harness Engineering 驾驭工程 深度解析 + GitHub 热门项目

---

## 🎯 Harness Engineering 驾驭工程深度解析

> 来源：`E:\workspace\skills\windows-control\agent-harness\` 源码分析

### 1. 🎯 这是什么（核心概念）

**Harness = 驾驭系统 / 测试框架**

Harness Engineering 是港大团队（HKUDS）的核心理念：**把任何软件系统封装成 AI Agent 可以调用的 CLI 接口**。

CLI-Anything = **CLI 封装任意软件** → AI Agent 通过标准化 CLI 调用任意软件

┌─────────────────────────────────────────────────────────────┐

│                    AI Agent (大脑)                          │

├─────────────────────────────────────────────────────────────┤

│                   CLI Harness (标准接口)                    │

│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │

│  │ Windows  │ │ Blender  │ │  GIMP    │ │  OBS     │      │

│  │  Control │ │ Control  │ │ Control  │ │ Control  │      │

│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘      │

│       │            │            │            │            │

│  ┌────▼────────────▼────────────▼────────────▼────┐      │

│  │          jingmai-agent Action System           │      │

│  │     (Win32/COM/UIA 原生 API 调用层)            │      │

│  └────────────────────────────────────────────────┘      │

└─────────────────────────────────────────────────────────────┘

### 2. 📝 关键功能点

#### 2.1 核心架构设计

| 层级 | 组件 | 功能 |

|------|------|------|

| **接口层** | Click CLI | 命令行参数解析 + 子命令分组 |

| **隔离层** | subprocess | 隔离 stderr、避免 PowerShell 错误污染 |

| **执行层** | jingmai-agent | 调用 Win32/COM/UIA 原生 API |

| **适配层** | Action System | 把原生 API 适配成标准化响应 |

#### 2.2 核心技术实现

**① 子进程隔离模式（核心创新）**

def _run_action(action_class, **kwargs):

"""通过 subprocess 动态执行 action，避免 stderr 污染"""

# 关键点：PowerShell 把 stderr 当成错误

# 解决方案：subprocess 隔离 + stderr 重定向到 /dev/null

script = f"""

import sys, os, asyncio, json

sys.path.insert(0, r'{_JINGMAI_PATH}')

os.environ['LOGURU_LEVEL'] = 'ERROR'  # 压制第三方日志

sys.stderr = open(os.devnull, 'w')    # 丢弃 stderr

# ... 执行 action ...

"""

result = subprocess.run([python, "-c", script], ...)

**② 动态代码生成 + 执行**

# 不是直接 import，而是动态构建 Python 脚本执行

# 原因：避免主进程的日志干扰子进程输出

kwargs_str = json.dumps(kwargs, ensure_ascii=False)

script = f"from {module} import {class}; action.execute({kwargs_str})"

**③ 分数坐标系统（跨分辨率适配）**

# 绝对坐标（分辨率相关）

cli-windows-control mouse click --x 1920 --y 1080

# 分数坐标（分辨率无关，0.0-1.0）

cli-windows-control mouse click-fraction --frac-x 0.5 --frac-y 0.5

#### 2.3 命令体系

| 命令组 | 命令 | 功能 |

|--------|------|------|

| **mouse** | click, double-click, move, drag, click-input, click-fraction | 鼠标控制 |

| **keyboard** | type, set-text, press, hotkey | 键盘控制 |

| **scroll** | scroll, wheel | 滚轮控制 |

| **window** | list, info, open | 窗口管理 |

| **ui** | screenshot, tree, controls, targets | UI 元素采集 |

| **system** | info, run, process, wait | 系统操作 |

| **file** | list, read, write, exists | 文件操作 |

### 3. ⚡ 怎么使用

#### 3.1 一键命令模式

# 安装

cd agent-harness && pip install -e .

# 鼠标操作

cli-windows-control mouse click --x 100 --y 200

# 键盘操作

cli-windows-control keyboard type --text "Hello World"

# 窗口管理

cli-windows-control window list

# UI 截图

cli-windows-control ui screenshot

# 系统信息

cli-windows-control system info

# JSON 输出（AI 专用）

cli-windows-control --json window list

#### 3.2 交互式 REPL

cli-windows-control

# 进入交互模式

windows-control> mouse click --x 100 --y 200

windows-control> keyboard type --text "Hello"

windows-control> quit

#### 3.3 Python 集成

# 作为 Python 包调用

from cli_anything.windows_control import WindowsControlCLI

cli = WindowsControlCLI()

result = cli.mouse_click(100, 200)

### 4. ✅ 优点

1. **接口标准化** - 任何软件都能变成 CLI，AI 只需要知道命令格式

2. **机器友好** - JSON 输出，机器可解析，不需要解析自然语言

3. **隔离安全** - subprocess 隔离，错误不会污染主进程

4. **跨分辨率** - 分数坐标支持，1080p/4K 自适应

5. **扩展性强** - 新增命令只需添加 Click 子命令

6. **即插即用** - pip install 后立即可用