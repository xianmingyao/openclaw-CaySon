"""Locator 抽象基类与定位结果模型。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class LocateResult:
    """单次定位结果。

    # rect 是 (left, top, right, bottom) 绝对像素坐标。
    # confidence 在 0~1 之间，UIA 精确匹配为 1.0，VLM/OCR 按模型输出。
    # meta 携带定位策略特有的附加信息（控件类型、OCR 文本等）。
    # element 可保存 UIA Element 对象引用，非 UIA 定位时为 None。
    """

    target: str
    rect: tuple[int, int, int, int]
    confidence: float = 1.0
    meta: dict[str, Any] = field(default_factory=dict)
    element: Any = None


class Locator(ABC):
    """元素定位器抽象基类。

    # 每种定位策略（UIA、OCR、VLM）实现 locate 方法。
    # locate 接收目标描述字符串和可选上下文，返回匹配结果列表。
    # 子类应保证：空结果返回 [] 而非抛异常，异常情况由调用方处理。
    """

    @abstractmethod
    async def locate(
        self,
        target: str,
        context: dict[str, Any] | None = None,
    ) -> list[LocateResult]:
        """根据目标描述查找 UI 元素。

        # target 是自然语言或结构化的目标描述。
        # context 携带窗口句柄、截图、上轮证据等辅助信息。
        # 返回按 confidence 降序排列的 LocateResult 列表。
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """定位器名称，用于日志和证据记录。"""
