#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
滚动操作 Actions
"""
import pyautogui

from app.service.actions.ufo_base_action import UFOBaseAction
from app.service.skills.base_action import (
    ActionResult,
    ActionParameter,
    ParameterType,
)


class ScrollAction(UFOBaseAction):
    """在指定坐标处滚动鼠标滚轮"""
    name = "scroll"
    description = "在指定坐标处滚动鼠标滚轮"
    parameters = [
        ActionParameter(name="scroll_x", type=ParameterType.INTEGER, description="水平滚动量", required=False, default=0),
        ActionParameter(name="scroll_y", type=ParameterType.INTEGER, description="垂直滚动量 (负数向下)", required=False, default=-3),
        ActionParameter(name="x", type=ParameterType.INTEGER, description="X 坐标", required=False, default=0),
        ActionParameter(name="y", type=ParameterType.INTEGER, description="Y 坐标", required=False, default=0),
    ]

    async def _execute(self, scroll_x: int = 0, scroll_y: int = -3, x: int = 0, y: int = 0) -> ActionResult:
        sx, sy = self._scale_coord(x, y)
        pyautogui.scroll(scroll_y, x=sx, y=sy)
        return ActionResult(success=True, metadata={"coordinates": {"x": sx, "y": sy}})


class WheelMouseInputAction(UFOBaseAction):
    """鼠标滚轮滚动（在当前鼠标位置滚动）"""
    name = "wheel_mouse_input"
    description = "鼠标滚轮滚动，不需要指定坐标（在当前鼠标位置滚动）"
    parameters = [
        ActionParameter(name="wheel_dist", type=ParameterType.INTEGER, description="滚动量 (负数向下)"),
    ]

    async def _execute(self, wheel_dist: int) -> ActionResult:
        pyautogui.scroll(wheel_dist)
        return ActionResult(success=True)
