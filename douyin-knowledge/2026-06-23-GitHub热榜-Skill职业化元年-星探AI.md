# 🔥GitHub本周热榜 - Skill职业化元年

**来源**: https://v.douyin.com/hVTVZQXKUDQ/
**博主**: 星探AI
**宁兄分享时间**: 2026-06-23 08:28（GMT+8）
**对应周期**: 2026年6月中下旬（ISO Week 25, Jun 15-21）

---

## 总结

**2026 是 AI Skills 的"职业化元年"！** 本周 GitHub Trending 几乎被 AI Skills 相关项目霸榜 —— 从官方仓库到社区集合、从代码理解到 Agent 增强、从记忆系统到安全治理，开发者正在用 Skills 文件重塑 AI 编程工作流。涨星总数超 9.3 万，Skills 已从"玩具"进化为"职业化工具"。

---

## 📊 本周 GitHub 热榜三大主题

### 主题1：Skills 生态大爆发 ⭐⭐⭐⭐⭐

| 项目 | Stars | 描述 |
|------|-------|------|
| **anthropics/skills** | **152.8k** | Anthropic 官方 Agent Skills 仓库（PDF/DOCX/XLSX/PPTX） |
| **scienceaix/agentskills** | - | Awesome Agent Skills 精选集合 |
| **claudemarketplaces.com** | - | 浏览 21,600+ Claude Code Skills 的目录 |
| **openaitoolshub.org** | - | 349 Claude Code Skills 跨 12 类别排名 |
| **mingrath/awesome-claude-skills** | - | 精选 Claude Code Skills 列表 |
| **akin-ozer/cc-devops-skills** | - | DevOps Skills for Claude Code / Codex |
| **skillleaderboard.com** | - | 基于 GitHub 实数据的 Skill 排行榜 |
| **discoveraiskills.com** | - | Top 10 Hottest Agent Skills |

### 主题2：Skills 进入安全治理阶段 ⭐⭐⭐⭐

- **NVIDIA SkillSpector** —— 扫描 26% Skills 的安全漏洞
- Skills 从"能跑就行" → 必须经过安全扫描才能上架
- **你的 edgeone-clawscan 正好踩在这个风口上！**

### 主题3：非 AI 工具开始回归 ⭐⭐⭐

- **kage**、**ponytail** 等非 AI 项目在 HN 表现更强
- 暗示：Skills 生态成熟后，市场开始关注"具体业务问题"
- AI 不再是万能解，专业工具重新获得尊重

---

## 🚀 本周最大黑马

### 🏆 Headroom（+14,272 stars/周）
- **类型**：LLM Token 压缩器
- **价值**：解决上下文窗口瓶颈，让长对话/大文档可用
- **关键场景**：长文档分析、跨会话记忆、多 Agent 协作

### 其他热门项目

| 项目 | 定位 | 关键能力 |
|------|------|---------|
| **MoneyPrinterTurbo** | 视频自动生成 | AI 一键生成短视频 |
| **MarkItDown** | 文档转换 | 任意格式 → Markdown |
| **Supermemory** | 跨会话记忆 | 解决上下文断流 |
| **ECC** | Claude Code 增强 | 边缘计算编排 |
| **taste-skill** | 去除 AI 腔调 | 让 AI 输出更"人类" |
| **VoxCPM** | 语音合成 | 下一代 TTS |

---

## 🎯 anthropics/skills 官方仓库深度拆解

### 为什么是 152.8k Stars？

**核心价值**：Anthropic 官方把 Skills 从"实验功能"升级为"Claude 核心能力"。

### Skills 目录结构

```
anthropics/skills/
├── skills/
│   ├── docx/           # Word 文档处理
│   ├── pdf/            # PDF 文档处理
│   ├── pptx/           # PowerPoint 处理
│   ├── xlsx/           # Excel 处理
│   ├── skill-creator/  # Meta Skill：教你写 Skill
│   └── template/       # 起始模板
└── ...
```

### Skills 核心分类（12 类）

| 类别 | 典型场景 |
|------|---------|
| 📄 文档处理 | PDF/Word/Excel/PPT 生成与解析 |
| 💻 软件开发 | 代码理解、PR Review、测试 |
| 🎨 创意设计 | 前端设计、海报、应用原型 |
| 🔌 API 集成 | Claude API / Anthropic SDK |
| 📊 数据分析 | 业务查询、可视化 |
| 🔒 安全治理 | Skill 漏洞扫描、权限校验 |
| 🚀 DevOps | CI/CD、容器、部署 |
| 🤖 Agent 增强 | 多 Agent 编排、记忆系统 |
| 💬 通讯协作 | Slack/邮件/通知 |
| 🛒 商业运营 | 营销、运营、客服 |
| 📚 学习研究 | 论文分析、知识整理 |
| 🧪 实验创新 | 新兴场景、原型验证 |

### Skill 本质：SKILL.md + 资源文件夹

```yaml
---
name: pdf-processing
description: 处理 PDF 文档的提取、编辑、生成
---

# PDF 处理 Skill

## 何时使用
当用户需要处理 PDF 文件时...

## 工具列表
- pdf-extract: 文本提取
- pdf-edit: 内容编辑
- pdf-generate: 文档生成

## 工作流
1. 接收 PDF 文件路径
2. 解析文档结构
3. 按需执行操作
```

> **关键洞察**：Skill = SKILL.md（YAML + Markdown）+ 工具集 + 工作流

---

## 💡 "Skill 职业化元年" 的 5 大信号

### 信号1：官方背书
- Anthropic 把 Skills 列为 Claude 核心能力
- Claude API 文档专门的 Skills 章节
- 官方提供 PDF/Word/Excel/PPT 等"生产级"Skills

### 信号2：生态规模
- Claude Marketplace：**21,600+ Skills**
- 社区精选：**349 Skills** 跨 12 个分类
- 增长速度：每周新增 100+ Skills

### 信号3：商业化起步
- SkillLeaderboard 实数据排名
- Awesome Skills 列表成新流量入口
- Skill 开发已成新职业方向

### 信号4：工具链成熟
- Skill Creator（Meta Skill）：教你怎么写 Skill
- Template：标准化起始模板
- NVIDIA SkillSpector：安全扫描工具

### 信号5：场景渗透
- 文档处理：替代传统 OCR + RPA
- 代码开发：替代传统 IDE 插件
- 业务分析：替代传统 BI 工具

---

## 🔥 与你已有体系的关联

### 你已经在 Skills 赛道！

| 你的项目 | 对标 Skill 类别 |
|---------|----------------|
| **jingmai-product-publish** | 🛒 商业运营 Skill（电商场景） |
| **summarize** | 📚 学习研究 Skill（内容总结） |
| **nano-banana-pro** | 🎨 创意设计 Skill（AI 图片生成） |
| **huguanjin-libtv-skill** | 🎬 视频创作 Skill |
| **memory-dream** | 🤖 Agent 增强 Skill（记忆系统） |
| **edgeone-clawscan** | 🔒 **安全治理 Skill**（🔥 本周风口！） |
| **social-media-publish** | 📢 通讯协作 Skill |

### 你错过的机会 & 抓到的机会

| 机会 | 状态 |
|------|------|
| 🔥 **Skills 安全治理**（NVIDIA SkillSpector） | ✅ **你已经做了 edgeone-clawscan！** |
| 🔥 **跨会话记忆**（Supermemory） | ⚠️ 你有 memory-dream 但定位是 dream 不是 supermemory |
| 🔥 **AI 腔调去除**（taste-skill） | ❌ 缺失 |
| 🔥 **Token 压缩**（headroom） | ❌ 缺失 |
| 🔥 **文档转换**（MarkItDown） | ⚠️ 你的 summarize 接近但不够通用 |

---

## 🎬 实战建议（宁兄向）

### 短期（1-2 周）

1. **edgeone-clawscan 升级为 Skill 形式**
   - 当前：每次手动调用
   - 目标：做成 Claude Code Skill + MCP 双重入口
   - 价值：直接对接 NVIDIA SkillSpector 赛道

2. **给 jingmai-product-publish 加 SKILL.md**
   - 当前：只有 SKILL.md 但还没接入 Claude Code
   - 目标：让 Claude Code 能直接调用
   - 价值：进入 anthropics/skills 候选

3. **复刻 taste-skill 思路**
   - 在你的 doubao-chat / 内容生成场景
   - 加一道"去 AI 腔调"的处理
   - 价值：跨境电商本地化文案更自然

### 中期（1 个月）

4. **Token 压缩器 headroom 思路整合**
   - 长文档分析场景（百万字上下文）
   - 京麦商品库 + 跨境电商 listing
   - 价值：节省 50-70% token 成本

5. **Supermemory 思路整合到 MAGMA**
   - 你已有四维记忆（语义/时间/因果/实体）
   - 加一层"跨会话持久化"接口
   - 价值：Agent 真正"记住"宁兄

### 长期（3 个月）

6. **打造 ELUCKY Skills Store**
   - 跨境电商专属 Skills 商店
   - TikTok / Facebook / Instagram 自动化 Skills
   - 价值：下一个百万星项目机会

---

## 🕳️ 避坑提醒

### 🔴 坑1：Skill 不等于 Function Calling
- Skill 是更高层的封装：包含 **YAML 元数据 + 工具集 + 工作流**
- 不要把 MCP 工具直接当 Skill 用

### 🔴 坑2：Skill 必须经过安全扫描
- NVIDIA SkillSpector 发现 26% Skills 有漏洞
- 你的 Skill 发布前必须经过 edgeone-clawscan
- 这就是你的护城河

### 🔴 坑3：不要重复造轮子
- 文档处理（PDF/Word/Excel）官方已有
- 你应该做的是 **垂直场景 Skills**（京麦/ELUCKY）

---

## 📊 总结

### 学习价值
⭐⭐⭐⭐⭐（5星） —— 给你指明了 Skills 赛道，且你的 edgeone-clawscan 正中靶心

### 推荐指数
⭐⭐⭐⭐⭐（5星） —— 立即把 Skills 战略纳入 ELUCKY/Jingmai 路线图

### 一句话总结
**"Skills 不是新功能，是新职业。Anthropic 重新定义了 AI 能力的边界。"**

---

## 📂 关联归档

| 文件 | 关联点 |
|------|-------|
| `2026-04-02-summarize-skill.md` | 你的首个 Skill 类工具 |
| `2026-04-02-nano-banana-pro.md` | AI 图片生成 Skill |
| `2026-05-08-Skills-MCP-Server.md` | Skills MCP Server 集成 |
| `2026-05-09-mattpocock-skills.md` | 工程实践 Skills 本地化 |
| `2026-06-16-Harness工程-自说自话的江哥.md` | Harness Engineering 基础 |
| `2026-06-23-AI新范式-循环工程Loop-Engineering与Harness.md` | Loop Engineering 新范式 |

---

## 🏷️ 标签

#GitHub热榜 #Skill职业化 #Anthropic #ClaudeCode #AgentSkills #Skills生态 #edgeone-clawscan #Skills安全 #Skills MCP #ELUCKY #京麦 #跨境电商自动化

---

## 📚 参考来源

- 视频原文：https://v.douyin.com/hVTVZQXKUDQ/
- 官方 Skills 仓库：https://github.com/anthropics/skills
- Awesome Agent Skills：https://github.com/scienceaix/agentskills
- Claude Marketplaces：https://claudemarketplaces.com/skills
- SkillLeaderboard：https://www.skillleaderboard.com/
- Tommy Z 周报：https://www.tommyz.blog/blog/github-trending-weekly-2026-06-02-to-2026-06-06
- Shareuhack 周报：https://www.shareuhack.com/en/posts/github-trending-weekly-2026-06-17
- Trendshift Week 25：https://trendshift.io/weekly/2026/25
- Anthropic Skills 完整指南：https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf
- 知乎 2026 第23周盘点：https://zhuanlan.zhihu.com/p/2047355813451273354
