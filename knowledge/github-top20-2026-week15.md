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

```
Normal: "The reason your React component is re-rendering is likely because 
         you're creating a new object reference on each render cycle..."
         
Caveman: "New object ref each render. Inline object prop = new ref = re-render. 
          Wrap in useMemo."
          
同一答案，75%更少文字，大脑还是大！
```

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

```
Wings（翅膀）  → 人/项目
Halls（大厅）  → 记忆类型
Rooms（房间）  → 具体想法
Drawers（抽屉）→ 子分类
Closets（橱柜）→ 更细分类
```

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

```
输入：任意代码文件夹 + PDF + 截图 + 视频 + 图片
输出：可交互知识图谱 + 71.5x更少Token
```

**输出文件：**
```
graphify-out/
├── graph.html        # 可交互图谱 - 点击节点/搜索/按社区过滤
├── GRAPH_REPORT.md  # 上帝节点 + 意外连接 + 建议问题
├── graph.json       # 持久化图谱 - 几周后再查无需重读
└── cache/           # SHA256缓存 - 只重新处理变更文件
```

**支持语言（23种）：**
Python, JavaScript, TypeScript, Go, Rust, Java, C, C++, Ruby, C#, Kotlin, Scala, PHP, Swift, Lua, Zig, PowerShell, Elixir, Objective-C, Julia, Vue, Svelte, Dart

**支持格式：**
代码 / PDF / Markdown / 截图 / 白板照片 / 视频(Whisper转录) / 音频

**与Karpathy的/raw文件夹呼应：**
Karpathy保持一个/raw文件夹存放论文/推文/截图/笔记，graphify是解决方案 - 71.5x更少Token，跨会话持久化

---

### 👩 nuwa-skill - 女娲.skill

**项目地址：** https://github.com/alchaincyf/nuwa-skill

> "你想蒸馏的下一个员工，何必是同事？"

**核心理念：** 蒸馏乔布斯/芒格/费曼/马斯克的思维方式，让他们给你打工

**示例 - Naval风格回答：**

```
用户："我同时想做自媒体、写书、做独立开发，精力完全不够"

Naval："你列了三个欲望。每个欲望都是你跟不快乐签的一份合同。
        不是精力不够，是合同太多。
        问你自己：哪一个做起来你会忘记时间？那个就是你的特定知识所在。
        不是三选一。是先一，再一，再一。串行复利，不是并行内耗。"
```

**示例 - 马斯克风格回答：**

```
用户："我们的SaaS产品获客成本太高"

马斯克："先别想怎么降。先算物理极限。
        获客的最小必要动作是什么？用户从知道你到付费，
        信息传递的理论最短路径是什么？
        
        现在你的实际路径是理论路径的几倍？
        如果超过3倍，中间一定有可以砍掉的步骤。
        不是优化漏斗，是质疑漏斗本身该不该存在。"
```

---

### 💼 career-ops - AI求职系统

**项目地址：** https://github.com/santifer/career-ops

| 功能 | 说明 |
|------|------|
| 自动评估 | 10维度加权评分系统（A-F评分） |
| 定制PDF | ATS优化简历，按岗位定制 |
| 门户扫描 | Greenhouse, Ashby, Lever等45+公司 |
| 批量处理 | 10+ offer并行评估 |
| 面试准备 | STAR+R故事库 |
| 谈判脚本 | 薪资谈判框架 |

**作者战绩：** 评估740+工作机会，生成100+定制简历，拿到Head of Applied AIoffer

---

### 🐎 OpenHarness - 港大Agent Harness

**项目地址：** https://github.com/HKUDS/OpenHarness

| 组件 | 功能 |
|------|------|
| 🔄 Agent Loop | 流式工具调用 / 指数退避重试 / 并行执行 / Token计数 |
| 🔧 Tools | 43+工具（文件/Shell/搜索/Web/MCP） |
| 🧠 Memory | 多层次记忆系统 |
| 👥 Multi-Agent | 多Agent协调 |
| 🛠️ Skills | 按需技能加载（.md格式） |

**内置个人Agent：** ohmo - 支持飞书/Slack/Telegram/Discord，可自主fork分支/写代码/跑测试/开PR

---

## 🔮 本周趋势总结

| 方向 | 代表项目 | 热度 |
|------|----------|------|
| 💰 **降Token** | caveman | 🆕 首次登场 |
| 🧠 **记忆系统** | MemPalace | 持续火爆 |
| 📊 **知识图谱** | graphify | 新上榜 |
| 🛠️ **技能工程化** | nuwa-skill / graphify | 爆发中 |
| 🤖 **Agent Harness** | OpenHarness / autoagent | 持续热门 |
| 💼 **垂直应用** | career-ops | 新上榜 |

---

## 📚 相关资料

- **赛博笔记抖音：** https://v.douyin.com/CWIZs7F4-jA/
- **视频数据：** 4931点赞 / 4913收藏 / 238评论 / 918分享
- **视频时长：** 04:33
- **章节：** 引言(00:00) → 前20名(00:23) → 前10名(02:04) → 前3名(03:25) → 总结(04:08)

---

## 🏷️ 标签

`#github排行榜` `#github开源` `#token` `#caveman` `#MemPalace` `#graphify` `#skill工程`
