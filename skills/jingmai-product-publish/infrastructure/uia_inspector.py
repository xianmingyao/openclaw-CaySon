"""
Fast UIA control inspection adapted from UFO's cached UIA backend.
"""

from __future__ import annotations

import functools
import platform
from typing import Any, List, Optional, TYPE_CHECKING, cast

if TYPE_CHECKING or platform.system() == "Windows":
    import comtypes.gen.UIAutomationClient as UIAutomationClient_dll
    import pywinauto
    import pywinauto.uia_defines
    from pywinauto.controls.uiawrapper import UIAWrapper
    from pywinauto.uia_element_info import UIAElementInfo
else:
    UIAutomationClient_dll = None
    pywinauto = None
    UIAWrapper = Any
    UIAElementInfo = Any


class UIAElementInfoFix(UIAElementInfo):
    _cached_rect = None

    def __init__(self, element, is_ref: bool = False):
        super().__init__(element, is_ref)

    def _get_current_rectangle(self):
        bound_rect = self._element.CurrentBoundingRectangle
        rect = pywinauto.win32structures.RECT()
        rect.left = bound_rect.left
        rect.top = bound_rect.top
        rect.right = bound_rect.right
        rect.bottom = bound_rect.bottom
        return rect

    def _get_cached_rectangle(self):
        if self._cached_rect is None:
            self._cached_rect = self._get_current_rectangle()
        return self._cached_rect

    @property
    def rectangle(self):
        return self._get_cached_rectangle()


class UIAControlInspector:
    """
    Cached UIA descendant lookup adapted from UFO's UIABackendStrategy.
    """

    @classmethod
    def find_descendants(
        cls,
        window: Optional["UIAWrapper"],
        control_type_list: List[str],
        is_visible: bool = True,
        is_enabled: bool = True,
        limit: int = 200,
    ) -> List["UIAWrapper"]:
        if platform.system() != "Windows" or pywinauto is None or window is None:
            return []

        try:
            window.is_enabled()
        except Exception:
            return []

        try:
            _, iuia_dll = cls._get_uia_defs()
            window_elem_info = cast(UIAElementInfo, window.element_info)
            window_elem_com_ref = cast(
                UIAutomationClient_dll.IUIAutomationElement, window_elem_info._element
            )

            condition = cls._get_control_filter_condition(
                control_type_list, is_visible=is_visible, is_enabled=is_enabled
            )
            cache_request = cls._get_cache_request()

            com_elem_array = window_elem_com_ref.FindAllBuildCache(
                scope=iuia_dll.TreeScope_Descendants,
                condition=condition,
                cacheRequest=cache_request,
            )

            elements: List["UIAWrapper"] = []
            for idx in range(min(com_elem_array.Length, limit)):
                elem = com_elem_array.GetElement(idx)
                elem_type = elem.CachedControlType
                elem_name = elem.CachedName
                elem_rect = elem.CachedBoundingRectangle

                element_info = UIAElementInfoFix(elem, True)
                element_info._cached_handle = 0
                element_info._cached_visible = True
                rect = pywinauto.win32structures.RECT()
                rect.left = elem_rect.left
                rect.top = elem_rect.top
                rect.right = elem_rect.right
                rect.bottom = elem_rect.bottom
                element_info._cached_rect = rect
                element_info._cached_name = elem_name
                element_info._cached_control_type = cls._get_uia_control_name_map().get(
                    elem_type, ""
                )
                element_info._cached_rich_text = elem_name
                elements.append(UIAWrapper(element_info))
            return elements
        except Exception:
            return []

    @staticmethod
    def _get_uia_control_id_map():
        iuia = pywinauto.uia_defines.IUIA()
        return iuia.known_control_types

    @staticmethod
    def _get_uia_control_name_map():
        iuia = pywinauto.uia_defines.IUIA()
        return iuia.known_control_type_ids

    @staticmethod
    @functools.lru_cache()
    def _get_cache_request():
        iuia_com, iuia_dll = UIAControlInspector._get_uia_defs()
        cache_request = iuia_com.CreateCacheRequest()
        cache_request.AddProperty(iuia_dll.UIA_ControlTypePropertyId)
        cache_request.AddProperty(iuia_dll.UIA_NamePropertyId)
        cache_request.AddProperty(iuia_dll.UIA_BoundingRectanglePropertyId)
        return cache_request

    @staticmethod
    def _get_control_filter_condition(
        control_type_list: List[str],
        is_visible: bool = True,
        is_enabled: bool = True,
    ):
        iuia_com, iuia_dll = UIAControlInspector._get_uia_defs()
        return iuia_com.CreateAndConditionFromArray(
            [
                iuia_com.CreatePropertyCondition(
                    iuia_dll.UIA_IsEnabledPropertyId, is_enabled
                ),
                iuia_com.CreatePropertyCondition(
                    iuia_dll.UIA_IsOffscreenPropertyId,
                    not is_visible,
                ),
                iuia_com.CreatePropertyCondition(
                    iuia_dll.UIA_IsControlElementPropertyId, True
                ),
                iuia_com.CreateOrConditionFromArray(
                    [
                        iuia_com.CreatePropertyCondition(
                            iuia_dll.UIA_ControlTypePropertyId,
                            UIAControlInspector._get_uia_control_id_map()[control_type],
                        )
                        for control_type in control_type_list
                    ]
                ),
            ]
        )

    @staticmethod
    def _get_uia_defs():
        iuia = pywinauto.uia_defines.IUIA()
        iuia_com: UIAutomationClient_dll.IUIAutomation = iuia.iuia
        iuia_dll: UIAutomationClient_dll = iuia.UIA_dll
        return iuia_com, iuia_dll
