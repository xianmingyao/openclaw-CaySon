"""
京麦商品发布自动化 - 表单操作 Actions
覆盖 102 个脚本：文本输入、下拉选择、粘贴搜索、商品信息填充、元素点击、字段修正
"""
import time
from typing import Dict, Any, Optional

from actions.registry import ActionRegistry


def _get_locator(locator=None, log=None):
    """获取定位器实例"""
    if locator is None:
        from infrastructure.locator import JingmaiLocator
        return JingmaiLocator(log=log)
    return locator


@ActionRegistry.register("fill_text", "form", "4 层输入 fallback 填充文本")
def fill_text(text: str, x: int = None, y: int = None, name: str = "",
              index: int = 0, clear: bool = True, locator=None, log=None) -> Dict[str, Any]:
    """
    4 层输入 fallback：
    1. UIA Edit.set_edit_text
    2. win32clipboard + Ctrl+V
    3. pyperclip + Ctrl+V
    4. pyautogui.typewrite
    """
    locator = _get_locator(locator, log)

    # 先点击目标位置激活输入框
    if x is not None and y is not None:
        if not locator.click(x, y, delay=0.3):
            return {"success": False, "message": f"激活输入框失败: ({x}, {y})"}
        time.sleep(0.2)

    # 清除已有内容
    if clear:
        try:
            import win32api
            import win32con
            win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
            win32api.keybd_event(0x41, 0, 0, 0)   # A down
            win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
            win32api.keybd_event(0x2E, 0, 0, 0)   # Delete down
            win32api.keybd_event(0x2E, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.1)
        except Exception:
            import pyautogui
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            pyautogui.press('delete')

    # 尝试 UIA set_edit_text
    input_ok = False
    if name:
        try:
            from pywinauto import Desktop
            desktop = Desktop(backend="uia")
            from infrastructure.locator import WINDOW_KEYWORDS
            for w in desktop.windows():
                title = w.window_text()
                if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                    continue
                edits = w.descendants(control_type="Edit")
                count = 0
                for edit in edits:
                    edit_name = edit.element_info.name or ""
                    if name in edit_name or (not name and count == index):
                        try:
                            edit.set_edit_text(text)
                            input_ok = True
                        except Exception:
                            pass
                        break
                    count += 1
                break
        except Exception:
            pass

    # 层2: win32clipboard
    if not input_ok:
        try:
            import win32clipboard
            import win32con
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()

            import win32api
            win32api.keybd_event(0x11, 0, 0, 0)  # Ctrl down
            win32api.keybd_event(0x56, 0, 0, 0)   # V down
            win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.3)
            input_ok = True
        except Exception:
            pass

    # 层3: pyperclip
    if not input_ok:
        try:
            import pyperclip
            import pyautogui
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            input_ok = True
        except Exception:
            pass

    # 层4: typewrite
    if not input_ok:
        try:
            import pyautogui
            pyautogui.typewrite(text, interval=0.05)
            input_ok = True
        except Exception:
            return {"success": False, "message": f"输入失败: {text[:20]}"}

    return {"success": True, "text": text[:20]}


@ActionRegistry.register("select_dropdown", "form", "ComboBox 下拉选择")
def select_dropdown(x: int, y: int, option_text: str, locator=None, log=None) -> Dict[str, Any]:
    """点击下拉框，然后选择指定选项"""
    locator = _get_locator(locator, log)

    # 1. 点击展开下拉框
    locator.click(x, y, delay=0.5)

    # 2. 查找并点击选项
    try:
        from pywinauto import Desktop
        desktop = Desktop(backend="uia")
        import pyautogui
        from infrastructure.locator import WINDOW_KEYWORDS

        for w in desktop.windows():
            title = w.window_text()
            if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                continue
            elements = w.descendants()
            for elem in elements:
                try:
                    name = elem.element_info.name or ""
                    if option_text in name:
                        rect = elem.rectangle()
                        pyautogui.click(rect.left + 5, rect.top + 5)
                        return {"success": True, "option": option_text}
                except Exception:
                    continue
            break
    except Exception:
        pass

    return {"success": False, "message": f"选项未找到: {option_text}"}


@ActionRegistry.register("paste_and_search", "form", "粘贴文本并搜索")
def paste_and_search(text: str, x: int, y: int, enter: bool = True, locator=None, log=None) -> Dict[str, Any]:
    """粘贴文本到输入框并可选按回车搜索"""
    locator = _get_locator(locator, log)

    # 点击输入框
    locator.click(x, y, delay=0.3)

    # 粘贴文本
    result = fill_text(text, x=x, y=y, clear=True, locator=locator, log=log)
    if not result["success"]:
        return result

    # 按回车
    if enter:
        time.sleep(0.3)
        try:
            import pyautogui
            pyautogui.press("enter")
        except Exception:
            locator.press_enter()

    return {"success": True, "text": text}


@ActionRegistry.register("fill_product_info", "form", "批量填充商品信息")
def fill_product_info(product: Dict[str, Any], locator=None, log=None) -> Dict[str, Any]:
    """
    批量填充商品信息
    product 包含：title, brand, model, sku, market_price, jd_price, purchase_price 等
    """
    locator = _get_locator(locator, log)
    from config.jingmai_coords import PRODUCT_INFO_PAGE

    # 字段到坐标的映射
    field_coords = {
        "title": PRODUCT_INFO_PAGE.get("title_input"),
        "model": PRODUCT_INFO_PAGE.get("model_input"),
        "sku": PRODUCT_INFO_PAGE.get("sku_input"),
        "market_price": PRODUCT_INFO_PAGE.get("market_price"),
        "jd_price": PRODUCT_INFO_PAGE.get("jd_price"),
        "purchase_price": PRODUCT_INFO_PAGE.get("purchase_price"),
    }

    results = []
    for field, coords in field_coords.items():
        value = product.get(field)
        if value and coords:
            r = fill_text(str(value), x=coords[0], y=coords[1], locator=locator, log=log)
            results.append({"field": field, "success": r["success"]})
            time.sleep(0.5)

    success_count = sum(1 for r in results if r["success"])
    return {"success": True, "filled": success_count, "total": len(results), "details": results}


@ActionRegistry.register("click_element", "form", "点击指定元素")
def click_element(x: int = None, y: int = None, name: str = "", locator=None, log=None) -> Dict[str, Any]:
    """按坐标或名称点击元素"""
    locator = _get_locator(locator, log)

    if x is not None and y is not None:
        success = locator.click(x, y, delay=0.5)
        return {"success": success, "method": "coordinate"}

    if name:
        try:
            from pywinauto import Desktop
            import pyautogui
            desktop = Desktop(backend="uia")
            from infrastructure.locator import WINDOW_KEYWORDS

            for w in desktop.windows():
                title = w.window_text()
                if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                    continue
                # 尝试 Button
                for btn in w.descendants(control_type="Button"):
                    try:
                        if name in (btn.element_info.name or ""):
                            btn.invoke()
                            return {"success": True, "method": "uia_button", "name": name}
                    except Exception:
                        pass
                # 尝试 Hyperlink
                for link in w.descendants(control_type="Hyperlink"):
                    try:
                        if name in (link.element_info.name or ""):
                            link.invoke()
                            return {"success": True, "method": "uia_link", "name": name}
                    except Exception:
                        pass
                break
        except Exception:
            pass

    return {"success": False, "message": f"元素未找到: {name}"}


@ActionRegistry.register("fix_field", "form", "修正表单字段")
def fix_field(x: int, y: int, correct_value: str, locator=None, log=None) -> Dict[str, Any]:
    """修正指定位置的字段值"""
    locator = _get_locator(locator, log)

    # 点击激活
    locator.click(x, y, delay=0.3)

    # 全选并删除
    try:
        import win32api
        import win32con
        win32api.keybd_event(0x11, 0, 0, 0)
        win32api.keybd_event(0x41, 0, 0, 0)
        win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
        win32api.keybd_event(0x2E, 0, 0, 0)
        win32api.keybd_event(0x2E, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)
    except Exception:
        pass

    # 输入正确值
    result = fill_text(correct_value, x=x, y=y, clear=False, locator=locator, log=log)
    return result


@ActionRegistry.register("upload_image", "form", "上传商品图片")
def upload_image(image_path: str, x: int = None, y: int = None,
                 locator=None, log=None) -> Dict[str, Any]:
    """上传商品图片到指定位置"""
    import os
    if not os.path.exists(image_path):
        return {"success": False, "message": f"图片文件不存在: {image_path}"}

    locator = _get_locator(locator, log)

    # 点击上传区域激活
    if x is not None and y is not None:
        locator.click(x, y, delay=0.5)

    # 尝试 Ctrl+V 粘贴（如果图片已在剪贴板）
    try:
        from PIL import Image
        import win32clipboard
        import win32con
        import io

        img = Image.open(image_path)
        output = io.BytesIO()
        img.save(output, "PNG")
        data = output.getvalue()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

        import win32api
        win32api.keybd_event(0x11, 0, 0, 0)
        win32api.keybd_event(0x56, 0, 0, 0)
        win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)
        return {"success": True, "method": "clipboard_paste", "image": image_path}
    except Exception:
        pass

    return {"success": False, "message": "图片上传失败，尝试粘贴方式未成功"}


@ActionRegistry.register("wait_and_click", "form", "等待元素出现后点击")
def wait_and_click(name: str = "", x: int = None, y: int = None,
                   timeout: float = 10.0, interval: float = 1.0,
                   locator=None, log=None) -> Dict[str, Any]:
    """等待指定元素出现后点击，超时返回失败"""
    import time as _time
    locator = _get_locator(locator, log)
    start = _time.time()

    while _time.time() - start < timeout:
        # 坐标方式：直接尝试点击
        if x is not None and y is not None:
            locator.click(x, y, delay=0.3)
            return {"success": True, "method": "coordinate"}

        # 名称方式：尝试 UIA 查找
        if name:
            try:
                from pywinauto import Desktop
                desktop = Desktop(backend="uia")
                from infrastructure.locator import WINDOW_KEYWORDS
                for w in desktop.windows():
                    title = w.window_text()
                    if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                        continue
                    for elem in w.descendants():
                        try:
                            elem_name = elem.element_info.name or ""
                            if name in elem_name:
                                elem.invoke()
                                return {"success": True, "method": "uia", "name": name}
                        except Exception:
                            continue
                    break
            except Exception:
                pass

        _time.sleep(interval)

    return {"success": False, "message": f"等待超时: {name or (x, y)}"}
