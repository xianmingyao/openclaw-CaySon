"""
京麦商品发布自动化 - 表单操作 Actions
覆盖 102 个脚本：文本输入、下拉选择、粘贴搜索、商品信息填充、元素点击、字段修正
"""
import time
from decimal import Decimal, InvalidOperation
from typing import Dict, Any, Optional

from actions.registry import ActionRegistry


def _get_locator(locator=None, log=None):
    """获取定位器实例"""
    if locator is None:
        from infrastructure.locator import JingmaiLocator
        return JingmaiLocator(log=log)
    return locator


def _normalize_text(value: Any) -> str:
    return str(value).strip().replace("\r\n", "\n").replace("\r", "\n")


def _normalize_numeric_text(value: Any) -> Optional[str]:
    text = _normalize_text(value).replace(",", "")
    if not text:
        return None
    try:
        number = Decimal(text)
    except (InvalidOperation, ValueError):
        return None
    normalized = format(number.normalize(), "f")
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    return normalized or "0"


def _compare_field_value(field: str, expected: Any, actual: Any) -> Dict[str, Any]:
    expected_text = _normalize_text(expected)
    actual_text = _normalize_text(actual)
    if field in {"market_price", "jd_price", "purchase_price"}:
        expected_norm = _normalize_numeric_text(expected_text)
        actual_norm = _normalize_numeric_text(actual_text)
        return {
            "success": expected_norm is not None and actual_norm is not None and expected_norm == actual_norm,
            "compare_mode": "numeric",
            "expected": expected_norm or expected_text,
            "actual": actual_norm or actual_text,
        }
    return {
        "success": expected_text == actual_text,
        "compare_mode": "text",
        "expected": expected_text,
        "actual": actual_text,
    }


def _read_clipboard_text() -> str:
    try:
        import win32clipboard

        win32clipboard.OpenClipboard()
        try:
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                return win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT) or ""
        finally:
            win32clipboard.CloseClipboard()
    except Exception:
        pass

    try:
        import pyperclip

        return pyperclip.paste() or ""
    except Exception:
        return ""


def _read_uia_value_for_field(locator, x: int, y: int) -> Dict[str, Any]:
    try:
        from actions._uia_helpers import find_jingmai_uia_window

        window = find_jingmai_uia_window(locator=locator)
        if not window:
            return {"success": False, "message": "uia window not found"}

        screen_x, screen_y = locator.window_to_screen(*locator.adapt_coords(x, y))
        best = None
        best_distance = None
        for edit in window.descendants(control_type="Edit"):
            try:
                rect = edit.rectangle()
                if rect.left <= screen_x <= rect.right and rect.top <= screen_y <= rect.bottom:
                    value = ""
                    try:
                        value = edit.get_value() or ""
                    except Exception:
                        value = ""
                    if value:
                        return {"success": True, "actual": value, "method": "uia-get-value"}
                    return {"success": False, "message": "uia value empty", "method": "uia-get-value"}

                center_x = (rect.left + rect.right) / 2
                center_y = (rect.top + rect.bottom) / 2
                distance = abs(center_x - screen_x) + abs(center_y - screen_y)
                if best_distance is None or distance < best_distance:
                    best_distance = distance
                    best = edit
            except Exception:
                continue

        if best is not None and best_distance is not None and best_distance <= 120:
            try:
                value = best.get_value() or ""
            except Exception:
                value = ""
            if value:
                return {"success": True, "actual": value, "method": "uia-nearest-edit"}
            return {"success": False, "message": "uia nearest value empty", "method": "uia-nearest-edit"}
        return {"success": False, "message": "no matching uia edit"}
    except Exception as exc:
        return {"success": False, "message": f"uia read failed: {exc}"}


def _read_clipboard_value_for_field(locator, x: int, y: int) -> Dict[str, Any]:
    if not locator.click(x, y, delay=0.2):
        return {"success": False, "message": f"readback focus failed: ({x}, {y})"}

    time.sleep(0.15)
    try:
        import pyautogui

        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.05)
        pyautogui.hotkey("ctrl", "c")
    except Exception:
        try:
            import win32api
            import win32con

            win32api.keybd_event(0x11, 0, 0, 0)
            win32api.keybd_event(0x41, 0, 0, 0)
            win32api.keybd_event(0x41, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
            win32api.keybd_event(0x11, 0, 0, 0)
            win32api.keybd_event(0x43, 0, 0, 0)
            win32api.keybd_event(0x43, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
        except Exception as exc:
            return {"success": False, "message": f"readback copy failed: {exc}"}

    time.sleep(0.15)
    actual_text = _read_clipboard_text()
    if not _normalize_text(actual_text):
        return {"success": False, "message": "clipboard readback empty", "method": "clipboard-readback"}
    return {"success": True, "actual": actual_text, "method": "clipboard-readback"}


def _verify_text_field(locator, field: str, x: int, y: int, expected: Any) -> Dict[str, Any]:
    readers = (_read_uia_value_for_field, _read_clipboard_value_for_field)
    failures = []
    for reader in readers:
        read_result = reader(locator, x, y)
        method = read_result.get("method", reader.__name__)
        if not read_result.get("success"):
            failures.append({"method": method, "reason": read_result.get("message", "read failed")})
            continue

        comparison = _compare_field_value(field, expected, read_result.get("actual", ""))
        if comparison["success"]:
            return {
                "success": True,
                "actual": comparison["actual"],
                "expected": comparison["expected"],
                "method": method,
                "compare_mode": comparison["compare_mode"],
            }

        failures.append(
            {
                "method": method,
                "reason": "value mismatch",
                "expected": comparison["expected"],
                "actual": comparison["actual"],
                "compare_mode": comparison["compare_mode"],
            }
        )

    summary = "; ".join(
        f"{item['method']}: {item['reason']}"
        + (f" (expected={item.get('expected')!r}, actual={item.get('actual')!r})" if "expected" in item else "")
        for item in failures
    ) or "no verification method available"
    return {"success": False, "message": summary, "failures": failures}


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
    
    注意：brand 是下拉选择，需要用 select_dropdown 而不是 fill_text
    """
    locator = _get_locator(locator, log)
    from config.jingmai_coords import PRODUCT_INFO_PAGE

    results = []

    # === 文本字段 ===
    text_fields = {
        "title": PRODUCT_INFO_PAGE.get("title_input"),
        "model": PRODUCT_INFO_PAGE.get("model_input"),
        "sku": PRODUCT_INFO_PAGE.get("sku_input"),
        "market_price": PRODUCT_INFO_PAGE.get("market_price"),
        "jd_price": PRODUCT_INFO_PAGE.get("jd_price"),
        "purchase_price": PRODUCT_INFO_PAGE.get("purchase_price"),
    }

    for field, coords in text_fields.items():
        value = product.get(field)
        if value and coords:
            r = fill_text(str(value), x=coords[0], y=coords[1], locator=locator, log=log)
            field_result = {
                "field": field,
                "method": "fill_text",
                "write_success": r["success"],
                "verify_success": False,
                "success": r["success"],
                "expected": str(value),
            }
            if r["success"]:
                verify = _verify_text_field(locator, field, coords[0], coords[1], value)
                field_result["verify_success"] = verify["success"]
                field_result["verification_method"] = verify.get("method", "")
                field_result["compare_mode"] = verify.get("compare_mode", "")
                field_result["actual"] = verify.get("actual", "")
                field_result["expected_normalized"] = verify.get("expected", str(value))
                if verify["success"]:
                    field_result["success"] = True
                else:
                    field_result["success"] = False
                    field_result["verify_error"] = verify.get("message", "readback failed")
                    field_result["verification_failures"] = verify.get("failures", [])
            else:
                field_result["verify_error"] = r.get("message", "write failed")
            results.append(field_result)
            time.sleep(0.3)

    # === 品牌下拉选择 ===
    brand = product.get("brand") or product.get("品牌")
    if brand:
        brand_select_coords = PRODUCT_INFO_PAGE.get("brand_select")
        if brand_select_coords:
            # 品牌是下拉选择，需要先点击展开，再选择选项
            r = _select_dropdown_option(brand, brand_select_coords[0], brand_select_coords[1], locator, log)
            results.append({
                "field": "brand",
                "method": "select_dropdown",
                "value": brand,
                "write_success": r["success"],
                "verify_success": r["success"],
                "success": r["success"],
            })
            time.sleep(0.5)

    success_count = sum(1 for r in results if r["success"])
    total = len(results)
    overall_success = total > 0 and success_count == total
    failed_fields = [r.get("field", "") for r in results if not r.get("success")]
    payload = {
        "success": overall_success,
        "filled": success_count,
        "total": total,
        "details": results,
    }
    if failed_fields:
        payload["failed_fields"] = failed_fields
        payload["message"] = f"Some product fields failed verification: {', '.join(failed_fields)}"
        payload["error"] = payload["message"]
    elif total == 0:
        payload["message"] = "No supported product fields were provided"
        payload["error"] = payload["message"]
    else:
        payload["message"] = "All requested product fields were filled and verified"
    return payload


def _select_dropdown_option(option_text: str, x: int, y: int, locator=None, log=None) -> Dict[str, Any]:
    """
    下拉选择内部实现：点击展开下拉框，然后选择选项
    """
    if log:
        log.debug(f"[select_dropdown] 展开下拉框: ({x}, {y}), 选择: {option_text}")
    
    # 1. 点击展开下拉框
    click_result = locator.click(x, y, delay=0.5)
    if not click_result:
        if log:
            log.warning(f"[select_dropdown] 点击下拉框失败: ({x}, {y})")
        return {"success": False, "message": f"点击下拉框失败: ({x}, {y})"}
    
    time.sleep(0.8)  # 等待下拉列表展开
    
    # 2. 查找并点击选项
    try:
        from pywinauto import Desktop
        import pyautogui
        from infrastructure.locator import WINDOW_KEYWORDS

        desktop = Desktop(backend="uia")
        
        for w in desktop.windows():
            title = w.window_text()
            # 只在京东窗口中查找
            if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                continue
            
            # 查找下拉列表中的选项
            elements = w.descendants()
            for elem in elements:
                try:
                    name = elem.element_info.name or ""
                    # 匹配选项文本（支持模糊匹配）
                    if option_text.lower() in name.lower() or name.lower() in option_text.lower():
                        rect = elem.rectangle()
                        # 点击选项中心
                        click_x = (rect.left + rect.right) // 2
                        click_y = (rect.top + rect.bottom) // 2
                        pyautogui.click(click_x, click_y)
                        if log:
                            log.info(f"[select_dropdown] 已选择选项: {name}")
                        return {"success": True, "option": name}
                except Exception:
                    continue
            break
    except Exception as e:
        if log:
            log.warning(f"[select_dropdown] 查找选项异常: {e}")
    
    return {"success": False, "message": f"选项未找到: {option_text}"}


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
