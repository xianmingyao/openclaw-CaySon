# WebMCP + 浏览器自动化MCP技术深度报告

> 研究日期：2026-04-02

> 关联项目：browser-use CLI 2.0、mcp-browser-use、WebMCP

---

## 1. 🎯 WebMCP 是什么

**WebMCP (Web Model Context Protocol)** 是 **Chrome 官方于 2026年2月10日** 发布的新Web标准，让网站可以向AI Agent暴露结构化工具。

**核心定位：** 把网站变成 AI Agent 的工具箱 —— 不再需要"假装人类"的截图式浏览。

**发布状态：**

- Chrome 146+ (Canary) 已支持

- 正式版预计 2026年中发布

- 微软 Edge 预计后续支持

---

## 2. 📝 WebMCP 核心概念

### 2.1 解决什么问题

| 传统方式 | WebMCP方式 |

|---------|-----------|

| AI截图理解页面 | 网站直接暴露工具API |

| 67%计算开销（benchmark数据） | 直接工具调用，~89% token节省 |

| 猜测UI元素位置 | 结构化schema定义 |

| 截图+再验证 | 确定性操作 |

### 2.2 两种API模式

**声明式 (Declarative) - 适合表单**

<!-- 网站直接暴露搜索工具 -->

<form webmcp:tool="search">

<input name="query" webmcp:param="query" />

<button type="submit">搜索</button>

</form>

**命令式 (Imperative) - 适合复杂逻辑**

// JavaScript注册工具

navigator.webmcp.registerTool({

name: "bookFlight",

description: "预订航班",

parameters: {

from: { type: "string" },

to: { type: "string" },

date: { type: "string" }

},

execute: async ({from, to, date}) => {

// 调用现有业务逻辑

return await bookingSystem.search({from, to, date});

}

});

---

## 3. 📊 WebMCP 技术架构

### 3.1 工作原理

┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐

│   AI Agent      │ ───▶ │   Chrome Browser  │ ───▶ │   Website        │

│  (Claude/Cursor)│      │   (WebMCP Client) │      │ (WebMCP Server)  │

└─────────────────┘      └──────────────────┘      └─────────────────┘

│                           │

│   MCP Protocol            │

│   (JSON-RPC over stdio)   │

└───────────────────────────┘

### 3.2 与MCP的关系

| 维度 | MCP | WebMCP |

|------|-----|--------|

| 目标 | AI Agent与外部工具连接 | 网站向AI Agent暴露工具 |

| 运行环境 | 本地/服务端 | 浏览器内 |

| 传输 | stdio/HTTP/SSE | 浏览器API |

| 典型用途 | 文件系统、数据库、API | 网页表单、交互操作 |

**关系：** WebMCP 灵感来自MCP，专为浏览器场景设计，可以看作是"MCP的浏览器实现"

---

## 4. ⚡ browser-use MCP 服务详解

### 4.1 官方MCP服务器

browser-use 内置 MCP 服务器，位于 `browser_use.mcp` 模块。

**启动方式：**

# 方式1：uvx (推荐)

uvx browser-use --mcp

# 方式2：python模块

python -m browser_use.mcp

# 方式3：CLI

browser-use --mcp

**配置示例 (Claude Desktop)：**

{

"mcpServers": {

"browser-use": {

"command": "uvx",

"args": ["browser-use[cli]", "--mcp"],

"env": {

"OPENAI_API_KEY": "sk-..."

}

}

}

}

### 4.2 提供的工具 (Tools)

| 工具 | 说明 |

|------|------|

| `browser_navigate` | 导航到URL |

| `browser_click` | 点击元素 |

| `browser_type` | 输入文本 |

| `browser_screenshot` | 截图 |

| `browser_get_state` | 获取页面状态 |

| `browser_execute_js` | 执行JavaScript |

| `browser_extract` | LLM提取数据 |

| `browser_go_back` | 后退 |

| `browser_scroll` | 滚动 |

| `browser_wait` | 等待 |

### 4.3 mcp-browser-use 第三方包

**GitHub:** github.com/Saik0s/mcp-browser-use

**版本:** 0.1.5