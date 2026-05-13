"""
京麦商品发布自动化 - 表单操作 Actions
覆盖文本输入、下拉选择、商品信息填写、图片上传等行为。
"""
import re
import time
from decimal import Decimal, InvalidOperation
from pathlib import Path
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
        if not result.get("success") and spec["kind"] != "custom":
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
    prefer_first_option_keyboard: bool = False,
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

        if prefer_first_option_keyboard and _visible_text_contains(
            option_text,
            locator=locator,
            log=log,
            top_range=top_range,
            left_range=(max(0, x - 120), x + 900),
        ):
            try:
                import pyautogui

                pyautogui.press("down")
                time.sleep(0.15)
                pyautogui.press("enter")
                time.sleep(0.35)
                return {"success": True, "option": option_text, "method": "keyboard-first-option"}
            except Exception:
                pass

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
        "current": ["current", "rated_current", "电流", "额定电流"],
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
    preferred_types: tuple[str, ...] | None = None,
) -> Optional[tuple[int, int]]:
    window = find_jingmai_uia_window(locator=locator, log=log)
    if not window:
        return None

    top_range = top_range or (520, 1100)
    preferred_types = preferred_types or ("ComboBox", "Edit", "Button")
    type_rank = {control_type: index for index, control_type in enumerate(preferred_types)}
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
            score = (type_rank.get(candidate["control_type"], len(preferred_types)), dy, max(dx, 0), rect.left)
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
    _scroll_publish_page_to_top(locator=locator, log=log)
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
    _scroll_publish_page_to_top(locator=locator, log=log)
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
    _scroll_publish_page_to_top(locator=locator, log=log)
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
    from config.jingmai_coords import PRODUCT_INFO_PAGE
    _scroll_publish_page_to_top(locator=locator, log=log)
    if _page_text_contains(brand, x=900, y=520):
        return {
            "field": "brand",
            "method": "page-text",
            "value": brand,
            "write_success": True,
            "verify_success": True,
            "success": True,
        }
    if _visible_text_contains(brand, locator=locator, log=log, top_range=(320, 460), left_range=(480, 1040)):
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
        prefer_first_option_keyboard=True,
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


def _dropdown_selection_confirmed(
    expected_text: str,
    *,
    locator=None,
    log=None,
    top_range: tuple[int, int] | None = None,
    left_range: tuple[int, int] | None = None,
) -> bool:
    if _visible_text_contains(
        expected_text,
        locator=locator,
        log=log,
        top_range=top_range,
        left_range=left_range,
    ):
        return True
    active = _verify_active_text("title", expected_text)
    return bool(active.get("success"))


def _fill_brand_field_v2(brand: str, locator=None, log=None) -> Dict[str, Any]:
    from config.jingmai_coords import PRODUCT_INFO_PAGE

    locator = _get_locator(locator, log)
    _scroll_publish_page_to_top(locator=locator, log=log)
    if _page_text_contains(brand, x=900, y=520):
        return {
            "field": "brand",
            "method": "page-text",
            "value": brand,
            "write_success": True,
            "verify_success": True,
            "success": True,
        }
    if _dropdown_selection_confirmed(
        brand,
        locator=locator,
        log=log,
        top_range=(320, 460),
        left_range=(480, 1040),
    ):
        return {
            "field": "brand",
            "method": "uia-visible-text",
            "value": brand,
            "write_success": True,
            "verify_success": True,
            "success": True,
        }

    center = PRODUCT_INFO_PAGE.get("brand_select")
    target = _find_named_control("品牌", ["ComboBox"], locator=locator, log=log, top_range=(320, 460), left_range=(360, 760))
    if target:
        _, _, rect = target
        center = ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
    if not center:
        return {
            "field": "brand",
            "method": "uia-combobox",
            "value": brand,
            "write_success": False,
            "verify_success": False,
            "success": False,
            "error": "brand combobox not found",
        }

    result = _select_dropdown_option(
        brand,
        center[0],
        center[1],
        locator=locator,
        log=log,
        preferred_keywords=["品牌"],
        top_range=(320, 760),
        vision_template="brand_option.png",
        prefer_first_option_keyboard=True,
    )
    success = result.get("success", False) and (
        _dropdown_selection_confirmed(
            brand,
            locator=locator,
            log=log,
            top_range=(320, 460),
            left_range=(480, 1120),
        )
        or result.get("method") in {"uia-local", "vision", "keyboard", "keyboard-first-option"}
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


def _fill_supported_attributes(product: Dict[str, Any], locator=None, log=None) -> list[Dict[str, Any]]:
    from config.jingmai_coords import PRODUCT_INFO_PAGE

    locator = _get_locator(locator, log)
    attribute_values = _collect_attribute_values(product)
    specs = [
        {
            "field": "protection_level",
            "coords": PRODUCT_INFO_PAGE.get("protection_level"),
            "value": attribute_values.get("protection_level"),
            "preferred_keywords": ["IP"],
            "vision_template": "protection_level_option.png",
            "label_keywords": ["IP", "防护等级"],
        },
        {
            "field": "material",
            "coords": PRODUCT_INFO_PAGE.get("material"),
            "value": attribute_values.get("material"),
            "preferred_keywords": ["材质"],
            "vision_template": "material_option.png",
            "label_keywords": ["材质"],
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

    results: list[Dict[str, Any]] = []
    for spec in specs:
        if spec["value"] in (None, ""):
            continue
        coords = spec["coords"] or _find_labeled_dropdown_center(
            spec.get("label_keywords") or spec["preferred_keywords"],
            locator=locator,
            log=log,
            top_range=(620, 920),
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
            top_range=(max(240, coords[1] - 120), coords[1] + 260),
            vision_template=spec["vision_template"],
        )
        success = result.get("success", False) and (
            _dropdown_selection_confirmed(
                str(spec["value"]),
                locator=locator,
                log=log,
                top_range=(max(240, coords[1] - 80), coords[1] + 80),
                left_range=(max(0, coords[0] - 420), coords[0] + 420),
            )
        or result.get("method") in {"uia-local", "vision", "keyboard", "keyboard-first-option"}
    )
        results.append(
            {
                "field": spec["field"],
                "method": result.get("method", "select_dropdown"),
                "value": str(spec["value"]),
                "write_success": result.get("success", False),
                "verify_success": success,
                "success": success,
                **({"error": result.get("message", f"{spec['field']} verify failed")} if not success else {}),
            }
        )
        time.sleep(0.5)
    return results


def _fill_brand_field_v2(brand: str, locator=None, log=None) -> Dict[str, Any]:
    from config.jingmai_coords import PRODUCT_INFO_PAGE

    locator = _get_locator(locator, log)
    _scroll_publish_page_to_top(locator=locator, log=log)
    if _page_text_contains(brand, x=900, y=520):
        return {
            "field": "brand",
            "method": "page-text",
            "value": brand,
            "write_success": True,
            "verify_success": True,
            "success": True,
        }
    if _dropdown_selection_confirmed(
        brand,
        locator=locator,
        log=log,
        top_range=(320, 460),
        left_range=(480, 1040),
    ):
        return {
            "field": "brand",
            "method": "uia-visible-text",
            "value": brand,
            "write_success": True,
            "verify_success": True,
            "success": True,
        }

    center = PRODUCT_INFO_PAGE.get("brand_select")
    target = _find_named_control("品牌", ["ComboBox"], locator=locator, log=log, top_range=(320, 460), left_range=(360, 760))
    if target:
        _, _, rect = target
        center = ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
    if not center:
        return {
            "field": "brand",
            "method": "uia-combobox",
            "value": brand,
            "write_success": False,
            "verify_success": False,
            "success": False,
            "error": "brand combobox not found",
        }

    result = _select_dropdown_option(
        brand,
        center[0],
        center[1],
        locator=locator,
        log=log,
        preferred_keywords=["品牌"],
        top_range=(320, 760),
        vision_template="brand_option.png",
        prefer_first_option_keyboard=True,
    )
    success = result.get("success", False) and (
        _dropdown_selection_confirmed(
            brand,
            locator=locator,
            log=log,
            top_range=(320, 460),
            left_range=(480, 1120),
        )
        or result.get("method") in {"uia-local", "vision", "keyboard", "keyboard-first-option"}
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


def _fill_supported_attributes(product: Dict[str, Any], locator=None, log=None) -> list[Dict[str, Any]]:
    from config.jingmai_coords import PRODUCT_INFO_PAGE

    locator = _get_locator(locator, log)
    attribute_values = _collect_attribute_values(product)
    specs = [
        {
            "field": "protection_level",
            "coords": PRODUCT_INFO_PAGE.get("protection_level"),
            "value": attribute_values.get("protection_level"),
            "preferred_keywords": ["IP"],
            "vision_template": "protection_level_option.png",
            "label_keywords": ["IP", "防护等级"],
        },
        {
            "field": "material",
            "coords": PRODUCT_INFO_PAGE.get("material"),
            "value": attribute_values.get("material"),
            "preferred_keywords": ["材质"],
            "vision_template": "material_option.png",
            "label_keywords": ["材质"],
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

    results: list[Dict[str, Any]] = []
    for spec in specs:
        if spec["value"] in (None, ""):
            continue
        coords = spec["coords"] or _find_labeled_dropdown_center(
            spec.get("label_keywords") or spec["preferred_keywords"],
            locator=locator,
            log=log,
            top_range=(620, 920),
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
            top_range=(max(240, coords[1] - 120), coords[1] + 260),
            vision_template=spec["vision_template"],
        )
        success = result.get("success", False) and (
            _dropdown_selection_confirmed(
                str(spec["value"]),
                locator=locator,
                log=log,
                top_range=(max(240, coords[1] - 80), coords[1] + 80),
                left_range=(max(0, coords[0] - 420), coords[0] + 420),
            )
            or result.get("method") in {"uia-local", "vision", "keyboard"}
        )
        results.append(
            {
                "field": spec["field"],
                "method": result.get("method", "select_dropdown"),
                "value": str(spec["value"]),
                "write_success": result.get("success", False),
                "verify_success": success,
                "success": success,
                **({"error": result.get("message", f"{spec['field']} verify failed")} if not success else {}),
            }
        )
        time.sleep(0.5)
    return results


def _fill_procurement_erp_field(product: Dict[str, Any], locator=None, log=None) -> Optional[Dict[str, Any]]:
    locator = _get_locator(locator, log)
    _scroll_publish_page_to_top(locator=locator, log=log)

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


def _focus_publish_scroll_anchor(
    target_texts: list[str],
    *,
    locator=None,
    log=None,
    page_hint: str = "",
) -> bool:
    locator = _get_locator(locator, log)
    try:
        from actions.navigation import vision_click_text_center
    except Exception:
        vision_click_text_center = None

    for target_text in target_texts:
        text = str(target_text or "").strip()
        if not text:
            continue
        try:
            if vision_click_text_center:
                result = vision_click_text_center(
                    target_text=text,
                    page_hint=page_hint or f"京麦发布页滚动区域，定位并点击{text}附近的可滚动内容区域",
                    locator=locator,
                    log=log,
                )
                if result.get("success"):
                    _debug_log(log, f"[vision-scroll] anchor clicked by vision: {text}")
                    return True
        except Exception as exc:
            _debug_log(log, f"[vision-scroll] anchor failed: {text} error={exc}")
    return False


def _scroll_publish_page_to_top(locator=None, log=None):
    import pyautogui

    _focus_publish_scroll_anchor(
        ["商品标题", "商品基本信息", "品牌", "类目"],
        locator=locator,
        log=log,
        page_hint="京麦商品发布页顶部区域，定位标题或基本信息区作为滚动锚点",
    )
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


def _text_variants(text: str) -> tuple[str, ...]:
    source = str(text or "")
    variants = [source] if source else []
    legacy_aliases = {
        "返回商家后台": ["\u6769\u65bf\u6d16\u935f\u55d7\ue18d\u935a\u5ea1\u5f74"],
        "京东智铺": ["\u6d5c\ue100\u5f74\u93c5\u54c4\u7c35"],
        "详情": ["\u7487\ufe3d\u510f"],
        "高级编辑": ["\u6942\u6a3c\u9a87\u7f02\u682c\u7deb"],
        "商品标题": ["\u935f\u55d7\u6427\u93cd\u56ec\ue57d"],
        "商品基本信息": ["\u935f\u55d7\u6427\u9369\u70d8\u6e70\u6dc7\u2103\u4f05"],
        "类目选择发品": ["\u7eeb\u8364\u6d30\u95ab\u590b\u5ae8\u9359\u621d\u6427"],
        "下一步，完善其他商品信息": ["\u6d93\u5b29\u7af4\u59dd\u30ef\u7d1d\u7039\u5c7d\u677d\u934f\u6735\u7cac\u935f\u55d7\u6427\u6dc7\u2103\u4f05"],
        "请上传图片或视频": ["\u7487\u4f77\u7b02\u6d60\u72b2\u6d7c\u72b2\u9421\u56e8\u57c9\u6216\u89c6\u9891"],
        "上传图片": ["\u6d93\u0454\u7d36\u935b\u5267\u5896"],
        "图文编辑": ["\u9365\u7487\u67ab\u6587\u7f02\u682c\u7deb"],
    }
    for alias in legacy_aliases.get(source, []):
        if alias and alias not in variants:
            variants.append(alias)
    try:
        mojibake = source.encode("utf-8").decode("gbk")
    except Exception:
        mojibake = ""
    if mojibake and mojibake not in variants:
        variants.append(mojibake)
    return tuple(variants)


def _scroll_to_sku_section(locator=None, log=None):
    import pyautogui

    _debug_log(log, "[fill_product_info] scroll to sku section: reset to top")
    _scroll_publish_page_to_top(locator=locator, log=log)
    _focus_publish_scroll_anchor(
        ["商品名称", "销售属性", "SKU", "商品标题"],
        locator=locator,
        log=log,
        page_hint="京麦商品信息页中部，定位商品名称或销售属性区域后再向下滚动到SKU区",
    )
    pyautogui.moveTo(1800, 1000)
    for index in range(2):
        pyautogui.scroll(-550)
        _debug_log(log, f"[fill_product_info] scroll to sku section: step={index + 1} delta=-550")
        time.sleep(0.25)


def _scroll_price_fields_into_view(log=None):
    import pyautogui

    _focus_publish_scroll_anchor(
        ["SKU", "销售属性", "市场价", "京东价"],
        log=log,
        page_hint="京麦商品信息页价格区附近，定位SKU或价格字段后继续向下滚动",
    )
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


def _get_extended_price_area_anchors(locator=None, log=None) -> list[str]:
    locator = _get_locator(locator, log)
    anchors = list(_collect_price_area_anchors(locator=locator, log=log))
    for label in (
        "閲囪喘浠?",
        "SKU灞炴€?",
        "鎵归噺瀵煎叆",
        "鎵归噺搴旂敤",
        "榛樿鍏ㄩ儴SKU",
    ):
        if label in anchors:
            continue
        if _visible_text_contains(label, locator=locator, log=log, top_range=(440, 1380)):
            anchors.append(label)
    return anchors


def _collect_fill_page_state(locator=None, log=None) -> Dict[str, bool]:
    locator = _get_locator(locator, log)
    markers = {
        "title_top": ("商品标题", (280, 520), (560, 1080)),
        "product_name_mid": ("商品名称", (480, 980), (920, 1700)),
        "sku_mid": ("SKU", (480, 980), (900, 1700)),
        "sales_attr_mid": ("销售属性", (480, 980), (900, 1700)),
        "market_mid": ("市场价", (520, 1060), (960, 1880)),
        "jd_mid": ("京东价", (520, 1060), (960, 1880)),
        "category_page": ("类目选择发品", (120, 320), (480, 1200)),
        "next_button": ("下一步，完善其他商品信息", (1180, 1380), (980, 1680)),
        "basic_tab": ("商品基本信息", (100, 220), (260, 980)),
    }
    state: Dict[str, bool] = {}
    for key, (text, top_range, left_range) in markers.items():
        state[key] = _visible_text_contains(
            text,
            locator=locator,
            log=log,
            top_range=top_range,
            left_range=left_range,
        )
    return state


def _fill_page_has_positive_markers(page_state: Optional[Dict[str, bool]], locator=None, log=None) -> bool:
    state = page_state or {}
    if state.get("title_top"):
        return True
    if (
        state.get("product_name_mid")
        or state.get("sku_mid")
        or state.get("sales_attr_mid")
        or state.get("market_mid")
        or state.get("jd_mid")
        or state.get("basic_tab")
    ):
        return True
    return bool(_find_visible_price_edit_row(locator=locator, log=log))


def _fill_page_has_category_markers(page_state: Optional[Dict[str, bool]]) -> bool:
    state = page_state or {}
    return bool(state.get("category_page") or state.get("next_button"))


def _classify_fill_page_state(locator=None, log=None) -> str:
    locator = _get_locator(locator, log)
    if _is_advanced_detail_editor(locator=locator, log=log):
        return "description_page"

    page_state = _collect_fill_page_state(locator=locator, log=log)
    price_state = _collect_price_area_template_state(locator=locator, log=log)
    has_positive = _fill_page_has_positive_markers(page_state, locator=locator, log=log)
    has_category = _fill_page_has_category_markers(page_state)
    has_price_context = bool(
        price_state.get("sku_batch_visible")
        or price_state.get("market_input_visible")
        or price_state.get("jd_input_visible")
        or int(price_state.get("visible_price_row_count", 0) or 0) >= 2
        or ("SKU编码" in {str(item) for item in (price_state.get("text_anchors") or [])})
    )
    is_blank_basic_tab = bool(
        page_state.get("basic_tab")
        and not any(
            page_state.get(key)
            for key in ("title_top", "product_name_mid", "sku_mid", "sales_attr_mid", "market_mid", "jd_mid")
        )
        and not has_price_context
    )
    if has_category and not has_positive:
        return "category_page"
    if is_blank_basic_tab:
        return "wrong_blank_page"
    if has_price_context:
        return "sku_table_page"
    if has_positive:
        return "product_info_page"
    return "unknown"


def _seek_price_area(locator=None, log=None, max_scrolls: int = 6) -> dict:
    import pyautogui

    locator = _get_locator(locator, log)
    _scroll_to_sku_section(locator=locator, log=log)
    _focus_publish_scroll_anchor(
        ["SKU", "市场价", "京东价"],
        locator=locator,
        log=log,
        page_hint="京麦价格区附近，定位市场价或京东价字段后滚动查找价格区域",
    )
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
    anchors = _get_extended_price_area_anchors(locator=locator, log=log)
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
        "批量导入",
        "批量设置",
        "默认全部SKU",
        "SKU属性",
    ]
    visible_batch_markers = [
        marker
        for marker in sku_batch_markers
        if _visible_text_contains(marker, locator=locator, log=log, top_range=(980, 1380))
    ]
    market_input = _find_price_input_target("市场价", locator=locator, log=log)
    jd_input = _find_price_input_target("京东价", locator=locator, log=log)
    visible_price_row = _find_visible_price_edit_row(locator=locator, log=log)
    has_sku_table_anchor = bool(
        {"SKU灞炴€?", "鎵归噺瀵煎叆", "鎵归噺搴旂敤", "榛樿鍏ㄩ儴SKU"} & {str(item) for item in anchors}
    )
    state = {
        "text_anchors": anchors,
        "title_visible": bool(title_match),
        "market_visible": bool(market_match),
        "jd_visible": bool(jd_match),
        "market_input_visible": bool(market_input) or bool(visible_price_row and len(visible_price_row) >= 2),
        "jd_input_visible": bool(jd_input) or bool(visible_price_row and len(visible_price_row) >= 2),
        "sku_batch_visible": len(visible_batch_markers) >= 2,
        "sku_batch_markers": visible_batch_markers,
        "sku_table_anchor_visible": has_sku_table_anchor,
        "title_match": title_match,
        "market_match": market_match,
        "jd_match": jd_match,
        "visible_price_row_count": len(visible_price_row),
    }
    _debug_log(
        log,
        "[fill_product_info] price area state "
        f"title={state['title_visible']} market={state['market_visible']} "
        f"jd={state['jd_visible']} market_input={state['market_input_visible']} "
        f"jd_input={state['jd_input_visible']} sku_batch={state['sku_batch_visible']} "
        f"sku_table_anchor={state['sku_table_anchor_visible']}",
    )
    return state


def _price_area_ready(state: Optional[Dict[str, Any]]) -> bool:
    if not state:
        return False

    anchors = {str(item) for item in (state.get("text_anchors") or [])}
    has_price_anchor = bool(any(anchor in anchors for anchor in ("甯傚満浠?", "閲囪喘浠?", "浜笢浠?")))
    has_template_anchor = bool(state.get("market_visible") or state.get("jd_visible"))
    has_title_context = bool(state.get("title_visible") or "SKU缂栫爜" in anchors or "閿€鍞睘鎬?" in anchors)
    has_sku_batch_context = bool(state.get("sku_batch_visible"))
    has_sku_table_anchor = bool(state.get("sku_table_anchor_visible"))
    has_input_target = bool(state.get("market_input_visible") or state.get("jd_input_visible"))
    has_visible_price_row = int(state.get("visible_price_row_count", 0) or 0) >= 2
    return (
        has_sku_batch_context
        or has_sku_table_anchor
        or has_input_target
        or has_visible_price_row
        or (has_template_anchor and (has_title_context or has_price_anchor))
    )
    has_price_anchor = bool({"市场价", "京东价"} & anchors)
    has_template_anchor = bool(state.get("market_visible") or state.get("jd_visible"))
    has_title_context = bool(state.get("title_visible") or "SKU编码" in anchors or "销售属性" in anchors)
    has_sku_batch_context = bool(state.get("sku_batch_visible"))
    has_input_target = bool(state.get("market_input_visible") or state.get("jd_input_visible"))
    has_visible_price_row = int(state.get("visible_price_row_count", 0) or 0) >= 2
    return (
        has_sku_batch_context
        or has_input_target
        or has_visible_price_row
        or (has_template_anchor and (has_title_context or has_price_anchor))
    )


def _ensure_price_area_visible(locator=None, log=None, max_rounds: int = 3) -> Dict[str, Any]:
    import pyautogui

    locator = _get_locator(locator, log)
    last_state: Dict[str, Any] = {}
    for round_index in range(1, max_rounds + 1):
        restored = _ensure_basic_info_page(locator=locator, log=log)
        _debug_fill_live_context(f"price-round-{round_index}-after-basic-restore", locator=locator, log=log)
        if not restored:
            last_state = _collect_price_area_template_state(locator=locator, log=log)
            continue

        _scroll_to_sku_section(locator=locator, log=log)
        _debug_fill_live_context(f"price-round-{round_index}-after-sku-scroll", locator=locator, log=log)
        _scroll_price_fields_into_view(log=log)
        _debug_fill_live_context(f"price-round-{round_index}-after-price-scroll", locator=locator, log=log)
        time.sleep(0.5)

        state = _collect_price_area_template_state(locator=locator, log=log)
        if _price_area_ready(state):
            return {"success": True, "round": round_index, "state": state}

        if state.get("sku_batch_visible") or state.get("sku_table_anchor_visible"):
            _debug_log(
                log,
                f"[fill_product_info] price area fail-fast: sku table context detected without price targets round={round_index}",
            )
            return {
                "success": False,
                "reason": "sku_table_context_without_price_targets",
                "round": round_index,
                "state": state,
            }

        pyautogui.moveTo(1800, 1000)
        for step in range(1, 7):
            delta = -240 if step <= 3 else -320
            pyautogui.scroll(delta)
            time.sleep(0.3)
            _debug_fill_live_context(f"price-round-{round_index}-step-{step}", locator=locator, log=log)
            state = _collect_price_area_template_state(locator=locator, log=log)
            if _price_area_ready(state):
                _debug_log(log, f"[fill_product_info] price area visible after round={round_index} step={step}")
                return {"success": True, "round": round_index, "step": step, "state": state}
        last_state = state
    return {"success": False, "reason": "price_area_not_found", "state": last_state}


def _find_visible_price_edit_row(locator=None, log=None) -> list[tuple[Any, Any]]:
    locator = _get_locator(locator, log)
    candidates: list[tuple[Any, Any]] = []
    for element, _name, rect in _find_edit_elements(locator=locator, log=log):
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        # 价格行在不同缩放/滚动位置下可能偏上，过窄的 top 窗口会把真实输入框误判掉。
        if not (620 <= rect.top <= 1280):
            continue
        if rect.left < 520:
            continue
        if width < 55 or width > 520:
            continue
        if height < 20 or height > 80:
            continue
        candidates.append((element, rect))

    if len(candidates) < 2:
        return []

    rows: list[list[tuple[Any, Any]]] = []
    for item in sorted(candidates, key=lambda pair: (pair[1].top, pair[1].left)):
        rect = item[1]
        for row in rows:
            if abs(rect.top - row[0][1].top) <= 48:
                row.append(item)
                break
        else:
            rows.append([item])

    ranked_rows = sorted(
        rows,
        key=lambda row: (
            -len(row),
            -(sum(max(0, pair[1].left) for pair in row) / max(len(row), 1)),
        ),
    )
    best = ranked_rows[0] if ranked_rows else []
    if len(best) < 2:
        return []
    return sorted(best, key=lambda pair: pair[1].left)


def _debug_fill_live_context(stage: str, locator=None, log=None) -> Dict[str, Any]:
    page_state = _collect_fill_page_state(locator=locator, log=log)
    visible_row = _find_visible_price_edit_row(locator=locator, log=log)
    row_rects = [
        [rect.left, rect.top, rect.right, rect.bottom]
        for _element, rect in visible_row
    ]
    _debug_log(
        log,
        f"[fill_product_info] context stage={stage} page_state={page_state} visible_price_row={row_rects}",
    )
    return {
        "page_state": page_state,
        "visible_price_row": row_rects,
    }


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


def _find_price_input_target(label: str, locator=None, log=None):
    locator = _get_locator(locator, log)
    target = _find_named_control(label, ["Text", "Edit", "ComboBox"], locator=locator, log=log, top_range=(480, 1320))
    if target:
        _, _, label_rect = target
        label_center_x = (label_rect.left + label_rect.right) // 2
        candidates = []
        for element, _, rect in _find_edit_elements(locator=locator, log=log):
            if rect.top < label_rect.bottom - 10:
                continue
            if not (480 <= rect.top <= 1320):
                continue
            edit_center_x = (rect.left + rect.right) // 2
            if abs(edit_center_x - label_center_x) > 260:
                continue
            overlap = max(0, min(rect.right, label_rect.right) - max(rect.left, label_rect.left))
            horizontal_gap = 0
            if rect.right < label_rect.left:
                horizontal_gap = label_rect.left - rect.right
            elif rect.left > label_rect.right:
                horizontal_gap = rect.left - label_rect.right
            vertical_gap = abs(rect.top - label_rect.bottom)
            score = (
                0 if overlap > 0 else 1,
                horizontal_gap,
                vertical_gap,
                abs(edit_center_x - label_center_x),
                rect.left,
            )
            candidates.append((score, element, rect))

        if candidates:
            _, element, rect = sorted(candidates, key=lambda item: item[0])[0]
            return (element, rect)
    inferred_row = _find_visible_price_edit_row(locator=locator, log=log)
    if inferred_row:
        index_map = {
            "市场价": 0,
            "采购价": 1,
            "京东价": 2,
        }
        index = index_map.get(label)
        if index is not None:
            if len(inferred_row) >= 3 and index < len(inferred_row):
                return inferred_row[index]
            if len(inferred_row) == 2:
                if label == "市场价":
                    return inferred_row[0]
                if label == "京东价":
                    return inferred_row[-1]
    return None


def _merge_close_price_centers(candidates: list[tuple[str, tuple[int, int]]], tolerance: int = 120) -> Optional[Dict[str, Any]]:
    if not candidates:
        return None

    groups: list[list[tuple[str, tuple[int, int]]]] = []
    for source, point in candidates:
        x, y = point
        for group in groups:
            anchor_x = sum(item[1][0] for item in group) / len(group)
            anchor_y = sum(item[1][1] for item in group) / len(group)
            if abs(x - anchor_x) <= tolerance and abs(y - anchor_y) <= tolerance:
                group.append((source, point))
                break
        else:
            groups.append([(source, point)])

    ranked = sorted(groups, key=lambda group: (-len(group), sorted(item[0] for item in group)))
    best = ranked[0] if ranked else []
    if len(best) < 2:
        return None

    center_x = int(sum(item[1][0] for item in best) / len(best))
    center_y = int(sum(item[1][1] for item in best) / len(best))
    return {
        "center": (center_x, center_y),
        "sources": [item[0] for item in best],
    }


def _find_price_input_center(label: str, locator=None, log=None) -> Optional[tuple[int, int]]:
    locator = _get_locator(locator, log)
    target_match = _find_price_input_target(label, locator=locator, log=log)
    if target_match:
        _, rect = target_match
        return ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
    center_candidates: list[tuple[str, tuple[int, int]]] = []
    template_center = _find_price_input_center_by_template(label, locator=locator, log=log)
    if template_center:
        center_candidates.append(("template", template_center))
    inferred_row = _find_visible_price_edit_row(locator=locator, log=log)
    if inferred_row:
        row_index_map = {
            "甯傚満浠?": 0,
            "閲囪喘浠?": 1,
            "浜笢浠?": 2,
        }
        row_index = row_index_map.get(label)
        if row_index is not None:
            row_rect = None
            if len(inferred_row) >= 3 and row_index < len(inferred_row):
                row_rect = inferred_row[row_index][1]
            elif len(inferred_row) == 2:
                if row_index == 0:
                    row_rect = inferred_row[0][1]
                elif row_index == 2:
                    row_rect = inferred_row[-1][1]
            if row_rect:
                center_candidates.append(
                    ("visible_row", ((row_rect.left + row_rect.right) // 2, (row_rect.top + row_rect.bottom) // 2))
                )
    window = find_jingmai_uia_window(locator=locator, log=log)
    nearby_named = []
    if window:
        for candidate in iter_named_descendants(window, control_types=["Text", "Edit", "ComboBox", "Button"], limit=500):
            name = (candidate["name"] or "").strip()
            rect = candidate["rect"]
            if rect.top < 430 or rect.top > 1320:
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

    target = _find_named_control(label, ["Text", "Edit", "ComboBox"], locator=locator, log=log, top_range=(480, 1320))
    if not target:
        _debug_log(log, f"[fill_product_info] price probe label={label} target_control=NOT_FOUND")
        return None

    _, _, label_rect = target
    label_center_x = (label_rect.left + label_rect.right) // 2
    candidates = []
    for _, _, rect in _find_edit_elements(locator=locator, log=log):
        if rect.top < label_rect.bottom - 10:
            continue
        if not (480 <= rect.top <= 1320):
            continue
        edit_center_x = (rect.left + rect.right) // 2
        if abs(edit_center_x - label_center_x) > 260:
            continue
        overlap = max(0, min(rect.right, label_rect.right) - max(rect.left, label_rect.left))
        horizontal_gap = 0
        if rect.right < label_rect.left:
            horizontal_gap = label_rect.left - rect.right
        elif rect.left > label_rect.right:
            horizontal_gap = rect.left - label_rect.right
        vertical_gap = abs(rect.top - label_rect.bottom)
        score = (
            0 if overlap > 0 else 1,
            horizontal_gap,
            vertical_gap,
            abs(edit_center_x - label_center_x),
            rect.left,
        )
        candidates.append((score, rect))

    _debug_log(
        log,
        "[fill_product_info] price probe "
        f"label={label} label_rect={[label_rect.left, label_rect.top, label_rect.right, label_rect.bottom]} "
        f"edit_candidates={[[r.left, r.top, r.right, r.bottom] for _, r in candidates[:8]]}",
    )

    if candidates:
        _, rect = sorted(candidates, key=lambda item: item[0])[0]
        center_candidates.append(("nearby_edit", ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)))

    consensus = _merge_close_price_centers(center_candidates)
    if consensus:
        _debug_log(
            log,
            f"[fill_product_info] price click consensus label={label} center={consensus['center']} sources={consensus['sources']}",
        )
        return consensus["center"]

    if center_candidates:
        _debug_log(log, f"[fill_product_info] price click consensus unresolved label={label} candidates={center_candidates}")

    return None


def _ensure_basic_info_page(locator=None, log=None) -> bool:
    locator = _get_locator(locator, log)
    page_state = _collect_fill_page_state(locator=locator, log=log)
    if _fill_page_has_positive_markers(page_state, locator=locator, log=log):
        _debug_log(log, "[fill_product_info] basic info page confirmed from page-state context")
        return True
    if _fill_page_has_category_markers(page_state):
        _debug_log(log, "[fill_product_info] category page detected before restore")
        return False
    if _visible_text_contains("商品标题", locator=locator, log=log, top_range=(280, 520), left_range=(560, 1080)):
        return True
    if (
        _visible_text_contains("商品名称", locator=locator, log=log, top_range=(480, 980), left_range=(920, 1700))
        or _visible_text_contains("SKU", locator=locator, log=log, top_range=(480, 980), left_range=(900, 1700))
        or _visible_text_contains("销售属性", locator=locator, log=log, top_range=(480, 980), left_range=(900, 1700))
        or _visible_text_contains("市场价", locator=locator, log=log, top_range=(520, 1060), left_range=(960, 1880))
        or _visible_text_contains("京东价", locator=locator, log=log, top_range=(520, 1060), left_range=(960, 1880))
        or _find_visible_price_edit_row(locator=locator, log=log)
    ):
        _debug_log(log, "[fill_product_info] basic info page confirmed from sku/price context")
        return True

    target = _find_named_control("商品基本信息", ["Text", "Button", "Hyperlink"], locator=locator, log=log, top_range=(100, 220))
    if target:
        element, _, _ = target
        if click_uia_element(element, log=log):
            time.sleep(0.8)
            refreshed_state = _collect_fill_page_state(locator=locator, log=log)
            if (
                refreshed_state.get("title_top")
                or refreshed_state.get("product_name_mid")
                or refreshed_state.get("sku_mid")
                or refreshed_state.get("market_mid")
                or refreshed_state.get("jd_mid")
            ):
                _debug_log(log, "[fill_product_info] switched to basic info page via UIA fallback/page-state")
                return True
            success = _visible_text_contains("商品标题", locator=locator, log=log, top_range=(280, 520), left_range=(560, 1080))
            if success:
                _debug_log(log, "[fill_product_info] switched to basic info page via UIA fallback")
                return True

    success = False
    page_state = _collect_fill_page_state(locator=locator, log=log)
    if _fill_page_has_positive_markers(page_state, locator=locator, log=log):
        _debug_log(log, "[fill_product_info] basic info page confirmed after fallback state refresh")
        return True
    if _fill_page_has_category_markers(page_state):
        _debug_log(log, "[fill_product_info] category page detected from page-state, skip unsafe top-tab coordinate fallback")
        return False
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
    refreshed_state = _collect_fill_page_state(locator=locator, log=log)
    if (
        refreshed_state.get("title_top")
        or refreshed_state.get("product_name_mid")
        or refreshed_state.get("sku_mid")
        or refreshed_state.get("market_mid")
        or refreshed_state.get("jd_mid")
    ):
        _debug_log(log, "[fill_product_info] switched to basic info page via top-tab/page-state")
        return True
    success = _visible_text_contains("商品标题", locator=locator, log=log, top_range=(280, 520), left_range=(560, 1080))
    if success:
        _debug_log(log, "[fill_product_info] switched to basic info page via top-tab coordinates")
        return True

    if not success and _return_from_advanced_detail_editor(locator=locator, log=log):
        time.sleep(1.0)
        success = (
            _visible_text_contains("商品标题", locator=locator, log=log, top_range=(280, 520), left_range=(560, 1080))
            or _visible_text_contains("鍟嗗搧鏍囬", locator=locator, log=log, top_range=(280, 520), left_range=(560, 1080))
        )
        if success:
            _debug_log(log, "[fill_product_info] returned from advanced detail editor to merchant backend")
            return True

    _debug_log(log, f"[fill_product_info] basic info page restore success={success}")
    return success


def _is_category_selection_page(locator=None, log=None) -> bool:
    locator = _get_locator(locator, log)
    page_state = _collect_fill_page_state(locator=locator, log=log)
    if _fill_page_has_positive_markers(page_state, locator=locator, log=log):
        _debug_log(log, "[fill_product_info] category-page guard bypassed: product-info markers already visible")
        return False
    return _fill_page_has_category_markers(page_state) or bool(
        any(
            _visible_text_contains(text, locator=locator, log=log, top_range=(120, 320), left_range=(480, 1200))
            for text in _text_variants("类目选择发品")
        )
        or any(
            _visible_text_contains(text, locator=locator, log=log, top_range=(1180, 1380), left_range=(980, 1680))
            for text in _text_variants("下一步，完善其他商品信息")
        )
    )


def _is_advanced_detail_editor(locator=None, log=None) -> bool:
    locator = _get_locator(locator, log)
    def any_visible(*texts: str, top_range=(0, 180), left_range=(0, 360)) -> bool:
        return any(
            _visible_text_contains(text, locator=locator, log=log, top_range=top_range, left_range=left_range)
            for text in texts
            if text
        )

    has_return = any_visible(*_text_variants("返回商家后台"), top_range=(0, 120), left_range=(0, 260))
    has_jdzp = any_visible(*_text_variants("京东智铺"), *_text_variants("商家后台"), top_range=(0, 180), left_range=(0, 360))
    has_detail = any_visible(*_text_variants("详情"), top_range=(0, 180), left_range=(120, 520))
    has_high_editor = any_visible(*_text_variants("高级编辑"), top_range=(180, 420), left_range=(760, 1240))
    return bool(has_return and ((has_jdzp and has_detail) or has_high_editor))


def _return_from_advanced_detail_editor(locator=None, log=None) -> bool:
    locator = _get_locator(locator, log)
    if not _is_advanced_detail_editor(locator=locator, log=log):
        return False

    for label in _text_variants("返回商家后台"):
        target = _find_named_control(label, ["Button", "Hyperlink", "Text"], locator=locator, log=log, top_range=(0, 120), left_range=(0, 260))
        if target:
            element, _, _ = target
            if click_uia_element(element, log=log):
                return True

    return locator.click(70, 24, delay=0.5)


def _scroll_to_description_section(locator=None, log=None):
    import pyautogui

    _scroll_publish_page_to_top(locator=locator, log=log)
    _focus_publish_scroll_anchor(
        ["商品描述", "商品介绍", "上传图片"],
        locator=locator,
        log=log,
        page_hint="京麦商品详情编辑区，定位商品描述或上传图片入口后再滚动到详情区",
    )
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
    if mode_label == "代码编辑":
        return locator.click(1040, 316, delay=0.4)
    if mode_label == "图文编辑":
        return locator.click(918, 316, delay=0.4)
    return False


def _build_description_html(product: Dict[str, Any]) -> str:
    detail_content = str(product.get("detail_content", "") or product.get("description", "") or "").strip()
    if detail_content:
        return detail_content

    lines = []
    title = str(product.get("title", "") or "").strip()
    brand = str(product.get("brand", "") or product.get("品牌", "") or "").strip()
    model = str(product.get("model", "") or "").strip()
    unit = str(product.get("unit", "") or "").strip()
    notes = str(product.get("notes", "") or "").strip()
    size_parts = [str(product.get("length_mm", "") or "").strip(), str(product.get("width_mm", "") or "").strip(), str(product.get("height_mm", "") or "").strip()]
    size_parts = [part for part in size_parts if part]
    weight = str(product.get("weight_kg", "") or "").strip()

    if title:
        lines.append(f"<p>{title}</p>")
    if "basic_info" in normalized_groups and brand:
        lines.append(f"<p>品牌：{brand}</p>")
    if model:
        lines.append(f"<p>型号：{model}</p>")
    if size_parts:
        lines.append(f"<p>规格：{' x '.join(size_parts)} mm</p>")
    if weight:
        lines.append(f"<p>重量：{weight} kg</p>")
    if unit:
        lines.append(f"<p>销售单位：{unit}</p>")
    if notes:
        lines.append(f"<p>说明：{notes}</p>")
    return "".join(lines)


def _fill_description_code_editor(html: str, locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    _scroll_to_description_section(locator=locator, log=log)
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


def _prepare_upload_image(image_path: str, log=None) -> Dict[str, Any]:
    from PIL import Image

    source_path = Path(image_path).resolve()
    if not source_path.exists():
        return {"success": False, "message": f"image not found: {source_path}"}

    min_width = 750
    max_width = 1500
    max_height = 29999

    with Image.open(source_path) as img:
        original_width, original_height = img.size
        width = original_width
        height = original_height
        scale = 1.0

        if width < min_width:
            scale = min_width / float(width)
        elif width > max_width:
            scale = max_width / float(width)

        if scale != 1.0:
            width = max(1, int(round(width * scale)))
            height = max(1, int(round(height * scale)))
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        else:
            img = img.copy()

        if height > max_height:
            scale = max_height / float(height)
            width = max(1, int(round(width * scale)))
            height = max(1, int(round(height * scale)))
            img = img.resize((width, height), Image.Resampling.LANCZOS)

        upload_mode = "design" if height >= 1500 else "image"
        size_limit = 5 * 1024 * 1024 if upload_mode == "design" else 3 * 1024 * 1024
        prepared_dir = source_path.parent / "_upload_ready"
        prepared_dir.mkdir(parents=True, exist_ok=True)
        prepared_path = prepared_dir / f"{source_path.stem}_{upload_mode}.jpg"

        if img.mode != "RGB":
            img = img.convert("RGB")

        quality = 92
        while True:
            img.save(prepared_path, format="JPEG", quality=quality, optimize=True)
            if prepared_path.stat().st_size <= size_limit or quality <= 55:
                break
            quality -= 7

    prepared_size = prepared_path.stat().st_size
    _debug_log(
        log,
        f"[upload_image] prepared local image: src={source_path} out={prepared_path} "
        f"size={width}x{height} bytes={prepared_size} mode={upload_mode}",
    )
    return {
        "success": True,
        "source_path": str(source_path),
        "prepared_path": str(prepared_path),
        "upload_mode": upload_mode,
        "width": width,
        "height": height,
        "size_bytes": prepared_size,
        "size_limit_bytes": size_limit,
        "transformed": str(source_path) != str(prepared_path) or (original_width, original_height) != (width, height),
    }


def _submit_file_dialog_path(file_path: str, log=None, timeout: float = 8.0) -> Dict[str, Any]:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            from pywinauto import Desktop

            desktop = Desktop(backend="uia")
            dialogs = []
            for window in desktop.windows():
                try:
                    title = str(window.window_text() or "")
                    if window.is_visible() and any(token in title for token in ("打开", "Open")):
                        dialogs.append(window)
                except Exception:
                    continue
            if not dialogs:
                time.sleep(0.2)
                continue

            dialog = dialogs[-1]
            dialog.set_focus()
            time.sleep(0.2)

            edits = []
            try:
                edits = [edit for edit in dialog.descendants(control_type="Edit") if edit.is_visible() and edit.is_enabled()]
            except Exception:
                edits = []

            if edits:
                try:
                    edits[-1].set_edit_text(file_path)
                except Exception:
                    edits[-1].click_input()
                    time.sleep(0.1)
                    import pyautogui
                    import pyperclip

                    pyperclip.copy(file_path)
                    pyautogui.hotkey("ctrl", "a")
                    time.sleep(0.05)
                    pyautogui.hotkey("ctrl", "v")
            else:
                import pyautogui
                import pyperclip

                pyperclip.copy(file_path)
                pyautogui.hotkey("ctrl", "v")

            time.sleep(0.2)
            for button_name in ("打开(O)", "打开", "Open"):
                try:
                    button = dialog.child_window(title=button_name, control_type="Button")
                    if button.exists():
                        button.click_input()
                        return {"success": True, "method": "file-dialog", "dialog_title": str(dialog.window_text() or "")}
                except Exception:
                    continue

            import pyautogui

            pyautogui.press("enter")
            return {"success": True, "method": "file-dialog-enter", "dialog_title": str(dialog.window_text() or "")}
        except Exception:
            time.sleep(0.2)

    return {"success": False, "message": "file dialog not found"}


def _description_upload_prompt_visible(locator=None, log=None) -> bool:
    locator = _get_locator(locator, log)
    return bool(
        _visible_text_contains("璇蜂笂浼犲浘鐗囨垨瑙嗛", locator=locator, log=log, top_range=(260, 1180), left_range=(760, 1880))
        or _visible_text_contains("涓婁紶鍥剧墖", locator=locator, log=log, top_range=(260, 1180), left_range=(760, 1880))
    )


def _upload_description_image(image_path: str, locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    _scroll_to_description_section(locator=locator, log=log)
    _select_description_mode("图文编辑", locator=locator, log=log)
    target = None
    for label in _text_variants("上传图片"):
        target = _find_named_control(label, ["Button", "Hyperlink", "Text"], locator=locator, log=log, top_range=(260, 1180), left_range=(760, 1880))
        if target:
            break
    if target:
        element, _, _ = target
        click_uia_element(element, log=log)
        time.sleep(0.4)
    else:
        locator.click(1330, 816, delay=0.4)

    result = upload_image(image_path, locator=locator, log=log)
    result["field"] = "detail_image"
    return result


# Override mojibake versions with clean Chinese labels used by Jingmai UI.
def _submit_file_dialog_path(file_path: str, log=None, timeout: float = 8.0) -> Dict[str, Any]:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            from pywinauto import Desktop

            desktop = Desktop(backend="uia")
            dialogs = []
            for window in desktop.windows():
                try:
                    title = str(window.window_text() or "")
                    if window.is_visible() and any(token in title for token in ("打开", "Open")):
                        dialogs.append(window)
                except Exception:
                    continue
            if not dialogs:
                time.sleep(0.2)
                continue

            dialog = dialogs[-1]
            dialog.set_focus()
            time.sleep(0.2)

            edits = []
            try:
                edits = [edit for edit in dialog.descendants(control_type="Edit") if edit.is_visible() and edit.is_enabled()]
            except Exception:
                edits = []

            if edits:
                try:
                    edits[-1].set_edit_text(file_path)
                except Exception:
                    edits[-1].click_input()
                    time.sleep(0.1)
                    import pyautogui
                    import pyperclip

                    pyperclip.copy(file_path)
                    pyautogui.hotkey("ctrl", "a")
                    time.sleep(0.05)
                    pyautogui.hotkey("ctrl", "v")
            else:
                import pyautogui
                import pyperclip

                pyperclip.copy(file_path)
                pyautogui.hotkey("ctrl", "v")

            time.sleep(0.2)
            for button_name in ("打开(O)", "打开", "Open"):
                try:
                    button = dialog.child_window(title=button_name, control_type="Button")
                    if button.exists():
                        button.click_input()
                        return {"success": True, "method": "file-dialog", "dialog_title": str(dialog.window_text() or "")}
                except Exception:
                    continue

            import pyautogui

            pyautogui.press("enter")
            return {"success": True, "method": "file-dialog-enter", "dialog_title": str(dialog.window_text() or "")}
        except Exception:
            time.sleep(0.2)

    return {"success": False, "message": "file dialog not found"}


def _description_upload_prompt_visible(locator=None, log=None) -> bool:
    locator = _get_locator(locator, log)
    return bool(
        _visible_text_contains("请上传图片或视频", locator=locator, log=log, top_range=(260, 1180), left_range=(760, 1880))
        or _visible_text_contains("上传图片", locator=locator, log=log, top_range=(260, 1180), left_range=(760, 1880))
    )


def _select_description_mode(mode_label: str, locator=None, log=None) -> bool:
    locator = _get_locator(locator, log)
    target = _find_named_control(mode_label, ["Text", "Button", "RadioButton"], locator=locator, log=log, top_range=(300, 520), left_range=(820, 1180))
    if target:
        element, _, _ = target
        if click_uia_element(element, log=log):
            time.sleep(0.4)
            return True
    if mode_label == "代码编辑":
        return locator.click(1040, 316, delay=0.4)
    if mode_label == "图文编辑":
        return locator.click(918, 316, delay=0.4)
    return False


def _upload_description_image(image_path: str, locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    _scroll_to_description_section(locator=locator, log=log)
    _select_description_mode("图文编辑", locator=locator, log=log)
    target = _find_named_control("上传图片", ["Button", "Hyperlink", "Text"], locator=locator, log=log, top_range=(260, 1180), left_range=(760, 1880))
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
    target = _find_sku_product_name_target(locator=locator, log=log)
    if target:
        _, rect = target
        return ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
    _scroll_to_sku_section(locator=locator, log=log)
    for _, name, rect in _find_edit_elements(locator=locator, log=log):
        if rect.left < 1800 or not (520 <= rect.top <= 720):
            continue
        if name in {"请输入", ""} or "商品名称" in name:
            return ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
    return (2024, 613)


def _find_sku_product_name_target(locator=None, log=None):
    locator = _get_locator(locator, log)
    _scroll_to_sku_section(locator=locator, log=log)
    label_target = _find_named_control("商品名称", ["Text", "Edit", "ComboBox"], locator=locator, log=log, top_range=(480, 1180))
    if label_target:
        _, _, label_rect = label_target
        candidates = []
        for element, name, rect in _find_edit_elements(locator=locator, log=log):
            if not (460 <= rect.top <= 1180):
                continue
            if rect.left < max(900, label_rect.left - 120):
                continue
            if rect.top < label_rect.bottom - 20:
                continue
            score = (
                abs(rect.top - label_rect.bottom),
                abs(rect.left - label_rect.left),
                rect.left,
            )
            candidates.append((score, element, rect))
        if candidates:
            _, element, rect = sorted(candidates, key=lambda item: item[0])[0]
            return element, rect

    for elem, name, rect in _find_edit_elements(locator=locator, log=log):
        if rect.left < 1400 or not (460 <= rect.top <= 1180):
            continue
        if name in {"请输入", ""} or "商品名称" in name:
            return elem, rect
    return None


def _fill_sku_product_name_field(title: str, locator=None, log=None) -> Dict[str, Any]:
    """Fill SKU product name field using UIA set_edit_text (cross-session capable)."""
    locator = _get_locator(locator, log)
    
    # Find the SKU element with UIA (returns element, name, rect)
    target = _find_sku_product_name_target(locator=locator, log=log)
    element = target[0] if target else None
    
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

    _scroll_to_sku_section(locator=locator, log=log)
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
        if not item["success"]:
            expected_text = str(value)
            if expected_text and _visible_text_contains(
                expected_text,
                locator=locator,
                log=log,
                top_range=(820, 1040),
                left_range=(max(0, x - 180), x + 260),
            ):
                item.update(
                    {
                        "method": "visible-text-existing",
                        "write_success": True,
                        "verify_success": True,
                        "success": True,
                        "actual": expected_text,
                        "verification_method": "visible-text-existing",
                    }
                )
        if not item["success"]:
            item["verify_error"] = verify.get("message", f"{field} verify failed")
        details.append(item)
        time.sleep(0.2)
    return details


def _fill_sku_pricing_fields_v3(product: Dict[str, Any], locator=None, log=None) -> list[Dict[str, Any]]:
    locator = _get_locator(locator, log)
    _ensure_basic_info_page(locator=locator, log=log)
    _scroll_to_sku_section(locator=locator, log=log)
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
        if visibility.get("reason") != "sku_table_context_without_price_targets":
            seek_result = _seek_price_area(locator=locator, log=log)
            if seek_result.get("success"):
                visibility = _ensure_price_area_visible(locator=locator, log=log, max_rounds=1)
            if not visibility.get("success") and seek_result.get("success"):
                visibility = {"success": True, "state": visibility.get("state") or seek_result}
    if not visibility.get("success"):
        details.append(
            {
                "field": "price_area_anchor",
                "method": "template-state-guard",
                "write_success": False,
                "verify_success": False,
                "success": False,
                "verify_error": (
                    f"price area not visible ({visibility.get('reason', 'unknown')}): "
                    f"{visibility.get('state', {})}"
                ),
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
    purchase_price = product.get("purchase_price")
    if purchase_price in (None, "") and product.get("jd_price") not in (None, ""):
        try:
            purchase_price = round(Decimal(str(product.get("jd_price"))) * Decimal("0.95"), 2)
        except Exception:
            purchase_price = product.get("purchase_price")

    field_specs = [
        ("market_price", "市场价", product.get("market_price"), (1278, 603)),
        ("purchase_price", "采购价", purchase_price, (1388, 603)),
        ("jd_price", "京东价", product.get("jd_price"), (1518, 603)),
    ]

    for field, label, value, fallback_center in field_specs:
        if value in (None, ""):
            continue
        x, y = fallback_center
        target_match = _find_price_input_target(label, locator=locator, log=log) if label else None
        if field == "purchase_price" and not target_match:
            _debug_log(log, "[fill_product_info] purchase_price target not found, skip optional derived field")
            continue
        if target_match:
            element, rect = target_match
            x, y = ((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
            try:
                element.set_edit_text(str(value))
                time.sleep(0.15)
                write_result = {"success": True, "method": "uia-set-edit-text"}
                verify = _verify_uia_edit_value(field, value, element)
            except Exception:
                write_result = {"success": False, "method": "uia-set-edit-text"}
                verify = {"success": False, "message": "uia write failed", "method": "uia-set-edit-text"}
        else:
            center = None
            if label:
                center = _find_price_input_center(label, locator=locator, log=log)
            if not center:
                details.append(
                    {
                        "field": field,
                        "method": "price-target-guard",
                        "write_success": False,
                        "verify_success": False,
                        "success": False,
                        "expected": str(value),
                        "actual": "",
                        "verify_error": (
                            f"price target not found ({label}) after sku context: "
                            f"{visibility.get('state', {})}"
                        ),
                    }
                )
                if field != "purchase_price":
                    return details
                continue
            x, y = center
            _debug_log(log, f"[fill_product_info] click price field {field} at ({x}, {y}) with hover-then-double-click")
            _hover_then_click(x, y, clicks=2, interval=0.1, delay=0.2)
            write_result = _write_active_text(value, clear=True)
            verify = _verify_text_field(locator, field, x, y, value)
        if not verify.get("success") and target_match:
            _debug_log(log, f"[fill_product_info] price field {field} ui a verify failed, fallback to active write")
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


def _flatten_required_visual_fields(required_visual_fields: Any) -> Dict[str, Dict[str, Any]]:
    flattened: Dict[str, Dict[str, Any]] = {}
    if not isinstance(required_visual_fields, dict):
        return flattened
    for group_name, items in required_visual_fields.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            field = str(item.get("field", "") or "").strip()
            if not field:
                continue
            flattened[field] = {
                "group": str(group_name or "").strip(),
                "label": str(item.get("label", "") or "").strip(),
                "value": item.get("value"),
            }
    return flattened


def _coerce_visual_field_value(field: str, value: Any) -> Any:
    text = str(value or "").strip()
    if not text:
        return value
    if field in {"jd_price", "market_price", "purchase_price"}:
        normalized = _normalize_numeric_text(text)
        return normalized if normalized is not None else value
    if field == "sales_unit":
        alias_map = {
            "1个": "个",
            "一只": "个",
            "1只": "个",
            "pcs": "个",
            "pc": "个",
        }
        return alias_map.get(text.lower(), alias_map.get(text, text))
    return text


def _is_placeholder_text(value: Any) -> bool:
    text = str(value or "").strip().lower()
    return text in {"", "无", "暂无", "-", "/", "none", "n/a", "na", "未填写", "待补充"}


def _extract_title_attribute_hints(value: Any) -> Dict[str, str]:
    text = str(value or "").strip()
    if not text:
        return {}

    hints: Dict[str, str] = {}

    socket_match = re.search(r"[【\[]?\s*(\d+)\s*位(?:】|\])?", text)
    if socket_match:
        hints["socket_config"] = f"{socket_match.group(1)}位"

    cable_match = re.search(r"总控\s*(\d+(?:\.\d+)?)\s*米", text, re.I)
    if cable_match is None:
        cable_match = re.search(r"(\d+(?:\.\d+)?)\s*米", text, re.I)
    if cable_match:
        hints["cable_length"] = f"{cable_match.group(1)}米"

    if any(keyword in text for keyword in ("插座", "排插", "插排", "转换器")):
        hints.setdefault("rated_voltage", "250V")
        hints.setdefault("current", "10A")

    model_candidates = re.findall(r"([A-Z]{1,6}-?\d{2,}[A-Z0-9-]*)", text.upper())
    if model_candidates:
        hints["model"] = model_candidates[-1]

    return hints


def _infer_required_product_values(product: Dict[str, Any], required_visual_fields: Any = None) -> Dict[str, Any]:
    enriched = dict(product or {})
    attributes = dict(enriched.get("attributes") or {})
    inferred_values: Dict[str, Any] = {}
    unresolved_required_fields: list[str] = []
    visual_map = _flatten_required_visual_fields(required_visual_fields)

    def assign_if_missing(field: str, value: Any) -> None:
        if value in (None, "", []):
            return
        current = enriched.get(field)
        if current not in (None, "", []):
            return
        enriched[field] = value
        inferred_values[field] = value

    def first_text(*values: Any) -> str:
        for value in values:
            text = str(value or "").strip()
            if text:
                return text
        return ""

    for field in ("jd_price", "market_price", "purchase_price", "sales_unit", "packing_list", "package_type"):
        visual_value = (visual_map.get(field) or {}).get("value")
        coerced_value = _coerce_visual_field_value(field, visual_value)
        assign_if_missing(field, coerced_value)

    assign_if_missing("jd_price", enriched.get("price"))
    assign_if_missing("market_price", enriched.get("jd_price") or enriched.get("price"))
    if enriched.get("purchase_price") in (None, "") and enriched.get("jd_price") not in (None, ""):
        try:
            purchase_price = float(round(Decimal(str(enriched.get("jd_price"))) * Decimal("0.95"), 2))
        except Exception:
            purchase_price = None
        assign_if_missing("purchase_price", purchase_price)

    if attributes.get("current") in (None, "") and attributes.get("rated_current") not in (None, ""):
        attributes["current"] = attributes.get("rated_current")
        inferred_values.setdefault("current", attributes["current"])
    title_hint_source = " ".join(
        part
        for part in [
            str(enriched.get("title", "") or ""),
            str(enriched.get("category", "") or ""),
            str(enriched.get("description", "") or ""),
        ]
        if str(part or "").strip()
    )
    title_hints = _extract_title_attribute_hints(title_hint_source)

    if attributes.get("current") in (None, ""):
        current_value = first_text(
            attributes.get("current"),
            enriched.get("current"),
            enriched.get("rated_current"),
            (visual_map.get("current") or {}).get("value"),
            title_hints.get("current"),
        )
        if current_value:
            attributes["current"] = current_value
            inferred_values.setdefault("current", current_value)

    for field in ("socket_config", "rated_voltage", "cable_length"):
        visual_value = _coerce_visual_field_value(field, (visual_map.get(field) or {}).get("value"))
        candidate = first_text(
            attributes.get(field),
            enriched.get(field),
            visual_value,
            title_hints.get(field),
        )
        if candidate:
            attributes.setdefault(field, candidate)
            assign_if_missing(field, candidate)
            inferred_values.setdefault(field, candidate)

    model_hint = first_text(
        (visual_map.get("model") or {}).get("value"),
        title_hints.get("model"),
    )
    if model_hint and _is_placeholder_text(enriched.get("model")):
        enriched["model"] = model_hint
        inferred_values.setdefault("model", model_hint)

    if attributes:
        enriched["attributes"] = attributes

    unit = first_text(enriched.get("sales_unit"), enriched.get("unit"), (visual_map.get("sales_unit") or {}).get("value"))
    if not unit and ("sales_unit" in visual_map or "sales_unit" in str(required_visual_fields)):
        unit = "个"
    assign_if_missing("sales_unit", unit)

    packing_list = first_text(
        enriched.get("packing_list"),
        enriched.get("notes"),
        (visual_map.get("packing_list") or {}).get("value"),
    )
    if not packing_list:
        title_or_model = first_text(enriched.get("title"), enriched.get("model"), enriched.get("brand"), "商品")
        packing_list = f"{title_or_model} x1"
    assign_if_missing("packing_list", packing_list)

    package_type = first_text(enriched.get("package_type"), (visual_map.get("package_type") or {}).get("value"))
    if not package_type:
        title_and_notes = " ".join(
            part
            for part in [
                str(enriched.get("title", "") or ""),
                str(enriched.get("notes", "") or ""),
                str(enriched.get("category", "") or ""),
            ]
            if str(part or "").strip()
        )
        for keyword, value in (
            ("袋", "袋装"),
            ("盒", "盒装"),
            ("箱", "箱装"),
            ("桶", "桶装"),
            ("罐", "罐装"),
            ("插座", "盒装"),
            ("开关", "盒装"),
        ):
            if keyword in title_and_notes:
                package_type = value
                break
    assign_if_missing("package_type", package_type)

    warranty_period = first_text(enriched.get("warranty_period"), (visual_map.get("warranty_period") or {}).get("value"))
    if not warranty_period:
        source_text = " ".join(
            part
            for part in [
                str(enriched.get("notes", "") or ""),
                str(enriched.get("description", "") or ""),
                str(enriched.get("detail_content", "") or ""),
            ]
            if str(part or "").strip()
        )
        match = re.search(r"(\d+)\s*(年|个月|月|天)\s*(质保|保修)?", source_text)
        if match:
            number, unit_token, _ = match.groups()
            warranty_period = f"{number}{unit_token}"
    assign_if_missing("warranty_period", warranty_period)

    special_delivery = first_text(
        enriched.get("special_delivery_mark"),
        (visual_map.get("special_delivery_mark") or {}).get("value"),
    )
    if not special_delivery:
        source_text = " ".join(
            part
            for part in [
                str(enriched.get("notes", "") or ""),
                str(enriched.get("title", "") or ""),
                str(enriched.get("category", "") or ""),
            ]
            if str(part or "").strip()
        )
        if any(keyword in source_text for keyword in ("冷链", "冷藏", "冷冻", "易碎", "危险", "液体", "粉末")):
            special_delivery = "特殊商品"
    assign_if_missing("special_delivery_mark", special_delivery)

    for field in visual_map:
        value = enriched.get(field)
        if field == "current" and value in (None, ""):
            value = attributes.get("current")
        if value in (None, "", []):
            unresolved_required_fields.append(field)

    return {
        "product": enriched,
        "inferred_values": inferred_values,
        "unresolved_required_fields": unresolved_required_fields,
        "required_visual_map": visual_map,
    }


def _activate_publish_section_tab(*labels: str, locator=None, log=None) -> bool:
    locator = _get_locator(locator, log)
    search_windows = [
        ((60, 220), (40, 980)),
        ((220, 620), (40, 980)),
        ((520, 1400), (40, 980)),
    ]
    for label in labels:
        text = str(label or "").strip()
        if not text:
            continue
        for top_range, left_range in search_windows:
            target = _find_named_control(
                text,
                ["Text", "Button", "Hyperlink"],
                locator=locator,
                log=log,
                top_range=top_range,
                left_range=left_range,
            )
            if not target:
                continue
            element, _, _ = target
            if click_uia_element(element, log=log):
                time.sleep(0.5)
                return True
    return False


def _fill_labeled_dropdown_field(
    field: str,
    label_keywords: list[str],
    value: Any,
    *,
    locator=None,
    log=None,
    top_range: tuple[int, int] | None = None,
    preferred_keywords: Optional[list[str]] = None,
) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    coords = _find_labeled_dropdown_center(label_keywords, locator=locator, log=log, top_range=top_range)
    if not coords:
        return {
            "field": field,
            "method": "dynamic-label-search",
            "write_success": False,
            "verify_success": False,
            "success": False,
            "verify_error": f"{field} dropdown anchor not found",
        }
    result = _select_dropdown_option(
        str(value),
        coords[0],
        coords[1],
        locator=locator,
        log=log,
        preferred_keywords=preferred_keywords or label_keywords,
        top_range=(max(240, coords[1] - 120), coords[1] + 260),
    )
    verify_success = result.get("success", False) and _dropdown_selection_confirmed(
        str(value),
        locator=locator,
        log=log,
        top_range=(max(240, coords[1] - 80), coords[1] + 100),
        left_range=(max(0, coords[0] - 420), coords[0] + 420),
    )
    if not verify_success and result.get("success", False):
        validation_still_visible = any(
            _visible_text_contains(
                f"{label}不能为空",
                locator=locator,
                log=log,
                top_range=(max(240, coords[1] - 60), coords[1] + 140),
                left_range=(max(0, coords[0] - 520), coords[0] + 520),
            )
            for label in label_keywords
            if str(label or "").strip()
        )
        if not validation_still_visible and (
            field in {"sales_unit", "package_type", "special_delivery_mark", "warranty_period"}
            or len(str(value)) <= 2
        ):
            verify_success = True
    payload = {
        "field": field,
        "method": result.get("method", "select_dropdown"),
        "write_success": result.get("success", False),
        "verify_success": verify_success,
        "success": result.get("success", False) and verify_success,
        "expected": str(value),
        "actual": str(value) if verify_success else "",
    }
    if not payload["success"]:
        payload["verify_error"] = result.get("message", f"{field} verify failed")
    return payload


def _fill_labeled_text_field(
    field: str,
    label_keywords: list[str],
    value: Any,
    *,
    locator=None,
    log=None,
    top_range: tuple[int, int] | None = None,
) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    coords = _find_labeled_dropdown_center(
        label_keywords,
        locator=locator,
        log=log,
        top_range=top_range,
        preferred_types=("Edit", "ComboBox", "Button"),
    )
    fallback_coords = coords if coords else None
    keyword = label_keywords[0] if label_keywords else field
    result = _fill_named_edit_field_v2(
        field,
        keyword,
        value,
        locator=locator,
        log=log,
        top_range=top_range,
        fallback_coords=fallback_coords,
    )
    if result.get("success") or not fallback_coords:
        return result
    verify = _verify_text_field(locator, field, fallback_coords[0], fallback_coords[1], value, prefer_uia=False)
    result["verify_success"] = verify.get("success", False)
    result["success"] = bool(result.get("write_success", False) and verify.get("success", False))
    result["actual"] = verify.get("actual", result.get("actual", ""))
    result["verification_method"] = verify.get("method", result.get("verification_method", ""))
    result["compare_mode"] = verify.get("compare_mode", result.get("compare_mode", ""))
    if not verify.get("success"):
        result["verify_error"] = verify.get("message", result.get("verify_error", f"{field} verify failed"))
    return result


def _normalize_hazardous_goods_value(value: Any) -> list[str]:
    if value in (None, "", False, 0):
        return []
    if isinstance(value, (list, tuple, set)):
        raw_items = list(value)
    else:
        raw_items = re.split(r"[，,、/;\n]+", str(value or ""))
    normalized = [str(item or "").strip() for item in raw_items if str(item or "").strip()]
    if len(normalized) == 1 and normalized[0] in {"否", "无", "不是", "非危险商品", "普通商品"}:
        return []
    return normalized


def _fill_hazardous_goods_field(value: Any, *, locator=None, log=None) -> Dict[str, Any]:
    labels = _normalize_hazardous_goods_value(value)
    if not labels:
        return {
            "field": "hazardous_goods",
            "method": "no-selection",
            "write_success": True,
            "verify_success": True,
            "success": True,
            "expected": "",
            "actual": "",
        }

    window = find_jingmai_uia_window(locator=locator, log=log)
    if not window:
        return {
            "field": "hazardous_goods",
            "method": "uia-checkbox",
            "write_success": False,
            "verify_success": False,
            "success": False,
            "verify_error": "hazardous goods checkbox area not found",
        }

    clicked: list[str] = []
    for label in labels:
        target = _find_named_control(label, ["CheckBox", "Text", "Button"], locator=locator, log=log, top_range=(520, 1320))
        if not target:
            return {
                "field": "hazardous_goods",
                "method": "uia-checkbox",
                "write_success": False,
                "verify_success": False,
                "success": False,
                "verify_error": f"hazardous goods option not found: {label}",
            }
        element, _, _ = target
        if not click_uia_element(element, log=log):
            return {
                "field": "hazardous_goods",
                "method": "uia-checkbox",
                "write_success": False,
                "verify_success": False,
                "success": False,
                "verify_error": f"hazardous goods option click failed: {label}",
            }
        clicked.append(label)
        time.sleep(0.15)

    return {
        "field": "hazardous_goods",
        "method": "uia-checkbox",
        "write_success": True,
        "verify_success": True,
        "success": True,
        "expected": ",".join(labels),
        "actual": ",".join(clicked),
    }


def _fill_required_logistics_fields(
    product: Dict[str, Any],
    required_visual_fields=None,
    locator=None,
    log=None,
    explicit_fields: Optional[set[str]] = None,
) -> list[Dict[str, Any]]:
    locator = _get_locator(locator, log)
    _activate_publish_section_tab("商品物流", "商品售后及其他", locator=locator, log=log)
    _focus_publish_scroll_anchor(
        ["销售单位", "商品包装", "包装清单", "商品物流", "商品售后及其他"],
        locator=locator,
        log=log,
        page_hint="京麦商品发布页物流与售后区域，定位销售单位、商品包装或包装清单字段",
    )
    required_map = _flatten_required_visual_fields(required_visual_fields)
    explicit_fields = explicit_fields or set()
    specs = [
        {
            "field": "shelf_life_days",
            "kind": "text",
            "labels": ["保质期（天）", "保质期(天)", "保质期"],
            "value": product.get("shelf_life_days") or product.get("shelf_life"),
        },
        {
            "field": "sales_unit",
            "kind": "text",
            "labels": ["销售单位"],
            "value": product.get("sales_unit") or product.get("unit"),
        },
        {
            "field": "package_spec",
            "kind": "text",
            "labels": ["包装规格"],
            "value": product.get("package_spec"),
        },
        {
            "field": "package_spec_unit",
            "kind": "dropdown",
            "labels": ["包装规格单位"],
            "value": product.get("package_spec_unit"),
        },
        {
            "field": "package_type",
            "kind": "dropdown",
            "labels": ["商品包装"],
            "value": product.get("package_type"),
        },
        {
            "field": "special_delivery_mark",
            "kind": "dropdown",
            "labels": ["特殊发货时效标记"],
            "value": product.get("special_delivery_mark"),
        },
        {
            "field": "hazardous_goods",
            "kind": "custom",
            "labels": ["是否危险商品"],
            "value": product.get("hazardous_goods"),
        },
        {
            "field": "packing_list",
            "kind": "text",
            "labels": ["包装清单"],
            "value": product.get("packing_list") or product.get("notes"),
        },
        {
            "field": "warranty_period",
            "kind": "dropdown",
            "labels": ["质保期"],
            "value": product.get("warranty_period"),
        },
    ]
    results: list[Dict[str, Any]] = []
    for spec in specs:
        field = spec["field"]
        required_visual = required_map.get(field) or {}
        should_try = field in required_map or field in explicit_fields
        if not should_try:
            continue
        value = spec["value"]
        if spec["kind"] != "custom" and value in (None, ""):
            continue
        if spec["kind"] == "dropdown":
            result = _fill_labeled_dropdown_field(
                field,
                spec["labels"],
                value,
                locator=locator,
                log=log,
                top_range=(520, 1320),
                preferred_keywords=spec["labels"],
            )
            if not result.get("success") and field in {"package_type", "warranty_period", "special_delivery_mark"}:
                current_text = str(value).strip()
                if current_text and _visible_text_contains(
                    current_text,
                    locator=locator,
                    log=log,
                    top_range=(520, 1380),
                    left_range=(900, 2300),
                ):
                    result = {
                        "field": field,
                        "method": "visible-text-existing",
                        "write_success": True,
                        "verify_success": True,
                        "success": True,
                        "expected": current_text,
                        "actual": current_text,
                    }
        elif spec["kind"] == "custom":
            result = _fill_hazardous_goods_field(value, locator=locator, log=log)
        else:
            result = _fill_labeled_text_field(
                field,
                spec["labels"],
                value,
                locator=locator,
                log=log,
                top_range=(520, 1320),
            )
            if not result.get("success") and field == "packing_list":
                current_text = str(value).strip()
                if current_text and _visible_text_contains(
                    current_text,
                    locator=locator,
                    log=log,
                    top_range=(520, 1380),
                    left_range=(900, 2300),
                ):
                    result = {
                        "field": field,
                        "method": "visible-text-existing",
                        "write_success": True,
                        "verify_success": True,
                        "success": True,
                        "expected": current_text,
                        "actual": current_text,
                    }
            if not result.get("success") and field in {"sales_unit", "shelf_life_days", "package_spec"}:
                current_text = str(value).strip()
                if current_text and _visible_text_contains(
                    current_text,
                    locator=locator,
                    log=log,
                    top_range=(520, 1380),
                    left_range=(900, 2300),
                ):
                    result = {
                        "field": field,
                        "method": "visible-text-existing",
                        "write_success": True,
                        "verify_success": True,
                        "success": True,
                        "expected": current_text,
                        "actual": current_text,
                    }
        if not result.get("success"):
            _activate_publish_section_tab("商品物流", "商品售后及其他", locator=locator, log=log)
            _focus_publish_scroll_anchor(
                spec["labels"],
                locator=locator,
                log=log,
                page_hint="浜害鍟嗗搧鍙戝竷椤典腑鍥炲埌褰撳墠澶辫触瀛楁闄勮繎锛岄噸璇曞畾浣嶅苟濉啓",
            )
            time.sleep(0.2)
            retry_result = (
                _fill_labeled_dropdown_field(
                    field,
                    spec["labels"],
                    value,
                    locator=locator,
                    log=log,
                    top_range=(520, 1380),
                    preferred_keywords=spec["labels"],
                )
                if spec["kind"] == "dropdown"
                else _fill_labeled_text_field(
                    field,
                    spec["labels"],
                    value,
                    locator=locator,
                    log=log,
                    top_range=(520, 1380),
                )
            )
            if retry_result.get("success"):
                result = retry_result
        results.append(result)
        time.sleep(0.2)
    return results


def _fill_required_sales_attributes_fields(
    product: Dict[str, Any],
    required_visual_fields=None,
    locator=None,
    log=None,
    explicit_fields: Optional[set[str]] = None,
) -> list[Dict[str, Any]]:
    locator = _get_locator(locator, log)
    required_map = _flatten_required_visual_fields(required_visual_fields)
    explicit_fields = explicit_fields or set()
    attribute_values = _collect_attribute_values(product)
    specs = [
        {
            "field": "current",
            "labels": ["电流", "请填写电流"],
            "value": attribute_values.get("current") or product.get("current"),
        },
        {
            "field": "rated_voltage",
            "labels": ["电压", "请输入电压"],
            "value": attribute_values.get("rated_voltage") or product.get("rated_voltage") or product.get("voltage"),
        },
        {
            "field": "lead_time",
            "labels": ["货期", "请输入货期"],
            "value": product.get("lead_time") or product.get("delivery_time"),
        },
    ]
    active_specs = [
        spec
        for spec in specs
        if (spec["field"] in required_map or spec["field"] in explicit_fields) and spec["value"] not in (None, "")
    ]
    if not active_specs:
        return []

    _activate_publish_section_tab("销售属性", "SKU属性", locator=locator, log=log)
    _focus_publish_scroll_anchor(
        ["销售属性", "SKU属性", "电流", "电压", "货期", "请填写电流"],
        locator=locator,
        log=log,
        page_hint="京麦商品发布页销售属性区域，定位电流、电压、货期列或SKU属性表格",
    )
    results: list[Dict[str, Any]] = []
    for spec in active_specs:
        result = _fill_labeled_text_field(
            spec["field"],
            spec["labels"],
            spec["value"],
            locator=locator,
            log=log,
            top_range=(1120, 1380),
        )
        if not result.get("success"):
            current_text = str(spec["value"]).strip()
            if current_text and _visible_text_contains(
                current_text,
                locator=locator,
                log=log,
                top_range=(1000, 1450),
                left_range=(900, 2300),
            ):
                result = {
                    "field": spec["field"],
                    "method": "visible-text-existing",
                    "write_success": True,
                    "verify_success": True,
                    "success": True,
                    "expected": current_text,
                    "actual": current_text,
                }
        results.append(result)
        time.sleep(0.2)
    return results

    _activate_publish_section_tab("销售属性", "SKU属性", locator=locator, log=log)
    _focus_publish_scroll_anchor(
        ["销售属性", "SKU属性", "电流", "请填写电流"],
        locator=locator,
        log=log,
        page_hint="京麦商品发布页销售属性区域，定位电流列或SKU属性表格",
    )
    result = _fill_labeled_text_field(
        "current",
        ["电流", "请填写电流"],
        current_value,
        locator=locator,
        log=log,
        top_range=(1120, 1380),
    )
    if not result.get("success"):
        current_text = str(current_value).strip()
        if current_text and _visible_text_contains(
            current_text,
            locator=locator,
            log=log,
            top_range=(1000, 1450),
            left_range=(900, 2300),
        ):
            result = {
                "field": "current",
                "method": "visible-text-existing",
                "write_success": True,
                "verify_success": True,
                "success": True,
                "expected": current_text,
                "actual": current_text,
            }
    return [result]


def _resolve_sku_image_values(product: Dict[str, Any]) -> Dict[str, str]:
    images = product.get("images")
    if not isinstance(images, list):
        images = []
    normalized_images = [str(item).strip() for item in images if str(item).strip()]
    return {
        "sku_square_image": str(
            product.get("sku_square_image")
            or product.get("square_image")
            or product.get("sku_image")
            or product.get("image")
            or (normalized_images[0] if normalized_images else "")
        ).strip(),
        "sku_transparent_image": str(
            product.get("sku_transparent_image")
            or product.get("transparent_image")
            or product.get("transparent_image_path")
            or ""
        ).strip(),
    }


def _click_sku_image_upload_anchor(
    field: str,
    label_keywords: list[str],
    *,
    locator=None,
    log=None,
) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    header = None
    for label in label_keywords:
        header = _find_named_control(
            label,
            ["Text", "Button", "Hyperlink"],
            locator=locator,
            log=log,
            top_range=(640, 980),
        )
        if header:
            break
    if not header:
        return {
            "field": field,
            "method": "sku-image-anchor",
            "success": False,
            "message": f"{field} upload header not found",
        }

    _, _, rect = header
    anchor_x = rect.left + max(35, min(60, max(1, (rect.right - rect.left) // 2)))
    anchor_y = rect.bottom + 72
    plus_target = _find_named_control(
        "+",
        ["Text", "Button", "Hyperlink"],
        locator=locator,
        log=log,
        top_range=(rect.bottom + 10, rect.bottom + 180),
        left_range=(max(0, rect.left - 40), rect.right + 140),
    )
    if plus_target:
        element, _, plus_rect = plus_target
        plus_center = ((plus_rect.left + plus_rect.right) // 2, (plus_rect.top + plus_rect.bottom) // 2)
        consensus = _merge_close_price_centers(
            [("uia_plus", plus_center), ("label_relative", (anchor_x, anchor_y))],
            tolerance=110,
        )
        if consensus:
            clicked = locator.click(consensus["center"][0], consensus["center"][1], delay=0.3)
            if clicked:
                time.sleep(0.25)
                return {
                    "field": field,
                    "method": "anchor-consensus-click",
                    "success": True,
                    "x": consensus["center"][0],
                    "y": consensus["center"][1],
                    "sources": consensus["sources"],
                }
        if click_uia_element(element, log=log):
            time.sleep(0.25)
            return {"field": field, "method": "uia-plus-button", "success": True}

    clicked = locator.click(anchor_x, anchor_y, delay=0.3)
    return {
        "field": field,
        "method": "label-relative-click",
        "success": bool(clicked),
        "x": anchor_x,
        "y": anchor_y,
        **({"message": f"{field} upload anchor click failed"} if not clicked else {}),
    }


def _fill_required_sku_image_fields(
    product: Dict[str, Any],
    required_visual_fields=None,
    locator=None,
    log=None,
    explicit_fields: Optional[set[str]] = None,
) -> list[Dict[str, Any]]:
    locator = _get_locator(locator, log)
    required_map = _flatten_required_visual_fields(required_visual_fields)
    explicit_fields = explicit_fields or set()
    image_values = _resolve_sku_image_values(product)
    specs = [
        {
            "field": "sku_square_image",
            "labels": ["方图"],
            "value": image_values.get("sku_square_image", ""),
            "request_keys": {"sku_square_image", "square_image", "sku_image", "image"},
        },
        {
            "field": "sku_transparent_image",
            "labels": ["透图"],
            "value": image_values.get("sku_transparent_image", ""),
            "request_keys": {"sku_transparent_image", "transparent_image", "transparent_image_path"},
        },
    ]
    active_specs = [
        spec
        for spec in specs
        if spec["value"]
        and any(key in required_map or key in explicit_fields for key in spec["request_keys"])
    ]
    if not active_specs:
        return []

    _activate_publish_section_tab("SKU图片信息", locator=locator, log=log)
    _focus_publish_scroll_anchor(
        ["SKU图片信息", "方图", "透图", "图片调节"],
        locator=locator,
        log=log,
        page_hint="京麦商品发布页 SKU 图片信息区域，定位方图和透图上传入口。",
    )
    results: list[Dict[str, Any]] = []
    for spec in active_specs:
        anchor_result = _click_sku_image_upload_anchor(
            spec["field"],
            spec["labels"],
            locator=locator,
            log=log,
        )
        if not anchor_result.get("success"):
            results.append(
                {
                    "field": spec["field"],
                    "method": anchor_result.get("method", "sku-image-anchor"),
                    "write_success": False,
                    "verify_success": False,
                    "success": False,
                    "expected": spec["value"],
                    "verify_error": anchor_result.get("message", f"{spec['field']} upload anchor not found"),
                }
            )
            continue

        upload_result = upload_image(spec["value"], locator=locator, log=log)
        success = bool(upload_result.get("success"))
        results.append(
            {
                "field": spec["field"],
                "method": f"{anchor_result.get('method', 'sku-image-anchor')}+{upload_result.get('method', 'upload_image')}",
                "write_success": success,
                "verify_success": success,
                "success": success,
                "expected": spec["value"],
                "actual": upload_result.get("prepared_image") or upload_result.get("image") or spec["value"],
                **({"verify_error": upload_result.get("message", f"{spec['field']} upload failed")} if not success else {}),
            }
        )
        time.sleep(0.25)
    return results


def _normalize_fill_result(item: Optional[Dict[str, Any]], section: str) -> Dict[str, Any]:
    payload = dict(item or {})
    payload["section"] = section
    success = bool(payload.get("success", False))
    payload["write_success"] = bool(payload.get("write_success", success))
    payload["verify_success"] = bool(payload.get("verify_success", success))
    payload["success"] = success
    if not payload.get("error") and payload.get("verify_error"):
        payload["error"] = payload["verify_error"]
    if not payload.get("verify_error") and not payload["success"]:
        field = payload.get("field") or section
        payload["verify_error"] = payload.get("error") or f"{field} failed"
    return payload


def _append_fill_results(results: list[Dict[str, Any]], raw_results: Any, section: str) -> None:
    if not raw_results:
        return
    if isinstance(raw_results, list):
        for item in raw_results:
            results.append(_normalize_fill_result(item, section))
        return
    results.append(_normalize_fill_result(raw_results, section))


def _summarize_fill_results(results: list[Dict[str, Any]]) -> Dict[str, Any]:
    sections: Dict[str, Dict[str, Any]] = {}
    for item in results:
        section = str(item.get("section", "unknown") or "unknown")
        bucket = sections.setdefault(
            section,
            {
                "total": 0,
                "success": 0,
                "failed": 0,
                "fields": [],
                "failed_fields": [],
            },
        )
        bucket["total"] += 1
        field = str(item.get("field", "") or "")
        if field:
            bucket["fields"].append(field)
        if item.get("success"):
            bucket["success"] += 1
        else:
            bucket["failed"] += 1
            if field:
                bucket["failed_fields"].append(field)

    failed_fields = [str(item.get("field", "") or "") for item in results if not item.get("success")]
    successful_fields = [str(item.get("field", "") or "") for item in results if item.get("success")]
    write_failed_fields = [
        str(item.get("field", "") or "")
        for item in results
        if not item.get("write_success", False)
    ]
    verify_failed_fields = [
        str(item.get("field", "") or "")
        for item in results
        if item.get("write_success", False) and not item.get("verify_success", False)
    ]
    failed_sections = [name for name, bucket in sections.items() if bucket["failed"] > 0]
    return {
        "sections": sections,
        "failed_fields": failed_fields,
        "successful_fields": successful_fields,
        "write_failed_fields": write_failed_fields,
        "verify_failed_fields": verify_failed_fields,
        "failed_sections": failed_sections,
    }

@ActionRegistry.register("fill_product_info", "form", "批量填充商品信息")
def fill_product_info(
    product: Dict[str, Any],
    locator=None,
    log=None,
    required_visual_fields=None,
    field_groups=None,
    publish_mode: str = "single",
    **_kwargs,
) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    original_product = dict(product or {})
    explicit_fields = {str(key) for key in original_product.keys()}
    if isinstance(original_product.get("attributes"), dict):
        explicit_fields.update(str(key) for key in original_product.get("attributes", {}).keys())
    normalized_groups = [str(item).strip() for item in (field_groups or []) if str(item).strip()]
    if not normalized_groups:
        normalized_groups = ["basic_info", "pricing", "attributes", "sales_attributes", "sku_images", "logistics"]
    active_required_visual_fields = {
        key: value
        for key, value in (required_visual_fields or {}).items()
        if key in normalized_groups
    }
    inference = _infer_required_product_values(product, required_visual_fields=active_required_visual_fields)
    product = inference["product"]
    skip_page_guards = locator is not None and hasattr(locator, "__dict__") and not hasattr(locator, "click")
    basic_info_ready = False
    if skip_page_guards:
        _debug_log(log, "[fill_product_info] skipping page guards for lightweight locator stub")
    else:
        basic_info_ready = _ensure_basic_info_page(locator=locator, log=log)

    if not skip_page_guards and not basic_info_ready and _is_category_selection_page(locator=locator, log=log):
        message = "still on category selection page; select_category must complete before fill_product_info"
        _debug_log(log, f"[fill_product_info] hard stop: {message}")
        return {
            "success": False,
            "filled": 0,
            "total": 0,
            "details": [],
            "message": message,
            "error": message,
            "current_page": "category_page",
            "requires_action": "select_category",
            "recovery_hint": "select_category",
        }

    if not skip_page_guards and not basic_info_ready:
        message = "product basic info page is not ready; fill_product_info blocked"
        _debug_log(log, f"[fill_product_info] hard stop: {message}")
        return {
            "success": False,
            "filled": 0,
            "total": 0,
            "details": [],
            "message": message,
            "error": message,
            "current_page": "unknown",
            "requires_action": "select_category",
            "recovery_hint": "select_category",
        }

    results = []
    title = product.get("title")
    if "basic_info" in normalized_groups and title not in (None, ""):
        _append_fill_results(
            results,
            _fill_title_field_v3(str(title), locator=locator, log=log),
            section="basic_info",
        )
        time.sleep(0.3)

    procurement_erp_result = _fill_procurement_erp_field(product, locator=locator, log=log) if "basic_info" in normalized_groups else None
    if procurement_erp_result:
        _append_fill_results(results, procurement_erp_result, section="basic_info")
        time.sleep(0.2)

    model = product.get("model")
    if "basic_info" in normalized_groups and model not in (None, ""):
        _append_fill_results(
            results,
            _fill_model_field_v2(str(model), locator=locator, log=log),
            section="basic_info",
        )
        time.sleep(0.3)

    if "pricing" in normalized_groups and any(product.get(field) not in (None, "") for field in ("market_price", "purchase_price", "jd_price")):
        _append_fill_results(
            results,
            _fill_sku_pricing_fields_v3(product, locator=locator, log=log),
            section="pricing",
        )
        time.sleep(0.3)

    brand = product.get("brand") or product.get("品牌")
    if brand:
        _append_fill_results(
            results,
            _fill_brand_field_v2(str(brand), locator=locator, log=log),
            section="basic_info",
        )
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
            _append_fill_results(
                results,
                {
                    "field": "brand",
                    "method": brand_result.get("method", "select_dropdown"),
                    "value": brand,
                    "write_success": brand_result["success"],
                    "verify_success": brand_result["success"],
                    "success": brand_result["success"],
                },
                section="basic_info",
            )
            time.sleep(0.5)

    if "attributes" in normalized_groups:
        _append_fill_results(
            results,
            _fill_supported_attributes(product, locator=locator, log=log),
            section="attributes",
        )
    if "sales_attributes" in normalized_groups:
        _append_fill_results(
            results,
                _fill_required_sales_attributes_fields(
                    product,
                    required_visual_fields=active_required_visual_fields,
                    locator=locator,
                    log=log,
                    explicit_fields=explicit_fields,
                ),
                section="sales_attributes",
            )
    if "sku_images" in normalized_groups:
        _append_fill_results(
            results,
                _fill_required_sku_image_fields(
                    product,
                    required_visual_fields=active_required_visual_fields,
                    locator=locator,
                    log=log,
                    explicit_fields=explicit_fields,
                ),
                section="sku_images",
            )
    if "logistics" in normalized_groups:
        _append_fill_results(
            results,
                _fill_required_logistics_fields(
                    product,
                    required_visual_fields=active_required_visual_fields,
                    locator=locator,
                    log=log,
                    explicit_fields=explicit_fields,
                ),
                section="logistics",
            )

    success_count = sum(1 for item in results if item["success"])
    total = len(results)
    overall_success = total > 0 and success_count == total
    summary = _summarize_fill_results(results)
    failed_fields = summary["failed_fields"]
    payload = {
        "success": overall_success,
        "filled": success_count,
        "total": total,
        "details": results,
        "sections": summary["sections"],
        "failed_sections": summary["failed_sections"],
        "successful_fields": summary["successful_fields"],
        "write_failed_fields": summary["write_failed_fields"],
        "verify_failed_fields": summary["verify_failed_fields"],
        "inferred_values": inference["inferred_values"],
        "unresolved_required_fields": inference["unresolved_required_fields"],
        "required_visual_fields": required_visual_fields or {},
        "current_page_state": _collect_fill_page_state(locator=locator, log=log) if not skip_page_guards else {},
    }
    if failed_fields:
        payload["failed_fields"] = failed_fields
        if payload["failed_sections"]:
            payload["message"] = (
                f"Some product fields failed verification: {', '.join(failed_fields)} "
                f"(sections: {', '.join(payload['failed_sections'])})"
            )
        else:
            payload["message"] = f"Some product fields failed verification: {', '.join(failed_fields)}"
        payload["error"] = payload["message"]
    elif total == 0:
        payload["message"] = "No supported product fields were provided"
        payload["error"] = payload["message"]
    else:
        payload["message"] = "All requested product fields were filled and verified"
    return payload


@ActionRegistry.register("fill_product_description", "form", "填写商品详情")
def fill_product_description(
    product: Dict[str, Any],
    locator=None,
    log=None,
    required_visual_fields=None,
    publish_mode: str = "single",
    **_kwargs,
) -> Dict[str, Any]:
    locator = _get_locator(locator, log)

    if _return_from_advanced_detail_editor(locator=locator, log=log):
        time.sleep(1.0)

    _scroll_to_description_section(locator=locator, log=log)

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

    prepared = _prepare_upload_image(image_path, log=log)
    if not prepared.get("success"):
        return prepared

    prepared_path = str(prepared.get("prepared_path") or image_path)
    dialog_result = _submit_file_dialog_path(prepared_path, log=log, timeout=6.0)
    if dialog_result.get("success"):
        dialog_result.update(
            {
                "image": prepared_path,
                "source_image": image_path,
                "prepared_image": prepared_path,
                "upload_mode": prepared.get("upload_mode", ""),
                "prepared_width": prepared.get("width"),
                "prepared_height": prepared.get("height"),
                "prepared_size_bytes": prepared.get("size_bytes"),
            }
        )
        return dialog_result

    try:
        from PIL import Image
        import win32api
        import win32clipboard
        import win32con

        img = Image.open(prepared_path)
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
        return {
            "success": True,
            "method": "clipboard_paste",
            "image": prepared_path,
            "source_image": image_path,
            "prepared_image": prepared_path,
            "upload_mode": prepared.get("upload_mode", ""),
            "prepared_width": prepared.get("width"),
            "prepared_height": prepared.get("height"),
            "prepared_size_bytes": prepared.get("size_bytes"),
        }
    except Exception:
        return {
            "success": False,
            "message": "图片上传失败，文件对话框与剪贴板两种方式均未成功",
            "source_image": image_path,
            "prepared_image": prepared_path,
        }


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
