"""UIA 控制器 — Windows UIAutomation 命令执行。

参考 UFO controller.py 的 ControlReceiver + Command 模式，
封装 click、fill、type、scroll、drag 等底层 GUI 操作。
所有操作通过 pywinauto 的 UIAWrapper 执行，支持异步包装。
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.commands.base import Command

logger = logging.getLogger(__name__)

# Windows 专用导入保护
try:
    import pywinauto  # type: ignore
    from pywinauto import Application  # type: ignore
    from pywinauto.uia_element_info import UIAElementInfo  # type: ignore
    from pywinauto.controls.uiawrapper import UIAWrapper  # type: ignore

    _HAS_PYWINAUTO = True
except ImportError:
    _HAS_PYWINAUTO = False


class TextTransformer:
    """文本转义器 — 将特殊字符转换为 pywinauto type_keys 格式。

    # pywinauto 的 type_keys 使用增强键盘语法，特殊字符需要转义。
    # 参考 UFO controller.py TextTransformer 实现。
    # 只处理会与 pywinauto 语法冲突的字符，不改变其他内容。
    """

    _ESCAPE_MAP = {
        "+": "{+}",
        "^": "{^}",
        "%": "{%}",
        "~": "{~}",
        "(": "{(}",
        ")": "{)}",
        "[": "{[}",
        "]": "{]}",
    }

    def transform(self, text: str) -> str:
        """转义文本中的 pywinauto 特殊字符。"""
        result: list[str] = []
        for ch in text:
            escaped = self._ESCAPE_MAP.get(ch, ch)
            result.append(escaped)
        return "".join(result)


class UIAController:
    """UIA 控制器 — 封装 Windows UIAutomation 操作。

    # 参考 UFO ControlReceiver，但使用 jm_ufo_agent 的 Command/AgentResult 接口。
    # click → 元素定位 + click_input。
    # fill → 剪贴板粘贴（绕过输入法）或 set_text。
    # type → type_keys 逐字输入（需要 TextTransformer 转义）。
    # scroll → wheel_mouse_input。
    # drag → 鼠标拖拽。
    # 所有 GUI 操作通过 asyncio.to_thread 包装为异步。
    """

    def __init__(self) -> None:
        """初始化 UIA 控制器。"""
        self._text_transformer = TextTransformer()

    def is_available(self) -> bool:
        """检查 pywinauto 是否可用。"""
        return _HAS_PYWINAUTO

    async def click(self, control: Any, coordinates: tuple[int, int] | None = None) -> AgentResult:
        """点击控件或坐标。

        # coordinates 为 (x, y) 绝对坐标时直接点击坐标。
        # coordinates 为 None 时点击控件中心。
        # 参考 UFO ControlReceiver.click_input / click_on_coordinates。
        """
        if not _HAS_PYWINAUTO:
            return AgentResult(ok=False, message="pywinauto 不可用", data={"action": "click"})

        try:
            if coordinates is not None:
                await asyncio.to_thread(
                    pywinauto.keyboard.send_keys, f"{{CLICK {coordinates[0]} {coordinates[1]}}}"
                )
                # 使用 mouse 点击坐标
                await asyncio.to_thread(self._click_at_coordinates, coordinates)
            else:
                await asyncio.to_thread(control.click_input)
            return AgentResult(ok=True, message="click 完成", data={"action": "click"})
        except Exception as exc:
            return AgentResult(ok=False, message=str(exc), data={"action": "click"})

    async def fill(self, control: Any, value: str, use_clipboard: bool = True) -> AgentResult:
        """填充文本到控件。

        # use_clipboard=True 时通过剪贴板粘贴，绕过输入法问题。
        # use_clipboard=False 时使用 set_edit_text 直接设置。
        # 参考 UFO ControlReceiver.set_edit_text。
        """
        if not _HAS_PYWINAUTO:
            return AgentResult(ok=False, message="pywinauto 不可用", data={"action": "fill"})

        try:
            if use_clipboard:
                await asyncio.to_thread(self._fill_via_clipboard, control, value)
            else:
                await asyncio.to_thread(self._fill_direct, control, value)
            return AgentResult(
                ok=True,
                message=f"fill 完成: {value[:20]}",
                data={"action": "fill", "value_preview": value[:20]},
            )
        except Exception as exc:
            return AgentResult(ok=False, message=str(exc), data={"action": "fill"})

    async def type_keys(self, control: Any, text: str) -> AgentResult:
        """逐字输入文本（经过 TextTransformer 转义）。

        # 参考 UFO ControlReceiver.type。
        # 先 focus 控件，再 type_keys 转义后的文本。
        # 适用于需要逐字输入的场景（搜索框等）。
        """
        if not _HAS_PYWINAUTO:
            return AgentResult(ok=False, message="pywinauto 不可用", data={"action": "type"})

        try:
            transformed = self._text_transformer.transform(text)
            await asyncio.to_thread(control.type_keys, transformed)
            return AgentResult(ok=True, message="type 完成", data={"action": "type"})
        except Exception as exc:
            return AgentResult(ok=False, message=str(exc), data={"action": "type"})

    async def scroll(self, control: Any, direction: str = "down", amount: int = 3) -> AgentResult:
        """滚动控件。

        # direction 支持 up/down/left/right。
        # amount 控制滚动量。
        # 参考 UFO ControlReceiver.scroll。
        """
        if not _HAS_PYWINAUTO:
            return AgentResult(ok=False, message="pywinauto 不可用", data={"action": "scroll"})

        try:
            wheel_delta = -120 * amount if direction == "down" else 120 * amount
            if direction in ("left", "right"):
                # 水平滚动需要特殊处理
                await asyncio.to_thread(
                    control.wheel_mouse_input, wheel_delta if direction == "right" else -wheel_delta, "horizontal"
                )
            else:
                await asyncio.to_thread(control.wheel_mouse_input, wheel_delta)
            return AgentResult(ok=True, message=f"scroll {direction} 完成", data={"action": "scroll"})
        except Exception as exc:
            return AgentResult(ok=False, message=str(exc), data={"action": "scroll"})

    async def drag(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> AgentResult:
        """从 start 坐标拖拽到 end 坐标。

        # 参考 UFO ControlReceiver.drag_on_coordinates。
        """
        if not _HAS_PYWINAUTO:
            return AgentResult(ok=False, message="pywinauto 不可用", data={"action": "drag"})

        try:
            await asyncio.to_thread(self._drag_impl, start, end)
            return AgentResult(ok=True, message="drag 完成", data={"action": "drag"})
        except Exception as exc:
            return AgentResult(ok=False, message=str(exc), data={"action": "drag"})

    @staticmethod
    def _click_at_coordinates(coordinates: tuple[int, int]) -> None:
        """在指定坐标点击。"""
        import pywinauto  # type: ignore

        x, y = coordinates
        pywinauto.mouse.click(coords=(x, y))

    @staticmethod
    def _fill_via_clipboard(control: Any, value: str) -> None:
        """通过剪贴板粘贴填充。"""
        import pyperclip  # type: ignore

        control.click_input()
        pyperclip.copy(value)
        # Ctrl+A 全选 → Ctrl+V 粘贴
        control.type_keys("^a^v", pause=0.05)

    @staticmethod
    def _fill_direct(control: Any, value: str) -> None:
        """直接设置文本。"""
        if hasattr(control, "set_text"):
            control.set_text(value)
        elif hasattr(control, "set_edit_text"):
            control.set_edit_text(value)
        else:
            # 退回到剪贴板方式
            UIAController._fill_via_clipboard(control, value)

    @staticmethod
    def _drag_impl(start: tuple[int, int], end: tuple[int, int]) -> None:
        """执行拖拽。"""
        import pywinauto  # type: ignore

        pywinauto.mouse.press(coords=start)
        pywinauto.mouse.move(coords=end)
        pywinauto.mouse.release(coords=end)
