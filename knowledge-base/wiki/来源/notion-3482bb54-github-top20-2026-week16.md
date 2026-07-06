# GitHub一周热门项目TOP20【2026第16周】

> 来源：赛博笔记抖音视频 | IT咖啡馆第87集

> 发布：2026-04-19 / 2026-04-18

> 标签：#AI新星计划 #Github #karpathy #智能体

---

## 本周核心主题

- "把同事蒸馏成AI技能"的新项目涌现

- 近期很少见的硬件项目首次登场

- karpathy-skills引爆技能蒸馏热潮

---

## TOP20项目列表

### TOP1: andrej-karpathy-skills ⭐ 54.7k

- **仓库**：`forrestchang/andrej-karpathy-skills`

- **Stars**：54.7k | **Fork**：-

- **核心理念**：Karpathy的编码逻辑 → 减少AI过度设计与误导性行为

- **项目结构**：

.claude-plugin/

skills/karpathy-guidelines/

CLAUDE.md

EXAMPLES.md

README.md

- **价值**：把AI大牛的思维方式直接封装成Claude Code Skill

- **来源**：赛博笔记第15集 / IT咖啡馆第87集(Cloud Code)

### TOP2: caveman ⭐ 36.9k

- **仓库**：`JuliusBrussee/caveman`

- **Stars**：36.9k | **Fork**：1.8k

- **Slogan**："Why use many token when few token do trick"

- **效果**：最高可节省**75%**的输出Token和响应时间

- **标签**：ai, skill, meme, caveman, claude, llm, prompt-engineering

- **模式**：Lite/Full/Ultra/文言文四种模式

- **来源**：赛博笔记第15集

### TOP3: multica ⭐ 15.4k

- **仓库**：`multica-ai/multica`

- **Stars**：15.4k | **Fork**：1.9k

- **核心定位**：把编码智能体变成真正的同事

- **Slogan**："The open-source management platform. Turn code teammates..."

- **数据**：416 Branches, 50 Tags, v0.2.5

- **来源**：赛博笔记第15集 / IT咖啡馆第87集

### TOP4: graphify ⭐ 29.1k

- **仓库**：`safishamsi/graphify`

- **Stars**：29.1k | **Fork**：3.2k

- **核心功能**：将代码、文档、论文等转化为可查询的知识图谱

- **支持**：Gemini CLI、OpenClaw等

- **标签**：gemini, knowledge-graph, codex, graphify, claude-code

- **来源**：赛博笔记第15集

### TOP5: gstack ⭐ 75k 🔥

- **仓库**：`garrytan/gstack`

- **Stars**：75k | **Fork**：10.6k

- **核心定位**：Use Garry Tan's exact code setup: 23 opinions... as CEO, Design... Release Manager... QA

- **Slogan**：旨在扮演从CEO到QA的全栈角色

- **数据**：Issues 105, PR 224, Branches 201

- **来源**：赛博笔记第15集

### TOP6: nuwa-skill ⭐ 12.3k

- **仓库**：`alchaincyf/nuwa-skill`

- **Stars**：12.3k | **Fork**：2k

- **核心理念**：把你佩服的同事变成AI技能

- **描述**：蒸馏任何人的思维模式、决策启发式

- **来源**：赛博笔记第15集

### TOP14: VoxCPM ⭐ 14.2k

- **仓库**：`OpenBMB/VoxCPM`

- **Stars**：14.2k | **Fork**：1.7k

- **核心功能**：

- Tokenizer-free for Multilingual Speech

- Creative Voice Life Cloning

- **特点**：新一代TTS，上下文感知+零样本克隆+连续云建模

- **来源**：赛博笔记第15集 / IT咖啡馆第87集(VOXCPM2)

---

## IT咖啡馆5大项目详解

| 时间 | 项目 | 核心要点 |

|------|------|----------|

| 00:22 | **Cloud Code** | 基于Karpathy经验总结的AI编程助手使用原则 |

| 02:14 | **Multica** | 开源托管AI Agent平台，编排+自我驱动，企业级 |

| 03:41 | **VOXCPM2** | 新一代TTS，上下文感知+零样本克隆+连续云建模 |

| 04:53 | **MarkItDown** | 全能文档转Markdown，支持多种格式 |

| 06:04 | **QMD** | 本地CLI搜索引擎，Markdown/文档/会议记录 |

### MarkItDown

- **仓库**：`microsoft/markitdown`

- **Stars**：112.6k（本周+9k）

- **功能**：文件一键转换成Markdown格式

- **来源**：骋风算力第174集

### QMD

- **类型**：本地CLI搜索引擎

- **功能**：Markdown/文档知识库/会议记录搜索

- **特点**：本地运行，隐私优先

---

## Claude Code 7层记忆架构

> 来源：大力AI抖音视频系列

### L1: 原始上下文

- 底层输入

### L2: 微压缩

- 轻度压缩

### L3: 会话记忆

- **路径**：`~/.claude/projects/<slug>/session-memory/<id>.md`

- **内容**：

# 当前任务

# 关键决策

# 踩过的坑

# 文件变更记录

- **核心**：边干活边记笔记

### L4: 全压缩