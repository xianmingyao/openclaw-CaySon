# 来源摘要：github-projects-10-shandian-2026-05-07.md

> 原始路径：raw/github-projects-10-shandian-2026-05-07.md
> 摄入时间：2026-06-03 08:50
> 验收状态：[~] pending

## 核心观点

该文件分析了AI架构图生成工具fireworks-tech-graph及10个开源神器，涵盖AI效率、多模态检索、自动化与求职辅助等方向。

## 关键细节

# fireworks-tech-graph 项目研究报告

## 📌 一句话定位

> **用中文描述系统架构，几秒钟生成 SVG + PNG 技术图** —— Claude Code Skill，专门解决程序员画架构图的痛点

## 📦 核心功能

| 功能 | 说明 |
|------|------|
| **输入** | 中文自然语言描述 |
| **输出** | SVG + PNG（1920px 2x视网膜分辨率）|
| **风格** | 7种视觉风格 |
| **图类型** | 14种UML图 + AI/Agent专属图 |

## 🎨 7种视觉风格

| # | 风格 | 背景 | 适用场景 |
|---|------|------|----------|
| 1 | 扁平图标风 | 白色 | 博客、文档、PPT |
| 2 | 暗黑极客风 | #0f0f1a | GitHub README、开发者文章 |
| 3 | 工程蓝图风 | #0a1628 | 架构设计、工程规范 |
| 4 | Notion极简风 | 白色 | Notion、Wiki |
| 5 | 玻璃态卡片风 | 深色渐变 | 产品官网、Keynote |
| 6 | Claude官方风格 | #f8f6f3 | Anthropic风格 |
| 7 | OpenAI官方风格 | 白色 | OpenAI风格 |

## 📊 支持的图类型

### AI/Agent专属
- RAG Pipeline
- Agentic Search
- Mem0记忆架构
- Multi-Agent协作
- Tool Call流程
- Agent记忆类型（5种）

### UML 14种
类图、组件图、部署图、包图、复合结构图、对象图、用例图、活动图、状态机图、序列图、通信图、时序图、交互概览图、ER图

## 🔧 安装方式

```bash
# Claude Code用户
npx skills add yizhiyanhua-ai/fireworks-tech-graph

# 或直接克隆
git clone https://github.com/yizhiyanhua-ai/fireworks-tech-graph.git ~/.claude/skills/
```

## 📝 触发词

```
画图 

## 相关实体
- [[fireworks-tech-graph]]
- [[Claude Code Skill]]
- [[OpenClaw]]
- [[Graphify]]
- [[Caveman]]
- [[Lum]]
- [[Codeburn]]
- [[MechanicalSculptor]]
- [[DesignExtract]]
- [[PnOps]]
- [[BrowserHarness]]
- [[n8n MCP-Server]]
- [[Mem0]]
- [[RAG Pipeline]]
- [[Multi-Agent协作]]
- [[Agent记忆类型]]
- [[Anthropic风格]]
- [[OpenAI风格]]
- [[GitHub]]
- [[NPM]]
- [[MIT License]]
- [[Python]]
- [[Shell]]
- [[Whisper]]
- [[GPT]]
- [[MCP协议]]
- [[Notion]]
- [[Keynote]]
- [[PPT]]
- [[博客]]
- [[技术文档]]
- [[项目汇报]]
- [[AI求职助手]]
- [[简历PDF]]
- [[求职追踪表]]

## 相关概念
- [[技术图自动生成]]
- [[AI/Agent架构图]]
- [[UML图类型]]
- [[视觉风格定制]]
- [[语义形状词汇]]
- [[语义箭头系统]]
- [[开源工具推荐]]
- [[多模态RAG检索]]
- [[AI编程效率优化]]
- [[自动化流程构建]]
- [[求职辅助工具]]
- [[浏览器自动化]]
- [[开源项目集成]]

---
*由 Karpathy 知识库系统自动生成*
