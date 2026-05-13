"""
Jingmai product publishing navigation actions.
"""

import json
import re
import tempfile
import time
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
from config.jingmai_coords import CATEGORY_PAGE, PRODUCT_INFO_PAGE
from llm.manager import LLMManager

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


def _category_search_variants(text: str) -> list[str]:
    raw = str(text or "").strip()
    if not raw:
        return []

    variants = [raw]
    fragments = [frag.strip() for frag in re.split(r"\s*>\s*|\s*/\s*", raw) if frag.strip()]
    if fragments:
        leaf = fragments[-1]
        if leaf not in variants:
            variants.append(leaf)
        if len(fragments) >= 2:
            parent_leaf = f"{fragments[-2]} > {fragments[-1]}"
            if parent_leaf not in variants:
                variants.append(parent_leaf)
    return variants


def _category_depth(name: str) -> int:
    text = str(name or "")
    return text.count(">") + text.count("＞") + text.count("/")


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


def _read_selected_category_texts(locator=None, log=None) -> list[str]:
    window = find_jingmai_uia_window(locator=_get_locator(locator, log), log=log)
    if not window:
        return []

    values = []
    for candidate in iter_named_descendants(window, control_types=["Text"], top_range=(620, 720), left_range=(500, 1200), limit=80):
        name = (candidate["name"] or "").strip()
        if not name or name == "已选类目：":
            continue
        values.append(name)
    return values


def _selected_category_matches(search_text: str, locator=None, log=None) -> bool:
    selected = " > ".join(_read_selected_category_texts(locator=locator, log=log))
    if not selected:
        return False

    variants = _category_search_variants(search_text)
    return any(variant and variant in selected for variant in variants)


def _collect_category_choice_candidates(search_text: str, locator=None, log=None) -> list[dict]:
    window = find_jingmai_uia_window(locator=_get_locator(locator, log), log=log)
    if not window:
        return []

    tokens = _tokenize_text(search_text)
    candidates = []
    for candidate in iter_named_descendants(
        window,
        control_types=["Text", "Button", "Hyperlink", "ListItem"],
        top_range=(240, 420),
        max_name_length=160,
        limit=260,
    ):
        name = (candidate["name"] or "").strip()
        if not name or name in {"近期使用类目：", "已选类目："}:
            continue
        score = score_text_match(name, search_text, tokens)
        if search_text and search_text in name:
            score += 10
        if search_text and name.endswith(search_text):
            score += 12
        if ">" in name and search_text and search_text in name:
            score += 15
        if name == search_text:
            score += 20
        rect = candidate["rect"]
        if rect.top <= 300:
            score += 2
        if score <= 0:
            continue
        candidates.append(
            {
                "score": score,
                "name": name,
                "element": candidate["element"],
                "rect": rect,
            }
        )
    return candidates


def _select_leaf_category_candidate(search_text: str, locator=None, log=None) -> Dict[str, Any]:
    candidates = _collect_category_choice_candidates(search_text, locator=locator, log=log)
    if not candidates:
        vision_result = vision_click_text_center(
            target_text=search_text,
            page_hint="京麦类目选择页，点击最匹配的叶子类目项",
            locator=locator,
            log=log,
        )
        if vision_result.get("success"):
            time.sleep(1.0)
            if _is_category_next_enabled(locator=locator, log=log) or _has_product_info_markers(locator=locator, log=log):
                return {
                    "success": True,
                    "name": search_text,
                    "score": 0,
                    "attempted_names": [],
                    "method": "ollama_vision_move_click",
                }
        return {"success": False, "message": f"no category candidate matched: {search_text}"}

    ranked = sorted(
        candidates,
        key=lambda item: (-_category_depth(item["name"]), -item["score"], item["rect"].top, item["rect"].left, len(item["name"])),
    )
    locator = _get_locator(locator, log)
    attempted_names = []
    last_error = ""

    for candidate in ranked[:5]:
        attempted_names.append(candidate["name"])
        clicked = click_uia_element(candidate["element"], log=log)
        if not clicked:
            rect = candidate["rect"]
            cx = (rect.left + rect.right) // 2
            cy = (rect.top + rect.bottom) // 2
            clicked = locator.click(cx, cy, delay=0.8)
        if not clicked:
            vision_result = vision_click_text_center(
                target_text=candidate["name"],
                page_hint="京麦类目选择页，点击最匹配的叶子类目项",
                locator=locator,
                log=log,
            )
            clicked = bool(vision_result.get("success"))
        if not clicked:
            last_error = f"failed to click matched category candidate: {candidate['name']}"
            continue

        time.sleep(1.0)
        if _is_category_next_enabled(locator=locator, log=log) or _has_product_info_markers(locator=locator, log=log):
            return {
                "success": True,
                "name": candidate["name"],
                "score": candidate["score"],
                "attempted_names": attempted_names,
            }

    if attempted_names:
        return {
            "success": False,
            "message": last_error or f"leaf candidates clicked but next button stayed disabled: {attempted_names}",
            "attempted_names": attempted_names,
        }
    return {"success": False, "message": f"failed to click matched category candidate: {search_text}"}


def _build_category_disabled_reason(search_text: str, locator=None, log=None) -> str:
    selected = _read_selected_category_texts(locator=locator, log=log)
    selected_text = " > ".join(selected) if selected else "none"
    candidates = _collect_category_choice_candidates(search_text, locator=locator, log=log)
    top_names = [item["name"] for item in candidates[:5]]
    return (
        f"next button is still disabled after category selection; "
        f"selected_category={selected_text}; "
        f"top_matches={top_names}"
    )


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


def _parse_vision_click_json(raw_text: str) -> dict | None:
    text = (raw_text or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None


def _safe_temp_vision_path() -> str:
    base_dir = Path(tempfile.gettempdir()) / "jingmai-product-publish"
    base_dir.mkdir(parents=True, exist_ok=True)
    return str(base_dir / f"vision_click_{int(time.time() * 1000)}.png")


def _build_vision_click_diagnostics(locator, screenshot: str, llm_x: int, llm_y: int) -> Dict[str, Any]:
    actual_width = actual_height = None
    scale_x = scale_y = None
    try:
        from PIL import Image
        from settings import get_settings

        settings = get_settings()
        with Image.open(screenshot) as img:
            actual_width, actual_height = img.size
        scale_x = round(int(settings.SCREENSHOT_MAX_WIDTH) / actual_width, 4) if actual_width else None
        scale_y = round(int(settings.SCREENSHOT_MAX_HEIGHT) / actual_height, 4) if actual_height else None
    except Exception:
        actual_width = actual_height = None

    mapped_x, mapped_y = locator.llm_to_screen(llm_x, llm_y, image_path=screenshot)
    return {
        "actual_vision_size": [actual_width, actual_height] if actual_width and actual_height else None,
        "scale_x": scale_x,
        "scale_y": scale_y,
        "mapped_x": mapped_x,
        "mapped_y": mapped_y,
    }


def _normalize_vision_bbox(payload: Dict[str, Any]) -> Optional[list[int]]:
    bbox = payload.get("bbox")
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        return None
    try:
        return [int(value) for value in bbox]
    except Exception:
        return None


def _vision_bbox_is_valid(bbox: Optional[list[int]], center_x: int, center_y: int) -> bool:
    if not bbox:
        return False
    left, top, right, bottom = bbox
    if right <= left or bottom <= top:
        return False
    if (right - left) < 8 or (bottom - top) < 8:
        return False
    return left <= center_x <= right and top <= center_y <= bottom


def _resolve_vision_click_consensus(samples: list[Dict[str, Any]], image_size: Optional[list[int]]) -> Dict[str, Any]:
    if not samples:
        return {"success": False, "reason": "no_valid_samples"}
    if len(samples) == 1:
        return {"success": True, "reason": "single_sample", "sample": samples[0]}

    width = int((image_size or [0, 0])[0] or 0)
    height = int((image_size or [0, 0])[1] or 0)
    max_dx = max(24, int(width * 0.08)) if width else 48
    max_dy = max(24, int(height * 0.08)) if height else 48

    xs = [int(item["llm_x"]) for item in samples]
    ys = [int(item["llm_y"]) for item in samples]
    if max(xs) - min(xs) > max_dx or max(ys) - min(ys) > max_dy:
        return {
            "success": False,
            "reason": "vision_target_drift",
            "samples": [{"x": item["llm_x"], "y": item["llm_y"]} for item in samples],
            "max_dx": max_dx,
            "max_dy": max_dy,
        }

    chosen = dict(samples[0])
    chosen["llm_x"] = round(sum(xs) / len(xs))
    chosen["llm_y"] = round(sum(ys) / len(ys))
    return {"success": True, "reason": "multi_sample_consensus", "sample": chosen}


def _mapped_point_is_safe(locator, x: int, y: int, margin: int = 12) -> bool:
    try:
        x = int(x)
        y = int(y)
    except Exception:
        return False

    if x <= margin or y <= margin:
        return False

    rect = getattr(locator, "window_rect", None)
    if not rect and hasattr(locator, "find_window"):
        try:
            info = locator.find_window()
            rect = getattr(info, "rect", None) if info else None
        except Exception:
            rect = None

    if rect and len(rect) == 4:
        left, top, right, bottom = [int(value) for value in rect]
        if x <= left + margin or y <= top + margin:
            return False
        if x >= right - margin or y >= bottom - margin:
            return False
    return True


@ActionRegistry.register("vision_click_text_center", "navigation", "浣跨敤 Ollama 瑙嗚瀹氫綅鏂囨湰涓績骞舵墽琛?move + click")
def vision_click_text_center(
    target_text: str,
    page_hint: str = "",
    screenshot_path: str = "",
    locator=None,
    log=None,
    **_kwargs,
) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    target_text = str(target_text or "").strip()
    if not target_text:
        return {"success": False, "message": "target_text is required"}

    screenshot = screenshot_path or _safe_temp_vision_path()
    if not screenshot_path:
        take_screenshot = getattr(locator, "take_screenshot", None)
        if not callable(take_screenshot):
            return {"success": False, "message": "vision screenshot capture is unavailable", "target_text": target_text}
        screenshot = take_screenshot(screenshot, for_vision=True)
    if not screenshot:
        return {"success": False, "message": "vision screenshot capture failed", "target_text": target_text}

    prompt = (
        "你是桌面自动化视觉定位器。"
        "请在截图中定位目标文本或最匹配的类目项/输入框，并只返回严格 JSON。"
        "禁止返回 markdown。"
        "JSON 字段必须包含: "
        '{"status":"ok|error","target_text":"","center_x":0,"center_y":0,"bbox":[x1,y1,x2,y2],"reason":""}. '
        "坐标必须基于当前图片像素坐标系。"
        "如果找不到，返回 status=error。"
        f"页面提示: {page_hint or '京麦发品页'}。"
        f"目标文本: {target_text}。"
    )

    try:
        llm = LLMManager()
    except Exception as exc:
        return {
            "success": False,
            "message": f"ollama vision click failed: {exc}",
            "target_text": target_text,
            "screenshot": screenshot,
        }

    samples: list[Dict[str, Any]] = []
    last_payload: Optional[Dict[str, Any]] = None
    last_error = ""
    for _ in range(2):
        try:
            response = llm.invoke_multimodal(prompt, screenshot)
        except Exception as exc:
            last_error = f"ollama vision click failed: {exc}"
            continue

        payload = _parse_vision_click_json(response)
        if not payload:
            last_error = "ollama vision response is not valid json"
            continue

        last_payload = payload
        if str(payload.get("status", "")).lower() != "ok":
            last_error = payload.get("reason") or "target not found"
            continue

        try:
            llm_x = int(payload["center_x"])
            llm_y = int(payload["center_y"])
        except Exception:
            last_error = "ollama vision response missing center_x/center_y"
            continue

        bbox = _normalize_vision_bbox(payload)
        if not _vision_bbox_is_valid(bbox, llm_x, llm_y):
            last_error = "vision bbox is invalid or does not contain center"
            continue

        samples.append({"llm_x": llm_x, "llm_y": llm_y, "bbox": bbox, "payload": payload})

    consensus = _resolve_vision_click_consensus(samples, None)
    if not consensus.get("success"):
        return {
            "success": False,
            "message": consensus.get("reason") or last_error or "vision click consensus failed",
            "target_text": target_text,
            "vision_result": last_payload,
            "samples": samples,
            "screenshot": screenshot,
        }

    chosen = consensus["sample"]
    llm_x = int(chosen["llm_x"])
    llm_y = int(chosen["llm_y"])
    payload = chosen["payload"]
    diagnostics = _build_vision_click_diagnostics(locator, screenshot, llm_x, llm_y)
    local_x = diagnostics["mapped_x"]
    local_y = diagnostics["mapped_y"]
    if log:
        log.debug(
            "[vision-click] "
            f"target={target_text} actual_vision_size={diagnostics.get('actual_vision_size')} "
            f"scale_x={diagnostics.get('scale_x')} scale_y={diagnostics.get('scale_y')} "
            f"mapped_x={local_x} mapped_y={local_y}"
        )
    if not _mapped_point_is_safe(locator, local_x, local_y):
        return {
            "success": False,
            "message": "mapped click point is unsafe",
            "target_text": target_text,
            "screenshot": screenshot,
            "llm_coords": {"x": llm_x, "y": llm_y},
            "mapped_coords": {"x": local_x, "y": local_y},
            "vision_result": payload,
            "samples": samples,
            **diagnostics,
        }
    clicked = locator.click(local_x, local_y, delay=0.6)
    return {
        "success": bool(clicked),
        "method": "ollama_vision_move_click",
        "target_text": target_text,
        "page_hint": page_hint,
        "screenshot": screenshot,
        "llm_coords": {"x": llm_x, "y": llm_y},
        "mapped_coords": {"x": local_x, "y": local_y},
        "consensus_reason": consensus.get("reason"),
        "samples": samples,
        **diagnostics,
        "vision_result": payload,
        "drag": False,
    }


def _focus_category_search_input(search_text: str, search_input=None, locator=None, log=None) -> Dict[str, Any]:
    locator = _get_locator(locator, log)
    if search_input:
        rect = search_input["rect"]
        center_x = (rect.left + rect.right) // 2
        center_y = (rect.top + rect.bottom) // 2
        clicked = locator.click(center_x, center_y, delay=0.3)
        return {
            "success": bool(clicked),
            "method": "uia_center_click" if clicked else "uia_center_click_failed",
            "coords": (center_x, center_y),
        }

    return vision_click_text_center(
        target_text="类目搜索框",
        page_hint=f"京麦类目选择页顶部搜索输入框，点击可输入“{search_text}”的搜索框，不要点击候选类目",
        locator=locator,
        log=log,
    )


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
        vision_result = vision_click_text_center(
            target_text=search_text,
            page_hint="京麦类目选择页搜索结果候选区，点击最匹配搜索词的候选结果，不要点击搜索框",
            locator=locator,
            log=log,
        )
        if vision_result.get("success"):
            time.sleep(0.8)
            if _is_category_next_enabled(locator=locator, log=log):
                return True
            if _has_product_info_markers(locator=locator, log=log):
                return True

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
        primary_keyword = next((keyword for keyword in keywords if keyword), "")
        vision_result = vision_click_text_center(
            target_text=primary_keyword or "按钮",
            page_hint=f"京麦页面按钮区域，点击按钮文本最匹配以下关键词之一的按钮: {keywords}",
            locator=locator,
            log=log,
        )
        if vision_result.get("success"):
            return {
                "success": True,
                "method": "ollama_vision_move_click",
                "button": primary_keyword or "按钮",
                "vision_fallback": vision_result,
            }
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

            vision_result = vision_click_text_center(
                target_text=name,
                page_hint=f"京麦页面按钮区域，点击文本为“{name}”的按钮",
                locator=locator,
                log=log,
            )
            if vision_result.get("success"):
                return {
                    "success": True,
                    "method": "ollama_vision_move_click",
                    "button": name,
                    "coords": (cx, cy),
                    "vision_fallback": vision_result,
                }

    return {"success": False, "message": f"button not found: {keywords}"}


def _click_category_next(locator=None, log=None) -> Dict[str, Any]:
    """
    点击"下一步"按钮进入商品信息页。

    优先使用 Session1 Helper，Session 0 环境下降级到 pyautogui。
    """
    named = _click_named_button(["下一步", "填写商品信息"], locator=locator, log=log)
    if named.get("success"):
        return named

    vision_click = vision_click_text_center(
        target_text="下一步",
        page_hint="京麦类目选择页底部下一步按钮，按钮文本通常为“下一步，完善其他商品信息”",
        locator=locator,
        log=log,
    )
    if vision_click.get("success"):
        return {"success": True, "method": "ollama_vision_move_click", "vision_fallback": vision_click}

    coords = CATEGORY_PAGE.get("next_button")
    if coords:
        bx, by = coords
        if HAS_SESSION1 and s1_click:
            if s1_click(bx, by, delay=1.2):
                return {"success": True, "method": "session1_click", "coords": coords}
        if _get_locator(locator, log).click(bx, by, delay=1.2):
            return {"success": True, "method": "coordinate_click", "coords": coords}

    image_fallback = _click_image_fallback("category_next_button.png", locator=locator, log=log)
    if image_fallback.get("success"):
        return {"success": True, "method": "vision", "vision_fallback": image_fallback}

    return {"success": False, "message": "next button not found"}


def _click_product_button(coords: tuple[int, int] | None, keywords: list[str], template_name: str, locator=None, log=None):
    locator = _get_locator(locator, log)
    lightweight_locator = not hasattr(locator, "take_screenshot") and not hasattr(locator, "get_uia_window")

    # 优先用 Session1 Helper 点击坐标
    if coords:
        if HAS_SESSION1 and s1_click:
            if s1_click(coords[0], coords[1], delay=1.5):
                return {"success": True, "method": "session1", "coords": coords}
        # Fallback: locator.click
        if locator.click(coords[0], coords[1], delay=1.5):
            return {"success": True, "method": "coordinate"}
        if lightweight_locator:
            return {"success": False, "message": f"coordinate click failed: {keywords}", "coords": coords}

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

    if search_text and _selected_category_matches(search_text, locator=locator, log=log):
        if _has_product_info_markers(locator=locator, log=log):
            return {"success": True, "steps": ["already_past_category"]}
        if _is_category_next_enabled(locator=locator, log=log):
            results.append("selected_category_reused")

    if search_text and not results:
        search_input = _find_category_search_input(locator=locator, log=log)
        if not search_input and not _has_category_page_markers(locator=locator, log=log):
            return {"success": True, "steps": ["already_past_category"]}
        search_coords = (
            ((search_input["rect"].left + search_input["rect"].right) // 2, (search_input["rect"].top + search_input["rect"].bottom) // 2)
            if search_input
            else None
        )

        from actions.form import fill_text

        selected_variant = ""
        search_variants = _category_search_variants(search_text)
        for variant_index, search_variant in enumerate(search_variants):
            focus_result = _focus_category_search_input(
                search_variant,
                search_input=search_input,
                locator=locator,
                log=log,
            )
            if not focus_result.get("success"):
                return {"success": False, "message": "click category search input failed", "steps": results}

            fill_result = fill_text(
                search_variant,
                x=search_coords[0] if search_coords else None,
                y=search_coords[1] if search_coords else None,
                locator=locator,
                log=log,
            )
            if not fill_result["success"]:
                return {"success": False, "message": fill_result.get("message", "fill category search failed"), "steps": results}
            if "search" not in results:
                results.append("search")
            time.sleep(1.0)

            if _select_search_result(search_variant, search_input=search_input, locator=locator, log=log):
                if "search_select" not in results:
                    results.append("search_select")
                selected_variant = search_variant
                time.sleep(1.0)
                break

            if variant_index == len(search_variants) - 1:
                return {
                    "success": False,
                    "message": f"category search result not found: {search_text}; tried={search_variants}",
                    "steps": results,
                }

        if not _is_category_next_enabled(locator=locator, log=log):
            leaf_result = _select_leaf_category_candidate(selected_variant or search_text, locator=locator, log=log)
            if leaf_result.get("success"):
                results.append("leaf_select")
                time.sleep(1.0)
            if not _is_category_next_enabled(locator=locator, log=log):
                message = _build_category_disabled_reason(selected_variant or search_text, locator=locator, log=log)
                if leaf_result.get("success"):
                    message = (
                        f"{message}; last_leaf_candidate={leaf_result.get('name')}"
                    )
                    if leaf_result.get("attempted_names"):
                        message = f"{message}; attempted_leaf_candidates={leaf_result.get('attempted_names')}"
                elif leaf_result.get("message"):
                    message = f"{message}; leaf_select_error={leaf_result.get('message')}"
                    if leaf_result.get("attempted_names"):
                        message = f"{message}; attempted_leaf_candidates={leaf_result.get('attempted_names')}"
                return {
                    "success": False,
                    "message": message,
                    "steps": results,
                }

        if _has_product_info_markers(locator=locator, log=log):
            return {"success": True, "steps": results + ["product_info_ready"]}

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
    time.sleep(1.2)

    for _ in range(4):
        if _has_product_info_markers(locator=locator, log=log):
            return {"success": True, "steps": results}
        if not _has_category_page_markers(locator=locator, log=log) and not _is_category_next_enabled(locator=locator, log=log):
            return {"success": True, "steps": results}
        time.sleep(0.8)

    if search_text and _selected_category_matches(search_text, locator=locator, log=log) and _is_category_next_enabled(locator=locator, log=log):
        second_next = _click_category_next(locator=locator, log=log)
        if second_next.get("success"):
            results.append("next_retry")
            time.sleep(1.5)
            if _has_product_info_markers(locator=locator, log=log):
                return {"success": True, "steps": results}

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
