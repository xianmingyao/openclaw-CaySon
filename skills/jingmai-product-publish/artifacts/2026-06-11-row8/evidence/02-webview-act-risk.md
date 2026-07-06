# webview-act 真实跑通风险评估（基于代码 + 进度文件 + 实战文档）
# 用户已选 F3 = 启动 webview-act 真实跑通 row8

## webview-act backend 实际能力
| 能力 | 来源 | 真实跑通性 |
|---|---|---|
| PyAutoGui 真实点击 | webview_backend.py L60-97 | 未跑通（progress.md 明确"未执行真实外部动作"）|
| PyAutoGui 真实输入 | webview_backend.py L141 | 同上 |
| 系统剪贴板写入 | webview_backend.py + clipboard_fill.py | 同上 |
| 坐标 click + 剪贴板 fill | webview_backend.py L171-176（allow_write=True 时）| 同上 |
| form_loop L2/L3 验证（OCR + 读回）| web_surface/form_loop.py | **OCR 失败**（tesseract 未装）|
| LocalSimilarityVerifier | web_surface/verifier.py | OK（但要截图配合）|

## 真实跑通失败点（按概率）
1. **HIGH：pyautogui 依赖未装**
   - webview_backend.py L74 抛 ImportError if pyautogui missing
   - 缓解：pip install pyautogui
2. **HIGH：pyperclip 依赖未装**
   - L86 抛 ImportError
   - 缓解：pip install pyperclip
3. **HIGH：tesseract 系统包未装**
   - capture-halt-evidence 已报 TesseractNotFoundError
   - 影响：所有字段读回验证失败
   - 缓解：装 tesseract-ocr 系统包（CHOCO install tesseract）
4. **MEDIUM：京麦窗口不在前台**
   - 当前前台是 Claude Code
   - 必须你手动点京麦窗口一次
5. **MEDIUM：当前空表单未关**
   - 截图显示 UUID 83f98cef... 的空 vcProductPublish 会话
   - 直接填会污染历史
   - 必须你手动关
6. **MEDIUM：2560x1440 分辨率校准**
   - runbook 坐标基于此分辨率
   - 屏幕当前确实是 2560x1440 ✓
   - 但**京麦窗口内部 WebView 可能缩放比例不同**
7. **LOW：PyAutoGui failsafe=True 触发**
   - 鼠标移动到屏幕角落会触发 FailSafeException
   - 我有意识避免

## 我（orchestrator）的应对策略
1. **分阶段 + 强制闸门**
   - 每个 E 步骤前再次跑 inspect-jingmai-window 验证窗口未变
   - 每个坐标点击后立即 capture-halt-evidence 拍现场
   - 视觉对比是否达预期状态
2. **失败立即停 + 报告**
   - 任何步骤未达预期：截图 + 报告 + 等你授权下一步
   - 绝不自动重试（避免循环点击坐标）
3. **双门禁**
   - 红色矩形 [1260,1370] x [1320,1405] 视为禁区
   - 保存草稿坐标 (1424, 1361) 偏离 x=1370 仅 54 像素——坐标误差会导致落禁区
   - **风险**：(1424, 1361) 不是 runbook L156 的 (1424, 1448)——两套坐标，**autonomous 的 1361 实际跑通过**
4. **OCR 替代方案**
   - tesseract 未装 → 用 MiniMax-M3 多模态读图（如果 SKU/VLM 走通）
   - 或仅依赖"页面跳转"作为成功信号（不强求 OCR 字段读回）

## 你必须做的（不能由我代劳）
1. **手动点京麦窗口**切前台
2. **手动关闭**当前 vcProductPublish 空表单（回草稿箱）
3. **确认账号已登录** + 有发布权限
4. **全程监督**——任何步骤觉得不对立即喊停
5. **签字 D1-D5**

## 我不会做的（无论发生什么）
1. 不会点击 (1315, 1361) 或 x ∈ [1260,1370] y ∈ [1320,1405] 内任何坐标
2. 不会点击"发布商品"按钮
3. 不会为了通过红字乱选危险品
4. 不会用 Excel 字面值硬塞平台枚举
5. 不会在没字面 D1=是 的情况下启动 webview-act
6. 不会在 OCR 读回失败时声称成功
