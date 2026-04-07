# MEMORY.md - 长期记忆

## 用户信息
- **称呼**：宁采臣 / 宁兄
- **身份**：CTO，24年技术老炮
- **时区**：Asia/Shanghai

## 核心规范
- 代码必须落地到文件，不能只存在对话中
- 铁律1：实事求是，数据说话
- 铁律2：代码质量 > 代码速度 > 代码炫技

## 记忆检索铁律（重要！）
1. 首选 → 云端 Milvus (8.137.122.11:19530)
2. 备选 → 本地 ChromaDB (Milvus 故障时降级)

## 日报格式逻辑

### 标准格式
```
YYYY.MM.DD(日报)
1、事项 + 完成进度%（括号内补充当日情况）
2、事项 + 状态（括号内补充当日情况）
...
```

### 格式要素
- **日期标题**：`YYYY.MM.DD(日报)`
- **序号**：用中文序号（1、2、3...）
- **事项**：简短描述工作内容
- **进度/状态**：方括号[65]表示百分比，或文字状态
- **括号补充**：说明当日具体情况

### 补充说明类型
- 完成进度：完成进度[65]%
- Git情况：今日无Git提交记录
- 异常情况：今日无异常反馈
- 申请状态：今日重新提交申请接口
- 持续运行：持续运行中

### 涉及人员
- 小刘、小龙虾、京采、小蒙

### 涉及项目
- 京麦智能体、知识库、OpenClaw系统

## 项目记忆
- 京麦智能体：搭建中，进度65%
- OpenClaw：多渠道AI助手，持续运行

## 2026-04-03 技术研究成果（新增）

### 剪映AI剪辑Skill - jianying-editor-skill

**来源：** 抖音@艾伦2077v 视频「完全不会剪辑也没关系！这个AI Skill帮你全自动出视频！」

| 项目 | 信息 |
|------|------|
| GitHub | `luoluoluo22/jianying-editor-skill` |
| 一键安装 | `irm is.gd/rpb65M \| iex` |
| 依赖 | Python + 剪映专业版(≤5.9) + playwright |
| 核心功能 | 自然语言控制剪映完成文案→配音→字幕→配乐→特效→导出 |
| 文档 | `knowledge/jianying-editor-skill.md` |

**关键发现：**
- 录屏自动加红圈标记鼠标点击位置，教程视频神器
- 影视解说功能：AI分析视频自动生成分镜脚本
- 网页动效转视频：HTML/Canvas动画直接变素材
- ⚠️ 自动导出依赖剪映5.9或更低版本

### Remotion Video Toolkit - React视频生成Skill

**来源：** 抖音@艾伦2077v 视频「Remotion的Skill」

| 项目 | 信息 |
|------|------|
| GitHub | `Arxchibobo/openclaw-remotion-video-toolkit` |
| 安装命令 | `openclaw skill install github:Arxchibobo/openclaw-remotion-video-toolkit` |
| 核心依赖 | Node.js 18+ / React 18+ / FFmpeg |
| 规则数 | 29条规则，覆盖动画/字幕/3D/图表全场景 |
| 文档 | `knowledge/remotion-video-toolkit.md` |

**核心价值：**
- 用React代码生成MP4视频（代码即视频）
- 批量个性化：一套模板，千人千面（Spotify Wrapped模式）
- TikTok字幕：音频转逐字高亮字幕
- 数据可视化：JSON → 视频自动化

**对比jianying-editor-skill：**
- jianying-editor-skill → 口播/Vlog/影视解说
- remotion-video-toolkit → 数据视频/批量个性化/程序化视频
- 两者组合 → 全面覆盖视频创作场景

### CLI vs MCP 专题研究报告

**来源：** 抖音@技术爬爬虾 - 「为什么巨头都在做CLI？比起MCP有哪些优势？」

| 项目 | Stars | 说明 |
|------|-------|------|
| CLI-Anything | 1.4k+ | 港大开源，自动为软件生成CLI接口 |
| OpenCLI | 9.6k | 任意网站/工具→CLI，Apache-2.0 |
| 巨头CLI | - | Claude Code/Codex CLI/钉钉/飞书/网易云 |

**核心结论：**
- CLI是AI Agent的通用交互语言（稳定 > GUI自动化）
- MCP需要官方支持，CLI可绕过官方自动生成
- CLI-Anything：7阶段自动生成CLI，支持GIMP/Blender等
- browser-use vs CLI-Anything：浏览器用前者，专业软件用后者

**文档：** `knowledge/cli-vs-mcp-research.md`

### Skill学习追踪表更新

| 技能 | 状态 | 安装日期 | 掌握程度 | 待解决问题 |
|------|------|---------|---------|-----------|
| summarize | ✅ 已安装 | 2026-04-02 | 精通 | - |
| nano-banana-pro | ✅ 已安装 | 2026-04-02 | 精通 | - |
| jianying-editor-skill | 🔍 研究完成 | 待安装 | ⭐待实践 | 需先装剪映5.9 |
| remotion-video-toolkit | 🔍 研究完成 | 待安装 | ⭐待实践 | 需Node.js 18+ |
| CLI-Anything | 🔍 研究完成 | 待实践 | ⭐待测试 | 需Python 3.10+ |
| OpenCLI | 🔍 研究完成 | 待实践 | ⭐待测试 | 需npm/Node.js |

### 2026-04-02 技术研究成果

### 浏览器自动化工具集（来源：抖音@大力AI）

| 工具 | 状态 | 说明 |
|------|------|------|
| browser-use CLI | ✅ 已安装 0.12.5 | YC孵化，Token高效，AI Agent专用 |
| agent-browser | ✅ 已装 | OpenClaw技能，Windows友好 |
| WebMCP | 🔍 研究完 | Chrome官方2026-02-10发布，趋势 |

### 关键文档
- `knowledge/browser-use-cli.md` - browser-use CLI 2.0 完整技术报告
- `knowledge/webmcp-mcp-browser-automation.md` - WebMCP + MCP深度报告

### 重要结论
1. **browser-use --mcp** 是官方MCP方案，mcp-browser-use第三方包暂不兼容
2. **Windows必须**设置 `$env:PYTHONIOENCODING="utf-8"` 避免emoji错误
3. **agent-browser + browser-use CLI** 互补，建议同时使用
4. **WebMCP** 是未来趋势（2026年中正式版），值得关注

### GitHub Claude Code相关仓库

| 仓库 | Stars | 定位 | 推荐度 |
|------|-------|------|--------|
| instructkr/claw-code | 48,000+ | Clean-room重写，合法安全 | ⭐⭐⭐⭐⭐ |
| sanbuphy/claude-code-source-code | Fork 41,500 | 泄露源码，法律风险高 | ⭐（仅研究） |
| unohee/OpenSwarm | 232 | 多Agent编排器 | ⭐⭐ |

### GStack 角色映射表

**核心理念：** AI Agent模拟软件团队全生命周期

9大角色：CEO规划 / 工程经理架构 / Staff工程师找bug / QA测试 / 安全护栏 等

### KiloClaw 全托管OpenClaw

**一句话：** OpenClaw全托管云服务，60秒一键部署

**核心特点：**
- ⚡ 60秒部署（vs自托管30-60分钟）
- 🔒 零运维（自动安全/更新/监控）
- 🌐 50+平台接入
- 🤖 500+模型（Kilo Gateway）
- 🏢 企业版解决"影子AI"安全问题

## AI-NATIVE 开发工作流 SOP（宁兄标准流程）

**来源：** 宁兄白板手绘流程图（2026-04-02）
**定位：** 宁兄所有项目的**标准作业流程（SOP）**

### 7阶段标准流程

```
阶段1：知识获取 → Google/GitHub/知网 → CodeWiki
阶段2：想法原型 → 产品方向 → Idea确定
阶段3：UI设计 → shadcn/ui → Midjourney/Stitch → Figma精修
阶段4：知识库 → Puppeteer/NotebookLM/Obsidian → Gemini理解
阶段5：AI逻辑 → Google AI Studio → Skills定义
阶段6：AI编程 → Cursor/Trae → Skills/MCP/rvl
阶段7：部署上线 → GitHub + Vercel → 产品上线
```

### CaySon职责（纠正流程错误）

**宁兄项目开发时，CaySon 必须监督执行：**
- ❌ 跳过调研直接开发 → 🔴 立即暂停，要求补全
- ❌ 没有设计稿直接写代码 → 🔴 立即暂停，要求先出Figma
- ❌ 不用AI IDE → 🟡 建议使用Cursor/Trae
- ❌ 没有知识库 → 🟡 建议建立NotebookLM/Obsidian
- ❌ 上线前没走GitHub → 🔴 立即暂停，必须走流程

### 检查清单
每个项目必须确认7个阶段都有产出物，缺一不可。

### 规范文档
- `knowledge/ai-native-workflow-SOP.md` - 完整SOP文档
- `knowledge/ai-native-workflow-mermaid.md` - Mermaid流程图代码

## SkillHub 技能管理规范（2026-04-02 新增）

### SkillHub CLI 用法
```bash
python ~/.skillhub/skills_store_cli.py search <关键词>
python ~/.skillhub/skills_store_cli.py install <技能名>
python ~/.skillhub/skills_store_cli.py update <技能名>
```

### 技能安装安全流程（铁律）
1. 安装前：edgeone-clawscan 安全扫描
2. 风险 HIGH/EXTREME → 拒绝安装
3. 风险 MEDIUM → 告知用户确认
4. 安装后验证

### 每日安全扫描 Cron
- **任务ID：** 5227d14e-ae2f-4a41-93c7-3f14b58b9cfc
- **时间：** 每天凌晨 12:30
- **内容：** edgeone-clawscan 全技能安全体检 + 版本更新检查
- **升级后：** 主动告知宁兄

### 已安装技能
| 技能 | 版本 | 日期 | 用途 |
|------|------|------|------|
| summarize | 1.0.0 | 2026-04-02 | 总结网页/PDF/YouTube |
| nano-banana-pro | 1.0.1 | 2026-04-02 | AI图片生成（Gemini 3 Pro） |

## 2026-04-02 今日完成总结

### 技术研究
- ✅ browser-use CLI 2.0 深度测试
- ✅ WebMCP + MCP 浏览器自动化研究
- ✅ GitHub 三大仓库对比分析（claw-code/OpenSwarm/sanbuphy）
- ✅ GStack 角色映射表整理
- ✅ KiloClaw 全托管 OpenClaw 研究
- ✅ AI-Native 开发工作流 SOP 制定

### 系统配置
- ✅ SkillHub CLI 安装完成
- ✅ summarize 技能安装
- ✅ nano-banana-pro 技能安装
- ✅ 每日安全扫描 Cron 设置（12:30）
- ✅ 行为准则更新（TOOLS.md）

### 知识库文档
- `knowledge/browser-use-cli.md` - browser-use CLI 2.0 技术报告
- `knowledge/webmcp-mcp-browser-automation.md` - WebMCP + MCP 深度报告
- `knowledge/github-repos-comparison.md` - GitHub仓库对比分析
- `knowledge/kiloclaw.md` - KiloClaw 深度报告
- `knowledge/ai-native-workflow-SOP.md` - AI-NATIVE 开发工作流 SOP

### Git 提交记录
- docs: add browser-use CLI 2.0 深度研究报告
- docs: add WebMCP + MCP浏览器自动化深度研究报告
- docs: add GitHub repos comparison
- docs: add KiloClaw research report
- docs: add AI-NATIVE workflow SOP as standard process
- docs: add SkillHub safety protocol and daily security scan cron

## 2026-04-06 今日完成总结

### Skills管理
- ✅ 提交9个新skills到git仓库
- ✅ Push到远程仓库（106 files, 24852 insertions）
- 新增：auto-publisher, cloudbase, content-hunter, phoenixclaw-ledger, skill-9, video-summary, wechat-article-scraper, wechat-mp-cn, wechat

## 2026-04-03 今日完成总结

### 技术研究
- ✅ 抖音@艾伦2077v 视频扒取分析（剪映Skill + Remotion Skill）
- ✅ jianying-editor-skill 深度研究（剪映AI剪辑Skill）
- ✅ remotion-video-toolkit 深度研究（React视频生成Skill）
- ✅ 整理两份完整技术报告

### 知识库文档
- `knowledge/jianying-editor-skill.md` - 剪映AI剪辑Skill完整技术报告
- `knowledge/remotion-video-toolkit.md` - React视频生成Skill完整技术报告

### 重要结论
1. **jianying-editor-skill** - 剪映自动化，自然语言驱动，适合口播/Vlog/影视解说
2. **remotion-video-toolkit** - React代码生成视频，适合数据视频/批量个性化
3. 两者组合可全面覆盖视频创作场景
4. 下一步：先下载剪映5.9，再运行一键安装脚本

### 待办事项
- [ ] 下载剪映5.9（夸克网盘：pan.quark.cn/s/81566e9c6e08）
- [ ] 运行Windows一键安装：`irm is.gd/rpb65M | iex`
- [ ] 实践剪映Skill自动化剪辑
- [ ] 安装remotion-video-toolkit（需Node.js 18+）

## 2026-04-07 今日完成总结

### 技术研究
- ✅ Claude Code中文生态深度研究（Ollama零成本、魔搭GLM-4.7）
- ✅ Shopify AI Agent跨境电商自动化2026（Agentic Storefronts）
- ✅ OpenClaw 4.5 梦境记忆系统深度研究（遗忘曲线机制）

### 系统维护
- ✅ 内容捕手汇报cron修复（多渠道投递channel问题）
- ✅ memory-dream Skill安装（@1.0.3）
- ✅ dream-nightly Cron设置（每天凌晨3:00）

### 新增知识库文档
- `knowledge/claude-code-chinese-ecosystem.md` - Claude Code中文生态完整报告
- `knowledge/shopify-ai-agent-ecommerce-2026.md` - Shopify AI Agent 2026报告
- `knowledge/openclaw-45-dreaming-memory.md` - OpenClaw 4.5梦境记忆系统报告

### 已安装Skills
| 技能 | 版本 | 日期 | 用途 |
|------|------|------|------|
| summarize | 1.0.0 | 2026-04-02 | 总结网页/PDF/YouTube |
| nano-banana-pro | 1.0.1 | 2026-04-02 | AI图片生成（Gemini 3 Pro） |
| memory-dream | 1.0.3 | 2026-04-07 | 记忆整合（睡眠记忆） |

### Cron任务状态
| 任务 | ID | 时间 | 状态 |
|------|-----|------|------|
| dream-nightly | 421b1f35 | 每天03:00 | ✅ 新建 |
| daily-git-commit | 1690b963 | 每天22:30 | ✅ ok |
| 内容捕手-汇报 | f27317c4 | 每天18:00 | ✅ 已修复 |
| daily-skill-security-scan | 5227d14e | 每天00:30 | ✅ ok |
| morning-wechat-login-check | e1f7f495 | 每天09:00 | ✅ ok |

### 待办事项
- [ ] 深入研究：Claude Code + Ollama 实战配置
- [ ] 深入研究：智梭ERP具体自动化流程
- [ ] Manus通用Agent情报（宁兄提到但未深入）
- [ ] 测试memory-dream实际效果

## 梦境记忆系统（Dream Memory System）

### 核心机制
- **Wake Phase**：日常工作记录到 memory/YYYY-MM-DD.md
- **Dream Phase**：定期整合到 MEMORY.md（模拟人类睡眠记忆整合）

### 相关Skill
- `memory-dream`（wavmson）：定期合并memory/*.md到MEMORY.md
- `openclaw-memory-dreaming`（ptburkis）：无向量DB的dream-cycle框架
- `engram`：完整记忆层，32 MCP tools

### 生物学灵感
- 艾宾浩斯遗忘曲线：决定什么该忘、什么该留
- Active Dreaming Memory (ADM)：双存储架构

### 文档
- `knowledge/openclaw-45-dreaming-memory.md`
