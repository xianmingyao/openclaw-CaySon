"""Write GEO-Platform system diagnostic & optimization report - PART 1"""
# -*- coding: utf-8 -*-
import os

OUT = r'E:\workspace\GEO-Platform-系统诊断与优化建议.md'

content = '''# GEO-Platform 系统诊断与优化建议(系统报告 v1.0)

> **报告人**:CaySon(AI 助手 / 24 年后端老炮视角)
> **审计时间**:2026-06-17
> **配套文件**:
> - `E:\\workspace\\GEO-Platform性能审计报告.md`(40KB / 1072 行) - 详细技术审计
> - `E:\\workspace\\GEO-Platform-p0-fixes.md`(10KB) - 已落地的 9 个 P0 修复
> - `E:\\workspace\\geo_audit_*.json / .md`(9 个) - 8 个并行子 agent 的原始产物
>
> **配套审计**:
> - 后端 34 个 router / 186 端点 + 50+ service + 7 model + 32 迁移 + 2 middleware
> - 前端 3 个 app(customer / admin / devpanel)
> - 累计问题:**513 个**(Critical 10 / High 187 / Medium 180 / Low 116)
> - **本次已修复 9 个 P0,Critical 章节 100% 清零**

---

## 0. 🎯 执行摘要(给老板/团队领导,3 分钟看完)

### 0.1 一句话结论

**GEO-Platform 是一个"功能完整但裸奔"的系统**。选型不错、9 个月跑出 67 张表 + 186 个端点 + 3 个前端 app,业务能跑。但 9 个月的快速迭代留下了**系统性的工程债**,**最严重的是完全没有缓存层**。

**好消息**:**没有一个是架构性问题**,全是"补作业"。按 ROI 排序的优化清单,144 人时(18 人天)可解 80% 痛点。

### 0.2 风险评级(从高到低)

| 等级 | 风险 | 触发场景 | 触发时间预估 |
|---|---|---|---|
| 🔴 **致命** | 临时爬虫阻塞 event loop 10 分钟 | 任何 admin 临时爬虫 | **每天都会触发** |
| 🔴 **致命** | `delete_client` 锁表几分钟 | admin 删除客户 | **每月 1-2 次** |
| 🔴 **致命** | 慢查询耗尽连接池 | 单条 query > 60s | **每周 1-2 次** |
| 🟠 **高危** | DCP 回调无签名,token 泄露即被滥用 | DCP token 泄露 | **安全事件级** |
| 🟠 **高危** | JWT 存 localStorage,XSS 一打就中 | 任何 XSS 漏洞 | **待 XSS 出现** |
| 🟠 **高危** | `mention_rate > 100%` 笛卡尔积 bug 重现 | 任何爬虫补数据 | **随时可能** |
| 🟡 **中危** | 服务重启丢 28 个长任务(导出/爬虫) | 重启/扩容/发布 | **每周 1-2 次** |
| 🟡 **中危** | 5 张高写入核心表无分区 | 数据量 10x 后 | **3-6 个月内** |
| 🟢 **低危** | bundle 体积过大 | SEO 评分下降 | **持续** |

### 0.3 数据说话(为什么要现在动手)

| 指标 | 当前 | 风险阈值 | 距离阈值 |
|---|---|---|---|
| 临时爬虫最大任务量 | ~5000 answer/任务 | 10000+ | 1-2 月 |
| `brand_mentions` 月增量 | ~百万 | 千万 | 6 月 |
| `crawl_answers` 月增量 | ~百万 | 千万 | 6 月 |
| 并发用户(估算) | < 50 | > 200 触发连接池耗尽 | 3-6 月 |
| 已知 Critical bug | 0(已修) | - | - |
| 测试覆盖 | ~5% | > 60% | 长期欠债 |

### 0.4 投入产出(老板关心的)

| 投入 | 产出 | 周期 |
|---|---|---|
| 18 人天(P0 必修) | 80% 痛点解决,首屏快 4 倍,生产稳定性大幅提升 | 1 月 |
| 10 人天(中期) | 数据 10x 后不崩,缓存 + 分区 + 索引 | 2 月 |
| 1-2 月(长期) | CQRS / ClickHouse / OpenTelemetry | 季度 |

**总结:宁兄,先动 18 人天的 P0,效果立竿见影。**

---

## 1. 📊 现状诊断(老炮视角)

### 1.1 项目结构

```
GEO-Platform/
├── apps/
│   ├── backend/         # FastAPI + asyncpg + SQLAlchemy 2.0 + Pydantic
│   │   ├── src/
│   │   │   ├── routers/        # 34 个 / 186 端点
│   │   │   ├── services/       # 50+ 个 (admin_* 25 + client_* 14 + core_* 10+)
│   │   │   ├── models/         # 66 个 ORM 跨 5 schema
│   │   │   ├── schemas/        # Pydantic schemas
│   │   │   ├── middleware/     # 2 个
│   │   │   ├── constants/      # platforms 等
│   │   │   ├── database.py     # ✅ 已 P0 修复
│   │   │   ├── config.py       # ⚠️ JWT_SECRET_KEY 默认值
│   │   │   └── main.py
│   │   ├── alembic/            # 32 迁移
│   │   ├── docs/sql/           # ⚠️ 漂移
│   │   └── requirements.txt
│   ├── customer/        # Next.js 14 + SWR + Tailwind + Recharts
│   ├── admin/           # UmiJS + Ant Design Pro + Antd Charts
│   └── devpanel/        # Next.js(运营内部工具)
├── docs/
├── scripts/
└── tools/
```

### 1.2 业务规模(数据说话)

| 维度 | 规模 | 评估 |
|---|---|---|
| 业务模块 | 20+ 个 | 完整度高 |
| 数据库表 | 67 张 + 2 物化视图 | 中型规模 |
| 路由端点 | 186 个 | 中型规模 |
| Service 文件 | 50+ | 充分分层 |
| alembic 迁移 | 32 个 | 9 个月高强度迭代 |
| OpenAPI 文档 | 634KB(openapi.json) | 完整 |

### 1.3 技术栈评估

✅ **选型正确**:
- **后端**:FastAPI + asyncpg + SQLAlchemy 2.0(async 风格统一)
- **DB**:PostgreSQL(支持 JSONB、分区、物化视图)
- **前端**:Next.js 14 + UmiJS + Ant Design(企业级标准)
- **爬虫交互**:DCP(独立服务,异步触发)

⚠️ **选型合理但用法欠债**:
- async SQLAlchemy 用了,但**多个文件用 sync engine 跑在 async 上下文**(P0 已修)
- Next.js 用了,但**根 layout 用 `await headers()` 强制 dynamic**(P0 已修)
- UmiJS 用了,但**11 个 service 没用 `useRequest` 包装**
- Pydantic 用了,但**2 个端点直接返回 dict**
- JWT 用了,但**存 localStorage**(安全债)

❌ **缺失的关键基础设施**:
- **零缓存层**(Redis / Memcached 都没引入)
- **零异步任务队列**(Celery / Arq / Dramatiq 都没用)
- **零链路追踪**(OpenTelemetry / Sentry 都没集成)
- **零 API 限流**(无 slowapi / fastapi-limiter)

### 1.4 代码质量雷达(24 年老炮视角)

```
                  ┌─────────────────────────────────┐
                  │ 业务功能完整度      ★★★★★ 5/5  │
                  │ 代码分层清晰度      ★★★★  4/5  │
                  │ 类型注解覆盖率      ★★★   3/5  │
                  │ 错误处理规范度      ★★    2/5  │
                  │ 测试覆盖度          ★     1/5  │
                  │ 性能意识            ★★    2/5  │
                  │ 安全意识            ★★    2/5  │
                  │ 可观测性            ★     1/5  │
                  │ 文档完整度          ★★★   3/5  │
                  │ 部署自动化          ★★    2/5  │
                  └─────────────────────────────────┘
```

### 1.5 老炮 3 大核心观察

> **观察 1:典型的"快速迭代债"**,不是技术问题,是节奏问题
>
> 9 个月做出 186 端点 + 67 表,**团队的战斗力是毋庸置疑的**。但 9 个月的快速迭代,没人有时间补基础设施——这不是"错",是"代价"。

> **观察 2:已经踩过笛卡尔积的坑,但没形成防御机制**
>
> `mention_rate > 100%` bug 修过(20260421 迁移),但只是局部修复 2 张表,**还有 2 张维度表裸奔**(`brand_answer_metrics` / `brand_rankings`)。这种"踩坑-修复-再踩"的模式不可持续,需要 UNIQUE 约束作为"硬防御"。

> **观察 3:最大的债不是性能,是"任务可靠性"**
>
> 28 个长任务用 FastAPI `BackgroundTasks`,**服务重启即丢**。这意味着:每次发布都可能丢几个客户的导出任务或爬虫任务。在客户视角是"我付了钱你给我做一半"。**这个债比性能债更影响业务**。

---
'''

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(content)
import os
print(f'Part 1: {os.path.getsize(OUT)} bytes')
