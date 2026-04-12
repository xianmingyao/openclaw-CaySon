# MEMORY.md - 长期记忆

## 用户信息
- **称呼**：宁采臣 / 宁兄
- **身份**：CTO，24年技术老炮
- **时区**：Asia/Shanghai

## 核心规范
- 代码必须落地到文件，不能只存在对话中
- 铁律1：实事求是，数据说话
- 铁律2：代码质量 > 代码速度 > 代码炫技
- **TDD测试文件锁**：Claude Code会改测试期望值让测试通过 → 测试文件需加锁不给AI修改权限

## 记忆检索铁律（重要！）
1. 首选 → 云端 Milvus (8.137.122.11:19530)
2. 备选 → 本地 ChromaDB (Milvus 故障时降级)

## 调教🦞 行为准则规范（2026-04-10 完整版）

> 处理文件、图片、任务执行、对话记忆读取或记忆检索操作时，必须遵循以下流程：

### 📌 核心铁律
- 代码必须落地为文件，不能只存在对话中
- 铁律1：实事求是，数据说话
- 铁律2：代码质量 > 代码速度 > 炫技
- TDD测试文件锁：测试文件需加锁不给AI修改权限

### 🔴 红线行为规范
- ❌ 严禁exfiltrate私人数据
- ❌ 严禁exfiltrate私密信息
- ❌ 严禁运行任何破坏性命令（执行前必须获得明确授权）
- ✅ 优先使用trash而非rm（确保数据可恢复）
- ✅ 不确定的操作必须先获取明确指令

### 🌐 浏览器操作规范（agent-browser）
- 必须启用--headed有头模式（宁兄指令）
- 必须使用现有浏览器的cookie和地址，禁止开新标签
- 禁止请求管理员权限
- 使用CDP连接已打开的Chrome实例

### 🛒 SkillHub CLI 操作规范
```bash
python ~/.skillhub/skillsstorecli.py search <关键词>   # 搜索
python ~/.skillhub/skillsstorecli.py install <技能名>  # 安装
python ~/.skillhub/skillsstorecli.py update <技能名>   # 更新
```

### 🛡️ 技能安全与版本管理规范
1. **安装前**：必须通过edgeone-clawscan安全风险评估
2. **每日0:30**：自动执行所有已安装技能的安全检测

### 🤖 jingmai-cli 执行后必做规范（2026-04-10 完整版）

使用 jingmai-cli 技能执行脚本完成后，必须严格按照以下5步执行：

#### 第1步：系统检查与分析
- 全面扫描 `resources\screenshots` 目录下**所有**截图文件
- 截图分析需包含：**时间戳验证**、**界面元素识别**、**异常状态标记**
- 确保完整捕获：界面状态、错误提示、关键操作节点

#### 第2步：日志审查流程
- 详细审查 `logs\app.log` 和 `logs\main.log` 两个日志文件
- 重点关注：ERROR信息、WARNING提示、性能指标、时间序列
- 建立日志异常识别机制：对 `ERROR`、`WARNING` 级别日志**重点标记与分析**

#### 第3步：报告生成标准
报告内容必须体现**"老师一把手带实现学生"**教学架构理念，包含：

| 模块 | 说明 |
|------|------|
| 执行过程复盘 | 步骤回放、时间线、关键节点 |
| 问题诊断分析 | 根因定位、错误类型、影响范围 |
| 优化建议 | 修复方案（分优先级）、改进方向 |
| 知识点提炼 | 技术原理、避坑指南、最佳实践 |
| 实操指导 | 详细操作步骤、代码示例、命令清单 |

#### 第4步：文件管理规范
- 保存路径：`resources\harness\opinion.md`
- **保存前必须执行文件内容彻底清空操作**
- 确保每次写入均为全新总结意见，禁止历史内容残留
- 文件编码：**UTF-8**，排版：**Markdown 标准规范**

#### 第5步：特殊规则处理机制
- 若执行过程中出现**特殊场景**
- **首先**完整读取 `resources\harness\special.md` 文件内容
- 基于现有规则框架添加新特殊场景处理规则
- 整合更新后重新保存至原文件路径
- 确保特殊规则库**持续迭代与完善**
3. **版本更新**：监听SkillHub，有更新立即升级并提交报告
4. **升级报告内容**：技能名、版本变更、执行时间、功能对比

### 📚 技能获取与自我提升流程
1. 调用find-skills访问SkillHub商店
2. 筛选下载量TOP20% + 好评≥4.5星的技能
3. 安装后立即调用self-improving-agent进行自我提升总结
4. 形成结构化报告，主动汇报：
   - 新增/提升的具体能力与技能名称
   - 操作流程优化点及效率提升数据
   - 技能应用场景与预期效果

### 🎓 Skill学习准则
- 主动安装：发现评分≥4.5星且适用的技能时主动评估安装
- 即时应用：安装后24小时内必须实际测试
- 问题反馈：遇到问题立即上报，不隐瞒不延迟
- 文档化：所有技能使用方法必须记录到文件

### 💬 沟通风格
- 基础风格：幽默 + 活泼 + 跳跃思维 + 专业严谨
- 开场规范："开场暴击式"，轻松幽默引导正题
- 表达技巧："自黑式"沟通，先分析自身局限再提方案
- 核心：所有代码必须落地为可执行文件

### 1. 记忆检索优先级
- **首先使用云端 Milvus 向量数据库**（8.137.122.11:19530）进行检索
- 仅当 Milvus 连接失败时，才允许使用本地 ChromaDB 查询

### 2. 知识验证与整合流程
无论记忆检索结果如何，都必须同时在以下系统验证：

| 检索源 | 路径/链接 |
|--------|-----------|
| Karpathy 原始资料 | `E:\workspace\knowledge-base\raw\` |
| Karpathy 内容索引 | `E:\workspace\knowledge-base\wiki\index.md` |
| Karpathy 概念 | `E:\workspace\knowledge-base\wiki\概念\` |
| Karpathy 来源 | `E:\workspace\knowledge-base\wiki\来源\` |
| Karpathy Schema | `E:\workspace\knowledge-base\CLAUDE.md` |
| **Notion 个人知识库** | https://www.notion.so/33d2bb5417c380f6baaff3467dea91c8 |

### 3. 知识处理与存储要求

**若检索到历史个人知识点：**
- 深入研究、剖析、整理和总结

**若未检索到历史个人知识点：**
- 创建新的整理总结内容

**必须执行的操作：**
1. 整理内容整合到 Karpathy 知识库系统
2. 文件/截图附件存入 `raw/` 目录
3. 整理成 Wiki 笔记
4. 同步至飞书文档
5. 同步至 Notion 笔记
6. 上传至云端 Milvus 记忆库

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
- 京麦智能体：搭建中，进度 **78%**（2026-04-10宁兄日报：78%）
- Seeduplex（2025-JQ03-W1237）：✅ 已结束归档（2026-04-10通知）
- OpenClaw：多渠道AI助手，持续运行

## 2026-04-12 Dream 整合记录

### 整合范围
- 扫描文件：2026-04-06 / 2026-04-07 / 2026-04-08 / 2026-04-09 / 2026-04-10（5个文件）

### MEMORY.md 更新
1. 京麦智能体进度 78% 已确认
2. Seeduplex 2025-JQ03-W1237 已结束归档
3. 知识库 compile.py 存在 SIGKILL 问题（内存/超时），飞书114文档同步完成
4. 内容捕手抖音受阻（需登录），B站成功326条
5. OpenMAIC/AgentSkills/Hermes Agent/GitNexus 研究成果已归档

### 旧日志标记
- 2026-03-27.md / 2026-03-28.md / 2026-03-31.md 已标记 consolidation

## 2026-04-10 新增研究成果（宁兄日报）

### Hermes Agent（Nous Research，33.3k Stars）
- 内置闭环学习系统，自动创建Skills，跨会话记忆
- 文档：`knowledge/Hermes-Agent-深度研究报告.md`

### GitNexus（Graph RAG可视化代码工具）
- 预防AI瞎改，可视化代码结构/依赖/调用链
- 文档：`knowledge/GitNexus-编程救星预防AI瞎改.md`

### OpenMAIC（清华THU-MAIC，13.6k Stars）
- PDF转课堂，AI教师，白板互动
- 文档：`knowledge/openmaic.md`

### OpenCLI（网页/Electron → CLI）
- 任意网站/Electron应用转CLI工具

### TTS横评：LongCat AudioDiT胜出
- LongCat AudioDiT: 3.5B, 12GB显存, 6秒生成, 音质很好
- Qwen2-TTS: 0.6B, 5GB, 33秒
- Fish Audio S2 Pro: 4B, 20GB, >60秒

### Coze扣子编程平台
- 1500万+用户，Vibe Coding平台
- **OpenClaw已入驻扣子！可一键部署**
- 对比：扣子更易用，OpenClaw更灵活
- 文档：`knowledge/Coze扣子编程平台研究报告.md`

### AgentSkills SKILL.md技术规范
- Skills本质：把人类经验写成说明书
- YAML头部：Name唯一性 + Description意图路由（命中率45%→92%）
- CoT思维链：判定条件 + 分步指南 + 异常分支
- 文档：`knowledge/AgentSkills-SKILL技术规范详解.md`

## Karpathy 知识库系统（2026-04-09 完整搭建完成）⭐

### 系统架构
```
knowledge-base/
├── CLAUDE.md           ← Schema规则手册
├── raw/               ← 原始资料（只读，611张宁兄抖音截图）
├── wiki/             ← 知识库（index/log/概念/来源/实体）
├── comparisons/       ← 对比分析
└── sync_*.py        ← 同步脚本
```

### 核心组件（全部完成）
| 组件 | 功能 | 状态 |
|------|------|------|
| compile.py | INGEST摄入（raw→wiki） | ⚠️ LLM编译存在SIGKILL问题（内存/超时），需优化 |
| lint.py | 健康检查 | ✅ |
| query.py | 问答查询 | ✅ |
| sync_feishu.py | 飞书同步（114文档） | ✅ |
| sync_notion.py | Notion同步（114文档） | ✅ |
| upload_mem0.py | Milvus云端同步（114条） | ✅ |

### 同步状态（2026-04-09）
- 飞书Database ID：33d2bb5417c380f6baaff3467dea91c8
- 飞书同步：114文档 ✅
- Notion同步：114文档 ✅
- Milvus云端：114条 ✅
- Cron定时同步：每天20:00 ✅

### 知识库Database ID
- 飞书：33d2bb5417c380f6baaff3467dea91c8
- Notion：已配置API Token + Database ID

### 新增内容（2026-04-09）
- Alchemy（清华AI科研自动化）：algorithm.py + yaml 交付模式
- Harness Engineering 2026：Prompt → Context → Harness 三阶段
- GitHub TOP20 第9周：GitNexus / Claude Code生态 / 端侧推理+知识图谱
- MemPalace（23.6k stars）：AI记忆系统
- chrome-devtools-mcp：Chrome DevTools MCP
- MCP生态全景图（12+服务）

### 新增内容（2026-04-10）
- **Hermes Agent**（Nous Research，33.3k Stars）：内置闭环学习系统，自动创建Skills，跨会话记忆
- **GitNexus**：Graph RAG可视化代码工具，预防AI瞎改，可视化依赖/调用链
- **OpenMAIC**（清华THU-MAIC，13.6k Stars）：PDF转课堂，AI教师，白板互动
- **OpenCLI**：任意网站/Electron应用转CLI工具
- **TTS横评**：LongCat AudioDiT胜出（3.5B/12GB显存/6秒生成）
- **Coze扣子平台**：1500万+用户，OpenClaw已入驻可一键部署
- **AgentSkills技术规范**：SKILL.md格式（YAML头部/Description/CoT思维链），命中率45%→92%
- **Karpathy流程升级**：raw→wiki→飞书→Notion→Milvus全链路同步

### 避坑记录
- 飞书 docx:document.block:convert 权限 → 手动申请开通 ✅
- Notion 集成Database权限 → 在Database页面添加连接 ✅

## 内容捕手状态（2026-04-10 更新）

| 平台 | 状态 | 数据量 | 待解决 |
|------|------|--------|--------|
| B站 | ✅ 成功 | 326条 | 有412限流，需重试 |
| 抖音 | ⚠️ 受阻 | 172条 | 需登录/cookie-sync |

### 待解决
- 方案A：cookie-sync skill 同步Chrome已登录Cookie（已安装）
- 方案B：human-browser / agent-reach 抖音通道
- 方案C：蝉妈妈/微播易 第三方API

## ELUCKY 账号矩阵（2026-04-07 更新）

| 平台 | 账号数量 | 定位 |
|------|---------|------|
| TikTok | 230 | 主力平台 |
| Facebook | 150 | 社交引流 |
| Instagram | 120 | 视觉内容 |
| X (Twitter) | 80 | 资讯分发 |

养号方案 v2.0：TikTok 14天周期 + 跨平台连坐风控 + 22周开发规划

## 2026-04-08 研究成果

### 上午研究（08:00-09:00）

#### 1. awesome-design-md 项目分析
- 项目：VoltAgent/awesome-design-md，24.4k Stars
- 58个平台设计系统开源（Linear/Vercel/Cursor等）
- 核心理念：DESIGN.md格式让AI编程工具直接生成像素级UI
- 格式规范：9大章节标准格式
- 文档：knowledge/awesome-design-md-analysis.md

#### 2. Karpathy 知识库编译工作流
- 三步曲：收集(raw/) → 编译(LLM) → 查询(直接答)
- 100篇/40万字规模下不需要RAG
- 查询结果反哺wiki，知识越滚越大
- 工具：Obsidian Web Clipper
- 文档：knowledge/karpathy-wiki-knowledge-base-workflow.md

#### 3. LangChain 三层学习框架
- Agent持续学习三层面：Model层/Harness层/Context层
- Trace是三层学习的共同原料
- Context层=Skills=OpenClaw热更新能力
- 神级类比：Model=引擎/Harness=底盘/Context=GPS
- 文档：knowledge/agent-continual-learning-three-layers.md

#### 4. AI Agent 知识管理统一框架
- 融合Karpathy + LangChain三层学习
- 统一框架：raw→wiki→query→Trace→三层学习
- 文档：knowledge/ai-agent-knowledge-management-unified-framework.md

#### 5. OpenClaw Context层Skills设计
- Skills = Context层可复用组件
- 核心Skill：knowledge-collector/wiki-compiler/knowledge-query/coworker
- 文档：knowledge/openclaw-context-layer-skills-design.md

#### 6. OpenClaw可观测性Trace系统
- Trace是三层学习的共同原料
- Trace数据结构：event_id/timestamp/session_id/event_type/data
- 文档：knowledge/openclaw-observability-trace-system.md

#### 7. Karpathy工作流OpenClaw实现
- 目录结构：raw/原始资料、wiki/知识库、workspace/代码
- 工具：Collector收集器、Compiler编译器、Query查询器
- 文档：knowledge/karpathy-wiki-workflow-openclaw-implementation.md

#### 8. AI周报第439期（产品君）
- 本周主题：开源爆发+语音AI突破
- 重大新闻：GPT-Image-2/Gemma4/Qwen3.5-Omni/同事.skill等
- 文档：knowledge/ai-weekly-report-2026-04-05.md

### 记忆上传
- 已上传9条记忆到云端Milvus + 本地ChromaDB
- 验证：Karpathy/三层学习/AI周报/Skills 均可搜索到
- 上传脚本：scripts/upload_today_memories.py

### Git提交
- docs: add weekly AI report + Context layer skills design + Trace system + Karpathy workflow implementation
- 4个文件，1740行新增

## 2026-04-08 下午研究成果（08:45-08:49）

### 视频研究

#### 1. SDD开发教程（大力AI第5集）
- OpenSpec规范多人协作
- SDD最小闭环：init→explore→propose→apply→archive
- 与纯裸聊差别：有回看、有reveal、有交接、有演进

#### 2. Red/Green TDD方法论（大力AI）
- Simon Willison提出：AI编程时代测试必须
- 流程：RED写测试→GREEN写代码→REFACTOR重构
- AI会作弊改期望值，需测试文件加锁

#### 3. Karpathy个人知识库（大力AI第18集）
- 三个文件夹：RO/原始素材、wiki/整理、altpus/答案报告
- CLOD.md指令文件
- 对比NotebookLM：Karpathy上限更高

#### 4. GitHub一周star排行TOP20（赛博笔记）
- 本周主题：AI基础设施+Agent工具+开发者效率
- 系列：第3集1.5万赞、第7集1859赞

### 新Skill发现

#### Anspire Web Search v1.0.3
- ClawHub上的国内信息搜索Skill
- 作者：Gavin，MIT-0，VirusTotal安全

#### xcrowd
- 数据采集必备Skill
- ClawHub未收录，可能刚发布

### ClawHub数据类Skills
- Data Analyst 5.1k stars
- Data Model Designer 3.9k stars
- 国内：Data Analyst Cn 1.6k stars

### 下午记忆上传
- 已上传7条记忆到云端Milvus + 本地ChromaDB

## 2026-04-08 上午研究成果（08:00-09:00）

### awesome-design-md 项目分析
- 仓库：VoltAgent/awesome-design-md，24.4k Stars
- 58个平台设计系统开源（Linear/Vercel/Cursor等）
- 核心理念：DESIGN.md格式让AI编程工具直接生成像素级UI
- 格式规范：9大章节标准格式
- 文档：knowledge/awesome-design-md-analysis.md

### Karpathy 知识库编译工作流
- 三步曲：收集(raw/) → 编译(LLM) → 查询(直接答)
- 100篇/40万字规模下不需要RAG
- 工具：Obsidian Web Clipper
- 文档：knowledge/karpathy-wiki-knowledge-base-workflow.md

### LangChain 三层学习框架
- Agent持续学习三层面：Model层(权重)/Harness层(执行框架)/Context层(运行时配置)
- 神级类比：Model=引擎/Harness=底盘/Context=GPS
- Context层=Skills=OpenClaw热更新能力
- 文档：knowledge/agent-continual-learning-three-layers.md

### OpenClaw 可观测性Trace系统
- Trace是三层学习的共同原料
- Trace数据结构：event_id/timestamp/session_id/event_type/data
- 文档：knowledge/openclaw-observability-trace-system.md

### AI周报第439期（产品君）
- 11条重大新闻：GPT-Image-2/Project Stagecraft/Gemma4/Qwen3.5-Omni/Sakana AI Marlin等
- 文档：knowledge/ai-weekly-report-2026-04-05.md

### 记忆上传
- 已上传9条记忆到云端Milvus + 本地ChromaDB
- 脚本：scripts/upload_today_memories.py

## 2026-04-08 下午研究成果（08:45-10:20）

### SDD开发教程 + Red/Green TDD方法论
- OpenSpec SDD最小闭环：init→explore→propose→apply→archive
- Simon Willison TDD流程：RED写测试→GREEN写代码→REFACTOR重构
- **重要避坑**：Claude Code会改测试期望值让测试通过，测试文件需加锁
- 文档：knowledge/openspec-sdd-dev-workflow.md

### Harness Engineering（@从小就坏）
- 核心理念：AI不确定性需控制系统，Prompt=系统宪法
- 心跳机制：一次性API调用 → 持续运行循环
- 以驾驭系统为中心，非以模型为中心

### Agent-Reach v1.4.0（16.3k Stars）
- 17平台支持：网页/YouTube/RSS/GitHub/Twitter/小红书/抖音/Reddit/LinkedIn/微信公众号/微博/V2EX/雪球/小宇宙播客
- MIT License，完全免费
- 文档：知识库

### GitHub一周star排行TOP20（赛博笔记）
- 本周主题：AI基础设施+Agent工具+开发者效率
- 系列推荐：第3集(everything-claude-code)1.5万点赞、第7集1859点赞

### jingmai-agent-cli 技能复刻与删除
- 读取源码 → skill-creator创建 → 测试通过 → 因需求变更已删除

## 2026-04-08 晚间任务（Karpathy风格知识库搭建）

### 目录结构
```
knowledge-base/
├── raw/               # 原始资料（不修改）
├── wiki/              # 编译后的知识库
├── altpus/            # AI 答案报告
└── CLOD.md           # 指令文件
```

### 核心脚本
| 脚本 | 功能 |
|------|------|
| compile.py | raw → wiki 编译 |
| sync_feishu.py | 飞书同步 |
| sync_notion.py | Notion 同步 |
| upload_mem0.py | 云端 Milvus 同步 |

### 已完成
- ✅ 目录结构创建
- ✅ 编译脚本 compile.py（测试通过）
- ✅ 飞书文档创建（2个文档）
- ✅ 云端 Milvus 上传（2条记忆，验证成功）

### 待完成
- [ ] 飞书文档内容写入（需要 docx:document.block:convert 权限）
- [ ] Notion API 配置
- [ ] 实际收集更多 raw 材料

## 内容捕手状态（2026-04-06 更新）

### 执行结果
| 平台 | 状态 | 数据量 | 问题 |
|------|------|--------|------|
| B站 | ✅ 成功 | 326条 | 有412限流，需重试 |
| 抖音 | ⚠️ 受阻 | 172条 | 需要msToken/X-Bogus签名 |

### 待解决
- [ ] human-browser skill绕过抖音验证码
- [ ] agent-reach技能抖音通道
- 脚本：scrape_bilibili.py（已优化带重试）/ scrape_douyin.py（需解决签名）

## 2026-04-03 Skills研究（待安装）

### MindsDB - AI分析查询引擎
- 一条SQL查遍200+数据源
- 安装：Docker或PyPI
- 文档：knowledge/mindsdb.md

### OpenMAIC - 清华开源AI课堂
- 一键生成完整课堂（课件+测验+视频）
- 文档：knowledge/openmaic.md

## 2026-04-08 Skills安装总结

### AI干货局6个必备Skill
| # | Skill | Stars | 状态 |
|---|-------|-------|------|
| 1 | react-best-practices | 3.6k | ✅ 已安装 |
| 2 | remotion-video-toolkit | 16k | ✅ 已安装 |
| 3 | superdesign | 28.2k | ✅ 已安装 |
| 4 | mobile | 1.6k | ✅ 已安装 |
| 5 | azure-ai | - | ⚠️ 未找到 |
| 6 | frontend-design-pro | - | ⚠️ 限流未安装 |

### 当前已安装Skills（共9个）
| Skill | Stars | 用途 |
|-------|-------|------|
| agent-reach | 16.3k | 17平台互联网能力 |
| anspire-web-search | - | 国内信息搜索 |
| mobile | 1.6k | 移动端开发 |
| react-best-practices | 3.6k | React性能优化57规则 |
| remotion-video-toolkit | 16k | 视频生成 |
| superdesign | 28.2k | 专家级UI设计 |
| windows-control | - | Windows自动化 |
| frontend-design | - | 前端设计 |
| ui-design | - | UI设计 |
- 上传脚本：scripts/upload_20260408_research.py

## 2026-03-31 今日AI热点（重要！）

### 1. 企业微信正式开源CLI ⭐⭐⭐⭐⭐
- 微信官方支持AI Agent调用企微7大办公能力（消息、审批、邮件等）
- 技术价值：企业级AI Agent工作流打通告微生态，CLI降低接入门槛
- 应用场景：企业内部AI助手、智能办公自动化、跨系统工作流编排

### 2. Midjourney Pretext ⭐⭐⭐⭐⭐
- 15KB轻量库实现网页排版渲染千倍提速
- 前端性能优化突破性进展，AI驱动排版算法革新

### 3. 微软VibeVoice ⭐⭐⭐⭐
- 长音频语音识别模型，单次处理可达60分钟
- 会议记录、电话录音处理、长视频字幕生成

### 4. UniPat AI EchoZ预测系统 ⭐⭐⭐⭐
- 专用预测模型在垂直领域超越通用大模型
- 金融预测、库存预测、需求预测等商业预测场景

### 5. 港科大AI气味戒指 ⭐⭐⭐⭐⭐
- 多模态AI + 可穿戴设备，通过皮肤代谢气味监测健康
- 交叉学科创新：传感 + AI + 生物化学

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
| memory-dream | ✅ 已安装 | 2026-04-07 | 精通 | - |
| openspace | ✅ 已安装 | 2026-04-07 | 🔰待实践 | 需API Key配置 |
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

### 已安装Skills/Packages
| 技能/包 | 版本 | 日期 | 用途 |
|---------|------|------|------|
| summarize | 1.0.0 | 2026-04-02 | 总结网页/PDF/YouTube |
| nano-banana-pro | 1.0.1 | 2026-04-02 | AI图片生成（Gemini 3 Pro） |
| memory-dream | 1.0.3 | 2026-04-07 | 记忆整合（睡眠记忆） |
| openspace | 0.1.0 | 2026-04-07 | HKUDS自进化引擎（GitHub安装） |

### Cron任务状态
| 任务 | ID | 时间 | 状态 |
|------|-----|------|------|
| dream-nightly | 421b1f35 | 每天03:00 | ✅ ok |
| daily-git-commit | 1690b963 | 每天22:30 | ✅ ok |
| 内容捕手-汇报 | f27317c4 | 每天18:00 | ✅ 已修复 |
| daily-skill-security-scan | 5227d14e | 每天00:30 | ✅ ok |
| morning-wechat-login-check | e1f7f495 | 每天09:00 | ✅ ok |
| knowledge-base-sync | - | 每天20:00 | ✅ Karpathy知识库定时同步 |

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

## HKUDS 港大AI Agent生态（2026-04新发布）

### 三项目矩阵
| 项目 | 定位 | Stars | 核心价值 |
|------|------|-------|---------|
| OpenSpace | 自进化引擎 | - | 技能进化+经验沉淀 |
| OpenHarness | 基础设施框架 | 4000+ | hands/eyes/memory/safety |
| CLI-Anything | CLI生成工具 | 1400+ | 任意软件→CLI |

### 三层架构
```
OpenSpace（进化层）→ OpenHarness（基础层）→ CLI-Anything（接口层）
```

### OpenSpace 自进化引擎
- **一句话**：让AI Agent自我进化的技能引擎
- **实测**：Token消耗-46%，收入4.2倍
- **命令**：openspace capture/evolve/optimize

### OpenHarness 轻量级框架
- **一句话**：1万行Python复刻Claude Code 98%功能
- **定位**：Agent基础设施（hands/eyes/memory/safety）
- **优势**：模型无关，可复用Claude Code生态

### 与OpenClaw协同
```
OpenClaw（主框架）
    ├── OpenHarness（基础设施增强）
    ├── OpenSpace（进化能力增强）
    └── CLI-Anything（工具扩展）
```

## HKUDS OpenSpace 自进化引擎

### 核心定位
- **一句话**：让AI Agent自我进化的技能引擎
- **官网**：github.com/HKUDS/OpenSpace
- **支持**：OpenClaw / Claude Code / Cursor / Codex / nanobot
- **状态**：✅ v0.1.0 已安装（2026-04-07）

### 三大核心能力
| 能力 | 说明 |
|------|------|
| 🔧 自动修复 | 技能失效自己修 |
| 📚 经验沉淀 | 成功经验固化为可复用Skill |
| ⚡ 工作流捕获 | 复杂任务简化为一条命令 |

### 核心数据
- Token消耗 **减少46%**
- 收入提升 **4.2倍**
- 6小时赚取 **$11K**

### 核心命令
```bash
openspace capture --task "任务" --output skill-name  # 捕获成功任务
openspace skill list                                  # 查看技能
openspace evolve --skill skill-name                   # 进化技能
openspace optimize --all                              # 批量优化
openspace engine start                                # 启动引擎
```

### 与梦境记忆的关系
- **梦境记忆（memory-dream）**：整理和遗忘（记忆层面）
- **OpenSpace**：技能进化（能力层面）
- **组合效果**：真正的学习型Agent

### 文档
- `knowledge/hkuds-openspace-self-evolution.md`
- `knowledge/hkuds-openharness-agent-framework.md`
- `knowledge/hkuds-ai-agent-ecosystem.md`

## OpenSpec SDD 规范驱动开发

### 核心定位
- **一句话**：先对齐规范，再写代码（Agree before you build）
- **官网**：github.com/Fission-AI/OpenSpec
- **定位**：AI-Native规范驱动开发系统

### 解决问题
- AI编程质量不稳定（有时神队友，有时漏洞百出）
- 需求只有聊天记录，没有结构化文档
- 多人协作规范不统一

### 工作流
```
📝 提案（Proposal） → 📋 规范（Spec） → 🎨 设计（Design） → ✅ 任务（Tasks）
```

### 安装命令
```bash
npm install -g openspec
# 或
pip install openspec
```

### 与AI-Native SOP对应
| AI-Native SOP阶段 | OpenSpec对应 |
|-------------------|-------------|
| 阶段5：AI逻辑 | Spec规范编写 |
| 阶段6：AI编程 | Generate生成 |
| 验证环节 | Verify验证 |

### 文档
- `knowledge/openspec-sdd-dev-workflow.md`

## DeerFlow 2.0 × ELUCKY 架构融合

### 核心信息
- **出品方**：字节跳动（ByteDance）
- **类型**：SuperAgent Harness
- **Stars**：47.3k+
- **基于**：LangGraph 1.0

### 六大组件
| 组件 | 说明 |
|------|------|
| memory | 多层次记忆系统 |
| tools | 扩展工具集 |
| subagents | 子Agent编排 |
| sandboxes | 沙箱隔离执行 |
| skills | 可扩展技能 |
| message gateway | 消息网关 |

### DeerFlow vs OpenHarness
| 维度 | DeerFlow 2.0 | OpenHarness |
|------|---------------|-------------|
| 出品方 | 字节跳动 | 港大HKUDS |
| Stars | 47.3k | 4000+ |
| 定位 | SuperAgent运行时 | 轻量基础设施 |

### ELUCKY v2融合方案
- Phase1：集成DeerFlow Harness Core
- Phase2：重构LangGraph Orchestrator
- Phase3：对接OpenSpace进化引擎
- Phase4：灰度发布验证

### 文档
- `knowledge/deerflow-elucky-integration.md`

## ELUCKY 跨境电商多平台矩阵（2026-04-07 更新）

### 账号矩阵规划（来源：Excel「改造Agent+风控+汇总.xlsx」）
| 平台 | 账号数量 | 定位 |
|------|---------|------|
| TikTok | 230 | 主力平台 |
| Facebook | 150 | 社交引流 |
| Instagram | 120 | 视觉内容 |
| X (Twitter) | 80 | 资讯分发 |

### ELUCKY养号方案 v2.0（TikTok + 跨平台连坐风控）
- **文档**：`knowledge/ELUCKY-account-nurture-plan.md`
- **新增**：TikTok完整养号14天周期 + 操作上限规则
- **新增**：FB+IG Meta关联跨平台连坐风控机制
- **开发阶段**：22周（5.5个月）规划

### ELUCKY Agent Task 拆解
- **文档**：`knowledge/ELUCKY-agent-task-list.md`
- **内容**：TK养号(11任务) / TK挂靠(8任务) / TK风控(10任务) / TK设备管理(8任务)
- **每日执行时间表** + 每周计划 + 监控指标

### DeerFlow 2.0 × ELUCKY 融合
- **文档**：`knowledge/deerflow-elucky-integration.md`
- **融合Phase**：DeerFlow Harness Core → LangGraph重构 → OpenSpace进化 → 灰度发布
- **融合价值**：成熟Harness运行时 + 沙箱隔离 + 多层次记忆系统
