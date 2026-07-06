"""元素定位器 — 多模态 UI 元素查找。

Locator 系统提供统一的元素定位接口，支持 UIA、屏幕表面（OCR）和 VLM
三种定位策略。每种策略实现 Locator ABC，返回 LocateResult 列表。
"""

from jm_ufo_agent.locators.base import Locator, LocateResult

__all__ = ["Locator", "LocateResult"]
