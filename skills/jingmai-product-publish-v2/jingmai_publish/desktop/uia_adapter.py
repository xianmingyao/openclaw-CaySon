"""真实 Windows UIA 适配器第一版。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
import re
import time

from PIL import ImageGrab

from jingmai_publish.desktop.adapter import WindowInfo


IMAGE_UPLOAD_EMPTY_TEXTS = {"请上传图片", "请上传主图", "请上传透图"}


@dataclass(slots=True)
class UIATuningConfig:
    """UIA 命中调优配置。"""

    window_keywords: list[str] = field(default_factory=lambda: ["京麦", "Jingmai"])
    preferred_classes: list[str] = field(
        default_factory=lambda: ["Button", "MenuItem", "Hyperlink", "SplitButton", "ListItem", "Static", "Text"]
    )
    click_text_aliases: dict[str, list[str]] = field(default_factory=dict)


class RealWindowsUIAAdapter:
    """基于 pywinauto 的真实 Windows UIA 适配器。

    当前目标：
    - 列举桌面顶层窗口
    - 激活京麦窗口
    - 在窗口内按文本点击目标控件
    - 对窗口区域截图
    - 输出窗口枚举、候选控件和命中原因
    """

    def __init__(
        self,
        screenshot_dir: str | Path = "logs/screenshots",
        backend: str = "uia",
        tuning: UIATuningConfig | None = None,
    ) -> None:
        """初始化适配器。"""

        self.backend = backend
        self.tuning = tuning or UIATuningConfig()
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def _iter_desktops(self) -> list[Any]:
        """按顺序返回可用桌面后端。

        原因：
        - 某些窗口在 `uia` 下标题不完整
        - 某些窗口在 `win32` 下更容易被发现
        所以这里做双后端联合枚举。
        """

        Desktop, _ = self._import_pywinauto()
        backends = [self.backend]
        if self.backend != "win32":
            backends.append("win32")
        return [Desktop(backend=item) for item in backends]

    def _import_pywinauto(self) -> tuple[Any, Any]:
        """延迟导入 pywinauto，避免测试环境硬依赖。"""

        try:
            from pywinauto import Desktop
            from pywinauto.application import Application
        except ImportError as exc:
            raise RuntimeError(
                "真实 UIA 适配器需要安装 pywinauto。请先执行: pip install pywinauto pywin32"
            ) from exc
        return Desktop, Application

    @staticmethod
    def _normalize_handle(handle: str | int) -> int:
        """将窗口句柄归一化为整数。"""

        return int(str(handle), 0) if isinstance(handle, str) else int(handle)

    def list_windows(self) -> list[WindowInfo]:
        """列出当前桌面的可见顶层窗口。"""

        windows: list[WindowInfo] = []
        seen_handles: set[str] = set()

        for desktop in self._iter_desktops():
            try:
                desktop_windows = desktop.windows()
            except Exception:
                continue
            for window in desktop_windows:
                try:
                    title = window.window_text()
                    handle = window.handle
                    visible = bool(window.is_visible())
                    class_name = window.class_name()
                except Exception:
                    continue

                normalized_handle = str(handle)
                if normalized_handle in seen_handles:
                    continue

                display_title = title or class_name or normalized_handle
                if not display_title:
                    continue

                windows.append(
                    WindowInfo(
                        handle=normalized_handle,
                        title=display_title,
                        class_name=class_name,
                        visible=visible,
                    )
                )
                seen_handles.add(normalized_handle)
        return windows

    def _score_candidate(
        self,
        target_text: str,
        control_text: str,
        class_name: str,
    ) -> tuple[int, list[str]]:
        """为候选控件打分并返回命中原因。"""

        score = 0
        reasons: list[str] = []

        normalized_text = control_text.strip().lower()
        normalized_class = class_name.strip().lower()
        alias_targets = [target_text, *self.tuning.click_text_aliases.get(target_text, [])]
        normalized_targets = [item.strip().lower() for item in alias_targets if item.strip()]

        for normalized_target in normalized_targets:
            if normalized_text == normalized_target:
                score += 100
                reasons.append(f"exact_text:{normalized_target}")
                break
            if normalized_text.startswith(normalized_target):
                score += 70
                reasons.append(f"prefix_match:{normalized_target}")
                break
            if normalized_target in normalized_text:
                score += 50
                reasons.append(f"contains_match:{normalized_target}")
                break

        preferred_classes = {item.lower() for item in self.tuning.preferred_classes}
        if normalized_class in preferred_classes:
            score += 20
            reasons.append("preferred_class")

        if "发布" in normalized_text:
            score += 15
            reasons.append("publish_keyword")

        if "商品" in normalized_text:
            score += 10
            reasons.append("product_keyword")

        return score, reasons

    def _expand_target_texts(self, target_text: str) -> list[str]:
        """展开目标文本与其别名。"""

        expanded = [target_text, *self.tuning.click_text_aliases.get(target_text, [])]
        seen: set[str] = set()
        result: list[str] = []
        for item in expanded:
            normalized = item.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            result.append(normalized)
        return result

    def rank_candidate_controls(self, handle: str, text: str, limit: int = 20) -> list[dict[str, object]]:
        """按文本匹配程度和控件类型对候选控件排序。"""

        Desktop, _ = self._import_pywinauto()
        window = Desktop(backend=self.backend).window(handle=self._normalize_handle(handle))
        ranked: list[dict[str, object]] = []

        try:
            descendants = window.descendants()
        except Exception:
            return ranked

        for control in descendants:
            try:
                control_text = control.window_text()
                friendly_class_name = control.friendly_class_name()
                rectangle = control.rectangle()
            except Exception:
                continue

            if not control_text:
                continue

            score, reasons = self._score_candidate(text, control_text, friendly_class_name)
            if score <= 0:
                continue

            ranked.append(
                {
                    "text": control_text,
                    "class_name": friendly_class_name,
                    "score": score,
                    "reasons": reasons,
                    "bounds": {
                        "left": rectangle.left,
                        "top": rectangle.top,
                        "right": rectangle.right,
                        "bottom": rectangle.bottom,
                    },
                }
            )

        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked[:limit]

    def list_candidate_controls(self, handle: str, text: str, limit: int = 20) -> list[dict[str, object]]:
        """列出窗口内与目标文本相关的候选控件。"""

        return self.rank_candidate_controls(handle, text, limit=limit)

    def build_click_diagnostics(self, handle: str, text: str, limit: int = 20) -> dict[str, object]:
        """构建点击命中与回退策略诊断。"""

        ranked = self.rank_candidate_controls(handle, text, limit=limit)
        aliases = self._expand_target_texts(text)
        preferred_classes = self.tuning.preferred_classes

        ordered_attempts: list[dict[str, object]] = []
        for preferred_class in preferred_classes:
            for alias in aliases:
                for candidate in ranked:
                    if candidate["class_name"].lower() != preferred_class.lower():
                        continue
                    if alias.lower() not in candidate["text"].lower():
                        continue
                    ordered_attempts.append(
                        {
                            "strategy": "preferred_class_then_alias",
                            "target_alias": alias,
                            "preferred_class": preferred_class,
                            "candidate": candidate,
                        }
                    )

        if not ordered_attempts:
            for candidate in ranked:
                ordered_attempts.append(
                    {
                        "strategy": "score_fallback",
                        "target_alias": text,
                        "preferred_class": candidate["class_name"],
                        "candidate": candidate,
                    }
                )

        return {
            "target_text": text,
            "aliases": aliases,
            "preferred_classes": preferred_classes,
            "ranked_candidates": ranked,
            "attempts": ordered_attempts[:limit],
        }

    def build_window_debug_snapshot(self, keyword: str | None = None, limit: int = 20) -> dict[str, object]:
        """构建窗口调试快照。"""

        windows = self.list_windows()
        keywords = [keyword] if keyword else self.tuning.window_keywords
        candidates = []
        signature_candidates = []
        for window in windows:
            haystack = f"{window.title} {window.class_name or ''}".lower()
            item = {
                "handle": window.handle,
                "title": window.title,
                "class_name": window.class_name,
                "visible": window.visible,
            }
            if any(item_keyword.lower() in haystack for item_keyword in keywords):
                candidates.append(item)
            if (window.class_name or "").lower() == "jmmainframebase" or (window.title or "").lower().startswith("jd_"):
                signature_candidates.append(item)
        return {
            "total_window_count": len(windows),
            "window_keywords": keywords,
            "matched_windows": candidates[:limit],
            "signature_windows": signature_candidates[:limit],
        }

    def activate_window(self, handle: str) -> bool:
        """激活目标窗口。"""

        Desktop, _ = self._import_pywinauto()
        window = Desktop(backend=self.backend).window(handle=self._normalize_handle(handle))
        try:
            window.restore()
        except Exception:
            pass
        try:
            window.set_focus()
            return True
        except Exception:
            return False

    def _get_window(self, handle: str) -> Any:
        """按句柄获取 pywinauto 窗口对象。"""

        Desktop, _ = self._import_pywinauto()
        return Desktop(backend=self.backend).window(handle=self._normalize_handle(handle))

    def _get_control(self, handle: str, automation_id: str, control_type: str) -> Any:
        """按 automation_id 和控件类型定位子控件。

        京麦 WebView 会把 `jd-id-<动态前缀>-<字段序号>` 的前缀重新生成。
        这里先尝试精确命中，再按末尾字段序号兜底找当前可见控件。
        """

        window = self._get_window(handle)
        exact = window.child_window(auto_id=automation_id, control_type=control_type)
        try:
            if exact.exists(timeout=0.1):
                return exact
        except Exception:
            pass

        suffix = automation_id.rsplit("-", 1)[-1]
        if not suffix:
            return exact

        candidates = self._iter_controls_by_automation_id_suffix(window, suffix, control_type)
        if candidates:
            return candidates[0]
        return exact

    def click_text(self, handle: str, text: str) -> bool:
        """按候选评分结果点击最优控件。

        点击策略：
        - 先直接调用控件自身的 `click_input`
        - 再尝试 `wrapper_object().click_input`
        - 再尝试 `invoke`
        - 最后回退为矩形中心坐标点击
        """

        Desktop, _ = self._import_pywinauto()
        window = Desktop(backend=self.backend).window(handle=self._normalize_handle(handle))
        diagnostics = self.build_click_diagnostics(handle, text)
        attempts = diagnostics["attempts"]
        if not attempts:
            return False

        try:
            descendants = window.descendants()
        except Exception:
            return False

        for attempt in attempts:
            candidate = attempt["candidate"]
            for control in descendants:
                try:
                    control_text = control.window_text()
                    friendly_class_name = control.friendly_class_name()
                except Exception:
                    continue

                if control_text != candidate["text"]:
                    continue
                if friendly_class_name != candidate["class_name"]:
                    continue

                if self._click_control_with_fallback(control):
                    return True
        return False

    def click_text_by_index(self, handle: str, text: str, index: int = 0) -> bool:
        """按出现顺序点击指定文本控件。

        这个方法主要用于同文案重复出现的场景，例如图片上传区同时存在多个
        `请上传图片` 占位按钮时，需要显式点击第几个候选。
        """

        Desktop, _ = self._import_pywinauto()
        window = Desktop(backend=self.backend).window(handle=self._normalize_handle(handle))
        exact_matches: list[Any] = []

        try:
            descendants = window.descendants()
        except Exception:
            return False

        for control in descendants:
            try:
                control_text = (control.window_text() or "").strip()
            except Exception:
                continue
            if control_text == text:
                exact_matches.append(control)

        if not exact_matches or index < 0 or index >= len(exact_matches):
            return False

        exact_matches.sort(
            key=lambda item: (
                item.rectangle().top,
                item.rectangle().left,
            )
        )
        return self._click_control_with_fallback(exact_matches[index])

    def hover_text_by_index(self, handle: str, text: str, index: int = 0) -> bool:
        """按出现顺序悬浮指定文本控件。"""

        Desktop, _ = self._import_pywinauto()
        window = Desktop(backend=self.backend).window(handle=self._normalize_handle(handle))
        exact_matches: list[Any] = []

        try:
            descendants = window.descendants()
        except Exception:
            return False

        for control in descendants:
            try:
                control_text = (control.window_text() or "").strip()
            except Exception:
                continue
            if control_text == text:
                exact_matches.append(control)

        if not exact_matches or index < 0 or index >= len(exact_matches):
            return False

        exact_matches.sort(key=lambda item: (item.rectangle().top, item.rectangle().left))
        target = exact_matches[index]
        try:
            rect = target.rectangle()
            x = (rect.left + rect.right) // 2
            y = (rect.top + rect.bottom) // 2
            if x <= 0 or y <= 0:
                return False
            from pywinauto import mouse

            mouse.move(coords=(x, y))
            time.sleep(0.25)
            return True
        except Exception:
            return False

    def click_text_in_region(
        self,
        handle: str,
        text: str,
        *,
        min_x_ratio: float,
        max_x_ratio: float,
        min_y_ratio: float,
        max_y_ratio: float,
    ) -> bool:
        """在窗口相对区域内点击指定文本控件。"""

        candidates = self.rank_candidate_controls(handle, text, limit=30)
        if not candidates:
            return False
        window = self._get_window(handle)
        try:
            rect = window.rectangle()
        except Exception:
            return False
        width = max(1, rect.right - rect.left)
        height = max(1, rect.bottom - rect.top)

        filtered: list[dict[str, object]] = []
        for candidate in candidates:
            bounds = candidate["bounds"]
            center_x = (int(bounds["left"]) + int(bounds["right"])) / 2
            center_y = (int(bounds["top"]) + int(bounds["bottom"])) / 2
            x_ratio = (center_x - rect.left) / width
            y_ratio = (center_y - rect.top) / height
            if min_x_ratio <= x_ratio <= max_x_ratio and min_y_ratio <= y_ratio <= max_y_ratio:
                filtered.append(candidate)

        if not filtered:
            return False
        filtered.sort(key=lambda item: (item["score"], item["bounds"]["top"], item["bounds"]["left"]), reverse=True)
        return self._click_candidate_snapshot(handle, filtered[0])

    def click_window_ratio(self, handle: str, x_ratio: float, y_ratio: float) -> bool:
        """按窗口相对坐标点击。"""

        window = self._get_window(handle)
        try:
            rect = window.rectangle()
            width = max(1, rect.right - rect.left)
            height = max(1, rect.bottom - rect.top)
            x = int(rect.left + width * x_ratio)
            y = int(rect.top + height * y_ratio)
            if x <= 0 or y <= 0:
                return False
            from pywinauto import mouse

            mouse.click(button="left", coords=(x, y))
            return True
        except Exception:
            return False

    def click_text_near_bounds(
        self,
        handle: str,
        text: str,
        *,
        anchor_bounds: dict[str, int],
        max_dx: int = 500,
        max_dy: int = 250,
    ) -> bool:
        """点击指定边界附近的文本控件。"""

        candidates = self.rank_candidate_controls(handle, text, limit=30)
        if not candidates:
            return False
        anchor_center_x = (int(anchor_bounds["left"]) + int(anchor_bounds["right"])) / 2
        anchor_center_y = (int(anchor_bounds["top"]) + int(anchor_bounds["bottom"])) / 2

        filtered: list[tuple[float, dict[str, object]]] = []
        for candidate in candidates:
            bounds = candidate["bounds"]
            center_x = (int(bounds["left"]) + int(bounds["right"])) / 2
            center_y = (int(bounds["top"]) + int(bounds["bottom"])) / 2
            dx = abs(center_x - anchor_center_x)
            dy = abs(center_y - anchor_center_y)
            if dx <= max_dx and dy <= max_dy:
                filtered.append((dx + dy, candidate))

        if not filtered:
            return False
        filtered.sort(key=lambda item: item[0])
        return self._click_candidate_snapshot(handle, filtered[0][1])

    def click_image_upload_slot(self, handle: str, index: int = 0) -> bool:
        """点击 SKU 图片上传槽位。

        京麦图片槽位通常暴露成 `DataItem/ListItem`，不是标准按钮，因此单独收口。
        """

        window = self._get_window(handle)
        candidates: list[Any] = []

        try:
            descendants = window.descendants()
        except Exception:
            return False

        for control in descendants:
            try:
                control_text = (control.window_text() or "").strip()
                class_name = control.friendly_class_name()
                rect = control.rectangle()
            except Exception:
                continue

            if control_text not in IMAGE_UPLOAD_EMPTY_TEXTS:
                continue
            if class_name not in {"DataItem", "ListItem", "Button", "Pane"}:
                continue
            if rect.left == rect.right or rect.top == rect.bottom:
                continue
            candidates.append(control)

        if not candidates or index < 0 or index >= len(candidates):
            return False

        candidates.sort(key=lambda item: (item.rectangle().top, item.rectangle().left))
        target = candidates[index]
        if self._click_control_with_fallback(target):
            return True

        try:
            rect = target.rectangle()
            x = (rect.left + rect.right) // 2
            y = (rect.top + rect.bottom) // 2
            if x <= 0 or y <= 0:
                return False
            from pywinauto import mouse

            mouse.click(coords=(x, y))
            return True
        except Exception:
            return False

    def _click_candidate_snapshot(self, handle: str, candidate: dict[str, object]) -> bool:
        """按快照匹配真实控件并点击。"""

        window = self._get_window(handle)
        try:
            descendants = window.descendants()
        except Exception:
            return False

        for control in descendants:
            try:
                control_text = control.window_text()
                class_name = control.friendly_class_name()
                rect = control.rectangle()
            except Exception:
                continue
            if control_text != candidate["text"]:
                continue
            if class_name != candidate["class_name"]:
                continue
            bounds = candidate["bounds"]
            if (
                rect.left == int(bounds["left"])
                and rect.top == int(bounds["top"])
                and rect.right == int(bounds["right"])
                and rect.bottom == int(bounds["bottom"])
            ):
                return self._click_control_with_fallback(control)
        return False

    def hover_image_upload_slot(self, handle: str, index: int = 0) -> bool:
        """悬浮 SKU 图片上传槽位，触发“本地上传”悬浮入口。"""

        slots = self.inspect_image_upload_slots(handle)
        empty_slots = [slot for slot in slots if slot.get("status") == "empty"]
        if not empty_slots or index < 0 or index >= len(empty_slots):
            return False

        target = empty_slots[index]
        bounds = target["bounds"]
        x = (int(bounds["left"]) + int(bounds["right"])) // 2
        y = (int(bounds["top"]) + int(bounds["bottom"])) // 2
        if x <= 0 or y <= 0:
            return False

        try:
            from pywinauto import mouse

            mouse.move(coords=(x, y))
            time.sleep(0.25)
            return True
        except Exception:
            return False

    def click_existing_image_slot(self, handle: str, index: int = 0) -> bool:
        """点击已存在图片的 SKU 图片槽位，用于替换已有图片。"""

        slots = self.inspect_image_upload_slots(handle)
        image_slots = [slot for slot in slots if slot.get("class_name") == "Image"]
        if not image_slots or index < 0 or index >= len(image_slots):
            return False

        target = image_slots[index]
        bounds = target["bounds"]
        x = (int(bounds["left"]) + int(bounds["right"])) // 2
        y = (int(bounds["top"]) + int(bounds["bottom"])) // 2
        if x <= 0 or y <= 0:
            return False

        try:
            from pywinauto import mouse

            mouse.click(coords=(x, y))
            return True
        except Exception:
            return False

    def click_local_upload_entry(self, handle: str, index: int = 0) -> bool:
        """优先命中图片管理弹层或悬浮层中的“本地上传”。"""

        if self.click_text_in_region(
            handle,
            "本地上传",
            min_x_ratio=0.78,
            max_x_ratio=1.0,
            min_y_ratio=0.0,
            max_y_ratio=0.22,
        ):
            return True

        if self.click_text_in_region(
            handle,
            "本地上传",
            min_x_ratio=0.75,
            max_x_ratio=0.95,
            min_y_ratio=0.60,
            max_y_ratio=0.82,
        ):
            return True

        slots = self.inspect_image_upload_slots(handle)
        empty_slots = [slot for slot in slots if slot.get("status") == "empty"]
        if 0 <= index < len(empty_slots):
            if self.click_text_near_bounds(
                handle,
                "本地上传",
                anchor_bounds=empty_slots[index]["bounds"],
                max_dx=420,
                max_dy=220,
            ):
                return True

        return self.click_text(handle, "本地上传")

    def click_upload_image_entry(self, handle: str) -> bool:
        """点击“上传图片”按钮或下拉项。"""

        if self.click_text_in_region(
            handle,
            "上传图片",
            min_x_ratio=0.78,
            max_x_ratio=1.0,
            min_y_ratio=0.05,
            max_y_ratio=0.40,
        ):
            return True
        return self.click_text(handle, "上传图片")

    def close_image_preview_overlay(self, handle: str) -> bool:
        """关闭图片预览遮罩。

        京麦点击已上传图片时会打开预览层，右上角只有一个无文本叉号；该遮罩会挡住
        后续上传入口。这里先用 `100%` 缩放工具条作为轻量可见性信号，再点击页面右上
        角的关闭控件或坐标。
        """

        document_text = self.read_document_text(handle)
        if "100%" not in document_text:
            return False

        window = self._get_window(handle)
        try:
            window_rect = window.rectangle()
            descendants = window.descendants()
        except Exception:
            return False

        candidates: list[Any] = []
        min_left = window_rect.right - 140
        max_bottom = window_rect.top + 140
        for control in descendants:
            try:
                class_name = control.friendly_class_name()
                text = (control.window_text() or "").strip()
                rect = control.rectangle()
            except Exception:
                continue
            if rect.left < min_left or rect.top > max_bottom:
                continue
            width = rect.right - rect.left
            height = rect.bottom - rect.top
            if width <= 0 or height <= 0 or width > 90 or height > 90:
                continue
            if class_name in {"Button", "Image", "Custom", "Pane"} and text in {"", "关闭", "×", "x", "X"}:
                candidates.append(control)

        candidates.sort(key=lambda item: (item.rectangle().left, item.rectangle().top), reverse=True)
        for candidate in candidates:
            if self._click_control_with_fallback(candidate):
                time.sleep(0.3)
                return True

        try:
            from pywinauto import mouse

            mouse.click(coords=(window_rect.right - 55, window_rect.top + 55))
            time.sleep(0.3)
            return True
        except Exception:
            return False

    def prepare_publish_form_view(self, handle: str, *, home: bool = False) -> bool:
        """关闭残留弹层，并按需把发布表单滚回顶部。"""

        try:
            window = self._get_window(handle)
            window.set_focus()
            from pywinauto.keyboard import send_keys

            send_keys("{ESC}", pause=0.02)
            if home:
                time.sleep(0.05)
                send_keys("{HOME}", pause=0.02)
            time.sleep(0.1)
            return True
        except Exception:
            return False

    def select_uploaded_image_and_confirm(self, handle: str, file_path: str) -> dict[str, object]:
        """在图片管理弹层内选中上传结果并点击确认。"""

        file_name = Path(file_path).name
        file_stem = Path(file_path).stem
        selected = False
        selected_by = ""

        for _ in range(12):
            if self.click_text(handle, file_name) or self.click_text(handle, file_stem):
                selected = True
                selected_by = "file_name"
                break
            if self._click_first_picker_image_candidate(handle):
                selected = True
                selected_by = "first_image_candidate"
                break
            time.sleep(0.25)

        if not selected:
            return {"success": False, "error": "picker_uploaded_image_not_selectable"}

        for _ in range(6):
            if self.click_text_in_region(
                handle,
                "确定",
                min_x_ratio=0.86,
                max_x_ratio=1.0,
                min_y_ratio=0.86,
                max_y_ratio=1.0,
            ):
                return {"success": True, "selected": file_name, "selected_by": selected_by}
            if self.click_text(handle, "确定"):
                return {"success": True, "selected": file_name, "selected_by": selected_by}
            time.sleep(0.2)

        return {"success": False, "error": "picker_confirm_button_not_clicked"}

    def _click_first_picker_image_candidate(self, handle: str) -> bool:
        """图片空间常只暴露缩略图，不暴露文件名；回退点击首个缩略图候选。"""

        window = self._get_window(handle)
        candidates: list[tuple[int, int, Any]] = []
        try:
            descendants = window.descendants()
        except Exception:
            return False

        for control in descendants:
            try:
                class_name = control.friendly_class_name()
                text = (control.window_text() or "").strip()
                rect = control.rectangle()
            except Exception:
                continue
            if not self._is_picker_image_candidate(class_name, text, rect.left, rect.top, rect.right, rect.bottom):
                continue
            candidates.append((rect.top, rect.left, control))

        if not candidates:
            return False

        candidates.sort(key=lambda item: (item[0], item[1]))
        return self._click_control_with_fallback(candidates[0][2])

    @staticmethod
    def _is_picker_image_candidate(
        class_name: str,
        text: str,
        left: int,
        top: int,
        right: int,
        bottom: int,
    ) -> bool:
        """判断控件是否像图片空间里的可选图片缩略图。"""

        width = right - left
        height = bottom - top
        if left <= 0 or top <= 0 or width < 56 or height < 56:
            return False
        if width > 420 or height > 420:
            return False
        if text in {"请上传图片", "本地上传", "上传图片", "确定", "取消"}:
            return False
        if class_name == "Image":
            return True
        if class_name in {"ListItem", "DataItem", "Pane"} and not text:
            return True
        return False

    def read_document_text(self, handle: str) -> str:
        """读取窗口中最长的 Document 文本。"""

        window = self._get_window(handle)
        best_text = ""
        for control in window.descendants():
            try:
                if control.friendly_class_name() != "Document":
                    continue
                text = control.window_text() or ""
            except Exception:
                continue
            if len(text) > len(best_text):
                best_text = text
        return best_text

    def fill_edit_by_automation_id(self, handle: str, automation_id: str, value: str) -> bool:
        """按 automation_id 填写输入框。"""

        try:
            control = self._get_control(handle, automation_id, "Edit")
        except Exception:
            return False
        return self._fill_edit_control(control, value)

    def select_combobox_by_automation_id(self, handle: str, automation_id: str, value: str) -> bool:
        """按 automation_id 选择下拉框值。"""

        try:
            control = self._get_control(handle, automation_id, "ComboBox")
        except Exception:
            return False
        return self._select_combobox_control(control, value)

    def fill_edit_by_label(self, handle: str, label: str, value: str) -> bool:
        """按字段标签定位输入框并写值。"""

        for target_class in ("Edit", "Document", "Pane"):
            control = self._find_control_near_label(handle, label, target_class)
            if control is not None and self._fill_edit_control(control, value):
                return True
        return False

    def select_combobox_by_label(self, handle: str, label: str, value: str) -> bool:
        """按字段标签定位下拉框并选择值。"""

        for target_class in ("ComboBox", "Edit", "Pane"):
            control = self._find_control_near_label(handle, label, target_class)
            if control is not None and self._select_combobox_control(control, value):
                return True
        return False

    def probe_select_options_by_label(self, handle: str, label: str) -> dict[str, object]:
        """按字段标签探测下拉框的当前可见选项。"""

        control = None
        for target_class in ("ComboBox", "Edit", "Pane"):
            control = self._find_control_near_label(handle, label, target_class)
            if control is not None:
                break

        if control is None:
            return {"success": False, "label": label, "options": [], "reason": "control_not_found"}

        activation = self._activate_control_with_fallback(control)
        time.sleep(0.3)
        options = self._collect_popup_options(control)
        if not options:
            options = self._collect_nearby_text_options(control)

        try:
            from pywinauto.keyboard import send_keys

            send_keys("{ESC}", pause=0.02)
        except Exception:
            pass

        return {
            "success": activation["success"],
            "label": label,
            "activation_method": activation["method"],
            "options": options,
        }

    def _fill_edit_control(self, control: Any, value: str) -> bool:
        """对已经定位到的输入控件执行写值。"""

        try:
            rect = control.rectangle()
            if rect.right > rect.left and rect.bottom > rect.top:
                from pywinauto import mouse
                from pywinauto.keyboard import send_keys

                mouse.click(coords=((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2))
                time.sleep(0.1)
                send_keys("^a{BACKSPACE}", pause=0.02)
                if self._should_paste_text(value):
                    self._paste_text(value)
                else:
                    send_keys(value, with_spaces=True, pause=0.02)
                send_keys("{TAB}", pause=0.02)
                return True
        except Exception:
            pass

        try:
            wrapper = control.wrapper_object()
            control.set_focus()
        except Exception:
            return False

        try:
            wrapper.set_edit_text(value)
            return True
        except Exception:
            try:
                wrapper.click_input()
                wrapper.type_keys("^a{BACKSPACE}", set_foreground=False)
                if self._should_paste_text(value):
                    self._paste_text(value)
                else:
                    wrapper.type_keys(value, with_spaces=True, set_foreground=False)
                wrapper.type_keys("{TAB}", set_foreground=False)
                return True
            except Exception:
                return False

    def _select_combobox_control(self, control: Any, value: str) -> bool:
        """对已经定位到的下拉控件执行选择。

        这里优先遵守“下拉选择”语义：
        1. 先尝试原生 `select`
        2. 再打开下拉弹层并点击真实选项
        3. 最后才退回到键盘输入+回车
        """

        try:
            wrapper = control.wrapper_object()
        except Exception:
            wrapper = None
        try:
            control.set_focus()
        except Exception:
            pass
        try:
            from pywinauto.keyboard import send_keys

            send_keys("{ESC}", pause=0.02)
            time.sleep(0.1)
            control.set_focus()
        except Exception:
            pass

        for open_method in ("center_click", "center_click_retry"):
            try:
                if not self._click_control_center(control):
                    continue
                time.sleep(0.25)
                options = self._collect_popup_options(control)
                if self._click_option_from_popup(control, value, options):
                    return True
                nearby_options = self._collect_nearby_text_options(control)
                if self._click_option_from_popup(control, value, nearby_options):
                    return True
            except Exception:
                continue

        try:
            self._activate_control_with_fallback(control)
            self._type_text_and_submit(value)
            return True
        except Exception:
            return False

    def _find_control_near_label(self, handle: str, label: str, target_class: str) -> Any | None:
        """按标签文本就近定位输入框或下拉框。"""

        window = self._get_window(handle)
        window_rect = window.rectangle()
        window_width = max(window_rect.right - window_rect.left, 1)
        form_left_boundary = window_rect.left + int(window_width * 0.20)
        label_controls: list[Any] = []
        target_candidates: list[Any] = []
        direct_target_matches: list[Any] = []
        normalized_label = self._normalize_label_text(label)

        for control in window.descendants():
            try:
                class_name = control.friendly_class_name()
                control_text = (control.window_text() or "").strip()
                rect = control.rectangle()
            except Exception:
                continue

            if target_class == class_name and rect.left >= form_left_boundary:
                target_candidates.append(control)
                if (
                    control_text
                    and normalized_label
                    and normalized_label in self._normalize_label_text(control_text)
                    and len(control_text) <= 40
                ):
                    direct_target_matches.append(control)

            if (
                control_text
                and normalized_label
                and normalized_label in self._normalize_label_text(control_text)
                and class_name != "Document"
                and class_name != target_class
                and len(control_text) <= 40
                and rect.left >= form_left_boundary
            ):
                label_controls.append(control)

        strong_direct_matches = [
            control
            for control in direct_target_matches
            if self._normalize_label_text((control.window_text() or "").strip()).startswith(normalized_label)
        ]
        if strong_direct_matches:
            return sorted(
                strong_direct_matches,
                key=lambda item: (
                    item.rectangle().top,
                    item.rectangle().left,
                    len((item.window_text() or "").strip()),
                ),
            )[0]

        if not label_controls or not target_candidates:
            if direct_target_matches:
                return sorted(
                    direct_target_matches,
                    key=lambda item: (
                        item.rectangle().top,
                        item.rectangle().left,
                        len((item.window_text() or "").strip()),
                    ),
                )[0]
            return None

        best_control: Any | None = None
        best_score: tuple[int, int, int] | None = None

        for label_control in label_controls:
            try:
                label_rect = label_control.rectangle()
            except Exception:
                continue

            for candidate in target_candidates:
                try:
                    candidate_rect = candidate.rectangle()
                except Exception:
                    continue

                vertical_gap = candidate_rect.top - label_rect.bottom
                if vertical_gap < -10 or vertical_gap > 140:
                    continue

                horizontal_gap = abs(candidate_rect.left - label_rect.left)
                overlap = min(label_rect.right, candidate_rect.right) - max(label_rect.left, candidate_rect.left)
                overlap_penalty = 0 if overlap > 0 else 1
                score = (overlap_penalty, vertical_gap, horizontal_gap)

                if best_score is None or score < best_score:
                    best_score = score
                    best_control = candidate

        return best_control

    def _collect_popup_options(self, anchor_control: Any) -> list[dict[str, object]]:
        """采集下拉弹层中当前可见的候选项。"""

        try:
            anchor_rect = anchor_control.rectangle()
        except Exception:
            return []

        collected: dict[tuple[str, str, int, int], dict[str, object]] = {}
        option_classes = {"ListItem", "Text", "MenuItem", "DataItem"}
        anchor_width = max(anchor_rect.right - anchor_rect.left, 1)
        anchor_center_x = int((anchor_rect.left + anchor_rect.right) / 2)

        try:
            descendants = anchor_control.top_level_parent().descendants()
        except Exception:
            descendants = []

        for control in descendants:
            try:
                class_name = control.friendly_class_name()
                text = (control.window_text() or "").strip()
                rect = control.rectangle()
            except Exception:
                continue

            if class_name not in option_classes or not text:
                continue
            if "\n" in text or len(text) > 80:
                continue
            if rect.left == rect.right or rect.top == rect.bottom:
                continue
            if rect.top < anchor_rect.top - 360 or rect.top > anchor_rect.bottom + 360:
                continue
            option_width = rect.right - rect.left
            option_center_x = int((rect.left + rect.right) / 2)
            if option_width > max(int(anchor_width * 1.6), 420):
                continue
            if abs(option_center_x - anchor_center_x) > max(int(anchor_width * 0.8), 120):
                continue
            horizontal_overlap = min(rect.right, anchor_rect.right) - max(rect.left, anchor_rect.left)
            if horizontal_overlap < 40 and abs(rect.left - anchor_rect.left) > 120:
                continue

            key = (text, class_name, rect.left, rect.top)
            collected[key] = {
                "text": text,
                "class_name": class_name,
                "bounds": {
                    "left": rect.left,
                    "top": rect.top,
                    "right": rect.right,
                    "bottom": rect.bottom,
                },
            }

        return sorted(
            collected.values(),
            key=lambda item: (
                abs(item["bounds"]["top"] - anchor_rect.bottom),
                abs(int((item["bounds"]["left"] + item["bounds"]["right"]) / 2) - anchor_center_x),
                item["bounds"]["top"],
                item["bounds"]["left"],
            ),
        )

    def _collect_nearby_text_options(self, anchor_control: Any) -> list[dict[str, object]]:
        """采集锚点附近以普通文本渲染的候选项。

        某些京麦下拉不会暴露标准 ListItem，而是直接把可选值渲染在页面文档层。
        这里做一次更宽松但仍受锚点几何约束的邻近文本采集。
        """

        try:
            anchor_rect = anchor_control.rectangle()
            window = anchor_control.top_level_parent()
            descendants = window.descendants()
        except Exception:
            return []

        collected: dict[tuple[str, str, int, int], dict[str, object]] = {}
        option_classes = {"Text", "ListItem", "MenuItem", "Static", "Hyperlink", "DataItem"}
        anchor_width = max(anchor_rect.right - anchor_rect.left, 1)
        anchor_center_x = int((anchor_rect.left + anchor_rect.right) / 2)

        for control in descendants:
            try:
                class_name = control.friendly_class_name()
                text = (control.window_text() or "").strip()
                rect = control.rectangle()
            except Exception:
                continue

            if class_name not in option_classes or not text:
                continue
            if "\n" in text or len(text) > 40:
                continue
            if rect.left == rect.right or rect.top == rect.bottom:
                continue
            if rect.top < anchor_rect.top - 20 or rect.top > anchor_rect.bottom + 260:
                continue

            option_width = rect.right - rect.left
            option_center_x = int((rect.left + rect.right) / 2)
            if option_width > max(int(anchor_width * 1.8), 320):
                continue
            if abs(option_center_x - anchor_center_x) > max(int(anchor_width * 1.4), 180):
                continue

            key = (text, class_name, rect.left, rect.top)
            collected[key] = {
                "text": text,
                "class_name": class_name,
                "bounds": {
                    "left": rect.left,
                    "top": rect.top,
                    "right": rect.right,
                    "bottom": rect.bottom,
                },
            }

        return sorted(
            collected.values(),
            key=lambda item: (
                abs(item["bounds"]["top"] - anchor_rect.bottom),
                abs(int((item["bounds"]["left"] + item["bounds"]["right"]) / 2) - anchor_center_x),
                item["bounds"]["top"],
                item["bounds"]["left"],
            ),
        )

    def _click_option_from_popup(self, anchor_control: Any, value: str, options: list[dict[str, object]]) -> bool:
        """从弹层候选中点击最匹配的选项。"""

        normalized_target = self._normalize_label_text(value)
        best_option: dict[str, object] | None = None

        for option in options:
            option_text = str(option["text"])
            normalized_option = self._normalize_label_text(option_text)
            if normalized_option == normalized_target or normalized_target in normalized_option:
                best_option = option
                break

        if best_option is None:
            return False

        bounds = best_option["bounds"]
        x = int((bounds["left"] + bounds["right"]) / 2)
        y = int((bounds["top"] + bounds["bottom"]) / 2)
        if x <= 0 or y <= 0:
            return False

        try:
            from pywinauto import mouse

            mouse.click(coords=(x, y))
            return True
        except Exception:
            return False

    def _type_text_and_submit(self, value: str) -> None:
        """向当前焦点控件输入文本并回车提交。"""

        from pywinauto.keyboard import send_keys

        send_keys("^a{BACKSPACE}", pause=0.02)
        if self._should_paste_text(value):
            self._paste_text(value)
        else:
            send_keys(value, pause=0.02)
        send_keys("{ENTER}", pause=0.02)

    @staticmethod
    def _should_paste_text(value: str) -> bool:
        """判断当前值是否更适合走剪贴板粘贴。"""

        if len(value) > 20:
            return True
        if any(ord(char) > 127 for char in value):
            return True
        return any(symbol in value for symbol in [".", "-", "/", "*", "，", "、"])

    @staticmethod
    def _normalize_label_text(text: str) -> str:
        """归一化标签文本，去掉空白和常见装饰字符。"""

        normalized = re.sub(r"[\s\*\(\)（）:：]", "", text)
        return normalized.strip().lower()

    def build_sku_probe(self, handle: str) -> dict[str, object]:
        """构建 SKU 区域探针结果。

        目的：
        - 观察动态 automation_id 是否会短暂出现
        - 区分可见控件和虚拟化控件
        - 为后续 T5 单元格激活策略提供证据
        """

        window = self._get_window(handle)
        automation_pattern = re.compile(r"jd-id-\d+-3\d+")
        samples: dict[tuple[str, str], dict[str, object]] = {}

        for _ in range(3):
            for control in window.descendants():
                try:
                    class_name = control.friendly_class_name()
                    automation_id = control.element_info.automation_id or ""
                    text = control.window_text() or ""
                    rect = control.rectangle()
                except Exception:
                    continue

                if not automation_pattern.fullmatch(automation_id):
                    continue

                key = (automation_id, class_name)
                item = samples.setdefault(
                    key,
                    {
                        "automation_id": automation_id,
                        "class_name": class_name,
                        "texts": [],
                        "rects": [],
                        "seen_count": 0,
                    },
                )
                item["seen_count"] += 1
                if text and text not in item["texts"]:
                    item["texts"].append(text)
                current_rect = (rect.left, rect.top, rect.right, rect.bottom)
                if current_rect not in item["rects"]:
                    item["rects"].append(current_rect)
            time.sleep(0.15)

        document_text = self.read_document_text(handle)
        interesting_keywords = [
            "销售属性",
            "商品名称",
            "市场价",
            "采购价",
            "京东价",
            "SKU属性",
            "重量",
            "长 (毫米)",
            "宽 (毫米)",
            "高 (毫米)",
        ]

        return {
            "document_keyword_hits": {
                keyword: keyword in document_text for keyword in interesting_keywords
            },
            "dynamic_controls": sorted(
                samples.values(),
                key=lambda item: (item["seen_count"], item["automation_id"]),
                reverse=True,
            ),
        }

    def activate_cell_by_automation_id(self, handle: str, automation_id: str) -> dict[str, object]:
        """按 automation_id 激活 SKU 单元格。

        这里不假设它一定是稳定的 Edit 控件，而是先枚举同 auto_id 的候选，
        再依次尝试焦点、点击和 invoke 回退。
        """

        window = self._get_window(handle)
        candidates: list[dict[str, object]] = []

        for control in self._iter_controls_by_automation_id(window, automation_id):
            try:
                class_name = control.friendly_class_name()
                text = control.window_text() or ""
                rectangle = control.rectangle()
            except Exception:
                continue

            activation = self._activate_control_with_fallback(control)
            candidates.append(
                {
                    "automation_id": automation_id,
                    "class_name": class_name,
                    "text": text,
                    "bounds": {
                        "left": rectangle.left,
                        "top": rectangle.top,
                        "right": rectangle.right,
                        "bottom": rectangle.bottom,
                    },
                    "activation_success": activation["success"],
                    "activation_method": activation["method"],
                }
            )
            if activation["success"]:
                return {
                    "success": True,
                    "automation_id": automation_id,
                    "selected_candidate": candidates[-1],
                    "candidate_count": len(candidates),
                    "candidates": candidates,
                }

        return {
            "success": False,
            "automation_id": automation_id,
            "selected_candidate": None,
            "candidate_count": len(candidates),
            "candidates": candidates,
        }

    def type_into_focused_control(self, handle: str, value: str, submit: bool = False) -> dict[str, object]:
        """向当前焦点控件发送键盘输入。

        该方法用于 SKU 虚拟化单元格实验。它只负责键盘注入和结果观测，
        不负责目标单元格定位。
        """

        try:
            from pywinauto.keyboard import send_keys
        except ImportError as exc:
            raise RuntimeError("键盘输入能力需要 pywinauto.keyboard") from exc

        before_text = self.read_document_text(handle)
        window = self._get_window(handle)

        try:
            window.set_focus()
        except Exception:
            pass

        try:
            send_keys("^a{BACKSPACE}", pause=0.02)
            if self._should_paste_text(value):
                self._paste_text(value)
            else:
                send_keys(value, with_spaces=True, pause=0.02)
            if submit:
                send_keys("{ENTER}", pause=0.02)
        except Exception as exc:
            return {
                "success": False,
                "value": value,
                "submit": submit,
                "error": str(exc),
                "before_contains": value in before_text,
                "after_contains": False,
            }

        time.sleep(0.2)
        after_text = self.read_document_text(handle)
        return {
            "success": True,
            "value": value,
            "submit": submit,
            "before_contains": value in before_text,
            "after_contains": value in after_text,
        }

    def type_into_detail_editor(self, handle: str, value: str) -> dict[str, object]:
        """定位商品详情编辑区并写入内容。

        京麦详情区是 WebView 富文本区，不能只依赖“当前焦点”。这里先点击
        `商详/代码编辑/高级编辑` 下方的编辑画布，再通过剪贴板粘贴写入。
        """

        before_text = self.read_document_text(handle)
        focus_result = self._focus_detail_editor_body(handle)
        if not focus_result.get("success"):
            focus_result.update({"value": value, "after_contains": False})
            return focus_result

        typing_result = self.type_into_focused_control(handle, value, submit=False)
        typing_result["focus_method"] = focus_result.get("method")
        typing_result["focus_point"] = focus_result.get("point")
        typing_result["before_contains"] = value in before_text
        return typing_result


    def _focus_detail_editor_body(self, handle: str) -> dict[str, object]:
        """点击真实详情编辑画布区域，避免输入落到导航或资源弹层。"""

        window = self._get_window(handle)
        try:
            from pywinauto import mouse

            window.set_focus()
            window_rect = window.rectangle()
            descendants = window.descendants()
        except Exception as exc:
            return {"success": False, "method": "detail_editor_body", "error": str(exc)}

        width = max(window_rect.right - window_rect.left, 1)
        height = max(window_rect.bottom - window_rect.top, 1)

        for control in descendants:
            try:
                text = (control.window_text() or "").strip()
                rect = control.rectangle()
            except Exception:
                continue
            if text not in {"请输入正文", "请补充商品描述"}:
                continue
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2
            x_ratio = (center_x - window_rect.left) / width
            y_ratio = (center_y - window_rect.top) / height
            if not (0.35 <= x_ratio <= 0.95 and 0.65 <= y_ratio <= 0.98):
                continue
            try:
                canvas_x = min(center_x + 260, window_rect.right - 180)
                canvas_y = max(center_y - 60, window_rect.top + int(height * 0.45))
                mouse.click(coords=(canvas_x, canvas_y))
                time.sleep(0.25)
                return {
                    "success": True,
                    "method": "placeholder_canvas",
                    "point": {"x": canvas_x, "y": canvas_y},
                }
            except Exception:
                continue

        anchors: list[tuple[int, int, int, Any]] = []
        anchor_keywords = ["商详", "代码编辑", "高级编辑", "图文编辑", "详情预览", "商品详情"]
        for control in descendants:
            try:
                text = (control.window_text() or "").strip()
                rect = control.rectangle()
            except Exception:
                continue
            if not text:
                continue
            if any(keyword in text for keyword in anchor_keywords):
                if "代码编辑" in text:
                    priority = 0
                elif "高级编辑" in text:
                    priority = 1
                elif "图文编辑" in text:
                    priority = 2
                elif "商详" in text:
                    priority = 3
                elif "详情预览" in text:
                    priority = 4
                else:
                    priority = 5
                anchors.append((priority, rect.top, rect.left, control))

        click_points: list[tuple[int, int, str]] = [
            (window_rect.left + int(width * 0.405), window_rect.top + int(height * 0.323), "ratio_code_body_top"),
        ]
        for _, _, _, control in sorted(anchors, key=lambda item: (item[0], item[1], item[2])):
            try:
                rect = control.rectangle()
                text = (control.window_text() or "").strip()
            except Exception:
                continue
            if "详情预览" in text:
                click_points.append((rect.right + 120, rect.bottom + 120, "preview_anchor"))
            elif "商详" in text:
                click_points.append((rect.left + 20, rect.bottom + 120, "detail_anchor"))
            elif any(keyword in text for keyword in ["代码编辑", "高级编辑", "图文编辑"]):
                click_points.append((rect.left - 140, rect.bottom + 90, "mode_anchor"))
            elif "商品详情" in text:
                click_points.append((rect.left + 360, rect.bottom + 160, "section_anchor"))

        click_points.extend(
            [
                (window_rect.left + int(width * 0.405), window_rect.top + int(height * 0.815), "ratio_code_body_bottom"),
                (window_rect.left + int(width * 0.62), window_rect.top + int(height * 0.72), "ratio_body_primary"),
                (window_rect.left + int(width * 0.52), window_rect.top + int(height * 0.68), "ratio_body_secondary"),
            ]
        )

        for raw_x, raw_y, method in click_points:
            x = max(window_rect.left + int(width * 0.38), min(raw_x, window_rect.right - 120))
            y = max(window_rect.top + int(height * 0.45), min(raw_y, window_rect.bottom - 120))
            if x <= 0 or y <= 0:
                continue
            try:
                mouse.click(coords=(x, y))
                time.sleep(0.25)
                return {"success": True, "method": method, "point": {"x": x, "y": y}}
            except Exception:
                continue

        return {"success": False, "method": "detail_editor_body", "error": "no_click_point_succeeded"}

    def _paste_text(self, value: str) -> None:
        """通过剪贴板粘贴文本，避免小数点在键盘注入时丢失。"""

        try:
            import win32clipboard  # type: ignore
            from pywinauto.keyboard import send_keys
        except ImportError:
            from pywinauto.keyboard import send_keys

            send_keys(value, with_spaces=True, pause=0.02)
            return

        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(value)
        finally:
            win32clipboard.CloseClipboard()

        send_keys("^v", pause=0.02)

    def upload_file_from_active_dialog(self, file_path: str) -> dict[str, object]:
        """向当前激活的系统文件对话框写入本地文件路径。

        优先接管当前激活窗口，只处理典型的资源管理器/文件选择窗口：
        - `CabinetWClass`
        - `#32770`
        """

        resolved_path = str(Path(file_path).resolve())
        dialog_candidates = self._list_file_dialog_candidates()

        if not dialog_candidates:
            return {
                "success": False,
                "file_path": resolved_path,
                "error": "active_file_dialog_not_found",
            }

        for candidate in dialog_candidates:
            result = self._upload_file_via_dialog_candidate(candidate, resolved_path)
            if result.get("success"):
                return result

        return {
            "success": False,
            "file_path": resolved_path,
            "error": "all_dialog_candidates_failed",
            "candidates": dialog_candidates,
        }

    def inspect_image_upload_slots(self, handle: str) -> list[dict[str, object]]:
        """读取当前图片上传槽位状态。"""

        window = self._get_window(handle)
        snapshots: list[dict[str, object]] = []

        for control in window.descendants():
            try:
                class_name = control.friendly_class_name()
                text = (control.window_text() or "").strip()
                rect = control.rectangle()
            except Exception:
                continue

            if not self._is_image_upload_slot_candidate(class_name, text, rect.left, rect.top, rect.right, rect.bottom):
                continue

            raw_snapshot = {
                "class_name": class_name,
                "text": text,
                "bounds": {
                    "left": rect.left,
                    "top": rect.top,
                    "right": rect.right,
                    "bottom": rect.bottom,
                },
            }
            normalized_snapshot = self._normalize_image_upload_slot_snapshot(raw_snapshot)
            if normalized_snapshot is None:
                continue
            self._merge_image_upload_slot_snapshot(snapshots, normalized_snapshot)

        snapshots.sort(key=self._image_upload_slot_sort_key)
        return snapshots

    @staticmethod
    def _image_upload_slot_sort_key(item: dict[str, object]) -> tuple[int, int, int, str]:
        """同一 SKU 行内按从左到右排序，避免方图/透图因控件 top 差异颠倒。"""

        bounds = item["bounds"]
        top = int(bounds["top"])
        left = int(bounds["left"])
        return (top // 150, left, top, str(item.get("class_name") or ""))

    @staticmethod
    def _is_image_upload_slot_candidate(
        class_name: str,
        text: str,
        left: int,
        top: int,
        right: int,
        bottom: int,
    ) -> bool:
        """判断控件是否属于京麦 SKU 图片上传槽区域。"""

        if left < 600 or right <= left or bottom <= top:
            return False

        # 真实页面中上传槽可能出现在 300~460，也可能在页面下方旧布局的 650~850。
        in_primary_band = 280 <= top <= 470 and 280 <= bottom <= 470
        in_legacy_band = 650 <= top <= 850 and 650 <= bottom <= 850
        if not (in_primary_band or in_legacy_band):
            return False

        if class_name == "DataItem" and text in IMAGE_UPLOAD_EMPTY_TEXTS:
            return True
        if class_name in {"ListItem", "ListBox"}:
            return True
        if class_name == "Image":
            # 顶部标题旁的小提示 icon 不应算上传槽。
            return top >= 220
        if class_name == "Button" and text in IMAGE_UPLOAD_EMPTY_TEXTS | {"+"}:
            return True
        return False

    @staticmethod
    def _normalize_image_upload_slot_snapshot(snapshot: dict[str, object]) -> dict[str, object] | None:
        """将原始 UIA 控件归一化为槽位状态，避免空槽中的加号图标被误算为已上传图片。"""

        bounds = snapshot["bounds"]
        left = int(bounds["left"])
        top = int(bounds["top"])
        right = int(bounds["right"])
        bottom = int(bounds["bottom"])
        width = right - left
        height = bottom - top
        class_name = str(snapshot.get("class_name") or "")
        text = str(snapshot.get("text") or "")

        if width <= 0 or height <= 0:
            return None

        status = ""
        normalized_class_name = class_name
        normalized_text = text

        if text in IMAGE_UPLOAD_EMPTY_TEXTS:
            # 过宽的 DataItem 往往是整行容器，不直接作为单个槽位返回。
            if class_name == "DataItem" and width > 450:
                return None
            status = "empty"
            normalized_class_name = "DataItem"
            normalized_text = text
        elif class_name in {"ListItem", "ListBox", "Button", "Pane"}:
            # 京麦空槽常暴露为 ListItem/ListBox，文本可能为空。
            if width < 60 or height < 60:
                return None
            status = "empty"
            normalized_class_name = "DataItem"
            normalized_text = "请上传图片"
        elif class_name == "Image":
            # 空槽里的加号 icon 很小，不应被当成已上传图片。
            if width <= 48 and height <= 48:
                return None
            status = "filled"
            normalized_class_name = "Image"
            normalized_text = ""
        else:
            return None

        return {
            "class_name": normalized_class_name,
            "text": normalized_text,
            "status": status,
            "bounds": {
                "left": left,
                "top": top,
                "right": right,
                "bottom": bottom,
            },
        }

    @staticmethod
    def _merge_image_upload_slot_snapshot(
        snapshots: list[dict[str, object]],
        candidate: dict[str, object],
    ) -> None:
        """合并同一槽位的多个控件快照，输出单一槽位状态。"""

        candidate_bounds = candidate["bounds"]
        candidate_left = int(candidate_bounds["left"])
        candidate_top = int(candidate_bounds["top"])
        candidate_right = int(candidate_bounds["right"])
        candidate_bottom = int(candidate_bounds["bottom"])
        candidate_width = candidate_right - candidate_left
        candidate_height = candidate_bottom - candidate_top
        candidate_center_x = (candidate_left + candidate_right) // 2
        candidate_center_y = (candidate_top + candidate_bottom) // 2

        for snapshot in snapshots:
            bounds = snapshot["bounds"]
            left = int(bounds["left"])
            top = int(bounds["top"])
            right = int(bounds["right"])
            bottom = int(bounds["bottom"])
            center_x = (left + right) // 2
            center_y = (top + bottom) // 2

            overlaps_horizontally = min(right, candidate_right) - max(left, candidate_left) > 0
            overlaps_vertically = min(bottom, candidate_bottom) - max(top, candidate_top) > 0
            centers_close = abs(center_x - candidate_center_x) <= 80 and abs(center_y - candidate_center_y) <= 80

            if not ((overlaps_horizontally and overlaps_vertically) or centers_close):
                continue

            snapshot_status = str(snapshot.get("status") or "")
            candidate_status = str(candidate.get("status") or "")
            snapshot_area = (right - left) * (bottom - top)
            candidate_area = candidate_width * candidate_height

            # 同槽位里若出现 empty 与 filled 冲突，小图标仍按空槽处理；
            # 大图则更可能是上传后缩略图，应升级为 filled。
            if snapshot_status == "empty" and candidate_status == "filled" and candidate_area <= 48 * 48:
                return
            if snapshot_status == "empty" and candidate_status == "filled":
                snapshot["class_name"] = candidate["class_name"]
                snapshot["text"] = candidate["text"]
                snapshot["status"] = candidate_status
                snapshot["bounds"] = candidate["bounds"]
                return
            if snapshot_status == "filled" and candidate_status == "empty":
                snapshot["class_name"] = candidate["class_name"]
                snapshot["text"] = candidate["text"]
                snapshot["status"] = candidate_status
                snapshot["bounds"] = candidate["bounds"]
                return
            if candidate_area > snapshot_area:
                snapshot["class_name"] = candidate["class_name"]
                snapshot["text"] = candidate["text"]
                snapshot["status"] = candidate_status
                snapshot["bounds"] = candidate["bounds"]
            return

        snapshots.append(candidate)

    def _list_file_dialog_candidates(self) -> list[dict[str, object]]:
        """??????????????????????????????"""

        foreground_handle = None
        z_order_handles: list[int] = []
        try:
            import win32con  # type: ignore
            import win32gui  # type: ignore

            foreground_handle = int(win32gui.GetForegroundWindow())
            current = win32gui.GetTopWindow(None)
            while current:
                if win32gui.IsWindowVisible(current):
                    z_order_handles.append(int(current))
                current = win32gui.GetWindow(current, win32con.GW_HWNDNEXT)
        except Exception:
            foreground_handle = None

        candidates: list[dict[str, object]] = []
        for window in self.list_windows():
            if window.class_name not in {"CabinetWClass", "#32770"}:
                continue
            if not window.visible:
                continue

            handle_int = self._normalize_handle(window.handle)
            score = 0.0
            title = window.title or ""
            if foreground_handle is not None and handle_int == foreground_handle:
                score += 1000
            if handle_int in z_order_handles:
                score += max(0, 500 - z_order_handles.index(handle_int))
            if window.class_name == "#32770":
                score += 300
            if title.endswith(":\\") or re.fullmatch(r"[A-Za-z]:\\", title):
                score += 120
            if title:
                score += min(len(title), 80)

            candidates.append(
                {
                    "handle": handle_int,
                    "title": title,
                    "class_name": window.class_name,
                    "score": score,
                }
            )

        candidates.sort(key=lambda item: item["score"], reverse=True)
        return candidates

    def _upload_file_via_dialog_candidate(self, candidate: dict[str, object], resolved_path: str) -> dict[str, object]:
        """在单个文件对话框候选里尝试完成文件路径注入。"""

        Desktop, _ = self._import_pywinauto()
        handle = int(candidate["handle"])
        title = str(candidate.get("title") or "")

        for backend in ("win32", "uia"):
            try:
                dialog = Desktop(backend=backend).window(handle=handle)
                dialog.wait("exists ready", timeout=1)
            except Exception:
                continue

            try:
                dialog.set_focus()
            except Exception:
                pass

            shortcut_result = self._try_navigate_dialog_via_shortcuts(dialog, resolved_path, handle)
            if shortcut_result.get("success"):
                shortcut_result.update({"backend": backend, "title": title, "class_name": candidate["class_name"]})
                return shortcut_result

            direct_result = self._try_fill_dialog_filename(dialog, resolved_path, handle)
            if direct_result.get("success"):
                direct_result.update({"backend": backend, "title": title, "class_name": candidate["class_name"]})
                return direct_result

        return {
            "success": False,
            "handle": handle,
            "title": title,
            "class_name": candidate["class_name"],
            "file_path": resolved_path,
            "error": "dialog_interaction_failed",
        }

    def _try_fill_dialog_filename(self, dialog: Any, resolved_path: str, dialog_handle: int | None = None) -> dict[str, object]:
        """优先命中文件名输入框和打开按钮。"""

        filename_edits: list[dict[str, object]] = []
        open_buttons: list[dict[str, object]] = []

        for control in dialog.descendants():
            try:
                class_name = control.friendly_class_name()
                text = (control.window_text() or "").strip()
                rect = control.rectangle()
            except Exception:
                continue

            if class_name == "Edit":
                if rect.right - rect.left >= 180:
                    filename_edits.append(
                        {
                            "control": control,
                            "bounds": {
                                "left": rect.left,
                                "top": rect.top,
                                "right": rect.right,
                                "bottom": rect.bottom,
                            },
                        }
                    )

            if class_name == "Button" and text in {"打开", "打开(&O)", "打开(O)", "Open"}:
                open_buttons.append(
                    {
                        "control": control,
                        "bounds": {
                            "left": rect.left,
                            "top": rect.top,
                            "right": rect.right,
                            "bottom": rect.bottom,
                        },
                    }
                )

        filename_edit = self._pick_dialog_filename_edit(filename_edits)
        open_button = self._pick_dialog_open_button(open_buttons)

        if filename_edit is None:
            return {"success": False, "error": "filename_edit_not_found"}

        try:
            self._fill_dialog_edit_and_submit(filename_edit, resolved_path, open_button)
            if self._is_dialog_still_open(dialog_handle):
                file_name = Path(resolved_path).name
                if self._try_click_dialog_file_item_and_submit(dialog, file_name, open_button, dialog_handle):
                    return {"success": True, "file_path": resolved_path, "method": "filename_edit_then_file_item_submit"}
                return {"success": False, "file_path": resolved_path, "error": "dialog_still_open_after_submit"}
            return {"success": True, "file_path": resolved_path, "method": "filename_edit_plus_submit"}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def _try_navigate_dialog_via_shortcuts(
        self,
        dialog: Any,
        resolved_path: str,
        dialog_handle: int | None = None,
    ) -> dict[str, object]:
        """通过地址栏快捷键退回完成文件注入。"""

        parent_dir = str(Path(resolved_path).parent)
        file_name = Path(resolved_path).name

        try:
            from pywinauto.keyboard import send_keys

            dialog.set_focus()
            send_keys("%d", pause=0.05)
            time.sleep(0.15)
            self._paste_text(parent_dir)
            send_keys("{ENTER}", pause=0.05)
            time.sleep(0.6)
            select_result = self._try_select_file_after_navigation(dialog, file_name, resolved_path, dialog_handle)
            if select_result.get("success"):
                select_result["method"] = "alt_d_directory_then_select"
                return select_result
        except Exception:
            pass

        try:
            from pywinauto.keyboard import send_keys

            dialog.set_focus()
            send_keys("^l", pause=0.05)
            time.sleep(0.15)
            self._paste_text(parent_dir)
            send_keys("{ENTER}", pause=0.05)
            time.sleep(0.6)
            select_result = self._try_select_file_after_navigation(dialog, file_name, resolved_path, dialog_handle)
            if select_result.get("success"):
                select_result["method"] = "ctrl_l_directory_then_select"
                return select_result
        except Exception as exc:
            return {"success": False, "error": str(exc)}

        return {"success": False, "error": "directory_navigation_select_failed"}

    @staticmethod
    def _pick_dialog_filename_edit(candidates: list[dict[str, object]]) -> Any | None:
        """优先选择位于对话框下半区的文件名输入框，而不是顶部地址栏。"""

        if not candidates:
            return None

        best = max(
            candidates,
            key=lambda item: (
                int(item["bounds"]["top"]),
                int(item["bounds"]["right"]) - int(item["bounds"]["left"]),
            ),
        )
        return best["control"]

    @staticmethod
    def _pick_dialog_open_button(candidates: list[dict[str, object]]) -> Any | None:
        """优先选择右下角的打开按钮。"""

        if not candidates:
            return None

        best = max(
            candidates,
            key=lambda item: (
                int(item["bounds"]["top"]),
                int(item["bounds"]["left"]),
            ),
        )
        return best["control"]

    def _fill_dialog_edit_and_submit(self, edit_control: Any, value: str, open_button: Any | None) -> None:
        """向文件名框写值并提交。"""

        from pywinauto.keyboard import send_keys

        edit_control.set_focus()
        send_keys("^a{BACKSPACE}", pause=0.02)
        self._paste_text(value)
        time.sleep(0.2)
        if open_button is not None and self._click_control_with_fallback(open_button):
            time.sleep(0.5)
            return
        send_keys("{ENTER}", pause=0.05)
        time.sleep(0.5)

    def _try_select_file_after_navigation(
        self,
        dialog: Any,
        file_name: str,
        resolved_path: str,
        dialog_handle: int | None = None,
    ) -> dict[str, object]:
        """进入目标目录后，再通过文件名输入框或键盘选择具体文件。"""

        filename_edits: list[dict[str, object]] = []
        open_buttons: list[dict[str, object]] = []
        for control in dialog.descendants():
            try:
                class_name = control.friendly_class_name()
                text = (control.window_text() or "").strip()
                rect = control.rectangle()
            except Exception:
                continue

            if class_name == "Edit" and rect.right - rect.left >= 180:
                filename_edits.append(
                    {
                        "control": control,
                        "bounds": {
                            "left": rect.left,
                            "top": rect.top,
                            "right": rect.right,
                            "bottom": rect.bottom,
                        },
                    }
                )
            if class_name == "Button" and text in {"打开", "打开(&O)", "打开(O)", "Open"}:
                open_buttons.append(
                    {
                        "control": control,
                        "bounds": {
                            "left": rect.left,
                            "top": rect.top,
                            "right": rect.right,
                            "bottom": rect.bottom,
                        },
                    }
                )

        filename_edit = self._pick_dialog_filename_edit(filename_edits)
        open_button = self._pick_dialog_open_button(open_buttons)
        if filename_edit is not None:
            try:
                self._fill_dialog_edit_and_submit(filename_edit, file_name, open_button)
                if self._is_dialog_still_open(dialog_handle):
                    if self._try_click_dialog_file_item_and_submit(dialog, file_name, open_button, dialog_handle):
                        return {"success": True, "file_path": resolved_path}
                    return {"success": False, "file_path": resolved_path, "error": "dialog_still_open_after_filename_submit"}
                return {"success": True, "file_path": resolved_path}
            except Exception:
                pass

        try:
            from pywinauto.keyboard import send_keys

            dialog.set_focus()
            self._paste_text(file_name)
            send_keys("{ENTER}", pause=0.05)
            time.sleep(0.5)
            if self._is_dialog_still_open(dialog_handle):
                if self._try_click_dialog_file_item_and_submit(dialog, file_name, open_button, dialog_handle):
                    return {"success": True, "file_path": resolved_path}
                return {
                    "success": False,
                    "file_path": resolved_path,
                    "error": "dialog_still_open_after_keyboard_submit",
                }
            return {"success": True, "file_path": resolved_path}
        except Exception as exc:
            return {"success": False, "file_path": resolved_path, "error": str(exc)}

    def _is_dialog_still_open(self, dialog_handle: int | None) -> bool:
        """判断目标文件对话框在提交后是否仍然可见。"""

        if dialog_handle is None:
            return False

        try:
            import win32gui  # type: ignore

            return bool(win32gui.IsWindow(dialog_handle) and win32gui.IsWindowVisible(dialog_handle))
        except Exception:
            pass

        for window in self.list_windows():
            try:
                handle_int = self._normalize_handle(window.handle)
            except Exception:
                continue
            if handle_int == dialog_handle and window.visible:
                return True
        return False

    def _try_click_dialog_file_item_and_submit(
        self,
        dialog: Any,
        file_name: str,
        open_button: Any | None,
        dialog_handle: int | None,
    ) -> bool:
        """显式点击目标文件项并再次提交，处理仅进入目录但未真正选中文件的情况。"""

        candidates: list[tuple[int, int, Any]] = []
        expected_name = self._normalize_dialog_file_item_text(file_name)
        expected_stem = self._normalize_dialog_file_item_text(Path(file_name).stem)

        for control in dialog.descendants():
            try:
                text = (control.window_text() or "").strip()
                class_name = control.friendly_class_name()
                rect = control.rectangle()
            except Exception:
                continue

            if not text:
                continue
            normalized_text = self._normalize_dialog_file_item_text(text)
            if (
                normalized_text != expected_name
                and normalized_text != expected_stem
                and not normalized_text.startswith(expected_stem)
            ):
                continue
            if class_name not in {"ListItem", "DataItem", "Text", "TreeItem"}:
                continue
            candidates.append((rect.top, rect.left, control))

        candidates.sort()
        for _, _, control in candidates:
            try:
                control.set_focus()
            except Exception:
                pass

            try:
                control.click_input(double=True)
            except Exception:
                if not self._click_control_with_fallback(control):
                    continue

            time.sleep(0.3)
            if open_button is not None and self._is_dialog_still_open(dialog_handle):
                self._click_control_with_fallback(open_button)
                time.sleep(0.5)
            if not self._is_dialog_still_open(dialog_handle):
                return True

        return False

    @staticmethod
    def _normalize_dialog_file_item_text(value: str) -> str:
        """归一化资源管理器图标视图里的文件名文本。

        大图标模式会把 `transparent-probe.png` 拆成多行展示，UIA 暴露出来的文本
        可能包含换行或空白。匹配前去掉空白，避免文件已可见却无法点击提交。
        """

        return re.sub(r"\s+", "", value).lower()

    def inspect_controls_by_automation_id(self, handle: str, automation_id: str) -> list[dict[str, object]]:
        """读取指定 automation_id 的当前控件快照。"""

        window = self._get_window(handle)
        snapshots: list[dict[str, object]] = []
        for control in self._iter_controls_by_automation_id(window, automation_id):
            try:
                rectangle = control.rectangle()
                snapshots.append(
                    {
                        "automation_id": automation_id,
                        "class_name": control.friendly_class_name(),
                        "text": control.window_text() or "",
                        "bounds": {
                            "left": rectangle.left,
                            "top": rectangle.top,
                            "right": rectangle.right,
                            "bottom": rectangle.bottom,
                        },
                    }
                )
            except Exception:
                continue
        return snapshots

    def _iter_controls_by_automation_id(self, window: Any, automation_id: str) -> list[Any]:
        """枚举窗口内指定 automation_id 的所有候选控件。"""

        matches: list[Any] = []
        for control in window.descendants():
            try:
                current_id = control.element_info.automation_id or ""
            except Exception:
                continue
            if current_id == automation_id:
                matches.append(control)
        if matches:
            return self._sort_controls_visible_first(matches)

        suffix = automation_id.rsplit("-", 1)[-1]
        if suffix:
            return self._iter_controls_by_automation_id_suffix(window, suffix, None)
        return matches

    def _iter_controls_by_automation_id_suffix(
        self,
        window: Any,
        suffix: str,
        control_type: str | None,
    ) -> list[Any]:
        """按动态 automation_id 后缀枚举候选控件。"""

        matches: list[Any] = []
        for control in window.descendants():
            try:
                current_id = control.element_info.automation_id or ""
                class_name = control.friendly_class_name()
                rect = control.rectangle()
            except Exception:
                continue
            if not current_id.endswith(f"-{suffix}"):
                continue
            if control_type is not None and class_name != control_type:
                continue
            if rect.right <= rect.left or rect.bottom <= rect.top:
                continue
            matches.append(control)
        return self._sort_controls_visible_first(matches)

    @staticmethod
    def _sort_controls_visible_first(controls: list[Any]) -> list[Any]:
        def sort_key(control: Any) -> tuple[int, int, int]:
            try:
                rect = control.rectangle()
                visible = rect.right > rect.left and rect.bottom > rect.top
                return (0 if visible else 1, rect.top, rect.left)
            except Exception:
                return (1, 0, 0)

        return sorted(controls, key=sort_key)

    def _activate_control_with_fallback(self, control: Any) -> dict[str, object]:
        """激活目标控件并返回成功方法。"""

        try:
            control.set_focus()
        except Exception:
            pass

        try:
            control.click_input()
            return {"success": True, "method": "control.click_input"}
        except Exception:
            pass

        try:
            wrapper = control.wrapper_object()
            wrapper.click_input()
            return {"success": True, "method": "wrapper.click_input"}
        except Exception:
            pass

        try:
            wrapper = control.wrapper_object()
            if hasattr(wrapper, "invoke"):
                wrapper.invoke()
                return {"success": True, "method": "wrapper.invoke"}
        except Exception:
            pass

        try:
            rectangle = control.rectangle()
            x = (rectangle.left + rectangle.right) // 2
            y = (rectangle.top + rectangle.bottom) // 2
            if x <= 0 or y <= 0:
                return {"success": False, "method": "invalid_rect"}
            from pywinauto import mouse

            mouse.click(coords=(x, y))
            return {"success": True, "method": "mouse.click"}
        except Exception:
            return {"success": False, "method": "all_failed"}

    def _click_control_center(self, control: Any) -> bool:
        """直接点击控件可见矩形中心，避开 WebView wrapper 阻塞。"""

        try:
            rect = control.rectangle()
            if rect.right <= rect.left or rect.bottom <= rect.top:
                return False
            from pywinauto import mouse

            mouse.click(coords=((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2))
            return True
        except Exception:
            return False

    def _click_control_with_fallback(self, control: Any) -> bool:
        """对单个控件执行多级点击回退。"""

        try:
            control.set_focus()
        except Exception:
            pass

        try:
            control.click_input()
            return True
        except Exception:
            pass

        try:
            wrapper = control.wrapper_object()
            wrapper.click_input()
            return True
        except Exception:
            pass

        try:
            wrapper = control.wrapper_object()
            if hasattr(wrapper, "invoke"):
                wrapper.invoke()
                return True
        except Exception:
            pass

        try:
            rectangle = control.rectangle()
            x = (rectangle.left + rectangle.right) // 2
            y = (rectangle.top + rectangle.bottom) // 2
            if x <= 0 or y <= 0:
                return False
            from pywinauto import mouse

            mouse.click(coords=(x, y))
            return True
        except Exception:
            return False

    def capture_window(self, handle: str) -> str | None:
        """对窗口区域截图并返回文件路径。"""

        Desktop, _ = self._import_pywinauto()
        window = Desktop(backend=self.backend).window(handle=self._normalize_handle(handle))

        try:
            rect = window.rectangle()
            image = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
        except Exception:
            return None

        target_path = self.screenshot_dir / (
            f"window-{handle}-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}.png"
        )
        image.save(target_path)
        return str(target_path)
