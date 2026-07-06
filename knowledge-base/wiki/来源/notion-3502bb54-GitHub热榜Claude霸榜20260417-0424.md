# 本周GitHub热榜 - Claude霸榜（2026.04.17-04.24）

> 来源：星探AI GitHub热榜周报第5集
> 整理时间：2026-04-28

## 📊 Top 5 榜单

| 排名 | 项目 | Stars | 本周增量 | 关键词 |
|:---:|------|-------|---------|--------|
| 🥇 | **Karpathy Skills** | 94k | +35k+ | Claude Code最佳实践 |
| 🥈 | **Hermes Agent** | 33k | +22k | Agent自进化框架 |
| 🥉 | **claude-mem** | 68k | +8.7k | 记忆持久化 |
| #4 | **Multica** | 22k | +6k | 多代理协作 |
| #5 | VoiceBox | 22k | +4.5k | AI语音克隆 |

---

## #1 Karpathy Skills（94k stars）

### 项目信息
- **仓库**：`forrestchang/andrej-karpathy-skills`
- **Stars**：94,055（持续增长中）
- **本周增量**：+35,000+
- **描述**：一个CLAUDE.md文件，基于Karpathy对LLM编码陷阱的观察优化Claude Code

### 核心功能
基于 **Andrej Karpathy**（李飞飞学生、OpenAI创始成员、Tesla AI负责人）对LLM编码陷阱的观察，制作的可安装Skill

### 解决的问题
Claude Code容易犯哪些错误？Karpathy总结了一套最佳实践，打包成可安装的Skill

### 适用场景
- 想要提升Claude Code表现
- 避免LLM常见编码陷阱
- 快速获取Karpathy经验

---

## #2 Hermes Agent（33k stars）

### 项目信息
- **仓库**：`NousResearch/Hermes`
- **Stars**：33k+
- **本周增量**：+22,000+
- **类型**：开源LLM + Agent框架

### 核心功能
- 内置闭环学习系统
- 自动创建Skills
- 跨会话记忆
- Agent自进化能力

### 解决的问题
传统Agent需要人工调优，Hermes可以持续自我优化

### 架构特点
```
[Agent] → [执行] → [评估] → [反思] → [优化]
              ↑                           ↓
              ←←←←←← 循环迭代 ←←←←←←←←←
```

---

## #3 claude-mem（68k stars）

### 项目信息
- **仓库**：`thedotmack/claude-mem`
- **Stars**：68,554
- **本周增量**：+8,739
- **描述**：一个Claude Code插件，自动捕捉编码会话中的所有操作，用AI压缩摘要，注入未来会话

### 核心功能
1. 🪝 **自动捕捉** - Hooks自动捕获所有编码会话
2. 🧠 **AI压缩** - 用Agent SDK提取关键决策和经验
3. 📚 **结构化知识** - 编译成跨引用的知识文章
4. 🔄 **持续进化** - 记忆随代码库一起成长

### 解决的问题
Claude Code每次新会话都是"失忆"状态，不知道之前做了什么决定、学到了什么

### 工作原理
```
编码会话 → 自动捕获 → AI压缩摘要 → 注入未来上下文 → 持续学习
```

---

## #4 Multica（22k stars）

### 项目信息
- **仓库**：`multica-ai/multica`
- **Stars**：22,004（本周+6,015）
- **描述**：把你的coding agents变成真正的团队成员

### 核心功能
- 📋 **分配任务** - 给不同Agent分配具体工作
- 📊 **跟踪进度** - 监控每个Agent的任务完成状态
- 🔄 **技能叠加** - Agent之间可以组合技能、协同工作
- 👥 **团队协作** - 把单个AI变成"AI团队"

### 解决的问题
"你的下一批员工不是人类" - 

多代理如何像真实团队一样协作

### 架构特点
```
[Orchestrator] → [Agent A] → Tools
              ↓
         [Agent B] → Tools
              ↓
         [Agent C] → Tools
```

---

## #5 VoiceBox（22k stars）

### 项目信息
- **Stars**：22,600（本周+4,495）
- **类型**：开源AI语音克隆工作室

### 核心功能
- AI语音克隆
- 开源版本
- 语音合成

---

## 🔍 其他热门项目

### Context Engineering（8.7k stars）

- **仓库**：`davidkimai/Context-Engineering`
- **Stars**：8,784
- **核心理念**：上下文工程是一门艺术和科学

#### Karpathy名言
> *"Context engineering is the delicate art and science of filling the context window with just the right information for the next step."*

#### 与Prompt Engineering的区别
| Prompt Engineering | Context Engineering |
|--------------------|---------------------|
| 怎么写提示词 | 怎么设计上下文 |
| 写得好 → 输出好 | 上下文完整 → 推理准确 |
| 技巧性 | 系统性工程 |

---

## 💡 本周趋势总结

### 核心关键词
1. **Agent自进化** - Hermes代表方向
2. **记忆系统** - claude-mem解决失忆痛点
3. **多代理协作** - Multica团队化
4. **上下文工程** - 从技巧到系统工程
5. **Claude官方参与** - 本周多个项目都有官方加持

### 技术架构演进
```
Single Agent → Multi-Agent → Agent + Memory → Self-Evolving
     ↓              ↓              ↓              ↓
   简单任务      复杂工作流     长期项目       持续优化
```

### 选型建议
- **简单任务**：Single Agent
- **需要记忆**：+ Memory Layer（claude-mem）
- **复杂工作流**：Multi-Agent（Multica）
- **需要工具**：+ MCP生态
- **持续优化**：Self-Evolving（Hermes）

---

## 📚 相关资源

- Karpathy视频：https://www.youtube.com/AndrejKarpathy
- Claude Code：https://docs.anthropic.com/claude-code
- MCP协议：https://modelcontextprotocol.io

---

*整理自抖音@星探AI GitHub热榜周报第5集*
