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

```
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
```

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
```python
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
```

**② 动态代码生成 + 执行**
```python
# 不是直接 import，而是动态构建 Python 脚本执行
# 原因：避免主进程的日志干扰子进程输出
kwargs_str = json.dumps(kwargs, ensure_ascii=False)
script = f"from {module} import {class}; action.execute({kwargs_str})"
```

**③ 分数坐标系统（跨分辨率适配）**
```bash
# 绝对坐标（分辨率相关）
cli-windows-control mouse click --x 1920 --y 1080

# 分数坐标（分辨率无关，0.0-1.0）
cli-windows-control mouse click-fraction --frac-x 0.5 --frac-y 0.5
```

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
```bash
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
```

#### 3.2 交互式 REPL
```bash
cli-windows-control
# 进入交互模式
windows-control> mouse click --x 100 --y 200
windows-control> keyboard type --text "Hello"
windows-control> quit
```

#### 3.3 Python 集成
```python
# 作为 Python 包调用
from cli_anything.windows_control import WindowsControlCLI

cli = WindowsControlCLI()
result = cli.mouse_click(100, 200)
```

### 4. ✅ 优点

1. **接口标准化** - 任何软件都能变成 CLI，AI 只需要知道命令格式
2. **机器友好** - JSON 输出，机器可解析，不需要解析自然语言
3. **隔离安全** - subprocess 隔离，错误不会污染主进程
4. **跨分辨率** - 分数坐标支持，1080p/4K 自适应
5. **扩展性强** - 新增命令只需添加 Click 子命令
6. **即插即用** - pip install 后立即可用

### 5. ❌ 缺点

1. **路径硬编码** - `_JINGMAI_PATH` 写死在代码里
2. **Windows Only** - 深度依赖 Win32 API，无法跨平台
3. **依赖 jingmai-agent** - 必须安装 jingmai-agent 才能用
4. **subprocess 开销** - 每次调用都启动新进程，有性能损失
5. **无重试机制** - action 失败不自动重试

### 6. 🎬 使用场景

| 场景 | 示例 |
|------|------|
| **AI Agent 自动化** | OpenClaw 调用 CLI 控制 Windows 应用 |
| **RPA 流程** | 自动化测试、数据录入、表单填写 |
| **跨应用集成** | 把多个独立软件串联成工作流 |
| **无头浏览器替代** | 直接控制桌面应用而非浏览器 |
| **游戏脚本** | 自动点击、重复操作 |

### 7. 🔧 运行依赖环境

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | >=3.10 | 运行环境 |
| Windows | 10/11 | 操作系统 |
| jingmai-agent | - | 底层 Action 系统 |
| click | >=8.0 | CLI 框架 |
| pyautogui | >=0.9.54 | 鼠标/键盘模拟 |
| pyperclip | >=1.8.2 | 剪贴板操作 |
| Pillow | >=10.0 | 图像处理 |
| psutil | >=5.9 | 系统信息 |

### 8. 🚀 部署使用注意点

1. **jingmai-agent 必须安装** - 在 `E:\PY\jingmai-agent`
2. **PowerShell 特殊处理** - stderr 会触发错误，用 subprocess 隔离
3. **LOGURU 日志压制** - 第三方库日志太多，需要压制
4. **坐标验证** - 点击前建议先用 `ui screenshot` 确认位置
5. **管理员权限** - 部分 Win32 API 需要提升权限

### 9. 🕳️ 避坑指南

| 坑 | 问题 | 解决 |
|-----|------|------|
| **PowerShell stderr** | stderr 被当成错误 | subprocess 隔离 + stderr=open(devnull) |
| **LOGURU 日志** | jingmai-agent 的 loguru 太吵 | `os.environ["LOGURU_LEVEL"] = "ERROR"` |
| **路径硬编码** | jingmai-agent 路径写死 | 改成环境变量或配置文件 |
| **分辨率依赖** | 绝对坐标在不同屏幕失效 | 用 `--frac-x/--frac-y` 分数坐标 |
| **进程残留** | subprocess 超时 | 设置 `timeout=30` |

### 10. 📊 总结

**学习价值：⭐⭐⭐⭐⭐（5星）**

| 维度 | 评分 | 说明 |
|------|------|------|
| 架构设计 | ⭐⭐⭐⭐⭐ | 适配器模式 + 子进程隔离，教科书级别 |
| 工程实践 | ⭐⭐⭐⭐⭐ | 完整 CLI 框架，可直接用于生产 |
| AI 集成 | ⭐⭐⭐⭐⭐ | 专为 AI Agent 设计，JSON 输出标准化 |
| 跨平台 | ⭐ | Windows Only，但这是合理的 |
| 可扩展性 | ⭐⭐⭐⭐⭐ | 添加新命令只需几十行代码 |

**推荐指数：⭐⭐⭐⭐⭐（5星）**

**核心启示：**
> **"任何软件都能变成 AI Agent 可以调用的 CLI"**
> 
> - **接口标准化** > 底层实现细节
> - **机器友好** > 人类友好
> - **隔离安全** > 直接调用

---

## 📚 GitHub 热门项目情报

> 来源：@AI未来 日榜 + @赛博笔记 周榜 + @超级大威

### 🏆 重点推荐项目

| 项目 | ⭐ | 方向 | 推荐 |
|------|-----|------|------|
| **deer-flow** | 46.2k | 字节 SuperAgent | ⭐⭐⭐⭐⭐ |
| **litellm** | 40.6k | LLM Gateway | ⭐⭐⭐⭐⭐ |
| **everything-claude-code** | 18.8k | Claude Code 配置 | ⭐⭐⭐⭐⭐ |
| **x-algorithm** | 12.3k | X 推荐算法 | ⭐⭐⭐⭐⭐ |
| **agency-agents** | - | AI 员工协作 | ⭐⭐⭐⭐⭐ |
| **CLI-Anything** | - | 软件代理适配 | ⭐⭐⭐⭐⭐ |

### 📈 技术趋势

1. **Multi-Agent 爆发** - deer-flow、ruflo、agency-agents 多项目井喷
2. **AI 记忆是刚需** - claude-subconscious、Supermemory、cognee
3. **Claude 生态热** - Anthropic 官方 + Vercel 官方双重背书
4. **TypeScript 崛起** - 4 个 TS 项目和 Python 五五开
5. **大厂开源加速** - 字节跳动、X/Twitter、Vercel

---

## 🔧 已安装 Skills 对应热门项目

| 我已安装 | 对应热门项目 |
|----------|-------------|
| agent-browser | agent-browser (#19) |
| human-browser | - |
| mem0 | Supermemory、cognee |
| self-improving | autoresearch |
| windows-control | **CLI-Anything 架构** |

---

## 📝 学习心得

### Harness Engineering 的核心思想

```
传统开发：人 → GUI → 软件
Harness 思想：AI → CLI → 任何软件
```

**本质：AI Agent 不需要理解软件的复杂 API，只需要知道 CLI 命令格式。**

### 设计模式应用

| 模式 | 应用 |
|------|------|
| **适配器模式** | 把 Win32 API 适配成 CLI 接口 |
| **命令模式** | 每个 action 都是一个命令对象 |
| **门面模式** | CLI 是 jingmai-agent 的统一门面 |
| **隔离模式** | subprocess 隔离实现细节 |

---

## 🚀 下一步学习计划

1. **P0 优先级**
   - 深入研究 deer-flow（字节 SuperAgent，多级子代理架构）
   - 研究 everything-claude-code（Claude Code 配置王炸）
   - 分析 x-algorithm（X 推荐算法开源）

2. **P1 优先级**
   - litellm（LLM Gateway 架构）
   - agent-skills（Vercel 官方技能封装）
   - agency-agents（AI 员工协作模式）

3. **实践计划**
   - 把 windows-control 的 Harness 思想应用到其他软件
   - 尝试封装 Blender/GIMP 的 CLI 接口
   - 研究 Multi-Agent 协作模式

---

## 📊 今日总结

| 项目 | 内容 |
|------|------|
| **GitHub 项目** | 20+ 热门项目分析 |
| **核心技能** | Harness Engineering 深度解析 |
| **设计模式** | 适配器 + 命令 + 门面 + 隔离 |
| **工程价值** | 把任何软件变成 AI 可调用接口 |
| **推荐指数** | ⭐⭐⭐⭐⭐（必学） |

