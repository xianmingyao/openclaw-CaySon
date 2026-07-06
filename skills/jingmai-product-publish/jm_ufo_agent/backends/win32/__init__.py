"""Win32 后端 — 原生 Win32 API 窗口操作封装。"""

from jm_ufo_agent.backends.win32.window import Win32WindowManager
from jm_ufo_agent.backends.win32.focus import Win32FocusManager

__all__ = ["Win32WindowManager", "Win32FocusManager"]
