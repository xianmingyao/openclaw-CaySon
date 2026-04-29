"""
京麦商品发布自动化 - 导航操作 Actions
覆盖 57 个脚本：类目选择、滚动、保存草稿、发布、修改、返回
"""
import time
from typing import Dict, Any, Optional

from actions.registry import ActionRegistry
from config.jingmai_coords import CATEGORY_PAGE, PRODUCT_INFO_PAGE


def _get_locator(locator=None, log=None):
    if locator is None:
        from infrastructure.locator import JingmaiLocator
        return JingmaiLocator(log=log)
    return locator


@ActionRegistry.register("select_category", "navigation", "选择商品类目")
def select_category(search_text: str = "", level3_coords: tuple = None,
                    level4_coords: tuple = None, locator=None, log=None) -> Dict[str, Any]:
    """
    选择商品类目：
    1. 输入类目关键词搜索
    2. 或直接按坐标点击类目层级
    """
    locator = _get_locator(locator, log)

    if search_text:
        # 搜索方式：在类目搜索框输入关键词
        # 类目搜索框坐标
        search_coords = (640, 260)
        locator.click(search_coords[0], search_coords[1], delay=0.3)

        # 输入搜索词
        from actions.form import fill_text
        fill_text(search_text, x=search_coords[0], y=search_coords[1], locator=locator, log=log)
        time.sleep(1.0)

        # 按回车搜索
        try:
            import pyautogui
            pyautogui.press("enter")
        except Exception:
            locator.press_enter()
        time.sleep(2.0)

    # 坐标点击方式
    results = []
    if level3_coords:
        locator.click(level3_coords[0], level3_coords[1], delay=0.5)
        results.append("level3")
        time.sleep(1.0)

    if level4_coords:
        locator.click(level4_coords[0], level4_coords[1], delay=0.5)
        results.append("level4")
        time.sleep(1.0)
    elif not level3_coords and not search_text:
        # 使用默认坐标
        l3 = CATEGORY_PAGE.get("level3_third_col")
        l4 = CATEGORY_PAGE.get("level4")
        if l3:
            locator.click(l3[0], l3[1], delay=0.5)
            results.append("level3_default")
            time.sleep(1.0)
        if l4:
            locator.click(l4[0], l4[1], delay=0.5)
            results.append("level4_default")
            time.sleep(1.0)

    # 点击下一步
    next_btn = CATEGORY_PAGE.get("next_button")
    if next_btn:
        locator.click(next_btn[0], next_btn[1], delay=1.5)
        results.append("next")

    return {"success": True, "steps": results}


@ActionRegistry.register("scroll_page", "navigation", "滚动页面")
def scroll_page(x: int = 1280, y: int = 700, delta: int = -3, locator=None, log=None) -> Dict[str, Any]:
    """滚动页面（负值向下，正值向上）"""
    locator = _get_locator(locator, log)

    try:
        import pyautogui
        if locator.window_rect:
            screen_x = locator.window_rect[0] + x
            screen_y = locator.window_rect[1] + y
        else:
            screen_x, screen_y = x, y

        pyautogui.moveTo(screen_x, screen_y)
        pyautogui.scroll(delta)
        time.sleep(0.3)
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}


@ActionRegistry.register("save_draft", "navigation", "保存草稿")
def save_draft(locator=None, log=None) -> Dict[str, Any]:
    """点击保存草稿按钮"""
    locator = _get_locator(locator, log)

    coords = PRODUCT_INFO_PAGE.get("save_draft_button")
    if coords:
        locator.click(coords[0], coords[1], delay=1.5)
        return {"success": True}

    # fallback: UIA 查找
    try:
        from pywinauto import Desktop
        desktop = Desktop(backend="uia")
        from infrastructure.locator import WINDOW_KEYWORDS
        for w in desktop.windows():
            title = w.window_text()
            if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                continue
            for btn in w.descendants(control_type="Button"):
                if "保存草稿" in (btn.element_info.name or ""):
                    btn.invoke()
                    return {"success": True, "method": "uia"}
            break
    except Exception:
        pass

    return {"success": False, "message": "保存草稿按钮未找到"}


@ActionRegistry.register("publish_product", "navigation", "发布商品")
def publish_product(locator=None, log=None) -> Dict[str, Any]:
    """点击发布商品按钮"""
    locator = _get_locator(locator, log)

    coords = PRODUCT_INFO_PAGE.get("publish_button")
    if coords:
        locator.click(coords[0], coords[1], delay=2.0)
        return {"success": True}

    # fallback: UIA
    try:
        from pywinauto import Desktop
        desktop = Desktop(backend="uia")
        from infrastructure.locator import WINDOW_KEYWORDS
        for w in desktop.windows():
            title = w.window_text()
            if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                continue
            for btn in w.descendants(control_type="Button"):
                if "发布" in (btn.element_info.name or ""):
                    btn.invoke()
                    return {"success": True, "method": "uia"}
            break
    except Exception:
        pass

    return {"success": False, "message": "发布按钮未找到"}


@ActionRegistry.register("click_modify", "navigation", "点击修改链接")
def click_modify(locator=None, log=None) -> Dict[str, Any]:
    """点击修改链接（编辑已有商品）"""
    locator = _get_locator(locator, log)

    # 修改链接坐标（常见位置）
    modify_coords = [
        (979, 225), (979, 325), (979, 425),  # 多行商品
    ]

    try:
        from pywinauto import Desktop
        import pyautogui
        desktop = Desktop(backend="uia")
        from infrastructure.locator import WINDOW_KEYWORDS

        for w in desktop.windows():
            title = w.window_text()
            if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                continue
            # 查找"修改"链接
            for link in w.descendants(control_type="Hyperlink"):
                if "修改" in (link.element_info.name or ""):
                    try:
                        link.invoke()
                        return {"success": True, "method": "uia_link"}
                    except Exception:
                        rect = link.rectangle()
                        pyautogui.click(rect.left + 5, rect.top + 5)
                        return {"success": True, "method": "uia_link_coord"}
            break
    except Exception:
        pass

    # fallback: 坐标点击第一个
    for coords in modify_coords:
        locator.click(coords[0], coords[1], delay=1.0)

    return {"success": True, "method": "coordinate_fallback"}


@ActionRegistry.register("go_back", "navigation", "返回上一页")
def go_back(locator=None, log=None) -> Dict[str, Any]:
    """返回上一页"""
    locator = _get_locator(locator, log)

    # 策略1: 浏览器后退（Alt+Left）
    try:
        import win32api
        import win32con
        win32api.keybd_event(0x12, 0, 0, 0)  # Alt down
        win32api.keybd_event(0x25, 0, 0, 0)   # Left down
        win32api.keybd_event(0x25, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x12, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)
        return {"success": True, "method": "alt_left"}
    except Exception:
        pass

    # 策略2: ESC
    locator.press_escape(delay=0.5)
    return {"success": True, "method": "escape"}
