"""
京麦商品发布自动化 - 表单操作 Actions
覆盖文本输入、下拉选择、商品信息填写、图片上传等行为。
"""
import time
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional

from actions._uia_helpers import (
    click_uia_element,
    find_jingmai_uia_window,
    iter_named_descendants,
    resolve_template_path,
    score_text_match,
)
from actions.registry import ActionRegistry


def _get_locator(locator=None, log=None):
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


def _field_search_margin(field: str) -> tuple[int, int, int, int]:
    if field in {"market_price", "jd_price", "purchase_price"}:
        return (140, 45, 260, 90)
    return (180, 60, 320, 140)


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


def _read_uia_value_for_field(locator, field: str, x: int, y: int) -> Dict[str, Any]:
    result_holder: Dict[str, Any] = {}

    def _search():
        try:
            from infrastructure.uia_inspector import UIAControlInspector
            from actions import _uia_helpers as uia_helpers

            window = uia_helpers.find_jingmai_uia_window(locator=locator)
            if not window:
                result_holder["result"] = {"success": False, "message": "uia window not found", "method": "uia-get-value"}
                return

            screen_x, screen_y = locator.window_to_screen(*locator.adapt_coords(x, y))
            local_x_margin, local_y_margin, expanded_x_margin, expanded_y_margin = _field_search_margin(field)
            local_candidates = []
            expanded_candidates = []
            for edit in UIAControlInspector.find_descendants(
                window,
                control_type_list=["Edit"],
                is_visible=True,
                is_enabled=True,
                limit=80,
            ):
                try:
                    rect = edit.rectangle()
                    if rect.left <= screen_x <= rect.right and rect.top <= screen_y <= rect.bottom:
                        value = edit.get_value() or ""
                        if value:
                            result_holder["result"] = {"success": True, "actual": value, "method": "uia-get-value"}
                            return
                        result_holder["result"] = {"success": False, "message": "uia value empty", "method": "uia-get-value"}
                        return

                    center_x = (rect.left + rect.right) / 2
                    center_y = (rect.top + rect.bottom) / 2
                    distance = abs(center_x - screen_x) + abs(center_y - screen_y)
                    if abs(center_x - screen_x) <= local_x_margin and abs(center_y - screen_y) <= local_y_margin:
                        local_candidates.append((distance, edit))
                    elif abs(center_x - screen_x) <= expanded_x_margin and abs(center_y - screen_y) <= expanded_y_margin:
                        expanded_candidates.append((distance, edit))
                except Exception:
                    continue

            candidates = local_candidates or expanded_candidates
            if candidates:
                _, best = sorted(candidates, key=lambda item: item[0])[0]
                value = best.get_value() or ""
                method = "uia-local-edit" if local_candidates else "uia-expanded-edit"
                if value:
                    result_holder["result"] = {"success": True, "actual": value, "method": method}
                    return
                result_holder["result"] = {"success": False, "message": "uia candidate value empty", "method": method}
                return

            result_holder["result"] = {"success": False, "message": "no matching uia edit", "method": "uia-get-value"}
        except Exception as exc:
            result_holder["result"] = {"success": False, "message": f"uia read failed: {exc}", "method": "uia-get-value"}

    try:
        import threading

        worker = threading.Thread(target=_search, daemon=True)
        worker.start()
        worker.join(timeout=1.5)
        if worker.is_alive():
            return {"success": False, "message": "uia read timeout (1.5s)", "method": "uia-timeout"}
        return result_holder.get("result", {"success": False, "message": "uia read returned no result", "method": "uia-get-value"})
    except Exception as exc:
        return {"success": False, "message": f"uia thread failed: {exc}", "method": "uia-get-value"}


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


def _verify_text_field(locator, field: str, x: int, y: int, expected: Any, prefer_uia: bool = True) -> Dict[str, Any]:
    readers = [_read_clipboard_value_for_field]
    if prefer_uia:
        readers.insert(0, _read_uia_value_for_field)

    failures = []
    for reader in readers:
        if reader is _read_uia_value_for_field:
            read_result = reader(locator, field, x, y)
        else:
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

    uia_timeout = any(item["method"] == "uia-timeout" for item in failures)
    summary = "; ".join(
        f"{item['method']}: {item['reason']}"
        + (f" (expected={item.get('expected')!r}, actual={item.get('actual')!r})" if "expected" in item else "")
        for item in failures
    ) or "no verification method available"
    return {"success": False, "message": summary, "failures": failures, "uia_timeout": uia_timeout}


@ActionRegistry.register("fill_text", "form", "4 层 fallback 填充文本")
def fill_text(
    text: str,
    x: int = None,
    y: int = None,
    name: str = "",
    index: int = 0,
    clear: bool = True,
    locator=None,
    log=None,
) -> Dict[str, Any]:
    locator = _get_locator(locator, log)

    if x is not None and y is not None:
        if not locator.click(x, y, delay=0.3):
            return {"success": False, "message": f"激活输入框失败: ({x}, {y})"}
        time.sleep(0.2)

    if clear:
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
            import pyautogui

            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.1)
            pyautogui.press("delete")

    input_ok = False
    if name:
        try:
            from pywinauto import Desktop
            from infrastructure.locator import WINDOW_KEYWORDS

            desktop = Desktop(backend="uia")
            for window in desktop.windows():
                title = window.window_text()
                if not any(keyword in (title or "").lower() for keyword in WINDOW_KEYWORDS):
                    continue
                edits = window.descendants(control_type="Edit")
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

    if not input_ok:
        try:
            import win32api
            import win32clipboard
            import win32con

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()

            win32api.keybd_event(0x11, 0, 0, 0)
            win32api.keybd_event(0x56, 0, 0, 0)
            win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
            win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.3)
            input_ok = True
        except Exception:
            pass

    if not input_ok:
        try:
            import pyautogui
            import pyperclip

            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
            input_ok = True
        except Exception:
            pass

    if not input_ok:
        try:
            import pyautogui

            pyautogui.typewrite(text, interval=0.05)
            input_ok = True
        except Exception:
            return {"success": False, "message": f"输入失败: {text[:20]}"}

    return {"success": True, "text": text[:20]}


def _build_dropdown_keywords(option_text: str, preferred_keywords: Optional[list[str]] = None) -> list[str]:
    keywords = []
    text = str(option_text or "").strip()
    if text:
        keywords.append(text)
        for token in text.replace("/", " ").replace(">", " ").replace("-", " ").split():
            token = token.strip()
            if token and token not in keywords:
                keywords.append(token)
    for keyword in preferred_keywords or []:
        if keyword and keyword not in keywords:
            keywords.append(keyword)
    return keywords[:8]


def _click_dropdown_template(template_name: str, locator=None, log=None, confidence: float = 0.88) -> Dict[str, Any]:
    template_path = resolve_template_path("templates", template_name)
    if not template_path:
        return {"success": False, "message": "template missing", "template": template_name}

    try:
        from actions.verification import find_element_by_image
        import pyautogui

        result = find_element_by_image(template_path=template_path, confidence=confidence, locator=locator, log=log)
        if not result.get("success"):
            return {"success": False, "message": result.get("message", "match failed"), "template": template_name}
        pyautogui.click(result["x"], result["y"])
        time.sleep(0.5)
        return {
            "success": True,
            "template": template_name,
            "template_path": template_path,
            "match_confidence": confidence,
            "position": {"x": result["x"], "y": result["y"]},
        }
    except Exception:
        return {"success": False, "message": "template click failed", "template": template_name}


def _select_dropdown_option(
    option_text: str,
    x: int,
    y: int,
    locator=None,
    log=None,
    preferred_keywords: Optional[list[str]] = None,
    top_range: Optional[tuple[int, int]] = None,
    vision_template: str = "",
) -> Dict[str, Any]:
    if not locator.click(x, y, delay=0.5):
        return {"success": False, "message": f"点击下拉框失败: ({x}, {y})"}
    time.sleep(0.8)

    window = find_jingmai_uia_window(locator=locator, log=log)
    keywords = _build_dropdown_keywords(option_text, preferred_keywords)
    if window:
        if not top_range:
            screen_y = y
            try:
                screen_y = locator.window_to_screen(*locator.adapt_coords(x, y))[1]
            except Exception:
                pass
            top_range = (max(120, screen_y - 80), screen_y + 320)

        candidates = []
        for candidate in iter_named_descendants(window, top_range=top_range, max_name_length=120, limit=240):
            score = score_text_match(candidate["name"], option_text, keywords)
            if candidate["control_type"] in {"ListItem", "Text", "Button"}:
                score += 2
            if preferred_keywords and any(keyword.lower() in candidate["name"].lower() for keyword in preferred_keywords):
                score += 2
            if score > 0:
                rect = candidate["rect"]
                candidates.append((score, rect.top, len(candidate["name"]), candidate))

        if candidates:
            _, _, _, best = sorted(candidates, key=lambda item: (-item[0], item[1], item[2]))[0]
            if click_uia_element(best["element"], log=log):
                return {"success": True, "option": best["name"], "method": "uia-local"}

    if vision_template:
        vision = _click_dropdown_template(vision_template, locator=locator, log=log)
        if vision.get("success"):
            return {"success": True, "option": option_text, "method": "vision", "vision_fallback": vision}

    try:
        import pyautogui

        if str(option_text).upper().startswith("IP"):
            pyautogui.typewrite(str(option_text), interval=0.03)
            time.sleep(0.2)
        else:
            pyautogui.press("down")
            time.sleep(0.2)
        pyautogui.press("enter")
        time.sleep(0.5)
        return {"success": True, "option": option_text, "method": "keyboard"}
    except Exception as exc:
        return {"success": False, "message": f"选项未找到: {option_text} ({exc})"}


def _collect_attribute_values(product: Dict[str, Any]) -> Dict[str, Any]:
    attributes = dict(product.get("attributes") or {})
    aliases = {
        "protection_level": ["protection_level", "防护等级", "ip_rating"],
        "material": ["material", "材质"],
    }
    for field, field_aliases in aliases.items():
        for alias in field_aliases:
            value = product.get(alias)
            if value not in (None, ""):
                attributes.setdefault(field, value)
    return attributes


def _fill_supported_attributes(product: Dict[str, Any], locator=None, log=None) -> list[Dict[str, Any]]:
    from config.jingmai_coords import PRODUCT_INFO_PAGE

    attribute_values = _collect_attribute_values(product)
    specs = [
        {
            "field": "protection_level",
            "coords": PRODUCT_INFO_PAGE.get("protection_level"),
            "value": attribute_values.get("protection_level"),
            "preferred_keywords": ["IP"],
            "vision_template": "protection_level_option.png",
        },
        {
            "field": "material",
            "coords": PRODUCT_INFO_PAGE.get("material"),
            "value": attribute_values.get("material"),
            "preferred_keywords": ["材质"],
            "vision_template": "material_option.png",
        },
    ]

    results = []
    for spec in specs:
        if spec["value"] in (None, "") or not spec["coords"]:
            continue
        result = _select_dropdown_option(
            str(spec["value"]),
            spec["coords"][0],
            spec["coords"][1],
            locator=locator,
            log=log,
            preferred_keywords=spec["preferred_keywords"],
            vision_template=spec["vision_template"],
        )
        results.append(
            {
                "field": spec["field"],
                "method": result.get("method", "select_dropdown"),
                "value": str(spec["value"]),
                "write_success": result["success"],
                "verify_success": result["success"],
                "success": result["success"],
                **({"error": result.get("message", "")} if not result["success"] else {}),
            }
        )
        time.sleep(0.5)
    return results


@ActionRegistry.register("select_dropdown", "form", "ComboBox 下拉选择")
def select_dropdown(x: int, y: int, option_text: str, locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    return _select_dropdown_option(option_text, x, y, locator=locator, log=log)


@ActionRegistry.register("paste_and_search", "form", "粘贴文本并搜索")
def paste_and_search(text: str, x: int, y: int, enter: bool = True, locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    locator.click(x, y, delay=0.3)
    result = fill_text(text, x=x, y=y, clear=True, locator=locator, log=log)
    if not result["success"]:
        return result

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
    locator = _get_locator(locator, log)
    from config.jingmai_coords import PRODUCT_INFO_PAGE

    results = []
    text_fields = {
        "title": PRODUCT_INFO_PAGE.get("title_input"),
        "model": PRODUCT_INFO_PAGE.get("model_input"),
        "sku": PRODUCT_INFO_PAGE.get("sku_input"),
        "market_price": PRODUCT_INFO_PAGE.get("market_price"),
        "jd_price": PRODUCT_INFO_PAGE.get("jd_price"),
        "purchase_price": PRODUCT_INFO_PAGE.get("purchase_price"),
    }

    prefer_uia_read = True
    for field, coords in text_fields.items():
        value = product.get(field)
        if value in (None, "") or not coords:
            continue
        write_result = fill_text(str(value), x=coords[0], y=coords[1], locator=locator, log=log)
        field_result = {
            "field": field,
            "method": "fill_text",
            "write_success": write_result["success"],
            "verify_success": False,
            "success": write_result["success"],
            "expected": str(value),
        }
        if write_result["success"]:
            verify = _verify_text_field(locator, field, coords[0], coords[1], value, prefer_uia=prefer_uia_read)
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
                if verify.get("uia_timeout"):
                    prefer_uia_read = False
        else:
            field_result["verify_error"] = write_result.get("message", "write failed")
        results.append(field_result)
        time.sleep(0.3)

    brand = product.get("brand") or product.get("品牌")
    if brand:
        brand_coords = PRODUCT_INFO_PAGE.get("brand_select")
        if brand_coords:
            brand_result = _select_dropdown_option(
                brand,
                brand_coords[0],
                brand_coords[1],
                locator=locator,
                log=log,
                preferred_keywords=["品牌"],
                vision_template="brand_option.png",
            )
            results.append(
                {
                    "field": "brand",
                    "method": brand_result.get("method", "select_dropdown"),
                    "value": brand,
                    "write_success": brand_result["success"],
                    "verify_success": brand_result["success"],
                    "success": brand_result["success"],
                }
            )
            time.sleep(0.5)

    results.extend(_fill_supported_attributes(product, locator=locator, log=log))

    success_count = sum(1 for item in results if item["success"])
    total = len(results)
    overall_success = total > 0 and success_count == total
    failed_fields = [item.get("field", "") for item in results if not item.get("success")]
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


@ActionRegistry.register("click_element", "form", "点击指定元素")
def click_element(x: int = None, y: int = None, name: str = "", locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)

    if x is not None and y is not None:
        return {"success": locator.click(x, y, delay=0.5), "method": "coordinate"}

    if name:
        window = find_jingmai_uia_window(locator=locator, log=log)
        if window:
            for control_type in ["Button", "Hyperlink"]:
                for candidate in iter_named_descendants(window, control_types=[control_type], limit=120):
                    if name in candidate["name"] and click_uia_element(candidate["element"], log=log):
                        return {"success": True, "method": f"uia_{control_type.lower()}", "name": name}

    return {"success": False, "message": f"元素未找到: {name}"}


@ActionRegistry.register("fix_field", "form", "修正表单字段")
def fix_field(x: int, y: int, correct_value: str, locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    locator.click(x, y, delay=0.3)
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
    return fill_text(correct_value, x=x, y=y, clear=False, locator=locator, log=log)


@ActionRegistry.register("upload_image", "form", "上传商品图片")
def upload_image(image_path: str, x: int = None, y: int = None, locator=None, log=None) -> Dict[str, Any]:
    import io
    import os

    if not os.path.exists(image_path):
        return {"success": False, "message": f"图片文件不存在: {image_path}"}

    locator = _get_locator(locator, log)
    if x is not None and y is not None:
        locator.click(x, y, delay=0.5)

    try:
        from PIL import Image
        import win32api
        import win32clipboard
        import win32con

        img = Image.open(image_path)
        output = io.BytesIO()
        img.save(output, "BMP")
        data = output.getvalue()[14:]

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()

        win32api.keybd_event(0x11, 0, 0, 0)
        win32api.keybd_event(0x56, 0, 0, 0)
        win32api.keybd_event(0x56, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)
        return {"success": True, "method": "clipboard_paste", "image": image_path}
    except Exception:
        return {"success": False, "message": "图片上传失败，尝试粘贴方式未成功"}


@ActionRegistry.register("wait_and_click", "form", "等待元素出现后点击")
def wait_and_click(
    name: str = "",
    x: int = None,
    y: int = None,
    timeout: float = 10.0,
    interval: float = 1.0,
    locator=None,
    log=None,
) -> Dict[str, Any]:
    import time as _time

    locator = _get_locator(locator, log)
    start = _time.time()

    while _time.time() - start < timeout:
        if x is not None and y is not None:
            locator.click(x, y, delay=0.3)
            return {"success": True, "method": "coordinate"}

        if name:
            window = find_jingmai_uia_window(locator=locator, log=log)
            if window:
                for candidate in iter_named_descendants(window, limit=180):
                    if name in candidate["name"] and click_uia_element(candidate["element"], log=log):
                        return {"success": True, "method": "uia", "name": name}

        _time.sleep(interval)

    return {"success": False, "message": f"等待超时: {name or (x, y)}"}
