"""
京麦商品发布自动化 - UIA 公共辅助函数
统一替代各 action 中重复的 Desktop(backend="uia").windows() 遍历
"""
from pathlib import Path
from typing import Iterable, Optional


def find_jingmai_uia_window(locator=None, log=None):
    """获取京麦 UIA 窗口对象，优先使用 locator 缓存。"""
    if locator and hasattr(locator, "get_uia_window"):
        try:
            window = locator.get_uia_window()
            if window:
                return window
        except Exception:
            pass

    try:
        from pywinauto import Desktop
        from infrastructure.locator import WINDOW_KEYWORDS

        desktop = Desktop(backend="uia")
        for window in desktop.windows():
            try:
                title = window.window_text()
                if any(keyword in (title or "").lower() for keyword in WINDOW_KEYWORDS):
                    return window
            except Exception:
                continue
    except Exception:
        pass

    return None


def iter_named_descendants(
    window,
    control_types: Optional[Iterable[str]] = None,
    top_range: Optional[tuple[int, int]] = None,
    left_range: Optional[tuple[int, int]] = None,
    keywords: Optional[Iterable[str]] = None,
    exclude_keywords: Optional[Iterable[str]] = None,
    max_name_length: int = 0,
    limit: int = 200,
):
    """Yield named descendants filtered by region and text rules."""
    try:
        from infrastructure.uia_inspector import UIAControlInspector

        elements = UIAControlInspector.find_descendants(
            window,
            control_type_list=list(control_types) if control_types else None,
            is_visible=True,
            is_enabled=True,
            limit=limit,
        )
    except Exception:
        try:
            elements = window.descendants()
        except Exception:
            elements = []

    include_terms = [str(item).strip().lower() for item in (keywords or []) if str(item).strip()]
    exclude_terms = [str(item).strip().lower() for item in (exclude_keywords or []) if str(item).strip()]

    for elem in elements:
        try:
            rect = elem.rectangle()
            name = str(getattr(elem.element_info, "name", "") or "").strip()
            control_type = str(getattr(elem.element_info, "control_type", "") or "")
        except Exception:
            continue

        if not name:
            continue
        if max_name_length and len(name) > max_name_length:
            continue
        if top_range and not (top_range[0] <= rect.top <= top_range[1]):
            continue
        if left_range and not (left_range[0] <= rect.left <= left_range[1]):
            continue

        lower_name = name.lower()
        if include_terms and not all(term in lower_name for term in include_terms):
            continue
        if exclude_terms and any(term in lower_name for term in exclude_terms):
            continue

        yield {
            "element": elem,
            "name": name,
            "control_type": control_type,
            "rect": rect,
        }


def click_uia_element(elem, log=None) -> bool:
    # 方法1: 尝试 UIA invoke()（标准点击，但 CEF 可能不响应）
    try:
        elem.invoke()
        return True
    except Exception:
        pass

    # 方法2: 尝试 click_input()（pywinauto 直接发送输入事件，对 CEF 有效）
    try:
        elem.click_input()
        return True
    except Exception:
        pass

    # 方法3: 使用 PostMessage WM_LBUTTONDOWN/UP 发送到 WindowFromPoint 目标窗口
    try:
        import win32gui
        import win32con

        rect = elem.rectangle()
        center_x = (rect.left + rect.right) // 2
        center_y = (rect.top + rect.bottom) // 2
        target_hwnd = win32gui.WindowFromPoint((center_x, center_y))

        if target_hwnd:
            win32gui.PostMessage(target_hwnd, win32con.WM_LBUTTONDOWN, 0, (center_y << 16) | center_x)
            win32gui.PostMessage(target_hwnd, win32con.WM_LBUTTONUP, 0, (center_y << 16) | center_x)
            return True
    except Exception:
        pass

    # 方法4: 降级到 pyautogui（可能对 CEF 无效）
    try:
        rect = elem.rectangle()
        import pyautogui

        pyautogui.click((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
        return True
    except Exception as exc:
        if log:
            log.warning(f"UIA click failed: {exc}")
        return False


def score_text_match(name: str, desired_text: str, keywords: Optional[Iterable[str]] = None) -> int:
    lower_name = str(name or "").lower()
    target = str(desired_text or "").strip().lower()
    score = 0

    if target and target in lower_name:
        score += 12

    for keyword in keywords or []:
        token = str(keyword).strip().lower()
        if token and token in lower_name:
            score += 4

    return score


def resolve_template_path(*parts: str) -> Optional[str]:
    candidate = Path(__file__).resolve().parent.parent / "resources" / "screenshots"
    for part in parts:
        candidate = candidate / part
    return str(candidate) if candidate.exists() else None
