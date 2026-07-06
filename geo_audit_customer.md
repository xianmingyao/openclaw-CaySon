# Customer 端性能审查

## 1. 页面级 SWR / 数据获取
- `dashboard/page.tsx`:6 个 useSWR(overview/trend/dist/recentAnswers/questions/subscription),并行 ✓;问题:`useRecentAnswers` + `useDashboardQuestions` 键分别与 `answers/page.tsx` 的 `useAnswerList` / `useQuestionList` 不共享,跨页去重失败
- `answers/page.tsx`:4 个 useSWR 并行 ✓;`useSubscription()`(全局 key `'client-subscription'`)与 dashboard 已命中缓存,但 `useQuestionList`(键 `['questions',projectId]`)与 dashboard 的 `useDashboardQuestions`(键 `['dashboard-questions',projectId]`)重复打同一接口
- `citations/page.tsx`:6 个 useSWR 并行 ✓;但 `useFeatureHeatmap` / `useTopArticles` 在 `overview` tab 时已发起请求,tab 切换没有按需触发,首屏即付出 ~6 个并发
- `visibility/page.tsx`:2 个 useSWR 并行 ✓;但 IIFE 内构造 `trendData/trendBrands/brandColorMap` 每渲染重建,触发 Recharts 子树 diff
- `brands/page.tsx`:2 个 useSWR 并行 ✓;`effectivePlatform` 由 `useMemo` 派生但 `brandId` 通过 `String(currentProjectId)` 即时拼装,无 memo
- `reports/page.tsx`:4 个 useSWR 并行 ✓;同时拉 `useDashboardQuestions` + `useRecentAnswers` + `useSubscription`,与 dashboard/answers 三方去重均失败

## 2. API client 层
- `lib/api/client.ts` L72-90、L138-156:**每次**响应(成功/失败)都 `import("@/lib/stores/debug-store")`,生产环境仍执行;首次触发动态 import 阻塞微任务,且每请求额外 `JSON.stringify(response.data)`(最多 500 字符截断重复)
- `lib/api/client.ts` L113:401 重定向用 `window.location.href`,整页刷新丢失 SWR 缓存
- 全局未配置 `<SWRConfig>`(`dedupingInterval` / `focusThrottleInterval` / `errorRetryInterval`),全部依赖默认值,跨 tab 切换可能误重拉
- `services/dashboard.ts` `getGpowerTrend` L84-93:每次调用并发 7 个请求(`all` + 6 平台),周期切换时无前端缓存
- 所有 services 文件未做 **stale-while-revalidate** 包装或接口级 `next: { revalidate }`,重复访问完全走网络
- `services/answers.ts` `getAnswerList` mock 分支与真实分支各自实现 `filterMockAnswers` / 过滤路径,代码与真接口逻辑并行,易产生字段不一致 bug

## 3. 重复渲染
- `dashboard/page.tsx` L267-283:`enrichedPlatformDist`、`formattedTrend`、`recentAnswers`、`questions` 均在渲染体里 `.map()` / 强制类型转换,无 `useMemo`;`periodOptions`/`platformConfig` useMemo 依赖 `[t]`,若 `useI18n` 返回的 `t` 非稳定引用则每次重算
- `citations/page.tsx` L289-294:`filterParams` 每次渲染新建对象后 spread 传入 5 个 hook(hook 内部仅解构基本字段,实际不影响 SWR key,但参数对象浪费 GC)
- `visibility/page.tsx` L188-200:渲染体里 IIFE `(() => { ... })()` 同时建 `trendData`/`brandColorMap`,Recharts 每渲染 diff 一遍
- `answers/page.tsx` L256-292:`columns` 数组在渲染体内逐字段 `columnHelper.accessor(...)`,组件树 `<GeoDataTable columns={columns}>` 每渲染触发 TanStack table 重新初始化(useMemo 化是必须)
- `brands/page.tsx` `ComparisonChart` 子组件:`hiddenBrands` 用本地 `useState`,每次切品牌图例都触发整个 5 图卡重渲
- 各页 `mouseEnter`/`mouseLeave` 内联手写 style 修改(`(e.currentTarget).style.backgroundColor = ...`)未 ref 化,触发 React 协调

## 4. 包体积 / 启动优化
- `package.json` L25-26:`echarts` + `echarts-for-react` 全仓 **零引用**(grep 不到 import),纯死依赖,~1MB+;直接移除
- `app/layout.tsx` L11-29:三个 `localFont` 同步加载,其中 `WorkSans-Variable.ttf` 为 TTF(~150KB),应转 WOFF2 + `display: swap`;`fraunces` 仅 400-700 字重但加载完整 variable
- `app/layout.tsx` L42-47:`await headers()` + `hasLocale` 强制整个布局为 dynamic,**所有页面失去静态优化**;URL 已有 `locale` 段,直接读 `params` 即可
- `app/layout.tsx` L49-50:`dangerouslySetInnerHTML` 内联 console.log 脚本阻塞首屏
- `recharts`(~100KB gz)在 4 个图表页顶部静态 import;未用 `next/dynamic` 切包,首屏 JS 体积爆炸
- `axios`(~30KB)与 `swr` 各页同步引入,登录页/平台页都吃到
- `@tanstack/react-table` ~50KB 全量打入,实际只 `answers` 页用
- 多个页面图表 lazy 候选:`echarts-for-react`(若保留)用 SSR 关闭的 dynamic import

## 总评(按 ROI)
1. **删除 `echarts` + `echarts-for-react`**:零引用死代码,移除直接省 ~1MB 安装包和 tree-shaking 后 ~150KB bundle,零风险
2. **`layout.tsx` 移除 `await headers()`**:取消动态渲染,所有页面可静态化,首屏 TTFB 立竿见影
3. **`recharts` 改 `next/dynamic` + `ssr:false`**:dashboard/brands/visibility/citations 4 个页首屏 JS 立降 60-80KB;同步把三个 localFont 转 WOFF2 + `display: swap`
4. **统一 SWR `<SWRConfig>` 配置 + 跨页 key 收敛**:在根 layout 注入 `dedupingInterval: 60_000` / `focusThrottleInterval: 300_000`,并把 `useDashboardQuestions` / `useQuestionList` 收敛到同一 `['questions',projectId]`,消除 dashboard↔answers↔reports 三方重复请求
5. **`columns`/派生数据 useMemo 化**:`answers/page.tsx` 的 columns、`dashboard` 的 `enrichedPlatformDist/formattedTrend`、`visibility` 的 IIFE 全部改 `useMemo`,TanStack table 与 Recharts diff 成本显著下降;顺便移除 `client.ts` 每次响应的 `import('@/lib/stores/debug-store')` 调试日志(放 `process.env.NODE_ENV==='development'` 守卫后)