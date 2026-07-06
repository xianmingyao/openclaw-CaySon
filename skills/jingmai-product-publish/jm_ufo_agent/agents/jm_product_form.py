"""京麦商品表单 Agent。"""

from __future__ import annotations

from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.agents.desktop import DesktopAgent


class JmProductFormAgent(DesktopAgent):
    """负责商品表单字段填充。"""

    def __init__(self, *args, **kwargs):
        """初始化商品表单 Agent。"""

        # 固定名称让 workflow 证据更稳定。
        # backend 仍可由测试或真实 UFO 适配层注入。
        # 安全策略由 DesktopAgent 默认启用。
        kwargs.setdefault("name", "jm_product_form")
        super().__init__(*args, **kwargs)

    async def fill_field(self, field_name: str, value: object, evidence: dict | None = None) -> AgentResult:
        """填充一个商品字段。"""

        # WebView 默认不可依赖 DOM/UIA，所以这里只暴露字段级 fill。
        # evidence 可携带 OCR/坐标/截图证据，后续 VerifyStrategy 使用。
        # 真正的坐标点击和剪贴板写入由 backend 适配。
        return await self.fill(target=field_name, value=value, label=f"填写字段:{field_name}", metadata=evidence or {})

    async def save_draft(self, evidence: dict | None = None) -> AgentResult:
        """保存草稿。"""

        # 保存草稿是明确白名单动作。
        # 仍然走 submit + SafetyPolicy，防止按钮 label 被误写成发布。
        # evidence 用于保存页面签名或按钮截图摘要。
        return await self.submit(target="draft", label="保存草稿", metadata=evidence or {})
