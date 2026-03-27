#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
键盘操作 Actions
"""
import asyncio

import pyautogui
import pyperclip
from loguru import logger

from app.service.actions.ufo_base_action import UFOBaseAction
from app.service.skills.base_action import (
    ActionResult,
    ActionParameter,
    ParameterType,
)
from app.service.utils.text_input import type_text


class TypeAction(UFOBaseAction):
    """使用智能输入文本 (ASCII 用 typewrite, 非 ASCII 用剪贴板粘贴)"""
    name = "type"
    description = "使用 pyautogui 直接输入文本（输入前自动清空当前输入框）"
    parameters = [
        ActionParameter(name="text", type=ParameterType.STRING, description="要输入的文本"),
        ActionParameter(name="interval", type=ParameterType.FLOAT, description="按键间隔(秒)", required=False, default=0.02),
    ]

    async def _execute(self, text: str, interval: float = 0.02) -> ActionResult:
        logger.info(f"[TypeAction] 输入文本: '{text[:50]}{'...' if len(text) > 50 else ''}' (长度={len(text)})")
        # 保存用户剪贴板内容，输入完成后恢复
        _clipboard_backup = None
        try:
            _clipboard_backup = pyperclip.paste()
        except Exception:
            pass
        try:
            # P1: 输入前先全选清空，防止新旧文本拼接
            pyautogui.hotkey('ctrl', 'a')
            await asyncio.sleep(0.15)
            pyautogui.press('delete')
            await asyncio.sleep(0.15)
            await type_text(text, interval)
            logger.info("[TypeAction] 文本输入完成")
            return ActionResult(success=True)
        except Exception as e:
            logger.error(f"[TypeAction] 文本输入异常: {e}")
            return ActionResult(success=False, error=f"文本输入异常: {e}")
        finally:
            # 恢复用户剪贴板
            if _clipboard_backup is not None:
                try:
                    await asyncio.sleep(0.1)
                    pyperclip.copy(_clipboard_backup)
                except Exception:
                    pass


class SetEditTextAction(UFOBaseAction):
    """向文本框输入内容（先点击聚焦再输入）"""
    name = "set_edit_text"
    description = "向文本框输入内容（先点击聚焦再输入）"
    parameters = [
        ActionParameter(name="text", type=ParameterType.STRING, description="要输入的文本"),
        ActionParameter(name="clear_current_text", type=ParameterType.BOOLEAN, description="是否清空当前文本", required=False, default=False),
    ]

    async def _execute(self, text: str, clear_current_text: bool = False) -> ActionResult:
        logger.info(f"[SetEditTextAction] 输入文本: '{text[:50]}{'...' if len(text) > 50 else ''}', clear={clear_current_text}")
        try:
            if clear_current_text:
                pyautogui.hotkey('ctrl', 'a')
                await asyncio.sleep(0.2)
            await type_text(text, 0.02)
            return ActionResult(success=True)
        except Exception as e:
            logger.error(f"[SetEditTextAction] 文本输入异常: {e}")
            return ActionResult(success=False, error=f"文本输入异常: {e}")


class KeyboardInputAction(UFOBaseAction):
    """模拟键盘按键组合，如 Ctrl+C, Alt+Tab"""
    name = "keyboard_input"
    description = "模拟键盘按键组合，如 Ctrl+C, Alt+Tab"
    parameters = [
        ActionParameter(name="keys", type=ParameterType.STRING, description="按键组合 (如 'ctrl+c', 'alt+tab')"),
    ]

    async def _execute(self, keys: str) -> ActionResult:
        parts = keys.replace('-', '+').split('+')
        pyautogui.hotkey(*[p.strip() for p in parts if p.strip()])
        return ActionResult(success=True)


class KeypressAction(UFOBaseAction):
    """按下并释放单个按键"""
    name = "keypress"
    description = "按下并释放单个按键"
    parameters = [
        ActionParameter(name="keys", type=ParameterType.STRING, description="按键名称 (如 'enter', 'tab')"),
    ]

    async def _execute(self, keys: str) -> ActionResult:
        if isinstance(keys, list):
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(keys)
        return ActionResult(success=True)
