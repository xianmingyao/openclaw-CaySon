"""WebView 坐标计划。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    """屏幕矩形区域。"""

    x: int
    y: int
    width: int
    height: int

    def center(self) -> tuple[int, int]:
        """返回矩形中心点。"""

        # 坐标点击默认使用中心点。
        # 使用整数除法，确保返回可直接用于 Win32/pyautogui。
        # 该方法不访问屏幕，只做几何计算。
        return (self.x + self.width // 2, self.y + self.height // 2)


@dataclass(frozen=True)
class CoordinatePlan:
    """字段坐标计划。"""

    field_name: str
    rect: Rect
    confidence: float
    source: str

    def is_trusted(self, threshold: float = 0.80) -> bool:
        """判断坐标计划是否可信。"""

        # confidence 来自 OCR/模板/VLM 等定位证据。
        # 阈值默认 0.80，低于阈值不应执行点击。
        # source 保留证据来源，方便失败排查。
        return self.confidence >= threshold


class CoordinatePlanner:
    """根据 OCR 文本生成字段坐标计划。"""

    def plan_from_label(self, field_name: str, label_rect: Rect, offset_x: int = 160) -> CoordinatePlan:
        """从字段标签位置推断输入框坐标。"""

        # 京麦 WebView 字段通常是标签右侧输入框。
        # Phase 2 用固定 offset 构造可测试计划。
        # 真实实现应结合页面 signature 和局部截图相似度校验。
        rect = Rect(x=label_rect.x + offset_x, y=label_rect.y, width=240, height=max(label_rect.height, 24))
        return CoordinatePlan(field_name=field_name, rect=rect, confidence=0.82, source="label_offset")
