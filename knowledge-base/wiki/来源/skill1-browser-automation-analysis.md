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

```
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
```

### 核心创新：引用系统（Ref）

传统爬虫需要：
1. 分析页面结构
2. 写 CSS 选择器/XPath
3. 调试 selector
4. 维护 selector（页面改版就失效）

agent-browser 的 Ref 方式：
```bash
agent-browser snapshot -i
# 输出：@e1 [input], @e2 [button], @e3 [link]

agent-browser click @e1    # 点击第一个输入框
agent-browser fill @e2 "Hello"  # 填写文本
```

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

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   open      │ ──▶ │  snapshot   │ ──▶ │   click     │
│   打开页面  │     │   获取引用   │     │   操作      │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                    ┌─────────────┐           │
                    │   wait      │ ◀──────────┘
                    │   等待结果  │
                    └─────────────┘
```

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

```bash
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
```

### 表单提交完整示例

```bash
agent-browser open https://example.com/signup
agent-browser snapshot -i
agent-browser fill @e1 "Jane Doe"
agent-browser fill @e2 "jane@example.com"
agent-browser select @e3 "California"  # 下拉选择
agent-browser click @e5
agent-browser wait --load networkidle
agent-browser snapshot -i  # 检查结果
```

### 状态持久化（登录保持）

```bash
# 登录后保存状态
agent-browser open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e1 "$USERNAME"
agent-browser fill @e2 "$PASSWORD"
agent-browser click @e3
agent-browser wait --url "**/dashboard"
agent-browser state save auth.json

# 下次使用
agent-browser state load auth.json
agent-browser open https://app.example.com/dashboard
```

### 多会话并行

```bash
# 同时打开多个网站
agent-browser --session site1 open https://site-a.com
agent-browser --session site2 open https://site-b.com

# 操作完后关闭
agent-browser --session site1 close
agent-browser --session site2 close
```

### 认证凭证管理

```bash
# 保存登录凭证
echo "password123" | agent-browser auth save github \
    --url https://github.com/login \
    --username myuser \
    --password-stdin

# 使用凭证登录
agent-browser auth login github
```

---

## ✅ 优点

1. **AI 友好的 Ref 系统** - 不需要硬编码 selector，AI 自己理解页面
2. **无头模式** - 后台运行，资源占用低
3. **状态持久化** - cookies/localStorage 保存，登录状态不丢失
4. **多会话支持** - 同时操作多个网站
5. **认证保险库** - 安全的凭证管理
6. **截图/PDF** - 完整的页面捕获能力
7. **diff 对比** - 页面变化检测

### vs 传统爬虫

| 维度 | 传统爬虫 | agent-browser |
|------|---------|---------------|
| selector | 硬编码，容易失效 | AI 自理解，动态 |
| 登录 | Cookie 手动处理 | auth 凭证管理 |
| 动态内容 | 需要分析 JS | 直接操作 DOM |
| 调试 | 繁琐 | 所见即所得 |

---

## ❌ 缺点

1. **依赖 Chromium** - 需要安装 Chromium
2. **Windows 需要 headed 模式** - 无头模式可能有问题
3. **Ref 生命周期管理** - 需要注意引用失效
4. **性能** - 比纯 HTTP 请求慢
5. **反爬** - 容易被检测为机器人

---

## 🎬 使用场景

| 场景 | 示例 |
|------|------|
| **网页自动化** | 自动填表、自动发帖 |
| **数据采集** | 爬取需要 JS 渲染的页面 |
| **登录保持** | 维持登录态访问受保护页面 |
| **截图/PDF** | 生成网页截图或 PDF |
| **页面测试** | 自动化测试 Web 应用 |
| **价格监控** | 监控电商价格变化 |
| **社交媒体** | 自动化操作 Twitter/LinkedIn |

---

## 🔧 运行依赖环境

| 依赖 | 说明 |
|------|------|
| Node.js | 运行环境 |
| Chromium | 浏览器引擎 |
| scripts/setup.sh | 安装脚本 |

### 安装步骤

```bash
cd skills/openclaw-agent-browser
./scripts/setup.sh
```

---

## 🚀 部署使用注意点

1. **首次使用需要 setup** - `./scripts/setup.sh` 安装 Chromium
2. **Windows headed 模式** - `--headed` 参数显示浏览器窗口
3. **Ref 重新获取** - 页面变化后必须重新 snapshot
4. **等待网络** - `wait --load networkidle` 确保页面加载完成
5. **状态保存** - 登录后及时 `state save`

---

## 🕳️ 避坑指南

| 坑 | 问题 | 解决 |
|-----|------|------|
| **Ref 失效** | 点击后引用失效 | 操作后重新 snapshot |
| **网络慢** | 元素还没加载 | 使用 `wait --load networkidle` |
| **弹窗拦截** | 新标签页被拦截 | `click @e1 --new-tab` |
| **Windows 无头问题** | 看不到浏览器 | 使用 `--headed` 参数 |
| **登录失效** | 状态过期 | 定期 `state save` |

### Windows 特定问题

根据 AGENTS.md 铁律：**Windows 必须用 `--headed` 模式！**

```bash
# ❌ 错误：无头模式，看不到窗口
agent-browser open https://example.com

# ✅ 正确：headed 模式，显示窗口
npx agent-browser --headed open "https://example.com"
```

---

## 📊 总结

**学习价值：⭐⭐⭐⭐⭐（5星）**

| 维度 | 评分 | 说明 |
|------|------|------|
| AI 友好度 | ⭐⭐⭐⭐⭐ | Ref 系统让 AI 告别硬编码 selector |
| 功能完整性 | ⭐⭐⭐⭐⭐ | 导航、交互、等待、截图、会话管理全覆盖 |
| 工程质量 | ⭐⭐⭐⭐⭐ | 完整 CLI，易用性强 |
| 场景覆盖 | ⭐⭐⭐⭐ | 适合 80% 的浏览器自动化场景 |
| 学习成本 | ⭐⭐⭐⭐ | 简单易学，文档清晰 |

**推荐指数：⭐⭐⭐⭐⭐（5星，必装）**

**核心启示：**
> **"AI 不需要理解 CSS 选择器，只需要理解 @e1/@e2 这种引用"**

---

## 📋 对应热门 GitHub 项目

| 项目 | 方向 | 对应功能 |
|------|------|---------|
| **Lightpanda** | AI 专用浏览器 | agent-browser 类似 |
| **Scrapling** | AI 爬虫框架 | 数据采集类似 |
| **agent-browser** | 官方内置 | ✅ 已安装 |

---

## 🔗 与 Harness Engineering 的关系

agent-browser 是 **Harness Engineering（驾驭工程）** 的典型案例：

```
浏览器（Chrome/Chromium）
        │
        ▼
  agent-browser CLI
        │
        ▼
  AI Agent 统一接口
```

**本质：用标准化 CLI 接口封装复杂系统，让 AI 方便调用。**

与 windows-control 的区别：
- windows-control → 封装 Windows 桌面应用
- agent-browser → 封装浏览器

---

## 📝 下一步

1. **安装 Office skill** - 技能4需要
2. **分析技能3** - Memory + AI-Enhanced
3. **实践练习** - 用 agent-browser 完成一个实际任务

