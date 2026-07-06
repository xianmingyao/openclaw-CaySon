# 京麦自主保存草稿工作流：大脑运行规则

日期：2026-06-09

适用场景：`公牛上架.xlsx` 已完成 row5、row6、row7 真实保存草稿，下一步从 row8 继续。目标是让大模型按实战经验自主决策，但只允许保存草稿，不允许发布商品。

## 硬边界

- 真实操作只允许保存草稿。
- 禁止点击 `发布商品`。
- 不能把“点击了按钮”当成成功。
- 每个关键动作后必须截图或读回验证。
- 京麦 WebView 内部 HTML 控件不假设 UIA/DOM/CDP 可用。
- 焦点、页面、字段、图片、枚举不确定时立即停止，不继续猜。

## 入口脚本

双击运行：

```bat
run_jingmai_autonomous_save_drafts.bat
```

默认行为：

- 读取 `D:\xwechat_files\XIANMINGYAO_f7ae\msg\file\2026-06\公牛上架.xlsx`。
- 读取 `docs/live-operations/2026-06-09-jingmai-live-skill-practice-training.md`。
- 读取本工作流文档。
- 使用 `data/live_runs/jingmai_autonomous_state.json` 作为真实 live 进度。
- 如果没有 live state，则只种子化 row5、row6、row7 为已保存草稿。
- 从 row8 开始，最多处理到 row10。
- 默认每次最多处理 3 行；任何一行验证失败立即停止。

调整单次最大行数：

```bat
set JINGMAI_MAX_ROWS=1
run_jingmai_autonomous_save_drafts.bat
```

## 进度规则

真实进度只看 live state 和草稿验证证据，不看 `data/breakpoints`。

原因：`data/breakpoints` 可能来自 dry-run，不能证明京麦真实草稿已保存。

初始事实：

| 行 | 状态 | 证据 |
| --- | --- | --- |
| row5 | 已保存草稿 | `data/screenshots/live_row5_after_save_draft_click_20260609_020310.png` |
| row6 | 已保存草稿 | `data/screenshots/live_row6_after_save_draft_click_20260609_continue.png` |
| row7 | 已保存草稿 | `data/screenshots/live_row7_after_save_draft_click_20260609.png` |
| row8 | 待处理 | 下一行 |

完成一行后，必须更新：

```text
data/live_runs/jingmai_autonomous_state.json
```

状态格式：

```json
{
  "completed_rows": {
    "8": {
      "status": "draft_saved",
      "verified_at": "2026-06-09T...",
      "evidence": ["...screenshot.png"],
      "title": "..."
    }
  }
}
```

## 大脑循环

每一步都按同一个闭环运行：

```text
Observe -> Decide -> Act -> Verify -> Record
```

### 1. Observe

先观察，不先点击：

- 读取 live state。
- 读取 Excel 当前行。
- 检查当前行主图是否存在。
- 确认京麦窗口存在。
- 截图当前页面。
- 判断当前页面是在草稿箱、类目页、基础信息页、图片空间还是文件选择框。

### 2. Decide

决策必须受约束：

- 如果 row8 未完成，则下一行只能是 row8。
- 如果 row8 成功验证后，才允许进入 row9。
- 如果 row9 成功验证后，才允许进入 row10。
- 不能跨过失败行。
- 不能用 dry-run 断点覆盖 live state。

### 3. Act

动作分层：

- 原生层：Windows 窗口、文件选择框、地址栏、原生控件，优先走 UFO/UIA/Win32/WinCOM 底层 action。
- WebView 层：京麦内部 HTML 表单，走截图/OCR/坐标/剪贴板 fallback。
- 图片上传：先进入京麦图片空间，再点 `本地上传`，文件框出现后再粘贴本地图片路径。

每次动作前必须确认目标窗口：

```text
窗口标题包含 jd_465d1abd3ee76
```

如果窗口不在前台，先激活；激活失败就停止。

### 4. Verify

验证优先级：

1. 字段读回。
2. 截图中可见字段值。
3. 下拉框选中态可见。
4. SKU 图片缩略图可见。
5. 保存草稿后草稿箱第一条标题匹配。
6. 编辑时间是本次运行时间。

验证失败时：

- 不标记成功。
- 不进入下一行。
- 保存截图。
- 写入 run log。

### 5. Record

每次运行产物：

```text
data/live_runs/<timestamp>_from_rowX/manifest.json
data/live_runs/<timestamp>_from_rowX/autonomous_prompt.md
data/live_runs/<timestamp>_from_rowX/launcher.jsonl
data/screenshots/...
```

## 字段决策规则

类目坚持：

```text
工业品 > 中低压配电 > 插座
```

平台枚举坚持：

| 字段 | 选择 |
| --- | --- |
| 电线长度 | 6米 |
| 孔型配置 | 16A |
| 额定电压 | 250V |
| 极数 | 2P+E |
| 销售单位 | 套 |
| 包装规格单位 | 套 |
| 商品包装 | 普通商品 |
| 质保期 | 1年质保 |
| 特殊发货时效标记 | 普通品 |

危险商品：

- 不勾选任何危险类型。
- 不为了通过红星乱选危险品。
- 保存草稿让平台校验决定。

价格：

- 京东价：Excel 价格。
- 市场价：`京东价 / 0.85`。
- 采购价：`京东价 * 0.95`。

图片：

```text
data/images/jd_selected/row_<row>_sku_<sku>_main.png
```

## 发布按钮禁区

底部按钮区域中：

- 左侧约 `x=1315,y=1361` 是 `发布商品`，禁止点击。
- 右侧约 `x=1424,y=1361` 是 `保存草稿`，只允许验证后点击。

自动化必须把发布按钮区域视为禁区：

```json
{
  "left": 1260,
  "top": 1320,
  "right": 1370,
  "bottom": 1405
}
```

## 中止条件

出现以下任一情况必须停止：

- 找不到京麦窗口。
- 当前焦点无法切回京麦。
- 当前页面不是预期页面。
- 下拉候选没有授权枚举。
- 文件选择框未出现。
- 图片上传后缩略图不可见。
- 保存草稿后没有进入草稿箱。
- 草稿箱第一条不是当前 row 标题。
- 编辑时间不是本次运行时间。
- 任何动作可能落到发布按钮禁区。

## 完成定义

一行完成必须同时满足：

- 当前 row 商品保存到草稿箱。
- 草稿箱第一条标题匹配当前 row。
- 编辑时间匹配本次运行。
- 有保存后的截图证据。
- live state 标记 `draft_saved`。
- 未点击发布商品。

只有满足以上条件，才允许处理下一行。
