"""剪贴板填充服务边界。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jm_ufo_agent.backends.web_surface.coordinate_plan import CoordinatePlan


@dataclass(frozen=True)
class ClipboardFillResult:
    """剪贴板填充结果。"""

    ok: bool
    field_name: str
    message: str


class ClipboardFillService:
    """使用坐标和剪贴板填充 WebView 字段。"""

    async def apply_fill(self, plan: CoordinatePlan, value: object) -> ClipboardFillResult:
        """执行 dry-run 填充。"""

        # 真实实现应点击 plan.rect.center()，清空字段，再粘贴 value。
        # dry-run 只校验坐标计划可信度，不碰系统剪贴板。
        # 坐标不可信时失败，阻止 workflow 误推进。
        if not plan.is_trusted():
            return ClipboardFillResult(ok=False, field_name=plan.field_name, message="坐标计划不可信")
        return ClipboardFillResult(ok=True, field_name=plan.field_name, message=f"dry-run filled {value}")


class SystemClipboardFillService(ClipboardFillService):
    """真实系统剪贴板填充服务。"""

    def __init__(self, api: Any, allow_write: bool = False):
        """初始化剪贴板写入服务。"""

        # api 由外部注入，必须提供 click、set_clipboard_text、hotkey。
        # allow_write 默认 False，防止测试或误配置时写入系统剪贴板。
        # 该服务只处理字段填充，不负责 OCR 读回，读回仍由 WebViewFormLoop 完成。
        self.api = api
        self.allow_write = allow_write

    async def apply_fill(self, plan: CoordinatePlan, value: object) -> ClipboardFillResult:
        """点击坐标、清空字段并粘贴文本。"""

        # 坐标可信度是第一道门槛，低可信坐标直接失败。
        # allow_write 是第二道门槛，没有显式启用时不碰真实桌面。
        # 写入后只返回“动作已执行”，是否成功必须靠 OCR/读回验证。
        if not plan.is_trusted():
            return ClipboardFillResult(ok=False, field_name=plan.field_name, message="坐标计划不可信")
        if not self.allow_write:
            return ClipboardFillResult(ok=False, field_name=plan.field_name, message="系统剪贴板写入未启用 allow_write")
        missing = [name for name in ("click", "set_clipboard_text", "hotkey") if not hasattr(self.api, name)]
        if missing:
            return ClipboardFillResult(ok=False, field_name=plan.field_name, message=f"底层 API 缺少能力: {','.join(missing)}")
        x, y = plan.rect.center()
        self.api.click(x, y)
        self.api.set_clipboard_text(str(value))
        self.api.hotkey("ctrl", "a")
        self.api.hotkey("ctrl", "v")
        return ClipboardFillResult(ok=True, field_name=plan.field_name, message="系统剪贴板填充已执行，等待 OCR 读回验证")
