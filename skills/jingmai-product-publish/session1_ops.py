# -*- coding: utf-8 -*-
"""
Session1 Helper 操作封装
提供统一的 Session1 操作接口，解决 Session 0 无法操作京麦窗口的问题

使用方式：
    from session1_ops import s1_click, s1_paste, s1_hotkey, s1_press

如果 Helper 未运行，所有函数自动降级到 pyautogui（可能无效）。
"""
import time

# Singleton pipe client
_pipe_client = None


def _get_client():
    """获取 Pipe Client，懒加载"""
    global _pipe_client
    if _pipe_client is None:
        try:
            from pipe_client import create_client

            _pipe_client = create_client()
        except Exception:
            _pipe_client = False  # 标记为不可用
    return _pipe_client if _pipe_client else None


def s1_click(x: int, y: int, delay: float = 0.3) -> bool:
    """点击坐标（Session1 Helper）"""
    client = _get_client()
    if client:
        try:
            result = client.click(x, y, delay=delay)
            return result.get("success", False)
        except Exception:
            pass
    # Fallback: pyautogui
    try:
        import pyautogui

        pyautogui.click(x, y)
        time.sleep(delay)
        return True
    except Exception:
        return False


def s1_paste(text: str) -> bool:
    """剪贴板粘贴（Session1 Helper，推荐用于中文）"""
    client = _get_client()
    if client:
        try:
            result = client.paste(text)
            return result.get("success", False)
        except Exception:
            pass
    # Fallback: pyautogui
    try:
        import pyautogui
        import pyperclip

        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.3)
        return True
    except Exception:
        return False


def s1_hotkey(*keys) -> bool:
    """发送快捷键（Session1 Helper）"""
    client = _get_client()
    if client:
        try:
            result = client.hotkey(*keys)
            return result.get("success", False)
        except Exception:
            pass
    # Fallback: pyautogui
    try:
        import pyautogui

        pyautogui.hotkey(*keys)
        return True
    except Exception:
        return False


def s1_press(key: str) -> bool:
    """按单个键（Session1 Helper）"""
    client = _get_client()
    if client:
        try:
            result = client.press(key)
            return result.get("success", False)
        except Exception:
            pass
    # Fallback: pyautogui
    try:
        import pyautogui

        pyautogui.press(key)
        return True
    except Exception:
        return False


def s1_wait(seconds: float) -> bool:
    """等待（Session1 Helper）"""
    client = _get_client()
    if client:
        try:
            result = client.wait(seconds)
            return result.get("success", False)
        except Exception:
            pass
    time.sleep(seconds)
    return True


def s1_is_available() -> bool:
    """检查 Helper 是否可用"""
    return _get_client() is not None
