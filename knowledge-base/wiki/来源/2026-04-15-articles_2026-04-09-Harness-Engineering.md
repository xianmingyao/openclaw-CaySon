# 来源摘要：articles\2026-04-09-Harness-Engineering.md

> 原始路径：raw/articles\2026-04-09-Harness-Engineering.md
> 摄入时间：2026-04-15 09:47
> 验收状态：[~] pending

## 核心观点

Harness Engineering 是让 AI Agent 可靠工作的关键技术，通过约束、反馈和控制三大组件实现。

## 关键细节

# Harness Engineering（驾驭工程）

> 来源：知乎/AI铺子综合整理
> 日期：2026-04-09
> 主题：2026年最火的工程范式

## 一句话总结

2025年证明了 Agent 能工作，2026年要解决的是如何让 Agent **可靠地工作**。答案就是 Harness Engineering。

## 核心定位

**Harness Engineering = AI 工程领域继 Prompt Engineering、Context Engineering 之后的第三次重心迁移**

## 为什么需要 Harness？

### 问题：模型幻觉与熵增

- **幻觉**：LLM 会编造不存在的信息
- **熵增**：随着对话进行，上下文会越来越混乱

### 解决方案：Harness 作为"操作系统"

Harness 是 AI 智能体的"操作系统"，通过以下方式解决问题：

| 能力 | 说明 |
|------|------|
| **约束（Constraint）** | 限制 Agent 的行为范围 |
| **反馈（Feedback）** | 让 Agent 知道自己的行为是否正确 |
| **控制（Control）** | 控制 Agent 的执行流程 |

## 演进历程

### 第一阶段：Prompt Engineering（提示词工程）
- 2019-2022年
- 核心：如何写好提示词
- 局限：只能控制单次输出

### 第二阶段：Context Engineering（上下文工程）
- 2022-2024年
- 核心：如何组织上下文
- 局限：上下文长度有限制

### 第三阶段：Harness Engineering（驾驭工程）
- 2024-至今
- 核心：如何让 Agent 可靠地工作
- 优势：系统化、可持续、可控

## Harness 的构成

### 三大核心组件

```
Harness（驾驭系统）
├── Constraint Engine（约束引擎）
│   ├── 规则定义
│   ├── 安全边界
│   └── 行为限制
├── Feedback System（反馈系统）
│   ├── 状态监控
│   ├── 结果验证
│   └── 错误处理
└── Control Loop（

## 相关实体
- [[Anthropic]]
- [[OpenAI]]
- [[DeepMind]]
- [[字节跳动]]

## 相关概念
- [[Harness Engineering]]
- [[Agent]]
- [[Constraint Engine]]
- [[Feedback System]]
- [[Control Loop]]
- [[Prompt Engineering]]
- [[Context Engineering]]
- [[LLM]]
- [[AI Agent]]
- [[DeerFlow]]

---
*由 Karpathy 知识库系统自动生成*
