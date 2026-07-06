# Vobcoding 开发流程规范

> **"先用头脑风暴分析问题，再用 gstack 管理实施，用 claude-mem 更新记忆，让 code-review-graph 把控质量。"**

---

## 1. `.ccg` 任务管理系统说明

### 1.1 什么是 `.ccg`

`.ccg/` 是 CCG Workflow 的任务管理系统目录，包含：
- `.ccg/tasks/` - 存储结构化任务（task.json、requirements.md、plan.md、review.md）
- 每个任务有独立子目录，包含需求、计划、审查等文件

### 1.2 当前项目状态

**当前项目不使用 `.ccg` 任务管理系统。**

原因：
- `.ccg` 是为代理式任务追踪设计的，但本项目采用更轻量的对话驱动方式
- 所有需求、计划、审查直接通过自然对话和文档管理
- 不需要维护额外的 task.json 结构

### 1.3 如何禁用 `.ccg`

在 CLAUDE.md 中已配置：
```markdown
## CCG 任务管理
- `.ccg/tasks/` 是 CCG Workflow 的任务追踪目录，**当前项目不使用**
- 所有任务直接通过自然对话管理，不需要创建 task.json
```

如需完全禁用，删除或重命名 `.ccg/` 目录即可：
```bash
mv .ccg .ccg.disabled  # 临时禁用
# 或
rm -rf .ccg            # 完全删除（不推荐，保留归档）
```

---

## 2. Vobcoding 标准流程

### 2.1 流程总览

```
用户问题
    ↓
[Step 1] brainstorming  ← 头脑风暴分析
    ↓
[Step 2] 制定计划       ← gstack plan 技能
    ↓
[Step 3] 实施与测试     ← gstack qa/investigate 技能
    ↓
[Step 4] 更新记忆       ← claude-mem 技能
    ↓
[Step 5] 代码质检       ← code-review-graph 技能
    ↓
完成
```

### 2.2 Step 1: 头脑风暴（必须）

**技能路径：** `C:\Users\Administrator\.codex\plugins\superpowers\skills\brainstorming\SKILL.md`

**触发时机：** 任何新功能、bug、需求变更

**执行命令：**
```
/brainstorming
```

**核心要求：**
- `<HARD-GATE>` 不管问题多简单，都必须先头脑风暴才能开始写代码
- 理解用户意图、约束条件、成功标准
- 提出 2-3 个方案并给出建议
- 设计文档化并保存到 `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- **必须用户批准设计方案后才能进入下一步**

**头脑风暴检查清单：**
1. [ ] 探索项目上下文（文件、文档、最近提交）
2. [ ] 视觉问题？（如果是，提供 Visual Companion）
3. [ ] 提问澄清问题（一次一个）
4. [ ] 提出 2-3 个方案及权衡
5. [ ] 展示设计（按复杂度缩放）
6. [ ] 写设计文档
7. [ ] Spec 自检（占位符、内部一致性、范围、歧义）
8. [ ] 用户审查设计
9. [ ] 调用 writing-plans 技能

---

### 2.3 Step 2: 制定计划

**使用 gstack 技能：**
- `/plan-ceo-review` - CEO/创始人模式计划评审
- `/plan-eng-review` - 工程经理模式架构评审

**执行命令：**
```
/plan-eng-review   ← 评审实施计划
```

**计划内容要求：**
- 基于头脑风暴的设计文档
- 具体的任务分解（WBS）
- 依赖关系分析
- 验收标准

---

### 2.4 Step 3: 实施与测试

**使用 gstack 技能：**
- `/qa` - 系统化 QA 测试并修复 bug
- `/investigate` - 系统化根本原因调试
- `/review` - 预落地 PR 审查

**执行命令：**
```
/qa               ← 执行测试
/investigate      ← 调试问题
/review           ← 代码审查
```

**关键原则：**
- 测试驱动：先写测试，再实现
- 使用 `uv run python -m pytest` 运行测试
- 修复后必须重新运行测试验证

---

### 2.5 Step 4: 更新记忆

**技能路径：** `C:\Users\Administrator\.codex\plugins\claude-mem\`

**触发时机：** 完成一个功能模块、修复重要 bug、架构变更

**使用技能：**
- `/learn-codebase` - 学习整个代码库到记忆中
- `/mem-search` - 搜索已有记忆
- `/do` - 执行具体的记忆更新操作

**执行命令：**
```
/learn-codebase   ← 如果需要更新全量记忆
/do               ← 执行具体的记忆更新操作
```

**更新内容：**
- 项目架构决策
- 重要的实现细节
- 遇到的问题和解决方案
- 未来的改进方向

---

### 2.6 Step 5: 代码质检

**使用技能：**
- `/review` - 预落地 PR 审查（使用 code-review-graph）
- `/codex` - OpenAI Codex 第二方意见

**执行命令：**
```
/review           ← 运行 code-review-graph 质量检查
/codex            ← 获取第二方审查意见
```

**检查内容：**
- [ ] 代码乱码/编码问题
- [ ] 潜在的安全漏洞
- [ ] 代码质量问题（复杂度、命名、可维护性）
- [ ] 逻辑错误
- [ ] 边界情况处理

---

## 3. 技能触发规则

### 3.1 自动触发规则

| 场景 | 触发的技能 |
|------|-----------|
| 新功能/需求变更 | `/brainstorming` → `/plan-eng-review` → `/qa` → `/do` → `/review` |
| Bug 修复 | `/investigate` → `/qa` → `/do` → `/review` |
| 代码变更 > 30 行 | `/review` → `/codex` |
| 安全相关变更 | `/verify-security` |
| 重构 | `/review` → `/verify-change` → `/verify-quality` |

### 3.2 技能路径参考

| 技能 | 路径 |
|------|------|
| brainstorming | `C:\Users\Administrator\.codex\plugins\superpowers\skills\brainstorming\` |
| gstack (plan, qa, review) | 直接在 Claude Code 调用 `/plan-eng-review`, `/qa`, `/review` |
| claude-mem | `C:\Users\Administrator\.codex\plugins\claude-mem\` |
| code-review-graph | `E:\workspace\skills\jingmai-product-publish\.code-review-graph\` |

---

## 4. 快速参考命令

```bash
# Step 1: 头脑风暴
/brainstorming

# Step 2: 计划评审
/plan-eng-review

# Step 3: 测试与调试
/qa
/investigate

# Step 4: 更新记忆
/learn-codebase
/do

# Step 5: 代码审查
/review
/codex
```

---

## 5. 注意事项

### 5.1 关于 `.ccg`
- `.ccg/tasks/` 是归档的任务目录
- 当前项目通过对话管理任务，不需要在 `.ccg` 中创建新任务
- 旧任务保留在 `.ccg/tasks/archive/` 中供参考

### 5.2 关于 code-review-graph
- 当前项目已有 `.code-review-graph/` 目录
- 使用 `/review` 命令运行代码审查
- 检查 graph.db 是否需要更新

### 5.3 关于 gstack
- 所有 gstack 技能直接在 Claude Code 调用
- 技能会自动激活，无需手动加载
- 如果技能不工作，运行：`cd ~/.claude/skills/gstack && ./setup`
