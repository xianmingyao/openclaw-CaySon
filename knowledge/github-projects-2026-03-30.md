# GitHub热门项目情报 2026-03-30

> 来源：@AI未来 日榜 + @赛博笔记 周榜 + @成也2077 额外推荐
> 整理时间：2026-03-30 03:10

---

## 📊 @AI未来 日榜 TOP 10

> "GitHub一天涨2万星" 系列

| 排名 | 项目 | ⭐ | 今日增量 | 方向 | 推荐 |
|------|------|-----|---------|------|------|
| 🥇#1 | **deer-flow** | 46.2k | +5,472 | SuperAgent/字节跳动 | ⭐⭐⭐⭐⭐ |
| 🥈#2 | **litellm** | 40.6k | +6,717 | LLM网关/Python | ⭐⭐⭐⭐⭐ |
| 🥉#3 | **ruflo** | 26.2k | +2,841 | 多Agent编排+Claude/TS | ⭐⭐⭐⭐ |
| #4 | Supermemory | 5.7k | +1,810 | AI记忆API/TS | ⭐⭐⭐ |
| #5 | last30days-skill | 4.9k | +1,342 | 信息聚合/Python | ⭐⭐⭐ |
| #6 | claude-subconscious | 1.4k | +110 | AI记忆/Claude | ⭐⭐⭐ |
| #7 | **ruview** | 42.3k | +5,757 | WiFi感知/Rust | ⭐⭐⭐⭐ |
| #8 | aimangastudio | - | - | 漫画创作/TS | ⭐⭐ |
| #9 | MoneyPrinterV2 | 25.5k | +1,065 | 社媒自动化/Python | ⭐⭐ |
| #10 | TradingAgents-CN | 21.3k | +4,427 | 金融多Agent/Python | ⭐⭐⭐ |

### 重点解读

1. **Multi-Agent 是顶流** —— deer-flow、ruflo、TradingAgents-CN 三个多 Agent 项目同时上榜
2. **AI 记忆是刚需** —— claude-subconscious、Supermemory、litellm 都在解决记忆/上下文问题
3. **TypeScript 崛起** —— 4个 TS 项目，和 Python 五五开
4. **字节跳动入场** —— deer-flow 代表大厂开源趋势

---

## 📊 @赛博笔记 GitHub 周榜（第3集）

| 排名 | 项目 | ⭐ | 方向 | 推荐 |
|------|------|-----|------|------|
| 🥇#1 | **everything-claude-code** | 18.8k | Claude Code配置/Anthropic获胜者 | ⭐⭐⭐⭐⭐ |
| 🥈#2 | Antigravity-Manager | 16.9k | 账号管理/Tauri v2 + Rust | ⭐⭐⭐ |
| 🆕#3 | **x-algorithm** | 12.3k | X (Twitter) 推荐算法开源 | ⭐⭐⭐⭐⭐ |
| 🆕#4 | **agent-skills** | 15.6k | Vercel 官方 AI 技能 | ⭐⭐⭐⭐ |
| #7 | maptoposter | 7k | 城市地图海报/Python | ⭐⭐ |
| #10 | AionUI | - | AI工作台/多模型 | ⭐⭐⭐ |
| #11 | **eigent** | - | 多Agent协作/工作流 | ⭐⭐⭐⭐ |
| #20 | Antigravity-Manager | 16.9k | Claude 账号管理/Tauri | ⭐⭐⭐ |

### 重点解读

1. **Claude 生态爆发** —— everything-claude-code、agent-skills、Antigravity-Manager 全是 Claude 相关
2. **大厂官方入场** —— Vercel 官方维护 agent-skills
3. **推荐算法开源** —— x-algorithm 是重大事件，让外界了解社交媒体推荐机制

---

## 📊 @成也2077 额外推荐

| 项目 | ⭐ | 方向 | 推荐 |
|------|-----|------|------|
| **agency-agents** | - | AI员工/多Agent协作 | ⭐⭐⭐⭐⭐ |

> 核心理念："程序员不做工具了，他们开始造 AI 员工了"

---

## 🏆 重点推荐项目深度分析

### 1. deer-flow（字节跳动 SuperAgent）🥇

**项目信息**
- GitHub：`bytedance/deer-flow`
- ⭐ 46.2k Stars
- 技术栈：Python

**核心功能**
- 🦌 字节开源 SuperAgent 框架
- 🔬 集研究·编码·创作于一体
- 🏗️ 多级子代理协同
- 🏖️ 沙箱环境
- 🧠 记忆系统

**学习价值**
- 多级子代理架构设计
- 沙箱安全隔离机制
- 字节跳动 AI 应用实践

---

### 2. everything-claude-code（Claude Code 配置王炸）🥇

**项目信息**
- GitHub：`everything-claude-code`
- ⭐ 18.8k Stars
- 来源：**Anthropic 获胜者**出品

**项目结构**
```
├── agents/          # 智能体配置
├── skills/          # 技能脚本
├── commands/        # 命令集
├── contexts/        # 上下文管理
├── mcp-configs/     # MCP 协议配置
├── hooks/           # 钩子脚本
└── rules/           # 规则配置
```

**学习价值**
- Claude Code 终极配置包
- Anthropic 官方认可的顶级用法
- 可直接抄作业

---

### 3. x-algorithm（X 推荐算法开源）🥇

**项目信息**
- GitHub：`ruvnet/x-algorithm`
- ⭐ 12.3k Stars
- 许可证：Apache-2.0

**项目结构**
```
├── candidate-pipeline/   # 候选管道
├── home-mixer/          # 主页混合器
├── phoenix/             # 凤凰子系统
└── thunder/            # 雷霆子系统
```

**核心描述**
> "This repository contains the core recommendation system powering the 'For You' feed on X."

**学习价值**
- 社交媒体推荐算法内部机制
- 可用于研究、复现、改进
- 理解社交媒体算法的黑盒

---

### 4. litellm（LLM Gateway）🥇

**项目信息**
- GitHub：`BerriAI/litellm`
- ⭐ 40.6k Stars
- 技术栈：Python

**核心功能**
- 🌐 统一调用 **100+ LLM API**
- 🔄 **OpenAI 格式兼容**
- 💰 成本追踪
- ⚖️ 负载均衡
- 🛡️ 安全防护

**杀手锏代码示例**
```python
# 原本写 Claude
response = client.messages.create(...)

# 用了 litellm 后，换模型只需要改名字
response = litellm.completion(
    model="claude-3-opus",
    messages=[...]
)
# 换成 GPT-4 只需要改 model 参数
response = litellm.completion(
    model="gpt-4-turbo",
    messages=[...]
)
```

**学习价值**
- LLM 网关架构设计
- 多模型统一调用范式
- API 成本追踪方案

---

### 5. agent-skills（Vercel 官方技能）

**项目信息**
- GitHub：`agent-skills`
- ⭐ 15.6k Stars
- 来源：**Vercel 官方**维护

**项目结构**
```
├── .github/workflows/           # GitHub Actions
├── packages/
│   └── react-best-practices-build/  # React 最佳实践
├── skills/                      # 技能包
├── AGENTS.md                   # Claude 配置
└── CLAUDE.md                   # Claude 能力配置
```

**核心定位**
> "AI 编码代理的技能集合" —— 打包给 AI 编程助手的能力

**学习价值**
- AI 技能标准化封装
- Vercel 的 AI 编程最佳实践
- 与 OpenClaw Skills 设计理念相通

---

### 6. ruview（WiFi 感知）

**项目信息**
- GitHub：`ruvnet/ruview`
- ⭐ 42.3k Stars
- 技术栈：Rust

**核心功能**
- 📡 WiFi DensePose 技术
- 🧍 实时人体姿态估计（不用摄像头，用 WiFi 信号）
- ❤️ 生命体征监测（呼吸、心率）
- 👁️ **零像素视频即可完成视觉感知**

**学习价值**
- 非视觉传感器的 AI 感知范式
- Rust 在实时系统中的应用
- 传感器融合技术

---

### 7. ruflo（Claude 多 Agent 编排）

**项目信息**
- GitHub：`ruvnet/ruflo`
- ⭐ 26.2k Stars
- 技术栈：TypeScript

**核心功能**
- 🏢 企业级分布式群组智能
- 🔍 RAG 集成
- 💻 原生 Codex 接入
- 🔄 Agent 编排

**与 ruvnet/ruview 是同作者**

---

### 8. eigent（多Agent协作工作流）

**项目信息**
- GitHub：`eigent`
- 定位：多Agent协作系统

**工作流示例**
1. **Browser Agent** → 访问网页 + 读取本地文件 → JSON
2. **Developer Agent** → 浏览器自动化提交表单
3. **Document Agent** → 生成统计报告 + 数据可视化

**技术亮点**
- 多Agent分工协作
- 浏览器自动化
- 本地文件处理
- 数据可视化报告生成

**学习价值**
- Multi-Agent 协作模式实战
- Agent 间通信和任务分配
- 办公自动化场景落地

---

### 9. agency-agents（AI 员工）

**项目信息**
- GitHub：`msitarzewski/agency-agents`

**项目结构**
```
├── engineering/     # 工程相关
├── design/          # 设计相关
├── academic/        # 学术相关
└── examples/       # 示例
```

**核心理念**
> "程序员不做工具了，他们开始造 AI 员工了"

**学习价值**
- AI Agent 分工协作模式
- 从"助手"到"员工"的认知转变
- 组建 AI 团队完成复杂任务

---

## 📈 技术趋势总结

### 1. Multi-Agent 爆发
- deer-flow（字节）、ruflo、agency-agents、TradingAgents-CN、**eigent**
- 从"单 Agent"到"多 Agent 团队协作"

### 2. AI 记忆是刚需
- claude-subconscious、Supermemory、mem0 + Milvus
- 解决 AI "健忘症"问题

### 3. Claude 生态热
- everything-claude-code、agent-skills、Antigravity-Manager
- Anthropic 获胜者 + Vercel 官方双重背书

### 4. TypeScript 崛起
- 4个 TS 项目（ruflo、Supermemory、aimangastudio、agent-skills）
- 和 Python 五五开

### 5. 大厂开源加速
- 字节跳动（deer-flow）
- X/Twitter（x-algorithm）
- Vercel（agent-skills）

---

## 🔧 待深入研究项目

| 优先级 | 项目 | 原因 |
|--------|------|------|
| P0 | deer-flow | 字节 SuperAgent，多级子代理架构 |
| P0 | everything-claude-code | Claude Code 配置王炸 |
| P0 | x-algorithm | 推荐算法开源，重大事件 |
| P1 | litellm | LLM Gateway 架构 |
| P1 | agent-skills | Vercel 官方技能封装 |
| P1 | agency-agents | AI 员工协作模式 |
| P2 | ruflo + ruview | 同作者，技术创新 |
| P2 | Supermemory | AI 记忆 API 设计 |

---

## 📚 相关知识库文件

- `knowledge/github-projects.md` - GitHub 项目情报汇总
- `knowledge/memory-system-architecture.md` - 记忆系统架构
- `skills/windows-control/` - windows-control v3.0
