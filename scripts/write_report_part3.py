"""Append PART 3 - Medium + Low + Routers + Architecture"""
# -*- coding: utf-8 -*-

REPORT = r'E:\workspace\GEO-Platform性能审计报告.md'

content = '''
## 4. Medium 级问题

### 4.1 [后端-M1] `report_service.py` f-string 拼 SQL(风格反模式)

**位置**:`apps/backend/src/services/report_service.py::L52, L333`

**修复**:改用 SQLAlchemy `select()` API。**工时**:2h

---

### 4.2 [后端-M2] `dcp_client.py` 每次重试新建 AsyncClient

**修复**:把 AsyncClient 提到模块级单例 + httpx 连接池。**工时**:1h

---

### 4.3 [前端-M1] `getAnalysisStatus` 4 个 `except Exception` 静默吞异常

**修复**:`logger.error(...)` + 显式 `unavailable: true` 标志位 + 前端 toast。**工时**:0.5h

---

### 4.4 [前端-M2] UmiJS `pages/Crawl/OneTime` 轮询不批量化

**修复**:轮询 endpoint 合并为 1 个聚合接口,或用 `Promise.allSettled`。**工时**:4h

---

### 4.5 [前端-M3] `lib/api/client.ts` 每次响应 `import('@/lib/stores/debug-store')` 阻塞

**位置**:`apps/customer/src/lib/api/client.ts::L72-90`

**修复**:用 `process.env.NODE_ENV==='development'` 守卫。**工时**:0.5h

---

### 4.6 [前端-M4] `lib/api/client.ts` L113 401 重定向 `window.location.href` 整页刷新

**修复**:用 SPA 路由 navigate,保留 SWR 缓存。**工时**:0.5h

---

### 4.7 [前端-M5] 跨页 SWR key 不收敛,dashboard/answers/reports 三方重复打同一接口

**修复**:
```typescript
// 统一收敛
export const useQuestionList = (projectId) => 
  useSWR(['questions', projectId], () => getQuestionList({ project_id: projectId }));

// dashboard 改用同一 hook
const { data: questions } = useQuestionList(projectId);  // 命中缓存
```

**工时**:2h

---

### 4.8 [DB-M1] `cms.cases` 表 28 列(12 个双语 TEXT)行尺寸 > 8KB

**症状**:PG 单行 8KB 上限,再加字段会爆。

**修复**:`cases` 主表 + `cases_content_i18n` 子表(按 locale 拆)。**工时**:8h

---

### 4.9 [DB-M2] 物化视图 `weekly_trends / monthly_trends` 无自动刷新

**修复**:用 `pg_cron` 加 `REFRESH MATERIALIZED VIEW CONCURRENTLY` 每 10 分钟。**工时**:4h

---

### 4.10 [DB-M3] 关键 FK 缺 `ON DELETE CASCADE` — 删父表阻塞或留孤儿

`crawl_screenshots / crawl_error_logs / brand_mentions / sentiment_scores / brand_answer_metrics / reference_paragraph_attribution`。

**修复**:加 `ON DELETE CASCADE / SET NULL`。**工时**:6h

---

### 4.11 [前端-M6] `customer` 8+ useState 合并 useReducer

**位置**:`answers/citations` 页面

**修复**:用 zustand 切片 store 或 useReducer。**工时**:4h

---

### 4.12 [前端-M7] 大组件拆分子组件 + React.memo

**位置**:`citations`(847行)、`health-diagnosis`(527行)、`database`(646行)、`brands`(497行)

**修复**:拆分子组件 + memo 纯展示组件。**工时**:8h

---

### 4.13 [后端-M3] **routers 层关键问题(186 端点全扫)**

**审计范围**:34 个 router 文件 / 186 个端点 / 全部 async def / 全部 AsyncSession
**审计产物**:`E:\\workspace\\geo_audit_routers.json` (81KB)

#### 4.13.1 [后端-R1] 28 个长任务用 FastAPI `BackgroundTasks` — **不可靠**

**位置**:
- `admin_crawler.py:create_temp_crawl_task / run_temp_crawl_draft / replay_temp_crawl_task`
- `admin_crawler.py:promote_temp_crawl_task` (数据转正)
- `admin_crawler.py:export_temp_crawl_results` (导出)
- `admin_projects.py:export_project_answers` / `delete_project` (级联删除)
- `admin_reports.py:create_report`
- `client_reports.py:create_report`
- `open_presale.py:create_presale_task`

**症状**:`background_tasks.add_task(...)` 与请求生命周期绑定,**服务重启即丢任务**。爬虫/PDF/CSV 生成、数据转正应入 **Celery/Arq 持久化队列**。

**修复**:
```python
# 现状
@router.post("/create_temp_crawl_task")
async def create_task(bg: BackgroundTasks, ...):
    bg.add_task(sync_crawl, job_id)  # 重启即丢
    return {"status": "started"}

# 修复 - 用 Celery
from celery_app import celery_app

@router.post("/create_temp_crawl_task")
async def create_task(...):
    sync_crawl_task.delay(job_id)  # 持久化
    return {"status": "queued", "task_id": ...}
```

**工时**:16h(基础)+ 28 个端点迁移 | **优先级**:P0 | **影响范围**:爬虫任务可靠性

---

#### 4.13.2 [后端-R2] GET 写操作混进查询路径 — 锁竞争

**位置**:`admin_crawler.py`
- `GET /admin/crawler/temp-tasks/{job_id}`
- `GET /admin/crawler/temp-tasks/{job_id}/progress`
- `GET /admin/crawler/temp-tasks/{job_id}/results`
- `GET /admin/crawler/temp-tasks/{job_id}/export`

**症状**:每次 GET 都先调 `sync_temp_crawl_results_from_answers` **写库**。
- ① 语义错误(GET 应该是幂等的)
- ② 并发轮询时锁竞争严重
- ③ 审计追踪不到

**修复**:把 `sync_temp_crawl_results_from_answers` 移到 POST 触发接口 / 或后台 cron。GET 接口只读不写。

**工时**:4h | **ROI**:★★★★

---

#### 4.13.3 [后端-R3] 31 个高频端点零 Redis 缓存

**位置**:
- `admin_dashboard.py:overview / client_kpi / crawl_today / analysis_status`
- `admin_projects.py:get_geo_scores`
- `client_dashboard.py:overview`
- `client_references.py:stats / top_domains / trend / distribution`
- `client_brand_sub.py:rankings / dynamic_rankings / competitors`
- `auth.py:me` (每次查 client_name + permissions)
- `admin_reference_analysis.py:stats / top_domains / feature-analysis`

**修复**:见 3.14 [架构-H1] Redis 缓存方案。**工时**:包含在 3.14 内。

---

#### 4.13.4 [后端-R4] 路由层权限粒度不一致 — 越权风险(7 处)

| 端点 | 问题 |
|---|---|
| `admin_client_users.py:get_user_projects / update_user_projects` | 用 `require_admin_or_operator` 而非 `_require_admin` → **operator 可改任何用户的项目授权** |
| `admin_api_keys.py:_require_admin` | 定义了**完全没使用**(dead code,CR 不会发现这个漏洞) |
| `admin_crawler.py:complete_temp_crawl_task_from_dcp` | DCP 内网回调**只校验共享 token**,无 IP 白名单/请求签名 → token 泄露即被滥用 |
| `admin_settings.py:test_llm_connection / test_email` | **无显式 role 校验**,任何登录用户都能触发外部 LLM/邮件 |
| `admin_users.py:list_users` | 严格 `_require_admin`(与 client-users 文件的不一致策略) |

**修复**:
1. 统一 `require_admin / require_admin_or_operator / require_client_user` 三档
2. DCP 回调加 IP 白名单 + HMAC 签名
3. `_require_admin` 死代码要么用要么删
4. settings 端点加 `require_admin` 装饰器

**工时**:6h | **ROI**:★★★★(安全)

---

#### 4.13.5 [后端-R5] 13 个别名路由完全重复

**位置**:`admin_crawler.py:temp_tasks_router`

**症状**:`/admin/temp-tasks/*` 与 `/admin/crawler/temp-tasks/*` 是同一组 13 个端点的别名实现。**维护成本翻倍**,每次修改要同步两处。

**修复**:合并 `include_router` 即可消除。**工时**:2h

---

#### 4.13.6 [后端-R6] 15 个端点无分页

**位置**:
- `admin_crawler_servers.py:list_crawler_servers / list_crawler_schedules`
- `admin_dashboard.py:crawl_today`
- `admin_reports.py:get_report_list`
- `client_attribution.py:feature_heatmap`
- `client_brands.py:brand_list` / `client_brand_sub.py:competitors`
- `client_dashboard.py:mention-trend` 等

**修复**:加 `page / page_size` query params,服务端 `limit + offset`。**工时**:8h

---

#### 4.13.7 [后端-R7] 2 处缺 `response_model`

**位置**:
- `admin_dashboard.py:client_kpi` 直接 `return {...} dict`
- `admin_crawler_servers.py:delete_crawler_schedule` `response_model=dict`

**修复**:加 Pydantic `response_model=OperationResponse`,自动文档 + 校验。**工时**:0.5h

---

#### 4.13.8 [后端-R8] 3 个空 stub 文件

**位置**:
- `apps/backend/src/routers/brands.py` — 空 stub
- `apps/backend/src/routers/reports.py` — 空 stub(被 admin_reports 取代)
- `apps/backend/src/routers/visibility.py` — 空 stub

**修复**:删除,合并到对应功能模块。**工时**:0.5h

---

#### 4.13.9 [后端-R9] `auth.py:logout` 无 JWT 黑名单

**症状**:登出后 token 仍可使用至过期。

**修复**:
1. logout 时把 token jti 写入 Redis 黑名单,设置剩余 TTL
2. 中间件检查黑名单
3. 或短期 access token (5min) + refresh token 轮换

**工时**:8h

---

#### 4.13.10 [后端-R10] `auth.py:login` bcrypt 同步阻塞 event loop

**症状**:`verify_password` (bcrypt 同步) 在 async 路径上阻塞事件循环。

**修复**:
```python
ok = await asyncio.to_thread(verify_password, plain, hashed)
```

**工时**:0.5h

---

## 5. Low 级问题(代码质量 + 包体积)

### 5.1 前端死依赖清理 — 总计可省 ~4MB bundle

| App | 死依赖 | 节省 |
|---|---|---|
| `customer` | `echarts` + `echarts-for-react`(grep 0 引用) | ~1MB |
| `admin` | `@antv/l7` + `@antv/l7-react`(grep 0 引用) | ~2.5MB |
| `admin` | `git-url-parse`(0 引用) | ~50KB |
| `admin` | `numeral`(0 引用,可用 `Intl.NumberFormat` 替代) | ~30KB |
| `admin` | `xlsx`(仅 2 处,可后置服务端) | ~400KB |

**修复**:
```bash
cd apps/customer && npm uninstall echarts echarts-for-react
cd apps/admin && npm uninstall @antv/l7 @antv/l7-react git-url-parse numeral
```

**工时**:0.5h | **ROI**:★★★★★(零风险)

---

### 5.2 32 个 alembic 迁移 0 个用 `CREATE INDEX CONCURRENTLY`

**修复**:所有 `op.create_index(...)` 改为 `op.execute("CREATE INDEX CONCURRENTLY ...")` 并在事务外执行。**工时**:12h

---

### 5.3 大量 `except Exception` 静默吞异常

`admin_dashboard.get_analysis_status` / `admin_project_analytics` 等 4 处。

**修复**:加 `logger.exception(...)` + 显式 `unavailable` 标志位。**工时**:2h

---

### 5.4 `docs/sql/` 手动 SQL 脚本与 alembic 重复

`docs/sql/auth-password-recovery/*` 和 `docs/sql/qwen-platform-support/*` 已被迁移替代。

**修复**:归档到 `docs/sql/_deprecated/` 或迁到 alembic。**工时**:1h

---

### 5.5 路由/服务缺缓存响应头(`ETag` / `Cache-Control`)

**修复**:`@router.get(..., response_headers={...})` 或中间件加 `Cache-Control: max-age=60`。

---

### 5.6 admin 全局未配置 `SWRConfig` / `useRequest` cache key

**修复**:用 umi `useRequest` 统一封装,配置 `cacheKey + staleTime + debounceInterval`。

---

### 5.7 [前端安全] JWT 存 localStorage — XSS 一打就中

**位置**:`apps/admin/src/services/auth.ts` + `apps/customer/src/lib/stores/auth-store.ts`

**修复**:迁移到 httpOnly Cookie + refresh 轮换。**工时**:8h | **优先级**:P0-安全

---
'''

with open(REPORT, 'a', encoding='utf-8') as f:
    f.write(content)
import os
print(f'After Part 3: {os.path.getsize(REPORT)} bytes')
