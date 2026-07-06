# Client Services 性能审查

## Critical

- `client_answers.py::get_answer_list:~455-490` — N+1: 对每条 answer 在 for 循环里串行执行 2 个 await db.execute() (BrandMentions + SentimentScores)。page_size=20 时约 41 次 round-trip (N+1)
  Fix: 复用 `get_answer_export_file` 已有的子查询模式，一次 LEFT JOIN mention_subquery + sentiment_subquery，0 个 per-row 查询
- `client_brand_sub.py::get_brand_mentions:76-78` — 无界分页: `if page_size > 0` 才加 LIMIT/OFFSET，传 `page_size=0` 返回 crawl_answers 全表 (含 `mention_context`/`question_content` 大字段)
  Fix: 强制 `LIMIT max(1, page_size)`, 移除 "返回全部" 分支 (前端不应请求全量)
- `client_answers.py::get_answer_list:376-377` — 无界分页: 同样 `if page_size > 0` 才 LIMIT，可绕过返回 crawl_answers 全表
  Fix: 同上强制 limit；前端禁用 page_size<=0
- `client_brands.py::get_brand_list:78-100` — N+1: 对每个 brand 循环内 2 个 await (monitored_platforms COUNT + QuestionPool COUNT)，M 个品牌 = 1+2M 次查询
  Fix: 单条 GROUP BY 查询 `SELECT project_id, COUNT(DISTINCT target_platform) AS mp, COUNT(qp.id) AS qc FROM ... LEFT JOIN question_pool ... GROUP BY project_id`
- `client_profile.py::_get_admin_profile:135-170` & `_build_profile_projects:235-280` — N+1: 每 project 2 个 await (Competitors + QuestionPool COUNT)，N 个项目 = 1+2N
  Fix: 用 `WHERE project_id = ANY(:ids)` 批量取 competitors 和 question_count 两个聚合

## High

- `client_dashboard.py::get_overview:~85-220` — 串行 await: 12 个独立 db.execute 顺序执行，每个 ~5ms round-trip 累积 ~60ms
  Fix: `asyncio.gather(*[db.execute(q) for q in queries])` 并发；period 区段不变
- `client_brands.py::get_brand_detail:~140-360` — 串行 await: 14 个独立 db.execute (gpower/mentions/avg_position/mention_rate/sentiment/rec 当前+历史)，platform filter 下仍全串行
  Fix: 用 `asyncio.gather` 或合并为单条带 CASE WHEN 的聚合 SQL (current+prev 用 UNION ALL 一次查)
- `client_references.py::get_citation_stats:180-220` — 串行 await: daily_row 和 attribution_row 独立但顺序执行
  Fix: `asyncio.gather` 并发；若两路都为空再调 `_get_crawl_answer_reference_stats` (保持 fallback 逻辑)
- `client_comparison.py::get_brand_comparison:70-185` — 串行 await: 5 个独立聚合查询 (freq/rate/rank/sentiment/rec) 顺序执行
  Fix: `asyncio.gather` 并发 5 个查询
- `client_answers.py::get_answer_export_file:~285-360` — sync I/O in async: `_build_answer_export_workbook` 调用 openpyxl 同步 `workbook.save(BytesIO)` 处理最多 10k 行，阻塞 event loop
  Fix: 把 openpyxl/csv 写入包到 `asyncio.to_thread(...)` 中执行

## Medium

- `client_references.py::get_top_domains / get_citation_trend / get_domain_distribution` — 3 段 fallback 顺序 await (主→rpa→answer)，仅在主结果为空时触发但仍 ~2 倍 RTT
  Fix: 用 `asyncio.gather` 并发三路查询，按优先级选非空结果；或加 `EXISTS` 短路判断
- `client_api_keys.py::list_api_keys:165-175` — N+1: 对每条 api_key 调 `await open_api_permissions.list_api_key_resource_keys(db, row.id)`
  Fix: 一次 `SELECT api_key_id, resource_key FROM ... WHERE api_key_id = ANY(:ids)` 然后 group by
- `client_attribution.py::get_feature_heatmap:530-540` — 串行 await (主+fallback)，仅在主结果空时触发
  Fix: 保留顺序但用 `asyncio.gather` 并发两路 (主优先) + 取先到非空
- `client_access_scope.py::resolve_access_scope_context:155-165` — operator 角色循环 await `_list_project_ids_for_client`，client scope N 个时串行 N 次
  Fix: 一次 `SELECT client_id, project_id FROM ... WHERE client_id = ANY(:ids)` 一次拿齐
- `client_reports.py::create_report_for_scope` — 串行 await `resolve_scoped_project_id` + `report_service.create_report`，后者内部也有 query
  Fix: 合并为单事务一次查询 + 复用 scope 元数据

## 总评

1. **N+1 是头号问题**: client_answers / client_brands / client_profile 三处列表端点都是 `1+2N` 模式，必须改为聚合子查询或 `WHERE id = ANY(:ids)` 批量
2. **无界分页是生产风险**: client_answers 和 client_brand_sub 都接受 `page_size=0` 返回全表，应移除该分支并强制最小 limit (如 1, max=200)
3. **串行 await 普遍**: client_dashboard / client_brands / client_comparison / client_references 都是独立查询串行执行，加 `asyncio.gather` 可降 50-70% 延迟
4. **导出接口的同步 openpyxl 写入**会阻塞 event loop 几百 ms，应挪到 `asyncio.to_thread`
5. **client_api_keys.list_api_keys 的资源键查询**是次要 N+1，统一改批量
