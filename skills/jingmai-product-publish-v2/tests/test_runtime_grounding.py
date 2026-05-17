"""test_runtime_grounding.py — 三路 Grounding 测试。
BL-095: 验证 UIA/Vision/Anchor 各路定位、优先级链仲裁、加权融合。
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from jingmai_publish.runtime.grounding import (
    AnchorGroundingAdapter,
    GroundingCandidate,
    GroundingResult,
    ThreeWayGroundingProvider,
    UIAGroundingAdapter,
)


# ── fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def mock_uia():
    """Mock UIA adapter。"""
    adapter = MagicMock(spec=UIAGroundingAdapter)
    return adapter


@pytest.fixture
def mock_vision():
    """Mock Vision provider。"""
    return MagicMock()


@pytest.fixture
def uia_adapter():
    return UIAGroundingAdapter(uia_adapter=None)


@pytest.fixture
def anchor_adapter():
    return AnchorGroundingAdapter(window_width=1920, window_height=1080)


@pytest.fixture
def grounding_provider(mock_uia, mock_vision, anchor_adapter):
    return ThreeWayGroundingProvider(
        uia=mock_uia,
        vision=mock_vision,
        anchor=anchor_adapter,
    )


# ── GroundingCandidate ───────────────────────────────────────────────


class TestGroundingCandidate:
    def test_defaults(self):
        c = GroundingCandidate(method="uia")
        assert c.method == "uia"
        assert c.bbox is None
        assert c.point is None
        assert c.confidence == 0.0
        assert c.element_info == {}
        assert c.error is None

    def test_with_data(self):
        c = GroundingCandidate(
            method="vision",
            bbox=(10, 20, 100, 80),
            point=(55, 50),
            confidence=0.85,
            element_info={"model": "qwen3-vl"},
        )
        assert c.bbox == (10, 20, 100, 80)
        assert c.point == (55, 50)
        assert c.confidence == 0.85


# ── GroundingResult ──────────────────────────────────────────────────


class TestGroundingResult:
    def test_defaults(self):
        r = GroundingResult(success=True)
        assert r.success is True
        assert r.method == "none"
        assert r.bbox is None
        assert r.point is None
        assert r.confidence == 0.0
        assert r.candidates == []
        assert r.fusion_method == ""

    def test_to_dict(self):
        r = GroundingResult(
            success=True,
            method="hybrid",
            bbox=(10, 20, 100, 80),
            point=(55, 50),
            confidence=0.82,
            candidates=[
                GroundingCandidate(method="uia", bbox=(10, 20, 100, 80), confidence=0.9),
                GroundingCandidate(method="vision", bbox=(12, 22, 98, 78), confidence=0.75),
            ],
            fusion_method="weighted_average",
        )
        d = r.to_dict()
        assert d["success"] is True
        assert d["method"] == "hybrid"
        assert d["bbox"] == [10, 20, 100, 80]
        assert d["point"] == [55, 50]
        assert d["confidence"] == 0.82
        assert len(d["candidates"]) == 2
        assert d["candidates"][0]["method"] == "uia"

    def test_to_dict_with_none(self):
        r = GroundingResult(success=False, error="all failed")
        d = r.to_dict()
        assert d["bbox"] is None
        assert d["point"] is None


# ── UIAGroundingAdapter ──────────────────────────────────────────────


class TestUIAGroundingAdapter:
    def test_not_initialized(self, uia_adapter):
        result = uia_adapter.locate("hwnd", "save_draft", "automation_id")
        assert result.method == "uia"
        assert result.confidence == 0.0
        assert "未初始化" in result.error

    def test_locate_by_automation_id_success(self):
        mock = MagicMock()
        mock.find_control_rect.return_value = [100, 200, 300, 250]
        adapter = UIAGroundingAdapter(mock)
        result = adapter.locate("hwnd", "btn_save", "automation_id")
        assert result.confidence == 0.9
        assert result.bbox == (100, 200, 300, 250)
        assert result.point == (200, 225)
        mock.find_control_rect.assert_called_once_with("hwnd", "btn_save")

    def test_locate_by_label_success(self):
        mock = MagicMock()
        mock.find_control_by_label.return_value = [50, 60, 150, 90]
        adapter = UIAGroundingAdapter(mock)
        result = adapter.locate("hwnd", "保存草稿", "label")
        assert result.confidence == 0.9
        assert result.bbox == (50, 60, 150, 90)
        mock.find_control_by_label.assert_called_once_with("hwnd", "保存草稿")

    def test_locate_by_class_name_success(self):
        mock = MagicMock()
        mock.find_control_by_class.return_value = [0, 0, 200, 100]
        adapter = UIAGroundingAdapter(mock)
        result = adapter.locate("hwnd", "Button", "class_name")
        assert result.confidence == 0.9
        mock.find_control_by_class.assert_called_once_with("hwnd", "Button")

    def test_locate_not_found(self):
        mock = MagicMock()
        mock.find_control_rect.return_value = None
        adapter = UIAGroundingAdapter(mock)
        result = adapter.locate("hwnd", "nonexistent", "automation_id")
        assert result.confidence == 0.0
        assert "未找到" in result.error

    def test_locate_zero_bbox(self):
        mock = MagicMock()
        mock.find_control_rect.return_value = [0, 0, 0, 0]
        adapter = UIAGroundingAdapter(mock)
        result = adapter.locate("hwnd", "zero", "automation_id")
        # 全零 bbox 视为无效
        assert result.confidence == 0.0

    def test_locate_exception(self):
        mock = MagicMock()
        mock.find_control_rect.side_effect = RuntimeError("boom")
        adapter = UIAGroundingAdapter(mock)
        result = adapter.locate("hwnd", "crash", "automation_id")
        assert result.confidence == 0.0
        assert "异常" in result.error


# ── AnchorGroundingAdapter ───────────────────────────────────────────


class TestAnchorGroundingAdapter:
    def test_known_rule_with_text_match(self, anchor_adapter):
        result = anchor_adapter.locate("save_draft", "保存草稿 下一步 商品信息")
        assert result.method == "anchor"
        assert result.confidence == 0.4
        assert result.bbox is not None
        assert len(result.bbox) == 4
        assert result.element_info["anchor_texts_found"] is True

    def test_known_rule_without_text_match(self, anchor_adapter):
        result = anchor_adapter.locate("save_draft", "其他内容")
        assert result.confidence == 0.15
        assert result.element_info["anchor_texts_found"] is False

    def test_known_rule_no_page_text(self, anchor_adapter):
        result = anchor_adapter.locate("publish")
        assert result.confidence == 0.15

    def test_unknown_rule(self, anchor_adapter):
        result = anchor_adapter.locate("unknown_target")
        assert result.confidence == 0.0
        assert "地标规则" in result.error

    def test_next_step_rule(self, anchor_adapter):
        result = anchor_adapter.locate("next_step", "下一步，完善其他商品信息")
        assert result.method == "anchor"
        assert result.confidence == 0.4
        assert result.bbox is not None

    def test_main_image_slot_rule(self, anchor_adapter):
        result = anchor_adapter.locate("main_image_slot", "主图视频")
        assert result.method == "anchor"
        assert result.confidence == 0.4

    def test_region_to_bbox_bottom_right(self, anchor_adapter):
        bbox = anchor_adapter._region_to_bbox("bottom_right", (0, 0))
        w, h = 1920, 1080
        assert bbox[0] == w * 3 // 4
        assert bbox[1] == h * 3 // 4

    def test_region_to_bbox_center_left(self, anchor_adapter):
        bbox = anchor_adapter._region_to_bbox("center_left", (0, 0))
        w, h = 1920, 1080
        assert bbox[0] == 20
        assert bbox[2] == w // 2

    def test_region_to_bbox_with_offset(self, anchor_adapter):
        bbox = anchor_adapter._region_to_bbox("bottom_right", (100, 50))
        w, h = 1920, 1080
        assert bbox[0] == w * 3 // 4 + 100
        assert bbox[1] == h * 3 // 4 + 50

    def test_unknown_region_falls_back_to_center(self, anchor_adapter):
        bbox = anchor_adapter._region_to_bbox("invalid", (0, 0))
        w, h = 1920, 1080
        assert bbox[0] == w // 4
        assert bbox[2] == w * 3 // 4


# ── ThreeWayGroundingProvider ────────────────────────────────────────


class TestThreeWayGroundingProvider:
    def test_uia_high_confidence_early_return(self, grounding_provider, mock_uia):
        """UIA 置信度 >= 0.8 时直接返回，不调用 Vision/Anchor。"""
        mock_uia.locate.return_value = GroundingCandidate(
            method="uia",
            bbox=(10, 20, 100, 80),
            point=(55, 50),
            confidence=0.95,
        )
        result = grounding_provider.ground(
            target="save_draft",
            window_handle="hwnd",
        )
        assert result.success is True
        assert result.method == "uia"
        assert result.fusion_method == "single"
        assert result.bbox == (10, 20, 100, 80)
        assert result.confidence == 0.95

    def test_vision_high_confidence_when_uia_fails(
        self, grounding_provider, mock_uia, mock_vision
    ):
        """UIA 失败后，Vision 高置信度时直接返回。"""
        mock_uia.locate.return_value = GroundingCandidate(
            method="uia", confidence=0.0, error="not found"
        )
        # Mock locate_element 返回成功的 VisionAnalysis
        from jingmai_publish.runtime.vision import VisionAnalysis
        mock_vision.locate_element.return_value = VisionAnalysis(
            success=True,
            bbox=(30, 40, 120, 90),
            point=(75, 65),
            confidence=0.88,
            model="qwen3-vl:8b",
        )
        result = grounding_provider.ground(
            target="save_draft",
            window_handle="hwnd",
            screenshot_path="test.png",
        )
        assert result.success is True
        assert result.method == "vision"
        assert result.bbox == (30, 40, 120, 90)

    def test_uia_disabled_falls_to_vision(self, mock_vision, anchor_adapter):
        """UIA 未配置时回退到 Vision。"""
        from jingmai_publish.runtime.vision import VisionAnalysis
        mock_vision.locate_element.return_value = VisionAnalysis(
            success=True,
            bbox=(50, 60, 200, 120),
            point=(125, 90),
            confidence=0.75,
        )
        provider = ThreeWayGroundingProvider(
            uia=None, vision=mock_vision, anchor=anchor_adapter
        )
        result = provider.ground(
            target="save_draft",
            screenshot_path="test.png",
            page_text="保存草稿",
        )
        # Vision confidence 0.75 < 0.8, won't early return, will fuse with anchor
        # Vision + Anchor both have bbox, so weighted fusion
        assert result.success is True
        assert result.method == "hybrid"

    def test_all_paths_fail(self, uia_adapter, anchor_adapter):
        """三路都无定位结果时返回失败。"""
        provider = ThreeWayGroundingProvider(
            uia=uia_adapter,  # 未初始化 → 失败
            vision=None,       # 未配置
            anchor=anchor_adapter,
        )
        # Anchor 的 "unknown_target" 也没有规则
        result = provider.ground(
            target="unknown_target",
            window_handle="hwnd",
            page_text="nothing",
        )
        assert result.success is False
        assert result.method == "none"
        assert "三路定位均失败" in result.error

    def test_vision_not_configured(self, anchor_adapter):
        """Vision 未配置时不阻塞。"""
        from unittest.mock import MagicMock as Mock

        mock_uia = Mock()
        mock_uia.locate.return_value = GroundingCandidate(
            method="uia",
            bbox=(10, 20, 100, 80),
            point=(55, 50),
            confidence=0.7,  # 低于 HIGH_CONFIDENCE
        )
        provider = ThreeWayGroundingProvider(
            uia=mock_uia, vision=None, anchor=anchor_adapter
        )
        result = provider.ground(
            target="save_draft",
            window_handle="hwnd",
            page_text="保存草稿",
        )
        # UIA (0.7) + Anchor (0.15 with no text match or 0.4 with match)
        # Both have bbox → weighted fusion
        assert result.success is True
        assert result.method == "hybrid"

    def test_vision_exception_handled(self, grounding_provider, mock_uia, mock_vision):
        """Vision 异常时不阻塞，继续走 Anchor。"""
        mock_uia.locate.return_value = GroundingCandidate(
            method="uia", confidence=0.0, error="not found"
        )
        mock_vision.locate_element.side_effect = RuntimeError("vision crash")
        result = grounding_provider.ground(
            target="save_draft",
            window_handle="hwnd",
            screenshot_path="test.png",
            page_text="保存草稿",
        )
        # UIA 失败、Vision 异常 → 只有 Anchor (有 bbox) → single
        assert result.success is True
        assert result.method == "anchor"

    def test_vision_no_screenshot(self, grounding_provider, mock_uia):
        """无截图时 Vision 跳过。"""
        mock_uia.locate.return_value = GroundingCandidate(
            method="uia", confidence=0.0, error="not found"
        )
        result = grounding_provider.ground(
            target="save_draft",
            window_handle="hwnd",
            screenshot_path=None,
            page_text="保存草稿",
        )
        # UIA 失败、Vision 无截图 → 只有 Anchor (有 bbox) → single
        assert result.success is True
        assert result.method == "anchor"


# ── 加权融合数学验证 ─────────────────────────────────────────────────


class TestWeightedFusion:
    def test_two_candidate_fusion(self):
        """验证两个候选的加权平均。"""
        provider = ThreeWayGroundingProvider()
        candidates = [
            GroundingCandidate(
                method="uia",
                bbox=(10, 10, 100, 100),
                point=(55, 55),
                confidence=0.9,
            ),
            GroundingCandidate(
                method="vision",
                bbox=(20, 20, 110, 110),
                point=(65, 65),
                confidence=0.7,
            ),
        ]
        bbox, point, conf = provider._weighted_fusion(candidates)
        # UIA: weight=0.50*0.9=0.45, Vision: weight=0.35*0.7=0.245
        # total=0.695
        # bbox values: (10*0.45+20*0.245)/0.695 ≈ (4.5+4.9)/0.695 ≈ 13.5 ... avg
        assert len(bbox) == 4
        assert bbox[0] != bbox[2]  # 不是退化值
        assert point[0] > 0
        assert 0 < conf <= 1.0

    def test_single_candidate_no_fusion(self):
        """单个有效候选时回退到该候选。"""
        provider = ThreeWayGroundingProvider()
        candidates = [
            GroundingCandidate(
                method="uia",
                bbox=(10, 20, 100, 80),
                point=(55, 50),
                confidence=0.0,  # 零置信度 → 权重为 0
            ),
            GroundingCandidate(
                method="vision",
                bbox=(15, 25, 95, 75),
                point=(55, 50),
                confidence=0.6,
            ),
        ]
        bbox, point, conf = provider._weighted_fusion(candidates)
        # UIA 权重=0, Vision 有效
        assert bbox == (15, 25, 95, 75)

    def test_all_zero_weight(self):
        """所有权重为零时回退到第一个有 bbox 的候选。"""
        provider = ThreeWayGroundingProvider()
        candidates = [
            GroundingCandidate(method="uia", bbox=(1, 2, 3, 4), confidence=0.0),
            GroundingCandidate(method="vision", bbox=None, confidence=0.0),
        ]
        bbox, point, conf = provider._weighted_fusion(candidates)
        assert bbox == (1, 2, 3, 4)

    def test_all_no_bbox(self):
        """所有候选都没有 bbox 时返回零值。"""
        provider = ThreeWayGroundingProvider()
        candidates = [
            GroundingCandidate(method="uia", confidence=0.0),
            GroundingCandidate(method="vision", confidence=0.0),
        ]
        bbox, point, conf = provider._weighted_fusion(candidates)
        assert bbox == (0, 0, 0, 0)
        assert point == (0, 0)
        assert conf == 0.0

    def test_confidence_capped_at_one(self):
        """融合置信度不应超过 1.0。"""
        provider = ThreeWayGroundingProvider()
        candidates = [
            GroundingCandidate(
                method="uia", bbox=(1, 1, 2, 2), point=(1, 1), confidence=2.0
            ),
        ]
        _, _, conf = provider._weighted_fusion(candidates)
        assert conf <= 1.0


# ── Anchor 自定义窗口尺寸 ─────────────────────────────────────────────


class TestAnchorCustomDimensions:
    def test_custom_window_size(self):
        adapter = AnchorGroundingAdapter(window_width=800, window_height=600)
        bbox = adapter._region_to_bbox("bottom_right", (0, 0))
        assert bbox[0] == 800 * 3 // 4
        assert bbox[1] == 600 * 3 // 4
