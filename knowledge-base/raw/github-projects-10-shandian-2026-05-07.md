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
画图 / 帮我画 / 生成图 / 做个图 / 架构图 / 流程图 / 可视化一下 / 出图
```

## 💡 核心价值

1. **不用手画图** - 中文描述 → 自动生成
2. **AI/Agent领域专属** - 内置RAG、Mem0、Multi-Agent等Pattern
3. **语义形状词汇** - LLM=双边框、Agent=六边形、VectorStore=圆柱
4. **语义箭头系统** - 颜色+虚线编码含义（写入/读取/异步/循环）

## 📊 项目信息

| 项目 | 内容 |
|------|------|
| GitHub | https://github.com/yizhiyanhua-ai/fireworks-tech-graph |
| NPM | https://www.npmjs.com/package/@yizhiyanhua-ai/fireworks-tech-graph |
| Stars | 2.4k |
| License | MIT |
| 语言 | Python + Shell |

## 🎯 与OpenClaw集成

**可以整合的方式：**
1. 安装为OpenClaw Skill
2. 写一个OpenClaw Skill包装器
3. 直接在对话中调用

**适用场景：**
- 知识库架构图生成
- 技术文档自动配图
- 项目汇报可视化

## 📅 研究时间
2026-04-15

---

# 闲田的10个GitHub开源神器

> 来源：抖音【闲田的作品】《99%的人不知道的10个github开源神器》
> 视频链接：https://v.douyin.com/QyFKGiM3R-k/
> 视频时长：06:16

## 📌 一句话定位

> **AI编程、自动化、求职辅助领域的10个宝藏开源工具**

## 📦 10个开源神器

| # | 工具 | 时间 | 核心功能 | GitHub | 学习价值 |
|---|------|------|----------|--------|----------|
| 1 | **Caveman** | 00:22 | 让AI回答更简洁，节省token，提高回答正确率 | 待查 | ⭐⭐⭐⭐ |
| 2 | **Graphify** | 01:21 | 多模态RAG检索系统，处理视频/截图/流程图，降低API费用 | 待查 | ⭐⭐⭐⭐⭐ |
| 3 | **Lum** | 02:02 | 视频→截图+音频→Whisper文本→GPT处理 | 待查 | ⭐⭐⭐⭐ |
| 4 | **Codeburn** | 03:05 | 追踪AI编程工具的token消耗和花费，提供优化建议 | 待查 | ⭐⭐⭐⭐⭐ |
| 5 | **MechanicalSculptor** | 03:27 | 美化AI生成的前端界面，实时预览功能 | 待查 | ⭐⭐⭐ |
| 6 | **DesignExtract** | 03:45 | 提取网站设计参考（排版系统、响应式方案等） | 待查 | ⭐⭐⭐⭐ |
| 7 | **PnOps** | 04:17 | AI求职助手，生成定制化简历PDF，更新求职追踪表 | 待查 | ⭐⭐⭐⭐ |
| 8 | **BrowserHarness** | 04:59 | 自我进化的浏览器自动化，提高成功率 | 待查 | ⭐⭐⭐⭐⭐ |
| 9 | **n8n MCP-Server** | 05:25 | TypeScript构建自动化流程，提高成功率 | 待查 | ⭐⭐⭐⭐⭐ |

## 🔍 重点关注

### ⭐⭐⭐⭐⭐ 高价值项目
1. **Graphify** - 多模态RAG检索，视频/截图/流程图通吃，降低API费用
2. **Codeburn** - token消耗追踪，适合AI编程工具成本优化
3. **BrowserHarness** - 自我进化的浏览器自动化，与OpenClaw browser-automation相关
4. **n8n MCP-Server** - TypeScript自动化流程，MCP协议实践

### ⭐⭐⭐⭐ 中高价值项目
5. **Lum** - 视频处理 pipeline，Whisper + GPT 组合
6. **Caveman** - AI回答简化，token节省
7. **DesignExtract** - 设计参考提取，前端开发辅助
8. **PnOps** - 简历PDF生成，求职追踪

## 💡 分类整理

### AI效率优化
- Caveman - AI回答简化
- Codeburn - token消耗追踪

### 多模态检索
- Graphify - 多模态RAG
- Lum - 视频→文本 pipeline

### 前端/设计
- MechanicalSculptor - AI前端美化
- DesignExtract - 设计参考提取

### 自动化
- BrowserHarness - 浏览器自动化进化
- n8n MCP-Server - 自动化流程

### 求职/效率
- PnOps - 简历生成

## 📅 研究时间
2026-05-07
