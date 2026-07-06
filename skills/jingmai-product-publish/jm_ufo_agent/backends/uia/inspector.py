"""UIA 检查器 — 后端策略 + 控件检查门面。

参考 UFO inspector.py 的 BackendStrategy + ControlInspectorFacade 模式，
提供窗口枚举、控件树遍历和元素查找能力。
"""

from __future__ import annotations

import logging
import platform
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)

# Windows 专用导入保护
try:
    import pywinauto  # type: ignore
    from pywinauto import Desktop  # type: ignore

    _HAS_PYWINAUTO = True
except ImportError:
    _HAS_PYWINAUTO = False


class BackendStrategy(ABC):
    """后端策略抽象基类。

    # 参考 UFO BackendStrategy，定义窗口枚举和控件查找接口。
    # UIA 和 Win32 各实现一套，通过 BackendFactory 创建。
    # find_control_elements_in_descendants 是核心方法，
    # 在窗口后代中按条件过滤控件。
    """

    @abstractmethod
    def get_desktop_windows(self, remove_empty: bool = True) -> list[Any]:
        """获取桌面上所有可见窗口。"""

    @abstractmethod
    def find_control_elements_in_descendants(
        self,
        window: Any,
        control_type_list: list[str] | None = None,
        class_name_list: list[str] | None = None,
        title_list: list[str] | None = None,
        is_visible: bool = True,
        is_enabled: bool = True,
        depth: int | None = None,
    ) -> list[Any]:
        """在窗口后代中查找匹配控件。"""


class UIABackendStrategy(BackendStrategy):
    """UIA 后端策略 — 使用 UIAutomation COM API。

    # 参考 UFO UIABackendStrategy。
    # get_desktop_windows 使用 Win32 枚举窗口句柄再转 UIA，
    # 性能优于纯 UIA 遍历。
    # find_control 使用 COM cache_request 批量获取属性。
    """

    def get_desktop_windows(self, remove_empty: bool = True) -> list[Any]:
        """获取桌面窗口列表。"""
        if not _HAS_PYWINAUTO:
            return []

        try:
            desktop = Desktop(backend="uia")
            windows = desktop.windows()
            if remove_empty:
                windows = [w for w in windows if w.window_text()]
            return windows
        except Exception as exc:
            logger.warning("UIA 枚举窗口异常: %s", exc)
            return []

    def find_control_elements_in_descendants(
        self,
        window: Any,
        control_type_list: list[str] | None = None,
        class_name_list: list[str] | None = None,
        title_list: list[str] | None = None,
        is_visible: bool = True,
        is_enabled: bool = True,
        depth: int | None = None,
    ) -> list[Any]:
        """在窗口后代中查找 UIA 控件。"""
        if not _HAS_PYWINAUTO:
            return []

        try:
            descendants = window.descendants(max_depth=depth)
        except Exception as exc:
            logger.debug("UIA 后代遍历异常: %s", exc)
            return []

        results: list[Any] = []
        for d in descendants:
            try:
                if control_type_list and d.element_info.control_type not in control_type_list:
                    continue
                if class_name_list and d.element_info.class_name not in class_name_list:
                    continue
                if title_list:
                    text = d.window_text() or ""
                    if not any(t.lower() in text.lower() for t in title_list):
                        continue
                if is_visible and not d.is_visible():
                    continue
                if is_enabled and not d.is_enabled():
                    continue
                results.append(d)
            except Exception:
                continue

        return results


class Win32BackendStrategy(BackendStrategy):
    """Win32 后端策略 — 使用 Win32 API。

    # 参考 UFO Win32BackendStrategy。
    # 更轻量，适合不需要 UIA 属性的场景。
    # 通过 pywinauto win32 backend 枚举和查找控件。
    """

    def get_desktop_windows(self, remove_empty: bool = True) -> list[Any]:
        """获取桌面窗口列表。"""
        if not _HAS_PYWINAUTO:
            return []

        try:
            desktop = Desktop(backend="win32")
            windows = desktop.windows()
            if remove_empty:
                windows = [w for w in windows if w.window_text()]
            return windows
        except Exception as exc:
            logger.warning("Win32 枚举窗口异常: %s", exc)
            return []

    def find_control_elements_in_descendants(
        self,
        window: Any,
        control_type_list: list[str] | None = None,
        class_name_list: list[str] | None = None,
        title_list: list[str] | None = None,
        is_visible: bool = True,
        is_enabled: bool = True,
        depth: int | None = None,
    ) -> list[Any]:
        """在窗口后代中查找 Win32 控件。"""
        if not _HAS_PYWINAUTO:
            return []

        try:
            descendants = window.descendants(max_depth=depth)
        except Exception:
            return []

        results: list[Any] = []
        for d in descendants:
            try:
                if class_name_list:
                    class_name = d.element_info.class_name if hasattr(d, "element_info") else ""
                    if class_name not in class_name_list:
                        continue
                if title_list:
                    text = d.window_text() or ""
                    if not any(t.lower() in text.lower() for t in title_list):
                        continue
                results.append(d)
            except Exception:
                continue

        return results


class BackendFactory:
    """后端工厂 — 按 backend 名称创建策略实例。"""

    _STRATEGIES: dict[str, type[BackendStrategy]] = {
        "uia": UIABackendStrategy,
        "win32": Win32BackendStrategy,
    }

    @classmethod
    def create(cls, backend: str = "uia") -> BackendStrategy:
        """创建后端策略实例。"""
        strategy_cls = cls._STRATEGIES.get(backend)
        if strategy_cls is None:
            raise ValueError(f"未知后端: {backend}，支持: {list(cls._STRATEGIES.keys())}")
        return strategy_cls()


class ControlInspectorFacade:
    """控件检查门面 — 单例封装后端策略。

    # 参考 UFO ControlInspectorFacade。
    # 提供高层 API：find_control、get_window 等。
    # 每个 backend 类型只创建一个门面实例。
    """

    _instances: dict[str, "ControlInspectorFacade"] = {}

    def __init__(self, backend: str = "uia") -> None:
        """初始化检查门面。"""
        self._strategy = BackendFactory.create(backend)
        self._backend_name = backend

    @classmethod
    def get_instance(cls, backend: str = "uia") -> "ControlInspectorFacade":
        """获取或创建单例门面。"""
        if backend not in cls._instances:
            cls._instances[backend] = cls(backend)
        return cls._instances[backend]

    def get_desktop_windows(self, remove_empty: bool = True) -> list[Any]:
        """获取桌面窗口。"""
        return self._strategy.get_desktop_windows(remove_empty)

    def find_control(
        self,
        window: Any,
        control_type_list: list[str] | None = None,
        class_name_list: list[str] | None = None,
        title_list: list[str] | None = None,
        is_visible: bool = True,
        is_enabled: bool = True,
        depth: int | None = None,
    ) -> list[Any]:
        """查找匹配控件。"""
        return self._strategy.find_control_elements_in_descendants(
            window=window,
            control_type_list=control_type_list,
            class_name_list=class_name_list,
            title_list=title_list,
            is_visible=is_visible,
            is_enabled=is_enabled,
            depth=depth,
        )

    def find_window_by_title(self, title: str) -> Any | None:
        """按标题查找窗口。"""
        windows = self.get_desktop_windows(remove_empty=True)
        for w in windows:
            try:
                if title.lower() in (w.window_text() or "").lower():
                    return w
            except Exception:
                continue
        return None
