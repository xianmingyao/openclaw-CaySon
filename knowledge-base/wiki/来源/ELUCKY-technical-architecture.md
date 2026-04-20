# ELUCKY 多平台Agent体系 — 技术架构设计文档

> **版本：** v1.0
> **日期：** 2026-04-03
> **项目：** ELUCKY 多平台社交媒体矩阵运营系统

---

## 1. 项目概述

### 1.1 项目背景

ELUCKY是一个面向印尼市场的多平台社交媒体矩阵运营系统，支持TikTok、Facebook、Instagram、Twitter(X)四个平台的自动化内容发布、账号养号、引流转化。

### 1.2 项目规模

| 维度 | 数量 |
|------|------|
| **平台数量** | 4个（TK/FB/IG/X） |
| **账号总数** | 580个 |
| **Agent模块** | 26个 |
| **Skill模块** | 105个 |
| **日均内容产出** | 约1,330条 |
| **月运营成本** | 约$6,938 |

### 1.3 账号分布

| 平台 | 内容号 | 引流号 | 备用号 | 合计 |
|------|--------|--------|--------|------|
| TikTok | 100 | 100 | 30 | 230 |
| Facebook | 80 | 50 | 20 | 150 |
| Instagram | 60 | 40 | 20 | 120 |
| Twitter(X) | 30 | 30 | 20 | 80 |
| **合计** | **270** | **220** | **90** | **580** |

---

## 2. 技术栈选型

### 2.1 核心技术栈

| 层级 | 技术选型 | 选型理由 |
|------|---------|---------|
| **后端主语言** | Python 3.10+ | Agent开发主流语言，生态丰富 |
| **Agent编排** | LangGraph | Agent流程编排首选，支持状态机 |
| **任务队列** | Redis + RQ | 轻量级任务队列，支持分布式 |
| **关系数据库** | PostgreSQL 15 | 稳定可靠，支持JSONB |
| **时序数据库** | ClickHouse | 高效处理时序数据 |
| **缓存层** | Redis 7 | 操作计数、会话缓存 |
| **浏览器自动化** | Playwright | 跨平台，支持指纹模拟 |
| **指纹浏览器** | AdsPower API | 成熟的多账号指纹管理 |
| **LLM调用** | Grok API | 脚本生成、评论生成 |
| **图像生成** | Grok-2-image | 封面图、配图生成 |
| **视频合成** | Kling 1.6 | 视频生成 |
| **部署** | Docker + Docker Compose | 容器化部署 |

### 2.2 为什么选择这个技术栈

#### Python + LangGraph

**优势：**
- Python是AI/Agent领域的事实标准
- LangGraph是LangChain团队出品，专为复杂Agent流程设计
- 支持状态机、循环、条件分支
- 与LangChain生态完美兼容

**替代方案对比：**

| 方案 | 优点 | 缺点 |
|------|------|------|
| **Python + LangGraph（选）** | 生态最全，调试方便 | 性能略低于Go |
| Go + 自研Agent框架 | 性能高 | 生态弱，轮子少 |
| Node.js | 前端友好 | AI生态弱 |
| LangChain alone | 简单场景够用 | 复杂流程难维护 |

#### PostgreSQL + ClickHouse

**为什么不用单一数据库：**

| 数据库 | 适用场景 | 不适用场景 |
|--------|---------|-----------|
| **PostgreSQL（选）** | 账号/内容/配置 | 海量时序数据 |
| **ClickHouse（选）** | 播放量/互动等时序 | 高并发写入 |
| MongoDB | 文档存储 | 关联查询 |
| MySQL | 简单CRUD | 复杂查询 |

**数据分离策略：**
- PostgreSQL：账号域、内容域、引流域、风控域、配置域
- ClickHouse：效果域（content_metrics时序数据）

#### Playwright vs Selenium vs Puppeteer

| 框架 | 跨平台 | 指纹支持 | 速度 | 选型 |
|------|--------|---------|------|------|
| **Playwright（选）** | ✅ | ✅ | 快 | 跨平台首选 |
| Selenium | ✅ | ⚠️ | 慢 | 老牌，稳定 |
| Puppeteer | ❌ | ⚠️ | 快 | 仅Chrome |

### 2.3 技术栈全景图

```
┌─────────────────────────────────────────────────────────────┐
│                      接入层                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ Web管理后台│  │ API接口 │  │ 定时任务 │  │ 运营客户端│   │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘   │
└───────┼────────────┼─────────┼─────────┼───────────────┘
        │            │         │         │
        ▼            ▼         ▼         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Agent编排层                              │
│  ┌─────────────────────────────────────────────────┐    │
│  │              LangGraph Agent Orchestrator            │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │    │
│  │  │ 主控Agent│ │ 脚本Agent│ │ 视频Agent│ │ 质检Agent│ │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │    │
│  │  │BrowserAgent│NurtureAgent│PublishAgent│OutreachAgent││    │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ │    │
│  │  ┌─────────┐ ┌─────────┐                          │    │
│  │  │ 风控Agent │ │ 调度Agent │                          │    │
│  │  └─────────┘ └─────────┘                          │    │
│  └─────────────────────────────────────────────────┘    │
└───────────────────────────┬─────────────────────────────┘
                              │
┌───────────────────────────┼─────────────────────────────┐
│                    模型服务层                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ Grok-3     │  │Grok-2-image│  │ Kling 1.6 │       │
│  │ 脚本/评论  │  │ 封面/配图   │  │ 视频合成   │       │
│  └────────────┘  └────────────┘  └────────────┘       │
└───────────────────────────┬─────────────────────────────┘
                              │
┌───────────────────────────┼─────────────────────────────┐
│                    执行层                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ Playwright │  │ AdsPower   │  │ 平台API    │       │
│  │ 浏览器自动化│  │ 指纹管理   │  │ X API等    │       │
│  └────────────┘  └────────────┘  └────────────┘       │
└───────────────────────────┬─────────────────────────────┘
                              │
┌───────────────────────────┼─────────────────────────────┐
│                    数据层                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ PostgreSQL │  │ ClickHouse │  │   Redis    │       │
│  │ 主库       │  │ 时序分析   │  │ 缓存/队列  │       │
│  └────────────┘  └────────────┘  └────────────┘       │
└───────────────────────────────────────────────────────┘
```

---

## 3. 系统架构设计

### 3.1 整体架构

```
ELUCKY 多平台Agent体系
│
├── 🖥️ Web管理后台（Flask/React）
│   ├── 账号管理
│   ├── 内容管理
│   ├── 数据看板
│   └── 系统配置
│
├── 📦 API服务（FastAPI）
│   ├── Agent调度API
│   ├── 内容API
│   ├── 账号API
│   └── 数据API
│
├── 🤖 Agent执行层（LangGraph）
│   ├── 主控Agent（任务编排）
│   ├── 脚本Agent（内容生成）
│   ├── 视频Agent（媒体处理）
│   ├── 质检Agent（合规检查）
│   ├── 浏览器Agent（平台操作）
│   ├── 养号Agent（账号维护）
│   ├── 发布Agent（内容发布）
│   ├── 引流Agent（转化承接）
│   └── 风控Agent（风险监控）
│
├── 🔧 执行器
│   ├── Playwright（浏览器自动化）
│   ├── AdsPower API（指纹管理）
│   └── 平台官方API
│
└── 💾 数据层
    ├── PostgreSQL（主库）
    ├── ClickHouse（分析库）
    └── Redis（缓存/队列）
```

### 3.2 Agent体系架构

#### 3.2.1 核心Agent设计

```
Agent体系（26个模块）
│
├── 🔰 主控Agent（1个）
│   └── 任务调度、跨平台协调
│
├── 📝 内容Agent（4个）
│   ├── 脚本Agent（TK/FB/IG/X）
│   ├── 视频Agent
│   ├── 图片Agent
│   └── 质检Agent
│
├── 🌐 平台Agent（12个 = 4平台×3Agent）
│   │
│   ├── TikTok
│   │   ├── TK-Browser
│   │   ├── TK-Nurture
│   │   └── TK-Publish + TK-Outreach
│   │
│   ├── Facebook
│   │   ├── FB-Browser
│   │   ├── FB-Nurture
│   │   └── FB-Publish + FB-Outreach
│   │
│   ├── Instagram
│   │   ├── IG-Browser
│   │   ├── IG-Nurture
│   │   └── IG-Publish + IG-Outreach
│   │
│   └── Twitter(X)
│       ├── X-Browser
│       ├── X-Nurture
│       └── X-Publish + X-Outreach
│
└── 🛡️ 风控Agent（1个）
    └── 健康评分、连坐监控、应急处理
```

#### 3.2.2 Agent状态机

```
                    ┌──────────────┐
                    │   IDLE      │
                    │   空闲      │
                    └──────┬─────┘
                           │ 领取任务
                           ▼
                    ┌──────────────┐
              ┌─────▶│  RUNNING    │◀────┐
              │      │   运行中    │     │
              │      └──────┬─────┘     │
              │             │           │
        任务完成      任务失败      超时/异常
              │             │           │
              ▼             ▼           ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │ COMPLETED │  │  FAILED  │  │ RETRYING  │
       │   完成    │  │   失败    │  │  重试中   │
       └──────────┘  └──────────┘  └──────────┘
```

### 3.3 数据流设计

```
数据流架构

                    用户需求输入
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│                    任务入口层                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ 定时调度 │  │ API触发  │  │ 手动触发  │         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
└───────┼────────────┼─────────┼─────────┼──────────────┘
        │            │         │         │
        └────────────┴────┬─────┴─────────┘
                         ▼
┌────────────────────────────────────────────────────────┐
│                    Agent执行层                           │
│                                                         │
│  脚本Agent ──▶ 媒体Agent ──▶ 质检Agent ──▶ 发布Agent │
│       │                                    │          │
│       │         ┌─────────────────────────┘          │
│       │         │                                      │
│       ▼         ▼                                      │
│  ┌─────────────────────────────────────────────┐      │
│  │              风控Agent（全程监控）              │      │
│  └─────────────────────────────────────────────┘      │
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│                    数据持久层                            │
│                                                         │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐  │
│  │ PostgreSQL │    │ ClickHouse │    │   Redis    │  │
│  │  结构化    │    │   时序     │    │   缓存     │  │
│  └────────────┘    └────────────┘    └────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## 4. 代码目录结构

### 4.1 整体目录

```
elucky/
├── 📁 src/
│   ├── 📁 agents/                    # Agent模块
│   │   ├── 📁 core/                  # 核心Agent
│   │   │   │   ├── __init__.py
│   │   │   │   ├── master_agent.py   # 主控Agent
│   │   │   │   ├── script_agent.py  # 脚本Agent
│   │   │   │   ├── video_agent.py   # 视频Agent
│   │   │   │   ├── image_agent.py   # 图片Agent
│   │   │   │   └── qc_agent.py      # 质检Agent
│   │   │
│   │   ├── 📁 platform/             # 平台Agent
│   │   │   ├── 📁 tiktok/
│   │   │   │   ├── browser.py
│   │   │   │   ├── nurture.py
│   │   │   │   ├── publish.py
│   │   │   │   └── outreach.py
│   │   │   ├── 📁 facebook/
│   │   │   ├── 📁 instagram/
│   │   │   └── 📁 twitter/
│   │   │
│   │   └── 📁 risk/
│   │       ├── risk_agent.py        # 风控Agent
│   │       ├── health_score.py      # 健康评分
│   │       └── cascade_monitor.py   # 连坐监控
│   │
│   ├── 📁 services/                  # 服务层
│   │   │   ├── __init__.py
│   │   │   ├── browser_service.py    # 浏览器服务
│   │   │   ├── adspower_service.py  # AdsPower服务
│   │   │   ├── llm_service.py       # LLM调用服务
│   │   │   ├── video_service.py     # 视频服务
│   │   │   ├── storage_service.py    # 存储服务
│   │   │   └── notification_service.py  # 通知服务
│   │
│   ├── 📁 models/                  # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── account.py
│   │   │   ├── content.py
│   │   │   ├── metrics.py
│   │   │   ├── outreach.py
│   │   │   └── risk_event.py
│   │
│   ├── 📁 schemas/                 # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── account.py
│   │   │   ├── content.py
│   │   │   └── task.py
│   │
│   ├── 📁 repositories/            # 数据访问层
│   │   │   ├── __init__.py
│   │   │   ├── account_repo.py
│   │   │   ├── content_repo.py
│   │   │   └── metrics_repo.py
│   │
│   ├── 📁 skills/                 # Skill模块（105个）
│   │   │   ├── __init__.py
│   │   │   ├── E_BOX_OPEN.py
│   │   │   ├── E_SNACK_REVIEW.py
│   │   │   ├── G_FOOD.py
│   │   │   └── ... (105个Skill)
│   │   │
│   │   └── 📁 adapters/           # 适配层引擎
│   │       ├── base_adapter.py
│   │       ├── fb_adapter.py
│   │       ├── ig_adapter.py
│   │       └── x_adapter.py
│   │
│   ├── 📁 api/                    # API层
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── accounts.py
│   │   │   │   ├── contents.py
│   │   │   │   ├── tasks.py
│   │   │   │   └── metrics.py
│   │   │   └── middleware/
│   │   │
│   │   └── main.py                # FastAPI入口
│   │
│   ├── 📁 core/                   # 核心配置
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # 配置管理
│   │   │   ├── database.py         # 数据库连接
│   │   │   └── security.py        # 安全加密
│   │
│   └── 📁 utils/                  # 工具函数
│       │   ├── __init__.py
│       │   ├── logger.py
│       │   ├── encrypt.py         # 加密工具
│       │   └── platform_utils.py  # 平台工具
│
├── 📁 scripts/                    # 脚本
│   │   ├── init_db.py            # 初始化数据库
│   │   ├── seed_data.py          # 种子数据
│   │   └── test_pipeline.py     # 测试管道
│
├── 📁 tests/                     # 测试
│   │   ├── 📁 unit/
│   │   ├── 📁 integration/
│   │   └── 📁 e2e/
│
├── 📁 configs/                   # 配置文件
│   │   ├── platforms.yaml        # 平台配置
│   │   ├── skills.yaml          # Skill配置
│   │   └── limits.yaml          # 限制配置
│
├── 📁 docker/                    # Docker配置
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── nginx.conf
│
├── 📁 docs/                      # 文档
│
├── 📁 logs/                      # 日志
│
├── 📁 data/                      # 数据文件
│   ├── scripts/                  # 脚本模板
│   ├── prompts/                  # Prompt模板
│   └── templates/                # 内容模板
│
├── pyproject.toml
├── poetry.lock
├── .env.example
└── README.md
```

### 4.2 Agent核心代码示例

```python
# src/agents/core/master_agent.py
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from typing import Optional, List, Dict
from .script_agent import ScriptAgent
from .video_agent import VideoAgent
from .qc_agent import QCAgent

class MasterAgentState(BaseModel):
    task_id: str
    platform: str  # tk/fb/ig/x
    skill_type: str
    status: str = "idle"  # idle/running/completed/failed
    script_text: Optional[str] = None
    media_url: Optional[str] = None
    qc_result: Optional[Dict] = None
    error: Optional[str] = None

class MasterAgent:
    """主控Agent - 任务编排入口"""

    def __init__(self):
        self.script_agent = ScriptAgent()
        self.video_agent = VideoAgent()
        self.qc_agent = QCAgent()

    def create_graph(self) -> StateGraph:
        workflow = StateGraph(MasterAgentState)

        # 添加节点
        workflow.add_node("generate_script", self.generate_script)
        workflow.add_node("generate_media", self.generate_media)
        workflow.add_node("quality_check", self.quality_check)
        workflow.add_node("handle_failure", self.handle_failure)

        # 设置边
        workflow.set_entry_point("generate_script")
        workflow.add_edge("generate_script", "generate_media")
        workflow.add_edge("generate_media", "quality_check")
        workflow.add_conditional_edges(
            "quality_check",
            self.should_retry,
            {
                "retry": "generate_script",
                "publish": END,
                "fail": "handle_failure"
            }
        )
        workflow.add_edge("handle_failure", END)

        return workflow.compile()

    async def generate_script(self, state: MasterAgentState) -> MasterAgentState:
        """调用脚本Agent生成内容"""
        script = await self.script_agent.generate(
            platform=state.platform,
            skill_type=state.skill_type
        )
        return {**state, "script_text": script}

    async def generate_media(self, state: MasterAgentState) -> MasterAgentState:
        """调用视频Agent生成媒体"""
        media_url = await self.video_agent.generate(
            script=state.script_text,
            platform=state.platform
        )
        return {**state, "media_url": media_url}

    async def quality_check(self, state: MasterAgentState) -> MasterAgentState:
        """调用质检Agent检查内容"""
        result = await self.qc_agent.check(
            media_url=state.media_url,
            platform=state.platform
        )
        return {**state, "qc_result": result}

    def should_retry(self, state: MasterAgentState) -> str:
        """判断是否重试"""
        if state.qc_result.get("passed"):
            return "publish"
        elif state.qc_result.get("retry_count", 0) < 3:
            return "retry"
        return "fail"
```

### 4.3 Skill代码结构

```python
# src/skills/E_BOX_OPEN.py
from typing import Dict, List, Optional
from ..adapters.base_adapter import BaseAdapter

class EBoxOpenSkill:
    """盲盒开箱Skill"""

    SKILL_ID = "E-BOX-OPEN"
    PLATFORMS = ["tk", "fb", "ig", "x"]
    CONTENT_TYPE = "video"

    def __init__(self, adapter: BaseAdapter):
        self.adapter = adapter

    def generate_script(self, context: Dict) -> str:
        """生成盲盒开箱脚本"""
        prompt = f"""
生成一个印尼语盲盒开箱视频脚本。

要求：
1. 时长：15-60秒
2. 风格：制造悬念和惊喜感
3. 结构：
   - 开头：吸引眼球，问"你们猜里面是什么？"
   - 中间：打开过程，逐步展示
   - 结尾：惊喜展示，CTA引导互动
4. 语言：印尼语（id-ID）
5. 格式：{script_format}

请生成完整的视频脚本。
"""
        return self.adapter.call_llm(prompt)

    def adapt_for_platform(self, script: str, platform: str) -> Dict:
        """适配到不同平台"""
        adapters = {
            "tk": self._adapt_tk,
            "fb": self._adapt_fb,
            "ig": self._adapt_ig,
            "x": self._adapt_x,
        }
        return adapters[platform](script)

    def _adapt_tk(self, script: str) -> Dict:
        return {
            "caption": script[:100] + "...",
            "hashtags": ["#blindbox", "#surprise", "#fyp"],
            "ratio": "9:16"
        }

    def _adapt_fb(self, script: str) -> Dict:
        return {
            "caption": script + "\n\n感兴趣？加WA咨询更多！",
            "hashtags": [],
            "cta": "消息"
        }

    def _adapt_ig(self, script: str) -> Dict:
        return {
            "caption": script,
            "hashtags": self._generate_ig_hashtags(),
            "carousel": True
        }

    def _adapt_x(self, script: str) -> Dict:
        return {
            "tweet": script[:280],
            "hashtags": ["#blindbox"]
        }
```

---

## 5. 数据库设计

### 5.1 PostgreSQL核心表

```sql
-- 账号表
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(10) NOT NULL,  -- tk/fb/ig/x
    username VARCHAR(255) NOT NULL,
    password_encrypted TEXT NOT NULL,  -- AES-256加密
    email VARCHAR(255),
    phone VARCHAR(50),
    account_type VARCHAR(20) NOT NULL,  -- content/outreach/backup
    batch_id VARCHAR(50),
    skill_type VARCHAR(50),
    status VARCHAR(30) DEFAULT 'idle',
    health_score INTEGER DEFAULT 100,
    nurture_start_date DATE,
    nurture_end_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(platform, username)
);

-- 账号环境配置表
CREATE TABLE account_profiles (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    adspower_profile_id VARCHAR(100),
    proxy_host VARCHAR(100),
    proxy_port INTEGER,
    proxy_user VARCHAR(100),
    proxy_password_encrypted TEXT,
    proxy_type VARCHAR(20),  -- residential/datacenter
    fingerprint_config JSONB,
    mobile_emulation BOOLEAN DEFAULT FALSE,
    cookie_data TEXT,
    session_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 每日操作计数表
CREATE TABLE account_daily_ops (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    date DATE NOT NULL,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    follows_count INTEGER DEFAULT 0,
    unfollows_count INTEGER DEFAULT 0,
    dms_sent INTEGER DEFAULT 0,
    posts_count INTEGER DEFAULT 0,
    stories_count INTEGER DEFAULT 0,
    friend_requests_count INTEGER DEFAULT 0,  -- FB专用
    group_posts_count INTEGER DEFAULT 0,       -- FB专用
    UNIQUE(account_id, date)
);

-- 账号状态变更日志表
CREATE TABLE account_status_log (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    old_status VARCHAR(30),
    new_status VARCHAR(30),
    reason TEXT,
    platform_error_code VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 内容表
CREATE TABLE contents (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(10) NOT NULL,
    account_id INTEGER REFERENCES accounts(id),
    skill_type VARCHAR(50),
    batch_id VARCHAR(50),
    content_type VARCHAR(30) NOT NULL,  -- video/post/reels/carousel/story/tweet/thread
    script_text TEXT,
    caption TEXT,
    hashtags TEXT[],
    media_urls JSONB,
    media_ratio VARCHAR(10),
    carousel_pages INTEGER,
    thread_count INTEGER,
    qc_status VARCHAR(20) DEFAULT 'pending',
    qc_score INTEGER,
    qc_fail_reason TEXT,
    platform_post_id VARCHAR(255),
    published_at TIMESTAMP,
    scheduled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 风控事件表
CREATE TABLE risk_events (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(10) NOT NULL,
    account_id INTEGER REFERENCES accounts(id),
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    detail JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 连坐事件表
CREATE TABLE cascade_events (
    id SERIAL PRIMARY KEY,
    trigger_account_id INTEGER,
    affected_account_ids INTEGER[],
    link_type VARCHAR(30),  -- same_ip/same_device/same_meta_id
    platform VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

-- IP信誉表
CREATE TABLE ip_reputation (
    ip_address VARCHAR(100) PRIMARY KEY,
    reputation_score INTEGER DEFAULT 100,
    platforms_used_on TEXT[],
    accounts_using INTEGER[],
    blacklisted BOOLEAN DEFAULT FALSE,
    last_checked_at TIMESTAMP DEFAULT NOW()
);

-- Meta关联表（FB-IG连坐）
CREATE TABLE meta_links (
    id SERIAL PRIMARY KEY,
    fb_account_id INTEGER,
    ig_account_id INTEGER,
    shared_meta_id BOOLEAN DEFAULT FALSE,
    link_risk_level VARCHAR(20) DEFAULT 'safe',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Skills配置表
CREATE TABLE skills (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(30),
    platforms_supported TEXT[],
    keyword_library JSONB,
    hashtag_library JSONB,
    template_library JSONB,
    config JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 平台限制表
CREATE TABLE platform_limits (
    platform VARCHAR(10) NOT NULL,
    operation_type VARCHAR(30) NOT NULL,
    account_age VARCHAR(10) NOT NULL,  -- new/mature
    daily_limit INTEGER,
    hourly_limit INTEGER,
    cooldown_seconds INTEGER,
    PRIMARY KEY(platform, operation_type, account_age)
);
```

### 5.2 ClickHouse时序表

```sql
-- 效果指标表（ClickHouse）
CREATE TABLE content_metrics (
    content_id UInt32,
    platform String,
    collected_at DateTime,
    views UInt32,
    plays UInt32,
    completion_rate Float32,
    likes UInt32,
    comments UInt32,
    shares UInt32,
    saves UInt32,
    reach UInt32,
    impressions UInt32,
    profile_visits UInt32,
    bio_link_clicks UInt32,
    cta_clicks UInt32,
    source_distribution JSON
) ENGINE = MergeTree()
ORDER BY (content_id, collected_at)
PARTITION BY toYYYYMM(collected_at);

-- 引流漏斗表
CREATE TABLE outreach_funnel (
    date Date,
    platform String,
    account_id UInt32,
    skill_type String,
    funnel_path String,
    actions_count UInt32,
    wa_clicks UInt32,
    wa_adds UInt32,
    registrations UInt32,
    conversion_rate Float32
) ENGINE = SummingMergeTree()
ORDER BY (date, platform, account_id);
```

---

## 6. API设计

### 6.1 核心API端点

```yaml
# API设计（OpenAPI格式）

paths:
  /api/v1/tasks:
    post:
      summary: 创建任务
      body:
        platform: tk
        skill_type: E-BOX-OPEN
        account_ids: [1, 2, 3]
        schedule_at: "2026-04-03T10:00:00Z"
      responses:
        201:
          body:
            task_id: "task_123"
            status: "queued"

  /api/v1/accounts:
    get:
      summary: 获取账号列表
      params:
        platform: tk
        status: active
        page: 1
        page_size: 20
      responses:
        200:
          body:
            total: 230
            accounts: [...]

    post:
      summary: 创建账号
      body:
        platform: fb
        username: "test_account"
        password: "xxx"
        account_type: content
        skill_type: E-BOX-OPEN

  /api/v1/accounts/{id}/status:
    put:
      summary: 更新账号状态
      body:
        status: action_block
        reason: "DM限流"

  /api/v1/contents:
    get:
      summary: 获取内容列表
      params:
        platform: tk
        qc_status: passed
        start_date: "2026-04-01"
        end_date: "2026-04-03"

  /api/v1/metrics/summary:
    get:
      summary: 获取数据汇总
      params:
        platform: tk
        date_range: last_7_days
      responses:
        200:
          body:
            total_posts: 1250
            avg_views: 8500
            total_wa_adds: 320
            conversion_rate: 0.056

  /api/v1/risk/events:
    get:
      summary: 获取风控事件
      params:
        severity: high
        resolved: false

  /api/v1/health:
    get:
      summary: 系统健康检查
      responses:
        200:
          body:
            status: healthy
            accounts_active: 450
            tasks_running: 12
            redis_connected: true
```

---

## 7. 部署架构

### 7.1 Docker Compose 配置

```yaml
# docker/docker-compose.yml

version: '3.8'

services:
  # API服务
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/elucky
      - REDIS_URL=redis://redis:6379/0
      - CLICKHOUSE_URL=clickhouse://clickhouse:9000/elucky
    depends_on:
      - postgres
      - redis
      - clickhouse
    volumes:
      - ../logs:/app/logs
      - ../data:/app/data

  # Agent执行器（可水平扩展）
  agent-worker-1:
    build:
      context: ..
      dockerfile: docker/Dockerfile.agent
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/elucky
      - REDIS_URL=redis://redis:6379/0
      - CLICKHOUSE_URL=clickhouse://clickhouse:9000/elucky
      - WORKER_ID=worker-1
    depends_on:
      - postgres
      - redis
      - clickhouse

  # PostgreSQL主库
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=elucky
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis缓存/队列
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # ClickHouse分析库
  clickhouse:
    image: clickhouse/clickhouse-server:23.3
    ports:
      - "8123:8123"
      - "9000:9000"
    volumes:
      - clickhouse_data:/var/lib/clickhouse

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api

volumes:
  postgres_data:
  redis_data:
  clickhouse_data:
```

### 7.2 部署拓扑

```
                    ┌─────────────────┐
                    │   用户/运营      │
                    └────────┬────────┘
                             │ HTTPS
                             ▼
                    ┌─────────────────┐
                    │     Nginx       │
                    │  (反向代理/SSL) │
                    └────────┬────────┘
                             │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │ Web管理  │  │ API服务   │  │Agent调度 │
       │  后台    │  │  (FastAPI)│  │  Worker  │
       └──────────┘  └────┬─────┘  └────┬─────┘
                          │             │
              ┌────────────┴────────────┴────────────┐
              │                                      │
              ▼                                      ▼
       ┌──────────────┐                    ┌──────────────┐
       │ PostgreSQL   │                    │    Redis     │
       │   主库       │                    │  缓存/队列   │
       └──────────────┘                    └──────────────┘
              │
              ▼
       ┌──────────────┐
       │ ClickHouse  │
       │  时序分析   │
       └──────────────┘
```

---

## 8. 安全设计

### 8.1 密码加密

```python
# src/core/security.py
from cryptography.fernet import Fernet
from typing import Optional
import os

class EncryptionService:
    """密码加密服务"""

    def __init__(self):
        # 密钥从环境变量获取，永不硬编码
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise ValueError("ENCRYPTION_KEY not set")
        self.fernet = Fernet(key.encode())

    def encrypt(self, plaintext: str) -> str:
        """AES-256加密"""
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """AES-256解密"""
        return self.fernet.decrypt(ciphertext.encode()).decode()
```

### 8.2 API认证

```python
# src/api/middleware/auth.py
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from typing import Optional

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """验证API Key"""
    valid_keys = get_configured_api_keys()  # 从数据库/配置获取
    if api_key not in valid_keys:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

### 8.3 敏感操作审计

```sql
-- 敏感操作审计日志表
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    action VARCHAR(50) NOT NULL,  -- login/read_password/write_content等
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    ip_address VARCHAR(50),
    user_agent TEXT,
    detail JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 9. 关键技术难点与解决方案

### 9.1 反检测技术

| 难点 | 解决方案 |
|------|---------|
| 设备指纹关联 | AdsPower指纹隔离，一号一Profile |
| IP关联封号 | 住宅IP固定绑定，不轮换 |
| 行为异常检测 | 操作间隔随机3-8秒，拟人化节奏 |
| 内容重复检测 | 同一脚本>30%差异加工 |

### 9.2 多平台适配

| 难点 | 解决方案 |
|------|---------|
| 格式差异 | 3个适配层引擎（fb/ig/x-adapter） |
| 字符限制 | 各平台独立校验（TK100字/IG2200字/X280字） |
| Hashtag策略 | 平台专属词库（TK3-5个/IG20-30个/X1-3个） |
| 内容差异率 | 必须>30%，否则重新生成 |

### 9.3 风控连坐防护

```
封号事件触发
    │
    ▼
查询受影响账号 ──────────────────────────────────────┐
    │                                                 │
    ├─ 同IP账号 ──▶ 降低操作频率 ──▶ 通知风控Agent
    │
    ├─ 同Meta账号 ──▶ 标记高风险 ──▶ 通知风控Agent
    │
    └─ 同设备 ──▶ 暂停该设备上所有账号
```

---

## 10. 开发计划

### 10.1 Phase划分

| Phase | 时间 | 任务 | 交付物 |
|-------|------|------|--------|
| Phase 1 | W1-W8 | TK矩阵 | 9个Agent + 23个Skill |
| Phase 2 | W9-W12 | IG扩展 | 4个IG Agent + 23个适配 |
| Phase 3 | W13-W17 | FB扩展 | 4个FB Agent + 23个适配 |
| Phase 4 | W18-W20 | X扩展 | 4个X Agent + 23个适配 |
| Phase 5 | W21-W22 | 联调测试 | 跨平台 + 压测 |

### 10.2 代码量预估

| 模块 | 文件数 | 代码行数 |
|------|--------|---------|
| Agent核心 | 15 | 5,000 |
| 平台Agent | 40 | 15,000 |
| Skill实现 | 105 | 30,000 |
| 服务层 | 20 | 8,000 |
| API层 | 15 | 5,000 |
| 数据库模型 | 10 | 3,000 |
| **总计** | **~205** | **~66,000** |

---

## 11. 监控与告警

### 11.1 监控指标

```yaml
# 关键监控指标
metrics:
  系统层面:
    - CPU使用率 (>80% 告警)
    - 内存使用率 (>85% 告警)
    - 磁盘使用率 (>90% 告警)
    - 网络IO

  业务层面:
    - 活跃账号数
    - 今日发布内容数
    - 质检通过率
    - 封号率 (>5% 告警)
    - WA引流新增数

  队列层面:
    - 等待任务数
    - 执行中任务数
    - 失败任务数
    - 任务平均执行时间
```

### 11.2 告警规则

```python
# 告警配置
ALERT_RULES = {
    "封号率过高": {
        "condition": "daily_ban_rate > 0.05",
        "severity": "critical",
        "channels": ["sms", "email", "wechat"]
    },
    "任务队列积压": {
        "condition": "pending_tasks > 1000",
        "severity": "high",
        "channels": ["email"]
    },
    "API调用失败率": {
        "condition": "api_failure_rate > 0.1",
        "severity": "medium",
        "channels": ["email"]
    }
}
```

---

## 12. 总结

### 12.1 技术选型总结

| 维度 | 选型 | 核心理由 |
|------|------|---------|
| 语言 | Python 3.10+ | AI生态最全 |
| Agent框架 | LangGraph | 状态机+循环+条件分支 |
| 主数据库 | PostgreSQL | JSONB支持平台差异 |
| 分析数据库 | ClickHouse | 时序数据高效 |
| 缓存/队列 | Redis | 操作计数+任务队列 |
| 浏览器 | Playwright + AdsPower | 指纹隔离+跨平台 |

### 12.2 架构亮点

1. **模块化设计**：Agent/Skill/Adapter分离，便于扩展
2. **平台无关性**：核心逻辑与平台实现解耦
3. **多数据库协同**：关系+时序+缓存各司其职
4. **安全第一**：AES加密+审计日志+API认证
5. **可观测性**：全链路监控+多级告警

### 12.3 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| 平台政策变化 | 高 | 风控Agent实时监控，快速响应 |
| 封号率上升 | 高 | 备用号池+分级风控 |
| API成本超支 | 中 | 用量监控+限流策略 |
| 系统稳定性 | 中 | Docker容器化+自动扩缩容 |

---

**文档版本：** v1.0
**下次更新：** 2026-04-10
**维护人：** CaySon
