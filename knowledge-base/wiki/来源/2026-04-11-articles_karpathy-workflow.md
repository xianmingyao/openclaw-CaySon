# 来源摘要：articles\karpathy-workflow.md

> 原始路径：raw/articles\karpathy-workflow.md
> 摄入时间：2026-04-11 20:03

## 核心观点

Karpathy 工作流利用 LLM 将原始资料编译成 wiki，通过三步曲实现知识管理。

## 关键细节

# Karpathy 知识库工作流

## 核心理念

用 LLM 把原始资料（论文/文章/代码）编译成 wiki 知识库。

## 工作流三步曲

### STEP 01: 收集
- raw/ 目录存放原始资料
- 支持：论文/文章/GitHub/数据集/截图
- 使用 Obsidian Web Clipper 保存网页

### STEP 02: 编译
- LLM 读取 raw/ 所有文件
- 提取核心概念
- 生成结构化 wiki 文章
- 建立双向链接

### STEP 03: 查询
- 直接向 LLM 提问
- LLM 在 wiki/ 中查找答案
- 好答案归档回 wiki

## 为什么不需要 RAG？

100 篇/40 万字规模下，LLM 的上下文窗口足够大，直接把所有 wiki 内容放进 context 就够了。

## 相关概念

- [[LLM]]
- [[Obsidian]]
- [[知识管理]]
- [[RAG]]


## 相关实体
- [[Karpathy 知识库工作流]]
- [[Obsidian Web Clipper]]
- [[raw/]]
- [[wiki/]]
- [[RAG]]

## 相关概念
- [[LLM]]
- [[知识库]]
- [[wiki]]
- [[工作流]]
- [[双向链接]]

---
*由 Karpathy 知识库系统自动生成*

