#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
信息获取 Actions
"""
import pyautogui
import pyperclip
import asyncio

from loguru import logger

from app.service.actions.ufo_base_action import UFOBaseAction
from app.service.skills.base_action import (
    ActionResult,
    ActionParameter,
    ParameterType,
)


class AnnotationAction(UFOBaseAction):
    """标注操作，在截图中添加注释信息供 LLM 理解"""
    name = "annotation"
    description = "对当前屏幕状态添加文字标注或注释（用于向 LLM 传达视觉观察）"
    parameters = [
        ActionParameter(name="text", type=ParameterType.STRING, description="标注文本内容", required=False, default=""),
    ]

    async def _execute(self, text: str = "") -> ActionResult:
        # annotation 不执行 UI 动作，仅传递标注信息
        return ActionResult(success=True, data={"annotation": text})


class TextsAction(UFOBaseAction):
    """获取当前聚焦控件中的文本内容（通过剪贴板复制获取选中文本）"""
    name = "texts"
    description = "获取当前聚焦控件中的文本内容（通过剪贴板复制获取选中文本）"
    parameters = []

    async def _execute(self) -> ActionResult:
        # Ctrl+A 全选 → Ctrl+C 复制 → 读取剪贴板
        pyautogui.hotkey('ctrl', 'a')
        await asyncio.sleep(0.2)
        pyautogui.hotkey('ctrl', 'c')
        await asyncio.sleep(0.3)
        try:
            text = pyperclip.paste()
            return ActionResult(success=True, data={"text": text})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class SummaryAction(UFOBaseAction):
    """视觉摘要，让 LLM 对当前截图进行文字描述"""
    name = "summary"
    description = "视觉摘要，让 LLM 对当前截图进行文字描述（用于信息获取和理解界面状态）"
    parameters = [
        ActionParameter(name="text", type=ParameterType.STRING, description="LLM 生成的摘要文本", required=False, default=""),
    ]

    async def _execute(self, text: str = "") -> ActionResult:
        # summary 操作本身不执行任何 UI 动作，只是传递 LLM 的观察结果
        return ActionResult(success=True, data={"summary": text})
