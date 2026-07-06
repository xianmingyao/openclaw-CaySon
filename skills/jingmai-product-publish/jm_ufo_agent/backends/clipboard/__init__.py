"""剪贴板后端 — Windows 剪贴板读写封装。

提供可靠的剪贴板操作，用于文本填充和图片传递。
独立于 web_surface/clipboard_fill.py，作为通用剪贴板模块。
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# 剪贴板库导入保护
try:
    import pyperclip  # type: ignore

    _HAS_PYPERCLIP = True
except ImportError:
    _HAS_PYPERCLIP = False


class ClipboardHandler:
    """剪贴板处理器 — 读写 Windows 剪贴板。

    # pyperclip 可用时使用 pyperclip 进行跨平台剪贴板操作。
    # pyperclip 不可用时尝试 ctypes Win32 API。
    # 所有操作都是同步的，GUI 操作通常在 to_thread 中调用。
    # 保存和恢复剪贴板内容，避免覆盖用户数据。
    """

    def __init__(self) -> None:
        """初始化剪贴板处理器。"""
        self._saved_content: str | None = None

    def is_available(self) -> bool:
        """检查剪贴板功能是否可用。"""
        return _HAS_PYPERCLIP or self._has_win32_clipboard()

    def read_text(self) -> str:
        """读取剪贴板文本。"""
        if _HAS_PYPERCLIP:
            try:
                return pyperclip.paste()
            except Exception as exc:
                logger.debug("pyperclip 读取失败: %s", exc)

        return self._win32_read_text()

    def write_text(self, text: str) -> None:
        """写入文本到剪贴板。"""
        if _HAS_PYPERCLIP:
            try:
                pyperclip.copy(text)
                return
            except Exception as exc:
                logger.debug("pyperclip 写入失败: %s", exc)

        self._win32_write_text(text)

    def save(self) -> None:
        """保存当前剪贴板内容。"""
        try:
            self._saved_content = self.read_text()
        except Exception:
            self._saved_content = None

    def restore(self) -> None:
        """恢复之前保存的剪贴板内容。"""
        if self._saved_content is not None:
            try:
                self.write_text(self._saved_content)
            except Exception as exc:
                logger.warning("恢复剪贴板失败: %s", exc)
            finally:
                self._saved_content = None

    def paste_via_keyboard(self) -> None:
        """模拟 Ctrl+V 粘贴。

        # 配合 write_text 使用：先写入剪贴板，再触发粘贴。
        # 需要目标窗口已获得焦点。
        """
        try:
            import pywinauto.keyboard as kb  # type: ignore

            kb.send_keys("^v", pause=0.05)
        except ImportError:
            logger.debug("pywinauto 不可用，无法模拟键盘粘贴")

    @staticmethod
    def _has_win32_clipboard() -> bool:
        """检查 Win32 剪贴板 API 是否可用。"""
        try:
            import ctypes

            return bool(ctypes.windll.user32.OpenClipboard(0))
        except Exception:
            return False
        finally:
            try:
                ctypes.windll.user32.CloseClipboard()
            except Exception:
                pass

    @staticmethod
    def _win32_read_text() -> str:
        """使用 Win32 API 读取剪贴板文本。"""
        try:
            import ctypes

            if not ctypes.windll.user32.OpenClipboard(0):
                return ""
            try:
                CF_UNICODETEXT = 13
                handle = ctypes.windll.user32.GetClipboardData(CF_UNICODETEXT)
                if not handle:
                    return ""
                return ctypes.c_wchar_p(handle).value or ""
            finally:
                ctypes.windll.user32.CloseClipboard()
        except Exception:
            return ""

    @staticmethod
    def _win32_write_text(text: str) -> None:
        """使用 Win32 API 写入剪贴板文本。"""
        try:
            import ctypes

            if not ctypes.windll.user32.OpenClipboard(0):
                return
            try:
                ctypes.windll.user32.EmptyClipboard()
                CF_UNICODETEXT = 13
                handle = ctypes.windll.kernel32.GlobalAlloc(0x0042, (len(text) + 1) * 2)
                ptr = ctypes.windll.kernel32.GlobalLock(handle)
                ctypes.cdll.msvcrt.wcscpy_s(ctypes.c_wchar_p(ptr), len(text) + 1, text)
                ctypes.windll.kernel32.GlobalUnlock(handle)
                ctypes.windll.user32.SetClipboardData(CF_UNICODETEXT, handle)
            finally:
                ctypes.windll.user32.CloseClipboard()
        except Exception as exc:
            logger.warning("Win32 剪贴板写入失败: %s", exc)
