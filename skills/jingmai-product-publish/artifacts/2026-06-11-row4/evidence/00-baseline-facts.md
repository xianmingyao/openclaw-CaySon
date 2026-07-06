# 2026-06-11 row4 现场事实（来自 inspect-jingmai-window + 环境采集）
# 用途：开始真实操作前留证，对比 06-08/06-09 实战基线。

## A. 屏幕与系统
- 屏幕分辨率：2560 x 1440（与 runbook L152 校准一致 ✓）
- 京麦进程：PID 42652，MainWindowHandle=400532
- 京麦窗口类：Qt51511QWindowIcon（Qt51511QWindowIcon + CefBrowserWindow x2 + Chrome_WidgetWin_0 x2 + Chrome_RenderWidgetHostHWND）
- Qt 子窗口数：42
- WebView pane 数：5

## B. UIA 探测（html_button_count / html_edit_count / html_combobox_count 全部 = 0）
结论：WebView 内部 HTML 控件**不暴露 UIA**。只能走 L1→L2→L3 fallback：
  L1: 原生 Qt/UIA 控件（地址栏、按钮壳）
  L2: WebView 坐标 + 剪贴板
  L3: 截图 + OCR + 剪贴板三连

## C. UFO 源码可适配性（inspect-ufo 输出）
- ufo_root: E:\PY\UFO\ufo（root_exists: true）
- ready_for_observe: true
- ready_for_write: true（**理论上可写，但需 --confirm-real-jingmai 显式开启**）
- capabilities: action_execution, clipboard, controller, inspector, native_dialog, screenshot, ui_tree 全在
- missing_capabilities: []

## D. 前台窗口检查（关键）
- 采集时刻：2026-06-11 ??:??:??
- Foreground HWND: 723436（= Claude Code 窗口）
- Title: "jingmai-product-publish — Claude: 5e213e2d"
- Rect: (-32000,-32000)-(-31840,-31972)（在屏幕外）
- 结论：**京麦未在前台**。需要用户手动点击京麦窗口切前台。

## E. 与 06-08/06-09 实战基线对比
| 项 | 06-08 实战 | 06-09 row5 | 06-09 row6 | 06-09 row7 | 本次采集 |
|---|---|---|---|---|---|
| 屏幕 | 2560x1440 | 2560x1440 | 2560x1440 | 2560x1440 | 2560x1440 ✓ |
| 京麦前台 | 是 | 是 | 是 | 是 | ❌ 否 |
| UFO ready | - | - | - | - | true（理论）|
| 真实实现 | 旧版 jingmai_publisher | 同左 | 同左 | 同左 | 当前 jm_ufo_agent（未连真实端到端）|
| row4 已保存 | 草稿 100282053911 | - | - | - | 待做 |

## F. 阻塞项（任一未解除即不能启动 E1）
1. D1 用户确认：仅保存草稿，不点发布 — ❌ 未确认（用户答"开始"≠"是"）
2. D2 京麦切前台 + 登录 + 权限 — ❌ 未确认
3. D3 主图本地路径 — ❌ 未提供
4. D4 电线长度平台枚举 — ❌ 未选

## G. 一旦 D1-D4 全部解除将立即执行
- E1 二次前台检查（HWND 标题含 jd_465d1abd3ee76）
- E2-E12 按双签确认单逐步骤执行
- 全程截图到 artifacts/2026-06-11-row4/evidence/
- 全程**永不点击「发布商品」**
