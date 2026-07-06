# gstack 使用指南

> 来源：@阿博粒 抖音视频

> 整理时间：2026-03-28

---

## 🎯 这是什么

✅ **gstack** 是 Y Combinator CEO Garry Tan 开源的创业方法论封装工具

**核心数据：**

┌─ 项目数据 ─────────────────────────────────┐

│ Star：33.2k（两周狂揽3万+）              │

│ Fork：4k                                   │

│ 创始人：Garry Tan（YC CEO）               │

│ License：MIT                                │

│ 分支：76个                                 │

└────────────────────────────────────────────┘

**核心定位：**

使用 Garry Tan 的 Claude Code 设置：

15个具有主见的工具担任：

• CEO（首席执行官）

• Designer（设计师）

• Eng Manager（工程经理）

• Release Manager（发布经理）

• Doc Engineer（文档工程师）

• QA（测试工程师）

---

## 📝 关键功能点

### 1. 核心能力

• 将YC创业方法论封装成AI Agent

• 15个专业角色分工协作

• 支持Claude Code、Codex、Gemini等多Agent

• 创业导师：人手一个YC导师

• 打造一人公司独角兽

### 2. 源码结构

┌─ 项目结构 ─────────────────────────────────┐

│ agents/sdk         - Agent SDK核心           │

│ github/workflows   - CI/CD集成              │

│ bin               - 入口脚本               │

│ browse            - 浏览器自动化           │

│ config            - 配置管理               │

│ codex             - Codex集成               │

│ design-consultant - 设计顾问               │

│ design-review     - 设计审查               │

│ docs              - 文档                  │

│ document-release  - 文档发布               │

│ freeze           - 冻结机制               │

│ guard            - 安全守卫               │

│ gstack-upgrade   - 升级工具              │

└────────────────────────────────────────────┘

### 3. 技术特性

• 多Agent支持（Codex, Gemini, Claude）

• 安全Hook技能（技能使用遥测）

• Windows支持（Node.js Playwright fallback）

• 自动化工作流

---

## ⚡ 怎么使用

### 第一步：安装配置

1. git clone https://github.com/garrytan/gstack.git

2. cd gstack

3. 安装依赖

4. 配置API Key

### 第二步：启动服务

┌─ bash ──────────────────────────────────────┐

│ python -m gstack.cli serve                   │

│ # 或                                         │

│ ./bin/gstack serve                          │

└─────────────────────────────────────────────┘

### 第三步：使用Agent

• /ship  - 发布产品

• /review - 代码审查

• /design - 设计咨询

• /doc    - 文档生成

---

## ✅ 优点

• YC CEO背书，方法论权威

• 15个专业角色，覆盖创业全流程

• 两周3万+ stars，验证度极高

• MIT协议，完全开源

• 多Agent协作（Codex/Gemini/Claude）

• Windows支持友好

• 持续活跃更新（昨天还有commit）

---

## ❌ 缺点

• 学习成本较高（15个Agent协作）

• 需要配置多个API Key

• 国内访问GitHub可能受限

• 文档主要英文

• 角色分工复杂，调试困难

• 资源消耗大（多Agent）

---

## 🎬 使用场景

• 创业公司：一人公司快速启动

• 产品发布：从0到1的完整流程

• 代码审查：多角色把关质量

• 设计评审：专业设计顾问

• 文档建设：自动化文档生成

• 团队协作：模拟大型公司分工

---

## 🔧 运行依赖环境

┌─ 环境要求 ─────────────────────────────────┐

│ 运行时                                    │

│   • Python 3.8+                         │