"""Generate GEO-Platform performance audit report - PART 1"""
# -*- coding: utf-8 -*-
import os

REPORT = r'E:\workspace\GEO-Platform性能审计报告.md'

content = '''# GEO-Platform 性能 & 架构审计报告

> **审计对象**:`E:\\PY\\yunfanshujing\\GEO-Platform`(FastAPI 后端 + 3 个前端 app)
> **审计时间**:2026-06
> **审计方式**:主线程读关键文件 + 8 个并行子 agent 分块扫描
> **审计范围**:后端 routers / services / models / alembic 迁移 / middleware + 前端 customer/admin/devpanel 3 个 app

---

## 📊 0. 审计总览

| 维度 | 扫描文件 | 问题总数 | Critical | High | Medium | Low |
|---|---|---|---|---|---|---|
| 后端 routers | 34 个 / 186 端点 | 30+ | - | **5**(28 长任务 + 7 越权 + 15 无分页) | - | - |
| 后端 services (admin_*) | 25 个 | 112 | **5** | 39 | 45 | 23 |
| 后端 services (client_*) | 14 个 | 167 | **5** | 79 | 56 | 32 |
| 后端 models + alembic | 7 models + 32 迁移 | **200** | - | **60** | 79 | 56+5info |
| 后端 middleware | 2 个 | **4** | - | **4** | - | - |
| 前端 (3 app) | customer/admin/devpanel | 18 优化点 | **5 个 P0** | 6 个 P1 | 5 个 P2 | 2 个 P3 |

**审计产物文件**:
- `E:\\workspace\\geo_audit_routers.json` — routers 186 端点 / 22 global findings (81KB)
- `E:\\workspace\\geo_audit_services_admin.json` — admin_*.py 50 函数 / 112 问题
- `E:\\workspace\\geo_audit_services_client.json` — client_*.py 14 文件 / 167 问题 + 5 critical
- `E:\\workspace\\geo_audit_db_schema.json` — 200 问题 / 19 迁移问题 / 15 优化建议
- `E:\\workspace\\geo_audit_frontend.json` — 前端 3 app / 18 recommendations
- `E:\\workspace\\geo_audit_admin.md` / `geo_audit_customer.md` / `geo_audit_client_services.md`

---

## 1. 架构概览

### 1.1 技术栈
- **后端**:FastAPI + asyncpg + SQLAlchemy 2.0(async) + Pydantic + JWT
- **DB**:PostgreSQL(**67 张业务表 + 2 张物化视图**)
- **爬虫交互**:DCP(Data-Collection-Platform)通过 HTTP 触发
- **缓存**:**未发现 Redis 等缓存层** — 所有高频接口裸奔
- **前端**:
  - `customer` — Next.js 14 (App Router) + SWR + Tailwind + Recharts
  - `admin` — UmiJS + Ant Design Pro + Antd Charts
  - `devpanel` — Next.js(运营内部工具)

### 1.2 模块规模
- **routers**:23 个(`admin_*` × 14 + `client_*` × 5 + 其他 × 4) — 186 个端点
- **services**:50+ 个(`admin_*` × 25 + `client_*` × 14 + `core_*` × 10)
- **models**:66 个 ORM 跨 5 个 schema(platform/crawler/analysis/cms/auth_audit)
- **alembic 迁移**:32 个,**0 个用 CREATE INDEX CONCURRENTLY**

---

## 2. Critical 级问题(必修)

### 2.1 [后端-CR1] 同步 SQLAlchemy 引擎跑在 async 上下文 — 阻塞事件循环

**位置**:
- `apps/backend/src/services/admin_temp_crawler.py::_trigger_dcp_and_update_status`
- `apps/backend/src/services/admin_temp_crawler.py::_watch_dcp_completion_and_sync_results`
- `apps/backend/src/services/admin_temp_crawler_helpers.py::sync_temp_crawl_results_from_answers_sync`

**症状**:在 `async def` 函数内,使用 `create_engine(_to_sync_db_url(db_url))`(psycopg2 同步驱动),并 `db = SessionLocal(); db.commit()` 同步调用。每次 commit 阻塞整个 async 事件循环。

`_watch_dcp_completion_and_sync_results` 是轮询循环,最多 60 次 × 10 秒 = 10 分钟,期间**持续阻塞事件循环**,导致其他请求 hang。

**修复**:
```python
# 现状
def _trigger_dcp_and_update_status(self, ...):
    sync_engine = create_engine(_to_sync_db_url(db_url))
    with Session(sync_engine) as db:
        db.commit()  # 同步阻塞

# 修复
async def _trigger_dcp_and_update_status(self, ...):
    async with async_session() as session:
        await session.commit()
```

**工时**:4h | **优先级**:P0 | **影响范围**:所有 admin 临时爬虫接口

---

### 2.2 [后端-CR2] `admin_clients.delete_client` — 19 个串行 DELETE 在单一事务

**位置**:`apps/backend/src/services/admin_clients.py::delete_client`

**症状**:
```python
# 19 个 await db.execute(delete(...)) 全在单事务
await db.execute(delete(ReferenceParagraphAttribution).where(...))
await db.execute(delete(ReferenceSourceDaily).where(...))
await db.execute(delete(BrandAnswerMetrics).where(...))
# ... 共 19 个串行删除 ...
await db.execute(delete(Users).where(...))
```

百万行级数据时,锁行几分钟,连接池耗尽,admin UI 全部卡死。

**修复**:
1. 拆为多个短事务,每批 1000-5000 行
2. 用 `TRUNCATE ... CASCADE`(快 100x)
3. 改后台任务 + 进度回调,不阻塞请求

**工时**:8h | **优先级**:P0 | **影响范围**:admin 客户删除

---

### 2.3 [后端-CR3] `sync_temp_crawl_results_from_answers` — N+1 INSERT 每次回调都跑

**位置**:`apps/backend/src/services/admin_temp_crawler_persistence.py::sync_temp_crawl_results_from_answers`

**症状**:
```python
for item in items:  # 可能 5000+ 条
    await db.execute(text("INSERT ... ON CONFLICT"))  # 每条 1 次往返
```

**5000 个 answer = 5000 次 round-trip**,期间阻塞事件循环。该函数从 4 个入口触发:get_temp_crawl_detail、replay_temp_crawl_job、handle_temp_crawl_completion_callback、build_project_answers_export。

**修复**:
1. 改用 `INSERT ... SELECT FROM ... ON CONFLICT DO UPDATE` 单条 SQL
2. 或 `executemany` 批量 + `db.commit()` 一次
3. 加 `sync_status` 字段:已同步的跳过,标记 dirty 增量同步

**工时**:6h | **优先级**:P0 | **影响范围**:admin 临时爬虫全链路

---

### 2.4 [后端-CR4] `query_result_items` — `page_size=0` 全量加载含大字段

**位置**:`apps/backend/src/services/admin_temp_crawler_helpers.py::query_result_items`

**症状**:
```python
if page_size > 0:
    # 分页
else:
    # 返回 ALL 全部行 + answer_text + answer_html
    # 1 万行任务 = 100MB+ Python 列表
```

配合 4 处 LATERAL join 嵌套循环,内存爆 + 序列化爆。**这是整个临时爬虫的 OOM 根因**。

**修复**:
1. **强制** `LIMIT max(1, min(page_size, 200))`,移除"返回全部"分支
2. 大字段 `answer_text/answer_html` 走单独懒加载 endpoint
3. 加 `streaming=True` 流式 JSON 响应

**工时**:2h | **优先级**:P0 | **影响范围**:admin 临时爬虫详情/导出

---

### 2.5 [DB-CR1] 5 张高写入核心表完全未分区

**位置**:`crawler.crawl_answers / task_queue / crawl_error_logs / reference_sources / temp_crawl_results`

**症状**:月度增量 100w~1000w 行,**无任何分区策略**。`vacuum` / `ANALYZE` / 索引重建会扫全表,业务高峰期 IO 风暴。

`brand_mentions` 是分析流水线的核心 JOIN 端,`crawl_answers` 没分区 → brand_mentions 的 JOIN 永远走大表 seq scan → **整个分析性能被上游拖累**。

**修复 SQL 示例**:
```sql
ALTER TABLE crawler.crawl_answers 
  RENAME TO crawler.crawl_answers_old;
CREATE TABLE crawler.crawl_answers (...)
  PARTITION BY RANGE (batch_date);
CREATE TABLE crawler.crawl_answers_2026m06 
  PARTITION OF crawler.crawl_answers 
  FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
-- ... 复制数据 + 自动 cron 创建下月 partition
```

**工时**:16h | **优先级**:P0 | **影响范围**:数据流水线全链路

---

### 2.6 [后端-CR6] 同步 openpyxl 阻塞 event loop

**位置**:`apps/backend/src/services/client_answers.py::get_answer_export_file` + `admin_temp_crawler_persistence.build_project_answers_export`

**症状**:
```python
workbook = openpyxl.Workbook()
for row in rows:  # 1 万行
    ws.append(row)
workbook.save(BytesIO())  # 几百 ms 阻塞 event loop
```

**修复**:`await asyncio.to_thread(_build_workbook_sync, rows)` **工时**:1h

---
'''

with open(REPORT, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Part 1 written: {os.path.getsize(REPORT)} bytes')
