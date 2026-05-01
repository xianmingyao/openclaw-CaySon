"""
京麦商品发布自动化 - UIA 窗口查找公共辅助函数
统一替代各 action 中重复的 Desktop(backend="uia").windows() 遍历
"""
from typing import Optional


def find_jingmai_uia_window(locator=None, log=None):
    """获取京麦 UIA 窗口对象（优先用 locator 缓存）

    优先使用 locator.get_uia_window()（带 5s TTL 缓存），
    fallback 直接遍历所有窗口（无缓存，慢）。
    """
    # 优先走 locator 缓存
    if locator and hasattr(locator, 'get_uia_window'):
        try:
            window = locator.get_uia_window()
            if window:
                return window
        except Exception:
            pass

    # fallback: 直接遍历（无缓存）
    try:
        from pywinauto import Desktop
        from infrastructure.locator import WINDOW_KEYWORDS
        desktop = Desktop(backend="uia")
        for w in desktop.windows():
            try:
                title = w.window_text()
                if any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                    return w
            except Exception:
                continue
    except Exception:
        pass

    return None
