# Hermes Agent 技术深挖报告（2026-04-13 更新）

> 来源：抖音视频Gggda + Web搜索 + 已有知识库
> 标签：AI-Agent / Self-Evolution / DSPy / GEPA / NousResearch / 三层记忆 / 学习循环

---

## 1. 🎯 这是什么

**Hermes Agent** 是 Nous Research 开发的一款**自进化AI Agent框架**（2026年最火开源Agent，32K+ Stars）。

**一句话定义：** 第一个"出厂就带缰绳"的AI Agent —— 不是人类从外部约束它，而是**AI自己给自己造缰绳**。

### 核心定位
```
OpenClaw的龙虾热还没散，Hermes Agent两个月飙到27000+ Stars
但它不是「又一个Agent」，而是第一个出厂就带缰绳的AI Agent
```

---

## 2. 📝 关键功能点

### v0.7.0 最新特性（2026-04-03）

| 特性 | 说明 |
|------|------|
| 🔌 **可插拔记忆后端** | Pluggable memory backends，支持多种存储 |
| 🛠️ **40+内置工具** | 覆盖常用操作，开箱即用 |
| 🔌 **MCP服务器模式** | Model Context Protocol 支持 |
| 🖥️ **6种终端后端** | 支持多种执行环境 |
| 🌐 **多平台Gateway** | 消息通道统一接入 |

---

## 3. ⚡ 核心架构（一条线串起来）

### Hermes架构 = 心脏 + 大脑 + 技能库 + 手脚 + 入口

```
┌─────────────────────────────────────────────────────────────┐
│                      多平台Gateway（入口）                      │
│         Telegram / Discord / Slack / WhatsApp / ...         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              40+ 内置工具（手脚）                             │
│    web_search / file_ops / code_run / memory / ...          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Scale系统（技能库）                              │
│         自动构建 + 持续优化 + 可复用Skills                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              三层记忆系统（大脑）                            │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│    │ 会话记忆  │  │ 持久记忆  │  │ Skill记忆 │              │
│    │ (Session)│  │(Persistent)│ │  (Skills)│              │
│    └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              学习循环（心脏）★ 核心创新 ★                     │
│    任务 → 复盘 → 改进 → 沉淀 → 下次更强                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 🔄 学习循环（核心创新）

### 什么是"缰绳"？

Harness Engineering 认为：AI的瓶颈不在模型，而在**环境控制系统**（缰绳）。

- OpenClaw：Skills = 人类写的缰绳（外部约束）
- **Hermes：让AI自己造缰绳（内置闭环）**

### 学习循环四阶段

```
① 任务执行
   ↓
② 自动复盘（Reflective Review）
   - 分析哪里做得好/不好
   - 提取可复用模式
   ↓
③ 持续改进（Continuous Improvement）
   - 更新记忆
   - 优化Skill
   - 调整策略
   ↓
④ 知识沉淀
   - 持久化到三层记忆
   - 下次遇到类似任务更快更准
```

### 三层记忆各司其职

| 记忆层 | 作用 | 持久性 |
|--------|------|--------|
| **会话记忆** | 当前任务上下文 | 单次会话 |
| **持久记忆** | 跨会话积累的知识 | 永久 |
| **Skill记忆** | 可复用的技能模块 | 永久 |

---

## 5. 🧬 自进化引擎：DSPy + GEPA

### Hermes Agent Self-Evolution

这是 Hermes 的**进化版**组件，专门负责"让技能自动变强"。

#### 核心技术

| 技术 | 全称 | 作用 |
|------|------|------|
| **DSPy** | Declarative Self-Improving Python | 声明式自优化框架 |
| **GEPA** | Genetic-Pareto Prompt Evolution | 遗传-帕累托提示词进化 |

#### GEPA工作原理

```
① 变异（Mutation）
   - 对Skills/工具描述/System Prompt/代码进行文本级变异
   - 生成多个候选变体

② 评估（Evaluation）
   - 在执行Traces上测试候选变体
   - 检查是否满足预设 guardrails（护栏）

③ 选择（Pareto Selection）
   - 多目标优化：质量 ↑ + 复杂度 ↓
   - 选择帕累托最优解

④ 沉淀（Integration）
   - 最佳版本替换旧版本
   - 永久生效
```

#### 实战效果

> "Phase-one score: 0.408 → 0.569，提升**39.5%**"
> — NousResearch 官方数据

#### 无需GPU训练

> "Everything operates via API calls — mutating text-based components"
> — GitHub README

**关键点：** 不需要训练权重，只需要API调用 + 文本变异 + 轨迹评估。任何人可以跑。

---

## 6. 🆚 Hermes vs OpenClaw（深度对比）

### 核心差异

| 维度 | Hermes Agent | OpenClaw |
|------|-------------|----------|
| **缰绳来源** | AI自己造缰绳（内置闭环） | 人类写Skills（外部约束） |
| **学习能力** | 内置自进化引擎 | 依赖外部Skills系统 |
| **记忆** | 三层记忆内置 | 梦境记忆 + 外部Milvus |
| **生态** | 新兴（32K Stars） | 成熟多渠道 |
| **用户建模** | 越用越精准 | 需手动配置 |
| **技能更新** | 自动进化 | 人工维护 |

### 差距最大的两个维度

Gggda 视频中明确指出：

> **1. 学习能力**
> - OpenClaw Scale：靠人工编写和调整，进化依赖社区和用户主动维护
> - Hermes Scale：用的越久，Scale越精准，自动进化

> **2. 用户建模**
> - OpenClaw：需要人类定义 SOUL.md / USER.md
> - Hermes：AI持续观察你的行为，自动构建用户画像

### 互补关系

```
不是选择题，是组合题

OpenClaw（多渠道入口）
    ↓
Hermes（进化引擎 + 用户建模）
    ↓
两者协同 = OpenClaw主框架 + Hermes辅助Agent
```

---

## 7. 🔧 安装与使用

### 快速开始

```bash
# Docker一键部署
docker run -d -p 8000:8000 nousresearch/hermes-agent

# 源码安装
git clone https://github.com/nousresearch/hermes-agent
cd hermes-agent
pip install -e .
hermes-agent start
```

### 自进化引擎安装

```bash
# 安装自进化组件
git clone https://github.com/nousresearch/hermes-agent-self-evolution
cd hermes-agent-self-evolution
pip install -e .

# 启动进化
hermes-agent evolve --skill <skill-name>
```

### 核心命令

```bash
hermes-agent start              # 启动
hermes-agent skill list         # 查看Skills
hermes-agent memory search       # 搜索记忆
hermes-agent session list       # 历史会话
hermes-agent doctor             # 全面检查
hermes-agent evolve --all       # 全量进化
```

---

## 8. 📊 技术规格

| 规格 | 数值 |
|------|------|
| **GitHub Stars** | 32K+（2026-04持续增长） |
| **最新版本** | v0.7.0（2026-04-03） |
| **创始人** | Nous Research |
| **开源协议** | MIT |
| **最低运行配置** | $5 VPS |
| **进化提升** | 39.5% quality score |
| **支持平台** | 6+（Telegram/Discord/Slack/WhatsApp/...） |

---

## 9. 🕳️ 避坑指南

### 🔴 坑1：Skill创建泛滥
**问题**：Agent过于积极创建Skill，Skill库臃肿
**解决**：配置创建阈值
```yaml
skill_creation:
  min_task_complexity: 3
  review_required: true
```

### 🔴 坑2：进化周期不足
**问题**：刚用就想看到效果
**解决**：持续使用1-3天，进化需要积累

### 🔴 坑3：记忆检索不准
**问题**：跨会话记忆相关度不高
**解决**：定期运行 `hermes-agent memory optimize`

---

## 10. 💡 对OpenClaw的启示

### OpenClaw缺什么？

| 缺失维度 | Hermes方案 | OpenClaw现状 |
|----------|-----------|--------------|
| 自动进化 | GEPA DSPy | Skills人工维护 |
| 用户建模 | AI自动观察 | 手动SOUL.md |
| 记忆闭环 | 三层内置 | 梦境记忆（外置） |

### OpenClaw可以借鉴

1. **引入GEPA进化机制** → 自动优化Skills质量
2. **强化用户建模** → 从行为中学习用户偏好
3. **与Hermes协同** → 把Hermes作为OpenClaw的辅助Agent

---

## 11. 📊 总结

| 维度 | 评分 |
|------|------|
| **创新性** | ⭐⭐⭐⭐⭐ |
| **实用性** | ⭐⭐⭐⭐ |
| **技术深度** | ⭐⭐⭐⭐⭐ |
| **社区活跃** | ⭐⭐⭐⭐⭐ |
| **与OpenClaw互补** | ⭐⭐⭐⭐⭐ |

**一句话总结：** Hermes = **自进化 + 内置缰绳**；OpenClaw = **多渠道 + Skills生态**。两者不是竞争，是组合。

---

## 相关资料

| 资源 | 链接 |
|------|------|
| 官网 | https://hermes-agent.ai/ |
| GitHub | https://github.com/nousresearch/hermes-agent |
| 自进化引擎 | https://github.com/NousResearch/hermes-agent-self-evolution |
| 文档 | https://hermes-agent.nousresearch.com/docs/ |
| 抖音视频 | Gggda - Hermes最佳实践(一)-概念篇 |
