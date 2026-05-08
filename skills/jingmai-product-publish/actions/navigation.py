"""
Jingmai product publishing navigation actions.
"""

import time
from typing import Any, Dict

from actions._uia_helpers import (
    click_uia_element,
    find_jingmai_uia_window,
    iter_named_descendants,
    resolve_template_path,
    score_text_match,
)
from actions.registry import ActionRegistry
from config.jingmai_coords import CATEGORY_PAGE, PRODUCT_INFO_PAGE

# Session1 Helper 操作
try:
    from session1_ops import s1_click, s1_paste, s1_press, s1_hotkey, s1_wait

    HAS_SESSION1 = True
except ImportError:
    HAS_SESSION1 = False
    s1_click = s1_paste = s1_press = s1_hotkey = s1_wait = None


def _get_locator(locator=None, log=None):
    if locator is None:
        from infrastructure.locator import JingmaiLocator

        return JingmaiLocator(log=log)
    return locator


def _tokenize_text(text: str) -> list[str]:
    normalized = str(text or "").replace(">", " ").replace("/", " ").replace("-", " ")
    tokens = [item.strip() for item in normalized.split() if item.strip()]
    if text and text not in tokens:
        tokens.insert(0, str(text).strip())
    return tokens[:6]


def _page_contains_text(expected_text: str, locator=None, log=None) -> bool:
    locator = _get_locator(locator, log)
    window = find_jingmai_uia_window(locator=locator, log=log)
    if not window:
        return False

    try:
        for candidate in iter_named_descendants(window, limit=300):
            if expected_text in candidate["name"]:
                return True
    except Exception as exc:
        if log:
            log.warning(f"page text scan failed: {exc}")
    return False


def _find_category_search_input(locator=None, log=None):
    window = find_jingmai_uia_window(locator=locator, log=log)
    if not window:
        return None

    candidates = []
    for candidate in iter_named_descendants(
        window,
        control_types=["Edit"],
        top_range=(100, 520),
        exclude_keywords=["ai搜索", "ai search"],
        limit=40,
    ):
        rect = candidate["rect"]
        score = 0
        if rect.top > 140:
            score += 4
        if rect.width() > 160:
            score += 2
        if rect.left > 280:
            score += 1
        candidates.append((score, rect.top, candidate))

    if not candidates:
        return None
    _, _, best = sorted(candidates, key=lambda item: (-item[0], item[1]))[0]
    return best


def _has_category_page_markers(locator=None, log=None) -> bool:
    return _page_contains_text("绫荤洰閫夋嫨鍙戝搧", locator=locator, log=log)


def _has_product_info_markers(locator=None, log=None) -> bool:
    if _page_contains_text("鍟嗗搧鏍囬", locator=locator, log=log):
        return True

    window = find_jingmai_uia_window(locator=_get_locator(locator, log), log=log)
    if not window:
        return False

    try:
        for element in window.descendants():
            try:
                name = element.window_text() or ""
                if "请输入商品标题" in name or "商品标题" in name:
                    return True
            except Exception:
                continue
    except Exception as exc:
        if log:
            log.warning(f"product info marker scan failed: {exc}")
    return False


def _click_image_fallback(template_name: str, locator=None, log=None, confidence: float = 0.86) -> Dict[str, Any]:
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
        time.sleep(0.6)
        return {
            "success": True,
            "template": template_name,
            "template_path": template_path,
            "match_confidence": confidence,
            "position": {"x": result["x"], "y": result["y"]},
        }
    except Exception as exc:
        if log:
            log.warning(f"vision fallback failed: {exc}")
        return {"success": False, "message": str(exc), "template": template_name}


def _category_next_region(locator=None) -> tuple[int, int, int, int] | None:
    coords = CATEGORY_PAGE.get("next_button")
    locator = _get_locator(locator, None)
    if not coords or locator is None:
        return None
    try:
        local_x, local_y = locator.adapt_coords(coords[0], coords[1])
        screen_x, screen_y = locator.window_to_screen(local_x, local_y)
        return (screen_x - 45, screen_y - 10, screen_x + 45, screen_y + 10)
    except Exception:
        return None


def _is_category_next_enabled(locator=None, log=None) -> bool:
    region = _category_next_region(locator=locator)
    if not region:
        return False

    try:
        from PIL import ImageGrab

        shot = ImageGrab.grab(bbox=region)
        pixels = list(shot.getdata())
        if not pixels:
            return False

        avg_r = sum(pixel[0] for pixel in pixels) / len(pixels)
        avg_g = sum(pixel[1] for pixel in pixels) / len(pixels)
        avg_b = sum(pixel[2] for pixel in pixels) / len(pixels)
        enabled = avg_r < 140 and avg_g < 170 and avg_b > 220
        if log:
            log.debug(
                f"category next button avg rgb=({avg_r:.1f}, {avg_g:.1f}, {avg_b:.1f}), enabled={enabled}"
            )
        return enabled
    except Exception as exc:
        if log:
            log.warning(f"next button state probe failed: {exc}")
        return False


def _select_search_result(search_text: str, search_input=None, locator=None, log=None) -> bool:
    """
    Select the category result after the search box has already been filled.

    Root cause:
    The previous implementation retyped Chinese text with pyautogui.typewrite(),
    which is not reliable for Han characters here and wiped out the valid query.

    优先使用 Session1 Helper 的 s1_click/s1_press。
    """
    window = find_jingmai_uia_window(locator=locator, log=log)
    if window:
        candidates = []
        for candidate in iter_named_descendants(window, top_range=(150, 420), max_name_length=120, limit=240):
            score = score_text_match(candidate["name"], search_text, _tokenize_text(search_text))
            if candidate["control_type"] in {"ListItem", "Text", "Button", "Hyperlink"}:
                score += 2
            if score > 0:
                rect = candidate["rect"]
                candidates.append((score, rect.top, len(candidate["name"]), candidate))

        if candidates:
            _, _, _, best = sorted(candidates, key=lambda item: (-item[0], item[1], item[2]))[0]
            if click_uia_element(best["element"], log=log):
                time.sleep(1.0)
                return True

    try:
        if search_input:
            rect = search_input["rect"]
            suggestion_points = [
                (rect.left + 140, rect.bottom + 18),
                (rect.left + 240, rect.bottom + 18),
                (rect.left + 140, rect.bottom + 42),
            ]
        else:
            suggestion_points = [(600, 295)]

        for point_x, point_y in suggestion_points:
            # 优先用 Session1 Helper
            if HAS_SESSION1 and s1_click:
                s1_click(point_x, point_y, delay=0.8)
            else:
                import pyautogui
                pyautogui.click(point_x, point_y)
                time.sleep(0.8)

            if _is_category_next_enabled(locator=locator, log=log):
                return True

        # 用键盘选择
        if HAS_SESSION1 and s1_press:
            s1_press("down")
            time.sleep(0.2)
            s1_press("enter")
        else:
            import pyautogui
            pyautogui.press("down")
            time.sleep(0.2)
            pyautogui.press("enter")
        time.sleep(1.0)
        return True
    except Exception as exc:
        if log:
            log.warning(f"search result selection failed: {exc}")
        return False


def _click_named_button(keywords: list[str], locator=None, log=None) -> Dict[str, Any]:
    window = find_jingmai_uia_window(locator=locator, log=log)
    if not window:
        return {"success": False, "message": "uia window not found"}

    for candidate in iter_named_descendants(window, control_types=["Button"], limit=120):
        name = candidate["name"]
        if any(keyword in name for keyword in keywords):
            rect = candidate["rect"]
            cx = (rect.left + rect.right) // 2
            cy = (rect.top + rect.bottom) // 2

            # 优先用 Session1 Helper 点击
            if HAS_SESSION1 and s1_click:
                if s1_click(cx, cy, delay=0.5):
                    return {"success": True, "method": "session1", "button": name, "coords": (cx, cy)}

            # Fallback: UIA
            if click_uia_element(candidate["element"], log=log):
                return {"success": True, "method": "uia", "button": name}

    return {"success": False, "message": f"button not found: {keywords}"}


def _click_category_next(locator=None, log=None) -> Dict[str, Any]:
    """
    点击"下一步"按钮进入商品信息页。

    优先使用 Session1 Helper，Session 0 环境下降级到 pyautogui。
    """
    coords = CATEGORY_PAGE.get("next_button")
    if coords:
        bx, by = coords
        # 优先用 Session1 Helper
        if HAS_SESSION1 and s1_click:
            if s1_click(bx, by, delay=1.2):
                return {"success": True, "method": "session1_click", "coords": coords}

        # Fallback: pyautogui
        try:
            import pyautogui

            pyautogui.click(bx, by)
            time.sleep(1.2)
            return {"success": True, "method": "pyautogui_click", "coords": coords}
        except Exception as exc:
            if log:
                log.warning(f"pyautogui click failed: {exc}")

    named = _click_named_button(["下一步", "填写商品信息"], locator=locator, log=log)
    if named.get("success"):
        return named

    vision = _click_image_fallback("category_next_button.png", locator=locator, log=log)
    if vision.get("success"):
        return {"success": True, "method": "vision", "vision_fallback": vision}

    return {"success": False, "message": "next button not found"}


def _click_product_button(coords: tuple[int, int] | None, keywords: list[str], template_name: str, locator=None, log=None):
    locator = _get_locator(locator, log)

    # 优先用 Session1 Helper 点击坐标
    if coords:
        if HAS_SESSION1 and s1_click:
            if s1_click(coords[0], coords[1], delay=1.5):
                return {"success": True, "method": "session1", "coords": coords}
        # Fallback: locator.click
        if locator.click(coords[0], coords[1], delay=1.5):
            return {"success": True, "method": "coordinate"}

    named = _click_named_button(keywords, locator=locator, log=log)
    if named.get("success"):
        return named

    vision = _click_image_fallback(template_name, locator=locator, log=log)
    if vision.get("success"):
        return {"success": True, "method": "vision", "vision_fallback": vision}

    return {"success": False, "message": f"button not found: {keywords}"}


@ActionRegistry.register("select_category", "navigation", "选择商品类目")
def select_category(
    search_text: str = "",
    level3_coords: tuple = None,
    level4_coords: tuple = None,
    locator=None,
    log=None,
) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    results = []

    if _has_product_info_markers(locator=locator, log=log) and not _has_category_page_markers(locator=locator, log=log):
        return {"success": True, "steps": ["already_past_category"]}

    if search_text:
        search_input = _find_category_search_input(locator=locator, log=log)
        if not search_input and not _has_category_page_markers(locator=locator, log=log):
            return {"success": True, "steps": ["already_past_category"]}
        search_coords = (
            ((search_input["rect"].left + search_input["rect"].right) // 2, (search_input["rect"].top + search_input["rect"].bottom) // 2)
            if search_input
            else (640, 260)
        )
        if not locator.click(search_coords[0], search_coords[1], delay=0.3):
            return {"success": False, "message": "click category search input failed", "steps": results}

        from actions.form import fill_text

        fill_result = fill_text(search_text, x=search_coords[0], y=search_coords[1], locator=locator, log=log)
        if not fill_result["success"]:
            return {"success": False, "message": fill_result.get("message", "fill category search failed"), "steps": results}
        results.append("search")
        time.sleep(1.0)

        if not _select_search_result(search_text, search_input=search_input, locator=locator, log=log):
            return {"success": False, "message": f"category search result not found: {search_text}", "steps": results}

        results.append("search_select")
        time.sleep(1.0)
        if not _is_category_next_enabled(locator=locator, log=log):
            return {
                "success": False,
                "message": "category search result was not committed; next button is still disabled",
                "steps": results,
            }

    if level3_coords:
        if not locator.click(level3_coords[0], level3_coords[1], delay=0.5):
            return {"success": False, "message": "click third-level category failed", "steps": results}
        results.append("level3")
        time.sleep(0.8)

    if level4_coords:
        if not locator.click(level4_coords[0], level4_coords[1], delay=0.5):
            return {"success": False, "message": "click fourth-level category failed", "steps": results}
        results.append("level4")
        time.sleep(0.8)
    elif not level3_coords and not search_text:
        level3 = CATEGORY_PAGE.get("level3_third_col")
        level4 = CATEGORY_PAGE.get("level4")
        if level3 and not locator.click(level3[0], level3[1], delay=0.5):
            return {"success": False, "message": "click default third-level category failed", "steps": results}
        if level3:
            results.append("level3_default")
            time.sleep(0.8)
        if level4 and not locator.click(level4[0], level4[1], delay=0.5):
            return {"success": False, "message": "click default fourth-level category failed", "steps": results}
        if level4:
            results.append("level4_default")
            time.sleep(0.8)

    next_result = _click_category_next(locator=locator, log=log)
    if not next_result.get("success"):
        return {"success": False, "message": "click next failed", "steps": results}
    results.append("next")
    time.sleep(2.0)

    if _is_category_next_enabled(locator=locator, log=log):
        return {"success": False, "message": "clicked next but category page did not advance", "steps": results}

    if _page_contains_text("类目选择发品", locator=locator, log=log):
        return {"success": False, "message": "still on category page after clicking next", "steps": results}

    return {"success": True, "steps": results}


@ActionRegistry.register("scroll_page", "navigation", "滚动页面")
def scroll_page(x: int = 1280, y: int = 700, delta: int = -3, locator=None, log=None) -> Dict[str, Any]:
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
    except Exception as exc:
        return {"success": False, "message": str(exc)}


@ActionRegistry.register("save_draft", "navigation", "保存草稿")
def save_draft(locator=None, log=None) -> Dict[str, Any]:
    return _click_product_button(
        PRODUCT_INFO_PAGE.get("save_draft_button"),
        ["保存草稿"],
        "save_draft_button.png",
        locator=locator,
        log=log,
    )


@ActionRegistry.register("publish_product", "navigation", "发布商品")
def publish_product(locator=None, log=None) -> Dict[str, Any]:
    return _click_product_button(
        PRODUCT_INFO_PAGE.get("publish_button"),
        ["发布", "提交"],
        "publish_button.png",
        locator=locator,
        log=log,
    )


@ActionRegistry.register("click_modify", "navigation", "点击修改链接")
def click_modify(locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    window = find_jingmai_uia_window(locator=locator, log=log)
    if window:
        for candidate in iter_named_descendants(window, control_types=["Hyperlink"], limit=100):
            if "修改" in candidate["name"] and click_uia_element(candidate["element"], log=log):
                return {"success": True, "method": "uia_link"}

    for coords in [(979, 225), (979, 325), (979, 425)]:
        if locator.click(coords[0], coords[1], delay=1.0):
            return {"success": True, "method": "coordinate_fallback"}

    return {"success": False, "message": "click modify link failed"}


@ActionRegistry.register("go_back", "navigation", "返回上一页")
def go_back(locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    try:
        import win32api
        import win32con

        win32api.keybd_event(0x12, 0, 0, 0)
        win32api.keybd_event(0x25, 0, 0, 0)
        win32api.keybd_event(0x25, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x12, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.5)
        return {"success": True, "method": "alt_left"}
    except Exception:
        pass

    locator.press_escape(delay=0.5)
    return {"success": True, "method": "escape"}
