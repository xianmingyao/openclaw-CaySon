# Code-Review-Graph 代码知识图谱

## 1. 🎯 这是什么（简介）

**code-review-graph** 是一款为 AI 编程助手打造的**本地代码知识图谱工具**，核心是用增量图谱替代全量读码，大幅降低 AI 上下文 Token 消耗、提升代码审查与理解效率。

通过 Tree-sitter 解析代码构建结构化图谱，只传递 AI 真正需要的相关文件，实现 **6.8× 代码审查 Token 节省**，日常编码任务最高可达 **49× 节省**。

---

## 2. 📝 关键功能点

| 功能 | 描述 |
|------|------|
| **本地知识图谱** | 用 Tree-sitter 解析代码，构建函数/类/导入/调用/继承的节点图谱 |
| **增量更新** | <2秒完成增量更新，SHA-256 哈希检查只重解析变更文件 |
| **Blast-radius 分析** | 追踪变更影响范围，精准定位受影响文件 |
| **MCP 集成** | 通过 Model Context Protocol 与 Claude Code/Cursor 等工具集成 |
| **语义搜索** | 向量嵌入搜索（sentence-transformers/Gemini/MiniMax） |
| **多平台支持** | Claude Code, Cursor, Windsurf, Codex, Zed, Continue, OpenCode, Qwen, Qoder, Kiro |
| **23+语言支持** | Python, TypeScript, Go, Rust, Java, Scala, C#, Ruby, Kotlin, Swift, PHP, Solidity, C/C++, Dart, R, Perl, Lua, Zig, PowerShell, Julia, Vue, Svelte + Jupyter |

---

## 3. ⚡ 怎么使用

### 安装

```bash
pip install code-review-graph
# 或
pipx install code-review-graph
```

### 自动配置（支持所有平台）

```bash
code-review-graph install
```

### 单独配置特定平台

```bash
code-review-graph install --platform claude-code  # 只配置 Claude Code
code-review-graph install --platform cursor        # 只配置 Cursor
code-review-graph install --platform kiro        # 只配置 Kiro
```

### 构建图谱

```bash
code-review-graph build  # 解析代码库
```

### Token 基准测试

```bash
code-review-graph eval --all  # 运行评估
```

---

## 4. ✅ 优点

- **🔴 极致 Token 节省**：代码审查 6.8×，日常编码 49×（Next.js monorepo 实测）
- **⚡ 增量更新 <2秒**：2900文件项目2秒内完成重索引
- **🔒 本地运行**：SQLite 存储，无外部数据库，无云依赖，代码不上传
- **🛠️ 多工具集成**：MCP 协议，支持 11+ AI 编程平台
- **🌐 多语言支持**：23 种编程语言 + Jupyter notebooks
- **📊 高级分析**：Blast-radius、Hub/Bridge 检测、Surprise 评分、知识差距分析
- **📤 多种导出**：GraphML/Neo4j/Obsidian/SVG/JSON

---

## 5. ❌ 缺点

- **⚠️ Windows 配置复杂**：需配置 `PYTHONUTF8=1`，避免 JSON 解析错误
- **⚠️ 预览模型 ID 风险**：使用 `-preview` 模型 ID 可能因维度变化导致全量重嵌入
- **⚠️ 当前嵌入范围**：仅嵌入函数签名（~10 tokens/node），非函数体/docstring
- **⚠️ 内存占用**：大型 monorepo 初始构建需要较多内存

---

## 6. 🎬 使用场景

| 场景 | 效果 |
|------|------|
| **代码审查** | 变更影响分析，精准定位需审查文件 |
| **Monorepo 开发** | 2.7万+文件的 Next.js monorepo → 仅15个文件需关注 |
| **日常编码** | AI 只读相关文件，49× Token 节省 |
| **代码理解** | 快速了解模块依赖、调用链、架构 |
| **重构辅助** | Rename preview、死代码检测 |
| **新人 onboarding** | 快速理解代码结构和依赖关系 |

---

## 7. 🔧 运行依赖环境

| 项目 | 要求 |
|------|------|
| **Python** | 3.10+ |
| **pip/pipx** | 最新版 |
| **uv** | 推荐安装（自动使用 uvx 模式） |
| **MCP 支持** | Claude Code / Cursor / Windsurf 等 |
| **操作系统** | macOS, Linux, Windows (需配置) |
| **数据库** | SQLite (本地 .code-review-graph/) |

---

## 8. 🚀 部署使用注意点

### Windows 配置（重要！）

Windows 用户在 `~/.claude.json` 中配置时：

```json
{
  "code-review-graph": {
    "command": "C:\\path\\to\\your\\venv\\Scripts\\code-review-graph.exe",
    "args": ["serve", "--repo", "C:\\path\\to\\your\\project"],
    "env": { "PYTHONUTF8": "1" }
  }
}
```

**不要** 使用 `cmd /c` 包装器，会导致 JSON 解析错误。

### 快速开始

1. `pip install code-review-graph`
2. `code-review-graph install`（自动检测并配置所有平台）
3. 重启编辑器/工具
4. 对 AI 说："Build the code review graph for this project"
5. 初始构建约10秒（500文件项目）

---

## 9. 🕳️ 避坑指南

| 坑 | 解决方案 |
|----|----------|
| **Invalid JSON: EOF while parsing** | Windows 配置不要用 `cmd /c`，直接用 .exe 路径 |
| **MCP error -32000: Connection closed** | 更新 fastmcp 到 3.2.4+，配置 PYTHONUTF8=1 |
| **预览模型 ID 风险** | 使用稳定模型：`text-embedding-3-small/large`、`Qwen/Qwen3-Embedding-8B` |
| **维度变化导致重嵌入** | 避免使用 `-preview` / `-beta` / `-exp` 模型 |
| **嵌入只含函数签名** | 当前 `_node_to_text` 仅嵌入签名，函数体嵌入是后续规划 |

---

## 10. 📊 总结

| 维度 | 评分 | 说明 |
|------|------|------|
| **学习价值** | ⭐⭐⭐⭐⭐ | Token 优化、MCP 集成、知识图谱最佳实践 |
| **实用性** | ⭐⭐⭐⭐⭐ | Monorepo 开发必备，AI 编码效率提升利器 |
| **技术深度** | ⭐⭐⭐⭐ | Tree-sitter 解析、MCP 协议、增量图谱 |
| **社区活跃** | ⭐⭐⭐⭐ | 持续迭代，v2.3.2 发布，6 个 PR 合并 |

### 关联项目

| 项目 | Stars | 定位 |
|------|-------|------|
| **graphify** | 25k | 代码→知识图谱，71.5x 更少 Token |
| **GitNexus** | - | MCP-Native 知识图谱，Claude Code/Cursor 结构感知 |

### 参考链接

- **GitHub**: https://github.com/tirth8205/code-review-graph
- **PyPI**: https://pypi.org/project/code-review-graph/
- **官网**: https://code-review-graph.com/
- **Discord**: https://discord.gg/3p58KXqGFN

---

## 📝 宁兄笔记

**核心原理**：用 Tree-sitter AST 解析代码，构建「节点（函数/类/导入）+ 边（调用/继承/测试）」的图谱，MCP 工具在审查时只返回 blast-radius 内的文件给 AI。

**落地场景**：OpenClaw 的 Claude Code 集成可以用这个优化 Agent 执行效率。
