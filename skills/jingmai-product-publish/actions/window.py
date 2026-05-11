"""
京麦商品发布自动化 - 窗口操作 Actions
覆盖 43 个脚本：窗口查找、激活、导航、截图、元素扫描、焦点管理
"""
import time
from typing import Optional, Dict, Any, List

from actions.registry import ActionRegistry


@ActionRegistry.register("find_window", "window", "查找京麦窗口")
def find_window(locator=None, log=None) -> Optional[Dict[str, Any]]:
    """查找京麦窗口，返回窗口信息"""
    if locator is None:
        from infrastructure.locator import JingmaiLocator
        locator = JingmaiLocator(log=log)

    window_info = locator.find_window()
    if window_info:
        return {
            "success": True,
            "hwnd": window_info.hwnd,
            "title": window_info.title,
            "rect": window_info.rect,
            "width": window_info.width,
            "height": window_info.height,
        }
    return {"success": False, "message": "未找到京麦窗口"}


@ActionRegistry.register("activate_window", "window", "激活并调整京麦窗口")
def activate_window(locator=None, log=None) -> Dict[str, Any]:
    """激活京麦窗口，调整大小和位置"""
    if locator is None:
        from infrastructure.locator import JingmaiLocator
        locator = JingmaiLocator(log=log)

    # 先查找窗口
    window_info = locator.find_window()
    if not window_info:
        return {"success": False, "message": "窗口未找到"}

    # 激活
    success = locator.activate_window()
    return {"success": success, "title": window_info.title}


@ActionRegistry.register("navigate_to", "window", "导航到指定页面")
def navigate_to(page: str = "publish", locator=None, log=None) -> Dict[str, Any]:
    """导航到指定页面（publish=发布商品, products=商品管理）"""
    if locator is None:
        from infrastructure.locator import JingmaiLocator
        locator = JingmaiLocator(log=log)

    # 导航坐标（窗口相对坐标）
    NAV_COORDS = {
        "publish": [
            ("点击商品菜单", 34, 145),
            ("点击发布商品", 34, 195),
        ],
        "products": [
            ("点击商品菜单", 34, 145),
            ("点击我的商品", 34, 220),
        ],
    }

    steps = NAV_COORDS.get(page, [])
    if not steps:
        return {"success": False, "message": f"未知页面: {page}"}

    results = []
    for desc, x, y in steps:
        if log:
            log.info(f"导航: {desc}")
        if not locator.click(x, y, delay=1.0):
            return {"success": False, "message": f"导航失败: {desc}", "steps": results}
        results.append(desc)
        time.sleep(1.5)

    return {"success": True, "page": page, "steps": results}


@ActionRegistry.register("take_screenshot", "window", "窗口截图")
def take_screenshot(save_path: str = None, locator=None, log=None) -> Dict[str, Any]:
    """对京麦窗口进行截图"""
    if locator is None:
        from infrastructure.locator import JingmaiLocator
        locator = JingmaiLocator(log=log)

    path = locator.take_screenshot(save_path)
    if path:
        return {"success": True, "path": path}
    return {"success": False, "message": "截图失败"}


@ActionRegistry.register("inspect_elements", "window", "UIA 元素扫描")
def inspect_elements(control_type: str = None, locator=None, log=None) -> Dict[str, Any]:
    """扫描窗口内 UIA 元素"""
    if locator is None:
        from infrastructure.locator import JingmaiLocator
        locator = JingmaiLocator(log=log)

    elements = locator.inspect_elements(control_type)
    return {"success": True, "count": len(elements), "elements": elements}


@ActionRegistry.register("set_focus", "window", "设置窗口焦点")
def set_focus(locator=None, log=None) -> Dict[str, Any]:
    """将京麦窗口设为前台焦点"""
    if locator is None:
        from infrastructure.locator import JingmaiLocator
        locator = JingmaiLocator(log=log)

    try:
        import win32gui
        import win32con
        if locator.hwnd:
            win32gui.ShowWindow(locator.hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)
            win32gui.SetForegroundWindow(locator.hwnd)
            time.sleep(0.3)
            return {"success": True}
    except Exception as e:
        pass

    # fallback: activate_window
    success = locator.activate_window()
    return {"success": success}


@ActionRegistry.register("refresh_page", "window", "刷新当前京麦页面")
def refresh_page(mode: str = "soft", locator=None, log=None) -> Dict[str, Any]:
    """Refresh the current Jingmai page with keyboard shortcuts."""
    if locator is None:
        from infrastructure.locator import JingmaiLocator
        locator = JingmaiLocator(log=log)

    try:
        locator.activate_window()
    except Exception:
        pass

    try:
        import pyautogui

        if str(mode or "").lower() == "hard":
            pyautogui.hotkey("ctrl", "f5")
            method = "ctrl+f5"
        else:
            pyautogui.press("f5")
            method = "f5"
        time.sleep(1.5)
        return {"success": True, "mode": mode, "method": method}
    except Exception as exc:
        return {"success": False, "mode": mode, "message": str(exc)}
