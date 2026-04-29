"""
京麦商品发布自动化 - 验证操作 Actions
覆盖 15 个脚本：结果验证、图像定位、状态检查
"""
import time
from typing import Dict, Any, Optional

from actions.registry import ActionRegistry


def _get_locator(locator=None, log=None):
    if locator is None:
        from infrastructure.locator import JingmaiLocator
        return JingmaiLocator(log=log)
    return locator


@ActionRegistry.register("verify_result", "verification", "验证执行结果")
def verify_result(check_errors: bool = True, locator=None, log=None) -> Dict[str, Any]:
    """验证当前页面状态，检查是否有错误"""
    locator = _get_locator(locator, log)

    result = {"success": True, "errors": [], "filled_count": 0}

    try:
        from pywinauto import Desktop
        desktop = Desktop(backend="uia")
        from infrastructure.locator import WINDOW_KEYWORDS

        for w in desktop.windows():
            title = w.window_text()
            if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                continue

            w.set_focus()
            time.sleep(0.3)

            if check_errors:
                error_indicators = ["错误", "失败", "异常", "error", "fail"]
                try:
                    for elem in w.descendants():
                        try:
                            name = (elem.element_info.name or "").lower()
                            ctrl_type = elem.element_info.control_type or ""
                            if any(ind in name for ind in error_indicators):
                                if ctrl_type in ("Text", "Button", "Pane"):
                                    result["errors"].append(elem.element_info.name)
                        except Exception:
                            continue
                except Exception:
                    pass

            # 统计已填写的编辑框
            try:
                edits = w.descendants(control_type="Edit")
                for edit in edits:
                    try:
                        value = edit.get_value()
                        if value and value.strip():
                            result["filled_count"] += 1
                    except Exception:
                        pass
            except Exception:
                pass

            break
    except Exception as e:
        result["errors"].append(str(e))
        result["success"] = False

    if result["errors"]:
        result["success"] = False

    return result


@ActionRegistry.register("find_element_by_image", "verification", "图像识别定位元素")
def find_element_by_image(template_path: str, confidence: float = 0.8,
                          locator=None, log=None) -> Dict[str, Any]:
    """通过图像模板匹配定位元素"""
    try:
        import pyautogui
        location = pyautogui.locateOnScreen(template_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            return {
                "success": True,
                "x": center.x,
                "y": center.y,
                "width": location.width,
                "height": location.height,
            }
    except Exception as e:
        return {"success": False, "message": str(e)}

    return {"success": False, "message": "图像未匹配"}


@ActionRegistry.register("check_status", "verification", "检查发布状态")
def check_status(locator=None, log=None) -> Dict[str, Any]:
    """检查商品发布状态"""
    locator = _get_locator(locator, log)

    # 截图保存用于分析
    screenshot = locator.take_screenshot()

    result = {
        "success": True,
        "status": "unknown",
        "screenshot": screenshot,
    }

    try:
        from pywinauto import Desktop
        desktop = Desktop(backend="uia")
        from infrastructure.locator import WINDOW_KEYWORDS

        for w in desktop.windows():
            title = w.window_text()
            if not any(kw in (title or "").lower() for kw in WINDOW_KEYWORDS):
                continue

            # 检查成功标识
            success_keywords = ["成功", "发布成功", "success", "已发布"]
            fail_keywords = ["失败", "错误", "error", "fail"]

            try:
                for elem in w.descendants():
                    try:
                        name = (elem.element_info.name or "").lower()
                        if any(kw in name for kw in success_keywords):
                            result["status"] = "success"
                            return result
                        if any(kw in name for kw in fail_keywords):
                            result["status"] = "failed"
                            result["success"] = False
                            return result
                    except Exception:
                        continue
            except Exception:
                pass
            break
    except Exception:
        pass

    return result
