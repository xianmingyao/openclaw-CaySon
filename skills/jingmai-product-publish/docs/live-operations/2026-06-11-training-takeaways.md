# 实战培训吸收总结（2026-06-11）
来源：docs/live-operations/ 5 篇文档

## 数据源澄清（最关键发现）

| 数据源 | 路径 | 状态 | 真实形态 |
|---|---|---|---|
| 湖南上架表格.xlsx | E:\workspace\skills\jingmai-product-publish\ | ✅ 存在 | **1 行商品**（row4 公牛 B5440）|
| 公牛上架.xlsx | D:\xwechat_files\XIANMINGYAO_f7ae\msg\file\2026-06\ | ✅ 存在 | **6 行商品**（row5-row10 公牛 GN-806DN/GN-805D 各种米数）|
| 自主循环 workflow 数据源 | 公牛上架.xlsx | 默认 | row5/6/7 已保存草稿，row8 是下一行 |

**结论**：A 路径"row5/6/7 小批量闭环 → row82"的真实数据源是 `公牛上架.xlsx`，
不是 `湖南上架表格.xlsx`。
- row4（湖南表格）= 第一次跑通的"试水行"
- row5/6/7（公牛表格）= 真实批量跑通的三行
- row8+（公牛表格）= 自主循环的下一行

## 公牛上架.xlsx 解析结果

| Excel 行 | row_index | 商品名 | 品牌 | 型号 | 长mm | 宽mm | 高mm | 重kg | 单位 | 京东价 | 京东链接 | 状态 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 5 | GN-806DN 线盘 30米带漏保+3*2.5 | 公牛 | GN-806DN | 100 | 100 | 100 | 11 | 个 | 842.7 | item.jd.com/10220710592599.html | ✅ 已保存（2026-06-09 row5）|
| 6 | 6 | 805D 30米 3*2.5 过热保护+漏保 | 公牛 | GN-805D | 930 | 320 | 152 | 9.67 | 个 | 1156.3 | item.jd.com/10224495969016.html | ✅ 已保存（2026-06-09 row6）|
| 7 | 7 | 805D 50米 3*2.5 过热保护+漏保 | 公牛 | GN-805D | 930 | 320 | 152 | 12.83 | 个 | 1465 | item.jd.com/10224495969015.html | ✅ 已保存（2026-06-09 row7）|
| 8 | 8 | **GN-806DN 50米带漏保+3*2.5** | 公牛 | GN-806DN | 100 | 100 | 100 | 12.3 | 个 | 1232 | item.jd.com/10220710592600.html | ⏳ 待处理 |
| 9 | 9 | GN-806DN 30米带漏保+3*1.5 | 公牛 | GN-806DN | 100 | 100 | 100 | 7.9 | 个 | 707.7 | item.jd.com/10220710592597.html | ⏳ 待处理 |
| 10 | 10 | GN-806DN 50米带漏保+3*1.5 | 公牛 | GN-806DN | 362 | 440 | 196 | 7.9 | 个 | 936.6 | item.jd.com/10220710592597.html | ⏳ 待处理 |

row4 是模板行（不是真实商品）。row5-row10 是 6 行真实商品。

## 实战坐标 fallback（2560x1440 校准）

| 动作 | 坐标 | 来源 |
|---|---|---|
| +发布商品 | (2160, 174) | runbook.md L156 |
| 类目搜索框 | (1280, 230) | runbook.md L157（实测 154 太高）|
| 搜索结果"插座" | (744, 270) | runbook.md L158 |
| 下一步 | (1280, 1314) | runbook.md L159 |
| **保存草稿** | **(1424, 1361)** | autonomous L196 |
| **发布商品（禁区）** | **(1315, 1361)** | autonomous L195 |
| 发布按钮矩形禁区 | left=1260, top=1320, right=1370, bottom=1405 | autonomous L200-207 |

## 字段决策表（autonomous workflow L161-170）

| 字段 | 选择 |
|---|---|
| 类目 | 工业品 > 中低压配电 > 插座 |
| 电线长度 | 6米（row5/6/7 实战授权；**row8 是 50米，需要再次确认**）|
| 孔型配置 | 16A |
| 额定电压 | 250V |
| 极数 | 2P+E |
| 销售单位 | 套（row4 实战用"个"是因为类目枚举差异）|
| 包装规格 | 1 |
| 包装规格单位 | 套 |
| 商品包装 | 普通商品 |
| 质保期 | 1年质保 |
| 发货时效 | 普通品 |
| 危险品 | 不勾（让平台校验）|

## 价格公式（autonomous L181-183）

- 京东价：Excel
- 市场价：京东价 / 0.85
- 采购价：京东价 * 0.95

row8 验证：
- 京东价 1232
- 市场价 = 1232 / 0.85 = 1449.41
- 采购价 = 1232 * 0.95 = 1170.4

## 图片策略（autonomous L187-189 + runbook L298-310）

- 默认路径：`data/images/jd_selected/row_<row>_sku_<sku>_main.png`
- 实际 row5 用：`E:\jingmai-product-publish\data\images\jd_selected\row_5_sku_10220710592599_main.png`
- **当前 data\images 目录不存在** ← 阻塞
- 上传流程：SKU → +添加 → 京麦图片空间 → 本地上传 → 文件框粘贴路径

## 硬边界 7 条（autonomous L8-15 + SKILL.md L449-451）

1. 真实操作只允许保存草稿
2. 禁止点击「发布商品」
3. 不能把"点击了按钮"当成成功
4. 每个关键动作后必须截图或读回验证
5. WebView 内部 HTML 控件不假设 UIA/DOM/CDP 可用
6. 焦点/页面/字段/图片/枚举不确定时立即停止
7. 平台枚举优先于 Excel 字面值，冲突留痕

## Verified Action Ladder（verified-actions.md L10-14）

- L1 Native：UIA/Win32/WinCOM + set_edit_text
- L2 WebView：坐标 + 剪贴板粘贴 + focused-text 读回
- L3 UFO-style：set_text / type_keys / 剪贴板三连

**铁律**：只有 verified action 报告成功才能标 FILLED；否则截图留证，workflow 不能 set FILLED。

## Observe → Decide → Act → Verify → Record 循环（autonomous L83）

- Observe：读 live state + Excel + 当前行主图 + 京麦窗口 + 截图 + 判断页面
- Decide：受约束决策（不能跨过失败行）
- Act：原生层 vs WebView 层 vs 图片上传
- Verify：字段读回 / 截图 / 下拉选中 / 图片缩略图 / 草稿箱标题 / 编辑时间
- Record：data/live_runs/<timestamp>_from_rowX/ + 截图

## 中止条件 9 条（autonomous L210-222）

- 找不到京麦窗口
- 焦点无法切回
- 当前页面不是预期
- 下拉候选无授权枚举
- 文件选择框未出现
- 图片上传后缩略图不可见
- 保存草稿后没进草稿箱
- 草稿箱第一条不是当前 row
- 编辑时间不是本次
- 任何动作可能落到发布按钮禁区

## 完成定义 6 条（autonomous L226-233）

- 当前 row 商品保存到草稿箱
- 草稿箱第一条标题匹配
- 编辑时间匹配本次运行
- 有保存后的截图证据
- live state 标记 draft_saved
- 未点击发布商品

## 致命真相（live state 揭露）

```json
{
  "status": "blocked",
  "halt_node": "FILL_AND_VERIFY_FIELDS",
  "blockers": ["title: 必填字段为空"],
  "root_cause": "jm-ufo-agent 的 production.py 硬编码了 observe_only 强制门控，
                 即使传入 --confirm-real-jingmai 也无法解除。
                 自动化填写/保存功能尚未实现。"
}
```

**jm-ufo-agent CLI 当前不能跑真实填表+保存草稿**。
必须由 orchestrator（我）按 runbook L52-71 的 14 步流程，
**手动驱动** Win32/UIA/截图/坐标 fallback。
