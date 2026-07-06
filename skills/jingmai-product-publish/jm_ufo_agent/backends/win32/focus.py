"""Win32 焦点管理 — 窗口激活和焦点控制。

处理窗口切换、焦点获取和 Z 序管理等操作。
确保目标窗口在执行操作前处于激活状态。
"""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

# Windows 专用导入保护
try:
    import ctypes
    import ctypes.wintypes  # type: ignore

    _HAS_WIN32 = True
except ImportError:
    _HAS_WIN32 = False


class Win32FocusManager:
    """Win32 焦点管理器。

    # 管理窗口激活和焦点切换。
    # 在执行 GUI 操作前确保目标窗口处于前台。
    # 支持 Alt+Tab 模拟和 SetForegroundWindow 调用。
    # 包含重试机制，应对 Windows 前台锁定限制。
    """

    def __init__(self, retry_count: int = 3, retry_interval_sec: float = 0.5):
        """初始化焦点管理器。"""
        self._retry_count = retry_count
        self._retry_interval = retry_interval_sec

    def is_available(self) -> bool:
        """检查 Win32 API 是否可用。"""
        return _HAS_WIN32

    def set_foreground(self, hwnd: int) -> bool:
        """将指定窗口设为前台窗口。

        # 使用 SetForegroundWindow，失败时重试。
        # Windows 限制非前台进程调用 SetForegroundWindow，
        # 通过 AttachThreadInput 绕过限制。
        """
        if not _HAS_WIN32:
            return False

        for attempt in range(self._retry_count):
            try:
                # 尝试直接设置前台
                result = ctypes.windll.user32.SetForegroundWindow(hwnd)
                if result:
                    return True

                # 直接设置失败，尝试 AttachThreadInput 方式
                if self._force_foreground(hwnd):
                    return True

            except Exception as exc:
                logger.debug("SetForegroundWindow 第 %d 次尝试异常: %s", attempt + 1, exc)

            if attempt < self._retry_count - 1:
                time.sleep(self._retry_interval)

        logger.warning("无法将窗口 %d 设为前台", hwnd)
        return False

    def get_foreground_window(self) -> int | None:
        """获取当前前台窗口句柄。"""
        if not _HAS_WIN32:
            return None

        try:
            return ctypes.windll.user32.GetForegroundWindow()
        except Exception:
            return None

    def is_foreground(self, hwnd: int) -> bool:
        """检查指定窗口是否在前台。"""
        current = self.get_foreground_window()
        return current == hwnd

    def wait_for_foreground(self, hwnd: int, timeout_sec: float = 5.0) -> bool:
        """等待窗口进入前台。"""
        deadline = time.monotonic() + timeout_sec
        while time.monotonic() < deadline:
            if self.is_foreground(hwnd):
                return True
            time.sleep(0.1)
        return False

    @staticmethod
    def _force_foreground(hwnd: int) -> bool:
        """强制将窗口设为前台（使用 AttachThreadInput）。"""
        try:
            foreground = ctypes.windll.user32.GetForegroundWindow()
            if foreground == hwnd:
                return True

            foreground_thread = ctypes.windll.user32.GetWindowThreadProcessId(foreground, None)
            target_thread = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)

            if foreground_thread != target_thread:
                ctypes.windll.user32.AttachThreadInput(foreground_thread, target_thread, True)

            ctypes.windll.user32.BringWindowToTop(hwnd)
            result = ctypes.windll.user32.SetForegroundWindow(hwnd)

            if foreground_thread != target_thread:
                ctypes.windll.user32.AttachThreadInput(foreground_thread, target_thread, False)

            return bool(result)
        except Exception:
            return False
