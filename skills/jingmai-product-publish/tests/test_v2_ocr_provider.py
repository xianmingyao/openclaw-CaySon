"""ScreenshotOcrService 真实 Provider 桥接测试。"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from jm_ufo_agent.backends.web_surface.screenshot_ocr import (
    LocalPaddleOcrProvider,
    ScreenshotOcrResult,
    ScreenshotOcrService,
)


class TestLocalPaddleOcrProvider:
    def test_provider_protocol_match(self):
        """LocalPaddleOcrProvider 应实现 capture_and_ocr 协议。"""
        provider = LocalPaddleOcrProvider()
        assert hasattr(provider, "capture_and_ocr")
        assert callable(provider.capture_and_ocr)

    @pytest.mark.asyncio
    async def test_provider_returns_result(self):
        """Provider 应返回 ScreenshotOcrResult（无 PaddleOCR 时 graceful fallback）。"""
        provider = LocalPaddleOcrProvider()
        result = await provider.capture_and_ocr()
        assert isinstance(result, ScreenshotOcrResult)
        # PaddleOCR 未安装时返回 fallback
        assert result.page_signature == "paddleocr-not-installed"


class TestScreenshotOcrServiceWithProvider:
    @pytest.mark.asyncio
    async def test_service_uses_injected_provider(self):
        """注入 provider 后 service 应使用它而非 dry-run。"""
        mock_provider = AsyncMock()
        mock_provider.capture_and_ocr.return_value = ScreenshotOcrResult(
            page_signature="test_sig",
            blocks=[],
        )
        service = ScreenshotOcrService(provider=mock_provider)
        result = await service.capture_and_ocr()
        assert result.page_signature == "test_sig"
        mock_provider.capture_and_ocr.assert_called_once()

    @pytest.mark.asyncio
    async def test_service_dry_run_without_provider(self):
        """没有 provider 时 service 返回 dry-run。"""
        service = ScreenshotOcrService()
        result = await service.capture_and_ocr()
        assert result.page_signature == "dry-run"
