"""Append PART 2 - High level issues"""
# -*- coding: utf-8 -*-

REPORT = r'E:\workspace\GEO-Platform性能审计报告.md'

content = '''
## 3. High 级问题(性能瓶颈)

### 3.1 N+1 查询 — 14 个 admin_*.py + 7 个 client_*.py

| 文件 | 函数 | 模式 | 复杂度 |
|---|---|---|---|
| `admin_clients.py` | `get_client_list` | per-page fan-out | 20 clients × 5 projects × 3 = **300 awaits** |
| `admin_clients.py` | `update_client` | `_rebuild_competitors` per-row `db.delete` | 8 comps = 8 round-trips |
| `admin_dashboard.py` | `_get_platform_status` | per-platform `MAX(TaskQueue.completed_at)` | 5 platforms = 5 round-trips |
| `admin_open_api_keys.py` | `get_admin_api_key_list` | per-row `list_api_key_resources` | 20 keys × 5 = **100 round-trips** |
| `admin_projects.py` | `get_project_list` | per-project 3 awaits | 20 × 4 = **80 awaits** |
| `admin_projects.py` | `update_project` | per-competitor `db.delete` | 10 + 10 = 20 round-trips |
| `admin_users.py` | `get_client_user_list` | per-user 2 awaits | 20 × 2 = **40 round-trips** |
| `client_answers.py` | `get_answer_list` | per-row 2 awaits (BrandMentions + SentimentScores) | 20 × 2 = **41 round-trips** |
| `client_brands.py` | `get_brand_list` | per-brand 2 awaits (monitored + question count) | M brands × 2 = **1+2M** |
| `client_profile.py` | `_get_admin_profile` | per-project 2 awaits | N projects × 2 |
| `client_api_keys.py` | `list_api_keys` | per-key `list_api_key_resource_keys` | K keys = K round-trips |
| `admin_data_scope.py` | `update_user_data_scope` | per-record `db.delete` | N = N round-trips |
| `admin_client_features.py` | `update_client_features` | per-feature SELECT + UPDATE/INSERT | 10 = 10 round-trips |
| `admin_crawler_servers.py` | `update_schedule` | 加载 ALL servers 找单个 | 100+ servers 一次性 |

**通用修复模板**:
```python
# 现状: N+1
for brand in brands:
    r = await db.execute(select(func.count(...)).where(Project.id == brand.id))
    items.append({**brand, "count": r.scalar_one()})

# 修复: 一次聚合查询
brand_ids = [b.id for b in brands]
counts_q = (
    select(Project.id, func.count(QuestionPool.id).label("qc"))
    .where(Project.id.in_(brand_ids))
    .group_by(Project.id)
)
counts = {row.id: row.qc for row in (await db.execute(counts_q)).all()}
items = [{**b, "count": counts.get(b.id, 0)} for b in brands]
```

**工时**:32h(全 14 个文件) | **ROI**:★★★★★

---

### 3.2 串行 await — 9+ 个核心接口

| 接口 | 串行次数 | 预估延迟 | 修复后预估 |
|---|---|---|---|
| `/client/dashboard/overview` (client_dashboard) | 12 | 60ms | 5ms |
| `/client/brands/{id}` (client_brands) | 14 | 70ms | 5ms |
| `/client/comparison` (client_comparison) | 5 | 25ms | 5ms |
| `/client/references/citation-stats` (client_references) | 2 | 10ms | 5ms |
| `/admin/dashboard/overview` (admin_dashboard) | 8 | 40ms | 5ms |
| `/admin/dashboard/client-kpi` (router) | 2 service 串行 | 20ms | 10ms |
| `/admin/dashboard/client-kpi-detail` | 多个 CTE | 30ms | 10ms |
| `client_access_scope.resolve_access_scope_context` | operator scope N 次串行 | O(N) | O(1) |
| `client_references` 4 个接口三层 fallback 串行 | rsd → rpa → answers | 3x RTT | 1x RTT |

**通用修复**:
```python
r1, r2, r3 = await asyncio.gather(
    db.execute(q1),
    db.execute(q2),
    db.execute(q3),
)
```

**工时**:16h | **ROI**:★★★★★

---

### 3.3 [DB-H1] `analysis.brand_mentions` 零索引 + 月度千万级

**位置**:`apps/backend/src/models/analysis.py::BrandMentions`

**症状**:
- 无任何业务索引(`crawl_answer_id / client_id / project_id / batch_date / target_platform` 全缺)
- 核心查询 `WHERE client_id=? AND project_id=? AND brand_name=? AND batch_date BETWEEN ? AND ?` 走 seq scan
- `crawl_answer_id` 无 FK CASCADE → 删父表会阻塞

**修复**:
```sql
CREATE INDEX CONCURRENTLY idx_brand_mentions_client_project_date
  ON analysis.brand_mentions (client_id, project_id, batch_date DESC);
CREATE INDEX CONCURRENTLY idx_brand_mentions_project_brand_date
  ON analysis.brand_mentions (project_id, brand_name, batch_date DESC);
CREATE INDEX CONCURRENTLY idx_brand_mentions_crawl_answer
  ON analysis.brand_mentions (crawl_answer_id);

ALTER TABLE analysis.brand_mentions
  ADD CONSTRAINT fk_brand_mentions_crawl_answer
  FOREIGN KEY (crawl_answer_id) REFERENCES crawler.crawl_answers(id)
  ON DELETE CASCADE;
```

**工时**:2h | **ROI**:★★★★★(立即缓解 90% 分析查询)

---

### 3.4 [DB-H2] 14 张表 JSONB 字段 0 张 GIN 索引

**症状**:`platform.projects.brand_aliases / target_platforms`、`crawler.question_pool.target_platforms`、`analysis.gpower_scores.entropy_weights`、`reference_paragraph_attribution.topic_tags / content_features` 等高频 `@>` 包含查询全部走全表扫。

**修复**(4h 完成):
```sql
CREATE INDEX CONCURRENTLY idx_projects_brand_aliases_gin 
  ON platform.projects USING GIN (brand_aliases jsonb_path_ops);
CREATE INDEX CONCURRENTLY idx_projects_target_platforms_gin 
  ON platform.projects USING GIN (target_platforms jsonb_path_ops);
CREATE INDEX CONCURRENTLY idx_question_pool_target_platforms_gin 
  ON crawler.question_pool USING GIN (target_platforms jsonb_path_ops);
-- ... 14 张表 ...
```

**工时**:4h | **ROI**:★★★★

---

### 3.5 [DB-H3] 高写入日志表无 `(user_id, created_at)` 索引 + 无分区

**位置**:
- `platform.api_request_logs`(百万~千万/月)
- `platform.user_login_history` / `platform.alert_history`
- `crawler.crawl_error_logs` / `platform.api_key_access_logs`

**修复**:`CREATE INDEX CONCURRENTLY` + 按月分区(工时 8h)

---

### 3.6 [DB-H4] 缺失 UNIQUE 防笛卡尔积 bug 重现

**症状**:之前 `mention_rate > 100%` bug 根因就是 `sentiment_scores / brand_mention_daily` 无 UNIQUE 导致 LEFT JOIN 笛卡尔积(已在 20260421 修复了 2 张)。`brand_answer_metrics` 和 `brand_rankings` 仍是裸表,aggregator 重跑必翻车。

**修复**:
```sql
CREATE UNIQUE INDEX CONCURRENTLY uq_brand_answer_metrics
  ON analysis.brand_answer_metrics (project_id, target_platform, batch_date, batch_round)
  WHERE batch_round IS NOT NULL;
CREATE UNIQUE INDEX CONCURRENTLY uq_brand_rankings
  ON analysis.brand_rankings (project_id, target_platform, brand_name, batch_date);
```

**工时**:4h | **ROI**:★★★★

---

### 3.7 [后端-H1] RequestLoggingMiddleware 同步 DB 写日志阻塞所有请求

**位置**:`apps/backend/src/middleware/request_logging.py`

**症状**:
```python
finally:
    try:
        async with async_session() as session:  # 每个请求新建 session
            session.add(ApiRequestLog(...))     # 同步 INSERT
            await session.commit()              # 阻塞响应
```

每个 API 请求都额外创建 session + 同步 INSERT。高 QPS 时连接池占满。`OpenApiAuditMiddleware` 同样问题。

**修复**:
```python
# 异步队列批量写
from collections import deque
_log_buffer: deque = deque(maxlen=1000)

async def _flush_logs():
    while True:
        await asyncio.sleep(5)
        batch = list(_log_buffer)
        _log_buffer.clear()
        if batch:
            async with async_session() as session:
                session.add_all(batch)
                await session.commit()
```

**工时**:4h | **ROI**:★★★★

---

### 3.8 [后端-H2] `database.py` 缺关键超时配置

**位置**:`apps/backend/src/database.py`

**修复**:
```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=30,
    connect_args={
        "server_settings": {
            "application_name": "geo-backend",
            "statement_timeout": "60s",
            "idle_in_transaction_session_timeout": "300s",
        },
        "timeout": 10,
    },
)
```

**工时**:1h | **ROI**:★★★★

---

### 3.9 [前端-H1] `admin/dashboard/index.tsx` 串行 3 个 await

**位置**:`apps/admin/src/pages/dashboard/index.tsx::L96-148`

**修复**:
```typescript
const [overviewResult, crawlResult, analysisResult] = await Promise.allSettled([
  getOverview(),
  getCrawlToday(),
  getAnalysisStatus(),
]);
```

**工时**:0.5h | **ROI**:★★★★★(零成本首屏快 60%)

---

### 3.10 [前端-H2] 大表格无 `virtual` + 无 `scroll.y` — 千行数据掉帧

**位置**:
- `apps/admin/src/pages/crawler/components/{StatusTab,SchedulesTab,...}` 4 个子 Tab
- `apps/admin/src/pages/clients/index.tsx` ProTable + 嵌套展开
- `apps/admin/src/pages/reports/index.tsx`
- `apps/admin/src/pages/projects/[id]/index.tsx` 用 `page_size:0` 拉全量

**修复**:
```typescript
<ProTable
  virtual
  scroll={{ y: 560 }}
  pagination={{ pageSize: 50, showSizeChanger: true }}
  request={async (params) => getQuestionList({ page: params.current, page_size: params.pageSize })}
/>
```

**工时**:8h | **ROI**:★★★

---

### 3.11 [前端-H3] `admin/projects/[id]/index.tsx` `page_size:0` 全量拉 questions

**位置**:`apps/admin/src/pages/projects/[id]/index.tsx::L222/L226`

**修复**:改服务端筛选 + 条件查询,加 `page_size≤100` 限制。**工时**:4h | **ROI**:★★★★

---

### 3.12 [前端-H4] admin service 裸调用无 useRequest 包装 — 11 个 service

**症状**:`apps/admin/src/services/*.ts` 11 个 service 文件全部是 `async function` 裸调用,没用 umi 的 `useRequest` 包装 → **没有 `staleTime` / `debounce` / `cacheKey` 复用**。

**修复**:
```typescript
import { useRequest } from 'umi';

export const useDashboardOverview = () => 
  useRequest(getDashboardOverview, { 
    cacheKey: 'dashboard-overview',
    staleTime: 5 * 60 * 1000,  // 5 min
  });
```

**工时**:8h | **ROI**:★★★★★

---

### 3.13 [前端-H5] 3 个 app 缺 ErrorBoundary + 401 拦截

**症状**:
- 无 ErrorBoundary → 接口报错白屏
- 401 无拦截器 → token 过期不会自动登出

**修复**:
```typescript
// app/error.tsx
'use client'
export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return <div><button onClick={reset}>Retry</button></div>;
}

// 401 拦截
axios.interceptors.response.use(
  res => res,
  err => { if (err.response?.status === 401) { /* 跳转登录 */ } return Promise.reject(err); }
);
```

**工时**:4h

---

### 3.14 [架构-H1] **零缓存层** — 这是 79 个 high 问题的总根因

**症状**:`global_findings.files_with_cache = []` — 14 个 client_*.py service **全部零缓存**,每个请求都查 DB。

**修复**:
```python
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_cache.backends.redis import RedisBackend

@router.get("/overview")
@cache(expire=60)  # 60s TTL
async def overview(...): ...

# 启动时:
app.state.cache = RedisBackend(aioredis.from_url("redis://localhost:6379"))
FastAPICache.init(app.state.cache)
```

按数据稳定性分级:
- **admin profile** → 1h
- **dashboard 概览** → 5min
- **列表** → 30s
- **实时数据**(答案列表) → 不缓存

**工时**:8h(基础) + 每个 endpoint 0.5h | **ROI**:★★★★★

---

### 3.15 [前端-H6] customer `layout.tsx` 强制整个布局为 dynamic

**位置**:`apps/customer/src/app/layout.tsx::L42-47`

```typescript
const headersList = await headers();  // 强制 dynamic
```

**症状**:整个布局 dynamic 化 → **所有页面失去静态优化**。URL 已有 `locale` 段,直接读 `params` 即可。

**修复**:改用 `params.locale`,移除 `await headers()`。**工时**:0.5h | **ROI**:★★★★★

---

### 3.16 [前端-H7] devpanel 轮询无 visibilitychange 暂停

**位置**:devpanel 的 `api-panorama` (30s) + `pipeline` (5s) 轮询

**症状**:后台标签页空跑 DB 查询。

**修复**:
```typescript
useEffect(() => {
  const tick = () => document.visibilityState === 'visible' && refetch();
  const id = setInterval(tick, 5000);
  document.addEventListener('visibilitychange', tick);
  return () => { clearInterval(id); document.removeEventListener('visibilitychange', tick); };
}, []);
```

**工时**:2h

---
'''

with open(REPORT, 'a', encoding='utf-8') as f:
    f.write(content)
import os
print(f'After Part 2: {os.path.getsize(REPORT)} bytes')
