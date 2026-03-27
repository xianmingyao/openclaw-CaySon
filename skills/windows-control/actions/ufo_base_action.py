#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UFO 基础 Action

继承 BaseAction，增加 UFO 特有的能力:
- screenshot_scale: 截图坐标 → 屏幕坐标的缩放比例
- screen_size: 屏幕分辨率
- capture_screenshot: 执行前后截图
"""
from typing import Dict, Any, Optional, Tuple

from loguru import logger
from PIL import Image as PILImage

from app.service.skills.base_action import (
    BaseAction,
    ActionResult,
    ActionParameter,
    ParameterType,
)
from app.service.utils.screenshot import capture_screenshot, compute_image_hash


class UFOBaseAction(BaseAction):
    """
    UFO 基础 Action

    所有 UFO 操作的基类，提供:
    - 坐标缩放 (screenshot_coord / scale = screen_coord)
    - 执行前后截图支持
    - 屏幕边界校验
    """

    def __init__(self):
        super().__init__()
        self._screenshot_scale: float = 1.0
        self._screen_size: Tuple[int, int] = (0, 0)

    def set_context(self, screenshot_scale: float, screen_size: Tuple[int, int]):
        """设置执行上下文 (每次执行前由 ActionRegistry 调用)"""
        self._screenshot_scale = screenshot_scale
        self._screen_size = screen_size

    def _scale_coord(self, x: int, y: int) -> Tuple[int, int]:
        """截图坐标 → 屏幕坐标"""
        scale = self._screenshot_scale
        if scale != 1.0:
            return int(x / scale), int(y / scale)
        return x, y

    def _validate_screen_coord(self, x: int, y: int) -> bool:
        """校验坐标是否在屏幕范围内"""
        sw, sh = self._screen_size
        if sw <= 0 or sh <= 0:
            return True
        if x < 0 or x > sw:
            logger.warning(f"[{self.name}] 坐标 x={x} 超出屏幕宽度 [0, {sw}]")
        if y < 0 or y > sh:
            logger.warning(f"[{self.name}] 坐标 y={y} 超出屏幕高度 [0, {sh}]")
        return True

    def _take_pre_screenshot(self, label: str = "") -> Optional[str]:
        """执行前截图并返回 hash (用于导航变化检测)"""
        img, _, _ = capture_screenshot(label=f"pre_{self.name}_{label}")
        if img:
            return compute_image_hash(img)
        return None
