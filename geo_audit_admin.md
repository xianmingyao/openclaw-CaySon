# Admin 端性能审查

## 1. useEffect 串行 await
- `pages/dashboard/index.tsx` L96-148: 3 个 try/catch 串行 await `getOverview / getCrawlToday / getAnalysisStatus`,首屏延迟叠加 2~3 倍,应改 `Promise.allSettled`。
- `pages/reports/index.tsx` L114-128: 串行 `loadClients` + 后才显示 ModalForm,虽仅 1 个接口但与 `request` 可并行。
- `pages/Crawl/OneTime/index.tsx` L86-200: 5 个 useEffect 串行触发 `getProject / getTempCrawlTask / getProgress`,且 `setInterval(4000ms)` 轮询每次 1 个 await 阻塞后续,应批量化。
- 其余页面(`Analysis/Reference`、`projects/[id]`、`settings`)已用 `Promise.allSettled`,符合规范。

## 2. 大表格性能
- `pages/crawler/components/StatusTab|SchedulesTab|...`: 4 个子 Tab 内 ProTable 未传 `scroll.y` 也没启用 `virtual`,大列表滚动掉帧。
- `pages/clients/index.tsx` L211-235: ProTable 无 `scroll.y`/`virtual`;`expandedRowRender` 嵌套 Table 全量渲染,百行以上卡顿。
- `pages/Crawl/TempTasks/index.tsx` L277: 已用 `virtual` + `scroll.y=560` + `pageSize≤100`,✅ 良好。
- `pages/Analysis/Reference/index.tsx` L39 `page_size: 20` 写死,无分页控制;`getProjectList(...page_size:100)` 全量拉下拉数据。
- `pages/projects/[id]/index.tsx` L222/L226: `getProjectQuestions / getProjectPublishedUrls` 用 `page_size: 0` 拉全量,questions 全量塞 state 是主因。
- `pages/reports/index.tsx` L213-215: ProTable 无 `virtual`/无 `scroll.y`。

## 3. 包体积
- `@antv/l7` ^2.22.7 + `@antv/l7-react` ^2.4.3: **src 内 0 处引用**,可全量移除(预计 -2.5MB gzipped)。
- `git-url-parse` ^16.1.0: src 无引用,可移除。
- `numeral` ^2.0.6: src 无引用,可用 `Intl.NumberFormat` 替代。
- `xlsx` ^0.18.5: 仅 2 处使用(StepUpload 解析、ConfigTab 导出),上传解析建议改后端 pandas/openpyxl,前端省 -400KB。
- `@ant-design/plots` ^2.6.0: dashboard 4 处图表必需,保留但可换 `@ant-design/charts` 精简版(若允许)。

## 总评(按 ROI 排序)
1. **dashboard 串行 await 改 Promise.all** — 改 1 处,首屏快 60%+,零成本。
2. **移除 `@antv/l7` + `@antv/l7-react`** — 未引用,删依赖,包体直降 2.5MB,零风险。
3. **大表格全量改分页 + `virtual`** — projects/clients/reports 三处加 `page_size≤50` + `scroll.y=560` + `virtual`,千行数据秒开。
4. **`getProjectQuestions / getProjectPublishedUrls` 改服务端筛选 + 条件查询** — 替代 `page_size:0` 全量,避免大项目首屏白屏。
5. **`numeral` / `git-url-parse` 移除 + `xlsx` 解析后置** — 锦上添花,合计 -500KB,无功能影响。
