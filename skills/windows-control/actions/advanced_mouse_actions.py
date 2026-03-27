#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
高级鼠标操作 Actions
包含 UFO 中的路径拖拽、UI标注等高级操作
"""

import asyncio
from typing import List, Optional

from PIL import Image, ImageDraw, ImageFont

from app.service.actions.ufo_base_action import UFOBaseAction
from app.service.skills.base_action import (
    ActionResult,
    ActionParameter,
    ParameterType,
)
from app.service.utils.screenshot import capture_screenshot


class PathDragAction(UFOBaseAction):
    """
    路径拖拽 - 沿多个点依次拖拽

    UFO 中对应: DragCommand + path 参数
    适用于选择多个元素、框选区域等场景
    """
    name = "path_drag"
    description = "沿路径拖拽，遍历路径中所有相邻点依次执行拖拽"
    parameters = [
        ActionParameter(
            name="path",
            type=ParameterType.ARRAY,
            description="路径点列表，每个点是 [x, y] 坐标数组，至少需要 2 个点"
        ),
        ActionParameter(
            name="scaler",
            type=ParameterType.ARRAY,
            description="缩放尺寸 [width, height]，可选",
            required=False,
            default=None
        ),
        ActionParameter(
            name="button",
            type=ParameterType.STRING,
            description="鼠标按键",
            required=False,
            default="left",
            enum=["left", "right", "middle"]
        ),
    ]

    async def _execute(
        self,
        path: List,
        scaler: Optional[List] = None,
        button: str = "left"
    ) -> ActionResult:
        import pyautogui

        if len(path) < 2:
            return ActionResult(success=False, error="路径至少需要 2 个点")

        # 转换坐标
        scaled_path = []
        for point in path:
            x, y = point[0], point[1]
            if scaler:
                sx, sy = self._scale_coord(x, y)
            else:
                sx, sy = x, y
            scaled_path.append((sx, sy))

        # 沿路径依次拖拽
        for i in range(len(scaled_path) - 1):
            start = scaled_path[i]
            end = scaled_path[i + 1]
            pyautogui.moveTo(start[0], start[1])
            pyautogui.dragTo(end[0], end[1], button=button, duration=0.3)
            await asyncio.sleep(0.1)

        return ActionResult(
            success=True,
            metadata={
                "path_points": len(scaled_path),
                "start": scaled_path[0],
                "end": scaled_path[-1]
            }
        )


class AnnotationAction(UFOBaseAction):
    """
    UI 控件标注 - 在截图上标注控件位置

    UFO 中对应: AnnotationCommand
    用于 AI Agent 通过视觉模型分析 UI 元素
    """
    name = "annotation"
    description = "对当前窗口截图并标注指定控件位置"
    parameters = [
        ActionParameter(
            name="control_labels",
            type=ParameterType.ARRAY,
            description="要标注的控件标签列表，空列表标注所有",
            required=False,
            default=[]
        ),
        ActionParameter(
            name="controls",
            type=ParameterType.ARRAY,
            description="控件列表，每项包含 name, left, top, right, bottom",
            required=False,
            default=[]
        ),
        ActionParameter(
            name="output_path",
            type=ParameterType.STRING,
            description="输出图片路径",
            required=False,
            default=None
        ),
    ]

    async def _execute(
        self,
        control_labels: List[str] = None,
        controls: List[dict] = None,
        output_path: Optional[str] = None
    ) -> ActionResult:
        from pathlib import Path

        if control_labels is None:
            control_labels = []
        if controls is None:
            controls = []

        # 截取当前窗口
        img, img_path, _ = capture_screenshot(label="annotation")
        if not img:
            return ActionResult(success=False, error="截图失败")

        # 在图片上标注控件
        draw = ImageDraw.Draw(img)

        # 尝试加载字体
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except Exception:
            font = ImageFont.load_default()

        # 标注颜色映射
        colors = [
            "#FF0000", "#00FF00", "#0000FF", "#FFFF00",
            "#FF00FF", "#00FFFF", "#FF8000", "#8000FF"
        ]

        for i, control in enumerate(controls):
            if not isinstance(control, dict):
                continue

            label = control.get("name", f"#{i+1}")
            try:
                left = int(control.get("left", 0))
                top = int(control.get("top", 0))
                right = int(control.get("right", left + 50))
                bottom = int(control.get("bottom", top + 30))
            except (ValueError, TypeError):
                continue

            color = colors[i % len(colors)]

            # 绘制矩形边框
            draw.rectangle(
                [left, top, right, bottom],
                outline=color,
                width=2
            )

            # 绘制标签
            draw.rectangle(
                [left, top, left + 120, top + 20],
                fill=color
            )
            draw.text(
                (left + 5, top + 2),
                f"{label[:15]}",
                fill="white",
                font=font
            )

        # 保存标注后的图片
        if output_path is None:
            output_path = img_path.replace(".png", "_annotated.png")

        img.save(output_path)

        return ActionResult(
            success=True,
            data={
                "original_screenshot": img_path,
                "annotated_screenshot": output_path,
                "controls_count": len(controls)
            }
        )


class HoverAction(UFOBaseAction):
    """
    鼠标悬停 - 移动到指定坐标并悬停

    UFO 中没有单独对应，但 pywinauto 支持
    """
    name = "hover"
    description = "移动鼠标到指定坐标（不点击）"
    parameters = [
        ActionParameter(name="x", type=ParameterType.INTEGER, description="X 坐标"),
        ActionParameter(name="y", type=ParameterType.INTEGER, description="Y 坐标"),
    ]

    async def _execute(self, x: int, y: int) -> ActionResult:
        import pyautogui
        sx, sy = self._scale_coord(x, y)
        pyautogui.moveTo(sx, sy)
        await asyncio.sleep(0.5)  # 悬停等待
        return ActionResult(success=True, metadata={"coordinates": {"x": sx, "y": sy}})


class TripleClickAction(UFOBaseAction):
    """
    三击 - 在指定位置执行三次点击

    适用于选中整行/整段文本
    """
    name = "triple_click"
    description = "在指定坐标执行三次点击（选中整行/整段）"
    parameters = [
        ActionParameter(name="x", type=ParameterType.INTEGER, description="X 坐标"),
        ActionParameter(name="y", type=ParameterType.INTEGER, description="Y 坐标"),
    ]

    async def _execute(self, x: int, y: int) -> ActionResult:
        import pyautogui
        sx, sy = self._scale_coord(x, y)
        # 三次点击实现
        for _ in range(3):
            pyautogui.click(x=sx, y=sy)
            await asyncio.sleep(0.1)
        return ActionResult(success=True, metadata={"coordinates": {"x": sx, "y": sy}})


class RightClickAction(UFOBaseAction):
    """
    右键点击 - 在指定坐标执行右键菜单

    UFO 中通过 button='right' 实现
    """
    name = "right_click"
    description = "在指定坐标执行右键点击（弹出上下文菜单）"
    parameters = [
        ActionParameter(name="x", type=ParameterType.INTEGER, description="X 坐标"),
        ActionParameter(name="y", type=ParameterType.INTEGER, description="Y 坐标"),
    ]

    async def _execute(self, x: int, y: int) -> ActionResult:
        import pyautogui
        sx, sy = self._scale_coord(x, y)
        pyautogui.click(x=sx, y=sy, button="right")
        return ActionResult(success=True, metadata={"coordinates": {"x": sx, "y": sy}})


class DoubleRightClickAction(UFOBaseAction):
    """
    右键双击 - 在指定坐标执行右键双击
    """
    name = "double_right_click"
    description = "在指定坐标执行右键双击"
    parameters = [
        ActionParameter(name="x", type=ParameterType.INTEGER, description="X 坐标"),
        ActionParameter(name="y", type=ParameterType.INTEGER, description="Y 坐标"),
    ]

    async def _execute(self, x: int, y: int) -> ActionResult:
        import pyautogui
        sx, sy = self._scale_coord(x, y)
        pyautogui.doubleClick(x=sx, y=sy, button="right")
        return ActionResult(success=True, metadata={"coordinates": {"x": sx, "y": sy}})
