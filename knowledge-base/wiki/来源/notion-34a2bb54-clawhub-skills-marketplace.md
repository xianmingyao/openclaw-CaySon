# ClawHub - OpenClaw Skills 市场研究报告

> 来源：v.vn886.com/chat/#/toolsHome（OpenClaw Skills商店界面截图）

> 研究日期：2026-04-06

---

## 1. 🎯 这是什么

**ClawHub** 是 OpenClaw 官方 Skills 市场/技能商店，为 OpenClaw AI 助手提供扩展能力。

| 项目 | 信息 |

|------|------|

| 官网 | clawhub.ai |

| 定位 | AI Agent 的 npm |

| 规模 | **3,286+ skills**，11个分类 |

| 特点 | 向量搜索 + 版本控制 + 社区评分 |

| CLI | `openclaw skills` 系列命令 |

---

## 2. 📝 关键功能点

### 2.1 Skills 分类（11大类）

从截图看到的分类：

| 分类 | 说明 |

|------|------|

| **通讯类** | Telegram、Discord、Slack、WhatsApp、钉钉、企业微信、微信公众号 |

| **日历/任务** | Google Calendar、Todoist、Notion、Jira、Linear |

| **代码类** | GitHub、GitLab |

| **邮件类** | Gmail、SendGrid、RESEND、SMTP2GO |

| **支付类** | 微信支付、支付宝、Stripe、PayPal |

| **数据库** | PostgreSQL、MySQL、Redis、MongoDB、Milvus、Qdrant、Pinecone |

| **云服务** | Vercel、Netlify、Cloudflare、Supabase、Firebase |

| **搜索** | Meilisearch |

### 2.2 已安装Skills（从截图可见）

| Skill | 状态 |

|-------|------|

| agent-browser | ✅ 已安装 |

| Summarize | ✅ 已安装 |

| Nano Banana Pro | ✅ 已安装 |

| Weather | 未安装 |

| Feishu (Lark) | 未安装 |

| Todoist | 未安装 |

| Google Calendar | 未安装 |

| Notion | 未安装 |

| GitHub | 未安装 |

---

## 3. ⚡ 怎么使用

### 3.1 CLI 命令

# 搜索skills

openclaw skills search <关键词>

# 安装skills

openclaw skills install <skill-name>

# 更新skills

openclaw skills update <skill-name>

# 列出已安装

openclaw skills list

# 查看详情

openclaw skills info <skill-name>

### 3.2 SkillHub CLI（第三方）

# 搜索技能

python ~/.skillhub/skills_store_cli.py search <关键词>

# 安装技能

python ~/.skillhub/skills_store_cli.py install <技能名>

# 更新技能

python ~/.skillhub/skills_store_cli.py update <技能名>

---

## 4. ✅ 优点

1. **生态完整** - 3,286+ skills，覆盖主流服务

2. **向量搜索** - 语义化检索，快速找到所需技能

3. **版本控制** - 每个Skill有版本号，可降级

4. **社区评分** - 可参考其他用户评价

5. **一键安装** - `openclaw skills install` 自动安装到workspace

---

## 5. ❌ 缺点

1. **质量参差** - 3,286+ skills中质量良莠不齐

2. **安全风险** - 第三方Skills可能存在安全威胁（需安全扫描）

3. **文档缺失** - 部分Skills文档不完整

4. **依赖地狱** - 某些Skills依赖复杂

---

## 6. 🎬 使用场景

| 场景 | 推荐Skill |

|------|----------|

| 办公协作 | Feishu、Slack、Discord |

| 日程管理 | Google Calendar、Todoist、Notion |

| 代码管理 | GitHub、GitLab |

| 邮件处理 | Gmail、RESEND |

| 数据库 | PostgreSQL、MongoDB、Milvus |

| 云服务 | Vercel、Netlify、Supabase |

---

## 7. 🔧 运行依赖环境

| 项目 | 要求 |

|------|------|

| OpenClaw版本 | 需最新版本 |

| Node.js | 部分Skills需要 |

| Python | 部分Skills需要 |

| 对应服务账号 | 如GitHub API Token等 |

---

## 8. 🚀 部署使用注意点

### 8.1 安全安装流程（铁律）

**每次安装前必须：**

# 1. 安全扫描

openclaw skills scan <技能名>

# 2. 风险评估

# 🔴 HIGH/EXTREME → 拒绝安装

# 🟡 MEDIUM → 告知用户确认

# 🟢 LOW → 可安装