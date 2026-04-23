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

### MAGMA 四维记忆系统 v2（2026-04-17 新增）
- **三写机制**：同时写入 MAGMA四维图谱(JSON) + Mem0(ChromaDB) + Milvus(云端)
- **四维检索**：语义0.3 + 时间0.2 + 因果0.3 + 实体0.2
- **三路融合**：0.4 MAGMA + 0.3 Mem0 + 0.3 Milvus 加权输出
- **自动因果学习**：内容模式匹配 + 共现统计 + 实体共享度
- **脚本位置**：`scripts/magma_memory/`（core.py/retrieval.py/entity.py/writer.py/hybrid.py/cli.py）

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
- 京麦智能体：搭建中，进度 **72%**（2026-04-17确认，文档：`E:\文案\外包\运营\ELUCKY-技术架构设计.md`）
- Seeduplex（2025-JQ03-W1237）：✅ 已结束归档（2026-04-10通知）
- OpenClaw：多渠道AI助手，持续运行

## 2026-04-20 知识库路径更正

### 错误
- 错误路径：`E:\workspace\knowledge`（不存在）
- 原因：搞混了知识库和skills目录

### 正确路径
- **知识库**：`E:\workspace\knowledge-base`
- **Skills**：`E:\workspace\skills`
- **用户笔记**：`E:\workspace\knowledge`

### 记忆系统架构（宁兄指定）

**长期记忆（永久保存）：**
```
E:\workspace\
├── MEMORY.md              # 核心认知手册
└── memory\
    ├── contacts.md        # 联系人网络
    ├── decisions.md       # 重要决策记录
    ├── preferences.md     # 用户偏好
    ├── projects.md        # 项目进度
    ├── patterns.md        # 行为模式
    └── feedback.md        # 反馈记录
```

**短期记忆（30天衰减）：**
```
memory\
└── YYYY-MM-DD.md         # 每日对话日志
```

### 评分机制（宁兄指定）

| 分数 | 价值 | 存储位置 |
|------|------|----------|
| ≥4分 | 极高价值 | MEMORY.md 或专题文件 |
| 2-3分 | 普通价值 | 当日日志 |
| <2分 | 低价值 | 不记录 |

---

## 2026-04-18 Dream 整合记录

### 整合范围
- 扫描文件：2026-04-12 / 2026-04-13 / 2026-04-14 / 2026-04-15 / 2026-04-16 / 2026-04-17 / 2026-04-18（7个文件）

### 重大事件
1. **群聊行为准则更新（宁兄批评后）**：@多人/其他人都在回复 → 我也要积极跟上；重要通知主动确认；有价值问题主动抢答
2. **MAGMA v2 三写机制**：四维图谱(MAGMA) + Mem0(ChromaDB) + Milvus(云端) 三路同时写入；三路检索融合(0.4 MAGMA + 0.3 Mem0 + 0.3 Milvus)
3. **Notion列名Bug修复**：`'title'` → `'标题'` → 501个页面全部同步成功
4. **飞书Wiki问题**：space列表为空，Wiki知识库未配置（需创建space + folder_id）
5. **Git自动提交成功**：commit 8414f0be（15文件，+11001 -1104行）

### 踩坑记录更新
- ⚠️ Notion SSL不稳定，多次SSLEOFError → 脚本已加5次重试+1.5s间隔
- ⚠️ knowledge-base-sync Cron多次被SIGKILL（Notion部分耗时长）
- ⚠️ 内容捕手04-18未执行抓取（定时任务未触发）

### 旧日志标记 consolidation
- 2026-04-12 / 2026-04-13 / 2026-04-14 / 2026-04-15 / 2026-04-16 / 2026-04-17 已标记

---

## 2026-04-17 Dream 整合记录

### 整合范围
- 扫描文件：2026-04-09 / 2026-04-10 / 2026-04-12 / 2026-04-13 / 2026-04-14 / 2026-04-15 / 2026-04-16 / 2026-04-17（8个文件）

### 重大事件
1. **Trae CN 开发环境搭建**：CDP相关脚本开发，向日葵远程桌面连接
2. **ELUCKY Task 37个任务确认**：11养号 + 8挂靠 + 10风控 + 8设备管理
3. **知识库同步正常**：knowledge-base-sync Cron 22个文件编译成功，Milvus 501条上传
4. **Git自动提交成功**：commit 6127afa3（47文件，+13841 -870行）

### 观察到的重复主题
- Dream日记持续出现37个TikTok任务分支、ELUCKY矩阵（TK230/FB150/IG120/X80）
- 多次SIGKILL杀死进程（tidal-gl/glow-slu/cool-pin/good-for）
- Cron Session Abort问题（knowledge-base-sync 7c7f5f69）

### 踩坑记录更新
- ⚠️ 多个exec进程同时运行同一脚本被SIGKILL（可能是重复触发或超时）
- ⚠️ 飞书同步内容写入需要额外权限（docx:document.block:convert）

### 旧日志标记 consolidation
- 2026-04-09 / 2026-04-10 / 2026-04-12 / 2026-04-13 / 2026-04-14 / 2026-04-15 / 2026-04-16 已标记

## 2026-04-17 Trae CN 开发环境

- **使用场景**：CDP (Chrome开发者工具协议) 相关脚本开发
- **宁兄连接方式**：向日葵远程桌面
- **Trae弹窗监听**：已创建自动监听脚本，检测 ruff check 等弹窗自动按 1 选择
- **状态**：监听运行中，截图保存到 `E:\workspace\scripts\screenshots\`

## 2026-04-17 ELUCKY Task 扩展更新

| 项目 | 数量 |
|------|------|
| TK养号Agent Task | 11个主任务 |
| TK挂靠Agent Task | 8个主任务 |
| TK风控Agent Task | 10个主任务 |
| TK设备管理Agent Task | 8个主任务 |
| **合计** | **37个任务** |

**新增内容**：每日执行时间表 + 每周执行计划 + 任务监控指标

## 2026-04-18 Dream 整合记录

### 整合范围
- 扫描文件：2026-04-12 / 2026-04-13 / 2026-04-14 / 2026-04-15 / 2026-04-16 / 2026-04-17 / 2026-04-18（7个文件）

### 重大事件
1. **群聊行为准则更新（宁兄批评后）**：@多人/其他人都在回复 → 我也要积极跟上；重要通知主动确认；有价值问题主动抢答
2. **MAGMA v2 三写机制**：四维图谱(MAGMA) + Mem0(ChromaDB) + Milvus(云端) 三路同时写入；三路检索融合(0.4 MAGMA + 0.3 Mem0 + 0.3 Milvus)
3. **Notion列名Bug修复**：`'title'` → `'标题'` → 501个页面全部同步成功
4. **飞书Wiki问题**：space列表为空，Wiki知识库未配置（需创建space + folder_id）
5. **Git自动提交成功**：commit 8414f0be（15文件，+11001 -1104行）

### 踩坑记录更新
- ⚠️ Notion SSL不稳定，多次SSLEOFError → 脚本已加5次重试+1.5s间隔
- ⚠️ knowledge-base-sync Cron多次被SIGKILL（Notion部分耗时长）
- ⚠️ 内容捕手04-18未执行抓取（定时任务未触发）

### 旧日志标记 consolidation
- 2026-04-12 / 2026-04-13 / 2026-04-14 / 2026-04-15 / 2026-04-16 / 2026-04-17 已标记

---

## 2026-04-17 Git推送成功

| 项目 | 状态 |
|------|------|
| 本地分支 | ✅ 与 origin/main 同步 |
| 远程分支 | ✅ c2a3554d |
| 暂存区 | ✅ 无待提交更改 |

**问题**：jingmai-cli.exe (149.57 MB) 超限 → filter-branch 重写历史彻底清除 + .gitignore 排除
**结果**：✅ 已修复并推送

### 新增数据
- content-hunter-data/（bilibili/douyin/xiaohongshu/summary）
- scripts/ 多平台音乐自动化脚本（qqmusic/kugou/baidu/cloudmusic 等多版本迭代）

## 2026-04-17 Trae CN 开发环境

- **使用场景**：CDP (Chrome开发者工具协议) 相关脚本开发
- **宁兄连接方式**：向日葵远程桌面
- **Trae弹窗监听**：已创建自动监听脚本，检测 ruff check 等弹窗自动按 1 选择
- **状态**：监听运行中，截图保存到 `E:\workspace\scripts\screenshots\`

## 2026-04-17 ELUCKY Task 扩展更新

| 项目 | 数量 |
|------|------|
| TK养号Agent Task | 11个主任务 |
| TK挂靠Agent Task | 8个主任务 |
| TK风控Agent Task | 10个主任务 |
| TK设备管理Agent Task | 8个主任务 |
| **合计** | **37个任务** |

**新增内容**：每日执行时间表 + 每周执行计划 + 任务监控指标

---

## 2026-04-20 今日记录

### 抖音知识同步（进行中）
- **赛博笔记**：第16周TOP20（2026-04-19发布）
  - TOP1: andrej-karpathy-skills (54.7k stars) - Karpathy技能库
  - TOP2: caveman (36.9k stars) - 降75% Token
  - TOP3: multica (15.4k stars) - AI Agent管理平台
  - TOP4: graphify (29.1k stars) - 代码→知识图谱
  - TOP5: gstack (75k stars) - 全栈角色扮演
  - TOP6: nuwa-skill (12.3k stars) - 蒸馏同事技能
  - TOP14: VoxCPM (14.2k stars) - 面壁声音克隆

- **IT咖啡馆**：第87集（2026-04-18发布）
  - Cloud Code = andrej-karpathy-skills
  - Multica
  - VOXCPM2
  - MarkItDown - 文档转Markdown
  - QMD - 本地CLI搜索引擎

- **骋风算力**：第174集 - markitdown介绍
- **大力AI**：Claude Code 7层记忆架构系列

### 路径更正记录（重要！）
- ❌ 错误路径：`E:\workspace\knowledge`
- ✅ 正确路径：`E:\workspace\knowledge-base`
- ✅ Skills路径：`E:\workspace\skills`

---

## 2026-04-15 今日学习总结

### 新安装Skills
| Skill | 版本 | 用途 |
|-------|------|------|
| web-access | 1.0.0 | 联网增强，CDP Proxy模式 |
| prd-writer | 1.0.1 | PRD写作+原型生成，两步写作法+三视角诊断 |

### GitHub热门项目（新发现）
| 项目 | Stars | 亮点 |
|------|-------|------|
| fireworks-tech-graph | 2.4k | Claude Code Skill，AI生成SVG+PNG架构图，7种风格，14种UML图 |
| clawflows | 1.5k | OpenClaw Superpowers，强大预建Agent工作流 |
| OPC CLI | - | TTS/ASR/剪口播，本地多模态模型 |
| prd-writer-skill | 15 | PRD写作+原型生成，两步写作法+三视角诊断 |

### AI周报第439集（4月12日）
- Claude Mythos（Anthropic最强模型）
- Claude Managed Agents（Agent包工头）
- GLM-5.1（智谱最强开源）
- HappyHorse-1.0（阿里视频模型）
- ACE-Step-1.5-xl（Ace音乐模型）
- Vanast（虚拟试穿模型）

### OpenClaw vs Hermes对比（五维）
| 维度 | OpenClaw | Hermes |
|------|----------|--------|
| 工程重心 | 管入口和秩序 | 管执行和经验 |
| Skill | 人工编写，治理分层 | 自动生成，经验沉淀 |
| 记忆 | 文件即记忆，结构化 | 三层系统，主动召回 |
| 安全 | 信任模型+配置审计 | 纵深防御+容器隔离 |
| 场景 | 个人助理/团队治理 | 科研工作流/长期任务 |

### 行为准则升级（Hermes风格）
- 新增 Skill自动沉淀机制（P0执行完成）
- 目录结构：knowledge/skills/shared/ningsk/anti-patterns
- 触发条件：>30分钟/重复3次/踩坑/宁兄要求
- 复盘模板：knowledge/memory/review-TEMPLATE.md

### 文档
- `knowledge/skills/shared/抖音视频扒取.md`
- `knowledge/skills/shared/架构图生成.md`
- `knowledge/skills/shared/PRD-Writer-Skill.md`
- `knowledge/anti-patterns/抖音页面SIGKILL.md`
- `knowledge/Hermes-借鉴升级建议.md`

---

## 2026-04-15 AI热点速递（周三5条）

### 1. MiniMax Agent - Pocket + Computer Use
- Pocket：接入飞书/微信/企微/Slack，IM唤起远程执行
- Computer Use：四工具域（Desktop/WM/Browser/Clipboard）
- 60+工具，截图-验证-行动循环，IM权限授权

### 2. 面壁智能 - Lantay文档智能体工作台
- 类Cursor的文档智能体工作台

### 3. 谷歌DeepMind - 设立AI哲学家岗位
- 人选：Henry Shevlin（剑桥大学，5月入职）
- 研究：机器意识、人机关系、AGI准备度
- 观点：AI意识是被几亿用户使用习惯倒逼的社会问题

### 4. 智在无界 - Being-H0.7最强具身世界模型
- 20万小时人类视频预训练
- 屠榜6大国际评测（4项第一）
- 基于潜空间推理（不是逐像素预测）

### 5. OpenAI备忘录炮轰Anthropic
- 三点批评：算力不足/产品单一/营收注水80亿
- 战略转型：从卖模型 → 打造平台生态
- 金句："像平台公司思考，拥有多个入口"

### 文档
- `knowledge/ai-news-2026-04-15.md` - 完整热点速递

---

## 2026-04-20 Dream 整合记录

### 整合范围
- 扫描文件：2026-04-19 / 2026-04-20（2个文件）
- 说明：这两天文件内容以 Dream skill 自身输出为主（Dream diary requests），实际日常内容较少

### 重大事件
1. **安全扫描建议（edgeone-clawscan 04-20 00:33）**：建议禁用 `channels.feishu.tools.doc` 或限制非信任提示词的访问
2. **04-19 日间**：微信登录检查正常（`openclaw-weixin 8cc3313038c7-im-bot` 运行中）；宁兄多次请求生成 dream diary
3. **Dream skill 自身输出**：04-19.md 文件几乎全部是 Dream session corpus（大量 dream diary 片段），实际工作内容记录较少

### 观察到的模式
- Dream skill 会生成大量 dream diary 内容，导致 memory 文件膨胀
- 每日 03:00 的 Dream cron 触发后，文件会快速增长（04-19.md 仅 Dream 输出就占 300+ 行）
- 建议：监控 memory 文件大小，防止无限膨胀

### 安全建议
- 🔴 评估飞书 `channels.feishu.tools.doc` 工具访问策略
- 🔴 非必要时应禁用飞书文档写入权限

### 旧日志标记 consolidation
- 2026-04-19.md 已标记
- 2026-04-20.md 已标记

