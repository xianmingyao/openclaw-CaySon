# 技能1：Browser-Automation 浏览器自动化深度分析

> 来源：`E:\workspace\skills\openclaw-agent-browser\` 源码 + 命令参考

---

## 🎯 这是什么（简介）

**agent-browser = AI 时代的浏览器自动化 CLI**

专为 AI Agent 设计的无头浏览器工具，通过 `@e1` 这种引用系统，让 AI 能够：

- 打开网页

- 理解页面元素

- 交互操作（点击、填表）

- 提取数据

- 截图/PDF

┌─────────────────────────────────────────────────────────────┐

│                     AI Agent (大脑)                          │

├─────────────────────────────────────────────────────────────┤

│                 agent-browser (浏览器控制)                   │

│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │

│  │  open   │ │snapshot │ │  click  │ │  fill   │       │

│  │  导航   │ │  快照   │ │  点击   │ │  填写   │       │

│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │

│       │            │            │            │             │

│  ┌────▼────────────▼────────────▼────────────▼────┐       │

│  │              Chromium / Chrome CDP              │       │

│  │            (无头浏览器 + 开发者协议)             │       │

│  └────────────────────────────────────────────────┘       │

└─────────────────────────────────────────────────────────────┘

### 核心创新：引用系统（Ref）

传统爬虫需要：

1. 分析页面结构

2. 写 CSS 选择器/XPath

3. 调试 selector

4. 维护 selector（页面改版就失效）

agent-browser 的 Ref 方式：

agent-browser snapshot -i

# 输出：@e1 [input], @e2 [button], @e3 [link]

agent-browser click @e1    # 点击第一个输入框

agent-browser fill @e2 "Hello"  # 填写文本

**AI 自己理解页面，用 @e1/@e2 引用，告别硬编码 selector！**

---

## 📝 关键功能点

### 1. 核心命令体系

| 命令组 | 命令 | 功能 |

|--------|------|------|

| **导航** | open, close | 打开/关闭网页 |

| **快照** | snapshot -i | 获取页面元素引用 |

| **交互** | click, fill, select, check | 页面操作 |

| **信息** | get text/html/url/title | 获取页面数据 |

| **等待** | wait @e1, wait --load | 等待元素/网络 |

| **捕获** | screenshot, pdf | 截图/PDF |

| **状态** | state save/load | 会话持久化 |

| **认证** | auth save/login | 登录凭证管理 |

### 2. 核心工作流

┌─────────────┐     ┌─────────────┐     ┌─────────────┐

│   open      │ ──▶ │  snapshot   │ ──▶ │   click     │

│   打开页面  │     │   获取引用   │     │   操作      │

└─────────────┘     └─────────────┘     └─────────────┘

│

┌─────────────┐           │

│   wait      │ ◀──────────┘

│   等待结果  │

└─────────────┘

### 3. 引用失效机制（关键）

**Refs 不是永久的！** 页面变化后引用失效。

| 操作 | Ref 是否有效 |

|------|-------------|

| click（导航） | ❌ 失效 |

| form submit | ❌ 失效 |

| 动态加载 | ❌ 失效 |

| scroll | ✅ 有效 |

| fill | ✅ 有效 |

**解决方案：操作后重新 snapshot！**

---

## ⚡ 怎么使用

### 基础用法

# 1. 打开网页

agent-browser open https://example.com

# 2. 获取元素引用

agent-browser snapshot -i

# 输出: @e1 [input type="email"], @e2 [input type="password"], @e3 [button]

# 3. 交互操作

agent-browser fill @e1 "user@example.com"

agent-browser fill @e2 "password123"

agent-browser click @e3

# 4. 等待结果

agent-browser wait --load networkidle

# 5. 重新获取引用（页面变化了！）

agent-browser snapshot -i

### 表单提交完整示例

agent-browser open https://example.com/signup

agent-browser snapshot -i

agent-browser fill @e1 "Jane Doe"

agent-browser fill @e2 "jane@example.com"

agent-browser select @e3 "California"  # 下拉选择

agent-browser click @e5

agent-browser wait --load networkidle

agent-browser snapshot -i  # 检查结果

### 状态持久化（登录保持）

# 登录后保存状态

agent-browser open https://app.example.com/login

agent-browser snapshot -i

agent-browser fill @e1 "$USERNAME"