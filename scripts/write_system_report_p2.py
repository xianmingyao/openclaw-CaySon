"""Write GEO-Platform system report - PART 2: 根因分析 + 风险评估"""
# -*- coding: utf-8 -*-

OUT = r'E:\workspace\GEO-Platform-系统诊断与优化建议.md'

content = '''
## 2. 🔍 问题根因分析(老炮溯源)

### 2.1 6 大根因(按影响范围排序)

#### **根因 #1:零缓存层 — 触发 79% 的 High 问题**

**症状**:`global_findings.files_with_cache = []`(14 个 client_*.py 全部零缓存)

**根因**:9 个月的快速迭代中,没人停下来引入 Redis。每个接口都直查 DB,导致:
- N+1 查询放大 10-20 倍
- 串行 await 累积延迟
- DB 连接池占满
- 慢查询雪崩

**24 年老炮视角**:
> 没有缓存层,任何 ORM 优化都是杯水车薪。SQL 写得再漂亮,1ms 一次查询,10 次串行就是 10ms,但如果 100 并发就是 1 秒,DB 端就 OOM 了。**缓存是性能优化的"水冷系统"**——没有它,CPU 跑得再快也会烧。

**修复策略**:
```
1. 引入 Redis(8h)
2. 装饰 31 个高频只读端点(16h)
   - /admin/dashboard/* (4 个)
   - /client/dashboard/* (3 个)
   - /client/brands/* (3 个)
   - /client/references/* (4 个)
   - 其他(17 个)
3. 按数据稳定性分级 TTL:
   - admin profile:1h
   - dashboard 概览:5min
   - 列表:30s
   - 实时数据(答案列表):不缓存
```

**预期收益**:QPS 提升 5-10x,DB 压力降低 50-70%

---

#### **根因 #2:数据库欠设计债 — 200 个 schema/索引问题**

**症状**:
- 14 张表 JSONB 字段 **0 张 GIN 索引**
- 5 张高写入核心表完全未分区
- 缺失 UNIQUE 约束导致笛卡尔积 bug 重现风险
- 14 张高读取表无业务索引
- 关键 FK 缺 `ON DELETE CASCADE`

**根因**:alembic 迁移主要服务"加字段",**没人 review "查询模式 vs 索引"**。

**24 年老炮视角**:
> "没有索引的查询 = 慢慢慢;没有分区的表 = 长大后炸;没有 UNIQUE 的关联 = 明天重复今天的 bug"。这 3 个债会**复利增长**,数据量 10x 后直接翻车。

**修复策略**:
```sql
-- 一次性创建所有缺失的索引(2h)
CREATE INDEX CONCURRENTLY idx_brand_mentions_client_project_date 
  ON analysis.brand_mentions (client_id, project_id, batch_date DESC);
-- ... 14 张表 × 平均 2-3 个索引 = 30+ 个 CONCURRENTLY 索引

-- 加 UNIQUE 防笛卡尔积(2h)
CREATE UNIQUE INDEX CONCURRENTLY uq_brand_answer_metrics
  ON analysis.brand_answer_metrics (project_id, target_platform, batch_date, batch_round)
  WHERE batch_round IS NOT NULL;

-- 5 张高写入表按月分区(16h,需要停机窗口)
ALTER TABLE crawler.crawl_answers 
  PARTITION BY RANGE (batch_date);
-- ... 4 张表同样操作

-- 14 张 JSONB 加 GIN 索引(4h)
CREATE INDEX CONCURRENTLY idx_projects_brand_aliases_gin 
  ON platform.projects USING GIN (brand_aliases jsonb_path_ops);
```

**预期收益**:查询性能 10-100x 提升,数据 10x 后不崩

---

#### **根因 #3:代码模式反模式 — async 上下文跑同步代码**

**症状**:
- `admin_temp_crawler` 用 `create_engine` 同步引擎跑在 `async def` 里,**阻塞 event loop 10 分钟**(P0 已修)
- `client_answers` 1 万行 `openpyxl.save` 阻塞 event loop 几百 ms(P0 已修)
- `auth.login` bcrypt 验证阻塞 event loop ~200ms(P0 已修)
- `RequestLoggingMiddleware` 每个请求同步 DB INSERT(P0 待修)

**根因**:**团队对 async/sync 边界的纪律不严**。async 上下文里写 `requests.post()` / `psycopg2.commit()` / `openpyxl.save()` / `bcrypt.hashpw()` 都是反模式。

**24 年老炮视角**:
> 这是 async Python 最容易踩的坑。Python 的 GIL 让人误以为"反正只有一个线程",但 async 是协作式多任务,**任何同步 I/O 都会 block 整个 event loop,所有其他请求全部卡死**。诊断金句:**"async 函数里看到 `await` 之外的操作,先怀疑是 I/O"**。

**修复策略**:
```python
# 1. CPU 密集型(bcrypt / openpyxl / 加密):用 to_thread
content = await asyncio.to_thread(build_workbook, rows)

# 2. 阻塞 I/O(httpx sync / requests / 文件):用 async 库
async with httpx.AsyncClient() as client:
    r = await client.post(url, ...)

# 3. 旧 sync DB 函数(psycopg2):用 to_thread
result = await asyncio.to_thread(sync_query_function, params)

# 4. 全异步:用 asyncpg + SQLAlchemy async + async session
async with async_session() as session:
    await session.execute(...)
```

**纪律建议**:
- code review 必查项:`async def` 函数里**有无同步 I/O**
- 添加 ruff rule:`RUF006 - asyncio-dangling-task`
- CI 加 `pytest-asyncio` + 测试:模拟 100 并发,如果 `event loop blocked > 100ms` 报警

**预期收益**:所有接口快 10-30%,生产稳定性大幅提升

---

#### **根因 #4:缺失异步任务队列 — 28 个长任务裸奔**

**症状**:导出 / 爬虫 / 同步 / 报告生成等 28 个长任务用 FastAPI `BackgroundTasks`,**服务重启即丢**

**根因**:FastAPI `BackgroundTasks` 与请求生命周期绑定,适合"请求结束顺手做"的小事,**不适合分钟级任务**。

**24 年老炮视角**:
> 这是 SaaS 系统的隐形炸弹。每次发布/扩容/重启,**正在跑的导出任务全部丢失**。客户视角:"我付了钱你给我做一半?"。这类 bug 不会立刻报错,但累积会变成客诉。

**修复策略**:
```python
# 现状(不可靠)
@router.post("/export")
async def export(bg: BackgroundTasks):
    bg.add_task(generate_csv, data)  # 重启即丢
    return {"status": "started"}

# 修复(可靠)
from celery_app import celery_app

@router.post("/export")
async def export():
    task = celery_app.send_task("generate_csv", args=[data])
    return {"status": "queued", "task_id": task.id}

# 客户端可查询进度
@router.get("/export/{task_id}/status")
async def status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    return {"status": result.status, "progress": result.info}
```

**Celery 基础设施**:
- Redis 作 broker + result backend(可与缓存层共用)
- 4 worker pool(导出 / 爬虫 / 同步 / 报告)
- 失败重试 3 次 + 死信队列
- 任务进度回调到 WebSocket/SSE

**预期收益**:服务重启不再丢任务,任务可查询/可重试,客户满意度提升

---

#### **根因 #5:缺失可观测性 — 出了问题靠 log 肉眼看**

**症状**:
- 无 OpenTelemetry / Sentry 集成
- 无结构化日志(JSON)
- 无慢查询监控(`pg_stat_statements` 没装)
- 无 QPS / P95 / P99 监控
- `RequestLoggingMiddleware` 同步写日志反而拖慢所有请求(P0 待修)

**根因**:**没时间搭**。9 个月都在堆功能,没时间做"运维视角"的事。

**24 年老炮视角**:
> "没有监控的系统 = 蒙眼开车"。生产环境出问题,只能 SSH 上服务器 `tail -f` log,然后人工关联。一个分布式请求经过 5 个服务,**没 trace ID 就只能猜**。

**修复策略**:
```
1. 引入 Sentry(2h) - 错误捕获 + 性能监控
2. 引入 OpenTelemetry(8h) - 分布式追踪
3. 启用 pg_stat_statements(1h) - 慢查询自动记录
4. 中间件改异步批量写(4h) - RequestLoggingMiddleware 优化
5. JSON 结构化日志(2h) - loguru + json formatter
6. 健康检查升级(2h) - /health 包含 DB/Redis/Celery 状态
```

**预期收益**:生产问题定位从 30 分钟降到 5 分钟,慢查询自动告警

---

#### **根因 #6:安全债 — 4 类可被攻击的漏洞**

**症状**:
- JWT 存 localStorage(XSS 一打就中)
- DCP 回调只校验共享 token(无 HMAC 签名)
- 7 处越权/权限不一致
- `JWT_SECRET_KEY` 默认值 `"change-me-in-production"`(没改就上生产 = 灾难)
- 无 API 限流(无 slowapi,可被暴力破解)

**根因**:开发模式没重视安全,生产化时没做安全审计。

**24 年老炮视角**:
> 安全债是**最容易累积、最难还**的债。**等出了问题再补,代价是事前的 100 倍**。JWT_SECRET_KEY 默认值是最容易踩的坑——一旦泄露,所有 token 可伪造。生产前必须改。

**修复策略**:
```python
# 1. JWT 迁 httpOnly Cookie + refresh 轮换(8h)
# 2. DCP 回调加 HMAC 签名 + IP 白名单(4h)
# 3. 7 处权限统一(6h):
#    - admin_client_users.require_admin_or_operator → require_admin
#    - admin_api_keys._require_admin 死代码修复或删除
#    - admin_settings 加 require_admin
#    - admin_users.list_users 与 client-users 策略对齐
# 4. config.py JWT_SECRET_KEY 加启动时强校验(1h)
# 5. 引入 slowapi 限流(2h)
# 6. 安全扫描:见 Snyk / npm audit / pip-audit
```

**预期收益**:通过等保 2.0 / SOC 2 审计,客户合规需求能接

---

### 2.2 根因因果链(老炮视角)

```
【业务快速增长】
       │
       ↓
【快速堆功能,无基础设施】
       │
       ├─→ 零缓存 ───────→ N+1 / 串行 / 慢查询 ──→ DB 压力 ↑
       ├─→ 零任务队列 ────→ 长任务裸奔 ──────────→ 任务丢失
       ├─→ 零监控 ────────→ 问题定位慢 ──────────→ 故障恢复慢
       ├─→ 零安全审计 ────→ 漏洞累积 ────────────→ 安全事件
       │
       ↓
【债越欠越多,系统变慢,团队变累,业务受阻】

       ✅ 解药:补基础设施(缓存 + 队列 + 监控 + 安全)
```

**老炮金句**:
> "基础设施是技术债的**复利**——欠的越久,还的越贵。**今天不补,明天加倍**。"

---
'''

with open(OUT, 'a', encoding='utf-8') as f:
    f.write(content)
import os
print(f'Part 2: {os.path.getsize(OUT)} bytes')
