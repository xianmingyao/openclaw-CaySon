# ELUCKY Multi-Agent System — Architecture Design
# ELUCKY 多平台Agent系统架构设计文档

> **项目名称**: ELUCKY 多平台社交媒体Agent运营系统
> **技术栈**: Python 3.12 + LangChain 1.0.4 + LangGraph 1.0.2 + LangChain-Community 0.4.0
> **Agent模式**: ReAct + Plan-and-Solve + Reflection + RAG
> **向量数据库**: Milvus
> **缓存**: Redis
> **版本**: v1.0
> **日期**: 2026-04-06

---

## 目录

1. [agent整体架构设计](#1-agent整体架构设计)
2. [数据库设计](#2-数据库设计)
3. [硬件设备设计](#3-硬件设备设计)
4. [api接口清单](#4-api接口清单)
5. [我们需要提前准备什么](#5-我们需要提前准备什么)
6. [交付标准归纳](#6-交付标准归纳)
7. [技术栈架构设计](#7-技术栈架构设计)
8. [agent提示词设计](#8-agent提示词设计)
9. [copilot边与节点状态的设计](#9-copilot边与节点状态的设计)
10. [ReAct设计](#10-react设计)
11. [Plan-and-Solve设计](#11-plan-and-solve设计)
12. [Reflection设计](#12-reflection设计)
13. [RAG知识库架构设计](#13-rag-知识库架构设计)
14. [长期记忆设计](#14-长期记忆设计)
15. [短期记忆设计](#15-短期记忆设计)
16. [工具MCP与CLI工具设计](#16-工具mcp与cli工具设计)
17. [Skills技能调用工具架构设计](#17-skills-技能调用工具架构设计)

---

## 1. Agent整体架构设计

### 1.1 架构设计理念

**参考项目对比分析：**

| 项目 | 核心架构 | 特点 | 借鉴点 |
|------|---------|------|--------|
| **Edict** (cft0808) | 三省六部制 | 多Agent编排 + 实时仪表盘 + 审计追踪 | 9个专业Agent分工 + 模型配置 + 审计日志 |
| **Agent-S** (Simular) | 通用体+专家体 | 分层规划 + GUI自动化 + 状态管理 | 主Agent负责任务分解，子Agent负责执行 |
| **DeerFlow 2.0** (ByteDance) | 分层编排 | Sub-Agent + Memory + Tools | 多层Agent协作 + 记忆管理 |
| **ClawCode** (UltraWorkers) | Clean-room rewrite | Terminal-native + Multi-agent | Agent分工 + 工具调用 |
| **AutoAgent** (KevinGu) | 自主迭代 | Self-optimizing harness | Agent可以自主优化自己的配置 |
| **Harness Engineering** | 环境+状态+控制 | 可靠性工程 | Agent运行环境的可靠性设计 |

### 1.2 ELUCKY Agent体系架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           🏛️ ELUCKY Agent System                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    📋 Master Agent (主控Agent)                    │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │   │
│  │  │ Platform    │  │ Task        │  │ Cross-Platform          │ │   │
│  │  │ Router     │  │ Scheduler   │  │ Coordinator             │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘ │   │
│  │                                                                  │   │
│  │  职责: 平台路由 | 任务调度 | 跨平台协调                           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│         ┌─────────────────────────┼─────────────────────────┐        │
│         │                         │                         │            │
│         ▼                         ▼                         ▼            │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐   │
│  │  FB Agent   │          │  IG Agent   │          │   X Agent   │   │
│  │  (Facebook) │          │(Instagram) │          │ (Twitter)   │   │
│  └──────┬──────┘          └──────┬──────┘          └──────┬──────┘   │
│         │                         │                         │            │
│  ┌──────┴──────┐          ┌──────┴──────┐          ┌──────┴──────┐   │
│  │ • Browser    │          │ • Browser    │          │ • Browser    │   │
│  │ • Nurture    │          │ • Nurture    │          │ • Nurture    │   │
│  │ • Publish    │          │ • Publish    │          │ • Publish    │   │
│  │ • Outreach   │          │ • Outreach   │          │ • Outreach   │   │
│  │ • Risk Ctrl │          │ • Risk Ctrl │          │ • Risk Ctrl │   │
│  └─────────────┘          └─────────────┘          └─────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    🧠 Memory System (记忆系统)                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │   │
│  │  │ Short-term  │  │ Long-term   │  │ RAG Knowledge Base      │ │   │
│  │  │ (Redis)    │  │ (Milvus)    │  │ (Vector DB)            │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    🛠️ Tools & Skills Layer                       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │   │
│  │  │ MCP Servers │  │ CLI Tools   │  │ Skills Registry        │ │   │
│  │  │ (Native)    │  │ (Browser)   │  │ (105 Skills)           │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.3 Agent职责矩阵

| Agent | 职责 | 核心能力 | 并行能力 |
|-------|------|---------|---------|
| **Master Agent** | 任务调度、平台路由、跨平台协调 | 任务分解、状态追踪、失败重试 | 最多5个平台任务并行 |
| **FB Browser Agent** | Profile管理、登录态维护 | 指纹隔离、Cookie管理 | 单账号操作 |
| **FB Nurture Agent** | 养号21-30天、社交图谱建立 | 行为模拟、Group渗透 | 最多20账号并行 |
| **FB Publish Agent** | Page/Group/Reels多形式发布 | 内容适配、数据采集 | 最多10账号并行 |
| **FB Outreach Agent** | Group引流、Messenger多轮对话 | 信任建立、WA转化 | 最多15账号并行 |
| **IG Browser Agent** | Profile管理、移动端模拟 | Meta共享体系 | 单账号操作 |
| **IG Nurture Agent** | 养号14-21天、关注互动 | Action Block应对 | 最多20账号并行 |
| **IG Publish Agent** | Reels/图文/Carousel/Story发布 | 多比例输出 | 最多10账号并行 |
| **IG Outreach Agent** | 关注→回关→DM→WA | DM限流应对 | 最多15账号并行 |
| **X Browser Agent** | Profile管理、API路线 | Cloudflare处理 | 单账号操作 |
| **X Nurture Agent** | 养号14天、文字社交 | 热推监控 | 最多30账号并行 |
| **X Publish Agent** | 推文/Thread/API发布 | API配额管理 | 最多20账号并行 |
| **X Outreach Agent** | 热推回复、引用推文、DM | 蹭热度引流 | 最多20账号并行 |

---

## 2. 数据库设计

### 2.1 核心表结构

```sql
-- 账号主表
CREATE TABLE `el_accounts` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `platform` ENUM('tk', 'fb', 'ig', 'x') NOT NULL,
    `username` VARCHAR(100) NOT NULL,
    `password_encrypted` VARCHAR(255) NOT NULL,
    `account_type` ENUM('content', 'outreach', 'backup') NOT NULL,
    `skill_type` VARCHAR(50) DEFAULT NULL,
    `status` ENUM('nurturing', 'active', 'action_block', 'shadow_ban', 'checkpoint', 'suspended', 'backup') NOT NULL DEFAULT 'nurturing',
    `health_score` TINYINT UNSIGNED DEFAULT 100,
    `proxy_ip` VARCHAR(50) DEFAULT NULL,
    `adspower_profile_id` VARCHAR(50) DEFAULT NULL,
    `last_active_time` DATETIME DEFAULT NULL,
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_platform_status` (`platform`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='账号主表';

-- 内容主表
CREATE TABLE `el_contents` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `platform` ENUM('tk', 'fb', 'ig', 'x') NOT NULL,
    `account_id` BIGINT UNSIGNED NOT NULL,
    `skill_type` VARCHAR(50) NOT NULL,
    `content_type` ENUM('video', 'post', 'reels', 'carousel', 'story', 'tweet', 'thread') NOT NULL,
    `script_text` TEXT,
    `caption` TEXT,
    `qc_status` ENUM('pending', 'passed', 'failed') DEFAULT 'pending',
    `platform_post_id` VARCHAR(100) DEFAULT NULL,
    `published_at` DATETIME DEFAULT NULL,
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_platform_account` (`platform`, `account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='内容主表';

-- Skill配置表
CREATE TABLE `el_skills` (
    `id` VARCHAR(50) NOT NULL COMMENT 'Skill ID',
    `category` ENUM('e_brand', 'g_outreach', 'fb_exclusive', 'ig_exclusive', 'x_exclusive') NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `platforms_supported` JSON,
    `publish_frequency` JSON,
    `is_active` TINYINT(1) DEFAULT 1,
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Skill配置表';

-- 引流事件表
CREATE TABLE `el_outreach_events` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `platform` ENUM('tk', 'fb', 'ig', 'x') NOT NULL,
    `account_id` BIGINT UNSIGNED NOT NULL,
    `event_type` ENUM('follow', 'dm_sent', 'dm_reply', 'comment', 'hot_reply') NOT NULL,
    `target_username` VARCHAR(100) DEFAULT NULL,
    `message_content` TEXT,
    `wa_click` TINYINT(1) DEFAULT 0,
    `event_time` DATETIME NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_platform_account` (`platform`, `account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='引流事件表';

-- 风控事件表
CREATE TABLE `el_risk_events` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `platform` ENUM('tk', 'fb', 'ig', 'x') NOT NULL,
    `account_id` BIGINT UNSIGNED NOT NULL,
    `event_type` ENUM('action_block', 'shadow_ban', 'checkpoint', 'suspended', 'rate_limit') NOT NULL,
    `severity` ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    `detail` JSON,
    `resolved` TINYINT(1) DEFAULT 0,
    `event_time` DATETIME NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_platform_account` (`platform`, `account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='风控事件表';

-- 操作日志表
CREATE TABLE `el_operation_logs` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `platform` ENUM('tk', 'fb', 'ig', 'x') DEFAULT NULL,
    `account_id` BIGINT UNSIGNED DEFAULT NULL,
    `agent_name` VARCHAR(50) NOT NULL,
    `operation_type` VARCHAR(50) NOT NULL,
    `operation_detail` JSON,
    `result` ENUM('success', 'failed', 'partial') DEFAULT 'success',
    `execution_time_ms` INT UNSIGNED DEFAULT NULL,
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_agent_operation` (`agent_name`, `operation_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';
```

---

## 3. 硬件设备设计

### 3.1 服务器配置

| 服务器 | 角色 | CPU | 内存 | 硬盘 | 数量 |
|--------|------|-----|------|------|------|
| **Server 1** | 主控节点 + PostgreSQL | 8核 | 16GB | 500GB SSD | 1台 |
| **Server 2** | Agent执行节点 | 16核 | 32GB | 1TB SSD | 1台 |
| **Server 3** | 向量数据库 + 缓存 | 8核 | 16GB | 500GB SSD | 1台 |
| **Client PC** | 浏览器自动化节点 | 6核 | 12GB | 256GB SSD | 按需 |

### 3.2 代理IP配置

| 平台 | IP类型 | 数量 | 轮换策略 |
|------|--------|------|---------|
| Facebook | **必须住宅IP** | 150个 | 固定IP |
| Instagram | **推荐住宅IP** | 120个 | 固定IP |
| Twitter | 机房IP可用 | 80个 | 固定IP |

---

## 4. API接口清单

| 模块 | 端点 | 方法 | 说明 |
|------|------|------|------|
| Agent | `/api/v1/agents` | POST | 创建Agent任务 |
| Agent | `/api/v1/agents/{task_id}` | GET | 查询任务进度 |
| 账号 | `/api/v1/accounts` | GET/POST | 账号列表/创建 |
| 账号 | `/api/v1/accounts/{id}/status` | PUT | 更新账号状态 |
| 内容 | `/api/v1/contents` | GET/POST | 内容列表/创建 |
| 内容 | `/api/v1/contents/{id}/metrics` | GET | 获取效果数据 |
| 引流 | `/api/v1/outreach/stats` | GET | 引流漏斗统计 |
| 风控 | `/api/v1/risk/events` | GET/POST | 风控事件 |
| 风控 | `/api/v1/risk/health-score` | GET | 矩阵健康评分 |
| Skill | `/api/v1/skills` | GET | Skill列表 |
| Skill | `/api/v1/skills/{id}` | GET/PUT | Skill详情/更新 |
| 看板 | `/api/v1/dashboard/overview` | GET | 总览数据 |

---

## 5. 我们需要提前准备什么

### 5.1 账号资源

| 平台 | 数量 | 状态 | 说明 |
|------|------|------|------|
| Facebook | 150个 | ❌ 需采购 | 80内容+50引流+20备用 |
| Instagram | 120个 | ❌ 需采购 | 60内容+40引流+20备用 |
| Twitter | 80个 | ❌ 需采购 | 30内容+30引流+20备用 |

### 5.2 代理IP

| 平台 | IP类型 | 供应商 | 状态 |
|------|--------|--------|------|
| FB/IG | 住宅IP | ipipgo | ✅ 已确定 |
| X | 机房IP | ipipgo | ✅ 已确定 |

### 5.3 软件授权

| 软件 | 用途 | 成本 |
|------|------|------|
| AdsPower指纹浏览器 | 多账号管理 | ¥100/月 |
| X API Basic Plan | Twitter API发布 | $100/月 |

---

## 6. 交付标准归纳

| 模块 | 交付标准 | 验收方法 |
|------|---------|---------|
| Agent系统 | 26个Agent模块正常运行 | 单元测试>95% |
| 数据库 | 15+核心表结构完整 | SQL脚本执行无错误 |
| API接口 | 50+ RESTful API | API测试通过 |
| 记忆系统 | Milvus + Redis双写 | 检索延迟<100ms |
| RAG知识库 | 105个Skill文档向量化 | 召回率>85% |
| Skills | 105个Skill可配置 | 配置加载正常 |

---

## 7. 技术栈架构设计

### 7.1 依赖版本

```
python==3.12.0
fastapi==0.109.0
langchain==1.0.4
langgraph==1.0.2
langchain-community==0.4.0
pymilvus==2.4.0
redis==5.0.0
playwright==1.41.0
asyncpg==0.29.0
```

### 7.2 项目结构

```
E:\PY\server\
├── app/
│   ├── api/v1/           # API层
│   ├── agent/           # Agent核心
│   │   ├── core/        # ReAct/PlanAndSolve/Reflection
│   │   ├── platforms/   # 平台Agent
│   │   ├── memory/      # 记忆系统
│   │   └── skills/     # Skills系统
│   ├── models/         # 数据模型
│   ├── schemas/        # Pydantic schemas
│   └── services/      # 业务逻辑
├── migrations/         # 数据库迁移
├── skills/            # Skills配置 (105个)
├── knowledge/        # RAG知识库
└── tests/            # 测试
```

---

## 8. Agent提示词设计

### 8.1 Master Agent提示词

```
# Master Agent - 任务调度专家

## 角色
多平台社交媒体运营系统的总调度Agent，负责协调Facebook、Instagram、Twitter三个平台。

## 调度规则
| 任务类型 | 对应Agent | 并发限制 |
|---------|----------|---------|
| browser | {platform}_browser_agent | 1账号 |
| nurture | {platform}_nurture_agent | 20账号 |
| publish | {platform}_publish_agent | 10账号 |
| outreach | {platform}_outreach_agent | 15账号 |

## 时间窗口
- 养号: 07:00-22:00
- 发布: 10:00-23:00
- 引流: 09:00-22:00
```

### 8.2 Platform Agent提示词

**FB Publish Agent**:
- 多形式内容: Page帖/Group帖/Reels/Story
- 长文支持 (200-500字符)
- Checkpoint验证频率高
- Link Preview支持

**IG Publish Agent**:
- 移动端模拟(90%用户)
- Action Block限制严
- Carousel最多10张
- Hashtag 20-30个

---

## 9. Copilot边与节点状态设计

### 9.1 节点状态

| 状态 | 说明 |
|------|------|
| PENDING | 等待执行 |
| RUNNING | 执行中 |
| COMPLETED | 已完成 |
| FAILED | 失败 |
| WAITING | 等待资源 |
| BLOCKED | 被阻塞 |

### 9.2 核心节点

```
[route_task] → [schedule_task] → [init_account]
                                        ↓
                              [check_health]
                                        ↓
                    ┌───────────────────┴───────────────────┐
                    ↓                                       ↓
              [nurture_profile]                        [publish]
                    ↓                                       ↓
              [nurture_social]                      [qc_content]
                    ↓                                       ↓
              [nurture_content]              ┌──────────┴──────────┐
                    ↓                          ↓                      ↓
              [update_memory]           [prepare]              [publish]
                    ↓                          ↓                      ↓
                   END                   [collect_metrics]         ↓
                                            ↓                      ↓
                                        [reflect] ←←←←←←←←←←←←←←←←←

```

---

## 10. ReAct设计

### 10.1 核心循环

```
Thought → Action → Observation → Thought → Action → ...
```

### 10.2 工具示例

- `search_content(query, platform)` - 搜索内容
- `generate_script(topic, skill_type)` - 生成脚本
- `publish_content(content, account_id)` - 发布内容
- `check_account_health(account_id)` - 检查账号健康
- `update_memory(key, value)` - 更新记忆

---

## 11. Plan-and-Solve设计

### 11.1 执行流程

```
1. PLAN: 分解任务为具体步骤
2. EXECUTE: 按依赖关系执行步骤
3. REFLECT: 评估执行结果
4. REPLAN: 如需要调整计划
```

### 11.2 与ReAct对比

| 维度 | ReAct | Plan-and-Solve |
|------|-------|----------------|
| 适用场景 | 简单任务 | 复杂任务 |
| 执行模式 | 边想边做 | 先想后做 |
| 回退能力 | 弱 | 强 |

---

## 12. Reflection设计

### 12.1 反思维度

1. **目标达成度** - 任务是否成功完成?
2. **执行效率** - 资源使用是否合理?
3. **质量评估** - 输出质量如何?
4. **问题识别** - 发现了哪些问题?
5. **改进建议** - 如何在下一次做得更好?

---

## 13. RAG 知识库架构设计

### 13.1 Collections

| Collection | 内容 | 用途 |
|------------|------|------|
| `platform_guides` | 官方文档+运营经验 | 平台操作指引 |
| `skill_docs` | 105个Skill配置 | 内容生成参考 |
| `best_practices` | 历史成功案例 | 运营策略优化 |
| `risk_patterns` | 风控事件记录 | 风险识别预防 |

### 13.2 检索流程

```
Query → Embedding → Vector Search → Rerank → Context Assembly → LLM
```

---

## 14. 长期记忆设计

### 14.1 记忆类型

| 类型 | 说明 |
|------|------|
| **SEMANTIC** | 语义记忆 - 事实和概念 |
| **EPISODIC** | 情景记忆 - 具体事件和经历 |
| **PROCEDURAL** | 程序记忆 - 技能和流程 |

### 14.2 整合策略

- 重要性阈值: 0.7
- 记忆衰减率: 0.99
- 最大条目: 10000

---

## 15. 短期记忆设计

### 15.1 Redis存储结构

```
Session Buffer: messages, context, state
Working Memory: 当前任务上下文
Execution Trace: 已执行步骤、工具调用历史
```

### 15.2 TTL配置

- Session: 24小时
- Trace: 1小时

---

## 16. 工具MCP与CLI工具设计

### 16.1 工具分类

| 类型 | 示例 |
|------|------|
| Native | Database, FileSystem |
| MCP | Facebook, Instagram, Twitter |
| CLI | AdsPower, ffmpeg, ImageMagick |

### 16.2 MCP工具示例

**Facebook MCP**:
- `fb_login(account_id)` - 登录
- `fb_post_page(account_id, page_id, content)` - Page发帖
- `fb_post_group(account_id, group_id, content)` - Group发帖
- `fb_send_message(account_id, recipient_id, message)` - 发私信
- `fb_get_post_metrics(account_id, post_id)` - 获取数据

---

## 17. Skills技能调用工具架构设计

### 17.1 Skill结构

```
skills/{SKILL-ID}/
├── SKILL.md           # Skill说明
├── config.json        # 配置参数
├── templates/         # 模板库
├── prompts/          # 生成Prompt
└── validators/       # 质检规则
```

### 17.2 Skill执行流程

```
1. 加载Skill配置
2. 生成内容 (Script/Caption/Hashtags)
3. 质量检查
4. 返回结果
```

### 17.3 105个Skill分类

| 分类 | 数量 | 说明 |
|------|------|------|
| E系列 (品牌号) | 9个 | 盲盒开箱、零食测评等 |
| G系列 (引流号) | 14个 | 美食、美妆、穿搭等 |
| 平台专属 | 10个 | FB/IG/X各有专属 |
| 适配引擎 | 3个 | 平台适配层 |

---

## 附录: 项目里程碑

| 阶段 | 时间 | 交付内容 |
|------|------|---------|
| Phase 1 | W1-W4 | FB平台核心功能 |
| Phase 2 | W5-W8 | IG平台扩展 |
| Phase 3 | W9-W12 | X平台扩展 |
| Phase 4 | W13-W16 | 跨平台联调 |
| Phase 5 | W17-W20 | 优化与正式运营 |

---

*文档版本: v1.0*
*最后更新: 2026-04-06*
