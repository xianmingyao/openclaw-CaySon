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


def _select_search_result(search_text: str, log=None) -> bool:
    """搜索类目后，尝试选择最匹配的搜索结果。"""
    try:
        import pyautogui
        # 京麦搜索后通常会有下拉列表，先按一次 ↓ 选中高亮项
        pyautogui.press("down")
        time.sleep(0.5)
        # 如果搜索词包含"插座"，尝试再按一次 ↓ 跳过可能的第一层分类
        if "插座" in search_text:
            pyautogui.press("down")
            time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(1.0)
        return True
    except Exception as exc:
        if log:
            log.warning(f"类目搜索结果选择失败: {exc}")
        return False


def _page_contains_text(expected_text: str, locator=None, log=None) -> bool:
    """使用 UIA 扫描当前窗口文本，判断页面是否出现目标文本。"""
    locator = _get_locator(locator, log)
    try:
        for elem in locator.inspect_elements():
            name = str(elem.get("name") or "")
            if expected_text in name:
                return True
    except Exception as exc:
        if log:
            log.warning(f"页面文本扫描失败: {exc}")
    return False


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
        if not locator.click(search_coords[0], search_coords[1], delay=0.3):
            return {"success": False, "message": "点击类目搜索框失败"}

        # 输入搜索词
        from actions.form import fill_text
        fill_result = fill_text(search_text, x=search_coords[0], y=search_coords[1], locator=locator, log=log)
        if not fill_result["success"]:
            return fill_result
        time.sleep(1.0)

        # 按回车搜索
        try:
            import pyautogui
            pyautogui.press("enter")
        except Exception:
            locator.press_enter()
        time.sleep(2.0)
        results = ["search"]
        if not _select_search_result(search_text, log=log):
            return {"success": False, "message": f"未找到类目搜索结果: {search_text}", "steps": results}
        results.append("search_select")
        time.sleep(1.0)
        if not _page_contains_text(search_text, locator=locator, log=log):
            return {
                "success": False,
                "message": f"类目选择后页面未出现目标关键词: {search_text}",
                "steps": results,
            }
    else:
        results = []

    # 坐标点击方式
    if level3_coords:
        if not locator.click(level3_coords[0], level3_coords[1], delay=0.5):
            return {"success": False, "message": "点击三级类目失败", "steps": results}
        results.append("level3")
        time.sleep(1.0)

    if level4_coords:
        if not locator.click(level4_coords[0], level4_coords[1], delay=0.5):
            return {"success": False, "message": "点击四级类目失败", "steps": results}
        results.append("level4")
        time.sleep(1.0)
    elif not level3_coords and not search_text:
        # 使用默认坐标
        l3 = CATEGORY_PAGE.get("level3_third_col")
        l4 = CATEGORY_PAGE.get("level4")
        if l3:
            if not locator.click(l3[0], l3[1], delay=0.5):
                return {"success": False, "message": "点击默认三级类目失败", "steps": results}
            results.append("level3_default")
            time.sleep(1.0)
        if l4:
            if not locator.click(l4[0], l4[1], delay=0.5):
                return {"success": False, "message": "点击默认四级类目失败", "steps": results}
            results.append("level4_default")
            time.sleep(1.0)

    # 点击下一步
    next_btn = CATEGORY_PAGE.get("next_button")
    if next_btn:
        if not locator.click(next_btn[0], next_btn[1], delay=1.5):
            return {"success": False, "message": "点击下一步失败", "steps": results}
        results.append("next")
        time.sleep(2.0)
        if _page_contains_text("类目选择发品", locator=locator, log=log):
            return {
                "success": False,
                "message": "点击下一步后仍停留在类目选择页",
                "steps": results,
            }

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
        success = locator.click(coords[0], coords[1], delay=1.5)
        return {"success": success, "method": "coordinate", "message": "" if success else "点击保存草稿失败"}

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
        success = locator.click(coords[0], coords[1], delay=2.0)
        return {"success": success, "method": "coordinate", "message": "" if success else "点击发布按钮失败"}

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
        if locator.click(coords[0], coords[1], delay=1.0):
            return {"success": True, "method": "coordinate_fallback"}

    return {"success": False, "message": "点击修改链接失败"}


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
