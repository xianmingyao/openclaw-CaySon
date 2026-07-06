"""VLM 定位器 — 通过视觉语言模型定位 UI 元素。

使用 VLM（如 qwen3-vl）分析截图，返回目标元素的坐标。
作为 UIA 和 OCR 之后的兜底策略，处理无法结构化匹配的场景。
"""

from __future__ import annotations

import json
import logging
from typing import Any

from jm_ufo_agent.locators.base import Locator, LocateResult

logger = logging.getLogger(__name__)


class VLMLocator(Locator):
    """基于视觉语言模型的 UI 元素定位器。

    # 将截图和目标描述发送给 VLM，让模型输出元素坐标。
    # 适用于 UIA 无法识别的自绘控件、Web 嵌套页面等。
    # VLM 输出格式要求：JSON 包含 rect 和 confidence 字段。
    # confidence 通常低于 UIA 的 1.0，建议阈值 0.7 以下才走 VLM。
    """

    def __init__(self, vlm_client: Any | None = None):
        """初始化 VLM 定位器。"""
        self._vlm_client = vlm_client

    @property
    def name(self) -> str:
        return "vlm"

    async def locate(
        self,
        target: str,
        context: dict[str, Any] | None = None,
    ) -> list[LocateResult]:
        """通过 VLM 分析截图定位目标元素。"""
        ctx = context or {}
        screenshot = ctx.get("screenshot")
        image_b64 = ctx.get("image_b64")

        if screenshot is None and image_b64 is None:
            screenshot = await self._take_screenshot(ctx)
            if screenshot is None:
                logger.debug("VLMLocator 无截图可用")
                return []

        if self._vlm_client is None:
            logger.debug("VLM 客户端未配置")
            return []

        try:
            response = await self._vlm_client.locate_element(
                target=target,
                image_b64=image_b64,
                image=screenshot,
            )
        except Exception as exc:
            logger.warning("VLM 定位异常: %s", exc)
            return []

        return self._parse_vlm_response(target, response)

    async def _take_screenshot(self, context: dict[str, Any]) -> Any | None:
        """尝试自行截图。"""
        try:
            from jm_ufo_agent.backends.web_surface.screenshot_ocr import take_screenshot

            return await take_screenshot()
        except Exception:
            return None

    @staticmethod
    def _parse_vlm_response(target: str, response: str) -> list[LocateResult]:
        """解析 VLM 返回的定位结果。

        # VLM 应返回 JSON 格式，包含 rect 和 confidence。
        # 容错处理：非 JSON 响应返回空列表。
        # rect 格式为 [left, top, right, bottom]。
        """
        try:
            data = json.loads(response)
        except (json.JSONDecodeError, TypeError):
            logger.debug("VLM 响应非 JSON: %s", response[:200] if response else "")
            return []

        if isinstance(data, dict):
            items = [data]
        elif isinstance(data, list):
            items = data
        else:
            return []

        results: list[LocateResult] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            rect_raw = item.get("rect", item.get("bbox", [0, 0, 0, 0]))
            if len(rect_raw) == 4:
                rect = tuple(int(v) for v in rect_raw)
            else:
                continue

            confidence = float(item.get("confidence", 0.5))
            results.append(
                LocateResult(
                    target=target,
                    rect=rect,  # type: ignore[arg-type]
                    confidence=confidence,
                    meta={"source": "vlm", "raw_response": item},
                )
            )

        results.sort(key=lambda r: r.confidence, reverse=True)
        return results
