"""Win32 窗口管理 — 窗口枚举、查找和操作。

提供 Win32 API 层面的窗口管理能力，比 UIA 更轻量。
适用于只需要窗口级操作（激活、移动、关闭）的场景。
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Windows 专用导入保护
try:
    import ctypes
    import ctypes.wintypes  # type: ignore

    _HAS_WIN32 = True
except ImportError:
    _HAS_WIN32 = False

try:
    import pywinauto  # type: ignore

    _HAS_PYWINAUTO = True
except ImportError:
    _HAS_PYWINAUTO = False


class Win32WindowManager:
    """Win32 窗口管理器。

    # 使用 ctypes 调用 Win32 API 枚举和操作窗口。
    # 比 UIA 更轻量，适合只需要窗口级操作的场景。
    # 不依赖 pywinauto 的 UIA 层，直接调用 Win32 API。
    """

    def is_available(self) -> bool:
        """检查 Win32 API 是否可用。"""
        return _HAS_WIN32

    def list_windows(self) -> list[dict[str, Any]]:
        """列出所有可见窗口。

        # 返回窗口信息列表，每项包含 handle、title、class_name、rect。
        # 过滤不可见窗口和空标题窗口。
        """
        if not _HAS_WIN32:
            return []

        windows: list[dict[str, Any]] = []

        def _enum_callback(hwnd: int, _lparam: int) -> bool:
            if not ctypes.windll.user32.IsWindowVisible(hwnd):
                return True

            title = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetWindowTextW(hwnd, title, 256)
            title_str = title.value.strip()

            if not title_str:
                return True

            class_name = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetClassNameW(hwnd, class_name, 256)

            rect = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))

            windows.append({
                "handle": hwnd,
                "title": title_str,
                "class_name": class_name.value,
                "rect": (rect.left, rect.top, rect.right, rect.bottom),
            })
            return True

        try:
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
            ctypes.windll.user32.EnumWindows(WNDENUMPROC(_enum_callback), 0)
        except Exception as exc:
            logger.warning("枚举窗口异常: %s", exc)

        return windows

    def find_window_by_title(self, title: str) -> dict[str, Any] | None:
        """按标题查找窗口（部分匹配）。"""
        title_lower = title.lower()
        for w in self.list_windows():
            if title_lower in w["title"].lower():
                return w
        return None

    def bring_to_front(self, hwnd: int) -> bool:
        """将窗口置于前台。"""
        if not _HAS_WIN32:
            return False

        try:
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            return True
        except Exception:
            return False

    def get_window_rect(self, hwnd: int) -> tuple[int, int, int, int] | None:
        """获取窗口矩形。"""
        if not _HAS_WIN32:
            return None

        try:
            rect = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            return (rect.left, rect.top, rect.right, rect.bottom)
        except Exception:
            return None

    def minimize_window(self, hwnd: int) -> bool:
        """最小化窗口。"""
        if not _HAS_WIN32:
            return False

        try:
            SW_MINIMIZE = 6
            ctypes.windll.user32.ShowWindow(hwnd, SW_MINIMIZE)
            return True
        except Exception:
            return False

    def restore_window(self, hwnd: int) -> bool:
        """恢复窗口。"""
        if not _HAS_WIN32:
            return False

        try:
            SW_RESTORE = 9
            ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
            return True
        except Exception:
            return False
