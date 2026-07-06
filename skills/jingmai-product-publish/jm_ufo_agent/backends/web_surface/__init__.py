"""WebView fallback backend。"""

from __future__ import annotations

from jm_ufo_agent.backends.web_surface.clipboard_fill import ClipboardFillResult, ClipboardFillService, SystemClipboardFillService
from jm_ufo_agent.backends.web_surface.coordinate_plan import CoordinatePlan, CoordinatePlanner, Rect
from jm_ufo_agent.backends.web_surface.form_loop import LocalSimilarityVerifier, WebViewFieldLoopResult, WebViewFormLoop
from jm_ufo_agent.backends.web_surface.screenshot_ocr import OcrBlock, ScreenshotOcrResult, ScreenshotOcrService, TesseractOcrProvider
from jm_ufo_agent.backends.web_surface.verifier import SurfaceVerificationResult, SurfaceVerifier

__all__ = [
    "ClipboardFillResult",
    "ClipboardFillService",
    "CoordinatePlan",
    "CoordinatePlanner",
    "LocalSimilarityVerifier",
    "OcrBlock",
    "Rect",
    "ScreenshotOcrResult",
    "ScreenshotOcrService",
    "SurfaceVerificationResult",
    "SurfaceVerifier",
    "SystemClipboardFillService",
    "TesseractOcrProvider",
    "WebViewFieldLoopResult",
    "WebViewFormLoop",
]
