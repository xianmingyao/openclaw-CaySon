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

**作用：** 描述性段落 + 关键特征列表，让 AI 理解设计的"感觉"而非只读数值。

---

### 3.2 Color Palette & Roles（颜色系统）

**格式：** 语义化命名 + Hex 值 + 功能说明

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