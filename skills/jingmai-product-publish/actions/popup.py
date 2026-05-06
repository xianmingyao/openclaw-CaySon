"""
京麦商品发布自动化 - 弹窗恢复 Actions
优先走轻量交互与 UIA，只有关键按钮才接视觉兜底。
"""
import time
from typing import Any, Dict

from actions._uia_helpers import click_uia_element, find_jingmai_uia_window, iter_named_descendants, resolve_template_path
from actions.registry import ActionRegistry


def _get_locator(locator=None, log=None):
    if locator is None:
        from infrastructure.locator import JingmaiLocator

        return JingmaiLocator(log=log)
    return locator


def _click_template(template_name: str, locator=None, log=None, confidence: float = 0.88) -> Dict[str, Any]:
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
    except Exception as exc:
        if log:
            log.warning(f"popup vision fallback failed: {exc}")
        return {"success": False, "message": str(exc), "template": template_name}


def _click_popup_button(keywords: list[str], locator=None, log=None) -> Dict[str, Any]:
    window = find_jingmai_uia_window(locator=locator, log=log)
    if not window:
        return {"success": False, "message": "uia window not found"}

    candidates = []
    for candidate in iter_named_descendants(window, control_types=["Button"], limit=160):
        name = candidate["name"].lower()
        if any(keyword.lower() in name for keyword in keywords):
            rect = candidate["rect"]
            score = 5
            if rect.top >= 180:
                score += 2
            candidates.append((score, rect.top, candidate))

    if not candidates:
        return {"success": False, "message": f"popup button not found: {keywords}"}

    _, _, best = sorted(candidates, key=lambda item: (-item[0], item[1]))[0]
    if click_uia_element(best["element"], log=log):
        return {"success": True, "method": "uia", "button": best["name"]}
    return {"success": False, "message": "uia popup click failed"}


@ActionRegistry.register("dismiss_popup", "popup", "关闭弹窗")
def dismiss_popup(method: str = "escape", x: int = None, y: int = None, locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    methods = [method] if method != "auto" else ["escape", "click_x", "click_ok", "vision_close"]

    for current in methods:
        if current == "escape":
            try:
                locator.press_escape(delay=0.5)
                return {"success": True, "method": "escape"}
            except Exception:
                continue

        if current == "click_x":
            if x is not None and y is not None and locator.click(x, y, delay=0.4):
                return {"success": True, "method": "click_x", "coords": (x, y)}
            button_result = _click_popup_button(["关闭", "close", "x"], locator=locator, log=log)
            if button_result.get("success"):
                return button_result
            continue

        if current == "click_ok":
            button_result = _click_popup_button(["确定", "ok", "取消", "cancel"], locator=locator, log=log)
            if button_result.get("success"):
                return button_result
            continue

        if current == "vision_close":
            vision = _click_template("popup_close_button.png", locator=locator, log=log)
            if vision.get("success"):
                return {"success": True, "method": "vision_close", "vision_fallback": vision}

    return {"success": False, "message": "弹窗关闭失败"}


@ActionRegistry.register("handle_dialog", "popup", "处理对话框")
def handle_dialog(action: str = "accept", locator=None, log=None) -> Dict[str, Any]:
    keywords = {
        "accept": ["确定", "ok", "是", "yes", "确认"],
        "dismiss": ["取消", "cancel", "否", "no", "关闭"],
    }.get(action, ["确定", "ok", "确认"])

    button_result = _click_popup_button(keywords, locator=locator, log=log)
    if button_result.get("success"):
        button_result["action"] = action
        return button_result

    template_name = "popup_confirm_button.png" if action == "accept" else "popup_cancel_button.png"
    vision = _click_template(template_name, locator=locator, log=log)
    if vision.get("success"):
        return {"success": True, "method": "vision", "action": action, "vision_fallback": vision}

    return {"success": False, "message": f"未找到对话框按钮: {action}"}


@ActionRegistry.register("dismiss_cef_popup", "popup", "关闭 CEF 弹窗")
def dismiss_cef_popup(locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)

    locator.press_escape(delay=0.4)
    time.sleep(0.2)

    button_result = _click_popup_button(["确定", "我知道了", "关闭", "取消"], locator=locator, log=log)
    if button_result.get("success"):
        return button_result

    try:
        import pyautogui

        pyautogui.press("tab")
        time.sleep(0.15)
        pyautogui.press("enter")
        time.sleep(0.25)
    except Exception:
        pass

    if locator.window_rect:
        right = locator.window_rect[2]
        top = locator.window_rect[1]
        for offset_x in [50, 100, 150]:
            for offset_y in [15, 25, 35]:
                locator.click(right - offset_x, top + offset_y, delay=0.2)

    vision = _click_template("popup_close_button.png", locator=locator, log=log)
    if vision.get("success"):
        return {"success": True, "method": "vision", "vision_fallback": vision}

    return {"success": True, "method": "multi_strategy"}
