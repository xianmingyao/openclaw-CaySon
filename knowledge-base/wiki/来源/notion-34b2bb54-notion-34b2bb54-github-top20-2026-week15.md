# GitHub一周热门项目TOP20【2026第15周】

> **来源：** 赛博笔记抖音视频

> **视频发布时间：** 2026-04-12

> **扒榜整理：** CaySon AI助手

---

## 📌 本周核心亮点

| 亮点 | 说明 |

|------|------|

| 🏆 **TOP3全部易主** | 新项目强势登顶，老项目被挤下神坛 |

| 💰 **降Token项目首次登场** | caveman项目 - 降65-75% Token消耗 |

| 🛠️ **技能工程化爆发** | graphify/nuwa-skill等多个.skill项目涌现 |

| ⚡ **代理效能优化** | everything-claude-code等Harness优化项目 |

---

## 🏅 完整TOP20榜单

### 🥇 TOP 1-5

| 排名 | 项目 | Stars | 简介 |

|:---:|------|-------|------|

| 1 | **MemPalace/mempalace** | 44.8k | 🧠 史上最高分AI记忆系统，LongMemEval 96.6%准确率，纯本地运行 |

| 2 | **santifer/career-ops** | 32.6k | 💼 AI求职系统，14种技能模式，740+工作机会评估，100+定制简历 |

| 3 | **JuliusBrussee/caveman** | 26k | 🪨 **降75%输出Token！** caveman说话风格保持技术准确性 |

| 4 | **safishamsi/graphify** | 25k | 📊 代码→知识图谱，支持23种语言，71.5x更少Token |

| 5 | **Gitlawb/openclaude** | 21k | 🔓 开源Claude coding-agent CLI，支持200+模型 |

### 🥈 TOP 6-10

| 排名 | 项目 | Stars | 简介 |

|:---:|------|-------|------|

| 6 | **alchaincyf/nuwa-skill** | 9.6k | 👩 女娲.skill - 蒸馏乔布斯/芒格/马斯克思维方式 |

| 7 | **HKUDS/OpenHarness** | 9.3k | 🐎 港大Open Agent Harness，内置个人Agent "ohmo" |

| 8 | **emdash-cms/emdash** | 9.2k | ⚛️ TypeScript CMS，基于Astro，WordPress精神继承者 |

| 9 | **garrytan/gbrain** | 7.4k | 🧠 OpenClaw/Hermes Agent Brain |

| 10 | **ultraworkers/claw-code-parity** | 6.7k | 🦀 claw-code Rust移植版 |

### 🥉 TOP 11-15

| 排名 | 项目 | Stars | 简介 |

|:---:|------|-------|------|

| 11 | **alchaincyf/zhangxuefeng-skill** | 5.5k | 📜 张锡峰.skill - 高考/职业规划/学习方法 |

| 12 | **0xGF/boneyard** | 4.7k | ⚰️ 自动生成骨架加载框架 |

| 13 | **kevinrgu/autoagent** | 4.1k | 🤖 自主Harness工程 |

| 14 | **farzaa/clicky** | 4.1k | 🍎 Swift iOS开发助手 |

| 15 | **QuipNetwork/quip-protocol-rs** | 3.8k | 🦀 Quip Protocol Rust实现 |

### 📍 TOP 16-20

| 排名 | 项目 | Stars | 简介 |

|:---:|------|-------|------|

| 16 | **xixu-me/awesome-persona-distill-skills** | 3.7k | 👤 .skill合集 - 人物/关系/纪念场景 |

| 17 | **QuipNetwork/xq-rs** | 3.7k | 🦀 Quip量子虚拟机Rust版 |

| 18 | **KKKKhazix/khazix-skills** | 3.5k | 🦗 刺客信条AI Skills |

| 19 | **QuipNetwork/xq-py** | 3.7k | 🐍 Quip量子虚拟机Python版 |

| 20 | **QuipNetwork/quip-node-manager** | 3.7k | 🖥️ Quip节点管理GUI |

---

## 🎯 重点项目深度解析

### 💰 caveman - 降Token神器（首次登场！）

**项目地址：** https://github.com/JuliusBrussee/caveman

Normal: "The reason your React component is re-rendering is likely because

you're creating a new object reference on each render cycle..."

Caveman: "New object ref each render. Inline object prop = new ref = re-render.

Wrap in useMemo."

同一答案，75%更少文字，大脑还是大！

**四种强度模式：**

| 模式 | 示例 |

|------|------|

| 🪶 Lite | "Your component re-renders because you create a new object reference each render. Inline object props fail shallow comparison every time. Wrap it in useMemo." |

| 🪨 Full | "New object ref each render. Inline object prop = new ref = re-render. Wrap in useMemo." |

| 🔥 Ultra | "Inline obj prop → new ref → re-render. useMemo." |

| 📜 文言文 | "物出新参照，致重绘。useMemo Wrap之。" |

**原理：** LLM对冗长表达的奖励不如简洁表达，caveman风格反而让模型更精准，输出Token减少75%

**适用场景：**

- 代码审查

- commit信息生成

- 代码评审

- 技术文档简化

---

### 🧠 MemPalace - 史上最高分AI记忆系统

**项目地址：** https://github.com/MemPalace/mempalace

| 指标 | 数据 |

|------|------|

| LongMemEval准确率 | **96.6%** |

| 测试题数 | 500题 |

| 费用 | **$0**（完全本地） |

| 存储方式 | 原始verbatim存储，不做摘要 |

**架构 - 宫殿记忆法：**

Wings（翅膀）  → 人/项目

Halls（大厅）  → 记忆类型

Rooms（房间）  → 具体想法

Drawers（抽屉）→ 子分类

Closets（橱柜）→ 更细分类

**核心特性：**

- 原始verbatim存储，不过滤不失真

- 96.6%准确率来自raw模式

- AAAK实验性压缩模式（84.2%，用于大规模重复实体）

- 完全本地运行，无云API

**注意事项（官方坦诚）：**

- AAAK示例的Token计算有误（已修正）

- "30x无损压缩"表述过度（AAAK是lossy）

- 社区在48小时内发现并报告了多个问题，团队已承认并修复中

---

### 📊 graphify - 代码秒变知识图谱

**项目地址：** https://github.com/safishamsi/graphify

输入：任意代码文件夹 + PDF + 截图 + 视频 + 图片

输出：可交互知识图谱 + 71.5x更少Token

**输出文件：**

graphify-out/

├── graph.html        # 可交互图谱 - 点击节点/搜索/按社区过滤