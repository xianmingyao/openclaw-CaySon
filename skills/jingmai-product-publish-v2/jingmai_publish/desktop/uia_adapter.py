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


@dataclass(slots=True)
class UIATuningConfig:
    """UIA 命中调优配置。"""

    window_keywords: list[str] = field(default_factory=lambda: ["京麦", "Jingmai"])
    preferred_classes: list[str] = field(
        default_factory=lambda: ["Button", "MenuItem", "Hyperlink", "SplitButton"]
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
            for window in desktop.windows():
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
        """按 automation_id 和控件类型定位子控件。"""

        window = self._get_window(handle)
        return window.child_window(auto_id=automation_id, control_type=control_type)

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
            wrapper = control.wrapper_object()
            control.set_focus()
        except Exception:
            return False

        try:
            wrapper.set_edit_text(value)
        except Exception:
            try:
                wrapper.click_input()
                wrapper.type_keys("^a{BACKSPACE}", set_foreground=False)
                wrapper.type_keys(value, with_spaces=True, set_foreground=False)
            except Exception:
                return False
        return True

    def select_combobox_by_automation_id(self, handle: str, automation_id: str, value: str) -> bool:
        """按 automation_id 选择下拉框值。"""

        try:
            control = self._get_control(handle, automation_id, "ComboBox")
            wrapper = control.wrapper_object()
            control.set_focus()
        except Exception:
            return False

        try:
            wrapper.select(value)
        except Exception:
            try:
                wrapper.click_input()
                wrapper.type_keys("^a{BACKSPACE}", set_foreground=False)
                wrapper.type_keys(value, with_spaces=True, set_foreground=False)
                wrapper.type_keys("{ENTER}", set_foreground=False)
            except Exception:
                return False
        return True

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
        return matches

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
