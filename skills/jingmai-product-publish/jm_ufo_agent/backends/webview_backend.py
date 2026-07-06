"""WebView 真实操作 backend — 京麦 Qt+Chromium WebView 走坐标+剪贴板+OCR 闭环。

# 该 backend 是 production.py 安全门控中 `webview-act` 的实现。
# 真实桌面动作（click/fill/submit）通过注入的 desktop api 委托给操作系统。
# 字段填写后必须由 WebViewFormLoop 的 OCR 读回验证通过，才返回 ok=True。
# 字段白名单从 product JSON 的 `fallback_coord` 字段读取；
# 任何不在白名单的字段直接拒绝，避免误填无关输入框。
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.backends.web_surface.clipboard_fill import (
    SystemClipboardFillService,
)
from jm_ufo_agent.backends.web_surface.coordinate_plan import (
    CoordinatePlanner,
    Rect,
)
from jm_ufo_agent.backends.web_surface.form_loop import (
    LocalSimilarityVerifier,
    WebViewFieldLoopResult,
    WebViewFormLoop,
)
from jm_ufo_agent.backends.web_surface.screenshot_ocr import (
    ScreenshotOcrService,
    TesseractOcrProvider,
)
from jm_ufo_agent.backends.web_surface.verifier import SurfaceVerifier
from jm_ufo_agent.commands.base import Command

logger = logging.getLogger(__name__)


class WebViewDesktopApi(Protocol):
    """WebView backend 要求的真实桌面 API 协议。"""

    def click(self, x: int, y: int) -> None:
        """点击屏幕坐标。"""
        ...

    def set_clipboard_text(self, text: str) -> None:
        """写入系统剪贴板。"""
        ...

    def hotkey(self, *keys: str) -> None:
        """发送键盘热键。"""
        ...

    def screenshot(self, path: str) -> None:
        """保存全屏截图到指定路径，用于 OCR 读回验证。"""
        ...


class PyAutoGuiDesktopApi:
    """基于 pyautogui 的真实桌面 API 实现。

    # pyautogui 在 Windows 上做绝对坐标点击 + 键盘热键。
    # 依赖缺失时构造时立刻抛错，让启动阶段就暴露环境问题。
    # 剪贴板单独走 pyperclip，比 pyautogui 内置更可靠。
    """

    def __init__(self) -> None:
        """初始化 PyAutoGui 桌面 API。"""
        try:
            import pyautogui  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "webview-act 需要 pyautogui；pip install pyautogui"
            ) from exc
        self._pyautogui = pyautogui

    def click(self, x: int, y: int) -> None:
        self._pyautogui.click(x, y)

    def set_clipboard_text(self, text: str) -> None:
        try:
            import pyperclip  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "webview-act 剪贴板需要 pyperclip；pip install pyperclip"
            ) from exc
        pyperclip.copy(text)

    def hotkey(self, *keys: str) -> None:
        self._pyautogui.hotkey(*keys)

    def screenshot(self, path: str) -> None:
        # pyautogui.screenshot 接受 str 或 Path；统一转 str 避免 PathLike 兼容问题。
        self._pyautogui.screenshot(str(path))


@dataclass(frozen=True)
class WebViewBackendConfig:
    """WebView backend 启动配置。"""

    # allow_write 是真实写操作的第二道门控；通过 CLI --no-observe-only 打开后
    # 仍由该字段控制是否真的点击/输入/提交。两道门控必须同时打开。
    allow_write: bool = False
    # 字段白名单 + 坐标表（来自 product JSON 的 fallback_coord）。
    # key 为字段名（与 product JSON 顶层 key 对应），value 为标签矩形。
    field_coords: dict[str, dict[str, int]] = field(default_factory=dict)
    # 截图/OCR 证据输出目录。
    artifact_dir: Path = Path("artifacts")
    # 是否启用 Tesseract 真实 OCR；关闭时 OCR provider 为空，读回用 dry-run。
    use_tesseract: bool = False


class WebViewDesktopBackend:
    """WebView 字段真实填写 backend。

    # 实现 Agent 协议 execute(Command) -> AgentResult。
    # 字段 fill 走 WebViewFormLoop 的 observe→act→verify 闭环。
    # 任何 fill 必须在 product JSON 的 fallback_coord 白名单内。
    # 任何 click 的坐标从 metadata.point / metadata.rect / 白名单 label rect 解析。
    """

    def __init__(
        self,
        api: WebViewDesktopApi,
        config: WebViewBackendConfig,
        loop: WebViewFormLoop | None = None,
    ) -> None:
        """初始化 WebView backend。"""
        self.api = api
        self.config = config
        self.loop = loop or self._build_default_loop()
        # executed 用于事后审计，登记每个 command（含被门控拒绝的）。
        self.executed: list[Command] = []

    def _build_default_loop(self) -> WebViewFormLoop:
        """按 config 构造默认 WebViewFormLoop 依赖。"""

        ocr_service = self._build_ocr_service()
        planner = CoordinatePlanner()
        clipboard = SystemClipboardFillService(api=self.api, allow_write=self.config.allow_write)
        verifier = SurfaceVerifier()
        similarity = LocalSimilarityVerifier()
        return WebViewFormLoop(
            ocr=ocr_service,
            planner=planner,
            clipboard=clipboard,
            verifier=verifier,
            similarity=similarity,
        )

    def _build_ocr_service(self) -> ScreenshotOcrService:
        """按 config 构造 OCR 服务。"""

        if not self.config.use_tesseract:
            return ScreenshotOcrService(provider=None)
        # 真实 OCR 需要 api 提供 screenshot(path) 能力；缺失时回退到 dry-run 并告警。
        if not hasattr(self.api, "screenshot"):
            logger.warning("api 缺少 screenshot 能力，回退到 dry-run OCR")
            return ScreenshotOcrService(provider=None)
        screenshot_path = self.config.artifact_dir / "screenshots" / "verify.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        return ScreenshotOcrService(
            provider=TesseractOcrProvider(self.api, screenshot_path)
        )

    async def execute(self, command: Command) -> AgentResult:
        """执行已经通过安全门控的 WebView 命令。"""

        # 命令到达这里前必须先通过 assert_production_allowed；
        # 该方法只做 backend 自身 allow_write 的最后一道校验。
        self.executed.append(command)
        if command.action in {"click", "fill", "submit", "upload"} and not self.config.allow_write:
            return AgentResult(
                ok=False,
                message="WebView 写操作未启用 allow_write",
                data={"action": command.action, "blocked": True},
            )
        if command.action == "fill":
            return await self._fill(command)
        if command.action == "click":
            return self._click(command)
        if command.action == "submit":
            # 保存草稿最终也是一次 click，坐标由 command.metadata.point 显式给定。
            return self._click(command)
        if command.action == "read":
            return AgentResult(ok=True, message="WebView read observed", data={"action": "read"})
        return AgentResult(
            ok=False,
            message=f"不支持的 WebView 命令: {command.action}",
            data={"action": command.action},
        )

    async def _fill(self, command: Command) -> AgentResult:
        """通过 WebViewFormLoop 真实填写并读回验证。"""

        field_name = command.target
        rect_payload = self.config.field_coords.get(field_name)
        if not rect_payload:
            return AgentResult(
                ok=False,
                message=f"字段 {field_name} 未在 fallback_coord 白名单中",
                data={
                    "field": field_name,
                    "whitelist": sorted(self.config.field_coords.keys()),
                },
            )
        try:
            label_rect = self._parse_rect(rect_payload)
        except (KeyError, TypeError, ValueError) as exc:
            return AgentResult(
                ok=False,
                message=f"fallback_coord.{field_name} 矩形格式非法: {exc}",
                data={"field": field_name, "rect_payload": rect_payload},
            )
        result: WebViewFieldLoopResult = await self.loop.fill_and_verify(
            field_name, label_rect, command.value
        )
        return AgentResult(
            ok=result.ok,
            message=result.fill_message if result.ok else f"{result.fill_message} | {result.verify_reason}",
            data={
                "field": field_name,
                "page_signature": result.page_signature,
                "screenshot_path": result.screenshot_path,
                "evidence": result.evidence,
            },
        )

    def _click(self, command: Command) -> AgentResult:
        """执行点击；坐标来源优先级：metadata.point > metadata.rect > 白名单 label rect。"""

        point = self._point_from_command(command)
        if point is None:
            return AgentResult(
                ok=False,
                message="缺少点击坐标或字段白名单",
                data={"target": command.target},
            )
        self.api.click(*point)
        return AgentResult(
            ok=True,
            message="真实点击已执行",
            data={"target": command.target, "point": list(point)},
        )

    @staticmethod
    def _parse_rect(payload: dict[str, Any]) -> Rect:
        """把 {x,y,width,height} dict 解析成 Rect。"""
        return Rect(
            x=int(payload["x"]),
            y=int(payload["y"]),
            width=int(payload["width"]),
            height=int(payload["height"]),
        )

    def _point_from_command(self, command: Command) -> tuple[int, int] | None:
        """从 command 解析点击坐标。"""

        point = command.metadata.get("point")
        if isinstance(point, (list, tuple)) and len(point) == 2:
            return (int(point[0]), int(point[1]))
        rect = command.metadata.get("rect")
        if isinstance(rect, dict):
            try:
                parsed = self._parse_rect(rect)
            except (KeyError, TypeError, ValueError):
                return None
            return (parsed.x + parsed.width // 2, parsed.y + parsed.height // 2)
        rect_payload = self.config.field_coords.get(command.target)
        if rect_payload:
            try:
                parsed = self._parse_rect(rect_payload)
            except (KeyError, TypeError, ValueError):
                return None
            return (parsed.x + parsed.width // 2, parsed.y + parsed.height // 2)
        return None


def build_webview_backend(
    config: WebViewBackendConfig,
    api: WebViewDesktopApi | None = None,
) -> WebViewDesktopBackend:
    """工厂：构造带 PyAutoGui API 的 WebView backend。

    # api 可注入 fake 以做单元测试；不传时默认用 PyAutoGuiDesktopApi。
    # 该工厂是 command.py 路由 webview-act 时唯一推荐的入口。
    """
    real_api = api or PyAutoGuiDesktopApi()
    return WebViewDesktopBackend(api=real_api, config=config)


async def run_webview_act(
    task_id: str,
    row_index: int,
    product: dict[str, Any],
    config: WebViewBackendConfig,
) -> dict[str, Any]:
    """按 product 字段在真实京麦 WebView 中填写并返回 state dict。"""

    # fallback_coord 必须与 product 同批提供；缺失时直接拒绝，避免自动猜测坐标。
    fallback_coord = product.get("fallback_coord") or {}
    if not isinstance(fallback_coord, dict):
        return {
            "ok": False,
            "task_id": task_id,
            "row_index": row_index,
            "status": "failed",
            "blockers": ["fallback_coord 必须是 object"],
            "verified_fields": [],
        }
    enriched_config = WebViewBackendConfig(
        allow_write=config.allow_write,
        field_coords={str(k): dict(v) for k, v in fallback_coord.items() if isinstance(v, dict)},
        artifact_dir=config.artifact_dir,
        use_tesseract=config.use_tesseract,
    )
    backend = build_webview_backend(enriched_config)
    verified: list[str] = []
    blockers: list[str] = []
    field_results: dict[str, Any] = {}
    for field_name, value in product.items():
        if field_name == "fallback_coord":
            continue
        if field_name not in enriched_config.field_coords:
            # 未列入白名单的字段不算 blocker，只是跳过（不强制全字段填写）。
            continue
        command = Command(action="fill", target=field_name, label=field_name, value=value)
        result = await backend.execute(command)
        field_results[field_name] = {
            "ok": result.ok,
            "message": result.message,
            "data": result.data,
        }
        if result.ok:
            verified.append(field_name)
        else:
            blockers.append(f"{field_name}: {result.message}")
    completion = len(verified) / max(1, len(enriched_config.field_coords))
    return {
        "ok": not blockers,
        "task_id": task_id,
        "row_index": row_index,
        "status": "completed" if not blockers else "halted",
        "current_node": "FILL_WEBVIEW_FORM",
        "completion_score": round(completion, 4),
        "verified_fields": verified,
        "blockers": blockers,
        "field_results": field_results,
        "executed_commands": len(backend.executed),
    }
