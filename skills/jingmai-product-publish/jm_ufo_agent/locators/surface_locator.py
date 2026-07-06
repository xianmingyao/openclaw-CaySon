"""屏幕表面定位器 — 通过截图 + OCR 查找元素。

适用于 UIA 无法覆盖的 Web 页面、自绘控件等场景。
结合 web_surface/screenshot_ocr.py 的 OCR 能力。
"""

from __future__ import annotations

import logging
from typing import Any

from jm_ufo_agent.locators.base import Locator, LocateResult

logger = logging.getLogger(__name__)


class SurfaceLocator(Locator):
    """基于截图 + OCR 的屏幕表面定位器。

    # 先截图再 OCR，根据目标文本在截图中定位元素位置。
    # confidence 取 OCR 置信度，通常低于 UIA 的 1.0。
    # 依赖 backends/web_surface/screenshot_ocr.py 提供截图和 OCR。
    # 在无 OCR 引擎可用时返回空结果，不抛异常。
    """

    def __init__(self, ocr_engine: Any | None = None):
        """初始化表面定位器。"""
        self._ocr_engine = ocr_engine

    @property
    def name(self) -> str:
        return "surface"

    async def locate(
        self,
        target: str,
        context: dict[str, Any] | None = None,
    ) -> list[LocateResult]:
        """通过截图 + OCR 查找匹配目标文本的区域。"""
        ctx = context or {}
        screenshot = ctx.get("screenshot")

        if screenshot is None:
            # 尝试自行截图
            screenshot = await self._take_screenshot(ctx)
            if screenshot is None:
                logger.debug("SurfaceLocator 无截图可用")
                return []

        ocr_results = await self._run_ocr(screenshot)
        if not ocr_results:
            return []

        results: list[LocateResult] = []
        target_lower = target.lower()
        for ocr_item in ocr_results:
            text = ocr_item.get("text", "")
            confidence = ocr_item.get("confidence", 0.5)
            rect = ocr_item.get("rect", (0, 0, 0, 0))

            if target_lower in text.lower():
                results.append(
                    LocateResult(
                        target=target,
                        rect=rect,
                        confidence=confidence,
                        meta={"ocr_text": text, "source": "surface"},
                    )
                )

        results.sort(key=lambda r: r.confidence, reverse=True)
        return results

    async def _take_screenshot(self, context: dict[str, Any]) -> Any | None:
        """尝试自行截图。"""
        try:
            from jm_ufo_agent.backends.web_surface.screenshot_ocr import take_screenshot

            return await take_screenshot()
        except Exception as exc:
            logger.debug("截图失败: %s", exc)
            return None

    async def _run_ocr(self, screenshot: Any) -> list[dict[str, Any]]:
        """执行 OCR 识别。"""
        if self._ocr_engine is not None:
            try:
                return await self._ocr_engine.recognize(screenshot)
            except Exception as exc:
                logger.warning("OCR 引擎异常: %s", exc)
                return []

        try:
            from jm_ufo_agent.backends.web_surface.screenshot_ocr import run_ocr

            return await run_ocr(screenshot)
        except Exception as exc:
            logger.debug("默认 OCR 不可用: %s", exc)
            return []
