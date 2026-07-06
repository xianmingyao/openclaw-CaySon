# GitHub AI Skills 榜单深挖报告
日期: 2026-05-19 | 来源: 抖音 + GitHub官方数据

---

## 一、GitHub AI Skills 榜单 Top 项目深挖

### 1. mattpocock/skills ⭐ 91.8k
**链接**: https://github.com/mattpocock/skills
**定位**: Skills for Real Engineers. Straight from my .claude directory.
**特点**: Matt Pocock 的 .claude 目录原味输出，实用工程师技能集合

---

### 2. hermes-agent ⭐ 152k（最大黑马）
**链接**: https://github.com/NousResearch/Hermes-Agent
**定位**: The agent that grows with you（与用户一同成长的智能体）
**公司**: Nous Research
**协议**: MIT

**核心功能**:
- 内置学习循环：自动从经验创建技能、使用时自我改进、主动记住知识
- 搜索历史对话：通过 FTS5 会话搜索 + LLM 摘要实现跨会话记忆
- 用户建模：集成 Honcho 方言用户建模
- 技能标准：兼容 agentskills.io 开放标准
- 多端入口：Telegram / Discord / Slack / WhatsApp / Signal / Email / CLI
- 模型路由：支持 Nous Portal / OpenRouter(200+模型) / OpenAI / Anthropic / HuggingFace 等
- 7种终端后端：Local / Docker / SSH / Singularity / Modal / Daytona / Vercal Sandbox
- 定时自动化：自然语言描述的 cron 调度任务
- **支持 OpenClaw 迁移**: `hermes claw migrate` 一键导入 SOUL.md / 记忆 / 技能 / API Keys

**安装**:
```bash
# Linux/macOS/WSL2/Termux
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Windows (早期测试版)
irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1 | iex
```

---

### 3. agentmemory ⭐ 12.8k
**链接**: https://github.com/rohitg00/agentmemory
**定位**: #1 Persistent memory for AI coding agents based on real-world benchmarks
**协议**: Apache-2.0

**核心数据**:
- 检索准确率: R@5 = 95.2%
- Token 节省: 92%
- MCP 工具: 53个
- 自动钩子: 12个
- 外部依赖: 0（无外部数据库）
- 测试: 950+ 测试通过

**支持智能体**:
Claude Code / Codex CLI / OpenClaw / Hermes / pi / OpenHuman / Cursor / Gemini CLI / OpenCode / Cline / Goose / Kilo Code / Aider / Claude Desktop / Windsurf / Roo Code

**安装**:
```bash
npm install -g @agentmemory/agentmemory
agentmemory                    # 启动内存服务器 :3111
agentmemory demo               # 种子示例 + 验证检索
agentmemory connect claude-code  # 连接智能体
```

**REST API** (124个端点):
- `/agentmemory/session/start` - 启动会话
- `/agentmemory/smart-search` - 混合搜索
- `/agentmemory/remember` - 长期记忆
- `/agentmemory/enrich` - 文件上下文 + 记忆 + Bug检索
- `/agentmemory/graph/query` - 知识图谱查询
- `/agentmemory/team/share` - 团队共享

---

### 4. academic-research-skills ⭐ (学术研究技能)
**链接**: https://github.com/Imbad0202/academic-research-skills
**定位**: 学术研究全流程技能套件（从研究到发表）
**版本**: v3.9.4.1 | 协议: CC BY-NC 4.0

**核心模块**:
1. **Deep Research** (13-agent团队) - 7种模式
   - full / quick / systematic-review(PRISMA) / socratic / fact-check / lit-review / review

2. **Academic Paper** (12-agent写Pipeline) - 10种模式
   - full / plan / outline-only / revision / revision-coach / abstract-only / lit-review / format-convert / citation-check / disclosure

3. **Academic Paper Reviewer** (7-agent评审) - 6种模式
   - EIC + 3动态评审 + Devil's Advocate，0-100质量量表

4. **Academic Pipeline** (10阶段编排器)
   - Stage 2.5/4.5 诚信门控：捕获虚假引用 + 统计错误
   - 可选交叉模型完整性验证

**反幻觉机制**:
- Zhao et al. (2026) 审计 111M 引用发现 146,932 个虚假引用
- ARS v3.7+v3.8 新增 L3 风险信号 + 五级 HIGH-WARN 分类
- 声称-支撑审计 (`ARS_CLAIM_AUDIT=1`)

**安装**:
```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

---

### 5. OpenHuman ⭐ (本周新晋顶流)
**链接**: https://github.com/tinyhumansai/openhuman
**定位**: Your Personal AI super intelligence. Private, Simple and extremely powerful.
**协议**: GNU | 官网: https://tinyhumans.ai/openhuman

**核心差异（vs其他Agent）**:
| 特性 | Claude Cowork | OpenClaw | Hermes Agent | OpenHuman |
|------|-------------|----------|-------------|-----------|
| 开源 | 🚫 专有 | ✅ MIT | ✅ MIT | ✅ GNU |
| 易用性 | ✅ 桌面+CLI | ⚠️ 终端优先 | ⚠️ 终端优先 | ✅ UI，分钟级 |
| 成本 | ⚠️ 订阅+附加 | ⚠️ 自带模型 | ⚠️ 自带模型 | ✅ 单一订阅+TokenJuice |
| 记忆 | ✅ 聊天范围 | ⚠️ 插件依赖 | ✅ 自我学习 | 🚀 记忆树+Obsidian保险库 |
| 集成 | ⚠️ 少量 | ⚠️ 自带 | ⚠️ 自带 | 🚀 118+ OAuth一键连 |
| 自动抓取 | 🚫 无 | 🚫 无 | 🚫 无 | ✅ 20分钟同步到记忆 |
| 模型路由 | 🚫 单模型 | ⚠️ 手动 | ⚠️ 手动 | ✅ 内置 |

**三大创新机制**:
1. **TokenJuice** - 智能Token压缩，减少80% token消耗，记住高达10亿Token信息
2. **潜意识循环** - Agent自主决定待办事项，化身虚拟形象加入Google Meet
3. **Auto-fetch** - 20分钟无感抓取OAuth连接数据，生成记忆树

**安装**:
```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.sh | bash

# Windows
irm https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.ps1 | iex
```

---

## 二、三大顶流Agent选型指南

| Agent | 绰号 | 适合场景 | 核心优势 |
|-------|------|---------|---------|
| **OpenClaw** | 龙虾 | 跨平台执行网关 | MCP生态，桌面自动化，Chrome/应用控制 |
| **HermesAgent** | 爱马仕 | 自我成长型员工 | 内置学习循环，技能自我改进，Nous生态系统 |
| **OpenHuman** | 🏆 顶流 | 贴身个人助理 | 118+集成，Auto-fetch记忆树，TokenJuice，省心 |

**结语**: Agent发展方向 = **执行力**（工具调用）+ **学习力**（自我改进）+ **记忆力**（持久上下文）

---

## 三、技术关联图谱

```
OpenHuman
  ├── Memory Tree（记忆树）
  ├── TokenJuice（压缩）
  ├── 118+ OAuth集成
  └── 可选agentmemory后端 ←→ agentmemory
                              ├── Claude Code
                              ├── Hermes Agent
                              ├── OpenClaw
                              └── OpenHuman

Hermes Agent
  ├── 自我学习循环
  ├── Skills系统（兼容agentskills.io）
  ├── OpenClaw迁移工具
  └── Honcho用户建模

mattpocock/skills
  └── 工程师技能实践标准
```

---

## 四、学习价值

- **工程价值**: ⭐⭐⭐⭐⭐（5星）
- **研究价值**: ⭐⭐⭐⭐⭐（5星）
- **投资价值**: ⭐⭐⭐⭐（4星）- OpenHuman + Hermes 生态值得关注
- **学习路径**: mattpocock/skills → agentmemory → hermes-agent → OpenHuman
