# mcporter - MCP TypeScript/CLI调用工具

> 2026-04-03 | 来源：抖音@技术爬爬虾

---

## 一句话

**mcporter = 用TypeScript或CLI调用MCP服务器，把MCP伪装成简单的本地函数**

---

## 项目信息

| 项目 | 信息 |

|------|------|

| **GitHub** | `steipete/mcporter` |

| **Stars** | **3.6k** |

| **npm** | `mcporter` |

| **官网** | mcporter.dev |

| **版本** | v0.8.1 |

| **许可证** | MIT |

| **平台** | macOS/Linux/Windows |

---

## 核心功能

| 功能 | 说明 |

|------|------|

| **TypeScript运行时** | 直接用TS代码调用MCP服务器 |

| **CLI工具** | 命令行调用MCP服务器 |

| **代码生成** | 自动生成类型定义 |

| **守护进程管理** | 管理MCP服务器进程 |

| **多协议支持** | HTTP + stdio |

---

## 安装

# npm全局安装（推荐）

npm install -g mcporter

# 验证安装

mcporter --version

---

## 演示案例：调用文件系统MCP

**目标：** 用mcporter执行文件操作（ls/cat等）

# Step 1: 启动文件系统MCP服务器

mcporter serve filesystem --path /tmp

# Step 2: 列出可用工具

mcporter tools list

# 输出示例：

# - filesystem.read_file

# - filesystem.write_file

# - filesystem.list_directory

# Step 3: 调用工具

mcporter call filesystem.read_file --path /tmp/test.txt

# Step 4: 用TypeScript调用（更优雅）

cat > example.ts << 'EOF'

import { createMCPClient } from 'mcporter';

const client = await createMCPClient({

server: 'filesystem',

args: ['--path', '/tmp']

});

// 直接调用，像本地函数一样

const content = await client.call('read_file', { path: '/tmp/test.txt' });

console.log(content);

EOF

npx ts-node example.ts

---

## 与现有工具关系

AI Agent调用工具

├── MCP协议

│   ├── mcporter ⭐ - TypeScript/CLI调用MCP

│   ├── WebMCP - 浏览器MCP

│   └── 官方MCP Server

│

├── CLI方案

│   ├── CLI-Anything - 软件→CLI

│   └── OpenCLI - 网站→CLI

│

└── GUI自动化

└── browser-use - 浏览器GUI

---

## 优缺点

| ✅ 优点 | ❌ 缺点 |

|---------|---------|

| 类型安全（TypeScript原生） | 需要Node.js环境 |

| CLI灵活 | 3.6k Stars，生态较小 |

| 多协议支持 | 学习曲线 |

| 代码生成自动补全 | |

---

## 记住这个

mcporter → TypeScript/CLI调用MCP

CLI-Anything → 软件→CLI

OpenCLI → 网站→CLI

browser-use → 浏览器GUI

---

## 文档

- `knowledge/cli-quick-start.md` - CLI工具速查

- `knowledge/mcporter.md` - 本文档