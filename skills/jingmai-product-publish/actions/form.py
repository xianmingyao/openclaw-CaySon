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


# ── Session1 Helper Pipe Client ──────────────────────────────────────────────
# 优先使用 Session1 Helper 解决 Session 0 无法操作京麦窗口的问题
_pipe_client = None


def _get_pipe_client():
    """获取或创建 Pipe Client（Singleton）"""
    global _pipe_client
    if _pipe_client is None:
        try:
            from pipe_client import create_client

            _pipe_client = create_client()
        except Exception:
            _pipe_client = None
    return _pipe_client


def _session1_click(x: int, y: int, delay: float = 0.3) -> bool:
    """通过 Session1 Helper 点击坐标"""
    client = _get_pipe_client()
    if client:
        try:
            result = client.click(x, y, delay=delay)
            return result.get("success", False)
        except Exception:
            pass
    return False


def _release_mouse_buttons():
    try:
        import win32api
        import win32con

        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    except Exception:
        pass


def _session1_paste(text: str) -> bool:
    """通过 Session1 Helper 剪贴板粘贴"""
    client = _get_pipe_client()
    if client:
        try:
            result = client.paste(text)
            return result.get("success", False)
        except Exception:
            pass
    return False


def _session1_hotkey(*keys) -> bool:
    """通过 Session1 Helper 发送快捷键"""
    client = _get_pipe_client()
    if client:
        try:
            result = client.hotkey(*keys)
            return result.get("success", False)
        except Exception:
            pass
    return False


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
    """
    填充文本字段。
    优先使用 Session1 Helper（Pipe）进行操作，解决 Session 0 无法操作京麦的问题。
    """
    # 优先用 Session1 Helper 点击
    if x is not None and y is not None:
        # 先用 Helper 点击
        if _session1_click(x, y, delay=0.5):
            time.sleep(0.3)
        else:
            # Fallback: 用 locator
            locator = _get_locator(locator, log)
            if not locator.click(x, y, delay=0.3):
                return {"success": False, "message": f"激活输入框失败: ({x}, {y})"}
            time.sleep(0.2)

    # 清空现有内容
    if clear:
        # 优先用 Helper 的 Ctrl+A + Delete
        if not _session1_hotkey("ctrl", "a"):
            try:
                import pyautogui

                pyautogui.hotkey("ctrl", "a")
                time.sleep(0.08)
                pyautogui.press("delete")
                time.sleep(0.08)
            except Exception:
                pass
        else:
            time.sleep(0.1)
            _session1_hotkey("ctrl", "a")  # Ctrl+A
            time.sleep(0.05)
            _session1_hotkey("delete")  # Delete
            time.sleep(0.1)

    # 尝试用 Session1 Helper 粘贴（最可靠的中文输入）
    input_ok = False

    if _session1_paste(text):
        input_ok = True

    # Fallback: UIA set_edit_text
    if not input_ok and name:
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

    # Fallback: pyautogui 剪贴板
    if not input_ok:
        try:
            import pyautogui

            if _set_clipboard_text(text):
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.25)
                input_ok = True
        except Exception:
            pass

    # 最后的 Fallback: typewrite
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
        "socket_config": ["socket_config", "孔型配置", "孔位配置", "插孔配置"],
        "rated_voltage": ["rated_voltage", "额定电压", "voltage"],
        "cable_length": ["cable_length", "电缆长度", "线长", "导线长度"],
    }
    for field, field_aliases in aliases.items():
        for alias in field_aliases:
            value = product.get(alias)
            if value not in (None, ""):
                attributes.setdefault(field, value)
    return attributes


def _find_labeled_dropdown_center(
    label_keywords: list[str],
    locator=None,
    log=None,
    top_range: tuple[int, int] | None = None,
) -> Optional[tuple[int, int]]:
    window = find_jingmai_uia_window(locator=locator, log=log)
    if not window:
        return None

    top_range = top_range or (520, 1100)
    labels = []
    controls = []
    for candidate in iter_named_descendants(window, control_types=["Text", "Button", "ComboBox", "Edit"], limit=400):
        rect = candidate["rect"]
        if not (top_range[0] <= rect.top <= top_range[1]):
            continue
        controls.append(candidate)
        name = (candidate["name"] or "").strip()
        if name and any(keyword in name for keyword in label_keywords):
            labels.append(candidate)

    if not labels:
        return None

    best_match = None
    for label in labels:
        label_rect = label["rect"]
        label_center_y = (label_rect.top + label_rect.bottom) / 2
        for candidate in controls:
            if candidate is label:
                continue
            if candidate["control_type"] not in {"ComboBox", "Edit", "Button"}:
                continue
            rect = candidate["rect"]
            candidate_center_y = (rect.top + rect.bottom) / 2
            dx = rect.left - label_rect.right
            dy = abs(candidate_center_y - label_center_y)
            if dx < -40 or dx > 900 or dy > 90:
                continue
            score = (0 if candidate["control_type"] == "ComboBox" else 1, dy, max(dx, 0), rect.left)
            if best_match is None or score < best_match[0]:
                best_match = (score, candidate)

    if not best_match:
        return None

    rect = best_match[1]["rect"]
    return ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)


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
        {
            "field": "socket_config",
            "coords": PRODUCT_INFO_PAGE.get("socket_config"),
            "value": attribute_values.get("socket_config"),
            "preferred_keywords": ["孔型", "插孔"],
            "vision_template": "",
            "label_keywords": ["孔型配置", "孔位配置", "插孔配置"],
        },
        {
            "field": "rated_voltage",
            "coords": PRODUCT_INFO_PAGE.get("rated_voltage"),
            "value": attribute_values.get("rated_voltage"),
            "preferred_keywords": ["额定", "电压"],
            "vision_template": "",
            "label_keywords": ["额定电压", "电压"],
        },
        {
            "field": "cable_length",
            "coords": PRODUCT_INFO_PAGE.get("cable_length"),
            "value": attribute_values.get("cable_length"),
            "preferred_keywords": ["长度", "线长"],
            "vision_template": "",
            "label_keywords": ["电缆长度", "导线长度", "线长"],
        },
    ]

    results = []
    for spec in specs:
        if spec["value"] in (None, ""):
            continue
        coords = spec["coords"]
        if not coords:
            coords = _find_labeled_dropdown_center(
                spec.get("label_keywords") or spec["preferred_keywords"],
                locator=locator,
                log=log,
            )
        if not coords:
            results.append(
                {
                    "field": spec["field"],
                    "method": "dynamic-label-search",
                    "value": str(spec["value"]),
                    "write_success": False,
                    "verify_success": False,
                    "success": False,
                    "error": f"{spec['field']} dropdown anchor not found",
                }
            )
            continue
        result = _select_dropdown_option(
            str(spec["value"]),
            coords[0],
            coords[1],
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


def _set_clipboard_text(text: str) -> bool:
    try:
        import pyperclip

        pyperclip.copy(text)
        return True
    except Exception:
        pass

    try:
        import win32clipboard

        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            return True
        finally:
            win32clipboard.CloseClipboard()
    except Exception:
        return False


def _write_active_text(text: Any, clear: bool = True) -> Dict[str, Any]:
    text_value = str(text)

    # 优先使用 Session1 Helper（解决跨 Session 0/1 问题）
    if _session1_paste(text_value):
        time.sleep(0.25)
        return {"success": True, "method": "session1-paste"}

    # Fallback: pyautogui（仅当 Helper 不可用时）
    try:
        import pyautogui
    except Exception as exc:
        return {"success": False, "message": f"pyautogui unavailable: {exc}"}

    if clear:
        # 优先用 Helper 的 Ctrl+A + Delete
        if not _session1_hotkey("ctrl", "a"):
            pyautogui.hotkey("ctrl", "a")
        time.sleep(0.08)
        if not _session1_hotkey("delete"):
            pyautogui.press("backspace")
        time.sleep(0.08)

    if _set_clipboard_text(text_value):
        # 优先用 Helper 的 Ctrl+V
        if not _session1_hotkey("ctrl", "v"):
            pyautogui.hotkey("ctrl", "v")
        time.sleep(0.25)
        return {"success": True, "method": "clipboard-paste"}

    try:
        pyautogui.typewrite(text_value, interval=0.03)
        return {"success": True, "method": "typewrite"}
    except Exception as exc:
        return {"success": False, "message": f"active write failed: {exc}"}


def _read_active_text() -> Dict[str, Any]:
    # 优先使用 Session1 Helper（解决跨 Session 0/1 问题）
    if _session1_hotkey("ctrl", "a") and _session1_hotkey("ctrl", "c"):
        time.sleep(0.12)
    else:
        # Fallback: pyautogui
        try:
            import pyautogui

            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.05)
            pyautogui.hotkey("ctrl", "c")
            time.sleep(0.12)
        except Exception as exc:
            return {"success": False, "message": f"active read failed: {exc}"}

    actual = _read_clipboard_text()
    if not _normalize_text(actual):
        return {"success": False, "message": "active field clipboard empty"}
    return {"success": True, "actual": actual, "method": "active-clipboard"}


def _verify_active_text(field: str, expected: Any) -> Dict[str, Any]:
    read_result = _read_active_text()
    if not read_result.get("success"):
        return {"success": False, "message": read_result.get("message", "active read failed")}

    comparison = _compare_field_value(field, expected, read_result.get("actual", ""))
    if comparison["success"]:
        return {
            "success": True,
            "actual": comparison["actual"],
            "expected": comparison["expected"],
            "method": read_result.get("method", "active-clipboard"),
            "compare_mode": comparison["compare_mode"],
        }
    return {
        "success": False,
        "message": "active value mismatch",
        "actual": comparison["actual"],
        "expected": comparison["expected"],
        "method": read_result.get("method", "active-clipboard"),
        "compare_mode": comparison["compare_mode"],
    }


def _find_edit_elements(locator=None, log=None) -> list[tuple[Any, str, Any]]:
    window = find_jingmai_uia_window(locator=locator, log=log)
    if not window:
        return []

    edits = []
    try:
        for element in window.descendants():
            try:
                if element.friendly_class_name() != "Edit":
                    continue
                rect = element.rectangle()
                edits.append((element, element.window_text() or "", rect))
            except Exception:
                continue
    except Exception:
        return []
    return edits


def _find_named_edit_center(keyword: str, locator=None, log=None, top_range: tuple[int, int] | None = None) -> Optional[tuple[int, int]]:
    for _, name, rect in _find_edit_elements(locator=locator, log=log):
        if keyword not in name:
            continue
        if top_range and not (top_range[0] <= rect.top <= top_range[1]):
            continue
        return ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
    return None


def _find_named_edit_element(
    keyword: str,
    locator=None,
    log=None,
    top_range: tuple[int, int] | None = None,
    left_range: tuple[int, int] | None = None,
):
    for element, name, rect in _find_edit_elements(locator=locator, log=log):
        if keyword not in name:
            continue
        if top_range and not (top_range[0] <= rect.top <= top_range[1]):
            continue
        if left_range and not (left_range[0] <= rect.left <= left_range[1]):
            continue
        return element, name, rect
    return None


def _find_named_control(
    keyword: str,
    control_types: list[str],
    locator=None,
    log=None,
    top_range: tuple[int, int] | None = None,
    left_range: tuple[int, int] | None = None,
):
    window = find_jingmai_uia_window(locator=locator, log=log)
    if not window:
        return None
    for candidate in iter_named_descendants(window, control_types=control_types, limit=320):
        name = candidate["name"] or ""
        rect = candidate["rect"]
        if keyword not in name:
            continue
        if top_range and not (top_range[0] <= rect.top <= top_range[1]):
            continue
        if left_range and not (left_range[0] <= rect.left <= left_range[1]):
            continue
        return candidate["element"], name, rect
    return None


def _visible_text_contains(
    expected: str,
    locator=None,
    log=None,
    top_range: tuple[int, int] | None = None,
    left_range: tuple[int, int] | None = None,
) -> bool:
    window = find_jingmai_uia_window(locator=locator, log=log)
    if not window:
        return False
    for candidate in iter_named_descendants(window, control_types=["Text", "Button", "ComboBox", "Edit"], limit=400):
        name = (candidate["name"] or "").strip()
        rect = candidate["rect"]
        if not name:
            continue
        if top_range and not (top_range[0] <= rect.top <= top_range[1]):
            continue
        if left_range and not (left_range[0] <= rect.left <= left_range[1]):
            continue
        if expected in name:
            return True
    return False


def _page_text_contains(expected: str, x: int = 900, y: int = 520) -> bool:
    try:
        import pyautogui

        pyautogui.click(x, y)
        time.sleep(0.15)
    except Exception:
        return False

    read_result = _read_active_text()
    if not read_result.get("success"):
        return False
    actual = str(read_result.get("actual", ""))
    return expected in actual


def _read_uia_edit_value(element) -> str:
    try:
        value = element.get_value()
        if value:
            return str(value)
    except Exception:
        pass
    try:
        value = element.legacy_properties().get("Value", "")
        if value:
            return str(value)
    except Exception:
        pass
    return ""


def _focus_uia_edit(element, locator=None) -> bool:
    if click_uia_element(element, log=None):
        return True
    if locator is None:
        return False
    try:
        rect = element.rectangle()
    except Exception:
        return False
    center_x = (rect.left + rect.right) // 2
    center_y = (rect.top + rect.bottom) // 2
    return locator.click(center_x, center_y, delay=0.25)


def _verify_uia_edit_value(field: str, expected: Any, element) -> Dict[str, Any]:
    actual = _read_uia_edit_value(element)
    if not actual:
        return {"success": False, "message": "uia edit value empty", "method": "uia-edit-value"}
    comparison = _compare_field_value(field, expected, actual)
    if comparison["success"]:
        return {
            "success": True,
            "actual": comparison["actual"],
            "expected": comparison["expected"],
            "method": "uia-edit-value",
            "compare_mode": comparison["compare_mode"],
        }
    return {
        "success": False,
        "message": "uia edit value mismatch",
        "actual": comparison["actual"],
        "expected": comparison["expected"],
        "method": "uia-edit-value",
        "compare_mode": comparison["compare_mode"],
    }


def _fill_named_edit_field_v2(
    field: str,
    keyword: str,
    value: Any,
    locator=None,
    log=None,
    top_range: tuple[int, int] | None = None,
    left_range: tuple[int, int] | None = None,
    fallback_coords: tuple[int, int] | None = None,
) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    target = _find_named_edit_element(keyword, locator=locator, log=log, top_range=top_range, left_range=left_range)
    element = target[0] if target else None
    
    # 优先使用 UIA set_edit_text（跨 Session 有效）
    if element:
        try:
            element.set_edit_text(str(value))
            time.sleep(0.2)
            verify = _verify_uia_edit_value(field, value, element)
            return {
                "field": field,
                "method": "uia-set-edit-text",
                "write_success": True,
                "verify_success": verify.get("success", False),
                "success": verify.get("success", False),
                "expected": str(value),
                "actual": verify.get("actual", ""),
                "verification_method": verify.get("method", ""),
                "compare_mode": verify.get("compare_mode", ""),
                "expected_normalized": verify.get("expected", str(value)),
            }
        except Exception:
            pass  # Fall through to legacy methods

    # Legacy: 尝试 focus + _write_active_text
    if element:
        if not _focus_uia_edit(element, locator=locator):
            return {"field": field, "success": False, "message": f"{field} field focus failed"}
    elif fallback_coords:
        if not locator.click(fallback_coords[0], fallback_coords[1], delay=0.3):
            return {"field": field, "success": False, "message": f"{field} field focus failed"}
    else:
        return {"field": field, "success": False, "message": f"{field} field not found"}

    write_result = _write_active_text(value, clear=True)
    if not write_result.get("success"):
        return {"field": field, **write_result}

    verify = _verify_active_text(field, value)
    if not verify.get("success") and element:
        verify = _verify_uia_edit_value(field, value, element)

    payload = {
        "field": field,
        "method": write_result.get("method", "active-write"),
        "write_success": write_result.get("success", False),
        "verify_success": verify.get("success", False),
        "success": verify.get("success", False),
        "expected": str(value),
        "actual": verify.get("actual", ""),
        "verification_method": verify.get("method", ""),
        "compare_mode": verify.get("compare_mode", ""),
        "expected_normalized": verify.get("expected", str(value)),
    }
    if not verify.get("success"):
        payload["verify_error"] = verify.get("message", f"{field} verify failed")
    return payload


def _fill_title_field(title: str, locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    center = _find_named_edit_center("请输入商品标题", locator=locator, log=log, top_range=(320, 520))
    if not center:
        center = (1443, 394)
    if not locator.click(center[0], center[1], delay=0.3):
        return {"success": False, "message": "title field focus failed"}

    write_result = _write_active_text(title, clear=True)
    if not write_result.get("success"):
        return write_result

    verify = _verify_active_text("title", title)
    payload = {
        "field": "title",
        "method": write_result.get("method", "active-write"),
        "write_success": True,
        "verify_success": verify.get("success", False),
        "success": verify.get("success", False),
        "expected": str(title),
        "actual": verify.get("actual", ""),
        "verification_method": verify.get("method", ""),
        "compare_mode": verify.get("compare_mode", ""),
        "expected_normalized": verify.get("expected", str(title)),
    }
    if not verify.get("success"):
        payload["verify_error"] = verify.get("message", "title verify failed")
    return payload


def _fill_title_field_v2(title: str, locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    _scroll_publish_page_to_top()
    target = _find_named_edit_element("商品标题", locator=locator, log=log, top_range=(240, 520), left_range=(700, 900))
    if not target:
        target = _find_named_edit_element("请输入商品标题", locator=locator, log=log, top_range=(240, 520), left_range=(700, 900))
    element = target[0] if target else None
    if element:
        if not _focus_uia_edit(element, locator=locator):
            return {"success": False, "message": "title field focus failed"}
    else:
        if not locator.click(1434, 318, delay=0.3):
            return {"success": False, "message": "title field focus failed"}

    write_result = _write_active_text(title, clear=True)
    if not write_result.get("success"):
        return write_result

    verify = _verify_uia_edit_value("title", title, element) if element else _verify_active_text("title", title)
    payload = {
        "field": "title",
        "method": write_result.get("method", "active-write"),
        "write_success": True,
        "verify_success": verify.get("success", False),
        "success": verify.get("success", False),
        "expected": str(title),
        "actual": verify.get("actual", ""),
        "verification_method": verify.get("method", ""),
        "compare_mode": verify.get("compare_mode", ""),
        "expected_normalized": verify.get("expected", str(title)),
    }
    if not verify.get("success"):
        payload["verify_error"] = verify.get("message", "title verify failed")
    return payload


def _fill_title_field_v3(title: str, locator=None, log=None) -> Dict[str, Any]:
    _scroll_publish_page_to_top()
    return _fill_named_edit_field_v2(
        "title",
        "请输入商品标题",
        title,
        locator=locator,
        log=log,
        top_range=(360, 470),
        left_range=(700, 900),
        fallback_coords=(1458, 434),
    )


def _fill_model_field_v2(model: str, locator=None, log=None) -> Dict[str, Any]:
    _scroll_publish_page_to_top()
    return _fill_named_edit_field_v2(
        "model",
        "型号",
        model,
        locator=locator,
        log=log,
        top_range=(520, 590),
        left_range=(980, 1100),
        fallback_coords=(1208, 552),
    )


def _fill_brand_field_v2(brand: str, locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    _scroll_publish_page_to_top()
    if _page_text_contains(brand, x=900, y=520):
        return {
            "field": "brand",
            "method": "page-text",
            "value": brand,
            "write_success": True,
            "verify_success": True,
            "success": True,
        }
    if _visible_text_contains(brand, locator=locator, log=log, top_range=(500, 590), left_range=(620, 1040)):
        return {
            "field": "brand",
            "method": "uia-visible-text",
            "value": brand,
            "write_success": True,
            "verify_success": True,
            "success": True,
        }

    target = _find_named_control("品牌", ["ComboBox"], locator=locator, log=log, top_range=(500, 590), left_range=(620, 700))
    if not target:
        return {
            "field": "brand",
            "method": "uia-combobox",
            "value": brand,
            "write_success": False,
            "verify_success": False,
            "success": False,
            "error": "brand combobox not found",
        }

    _, _, rect = target
    result = _select_dropdown_option(
        brand,
        (rect.left + rect.right) // 2,
        (rect.top + rect.bottom) // 2,
        locator=locator,
        log=log,
        preferred_keywords=["品牌"],
        top_range=(500, 760),
        vision_template="brand_option.png",
    )
    success = result.get("success", False) and _visible_text_contains(
        brand,
        locator=locator,
        log=log,
        top_range=(500, 590),
        left_range=(620, 1040),
    )
    payload = {
        "field": "brand",
        "method": result.get("method", "select_dropdown"),
        "value": brand,
        "write_success": result.get("success", False),
        "verify_success": success,
        "success": success,
    }
    if not success:
        payload["error"] = result.get("message", "brand verify failed")
    return payload


def _fill_procurement_erp_field(product: Dict[str, Any], locator=None, log=None) -> Optional[Dict[str, Any]]:
    locator = _get_locator(locator, log)
    _scroll_publish_page_to_top()

    procurement_value = (
        product.get("purchase_erp")
        or product.get("procurement_erp")
        or product.get("buyer_erp")
        or product.get("采购员ERP")
    )

    sales_target = _find_named_edit_element("ERP", locator=locator, log=log, top_range=(500, 760), left_range=(500, 900))
    if not procurement_value and sales_target:
        procurement_value = _read_uia_edit_value(sales_target[0]).strip()

    if not procurement_value:
        return None

    target = _find_named_edit_element("ERP", locator=locator, log=log, top_range=(500, 760), left_range=(1400, 1550))
    if not target:
        return {
            "field": "procurement_erp",
            "success": False,
            "write_success": False,
            "verify_success": False,
            "verify_error": "procurement ERP field not found",
        }

    element = target[0]
    if not _focus_uia_edit(element, locator=locator):
        return {
            "field": "procurement_erp",
            "success": False,
            "write_success": False,
            "verify_success": False,
            "verify_error": "procurement ERP field focus failed",
        }

    try:
        element.set_edit_text(str(procurement_value))
        method = "uia-set-edit-text"
        write_success = True
    except Exception:
        write_result = _write_active_text(str(procurement_value), clear=True)
        method = write_result.get("method", "active-write")
        write_success = write_result.get("success", False)

    if not write_success:
        return {
            "field": "procurement_erp",
            "success": False,
            "write_success": False,
            "verify_success": False,
            "verify_error": "procurement ERP write failed",
        }

    verify = _verify_uia_edit_value("procurement_erp", procurement_value, element)
    payload = {
        "field": "procurement_erp",
        "method": method,
        "write_success": True,
        "verify_success": verify.get("success", False),
        "success": verify.get("success", False),
        "expected": str(procurement_value),
        "actual": verify.get("actual", ""),
        "verification_method": verify.get("method", ""),
        "compare_mode": verify.get("compare_mode", ""),
        "expected_normalized": verify.get("expected", str(procurement_value)),
    }
    if not verify.get("success"):
        payload["verify_error"] = verify.get("message", "procurement ERP verify failed")
    return payload


def _scroll_publish_page_to_top():
    import pyautogui

    pyautogui.moveTo(1800, 1000)
    for _ in range(12):
        pyautogui.scroll(700)
        time.sleep(0.05)


def _debug_log(log, message: str):
    if log:
        try:
            log.debug(message)
        except Exception:
            pass


def _scroll_to_sku_section(log=None):
    import pyautogui

    _debug_log(log, "[fill_product_info] scroll to sku section: reset to top")
    _scroll_publish_page_to_top()
    pyautogui.moveTo(1800, 1000)
    for index in range(2):
        pyautogui.scroll(-550)
        _debug_log(log, f"[fill_product_info] scroll to sku section: step={index + 1} delta=-550")
        time.sleep(0.25)


def _scroll_price_fields_into_view(log=None):
    import pyautogui

    pyautogui.moveTo(1800, 1000)
    for index in range(3):
        pyautogui.scroll(-420)
        _debug_log(log, f"[fill_product_info] scroll to price fields: step={index + 1} delta=-420")
        time.sleep(0.25)


def _collect_price_area_anchors(locator=None, log=None) -> list[str]:
    anchors = []
    for label in ("市场价", "京东价", "SKU编码", "销售属性"):
        if _visible_text_contains(label, locator=locator, log=log, top_range=(480, 980)):
            anchors.append(label)
    return anchors


def _seek_price_area(locator=None, log=None, max_scrolls: int = 6) -> dict:
    import pyautogui

    locator = _get_locator(locator, log)
    _scroll_to_sku_section(log=log)
    pyautogui.moveTo(1800, 1000)

    for attempt in range(max_scrolls + 1):
        anchors = _collect_price_area_anchors(locator=locator, log=log)
        _debug_log(log, f"[fill_product_info] price anchors attempt={attempt + 1} found={anchors}")
        if "市场价" in anchors or "京东价" in anchors:
            return {"success": True, "anchors": anchors, "attempt": attempt + 1}
        if attempt < max_scrolls:
            pyautogui.scroll(-380)
            _debug_log(log, f"[fill_product_info] seek price anchors scroll step={attempt + 1} delta=-380")
            time.sleep(0.25)

    return {"success": False, "anchors": anchors, "attempt": max_scrolls + 1}


def _locate_template_in_window(
    template_name: str,
    *,
    locator=None,
    log=None,
    cache_name: str = "template_probe.png",
    confidences: tuple[float, ...] = (0.95, 0.92, 0.88, 0.84, 0.80),
) -> Optional[Dict[str, Any]]:
    locator = _get_locator(locator, log)
    template_path = resolve_template_path("templates", template_name)
    if not template_path:
        _debug_log(log, f"[vision] template missing: {template_name}")
        return None

    try:
        from pathlib import Path

        from PIL import Image
        import pyautogui

        probe_path = locator.take_screenshot(
            save_path=str(Path("resources") / "screenshots" / "cache" / cache_name)
        )
        if not probe_path:
            _debug_log(log, f"[vision] screenshot failed for template {template_name}")
            return None

        haystack = Image.open(probe_path)
        needle = Image.open(template_path)
        for confidence in confidences:
            try:
                box = pyautogui.locate(needle, haystack, confidence=confidence)
            except Exception:
                box = None
            if not box:
                continue
            return {
                "template": template_name,
                "confidence": confidence,
                "box": (int(box.left), int(box.top), int(box.width), int(box.height)),
                "center": (int(box.left + box.width / 2), int(box.top + box.height / 2)),
                "screenshot_path": probe_path,
            }
    except Exception as exc:
        _debug_log(log, f"[vision] template locate failed {template_name}: {exc}")
    return None


def _collect_price_area_template_state(locator=None, log=None) -> Dict[str, Any]:
    anchors = _collect_price_area_anchors(locator=locator, log=log)
    title_match = _locate_template_in_window(
        "product_title_label.png",
        locator=locator,
        log=log,
        cache_name="price_state_title.png",
        confidences=(0.95, 0.92, 0.88, 0.84),
    )
    market_match = _locate_template_in_window(
        "market_price_label.png",
        locator=locator,
        log=log,
        cache_name="price_probe_市场价.png",
        confidences=(0.95, 0.92, 0.88, 0.84, 0.80),
    )
    jd_match = _locate_template_in_window(
        "jd_price_label.png",
        locator=locator,
        log=log,
        cache_name="price_probe_京东价.png",
        confidences=(0.95, 0.92, 0.88, 0.84, 0.80),
    )
    sku_batch_markers = [
        "鎵归噺瀵煎叆",
        "鎵归噺璁剧疆",
        "榛樿鍏ㄩ儴SKU",
        "SKU灞炴€?",
    ]
    visible_batch_markers = [
        marker
        for marker in sku_batch_markers
        if _visible_text_contains(marker, locator=locator, log=log, top_range=(1120, 1380))
    ]
    state = {
        "text_anchors": anchors,
        "title_visible": bool(title_match),
        "market_visible": bool(market_match),
        "jd_visible": bool(jd_match),
        "sku_batch_visible": len(visible_batch_markers) >= 2,
        "sku_batch_markers": visible_batch_markers,
        "title_match": title_match,
        "market_match": market_match,
        "jd_match": jd_match,
    }
    _debug_log(
        log,
        "[fill_product_info] price area state "
        f"title={state['title_visible']} market={state['market_visible']} "
        f"jd={state['jd_visible']} sku_batch={state['sku_batch_visible']}",
    )
    return state


def _price_area_ready(state: Optional[Dict[str, Any]]) -> bool:
    if not state:
        return False

    anchors = {str(item) for item in (state.get("text_anchors") or [])}
    has_price_anchor = bool({"市场价", "京东价"} & anchors)
    has_template_anchor = bool(state.get("market_visible") or state.get("jd_visible"))
    has_title_context = bool(state.get("title_visible") or "SKU编码" in anchors or "销售属性" in anchors)
    has_sku_batch_context = bool(state.get("sku_batch_visible"))
    return has_price_anchor or (has_template_anchor and has_title_context) or has_sku_batch_context


def _ensure_price_area_visible(locator=None, log=None, max_rounds: int = 3) -> Dict[str, Any]:
    import pyautogui

    locator = _get_locator(locator, log)
    last_state: Dict[str, Any] = {}
    for round_index in range(1, max_rounds + 1):
        _ensure_basic_info_page(locator=locator, log=log)
        _scroll_publish_page_to_top()
        time.sleep(0.5)

        state = _collect_price_area_template_state(locator=locator, log=log)
        if _price_area_ready(state):
            return {"success": True, "round": round_index, "state": state}

        pyautogui.moveTo(1800, 1000)
        for step in range(1, 7):
            pyautogui.scroll(-360)
            time.sleep(0.3)
            state = _collect_price_area_template_state(locator=locator, log=log)
            if _price_area_ready(state):
                _debug_log(log, f"[fill_product_info] price area visible after round={round_index} step={step}")
                return {"success": True, "round": round_index, "step": step, "state": state}
        last_state = state
    return {"success": False, "state": last_state}


def _find_price_input_center_by_template(label: str, locator=None, log=None) -> Optional[tuple[int, int]]:
    template_specs = {
        "市场价": ("market_price_label.png", 138, 35),
        "京东价": ("jd_price_label.png", 140, 35),
    }
    spec = template_specs.get(label)
    if not spec:
        return None

    template_name, dx, dy = spec
    match = _locate_template_in_window(
        template_name,
        locator=locator,
        log=log,
        cache_name=f"price_probe_{label}.png",
        confidences=(0.95, 0.92, 0.88, 0.84, 0.80),
    )
    if not match:
        _debug_log(log, f"[fill_product_info] price template anchor no-match label={label} template={template_name}")
        return None
    left, top, width, height = match["box"]
    local_x = int(left + width / 2 + dx)
    local_y = int(top + height / 2 + dy)
    try:
        screen_x, screen_y = locator.window_to_screen(local_x, local_y)
    except Exception:
        screen_x, screen_y = local_x, local_y
    _debug_log(
        log,
        "[fill_product_info] price template anchor "
        f"label={label} template={template_name} confidence={match['confidence']} "
        f"label_box={match['box']} local_input=({local_x}, {local_y}) screen_input=({screen_x}, {screen_y})",
    )
    return (screen_x, screen_y)


def _find_price_input_center(label: str, locator=None, log=None) -> Optional[tuple[int, int]]:
    locator = _get_locator(locator, log)
    template_center = _find_price_input_center_by_template(label, locator=locator, log=log)
    if template_center:
        return template_center
    window = find_jingmai_uia_window(locator=locator, log=log)
    nearby_named = []
    if window:
        for candidate in iter_named_descendants(window, control_types=["Text", "Edit", "ComboBox", "Button"], limit=500):
            name = (candidate["name"] or "").strip()
            rect = candidate["rect"]
            if rect.top < 430 or rect.top > 1080:
                continue
            if label in name or name in {"市场价", "京东价", "SKU编码", "销售属性", "请输入"}:
                nearby_named.append(
                    {
                        "name": name,
                        "type": candidate["control_type"],
                        "rect": [rect.left, rect.top, rect.right, rect.bottom],
                    }
                )
    if nearby_named:
        _debug_log(log, f"[fill_product_info] price probe label={label} nearby_named={nearby_named[:12]}")

    target = _find_named_control(label, ["Text", "Edit", "ComboBox"], locator=locator, log=log, top_range=(480, 980))
    if not target:
        _debug_log(log, f"[fill_product_info] price probe label={label} target_control=NOT_FOUND")
        return None

    _, _, label_rect = target
    label_center_x = (label_rect.left + label_rect.right) // 2
    candidates = []
    for _, _, rect in _find_edit_elements(locator=locator, log=log):
        if rect.top < label_rect.bottom - 10:
            continue
        if not (480 <= rect.top <= 1050):
            continue
        edit_center_x = (rect.left + rect.right) // 2
        if abs(edit_center_x - label_center_x) > 260:
            continue
        distance = abs(edit_center_x - label_center_x) + abs(rect.top - label_rect.bottom)
        candidates.append((distance, rect))

    _debug_log(
        log,
        "[fill_product_info] price probe "
        f"label={label} label_rect={[label_rect.left, label_rect.top, label_rect.right, label_rect.bottom]} "
        f"edit_candidates={[[r.left, r.top, r.right, r.bottom] for _, r in candidates[:8]]}",
    )

    if candidates:
        _, rect = sorted(candidates, key=lambda item: item[0])[0]
        return ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)

    fallback_x = min(max(label_center_x, 200), 2360)
    fallback_y = min(max(label_rect.bottom + 55, 520), 980)
    return (fallback_x, fallback_y)


def _ensure_basic_info_page(locator=None, log=None) -> bool:
    locator = _get_locator(locator, log)
    if _visible_text_contains("商品标题", locator=locator, log=log, top_range=(280, 520), left_range=(560, 1080)):
        return True

    target = _find_named_control("商品基本信息", ["Text", "Button", "Hyperlink"], locator=locator, log=log, top_range=(100, 220))
    if target:
        element, _, _ = target
        if click_uia_element(element, log=log):
            time.sleep(0.8)
            success = _visible_text_contains("商品标题", locator=locator, log=log, top_range=(280, 520), left_range=(560, 1080))
            if success:
                _debug_log(log, "[fill_product_info] switched to basic info page via UIA fallback")
                return True

    success = False
    if (
        _visible_text_contains("类目选择发品", locator=locator, log=log, top_range=(120, 320), left_range=(480, 1200))
        or _visible_text_contains("下一步，完善其他商品信息", locator=locator, log=log, top_range=(1180, 1380), left_range=(980, 1680))
    ):
        _debug_log(log, "[fill_product_info] category page detected, skip unsafe top-tab coordinate fallback")
        return False

    _debug_log(log, "[fill_product_info] basic info page missing, force click top tab")
    if locator.click(410, 160, delay=0.6):
        time.sleep(0.5)
        locator.click(410, 160, delay=0.4)
        time.sleep(0.8)
    success = _visible_text_contains("商品标题", locator=locator, log=log, top_range=(280, 520), left_range=(560, 1080))
    if success:
        _debug_log(log, "[fill_product_info] switched to basic info page via top-tab coordinates")
        return True

    if not success and _return_from_advanced_detail_editor(locator=locator, log=log):
        time.sleep(1.0)
        success = _visible_text_contains("鍟嗗搧鏍囬", locator=locator, log=log, top_range=(280, 520), left_range=(560, 1080))
        if success:
            _debug_log(log, "[fill_product_info] returned from advanced detail editor to merchant backend")
            return True

    _debug_log(log, f"[fill_product_info] basic info page restore success={success}")
    return success


def _is_advanced_detail_editor(locator=None, log=None) -> bool:
    locator = _get_locator(locator, log)
    has_return = _visible_text_contains("杩斿洖鍟嗗鍚庡彴", locator=locator, log=log, top_range=(0, 120), left_range=(0, 260))
    has_jdzp = _visible_text_contains("浜彴鏅哄簵", locator=locator, log=log, top_range=(0, 180), left_range=(0, 360))
    has_detail = _visible_text_contains("璇︽儏", locator=locator, log=log, top_range=(0, 180), left_range=(120, 520))
    has_high_editor = _visible_text_contains("楂樼骇缂栬緫", locator=locator, log=log, top_range=(180, 420), left_range=(760, 1240))
    return bool(has_return and ((has_jdzp and has_detail) or has_high_editor))


def _return_from_advanced_detail_editor(locator=None, log=None) -> bool:
    locator = _get_locator(locator, log)
    if not _is_advanced_detail_editor(locator=locator, log=log):
        return False

    target = _find_named_control("杩斿洖鍟嗗鍚庡彴", ["Button", "Hyperlink", "Text"], locator=locator, log=log, top_range=(0, 120), left_range=(0, 260))
    if target:
        element, _, _ = target
        if click_uia_element(element, log=log):
            return True

    return locator.click(70, 24, delay=0.5)


def _scroll_to_description_section(log=None):
    import pyautogui

    _scroll_publish_page_to_top()
    pyautogui.moveTo(1780, 980)
    for index in range(4):
        pyautogui.scroll(-520)
        _debug_log(log, f"[fill_product_description] scroll to description: step={index + 1} delta=-520")
        time.sleep(0.08)


def _select_description_mode(mode_label: str, locator=None, log=None) -> bool:
    locator = _get_locator(locator, log)
    target = _find_named_control(mode_label, ["Text", "Button", "RadioButton"], locator=locator, log=log, top_range=(300, 520), left_range=(820, 1180))
    if target:
        element, _, _ = target
        if click_uia_element(element, log=log):
            time.sleep(0.4)
            return True
    if mode_label == "浠ｇ爜缂栬緫":
        return locator.click(1040, 316, delay=0.4)
    if mode_label == "鍥炬枃缂栬緫":
        return locator.click(918, 316, delay=0.4)
    return False


def _build_description_html(product: Dict[str, Any]) -> str:
    detail_content = str(product.get("detail_content", "") or product.get("description", "") or "").strip()
    if detail_content:
        return detail_content

    lines = []
    title = str(product.get("title", "") or "").strip()
    brand = str(product.get("brand", "") or product.get("鍝佺墝", "") or "").strip()
    model = str(product.get("model", "") or "").strip()
    unit = str(product.get("unit", "") or "").strip()
    notes = str(product.get("notes", "") or "").strip()
    size_parts = [str(product.get("length_mm", "") or "").strip(), str(product.get("width_mm", "") or "").strip(), str(product.get("height_mm", "") or "").strip()]
    size_parts = [part for part in size_parts if part]
    weight = str(product.get("weight_kg", "") or "").strip()

    if title:
        lines.append(f"<p>{title}</p>")
    if brand:
        lines.append(f"<p>鍝佺墝锛?{brand}</p>")
    if model:
        lines.append(f"<p>鍨嬪彿锛?{model}</p>")
    if size_parts:
        lines.append(f"<p>瑙勬牸锛?{' x '.join(size_parts)} mm</p>")
    if weight:
        lines.append(f"<p>閲嶉噺锛?{weight} kg</p>")
    if unit:
        lines.append(f"<p>閿€鍞崟浣嶏細{unit}</p>")
    if notes:
        lines.append(f"<p>璇存槑锛?{notes}</p>")
    return "".join(lines)


def _fill_description_code_editor(html: str, locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    _scroll_to_description_section(log=log)
    _select_description_mode("浠ｇ爜缂栬緫", locator=locator, log=log)
    time.sleep(0.4)

    target = None
    for element, name, rect in _find_edit_elements(locator=locator, log=log):
        if rect.left < 820 or rect.top < 320 or rect.bottom < 420:
            continue
        target = (element, rect)
        break

    if target:
        element, _ = target
        try:
            element.set_edit_text(html)
            time.sleep(0.3)
            verify = _verify_uia_edit_value("detail_content", html, element)
            return {
                "field": "detail_content",
                "method": "uia-set-edit-text",
                "write_success": True,
                "verify_success": verify.get("success", False),
                "success": verify.get("success", False),
                "expected": html,
                "actual": verify.get("actual", ""),
                "verification_method": verify.get("method", ""),
                "compare_mode": verify.get("compare_mode", ""),
            }
        except Exception:
            pass

    if locator.click(1260, 530, delay=0.4):
        write_result = _write_active_text(html, clear=True)
        verify = _verify_active_text("detail_content", html)
        return {
            "field": "detail_content",
            "method": write_result.get("method", "active-write"),
            "write_success": write_result.get("success", False),
            "verify_success": verify.get("success", False),
            "success": write_result.get("success", False) and verify.get("success", False),
            "expected": html,
            "actual": verify.get("actual", ""),
            "verification_method": verify.get("method", ""),
            "compare_mode": verify.get("compare_mode", ""),
            **({"verify_error": verify.get("message", "detail content verify failed")} if not verify.get("success") else {}),
        }

    return {
        "field": "detail_content",
        "write_success": False,
        "verify_success": False,
        "success": False,
        "verify_error": "detail editor not found",
    }


def _extract_description_images(product: Dict[str, Any]) -> list[str]:
    candidates = []
    for key in ("description_images", "detail_images", "images"):
        value = product.get(key)
        if isinstance(value, list):
            candidates.extend(str(item).strip() for item in value if str(item).strip())
        elif isinstance(value, str) and value.strip():
            candidates.append(value.strip())
    return candidates


def _description_upload_prompt_visible(locator=None, log=None) -> bool:
    locator = _get_locator(locator, log)
    return bool(
        _visible_text_contains("璇蜂笂浼犲浘鐗囨垨瑙嗛", locator=locator, log=log, top_range=(260, 1180), left_range=(760, 1880))
        or _visible_text_contains("涓婁紶鍥剧墖", locator=locator, log=log, top_range=(260, 1180), left_range=(760, 1880))
    )


def _upload_description_image(image_path: str, locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    _scroll_to_description_section(log=log)
    _select_description_mode("鍥炬枃缂栬緫", locator=locator, log=log)
    target = _find_named_control("涓婁紶鍥剧墖", ["Button", "Hyperlink", "Text"], locator=locator, log=log, top_range=(260, 1180), left_range=(760, 1880))
    if target:
        element, _, _ = target
        click_uia_element(element, log=log)
        time.sleep(0.4)
    else:
        locator.click(1330, 816, delay=0.4)

    result = upload_image(image_path, locator=locator, log=log)
    result["field"] = "detail_image"
    return result


def _hover_then_click(x: int, y: int, *, clicks: int = 1, interval: float = 0.1, delay: float = 0.25) -> bool:
    try:
        import pyautogui

        _release_mouse_buttons()
        pyautogui.moveTo(x, y, duration=0.12)
        time.sleep(0.08)
        if clicks == 2:
            pyautogui.doubleClick(x, y, interval=interval)
        else:
            pyautogui.click(x, y, clicks=clicks, interval=interval)
        time.sleep(delay)
        return True
    except Exception:
        return _session1_click(x, y, delay=delay)


def _find_sku_product_name_center(locator=None, log=None) -> Optional[tuple[int, int]]:
    _scroll_to_sku_section(log=log)
    for _, name, rect in _find_edit_elements(locator=locator, log=log):
        if rect.left < 1800 or not (520 <= rect.top <= 720):
            continue
        if name in {"请输入", ""} or "商品名称" in name:
            return ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
    return (2024, 613)


def _fill_sku_product_name_field(title: str, locator=None, log=None) -> Dict[str, Any]:
    """Fill SKU product name field using UIA set_edit_text (cross-session capable)."""
    locator = _get_locator(locator, log)
    
    # Find the SKU element with UIA (returns element, name, rect)
    _scroll_to_sku_section(log=log)
    element = None
    for elem, name, rect in _find_edit_elements(locator=locator, log=log):
        # SKU region: left >= 1800, top 520-720
        if rect.left < 1800 or not (520 <= rect.top <= 720):
            continue
        if name in {"请输入", ""} or "商品名称" in name:
            element = elem
            break
    
    # Fallback to coordinates if element not found
    if not element:
        center = _find_sku_product_name_center(locator=locator, log=log)
        if center:
            # Try using Session1 Helper to click and write
            if _session1_click(center[0], center[1], delay=0.3):
                time.sleep(0.2)
                write_result = _write_active_text(title, clear=True)
                verify = _verify_active_text("title", title)
                payload = {
                    "field": "sku_product_name",
                    "method": write_result.get("method", "session1-write"),
                    "write_success": write_result.get("success", False),
                    "verify_success": verify.get("success", False),
                    "success": write_result.get("success", False) and verify.get("success", False),
                    "expected": str(title),
                    "actual": verify.get("actual", ""),
                    "verification_method": verify.get("method", ""),
                    "compare_mode": verify.get("compare_mode", ""),
                }
                if not verify.get("success"):
                    payload["verify_error"] = verify.get("message", "sku product name verify failed")
                return payload
        return {
            "field": "sku_product_name",
            "write_success": False,
            "verify_success": False,
            "success": False,
            "verify_error": "sku product name field not found",
        }
    
    # Use UIA set_edit_text directly (cross-session effective)
    try:
        element.set_edit_text(str(title))
        time.sleep(0.2)
        verify = _verify_uia_edit_value("title", title, element)
        payload = {
            "field": "sku_product_name",
            "method": "uia-set-edit-text",
            "write_success": True,
            "verify_success": verify.get("success", False),
            "success": verify.get("success", False),
            "expected": str(title),
            "actual": verify.get("actual", ""),
            "verification_method": verify.get("method", ""),
            "compare_mode": verify.get("compare_mode", ""),
        }
        if not verify.get("success"):
            payload["verify_error"] = verify.get("message", "sku product name verify failed")
        return payload
    except Exception as exc:
        # Fallback to session1 click + write
        try:
            rect = element.rectangle()
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2
            _session1_click(center_x, center_y, delay=0.3)
        except Exception:
            pass
        time.sleep(0.2)
        write_result = _write_active_text(title, clear=True)
        verify = _verify_active_text("title", title)
        payload = {
            "field": "sku_product_name",
            "method": write_result.get("method", "active-write"),
            "write_success": write_result.get("success", False),
            "verify_success": verify.get("success", False),
            "success": write_result.get("success", False) and verify.get("success", False),
            "expected": str(title),
            "actual": verify.get("actual", ""),
            "verification_method": verify.get("method", ""),
            "compare_mode": verify.get("compare_mode", ""),
        }
        if not verify.get("success"):
            payload["verify_error"] = verify.get("message", "sku product name verify failed")
        return payload


def _drag_sku_horizontal_scrollbar():
    for _ in range(3):
        _hover_then_click(1800, 915, delay=0.3)


def _reset_sku_horizontal_scrollbar():
    for _ in range(3):
        _hover_then_click(1200, 915, delay=0.3)


def _fill_sku_pricing_fields_v2(product: Dict[str, Any], locator=None, log=None) -> list[Dict[str, Any]]:
    market_price = product.get("market_price")
    jd_price = product.get("jd_price")
    purchase_price = product.get("purchase_price")
    if purchase_price in (None, "") and jd_price not in (None, ""):
        try:
            purchase_price = round(Decimal(str(jd_price)) * Decimal("0.95"), 2)
        except Exception:
            purchase_price = ""

    _scroll_to_sku_section()
    _drag_sku_horizontal_scrollbar()

    import pyautogui

    fields = [
        ("market_price", market_price, (1278, 603)),
        ("purchase_price", purchase_price, (1388, 603)),
        ("jd_price", jd_price, (1498, 603)),
    ]

    details: list[Dict[str, Any]] = []
    for field, value, (x, y) in fields:
        if value in (None, ""):
            continue
        pyautogui.click(x, y)
        time.sleep(0.2)
        write_result = _write_active_text(value, clear=True)
        verify = _verify_active_text(field, value)
        item = {
            "field": field,
            "method": write_result.get("method", "active-write"),
            "write_success": write_result.get("success", False),
            "verify_success": verify.get("success", False),
            "success": write_result.get("success", False) and verify.get("success", False),
            "expected": str(value),
            "actual": verify.get("actual", ""),
            "verification_method": verify.get("method", ""),
            "compare_mode": verify.get("compare_mode", ""),
        }
        if not verify.get("success"):
            item["verify_error"] = verify.get("message", f"{field} verify failed")
        details.append(item)
        time.sleep(0.2)
    return details


def _fill_sku_pricing_fields_v3(product: Dict[str, Any], locator=None, log=None) -> list[Dict[str, Any]]:
    locator = _get_locator(locator, log)
    _ensure_basic_info_page(locator=locator, log=log)
    _scroll_to_sku_section(log=log)
    _reset_sku_horizontal_scrollbar()
    _debug_log(log, "[fill_product_info] sku scrollbar reset by click-track")

    details: list[Dict[str, Any]] = []
    title = str(product.get("title", "") or "")
    if title:
        _debug_log(log, "[fill_product_info] fill sku product name")
        details.append(_fill_sku_product_name_field(title, locator=locator, log=log))
        time.sleep(0.2)

    visibility = _ensure_price_area_visible(locator=locator, log=log)
    if not visibility.get("success"):
        details.append(
            {
                "field": "price_area_anchor",
                "method": "template-state-guard",
                "write_success": False,
                "verify_success": False,
                "success": False,
                "verify_error": f"price area not visible: {visibility.get('state', {})}",
            }
        )
        return details

    _drag_sku_horizontal_scrollbar()
    state = visibility.get("state", {})
    _debug_log(
        log,
        "[fill_product_info] sku scrollbar shift right by click-track "
        f"title={state.get('title_visible')} market={state.get('market_visible')} jd={state.get('jd_visible')}",
    )

    import pyautogui

    field_specs = [
        ("market_price", "市场价", product.get("market_price"), (1278, 603)),
        ("purchase_price", "", product.get("purchase_price"), (1388, 603)),
        ("jd_price", "京东价", product.get("jd_price"), (1518, 603)),
    ]

    for field, label, value, fallback_center in field_specs:
        if value in (None, ""):
            continue
        x, y = fallback_center
        if label:
            center = _find_price_input_center(label, locator=locator, log=log)
            if center:
                x, y = center
        _debug_log(log, f"[fill_product_info] click price field {field} at ({x}, {y}) with hover-then-double-click")
        _hover_then_click(x, y, clicks=2, interval=0.1, delay=0.2)
        write_result = _write_active_text(value, clear=True)
        verify = _verify_text_field(locator, field, x, y, value)
        item = {
            "field": field,
            "method": write_result.get("method", "active-write"),
            "write_success": write_result.get("success", False),
            "verify_success": verify.get("success", False),
            "success": write_result.get("success", False) and verify.get("success", False),
            "expected": str(value),
            "actual": verify.get("actual", ""),
            "verification_method": verify.get("method", ""),
            "compare_mode": verify.get("compare_mode", ""),
        }
        if not verify.get("success"):
            item["verify_error"] = verify.get("message", f"{field} verify failed")
        details.append(item)
        time.sleep(0.2)
    return details


def _fill_sku_pricing_fields(product: Dict[str, Any], locator=None, log=None) -> list[Dict[str, Any]]:
    locator = _get_locator(locator, log)
    title = str(product.get("title", "") or "")
    market_price = product.get("market_price")
    jd_price = product.get("jd_price")
    purchase_price = product.get("purchase_price")
    if purchase_price in (None, "") and jd_price not in (None, ""):
        try:
            purchase_price = round(Decimal(str(jd_price)) * Decimal("0.95"), 2)
        except Exception:
            purchase_price = ""

    start = _find_sku_product_name_center(locator=locator, log=log)
    if not start or not locator.click(start[0], start[1], delay=0.3):
        return [{"field": "market_price", "success": False, "write_success": False, "verify_success": False, "verify_error": "sku product row focus failed"}]

    import pyautogui

    details: list[Dict[str, Any]] = []
    sequence = [
        ("sku_product_name", title, True),
        ("sku_short_title", title[:30] if title else "", False),
        ("market_price", market_price, True),
        ("purchase_price", purchase_price, False),
        ("jd_price", jd_price, True),
    ]

    for index, (field, value, verify_required) in enumerate(sequence):
        if value not in (None, ""):
            write_result = _write_active_text(value, clear=True)
            verify = _verify_active_text(field if field in {"market_price", "purchase_price", "jd_price"} else "title", value)
            item = {
                "field": field,
                "method": write_result.get("method", "active-write"),
                "write_success": write_result.get("success", False),
                "verify_success": verify.get("success", False),
                "success": write_result.get("success", False) and (verify.get("success", False) if verify_required else True),
                "expected": str(value),
                "actual": verify.get("actual", ""),
                "verification_method": verify.get("method", ""),
                "compare_mode": verify.get("compare_mode", ""),
            }
            if verify_required and not verify.get("success"):
                item["verify_error"] = verify.get("message", f"{field} verify failed")
            details.append(item)
        if index < len(sequence) - 1:
            pyautogui.press("tab")
            time.sleep(0.2)

    return details


@ActionRegistry.register("fill_product_info", "form", "批量填充商品信息")
def fill_product_info(product: Dict[str, Any], locator=None, log=None, required_visual_fields=None, **_kwargs) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    results = []
    title = product.get("title")
    if title not in (None, ""):
        title_result = _fill_title_field_v3(str(title), locator=locator, log=log)
        results.append(title_result)
        time.sleep(0.3)

    procurement_erp_result = _fill_procurement_erp_field(product, locator=locator, log=log)
    if procurement_erp_result:
        results.append(procurement_erp_result)
        time.sleep(0.2)

    model = product.get("model")
    if model not in (None, ""):
        results.append(_fill_model_field_v2(str(model), locator=locator, log=log))
        time.sleep(0.3)

    if any(product.get(field) not in (None, "") for field in ("market_price", "purchase_price", "jd_price")):
        results.extend(_fill_sku_pricing_fields_v3(product, locator=locator, log=log))
        time.sleep(0.3)

    brand = product.get("brand") or product.get("品牌")
    if brand:
        results.append(_fill_brand_field_v2(str(brand), locator=locator, log=log))
        time.sleep(0.5)
        brand_coords = None
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


@ActionRegistry.register("fill_product_description", "form", "填写商品详情")
def fill_product_description(product: Dict[str, Any], locator=None, log=None, **_kwargs) -> Dict[str, Any]:
    locator = _get_locator(locator, log)

    if _return_from_advanced_detail_editor(locator=locator, log=log):
        time.sleep(1.0)

    _scroll_to_description_section(log=log)

    if _is_advanced_detail_editor(locator=locator, log=log):
        return {
            "success": False,
            "field": "detail_content",
            "message": "advanced detail editor is still active after return attempt",
        }

    image_paths = _extract_description_images(product)
    detail_content = str(product.get("detail_content", "") or product.get("description", "") or "").strip()

    if image_paths:
        upload_result = _upload_description_image(image_paths[0], locator=locator, log=log)
        upload_result["success"] = bool(upload_result.get("success"))
        if not upload_result["success"] and "message" not in upload_result:
            upload_result["message"] = upload_result.get("verify_error", "detail image upload failed")
        return upload_result

    if detail_content:
        result = _fill_description_code_editor(detail_content, locator=locator, log=log)
        result["success"] = bool(result.get("success"))
        if not result["success"] and "message" not in result:
            result["message"] = result.get("verify_error", "detail content fill failed")
        return result

    return {
        "success": False,
        "field": "detail_content",
        "message": "detail_content missing and no description_images available for backend detail editor",
    }


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
