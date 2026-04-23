# Google DESIGN.md 深度解析

> 🔬 调研日期：2026-04-23
> 📊 数据源：GitHub / Google Stitch / HuggingFace Papers

---

## 1. 🎯 这是什么（简介）

**Google DESIGN.md** 是 Google Stitch 团队提出的**设计规范描述语言**，以 Markdown 格式让 AI Agent 能够生成符合品牌规范的用户界面。

**定位**：
- `AGENTS.md` = **怎么做**（构建逻辑）
- `DESIGN.md` = **长什么样**（视觉规范）

> 核心理念：**像 HTML 统一网页标准一样，统一 AI 生成 UI 的设计规范**

---

## 2. 📝 关键功能点

### 核心功能
| 功能 | 说明 |
|------|------|
| **品牌视觉规范** | 颜色、字体、间距的数字化描述 |
| **Typography 规范** | 支持多语言（日文/欧文/中文）的排版规则 |
| **Design Tokens** | 设计变量（颜色/字号/间距）的标准化 |
| **组件状态** | 按钮/表单/导航的交互状态定义 |
| **Guardrails** | AI 生成 UI 时的设计护栏 |

### 解决的问题
1. **设计师-程序员对齐成本高** → 规范文本化，AI 直接读取
2. **AI 生成 UI 还原度差** → 提供精确设计 Token
3. **多语言 UI 规范缺失** → 日文/中文 typography 专项扩展

---

## 3. ⚡ 怎么使用

### 基本结构（9大章节）

```markdown
# 1. Visual Theme     — 视觉主题与氛围
# 2. Colors          — 色彩体系
# 3. Typography      — 排版规范（含多语言扩展）
# 4. Components      — 组件样式
# 5. Layout          — 布局原则
# 6. Depth & Shadow  — 深度与阴影
# 7. Guardrails      — 设计护栏（AI 专用）
# 8. Responsive      — 响应式规范
# 9. Agent Prompts   — Agent 使用指南
```

### 日文 Typography 扩展示例

| 项目 | 规范值 |
|------|--------|
| **字体栈** | フォントファミリー指定（和文→欧文→generic） |
| **行高** | 1.5-2.0（中文 1.7-2.0） |
| **字间距** | 0.04-0.1em（正文） |
| **禁则处理** | 句读点/括弧的行头行末规则 |
| **Proportional** | `比例制` vs `字数固定制` |

---

## 4. ✅ 优点

| 优点 | 说明 |
|------|------|
| **品牌一致性** | AI 生成的 UI 严格遵循设计规范 |
| **多语言支持** | 专为 CJK 字体设计，弥补西方案例不足 |
| **可机读** | Markdown 格式，AI 可直接解析 |
| **社区活跃** | awesome-design-md 已有 55+ 品牌案例 |
| **设计护栏** | 内置 Guardrails 防止 AI 自由发挥过度 |

---

## 5. ❌ 缺点

| 缺点 | 说明 |
|------|------|
| **规范维护成本** | 需要专人维护 DESIGN.md 文件 |
| **覆盖范围有限** | 目前主要是欧美日知名品牌 |
| **中文案例少** | CJK 扩展主要是日文，中文较少 |
| **版本同步难** | 品牌更新后需同步更新 DESIGN.md |

---

## 6. 🎬 使用场景

| 场景 | 用途 |
|------|------|
| **AI Coding Agent** | Claude Code / Cursor 生成 UI 时读取 DESIGN.md |
| **品牌 UI 生成** | 自动生成符合品牌规范的营销页面 |
| **跨平台一致性** | Web / Mobile / Desktop 使用同一套设计规范 |
| **设计系统文档化** | 将现有设计系统转换为 AI 可读的 Markdown |

---

## 7. 🔧 运行依赖环境

| 依赖 | 说明 |
|------|------|
| **Markdown 解析** | 任何支持 Markdown 的工具 |
| **浏览器 DevTools** | 用于从网站提取 CSS 设计 Token |
| **可选** | Stitch CLI 工具（设计 Token 可视化） |

---

## 8. 🚀 部署使用注意点

### 快速开始

```bash
# 1. 克隆 awesome-design-md 仓库
git clone https://github.com/VoltAgent/awesome-design-md.git

# 2. 查看已有品牌案例
cd awesome-design-md

# 3. 参考日文扩展版本
# https://github.com/kzhrknt/awesome-design-md-jp

# 4. 创建自己的 DESIGN.md
cp template/DESIGN.md your-brand/DESIGN.md
```

### 设计 Token 提取工具

| 工具 | 说明 |
|------|------|
| **Stitch** | Google 官方的设计 Token 提取 CLI |
| **bergside/design-md-firefox** | Firefox 扩展，从网站提取 DESIGN.md |

---

## 9. 🕳️ 避坑指南

### 坑1：CJK Typography 容易忽略
**问题**：直接用西方案例生成中文/日文 UI 会字体混乱
**解决**：使用 `awesome-design-md-jp` 的日文扩展模板

### 坑2：Design Token 版本不同步
**问题**：网站更新后 DESIGN.md 过期
**解决**：使用 Firefox 扩展定期重新提取

### 坑3：Guardrails 约束不足
**问题**：AI 生成的 UI 仍然自由发挥
**解决**：在 Guardrails 章节明确列出 Do's and Don'ts

---

## 10. 📊 总结

### 核心定位
**Google DESIGN.md = AI 时代的设计规范语言**

| 维度 | 评分 | 说明 |
|------|------|------|
| **学习价值** | ⭐⭐⭐⭐⭐ | 必学，Agent 标配 |
| **实用价值** | ⭐⭐⭐⭐ | 多语言 UI 开发神器 |
| **生态完善度** | ⭐⭐⭐ | 社区活跃但中文少 |

### 关键洞察

1. **双文件机制**：`AGENTS.md` + `DESIGN.md` = 完整项目规范
2. **Stitch 格式**：Google 提出的标准化设计描述格式
3. **多语言扩展**：日文案例比中文更完善（553 stars）
4. **工具链**：Firefox 扩展可自动从网站提取 DESIGN.md

### 相关资源

| 资源 | 链接 |
|------|------|
| **awesome-design-md** | https://github.com/VoltAgent/awesome-design-md |
| **日文扩展版** | https://github.com/kzhrknt/awesome-design-md-jp |
| **Firefox 提取扩展** | https://github.com/bergside/design-md-firefox |
| **Stitch 官方** | https://github.com/google-labs/designmd |

---

## 📌 与 OpenClaw 的关联

### OpenClaw AGENTS.md 对比

| 维度 | OpenClaw AGENTS.md | Google DESIGN.md |
|------|-------------------|------------------|
| **定位** | 行为准则 | 视觉规范 |
| **对象** | AI Agent | AI Coding Agent |
| **内容** | 工作流程/Skill | 颜色/字体/布局 |
| **格式** | Markdown | Markdown |
| **关系** | 独立使用 | 配合 AGENTS.md |

**结论**：DESIGN.md 是 OpenClaw AGENTS.md 的**视觉补充**，两者结合 = 完整 AI 项目规范
