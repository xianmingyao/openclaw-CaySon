"""
京麦商品发布自动化 - 弹窗操作 Actions
覆盖 56 个脚本：关闭弹窗、处理对话框、关闭 CEF 弹窗
"""
import time
from typing import Dict, Any, Optional

from actions.registry import ActionRegistry


def _get_locator(locator=None, log=None):
    if locator is None:
        from infrastructure.locator import JingmaiLocator
        return JingmaiLocator(log=log)
    return locator


@ActionRegistry.register("dismiss_popup", "popup", "关闭弹窗")
def dismiss_popup(method: str = "escape", x: int = None, y: int = None,
                  locator=None, log=None) -> Dict[str, Any]:
    """
    关闭弹窗，多种方式：
    - escape: 按 ESC
    - click_x: 点击关闭按钮（需传坐标）
    - click_ok: 点击确定按钮
    - auto: 自动尝试所有方式
    """
    locator = _get_locator(locator, log)
    methods = [method] if method != "auto" else ["escape", "click_x", "click_ok"]

    for m in methods:
        if m == "escape":
            try:
                locator.press_escape(delay=0.5)
                if log:
                    log.debug("dismiss_popup: ESC")
                return {"success": True, "method": "escape"}
            except Exception:
                continue

        elif m == "click_x" and x is not None and y is not None:
            try:
                locator.click(x, y, delay=0.5)
                return {"success": True, "method": "click_x", "coords": (x, y)}
            except Exception:
                continue

        elif m == "click_ok":
            try:
                from pywinauto import Desktop
                desktop = Desktop(backend="uia")
                from infrastructure.locator import WINDOW_KEYWORDS
                for w in desktop.windows():
                    title = w.window_text()
                    if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                        continue
                    for btn in w.descendants(control_type="Button"):
                        btn_name = (btn.element_info.name or "").lower()
                        if any(kw in btn_name for kw in ["确定", "ok", "关闭", "close", "取消"]):
                            try:
                                btn.invoke()
                                return {"success": True, "method": "click_ok"}
                            except Exception:
                                rect = btn.rectangle()
                                import pyautogui
                                pyautogui.click(rect.left + 5, rect.top + 5)
                                return {"success": True, "method": "click_ok_coord"}
                    break
            except Exception:
                continue

    return {"success": False, "message": "弹窗关闭失败"}


@ActionRegistry.register("handle_dialog", "popup", "处理对话框")
def handle_dialog(action: str = "accept", locator=None, log=None) -> Dict[str, Any]:
    """处理对话框（accept=确认, dismiss=取消）"""
    locator = _get_locator(locator, log)

    button_keywords = {
        "accept": ["确定", "ok", "是", "yes", "确认"],
        "dismiss": ["取消", "cancel", "否", "no", "关闭"],
    }
    keywords = button_keywords.get(action, button_keywords["accept"])

    try:
        from pywinauto import Desktop
        import pyautogui
        desktop = Desktop(backend="uia")
        from infrastructure.locator import WINDOW_KEYWORDS

        for w in desktop.windows():
            title = w.window_text()
            if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                continue
            for btn in w.descendants(control_type="Button"):
                btn_name = (btn.element_info.name or "").lower()
                if any(kw in btn_name for kw in keywords):
                    try:
                        btn.invoke()
                    except Exception:
                        rect = btn.rectangle()
                        pyautogui.click(rect.left + 5, rect.top + 5)
                    return {"success": True, "action": action, "button": btn.element_info.name}
            break
    except Exception as e:
        return {"success": False, "message": str(e)}

    return {"success": False, "message": f"未找到对话框按钮: {action}"}


@ActionRegistry.register("dismiss_cef_popup", "popup", "关闭 CEF 弹窗")
def dismiss_cef_popup(locator=None, log=None) -> Dict[str, Any]:
    """关闭 CEF 内嵌浏览器弹窗 — 多策略尝试"""
    locator = _get_locator(locator, log)

    # 策略1: ESC
    locator.press_escape(delay=0.5)
    time.sleep(0.3)

    # 策略2: Tab + Enter（焦点可能在弹窗按钮上）
    try:
        import pyautogui
        pyautogui.press('tab')
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(0.3)
    except Exception:
        pass

    # 策略3: 右上角 X 坐标（常见位置）
    if locator.window_rect:
        # 尝试窗口右上角区域的关闭按钮
        right = locator.window_rect[2]
        top = locator.window_rect[1]
        for offset_x in [50, 100, 150]:
            for offset_y in [15, 25, 35]:
                locator.click(right - offset_x, top + offset_y, delay=0.3)

    return {"success": True, "method": "multi_strategy"}
