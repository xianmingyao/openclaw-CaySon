"""观察策略。"""

from __future__ import annotations

from typing import Any

from jm_ufo_agent.agents.jm_webview import JmWebViewAgent


class ObserveStrategy:
    """收集页面证据，不做成功推断。"""

    def __init__(self, webview_agent: JmWebViewAgent | None = None):
        """初始化观察策略。"""

        # webview_agent 可注入真实截图/OCR能力。
        # 默认使用 dry-run Agent，返回稳定的空观察。
        # 策略层只收集证据，不修改业务状态。
        self.webview_agent = webview_agent or JmWebViewAgent()

    async def observe(self) -> dict[str, Any]:
        """获取当前页面观察结果。"""

        # 调用 Agent 获取观察数据。
        # ok=false 时仍返回数据和错误信息，由上层节点决定 halt。
        # 不把“观察成功”直接等价为“字段已完成”。
        result = await self.webview_agent.observe_form()
        return {"ok": result.ok, "message": result.message, "data": result.data}
