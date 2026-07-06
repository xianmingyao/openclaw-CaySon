"""京麦 WebView Agent。"""

from __future__ import annotations

from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.agents.stateful import StatefulAgent
from jm_ufo_agent.backends.web_surface.coordinate_plan import Rect
from jm_ufo_agent.backends.web_surface.form_loop import WebViewFormLoop


class JmWebViewAgent(StatefulAgent):
    """负责 WebView 截图/OCR/坐标/剪贴板证据。"""

    def __init__(self, form_loop: WebViewFormLoop | None = None):
        """初始化 WebView Agent。"""

        # WebView Agent 只处理观察和局部闭环，不绕过 SafetyPolicy 做发布。
        # form_loop 可注入真实截图/OCR/剪贴板实现。
        # 默认 form_loop 是 dry-run 安全实现，不触碰真实桌面。
        super().__init__(name="jm_webview")
        self.form_loop = form_loop or WebViewFormLoop()

    async def observe_form(self) -> AgentResult:
        """观察当前表单页面。"""

        # 不假设 DOM 或 JS 可写。
        # 通过 form_loop 的 OCR 服务拿页面签名和文本块。
        # 返回数据保留 uia_html_controls=0，强调 HTML 控件默认不可达。
        snapshot = await self.form_loop.ocr.capture_and_ocr()
        return AgentResult(
            ok=True,
            message="webview observation captured",
            data={
                "uia_html_controls": 0,
                "screenshot_path": str(snapshot.screenshot_path) if snapshot.screenshot_path else None,
                "page_signature": snapshot.page_signature,
                "ocr_blocks": [{"text": block.text, "rect": block.rect.__dict__, "confidence": block.confidence} for block in snapshot.blocks],
            },
        )

    async def fill_field_with_surface_loop(self, field_name: str, label_rect: Rect, expected_value: object) -> AgentResult:
        """使用 WebView 表面闭环填写并验证字段。"""

        # 该方法执行截图/OCR/坐标/剪贴板/读回验证完整闭环。
        # 失败时 ok=False，上层 workflow 不应标记字段 verified。
        # evidence 中包含坐标、读回值、局部相似度和页面签名。
        result = await self.form_loop.fill_and_verify(field_name, label_rect, expected_value)
        return AgentResult(
            ok=result.ok,
            message=result.verify_reason if not result.ok else "WebView 字段读回验证通过",
            data={
                "field_name": result.field_name,
                "page_signature": result.page_signature,
                "fill_message": result.fill_message,
                "verify_reason": result.verify_reason,
                "screenshot_path": result.screenshot_path,
                **result.evidence,
            },
        )
