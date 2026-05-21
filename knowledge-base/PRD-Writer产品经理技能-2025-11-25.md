# PRD Writer 产品经理技能合集

> **来源**：抖音@吃土说AI
> **视频日期**：2025-11-25
> **深挖时间**：2026-05-21

---

## 一句话评价

> **产品经理的 AI 写作神器** —— 多个 GitHub 项目让 Claude Code / OpenClaw 变成专业 PRD 撰写工具，从模糊需求到可交付文档，一条龙服务。

---

## 🔥 三大 PRD Writer 项目

### 1. Kira2red/Kira-product-monster-skills
**产品经理 AI 技能集（含 PRD/功能清单/白皮书）**

| 项目 | 说明 |
|------|------|
| **GitHub** | https://github.com/Kira2red/Kira-product-monster-skills |
| **Stars** | 118 ⭐ |
| **技能数** | 3个（PRD + 功能清单 + 白皮书）|
| **支持平台** | OpenClaw（推荐）、Antigravity、Codex |

**包含的技能：**

#### 1.1 2red-product-monster-prd
**顶级结构化 PRD 撰写工具**

| 特性 | 说明 |
|------|------|
| ✅ 序号层级体系 | 1/1-1/1-1-1 严格层级 |
| ✅ 微交互状态机 | 完整的状态描述 |
| ✅ 异常边界 | 容错处理 |
| ✅ 纯中文表达 | 无英文术语 |
| ✅ MECE 原则 | 相互独立、完全穷尽 |

#### 1.2 2red-product-monster-featurelist
**结构化功能清单提炼工具**

| 特性 | 说明 |
|------|------|
| ✅ MECE 拆解 | 功能模块拆分 |
| ✅ 多维表格 | 属性映射 |
| ✅ 软硬件依赖 | 分析依赖关系 |
| ✅ 用户故事 | 表述用户视角 |

#### 1.3 2red-product-whitepaper
**产品白皮书维护工具**

| 特性 | 说明 |
|------|------|
| ✅ PRD 增量合并 | 自动合并变更 |
| ✅ 模块化组织 | 按功能模块组织 |
| ✅ 版本号管理 | 自动管理 |
| ✅ 安全删除 | 确认机制 |

**安装（OpenClaw）：**
```bash
git clone https://github.com/Kira2red/Kira-product-monster-skills.git
cd Kira-product-monster-skills
ln -s $(pwd)/skills ~/.openclaw/skills/
```

**使用：**
```
@2red-product-monster-prd 帮我写一个用户登录模块的 PRD
```

---

### 2. GYX1616/prd-writer
**标准化 PRD 撰写 Claude Code Skill**

| 项目 | 说明 |
|------|------|
| **GitHub** | https://github.com/GYX1616/prd-writer |
| **Stars** | 1 ⭐ |
| **模板** | 完整版(7章节) + 简略版(3章节) |

**PRD 模板结构：**

#### 完整版（7章节）

| # | 章节 | 内容 |
|---|------|------|
| 1 | 功能描述 | 「是什么」+ 「为什么」|
| 2 | 交互逻辑 | 有序的步骤流程 |
| 3 | 跳转逻辑 | 导航表格 |
| 4 | 跳转过程逻辑 | 导航期间的系统行为 |
| 5 | 正向限制 | 允许的内容（限制/格式/角色）|
| 6 | 反向限制 | 不支持的内容 |
| 7 | 异常/空态/错误 | 错误状态、空态、边界情况 |

#### 简略版（3章节）

| # | 章节 | 内容 |
|---|------|------|
| 1 | 功能描述 | 「是什么」+ 「为什么」|
| 2 | 交互逻辑 | 核心用户流程 |
| 3 | 限制与异常 | 约束和错误处理合并 |

**安装：**
```bash
git clone https://github.com/GYX1616/prd-writer.git
ln -sf "$(pwd)/prd-writer" ~/.claude/skills/prd-writer
```

**使用：**
```
/prd-writer
帮我用完整版模板写一个「用户评论」功能的 PRD，保存到 ./docs/prd-v1.md
```

---

### 3. GarrusHuang/prd-writer
**专业级 PRD → .docx 输出**

| 项目 | 说明 |
|------|------|
| **GitHub** | https://github.com/GarrusHuang/prd-writer |
| **特点** | 输出专业格式 .docx 文件 |

**核心设计理念：**
- **不凭空创造业务规则** — 每个功能点必须通过三维度检查（数据源 / 业务规则 / 异常处理）
- **只做产品经理该做的事** — 定义做什么和为什么，不是怎么实现
- **交付物是真实文档** — .docx 格式，含封面、目录、三线表、页眉

**三种模式：**

| 模式 | 说明 |
|------|------|
| **New** | 从零开始 |
| **Complete** | 填充现有草案的空白 |
| **Research** | 仅收集领域背景知识 |

**PRD 结构：**

| 章节 | 说明 |
|------|------|
| Non-Goals | 明确范围边界及原因 |
| Given/When/Then | 验收标准，可直接用于测试计划 |
| Leading + Lagging 指标 | 提前指标（week-1验证）+ 滞后指标（长期）|
| Open Items | 未解决问题，带负责人和是否阻塞开发标记 |
| Domain Knowledge Memory | 领域知识记忆，下次 PRD 自动利用 |

**安装：**
```bash
git clone https://github.com/GarrusHuang/prd-writer.git ~/.claude/skills/prd-writer
```

**使用：**
```
帮我写一个「消息通知」功能的 PRD
```

---

## 📊 三大项目对比

| 特性 | Kira-product-monster-skills | GYX1616/prd-writer | GarrusHuang/prd-writer |
|------|---------------------------|---------------------|----------------------|
| **Stars** | 118 ⭐ | 1 ⭐ | - |
| **输出格式** | Markdown | Markdown | **.docx** |
| **模板结构** | 序号层级 | 7章/3章可选 | 完整专业结构 |
| **中文支持** | ✅ 纯中文 | ✅ 中英双语 | ✅ 中英双语 |
| **平台** | OpenClaw | Claude Code | Claude Code |
| **特殊功能** | PRD+功能清单+白皮书 | 双输入（口述+截图）| 三维度审查 |

---

## 🚀 快速上手

### 选择建议

| 需求 | 推荐 |
|------|------|
| **中文环境 + OpenClaw** | Kira-product-monster-skills |
| **Claude Code + 快速模板** | GYX1616/prd-writer |
| **专业交付物 + .docx** | GarrusHuang/prd-writer |
| **完整产品文档体系** | Kira-product-monster-skills |

### 安装步骤（以 Claude Code 为例）

```bash
# 1. 克隆最喜欢的项目
git clone https://github.com/Kira2red/Kira-product-monster-skills.git

# 2. 链接到 skills 目录
ln -sf "$(pwd)/skills/prd-writer" ~/.claude/skills/prd-writer

# 3. 在 Claude Code 中使用
/prd-writer
帮我写一个「用户登录」功能的 PRD
```

### 使用示例

```
PRD 写作示例：

@2red-product-monster-prd
写一个充电预约功能的 PRD，需要包含：
- 用户可以设置充电时间段
- 支持充至停止时间或充至上限两种模式
- 低电量时自动充电不受预约限制
```

---

## 🎯 PRD 写作最佳实践

### 1. 三维度审查（来自 GarrusHuang）

每个功能点必须回答：

```
1. 数据源 — 数据从哪里来？
2. 业务规则 — 规则是什么？
3. 异常处理 — 出错怎么办？
```

### 2. MECE 原则（来自 Kira）

| 原则 | 说明 |
|------|------|
| **相互独立** | 各点不重叠 |
| **完全穷尽** | 覆盖所有情况 |

### 3. Given/When/Then 验收标准

```
GIVEN（前提）: 用户已登录
WHEN（操作）: 点击"发表评论"按钮
THEN（结果）: 评论显示在评论区顶部
```

---

## 📝 模板选择指南

```
┌─────────────────────────────────────────────────────────────┐
│                    PRD 模板选择决策树                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  是否需要交付给开发团队？                                       │
│       ↓                                                      │
│  是 → 需要 .docx 格式？                                       │
│       ↓ 是    ↓ 否                                           │
│  Garrus    GYX1616（7章节完整版）                            │
│                                                             │
│       ↓                                                      │
│  否 → 是否需要功能清单+白皮书？                                │
│       ↓ 是    ↓ 否                                           │
│  Kira     GYX1616（3章节简略版）                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔗 相关链接

| 项目 | GitHub | Stars |
|------|--------|-------|
| **Kira 产品经理技能集** | https://github.com/Kira2red/Kira-product-monster-skills | 118 ⭐ |
| **GYX PRD Writer** | https://github.com/GYX1616/prd-writer | 1 ⭐ |
| **Garrus PRD Writer** | https://github.com/GarrusHuang/prd-writer | - |
| **AgentSkills 标准** | https://github.com/openclaw/openclaw | - |

---

**标签**：`#PRD` `#产品经理` `#需求文档` `#ClaudeCode` `#OpenClaw` `#吃土说AI` `#Skill` `#产品设计`
