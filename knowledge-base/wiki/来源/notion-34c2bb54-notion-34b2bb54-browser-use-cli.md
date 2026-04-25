# browser-use CLI 2.0 技术深度报告

> 来源：抖音大力AI视频 + 官方文档 + 实际测试

> 日期：2026-04-02

> 版本：0.12.5

## 1. 🎯 这是什么

**browser-use** 是 YC 孵化的 AI 浏览器自动化明星项目，GitHub **78,000+ Stars**，刚发布 CLI 2.0 版本。

**核心定位：** 让 AI Agent 自己操作浏览器 —— 专为 Claude Code、Cursor、Codex 等 AI 编码代理设计。

**融资背景：** YC 孵化，Felicis Ventures 领投 1700 万美元种子轮，Paul Graham 个人参投。

---

## 2. 📝 关键功能点

### 2.1 命令矩阵

| 命令 | 功能 | 示例 |

|------|------|------|

| `open` | 打开URL | `browser-use open "https://baidu.com"` |

| `click` | 点击元素 | `browser-use click 60` |

| `type` | 输入文本 | `browser-use type "hello"` |

| `input` | 输入到指定元素 | `browser-use input 17 "text"` |

| `scroll` | 滚动页面 | `browser-use scroll 300` |

| `back` | 后退 | `browser-use back` |

| `screenshot` | 截图 | `browser-use screenshot` |

| `state` | 获取DOM树 | `browser-use state` |

| `switch` | 切换标签 | `browser-use switch 2` |

| `close-tab` | 关闭标签 | `browser-use close-tab` |

| `keys` | 发送键盘 | `browser-use keys "Enter"` |

| `select` | 下拉选择 | `browser-use select 60 "value"` |

| `upload` | 文件上传 | `browser-use upload 60 "C:\file.png"` |

| `eval` | 执行JS | `browser-use eval "document.title"` |

| `extract` | LLM提取 | `browser-use extract "提取数据"` ⚠️未实现 |

| `hover` | 悬停 | `browser-use hover 60` |

| `dblclick` | 双击 | `browser-use dblclick 60` |

| `rightclick` | 右键 | `browser-use rightclick 60` |

| `cookies` | Cookie管理 | `browser-use cookies get` |

| `wait` | 等待条件 | `browser-use wait 3` |

| `get` | 获取信息 | `browser-use get url` |

| `python` | 执行Python | `browser-use python "print('hi')"` |

| `tunnel` | Cloudflare隧道 | `browser-use tunnel` |

| `close` | 关闭浏览器 | `browser-use close` |

| `sessions` | 列出会话 | `browser-use sessions` |

| `cloud` | 云浏览器API | `browser-use cloud login` |

| `profile` | 浏览器配置 | `browser-use profile` |

| `mcp` | MCP服务器模式 | `browser-use --mcp` |

### 2.2 全局参数

| 参数 | 说明 |

|------|------|

| `--headed` | 显示浏览器窗口（默认无头） |

| `--profile [名称]` | 使用真实Chrome用户配置 |

| `--cdp-url URL` | 连接远程Chrome |

| `--connect` | 自动发现并连接运行中的Chrome |

| `--session 名称` | 指定会话名（默认default） |

| `--json` | JSON格式输出 |

| `--mcp` | MCP服务器模式 |

| `--template 文件` | 生成模板文件 |

---

## 3. ⚡ 怎么使用

### 3.1 安装

# Python包安装

pip install browser-use

# 检查版本

browser-use --version

# 安装Chromium（需要playwright）

playwright install chromium

# 或用browser-use安装

browser-use install

### 3.2 基础操作

# 打开页面（无头模式）

browser-use open "https://baidu.com"

# 打开页面（显示窗口）

browser-use --headed open "https://baidu.com"

# 获取页面状态（DOM树）

browser-use state

# 点击元素（按索引）

browser-use click 60

# 截图

browser-use screenshot

# 执行JavaScript

browser-use eval "document.title"

### 3.3 Windows编码问题解决

# 方案1：环境变量

$env:PYTHONIOENCODING="utf-8"

browser-use open "https://baidu.com"

# 方案2：永久设置（用户环境变量）

[Environment]::SetEnvironmentVariable("PYTHONIOENCODING", "utf-8", "User")

### 3.4 MCP服务器模式

# 启动MCP服务器

browser-use --mcp

# MCP模式下AI Agent可通过JSON-RPC控制浏览器

### 3.5 Python API（面向AI Agent）

from browser_use import Controller

controller = Controller()

# AI Agent通过action描述来控制浏览器

result = await controller.act("点击搜索框，然后输入'天气'，点击搜索")

---

## 4. ✅ 优点

| 优点 | 说明 |

|------|------|

| 🎯 **专为AI设计** | 元素引用轻量级，Token消耗减少50%（官方数据） |

| ⚡ **速度快** | 2.0版本比Playwright快2倍 |

| 🔌 **MCP原生** | 可作为MCP服务器供AI Agent调用 |

| 🌐 **多浏览器** | 支持Headless/Chrome Profile/Cloud |

| 🧠 **LLM集成** | 支持OpenAI/Anthropic/Google/Groq/Ollama |