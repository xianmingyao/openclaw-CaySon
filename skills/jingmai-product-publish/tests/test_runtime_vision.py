"""test_runtime_vision.py — OllamaVisionProvider 测试。
BL-092: 验证截图分析、元素定位、前后对比、降级回退。
"""

from __future__ import annotations

import base64
import io
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from jingmai_publish.runtime.vision import (
    OllamaVisionProvider,
    VisionAnalysis,
    create_vision_provider_from_env,
)


# ── fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def vision_provider():
    return OllamaVisionProvider(
        base_url="http://localhost:11434",
        model="qwen3-vl:8b",
        timeout=30,
    )


@pytest.fixture
def vision_provider_with_fallback():
    return OllamaVisionProvider(
        base_url="http://localhost:11434",
        model="qwen3-vl:8b",
        timeout=30,
        fallback_base_url="http://localhost:8001",
        fallback_model="fallback-model",
    )


@pytest.fixture
def sample_image_path(tmp_path):
    """创建一张 200x200 的测试 PNG。"""
    img = Image.new("RGB", (200, 200), color="blue")
    img_path = tmp_path / "test.png"
    img.save(img_path, "PNG")
    return str(img_path)


@pytest.fixture
def large_image_path(tmp_path):
    """创建一张超过 max_image_size 的测试 PNG。"""
    img = Image.new("RGB", (3000, 3000), color="red")
    img_path = tmp_path / "large.png"
    img.save(img_path, "PNG")
    return str(img_path)


# ── VisionAnalysis ───────────────────────────────────────────────────


class TestVisionAnalysis:
    def test_defaults(self):
        va = VisionAnalysis(success=True)
        assert va.success is True
        assert va.page_state is None
        assert va.elements == []
        assert va.text_content == ""
        assert va.bbox is None
        assert va.point is None
        assert va.confidence == 0.0
        assert va.raw_response == ""
        assert va.model == ""
        assert va.elapsed_ms == 0.0
        assert va.error is None

    def test_to_dict(self):
        va = VisionAnalysis(
            success=True,
            page_state="form_filled",
            elements=[{"type": "input", "text": "test"}],
            text_content="hello world",
            bbox=(10, 20, 30, 40),
            point=(20, 30),
            confidence=0.85,
            model="qwen3-vl:8b",
            elapsed_ms=500.0,
            error=None,
        )
        d = va.to_dict()
        assert d["success"] is True
        assert d["page_state"] == "form_filled"
        assert d["bbox"] == [10, 20, 30, 40]
        assert d["point"] == [20, 30]
        assert d["confidence"] == 0.85
        assert d["model"] == "qwen3-vl:8b"
        assert d["elapsed_ms"] == 500.0
        assert d["error"] is None

    def test_to_dict_with_none_bbox_and_point(self):
        va = VisionAnalysis(success=False, error="failed")
        d = va.to_dict()
        assert d["bbox"] is None
        assert d["point"] is None


# ── OllamaVisionProvider 初始化 ──────────────────────────────────────


class TestInit:
    def test_default_values(self):
        p = OllamaVisionProvider()
        assert p.base_url == "http://localhost:11434"
        assert p.model == "qwen3-vl:8b"
        assert p.timeout == 120
        assert p.max_image_size == 2048

    def test_custom_values(self):
        p = OllamaVisionProvider(
            base_url="http://custom:9999",
            model="custom-model",
            timeout=60,
            max_image_size=1024,
        )
        assert p.base_url == "http://custom:9999"
        assert p.model == "custom-model"
        assert p.timeout == 60
        assert p.max_image_size == 1024

    def test_base_url_strips_trailing_slash(self):
        p = OllamaVisionProvider(base_url="http://localhost:11434/")
        assert p.base_url == "http://localhost:11434"


# ── _encode_image ────────────────────────────────────────────────────


class TestEncodeImage:
    def test_encodes_small_image(self, vision_provider, sample_image_path):
        b64 = vision_provider._encode_image(Path(sample_image_path))
        assert isinstance(b64, str)
        # 验证是有效 base64
        decoded = base64.b64decode(b64)
        assert len(decoded) > 0

    def test_scales_large_image(self, vision_provider, large_image_path):
        b64 = vision_provider._encode_image(Path(large_image_path))
        decoded = base64.b64decode(b64)
        # 解码后应该是 PNG
        img = Image.open(io.BytesIO(decoded))
        assert max(img.size) <= 2048

    def test_nonexistent_file(self, vision_provider, tmp_path):
        bad_path = tmp_path / "nonexistent.png"
        result = vision_provider.analyze_screenshot(bad_path)
        assert result.success is False
        assert "不存在" in result.error


# ── _extract_json ────────────────────────────────────────────────────


class TestExtractJson:
    def test_plain_json(self, vision_provider):
        text = '{"success": true, "confidence": 0.9}'
        data = vision_provider._extract_json(text)
        assert data == {"success": True, "confidence": 0.9}

    def test_json_in_code_block(self, vision_provider):
        text = '```json\n{"success": true, "confidence": 0.8}\n```'
        data = vision_provider._extract_json(text)
        assert data == {"success": True, "confidence": 0.8}

    def test_json_without_lang_tag(self, vision_provider):
        text = '```\n{"found": true}\n```'
        data = vision_provider._extract_json(text)
        assert data == {"found": True}

    def test_embedded_json_with_prefix_suffix(self, vision_provider):
        text = '分析结果：{"found": true, "bbox": [1,2,3,4]} 完毕'
        data = vision_provider._extract_json(text)
        assert data == {"found": True, "bbox": [1, 2, 3, 4]}

    def test_invalid_text(self, vision_provider):
        text = "没有 JSON 的纯文本"
        data = vision_provider._extract_json(text)
        assert data is None

    def test_empty_text(self, vision_provider):
        data = vision_provider._extract_json("")
        assert data is None

    def test_none_text(self, vision_provider):
        data = vision_provider._extract_json(None)
        assert data is None


# ── _parse_analysis_response ─────────────────────────────────────────


class TestParseAnalysisResponse:
    def test_parses_valid_json(self, vision_provider):
        text = json.dumps({
            "page_state": "form_filled",
            "text_content": "商品标题",
            "elements": [{"type": "input", "text": "test"}],
            "confidence": 0.9,
        })
        result = vision_provider._parse_analysis_response(text)
        assert result.success is True
        assert result.page_state == "form_filled"
        assert result.text_content == "商品标题"
        assert len(result.elements) == 1
        assert result.confidence == 0.9

    def test_fallback_on_invalid_json(self, vision_provider):
        text = "这不是有效 JSON"
        result = vision_provider._parse_analysis_response(text)
        assert result.success is True  # 部分成功
        assert result.page_state == "unknown"
        assert result.confidence == 0.1
        assert result.text_content == text[:500]


# ── _parse_comparison_response ───────────────────────────────────────


class TestParseComparisonResponse:
    def test_action_successful(self, vision_provider):
        text = json.dumps({
            "changed": True,
            "action_successful": True,
            "page_state_after": "draft_saved",
            "changes": [{"region": "button", "before": "enabled", "after": "disabled"}],
            "confidence": 0.92,
        })
        result = vision_provider._parse_comparison_response(text)
        assert result.success is True
        assert result.page_state == "draft_saved"
        assert result.confidence == 0.92

    def test_action_failed(self, vision_provider):
        text = json.dumps({
            "changed": False,
            "action_successful": False,
            "page_state_after": "error_displayed",
            "changes": [],
            "confidence": 0.7,
        })
        result = vision_provider._parse_comparison_response(text)
        assert result.success is False
        assert result.page_state == "error_displayed"

    def test_invalid_json_fallback(self, vision_provider):
        text = "no json here"
        result = vision_provider._parse_comparison_response(text)
        assert result.success is False
        assert result.page_state == "comparison_failed"
        assert result.confidence == 0.1


# ── _parse_location_response ─────────────────────────────────────────


class TestParseLocationResponse:
    def test_found_with_bbox_and_point(self, vision_provider):
        text = json.dumps({
            "found": True,
            "description": "保存按钮",
            "bbox": [100, 200, 300, 250],
            "point": [200, 225],
            "confidence": 0.88,
        })
        result = vision_provider._parse_location_response(text)
        assert result.success is True
        assert result.bbox == (100, 200, 300, 250)
        assert result.point == (200, 225)
        assert result.confidence == 0.88

    def test_not_found(self, vision_provider):
        text = json.dumps({
            "found": False,
            "confidence": 0.1,
        })
        result = vision_provider._parse_location_response(text)
        assert result.success is False
        assert result.bbox is None
        assert result.point is None

    def test_invalid_json(self, vision_provider):
        text = "garbage"
        result = vision_provider._parse_location_response(text)
        assert result.success is False
        assert "无法解析" in result.error


# ── Ollama API 调用 (mock) ───────────────────────────────────────────


class TestOllamaApiCall:
    @patch("jingmai_publish.runtime.vision.requests.post")
    def test_analyze_screenshot_success(
            self, mock_post, vision_provider, sample_image_path
    ):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "message": {
                "content": json.dumps({
                    "page_state": "basic_info",
                    "text_content": "商品信息",
                    "elements": [],
                    "confidence": 0.95,
                })
            }
        }
        result = vision_provider.analyze_screenshot(sample_image_path)
        assert result.success is True
        assert result.page_state == "basic_info"
        assert result.confidence == 0.95
        assert result.model == "qwen3-vl:8b"
        assert result.elapsed_ms > 0

    @patch("jingmai_publish.runtime.vision.requests.post")
    def test_compare_screenshots_success(
            self, mock_post, vision_provider, sample_image_path
    ):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "message": {
                "content": json.dumps({
                    "changed": True,
                    "action_successful": True,
                    "page_state_after": "draft_saved",
                    "changes": [],
                    "confidence": 0.9,
                })
            }
        }
        result = vision_provider.compare_screenshots(
            sample_image_path, sample_image_path
        )
        assert result.success is True
        assert result.page_state == "draft_saved"

    @patch("jingmai_publish.runtime.vision.requests.post")
    def test_locate_element_success(
            self, mock_post, vision_provider, sample_image_path
    ):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "message": {
                "content": json.dumps({
                    "found": True,
                    "bbox": [10, 20, 100, 50],
                    "point": [55, 35],
                    "confidence": 0.85,
                })
            }
        }
        result = vision_provider.locate_element(sample_image_path, "保存按钮")
        assert result.success is True
        assert result.bbox == (10, 20, 100, 50)

    @patch("jingmai_publish.runtime.vision.requests.post")
    def test_ollama_returns_non_200(
            self, mock_post, vision_provider, sample_image_path
    ):
        mock_post.return_value.status_code = 500
        result = vision_provider.analyze_screenshot(sample_image_path)
        assert result.success is False
        assert "不可用" in result.error


# ── vLLM 回退 ────────────────────────────────────────────────────────


class TestVllmFallback:
    @patch("jingmai_publish.runtime.vision.requests.post")
    def test_falls_back_to_vllm_when_ollama_fails(
            self, mock_post, vision_provider_with_fallback, sample_image_path
    ):
        """Ollama 不可用时应回退到 vLLM。"""
        # 第一次调用：Ollama 500 → 第二次调用：vLLM 200
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.side_effect = [
            # vLLM 响应
            {
                "choices": [{
                    "message": {
                        "content": json.dumps({
                            "page_state": "form_filled",
                            "text_content": "test",
                            "elements": [],
                            "confidence": 0.8,
                        })
                    }
                }]
            }
        ]

        # 需要 Ollama 先失败再走 vLLM
        # 用不同的 side_effect
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            resp = MagicMock()
            if "/api/chat" in args[0]:
                resp.status_code = 500  # Ollama 失败
            else:
                resp.status_code = 200
                resp.json.return_value = {
                    "choices": [{
                        "message": {
                            "content": json.dumps({
                                "page_state": "vllm_fallback",
                                "text_content": "vllm",
                                "elements": [],
                                "confidence": 0.75,
                            })
                        }
                    }]
                }
            return resp

        mock_post.side_effect = side_effect

        result = vision_provider_with_fallback.analyze_screenshot(sample_image_path)
        # vLLM 回退成功
        assert result.success is True

    @patch("jingmai_publish.runtime.vision.requests.post")
    def test_both_fail(self, mock_post, vision_provider_with_fallback, sample_image_path):
        """Ollama 和 vLLM 都失败时返回 error。"""
        mock_post.return_value.status_code = 500
        result = vision_provider_with_fallback.analyze_screenshot(sample_image_path)
        assert result.success is False
        assert "不可用" in result.error


# ── compare_screenshots 第二张图不存在 ───────────────────────────────


class TestCompareScreenshotsEdgeCases:
    @patch("jingmai_publish.runtime.vision.requests.post")
    def test_second_image_missing(
            self, mock_post, vision_provider, sample_image_path, tmp_path
    ):
        bad_path = tmp_path / "missing.png"
        result = vision_provider.compare_screenshots(sample_image_path, bad_path)
        assert result.success is False
        assert "不存在" in result.error


# ── 工厂函数 ─────────────────────────────────────────────────────────


class TestCreateFromEnv:
    def test_defaults(self, monkeypatch):
        monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
        monkeypatch.delenv("OLLAMA_MODEL", raising=False)
        monkeypatch.delenv("LLM_TIMEOUT", raising=False)
        monkeypatch.delenv("VLLM_BASE_URL", raising=False)
        monkeypatch.delenv("VLLM_MODEL", raising=False)
        p = create_vision_provider_from_env()
        assert p.base_url == "http://localhost:11434"
        assert p.model == "qwen3-vl:8b"
        assert p.timeout == 120
        assert p.fallback_base_url is None
        assert p.fallback_model is None

    def test_custom_values(self, monkeypatch):
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://custom:1234")
        monkeypatch.setenv("OLLAMA_MODEL", "custom-vl")
        monkeypatch.setenv("LLM_TIMEOUT", "60")
        monkeypatch.setenv("VLLM_BASE_URL", "http://vllm:8001")
        monkeypatch.setenv("VLLM_MODEL", "vllm-model")
        p = create_vision_provider_from_env()
        assert p.base_url == "http://custom:1234"
        assert p.model == "custom-vl"
        assert p.timeout == 60
        assert p.fallback_base_url == "http://vllm:8001"
        assert p.fallback_model == "vllm-model"


# ── 图片编码异常 ─────────────────────────────────────────────────────


class TestImageEncodingErrors:
    def test_invalid_image_file(self, vision_provider, tmp_path):
        bad_img = tmp_path / "bad.png"
        bad_img.write_text("not an image")
        result = vision_provider.analyze_screenshot(bad_img)
        assert result.success is False
        assert "编码" in result.error


# ── _convert_to_openai_format ────────────────────────────────────────


class TestConvertToOpenaiFormat:
    def test_string_content_passthrough(self, vision_provider):
        msgs = [{"role": "user", "content": "hello"}]
        result = vision_provider._convert_to_openai_format(msgs)
        assert result[0]["content"] == "hello"

    def test_list_content_conversion(self, vision_provider):
        msgs = [{
            "role": "user",
            "content": [
                {"type": "text", "text": "describe"},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64,abc"}},
            ]
        }]
        result = vision_provider._convert_to_openai_format(msgs)
        assert result[0]["role"] == "user"
        assert len(result[0]["content"]) == 2
        assert result[0]["content"][0]["type"] == "text"
        assert result[0]["content"][1]["type"] == "image_url"
