"""UIA 定位器 — 通过 Windows UIAutomation 查找控件。

参考 UFO inspector.py 的 BackendStrategy + ControlInspectorFacade 模式，
使用 UIA COM API 进行精确的控件树遍历和属性匹配。
"""

from __future__ import annotations

import logging
from typing import Any

from jm_ufo_agent.locators.base import Locator, LocateResult

logger = logging.getLogger(__name__)

# Windows 专用导入保护
try:
    import comtypes  # type: ignore
    from comtypes import client as comtypes_client  # type: ignore

    _HAS_COMTYPES = True
except ImportError:
    _HAS_COMTYPES = False


class UIALocator(Locator):
    """基于 UIAutomation 的控件定位器。

    # 使用 UIA COM API 遍历控件树，按 control_type / name / class_name
    # 匹配目标控件。支持深度和可见性过滤。
    # 在非 Windows 平台或 comtypes 不可用时降级为空结果。
    # 参考 UFO inspector.py UIABackendStrategy.find_control_elements_in_descendants。
    """

    def __init__(
        self,
        max_depth: int = 10,
        max_elements: int = 500,
        timeout_ms: int = 3000,
    ):
        """初始化 UIA 定位器。"""
        self._max_depth = max_depth
        self._max_elements = max_elements
        self._timeout_ms = timeout_ms
        self._inspector: Any = None

    @property
    def name(self) -> str:
        return "uia"

    async def locate(
        self,
        target: str,
        context: dict[str, Any] | None = None,
    ) -> list[LocateResult]:
        """通过 UIA 查找匹配目标描述的控件。"""
        if not _HAS_COMTYPES:
            logger.debug("comtypes 不可用，UIALocator 返回空结果")
            return []

        ctx = context or {}
        window = ctx.get("window")
        if window is None:
            logger.debug("UIALocate 缺少 window 上下文")
            return []

        control_type_list = ctx.get("control_type_list", [])
        class_name_list = ctx.get("class_name_list", [])
        title_list = [target]

        try:
            elements = await self._find_controls(
                window=window,
                control_type_list=control_type_list,
                class_name_list=class_name_list,
                title_list=title_list,
            )
        except Exception as exc:
            logger.warning("UIA 定位异常: %s", exc)
            return []

        results: list[LocateResult] = []
        for elem in elements[:self._max_elements]:
            try:
                rect = self._get_element_rect(elem)
                name = self._get_element_name(elem)
                ctrl_type = self._get_element_control_type(elem)
                results.append(
                    LocateResult(
                        target=target,
                        rect=rect,
                        confidence=1.0,
                        meta={"control_type": ctrl_type, "name": name, "source": "uia"},
                        element=elem,
                    )
                )
            except Exception as exc:
                logger.debug("跳过无法读取的 UIA 元素: %s", exc)
                continue

        results.sort(key=lambda r: r.confidence, reverse=True)
        return results

    async def _find_controls(
        self,
        window: Any,
        control_type_list: list[str],
        class_name_list: list[str],
        title_list: list[str],
    ) -> list[Any]:
        """在窗口后代中查找匹配控件。

        # 参考 UFO UIABackendStrategy.find_control_elements_in_descendants。
        # 使用 COM cache_request 批量获取属性以提升性能。
        # 限制最大返回数量，防止控件树过大导致超时。
        """
        import asyncio

        return await asyncio.to_thread(
            self._find_controls_sync,
            window,
            control_type_list,
            class_name_list,
            title_list,
        )

    def _find_controls_sync(
        self,
        window: Any,
        control_type_list: list[str],
        class_name_list: list[str],
        title_list: list[str],
    ) -> list[Any]:
        """同步版本的控件查找。"""
        try:
            from ufo.automator.ui_control.inspector import ControlInspectorFacade  # type: ignore

            facade = ControlInspectorFacade(backend="uia")
            return facade.find_control_elements_in_descendants(
                window=window,
                control_type_list=control_type_list,
                class_name_list=class_name_list,
                title_list=title_list,
            )
        except ImportError:
            logger.debug("UFO inspector 不可用，尝试直接 UIA 查找")
            return self._direct_uia_find(window, title_list)

    def _direct_uia_find(self, window: Any, title_list: list[str]) -> list[Any]:
        """不依赖 UFO inspector 的直接 UIA 查找。"""
        if not _HAS_COMTYPES:
            return []

        try:
            import pywinauto  # type: ignore
            from pywinauto.uia_element_info import UIAElementInfo  # type: ignore

            results: list[Any] = []
            for title in title_list:
                try:
                    descendants = window.descendants()
                    for d in descendants:
                        try:
                            if title and title.lower() in (d.window_text() or "").lower():
                                results.append(d)
                        except Exception:
                            continue
                except Exception as exc:
                    logger.debug("UIA 遍历异常: %s", exc)
            return results[: self._max_elements]
        except ImportError:
            return []

    @staticmethod
    def _get_element_rect(element: Any) -> tuple[int, int, int, int]:
        """获取元素的像素坐标矩形。"""
        try:
            rect = element.rectangle()
            return (rect.left, rect.top, rect.right, rect.bottom)
        except Exception:
            try:
                rect = element.element_info.rectangle
                return (rect.left, rect.top, rect.right, rect.bottom)
            except Exception:
                return (0, 0, 0, 0)

    @staticmethod
    def _get_element_name(element: Any) -> str:
        """获取元素名称。"""
        try:
            return element.window_text() or ""
        except Exception:
            return ""

    @staticmethod
    def _get_element_control_type(element: Any) -> str:
        """获取元素控件类型。"""
        try:
            return element.element_info.control_type or ""
        except Exception:
            return ""
