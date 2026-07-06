# AI新范式：循环工程（Loop Engineering）与 Harness Engineering 演进

**来源**: https://v.douyin.com/vSSEbgNpEnI/
**博主**: AI有点聊
**日期**: 2026-06-23（宁兄分享）
**视频原标题**: AI新范式：循环工程 还在研究Harness En...

---

## 总结

AI 工程范式从 Prompt → Context → Harness → Loop 四阶段演进，每一次"改名"背后都是上一个瓶颈被解决、新瓶颈暴露的标志。Claude Code 负责人已不再一句一句敲 prompt，而是写个"循环"让 AI 自己去读需求、自己决定下一步干啥。这是 AI 编程能力边界再次外推的关键一步。

---

## 核心要点

### 1. AI 工程范式四级演进（2022-2026）

| 阶段 | 时间 | 核心思想 | 解决的核心问题 |
|------|------|---------|--------------|
| **Prompt Engineering** | 2022-2024 | 怎么写好提示词 | 让模型理解意图 |
| **Context Engineering** | 2025 | 怎么给模型喂对上下文 | 信息密度+相关性 |
| **Harness Engineering** | 2026年2月 | 怎么"驾驭"AI Agent | 约束/引导/验证/修正行为 |
| **Loop Engineering** | 2026年6月 | 怎么让 AI 自己跑循环 | 递归目标+自我迭代 |

> 关键洞察：**每一次改名背后都是上一个瓶颈被解决、新瓶颈暴露**

### 2. Harness Engineering（驾驭工程）回顾

**核心理念**：AI 时代的全新软件工程学科 —— 设计和实现系统来约束、引导、验证和修正 AI 智能体的行为，让强大但不可预测的 AI 模型能够可靠地完成复杂任务。

**关键里程碑**：
- 2026年2月 Mitchell Hashimoto 在博客中提出
- OpenAI 紧接着发了百万行代码的实验报告
- Martin Fowler 跟进写了深度分析

**形象类比**（江哥第88集）：
- 模型 = 大脑
- Harness = 身体（包含工具）
- 没有 Harness，模型再强也只能"纸上谈兵"

**典型组件**：
- 业务模型 + 指标字典
- 数据查询工具
- 结果生成
- 日志系统
- 验证机制

### 3. Loop Engineering（循环工程）核心

**定义**：设计让 AI Agent 自我驱动的"循环系统"，而不是手工写 prompt。

**关键转变**：
- ❌ 过去：人写 prompt → AI 执行
- ✅ 现在：人定义目标 → AI 在循环中自己迭代，直到完成

**核心特征**：
- **递归目标（Recursive Goal）**：你定义一个目的，AI 持续迭代
- **子智能体（Sub-agents）**：循环中可以拆出子任务
- **外部状态（External State）**：循环读取持久化状态
- **验证机制**：每步验证是否符合目标
- **自动交接**：循环决定何时交回给人

**典型实践**：
- Claude Code 已支持 loop 命令
- Codex / Cursor 跟进
- 5 个核心构建块（待详细解析）

### 4. Loop Engineering vs Harness Engineering 边界

| 维度 | Harness Engineering | Loop Engineering |
|------|--------------------| -----------------|
| **关注点** | 怎么"驾驭"单个 Agent | 怎么让 Agent 自我驱动循环 |
| **抽象层级** | 工具+约束+验证 | 目标+迭代+递归 |
| **人机协作** | 人是"驾驶员" | 人是"目标设定者" |
| **瓶颈** | 单次调用的可靠性 | 多步迭代的效率 |
| **典型问题** | "这步别出错" | "别在循环里打转" |

**两者关系**：
- Harness 是 Loop 的"基础设施" —— 没有可靠的 Harness，Loop 跑不起来
- Loop 是 Harness 的"上层范式" —— Harness 是约束单个 Agent，Loop 是让 Agent 自主串联

### 5. 内循环 vs 外循环（关键区分）

**内循环（Inner Loop）**：
- Agent 内部"思考→行动→观察"的单次循环
- ReAct 模式就是这个
- 解决：单步决策质量

**外循环（Outer Loop）**：
- Agent 跨多步、多会话的持续循环
- Loop Engineering 的核心战场
- 解决：任务级目标达成

**Loop Engineering 的核心价值**：把"内循环"扩展到"外循环"，让 Agent 不只在一轮对话里聪明，而是能持续推进复杂任务。

---

## 一句话概括

**Loop Engineering = 让 AI 写循环给自己跑** —— 从"人写 prompt 给 AI"进化到"人定义目标、AI 自己循环到完成"，Harness 是身体，Loop 是行为模式。

---

## 与宁兄已有知识关联

### 已有 Harness 归档
- `2026-06-16-Harness工程-自说自话的江哥.md` - 江哥第88集 Harness 基础
- 本文档是 Harness → Loop 的演进补充

### 与已有概念的串联

**MCP（Model Context Protocol）**：
- Harness Engineering 的核心组件
- 给 Agent 提供"身体"的标准化接口

**ReAct / Plan+Execute**：
- 内循环模式的典型实现
- Loop Engineering 的"细胞"单元

**Multi-Agent 编排**：
- Loop Engineering 的多 Agent 协同场景
- 子智能体（sub-agents）是 Loop 的关键能力

**Claude Code / Codex / Cursor**：
- Loop Engineering 的主要实践平台
- 已支持 loop / command 等机制

---

## 实践建议（宁兄向）

### 如果你在用 Claude Code / Codex：
1. **从单步 prompt 升级到 loop 命令** —— 让 AI 自己跑循环
2. **先定义清晰目标，再让 AI 决定路径** —— 别过度指定步骤
3. **配合 Harness 基础设施** —— MCP/工具/状态先就位

### 如果在设计 Agent 系统：
1. **先做 Harness**（约束/验证/工具）→ 再上 Loop（迭代/递归）
2. **区分内/外循环** —— 别把所有智能都堆在一个 ReAct 里
3. **给 Loop 加终止条件** —— 避免"无限打转"

### 与 ELUCKY / 京麦场景结合：
- **京麦商品发布**：Loop 跑"截图→识别→填表→验证"循环
- **跨境电商运营**：Loop 跑"分析数据→生成内容→发布→跟踪"循环

---

## 待深挖

- [ ] Loop Engineering 5 个核心构建块细节
- [ ] Claude Code / Codex 的 loop 命令实战
- [ ] Mitchell Hashimoto / OpenAI / Martin Fowler 原文链接
- [ ] "内循环 vs 外循环"边界澄清原文

---

## 参考来源

- 视频原文：https://v.douyin.com/vSSEbgNpEnI/
- B站对照：https://www.bilibili.com/video/BV1pqjg61EZ5/
- 博客园拆解：https://www.cnblogs.com/boydfd/p/20525224
- CSDN综述：https://blog.csdn.net/qq_32799165/article/details/161901342
- GitHub Loop Engineering：https://github.com/cobusgreyling/loop-engineering
- 知乎 Harness 深度：https://zhuanlan.zhihu.com/p/2014014859164026634
- 知乎 Harness 新范式：https://zhuanlan.zhihu.com/p/2024185459392226745

---

## 标签

#LoopEngineering #HarnessEngineering #AI工程范式 #ClaudeCode #AI编程 #Agent演进 #Prompt到Loop #MCP #ReAct #MultiAgent
