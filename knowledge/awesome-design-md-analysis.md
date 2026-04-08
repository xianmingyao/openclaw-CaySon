# awesome-design-md 项目深度分析报告

> 来源：抖音@猿AI 视频「本周 GitHub 最火的设计师项目」
> GitHub：`VoltAgent/awesome-design-md` | Stars: 24.4k | MIT License

---

## 1. 🎯 这是什么

### 核心定位
**AI 时代的"设计交接单"格式** — 把热门网站的设计系统提取成 Markdown 文件，AI 编程工具（Claude Code/Cursor/OpenClaw）读取后直接生成像素级匹配 UI。

### 解决的问题
| 痛点 | 解决方案 |
|------|---------|
| 设计师和开发者语言不通 | 用 Markdown 作为"桥梁语言" |
| 设计稿还原耗时 | AI 读取 DESIGN.md 直接生成代码 |
| 设计系统维护成本高 | 开源社区共建，持续更新热门网站设计 |
| AI 编程工具 UI 不一致 | 提供标准化的设计规范文档 |

### 灵感来源
**Google Stitch** 提出的 `DESIGN.md` 概念：
- `AGENTS.md` → 编程 Agent 读（怎么构建）
- `DESIGN.md` → 设计 Agent 读（长什么样）

### 仓库结构
```
awesome-design-md/
├── design-md/
│   ├── linear.app/       # Linear 设计系统
│   │   ├── DESIGN.md     # 核心设计规范（Agent 读取）
│   │   ├── preview.html   # 浅色预览
│   │   └── preview-dark.html  # 深色预览
│   ├── vercel/           # Vercel 官网风格
│   ├── airbnb/           # Airbnb 风格
│   ├── cursor/           # Cursor IDE 风格
│   └── ... (58+ 平台)
├── README.md
└── CONTRIBUTING.md
```

### 平台覆盖（2026-04 最新：58 个）

| 分类 | 平台 |
|------|------|
| AI/ML | Claude, Cohere, ElevenLabs, Minimax, Mistral AI, Ollama, OpenCode AI, Replicate, RunwayML, Together AI, VoltAgent, x.ai |
| 开发工具 | Cursor, Expo, Linear, Lovable, Mintlify, PostHog, Raycast, Resend, Sentry, Supabase, Superhuman, Vercel, Warp, Zapier |
| 基础设施 | ClickHouse, Composio, HashiCorp, MongoDB, Sanity, Stripe |
| 设计/效率 | Airtable, Cal.com, Clay, Figma, Framer, Intercom, Miro, Notion, Pinterest, Webflow |
| 金融/Crypto | Coinbase, Kraken, Revolut, Wise |
| 企业/消费 | Airbnb, Apple, IBM, NVIDIA, SpaceX, Spotify, Uber |
| 汽车品牌 | BMW, Ferrari, Lamborghini, Renault, Tesla |

---

## 2. 📝 DESIGN.md 格式规范（9 大章节）

每个 DESIGN.md 文件严格按照 Google Stitch 规范，包含 **9 个标准章节**：

### 章节结构

| # | 章节 | 捕获内容 |
|---|------|---------|
| 1 | Visual Theme & Atmosphere | 氛围、密度、设计哲学 |
| 2 | Color Palette & Roles | 语义化颜色名称 + Hex + 功能角色 |
| 3 | Typography Rules | 字体族、完整层级表 |
| 4 | Component Stylings | 按钮、卡片、输入框、导航的各状态 |
| 5 | Layout Principles | 间距系统、网格、留白哲学 |
| 6 | Depth & Elevation | 阴影系统、表面层级 |
| 7 | Do's and Don'ts | 设计 guardrails 和反模式 |
| 8 | Responsive Behavior | 断点、触摸目标、折叠策略 |
| 9 | Agent Prompt Guide | 快速颜色参考 + 可用 Prompt 示例 |

---

## 3. ⚡ 格式详解

### 3.1 Visual Theme & Atmosphere（视觉主题与氛围）

**内容示例（Linear）：**
```markdown
Linear's website is a masterclass in dark-mode-first product design — 
a near-black canvas (`#08090a`) where content emerges from darkness 
like starlight. The overall impression is one of extreme precision 
engineering: every element exists in a carefully calibrated hierarchy 
of luminance.

**Key Characteristics:**
- Dark-mode-native: `#08090a` marketing background
- Inter Variable with `"cv01", "ss03"` globally
- Brand indigo-violet: `#5e6ad2` (bg) / `#7170ff` (accent)
- Semi-transparent white borders throughout
```

**作用：** 描述性段落 + 关键特征列表，让 AI 理解设计的"感觉"而非只读数值。

---

### 3.2 Color Palette & Roles（颜色系统）

**格式：** 语义化命名 + Hex 值 + 功能说明

```markdown
### Background Surfaces
- **Marketing Black** (`#010102` / `#08090a`): The deepest background
- **Panel Dark** (`#0f1011`): Sidebar and panel backgrounds
- **Level 3 Surface** (`#191a1b`): Elevated surface areas, card backgrounds

### Text & Content
- **Primary Text** (`#f7f8f8`): Near-white, default text color
- **Secondary Text** (`#d0d6e0`): Cool silver-gray for body text
- **Tertiary Text** (`#8a8f98`): Muted gray for placeholders

### Brand & Accent
- **Brand Indigo** (`#5e6ad2`): Primary brand color — CTA buttons
- **Accent Violet** (`#7170ff`): Brighter variant for interactive elements
```

**作用：** 颜色有语义化名称（如 "Brand Indigo" 而非 "Primary Blue"），方便 AI 按功能调用。

---

### 3.3 Typography Rules（字体系统）

**核心表格：完整字体层级**

| Role | Font | Size | Weight | Line Height | Letter Spacing | Notes |
|------|------|------|--------|-------------|----------------|-------|
| Display XL | Inter Variable | 72px | 510 | 1.00 | -1.584px | Hero headlines |
| Heading 1 | Inter Variable | 32px | 400 | 1.13 | -0.704px | Major section titles |
| Body | Inter Variable | 16px | 400 | 1.50 | normal | Standard reading text |
| Caption | Inter Variable | 13px | 400-510 | 1.50 | -0.13px | Metadata, timestamps |

**格式要点：**
- **必须包含：** 字体族、字重、行高、字间距的完整组合
- **OpenType 特性：** `"cv01", "ss03"` 等特殊字体特性需标注
- **Principles 段落：** 解释设计决策（如 "510 is the signature weight"）

---

### 3.4 Component Stylings（组件样式）

**格式：** 按组件类型分组，详细描述每个状态的样式

```markdown
### Buttons

**Ghost Button (Default)**
- Background: `rgba(255,255,255,0.02)`
- Text: `#e2e4e7`
- Padding: comfortable
- Radius: 6px
- Border: `1px solid rgb(36, 40, 44)`
- Use: Standard actions, secondary CTAs

**Primary Brand Button**
- Background: `#5e6ad2`
- Text: `#ffffff`
- Hover: `#828fff` shift
- Use: Primary CTAs ("Start building", "Sign up")

### Cards & Containers
- Background: `rgba(255,255,255,0.02)` to `rgba(255,255,255,0.05)`
- Border: `1px solid rgba(255,255,255,0.08)`
- Radius: 8px (standard), 12px (featured)
```

**覆盖的组件类型：**
- Buttons（所有变体）
- Cards & Containers
- Inputs & Forms
- Badges & Pills
- Navigation
- Image Treatment

---

### 3.5 Layout Principles（布局原则）

```markdown
### Spacing System
- Base unit: 8px
- Scale: 1px, 4px, 7px, 8px, 11px, 12px, 16px, 19px, 20px, 22px, 24px, 28px, 32px, 35px

### Grid & Container
- Max content width: approximately 1200px
- Hero: centered single-column with generous vertical padding

### Whitespace Philosophy
- **Darkness as space**: Empty space isn't white — it's absence.
- **Section isolation**: 80px+ vertical padding, no visible dividers
```

---

### 3.6 Depth & Elevation（深度系统）

**格式：** 层级表格 + 阴影配方

```markdown
| Level | Treatment | Use |
|-------|-----------|-----|
| Flat (Level 0) | No shadow, `#010102` bg | Page background |
| Surface (Level 2) | `rgba(255,255,255,0.05)` bg + border | Cards, input fields |
| Elevated (Level 4) | `rgba(0,0,0,0.4) 0px 2px 4px` | Floating elements |
| Dialog (Level 5) | Multi-layer shadow stack | Popovers, modals |

**Shadow Philosophy**: 
On dark surfaces, traditional shadows are nearly invisible. 
Linear uses semi-transparent white borders as primary depth indicator.
```

---

### 3.7 Do's and Don'ts（设计规范）

```markdown
### Do
- Use Inter Variable with `"cv01", "ss03"` on ALL text
- Use weight 510 as your default emphasis weight
- Apply aggressive negative letter-spacing at display sizes

### Don't
- Don't use pure white (`#ffffff`) as primary text
- Don't use solid colored backgrounds for buttons
- Don't apply the brand indigo decoratively
```

---

### 3.8 Responsive Behavior（响应式）

```markdown
### Breakpoints
| Name | Width | Key Changes |
|------|-------|-------------|
| Mobile Small | <600px | Single column |
| Tablet | 640–768px | Two-column grids begin |
| Desktop Small | 768–1024px | Full card grids |

### Touch Targets
- Buttons: 6px radius minimum
- Navigation links: 13–14px with adequate spacing
```

---

### 3.9 Agent Prompt Guide（AI Prompt 指南）

**最重要的一章！包含：**

1. **Quick Color Reference（快速颜色参考）**
```markdown
### Quick Color Reference
- Primary CTA: Brand Indigo (`#5e6ad2`)
- Page Background: Marketing Black (`#08090a`)
- Heading text: Primary White (`#f7f8f8`)
```

2. **Example Component Prompts（组件 Prompt 示例）**
```markdown
"Create a hero section on `#08090a` background. Headline at 48px 
Inter Variable weight 510, line-height 1.00, letter-spacing -1.056px, 
color `#f7f8f8`. Subtitle at 18px weight 400, line-height 1.60, 
color `#8a8f98`. Brand CTA button (`#5e6ad2`, 6px radius)."
```

3. **Iteration Guide（迭代指南）**
```markdown
1. Always set font-feature-settings `"cv01", 'ss03'`
2. Letter-spacing scales with font size
3. Three weights: 400 (read), 510 (emphasize), 590 (announce)
```

---

## 4. ✅ 优点

1. **标准化格式** — 9 大章节固定结构，AI 容易解析
2. **语义化命名** — 颜色/字体有功能描述，非单纯数值
3. **覆盖全面** — 从氛围到组件到响应式，完整闭环
4. **社区共建** — 58+ 平台持续更新
5. **预览工具** — 附带 HTML 预览，直接看效果
6. **AI 原生设计** — 从一开始就是给 AI 看的，不是给设计师看的

---

## 5. ❌ 缺点

1. **维护成本** — 依赖社区同步网站设计更新
2. **覆盖有限** — 目前只有 58 个平台
3. **AI 理解依赖** — 还原度取决于 AI 对 md 的解析能力
4. **无 Figma 集成** — 纯文本格式，不支持设计工具直接导入
5. **更新延迟** — 网站改版后 DESIGN.md 可能滞后

---

## 6. 🎬 使用场景

### 场景 1：AI 编程 Agent 生成 UI
```
1. 复制 DESIGN.md 到项目根目录
2. 告诉 AI："按照 DESIGN.md 构建这个页面"
3. AI 读取规范 → 生成匹配代码
```

### 场景 2：学习大厂设计系统
```
1. 选择目标平台（如 Linear、Vercel）
2. 阅读 DESIGN.md 理解设计决策
3. 参考 preview.html 预览效果
```

### 场景 3：快速启动新项目
```
1. 选择喜欢的 DESIGN.md（如 Notion 风格）
2. 复制到新项目
3. 告诉 AI："参考 DESIGN.md 构建后台界面"
```

---

## 7. 🔧 运行依赖环境

| 依赖 | 说明 |
|------|------|
| AI 编程工具 | Claude Code / Cursor / OpenClaw |
| Markdown 阅读能力 | 原生支持 |
| 可选：预览工具 | 浏览器打开 preview.html |

---

## 8. 🚀 部署使用注意点

### 安装（Clone 仓库）
```bash
git clone --depth 1 https://github.com/VoltAgent/awesome-design-md.git
```

### 使用流程
```markdown
1. 选择平台（如 design-md/vercel/DESIGN.md）
2. 复制 DESIGN.md 到项目根目录
3. 在 OpenClaw/Cursor/Claude Code 中使用：

   "参考这个 DESIGN.md，帮我构建一个 landing page"
```

### 与 OpenClaw 结合
```markdown
OpenClaw 读取 DESIGN.md → 结合 AGENTS.md → 
生成匹配 UI 的代码 → 输出到项目文件
```

---

## 9. 🕳️ 避坑指南

### 坑 1：AI 误解颜色功能
**问题：** AI 可能只读 Hex 值，不理解语义化命名
**解决：** 在 Prompt 中明确指定功能，如"使用 Brand Indigo 作为主 CTA"

### 坑 2：字体加载失败
**问题：** 自定义字体（Geist/Inter Variable）可能需要 CDN
**解决：** 在项目中引入 Google Fonts 或使用系统字体 fallback

### 坑 3：预览 HTML 本地打不开
**问题：** preview.html 可能依赖 CDN 资源
**解决：** 使用本地服务器或在线预览

---

## 10. 📊 总结

| 维度 | 评分 |
|------|------|
| 学习价值 | ⭐⭐⭐⭐⭐（5星） |
| 实用价值 | ⭐⭐⭐⭐（4星） |
| 社区活跃度 | ⭐⭐⭐⭐（4星） |
| 格式完整性 | ⭐⭐⭐⭐⭐（5星） |
| 推荐指数 | ⭐⭐⭐⭐⭐（5星） |

### 一句话总结
> **DESIGN.md = AI 编程时代的"设计交接单"，58+ 平台设计系统开源共享，让 AI 帮你像素级还原任何网站的 UI。**

### 与 AI-Native SOP 结合
```
阶段5（AI逻辑）→ DESIGN.md 定义设计规范
    ↓
阶段6（AI编程）→ AI Agent 读取 DESIGN.md 生成代码
    ↓
验证环节 → 对比 DESIGN.md 检查还原度
```

### 下一步
1. ✅ 已 Clone 仓库到 `E:\workspace\awesome-design-md`
2. ⬜ 测试用 OpenClaw 配合 Linear 的 DESIGN.md 生成 UI
3. ⬜ 探索自动生成 DESIGN.md 的工作流
