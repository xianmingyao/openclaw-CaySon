# 来源摘要：graphify-openclaw-usage-analysis-2026-05-07.md

> 原始路径：raw/graphify-openclaw-usage-analysis-2026-05-07.md
> 摄入时间：2026-05-07 15:56
> 验收状态：[~] pending

## 核心观点

报告详细介绍了 Graphify 的安装、使用流程及其与其他工具如 OpenClaw 和 Claude Code 的集成方式。

## 关键细节

# Graphify 完整使用流程分析报告

> 分析日期：2026-05-07
> 源码：https://github.com/safishamsi/graphify

---

## 一、核心定位

Graphify 是**代码知识图谱构建工具**，将任意代码/文档/视频/图片文件夹转换为可查询的知识图谱。

**与 MAGMA 图谱的关系：**
- Graphify = **代码/文档级图谱**（代码结构、跨文件关系）
- MAGMA = **记忆/知识级图谱**（用户交互、学习积累）

---

## 二、安装与配置

### 2.1 安装

```bash
# 官方包名是 graphifyy（双y）
uv tool install graphifyy && graphify install

# 可选依赖
pip install 'graphifyy[office]'    # docx/xlsx 支持
pip install 'graphifyy[video]'     # YouTube/视频转录
pip install 'graphifyy[mcp]'       # MCP 服务
```

### 2.2 OpenClaw 平台配置

```bash
# 安装 OpenClaw 集成
graphify install --platform claw

# 这会在 OpenClaw 中注册 skill，使其可以被触发
```

### 2.3 API Key 配置（用于语义提取）

```bash
# 语义提取（文档/图片）需要以下任一 Key
export GEMINI_API_KEY=xxx      # 默认用 Gemini
export ANTHROPIC_API_KEY=xxx   # 可选 Claude
export OPENAI_API_KEY=xxx      # 可选 GPT
export MOONSHOT_API_KEY=xxx   # 可选 Kimi

# 指定模型
export GRAPHIFY_GEMINI_MODEL=gemini-3-pro-preview
```

**注意：代码 AST 提取完全本地进行，无需 API Key**

---

## 三、触发图谱构建（存入数据）

### 3.1 完整 Pipeline

## 相关实体
- [[Graphify]]
- [[MAGMA 图谱]]
- [[AST提取]]
- [[Leiden 社区检测]]
- [[OpenClaw 平台]]
- [[API Key配置]]
- [[Git Hook]]
- [[增量更新]]
- [[Claude Code]]
- [[Codex]]
- [[MCP]]

## 相关概念
- [[代码知识图谱构建工具]]
- [[Graphify]]
- [[MAGMA 图谱]]
- [[AST提取]]
- [[Leiden 社区检测]]
- [[语义提取]]
- [[Git Hook]]
- [[增量更新]]
- [[OpenClaw 平台]]
- [[API Key配置]]
- [[命令行触发]]
- [[增量更新]]
- [[Watch模式]]
- [[图谱数据结构]]
- [[Claude Code集成]]
- [[Codex集成]]
- [[MCP工具调用]]

---
*由 Karpathy 知识库系统自动生成*
