# Matt Pocock Skills - Claude Code 工程师技能包

## 1. 🎯 这是什么

**Matt Pocock Skills** 是 TypeScript 领域顶级教育者 Matt Pocock（Total TypeScript 创始人，前 Vercel Developer Advocate）将自己每日使用的 Claude Code 技能开源的项目。

**GitHub**: mattpocock/skills (⭐ 62k+)
**核心理念**: "Skills for Real Engineers" — 告别 Vibe Coding，让 AI 按工程规范写代码

---

## 2. 📝 16个技能详解

Matt Pocock 把自己的 `.claude/` 目录里每天用的 16 个 Skill 全部开源，覆盖 **4 大类**：

### 📋 Issue 管理类

| 技能 | 命令 | 功能 |
|------|------|------|
| **Triage** | `/triage` | Issue 分类管理，自动识别优先级和标签 |
| **Spec** | `/spec` | 生成规格说明文档 |
| **Review** | `/review` | 代码评审，检查潜在问题 |

### 🧪 测试与质量类

| 技能 | 命令 | 功能 |
|------|------|------|
| **Test** | `/test` | TDD 红绿重构循环，确保功能健壮 |
| **Coverage** | `/coverage` | 检查测试覆盖率 |
| **Lint** | `/lint` | 代码风格检查和修复 |

### 📐 设计与架构类

| 技能 | 命令 | 功能 |
|------|------|------|
| **Architecture** | `/arch` | 架构评审和改进建议 |
| **Diagram** | `/diagram` | 生成架构图/流程图 |
| **Doc** | `/doc` | 生成技术文档 |

### 🚀 开发效率类

| 技能 | 命令 | 功能 |
|------|------|------|
| **Git** | `/git` | Git 操作护栏，防止误操作 |
| **Debug** | `/debug` | 结构化调试流程 |
| **Refactor** | `/refactor` | 安全重构指导 |

---

## 3. ⚡ 核心问题解决

Matt Pocock 认为 Agent 失败的 **4 个根因**：

| 根因 | 问题 | 对应技能 |
|------|------|----------|
| **需求不清** | 需求描述模糊，导致方向错误 | `/spec` `/triage` |
| **对话啰嗦** | 上下文太长，AI 遗忘关键信息 | 分段对话、上下文管理 |
| **代码跑不通** | 缺少测试覆盖，改动引入 Bug | `/test` `/coverage` |
| **代码变屎山** | 缺乏架构意识，技术债累积 | `/arch` `/refactor` |

---

## 4. 🔧 使用方法

### 安装
```bash
# 1. 克隆仓库
git clone https://github.com/mattpocock/skills.git

# 2. 在 Claude Code 中运行
/setup-matt-pocock-skills

# 3. 按提示配置
# - 选择 Issue Tracker (GitHub / Linear / 本地文件)
# - 配置标签规则
# - 设置文档保存位置
```

### 常用命令
```bash
/triage          # 分类 Issue
/spec            # 生成规格说明
/test            # TDD 开发
/review          # 代码评审
/debug           # 结构化调试
/doc             # 生成文档
```

---

## 5. ✅ 优点

- ✅ **工程级输出**：不是 vibe coding，是真正的工程实践
- ✅ **可组合**：每个技能独立，可按需选装
- ✅ **经过实战**：直接从 Matt 日常使用的 `.claude` 目录开源
- ✅ **小白友好**：不需要 TDD 经验也能上手
- ✅ **社区活跃**：62k+ stars，大量 fork 和贡献

---

## 6. ❌ 缺点

- ❌ 主要是 TypeScript/React 方向
- ❌ 需要手动配置（虽然有引导）
- ❌ 部分技能依赖特定工具链

---

## 7. 🎬 使用场景

| 场景 | 推荐技能 |
|------|----------|
| 新功能开发 | `/spec` → `/test` → `/review` |
| Bug 修复 | `/debug` → `/test` → `/review` |
| 代码重构 | `/arch` → `/refactor` → `/test` |
| 文档生成 | `/doc` |
| Issue 管理 | `/triage` |

---

## 8. 📊 总结

| 维度 | 评分 |
|------|------|
| 内容质量 | ⭐⭐⭐⭐⭐ |
| 实用价值 | ⭐⭐⭐⭐⭐ |
| 工程规范 | ⭐⭐⭐⭐⭐ |
| 学习曲线 | ⭐⭐⭐（有引导，但需时间适应） |

**一句话评价**：告别 vibe coding，用工程思维驾驭 AI 编程！

---

## 9. 🔗 相关资源

- GitHub: https://github.com/mattpocock/skills
- 视频教程: B 站搜索 "Matt Pocock Skills"
- 安装指南: 运行 `/setup-matt-pocock-skills`

---

*📅 收录日期：2026-05-08*
*🔗 来源：抖音 @stock master / @IT咖啡馆 推荐*
*⭐ Stars: 62k+ (持续增长中)*
