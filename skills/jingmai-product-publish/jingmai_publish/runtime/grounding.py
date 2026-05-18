"""三路 Grounding 仲裁 — DOM/UIA + Vision + Anchor 候选融合。

BL-095: 当单一元素定位方法失败时，通过三路候选融合提高定位成功率。
优先级链：UIA（最快最准）→ Vision（视觉理解）→ Anchor（文本/地标回退）

仲裁策略：
1. UIA 命中且 confidence >= 0.8 → 直接返回
2. UIA 未命中 → 尝试 Vision 定位
3. Vision 不可用或低置信度 → 回退到 Anchor
4. 多路都有候选 → 按加权平均融合（UIA 权重 0.5, Vision 0.35, Anchor 0.15）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ── 数据结构 ────────────────────────────────────────────────────────


@dataclass(slots=True)
class GroundingCandidate:
    """单路定位候选结果。"""

    method: str  # "uia", "vision", "anchor"
    bbox: tuple[int, int, int, int] | None = None  # 元素边界框
    point: tuple[int, int] | None = None  # 元素中心点
    confidence: float = 0.0  # 该路置信度
    element_info: dict[str, Any] = field(default_factory=dict)  # 元素额外信息
    error: str | None = None  # 该路错误信息


@dataclass(slots=True)
class GroundingResult:
    """三路仲裁最终结果。"""

    success: bool
    method: str = "none"  # 最终采用的方法: "uia", "vision", "anchor", "hybrid", "none"
    bbox: tuple[int, int, int, int] | None = None
    point: tuple[int, int] | None = None
    confidence: float = 0.0
    candidates: list[GroundingCandidate] = field(default_factory=list)
    fusion_method: str = ""  # "single", "weighted_average", "majority_vote"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "method": self.method,
            "bbox": list(self.bbox) if self.bbox else None,
            "point": list(self.point) if self.point else None,
            "confidence": self.confidence,
            "fusion_method": self.fusion_method,
            "error": self.error,
            "candidates": [
                {
                    "method": c.method,
                    "bbox": list(c.bbox) if c.bbox else None,
                    "confidence": c.confidence,
                    "error": c.error,
                }
                for c in self.candidates
            ],
        }


# ── UIA 定位器接口 ─────────────────────────────────────────────────


class UIAGroundingAdapter:
    """UIA/DOM 定位适配器 — 通过 automation_id、标签文本等定位控件。

    封装 RealWindowsUIAAdapter 的定位能力，统一为 GroundingCandidate 格式。
    """

    def __init__(self, uia_adapter: Any = None) -> None:
        self._adapter = uia_adapter

    def locate(
            self,
            window_handle: str,
            target: str,
            target_type: str = "automation_id",
    ) -> GroundingCandidate:
        """通过 UIA 定位元素。

        参数:
            window_handle: 窗口句柄
            target: 定位目标（automation_id 或标签文本）
            target_type: 定位方式 ("automation_id", "label", "class_name")
        """
        if self._adapter is None:
            return GroundingCandidate(
                method="uia",
                confidence=0.0,
                error="UIA adapter 未初始化",
            )

        try:
            rect = None
            if target_type == "automation_id":
                rect = self._adapter.find_control_rect(window_handle, target)
            elif target_type == "label":
                rect = self._adapter.find_control_by_label(window_handle, target)
            elif target_type == "class_name":
                rect = self._adapter.find_control_by_class(window_handle, target)

            if rect and len(rect) == 4 and any(v > 0 for v in rect):
                bbox = tuple(rect)
                point = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)
                return GroundingCandidate(
                    method="uia",
                    bbox=bbox,
                    point=point,
                    confidence=0.9,
                    element_info={"automation_id": target, "type": target_type},
                )
            return GroundingCandidate(
                method="uia",
                confidence=0.0,
                error=f"UIA 未找到 {target_type}={target}",
            )
        except Exception as exc:
            return GroundingCandidate(
                method="uia",
                confidence=0.0,
                error=f"UIA 定位异常: {exc}",
            )


# ── Anchor 定位器 ──────────────────────────────────────────────────


class AnchorGroundingAdapter:
    """Anchor 定位器 — 基于文本、地标关系推断元素位置。

    当 UIA 和 Vision 都不可用时，通过已知文本位置 + 相对偏移推断目标位置。
    例如："保存草稿" 按钮通常在页面底部，"下一步" 按钮在右下角。
    """

    # 京麦页面常见地标规则
    ANCHOR_RULES: dict[str, dict[str, Any]] = {
        "save_draft": {
            "anchor_texts": ["保存草稿", "保存", "草稿"],
            "region": "bottom_right",
            "relative_offset": (0, 0),
        },
        "next_step": {
            "anchor_texts": ["下一步", "下一步，完善其他商品信息"],
            "region": "bottom_right",
            "relative_offset": (0, 0),
        },
        "publish": {
            "anchor_texts": ["发布", "发布商品", "提交"],
            "region": "bottom_right",
            "relative_offset": (0, 0),
        },
        "main_image_slot": {
            "anchor_texts": ["主图", "主图视频"],
            "region": "center_left",
            "relative_offset": (100, 50),
        },
    }

    def __init__(self, window_width: int = 1920, window_height: int = 1080) -> None:
        self.window_width = window_width
        self.window_height = window_height

    def locate(
            self,
            target: str,
            page_text: str = "",
    ) -> GroundingCandidate:
        """基于文本地标推断元素位置。

        参数:
            target: 目标元素标识（如 "save_draft", "next_step"）
            page_text: 当前页面文本内容（用于验证地标是否存在）
        """
        rule = self.ANCHOR_RULES.get(target)
        if rule is None:
            return GroundingCandidate(
                method="anchor",
                confidence=0.0,
                error=f"未找到 {target} 的地标规则",
            )

        # 验证页面文本中是否包含地标关键词
        anchor_texts = rule.get("anchor_texts", [])
        text_match = any(t in page_text for t in anchor_texts) if page_text else False

        region = rule.get("region", "bottom_right")
        offset = rule.get("relative_offset", (0, 0))

        # 根据区域推断位置
        bbox = self._region_to_bbox(region, offset)
        point = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)

        confidence = 0.4 if text_match else 0.15

        return GroundingCandidate(
            method="anchor",
            bbox=bbox,
            point=point,
            confidence=confidence,
            element_info={
                "rule": target,
                "region": region,
                "anchor_texts_found": text_match,
            },
        )

    def _region_to_bbox(
            self,
            region: str,
            offset: tuple[int, int],
    ) -> tuple[int, int, int, int]:
        """将区域名称转换为近似边界框。"""
        w, h = self.window_width, self.window_height
        ox, oy = offset

        regions = {
            "bottom_right": (w * 3 // 4 + ox, h * 3 // 4 + oy, w - 20, h - 40),
            "bottom_left": (20, h * 3 // 4 + oy, w // 4 + ox, h - 40),
            "center_left": (20, h // 3 + oy, w // 2 + ox, h * 2 // 3),
            "center_right": (w // 2 + ox, h // 3 + oy, w - 20, h * 2 // 3),
            "top_right": (w * 3 // 4 + ox, 20, w - 20, h // 4 + oy),
            "top_left": (20, 20, w // 4 + ox, h // 4 + oy),
            "center": (w // 4 + ox, h // 3 + oy, w * 3 // 4, h * 2 // 3),
        }
        return regions.get(region, regions["center"])


# ── 三路 Grounding 仲裁器 ──────────────────────────────────────────


class ThreeWayGroundingProvider:
    """三路 Grounding 仲裁 — DOM/UIA + Vision + Anchor 候选融合。

    使用方式:
        provider = ThreeWayGroundingProvider(
            uia=UIAGroundingAdapter(adapter),
            vision=OllamaVisionProvider(...),
            anchor=AnchorGroundingAdapter(),
        )
        result = provider.ground(
            target="save_draft",
            window_handle="1187102",
            screenshot_path="screenshot.png",
            page_text="...",
        )
    """

    # 各路权重
    UIA_WEIGHT = 0.50
    VISION_WEIGHT = 0.35
    ANCHOR_WEIGHT = 0.15

    # 高置信度阈值：单路达到此值直接采用，不融合
    HIGH_CONFIDENCE = 0.8

    def __init__(
            self,
            uia: UIAGroundingAdapter | None = None,
            vision: Any = None,  # OllamaVisionProvider
            anchor: AnchorGroundingAdapter | None = None,
    ) -> None:
        self.uia = uia
        self.vision = vision
        self.anchor = anchor

    def ground(
            self,
            target: str,
            window_handle: str = "",
            screenshot_path: str | Path | None = None,
            page_text: str = "",
            target_type: str = "automation_id",
    ) -> GroundingResult:
        """执行三路 grounding 仲裁。

        参数:
            target: 定位目标（automation_id 或元素描述）
            window_handle: 窗口句柄
            screenshot_path: 最新截图路径（供 Vision 使用）
            page_text: 页面文本内容（供 Anchor 使用）
            target_type: UIA 定位方式

        返回:
            GroundingResult 包含最终采用的坐标和方法
        """
        candidates: list[GroundingCandidate] = []

        # ── 第一路：UIA（最快最准）──
        uia_candidate = self._try_uia(window_handle, target, target_type)
        candidates.append(uia_candidate)
        if uia_candidate.confidence >= self.HIGH_CONFIDENCE:
            return GroundingResult(
                success=True,
                method="uia",
                bbox=uia_candidate.bbox,
                point=uia_candidate.point,
                confidence=uia_candidate.confidence,
                candidates=candidates,
                fusion_method="single",
            )

        # ── 第二路：Vision ──
        vision_candidate = self._try_vision(screenshot_path, target)
        candidates.append(vision_candidate)
        if vision_candidate.confidence >= self.HIGH_CONFIDENCE:
            return GroundingResult(
                success=True,
                method="vision",
                bbox=vision_candidate.bbox,
                point=vision_candidate.point,
                confidence=vision_candidate.confidence,
                candidates=candidates,
                fusion_method="single",
            )

        # ── 第三路：Anchor ──
        anchor_candidate = self._try_anchor(target, page_text)
        candidates.append(anchor_candidate)

        # ── 融合仲裁 ──
        valid_candidates = [c for c in candidates if c.bbox is not None]
        if not valid_candidates:
            return GroundingResult(
                success=False,
                method="none",
                candidates=candidates,
                error="三路定位均失败",
            )

        if len(valid_candidates) == 1:
            c = valid_candidates[0]
            return GroundingResult(
                success=True,
                method=c.method,
                bbox=c.bbox,
                point=c.point,
                confidence=c.confidence,
                candidates=candidates,
                fusion_method="single",
            )

        # 加权平均融合
        fused_bbox, fused_point, fused_conf = self._weighted_fusion(valid_candidates)
        return GroundingResult(
            success=True,
            method="hybrid",
            bbox=fused_bbox,
            point=fused_point,
            confidence=fused_conf,
            candidates=candidates,
            fusion_method="weighted_average",
        )

    # ── 各路尝试 ─────────────────────────────────────────────────

    def _try_uia(
            self, window_handle: str, target: str, target_type: str
    ) -> GroundingCandidate:
        if self.uia is None:
            return GroundingCandidate(
                method="uia", confidence=0.0, error="UIA 定位器未配置"
            )
        return self.uia.locate(window_handle, target, target_type)

    def _try_vision(
            self, screenshot_path: str | Path | None, target: str
    ) -> GroundingCandidate:
        if self.vision is None:
            return GroundingCandidate(
                method="vision", confidence=0.0, error="Vision provider 未配置"
            )
        if screenshot_path is None:
            return GroundingCandidate(
                method="vision", confidence=0.0, error="无截图可用"
            )
        try:
            analysis = self.vision.locate_element(screenshot_path, target)
            if analysis.success and analysis.bbox:
                return GroundingCandidate(
                    method="vision",
                    bbox=analysis.bbox,
                    point=analysis.point,
                    confidence=analysis.confidence,
                    element_info={"model": analysis.model, "elapsed_ms": analysis.elapsed_ms},
                )
            return GroundingCandidate(
                method="vision",
                confidence=analysis.confidence if analysis else 0.0,
                error=analysis.error or "Vision 未找到目标",
            )
        except Exception as exc:
            return GroundingCandidate(
                method="vision", confidence=0.0, error=f"Vision 异常: {exc}"
            )

    def _try_anchor(
            self, target: str, page_text: str
    ) -> GroundingCandidate:
        if self.anchor is None:
            return GroundingCandidate(
                method="anchor", confidence=0.0, error="Anchor 定位器未配置"
            )
        return self.anchor.locate(target, page_text)

    # ── 加权融合 ─────────────────────────────────────────────────

    def _weighted_fusion(
            self, candidates: list[GroundingCandidate]
    ) -> tuple[tuple[int, int, int, int], tuple[int, int], float]:
        """按权重加权平均多个候选的 bbox 和 point。"""
        weight_map = {"uia": self.UIA_WEIGHT, "vision": self.VISION_WEIGHT, "anchor": self.ANCHOR_WEIGHT}

        total_weight = 0.0
        weighted_left = weighted_top = weighted_right = weighted_bottom = 0.0
        weighted_x = weighted_y = 0.0
        weighted_conf = 0.0

        for c in candidates:
            w = weight_map.get(c.method, 0.1) * c.confidence
            if w <= 0 or c.bbox is None:
                continue
            total_weight += w
            weighted_left += c.bbox[0] * w
            weighted_top += c.bbox[1] * w
            weighted_right += c.bbox[2] * w
            weighted_bottom += c.bbox[3] * w
            if c.point:
                weighted_x += c.point[0] * w
                weighted_y += c.point[1] * w
            weighted_conf += c.confidence * w

        if total_weight == 0:
            # 回退到第一个有 bbox 的候选
            for c in candidates:
                if c.bbox:
                    return c.bbox, c.point or (0, 0), c.confidence
            return (0, 0, 0, 0), (0, 0), 0.0

        fused_bbox = (
            int(weighted_left / total_weight),
            int(weighted_top / total_weight),
            int(weighted_right / total_weight),
            int(weighted_bottom / total_weight),
        )
        fused_point = (
            int(weighted_x / total_weight) if weighted_x else (fused_bbox[0] + fused_bbox[2]) // 2,
            int(weighted_y / total_weight) if weighted_y else (fused_bbox[1] + fused_bbox[3]) // 2,
        )
        fused_conf = weighted_conf / total_weight if total_weight else 0.0

        return fused_bbox, fused_point, min(fused_conf, 1.0)
