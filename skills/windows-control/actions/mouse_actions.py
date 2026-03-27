#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
鼠标操作 Actions
"""
import pyautogui
from loguru import logger

from app.service.actions.ufo_base_action import UFOBaseAction
from app.service.skills.base_action import (
    ActionResult,
    ActionParameter,
    ParameterType,
)


class ClickAction(UFOBaseAction):
    """点击指定屏幕坐标 (x, y)"""
    name = "click"
    description = "点击指定屏幕坐标 (x, y)"
    parameters = [
        ActionParameter(name="x", type=ParameterType.INTEGER, description="X 坐标"),
        ActionParameter(name="y", type=ParameterType.INTEGER, description="Y 坐标"),
        ActionParameter(name="button", type=ParameterType.STRING, description="鼠标按键 (left/right/middle)", required=False, default="left"),
    ]

    async def _execute(self, x: int, y: int, button: str = "left") -> ActionResult:
        _hash = self._take_pre_screenshot()
        sx, sy = self._scale_coord(x, y)
        self._validate_screen_coord(sx, sy)
        pyautogui.click(x=sx, y=sy, button=button)
        metadata = {"coordinates": {"x": sx, "y": sy, "screenshot_x": x, "screenshot_y": y}}
        if _hash:
            metadata["screen_hash"] = _hash
        return ActionResult(success=True, metadata=metadata)


class DoubleClickAction(UFOBaseAction):
    """双击指定屏幕坐标 (x, y)"""
    name = "double_click"
    description = "双击指定屏幕坐标 (x, y)"
    parameters = [
        ActionParameter(name="x", type=ParameterType.INTEGER, description="X 坐标"),
        ActionParameter(name="y", type=ParameterType.INTEGER, description="Y 坐标"),
    ]

    async def _execute(self, x: int, y: int) -> ActionResult:
        _hash = self._take_pre_screenshot()
        sx, sy = self._scale_coord(x, y)
        pyautogui.doubleClick(x=sx, y=sy)
        metadata = {"coordinates": {"x": sx, "y": sy, "screenshot_x": x, "screenshot_y": y}}
        if _hash:
            metadata["screen_hash"] = _hash
        return ActionResult(success=True, metadata=metadata)


class ClickInputAction(UFOBaseAction):
    """控件级点击，支持双击和修饰键"""
    name = "click_input"
    description = "控件级点击，支持双击和修饰键（先聚焦再点击，适用于精确控件操作）"
    parameters = [
        ActionParameter(name="x", type=ParameterType.INTEGER, description="X 坐标"),
        ActionParameter(name="y", type=ParameterType.INTEGER, description="Y 坐标"),
        ActionParameter(name="button", type=ParameterType.STRING, description="鼠标按键", required=False, default="left"),
        ActionParameter(name="double", type=ParameterType.BOOLEAN, description="是否双击", required=False, default=False),
        ActionParameter(name="pressed", type=ParameterType.STRING, description="按住的修饰键", required=False, default=""),
    ]

    async def _execute(self, x: int, y: int, button: str = "left", double: bool = False, pressed: str = "") -> ActionResult:
        sx, sy = self._scale_coord(x, y)
        if pressed:
            pyautogui.keyDown(pressed)
        if double:
            pyautogui.doubleClick(x=sx, y=sy, button=button)
        else:
            pyautogui.click(x=sx, y=sy, button=button)
        if pressed:
            pyautogui.keyUp(pressed)
        return ActionResult(success=True, metadata={"coordinates": {"x": sx, "y": sy}})


class ClickOnCoordinatesAction(UFOBaseAction):
    """分数坐标点击，坐标为相对于截图的归一化值 (0.0~1.0)"""
    name = "click_on_coordinates"
    description = "分数坐标点击，坐标为相对于截图的归一化值 (0.0~1.0)"
    parameters = [
        ActionParameter(name="frac_x", type=ParameterType.FLOAT, description="归一化 X 坐标 (0.0~1.0)"),
        ActionParameter(name="frac_y", type=ParameterType.FLOAT, description="归一化 Y 坐标 (0.0~1.0)"),
        ActionParameter(name="button", type=ParameterType.STRING, description="鼠标按键", required=False, default="left"),
        ActionParameter(name="double", type=ParameterType.BOOLEAN, description="是否双击", required=False, default=False),
    ]

    async def _execute(self, frac_x: float, frac_y: float, button: str = "left", double: bool = False) -> ActionResult:
        sw, sh = self._screen_size
        sx, sy = self._scale_coord(int(frac_x * sw), int(frac_y * sh))
        if double:
            pyautogui.doubleClick(x=sx, y=sy, button=button)
        else:
            pyautogui.click(x=sx, y=sy, button=button)
        return ActionResult(success=True, metadata={"coordinates": {"x": sx, "y": sy}})


class MoveAction(UFOBaseAction):
    """移动鼠标到指定屏幕坐标"""
    name = "move"
    description = "移动鼠标到指定屏幕坐标"
    parameters = [
        ActionParameter(name="x", type=ParameterType.INTEGER, description="X 坐标"),
        ActionParameter(name="y", type=ParameterType.INTEGER, description="Y 坐标"),
    ]

    async def _execute(self, x: int, y: int) -> ActionResult:
        sx, sy = self._scale_coord(x, y)
        pyautogui.moveTo(x=sx, y=sy)
        return ActionResult(success=True, metadata={"coordinates": {"x": sx, "y": sy}})


class DragAction(UFOBaseAction):
    """从起点拖拽到终点"""
    name = "drag"
    description = "从起点拖拽到终点"
    parameters = [
        ActionParameter(name="start_x", type=ParameterType.INTEGER, description="起点 X 坐标"),
        ActionParameter(name="start_y", type=ParameterType.INTEGER, description="起点 Y 坐标"),
        ActionParameter(name="end_x", type=ParameterType.INTEGER, description="终点 X 坐标"),
        ActionParameter(name="end_y", type=ParameterType.INTEGER, description="终点 Y 坐标"),
        ActionParameter(name="duration", type=ParameterType.FLOAT, description="拖拽持续时间(秒)", required=False, default=0.5),
    ]

    async def _execute(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5) -> ActionResult:
        ssx, ssy = self._scale_coord(start_x, start_y)
        sex, sey = self._scale_coord(end_x, end_y)
        pyautogui.moveTo(ssx, ssy)
        pyautogui.dragTo(sex, sey, duration=duration)
        return ActionResult(
            success=True,
            metadata={"coordinates": {"start_x": ssx, "start_y": ssy, "end_x": sex, "end_y": sey}},
        )


class DragOnCoordinatesAction(UFOBaseAction):
    """分数坐标拖拽，支持按住修饰键拖拽"""
    name = "drag_on_coordinates"
    description = "分数坐标拖拽，支持按住修饰键拖拽（如 Shift 选择区域）"
    parameters = [
        ActionParameter(name="start_frac_x", type=ParameterType.FLOAT, description="起点归一化 X"),
        ActionParameter(name="start_frac_y", type=ParameterType.FLOAT, description="起点归一化 Y"),
        ActionParameter(name="end_frac_x", type=ParameterType.FLOAT, description="终点归一化 X"),
        ActionParameter(name="end_frac_y", type=ParameterType.FLOAT, description="终点归一化 Y"),
        ActionParameter(name="duration", type=ParameterType.FLOAT, description="持续时间(秒)", required=False, default=0.5),
        ActionParameter(name="button", type=ParameterType.STRING, description="鼠标按键", required=False, default="left"),
        ActionParameter(name="key_hold", type=ParameterType.STRING, description="按住的修饰键", required=False, default=""),
    ]

    async def _execute(self, start_frac_x: float, start_frac_y: float,
                        end_frac_x: float, end_frac_y: float,
                        duration: float = 0.5, button: str = "left", key_hold: str = "") -> ActionResult:
        sw, sh = self._screen_size
        ssx, ssy = self._scale_coord(int(start_frac_x * sw), int(start_frac_y * sh))
        sex, sey = self._scale_coord(int(end_frac_x * sw), int(end_frac_y * sh))
        if key_hold:
            pyautogui.keyDown(key_hold)
        pyautogui.moveTo(ssx, ssy)
        pyautogui.dragTo(sex, sey, duration=duration, button=button)
        if key_hold:
            pyautogui.keyUp(key_hold)
        return ActionResult(
            success=True,
            metadata={"coordinates": {"start_x": ssx, "start_y": ssy, "end_x": sex, "end_y": sey}},
        )
