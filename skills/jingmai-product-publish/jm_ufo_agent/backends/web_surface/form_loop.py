"""WebView 表单读写验证闭环。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jm_ufo_agent.backends.web_surface.clipboard_fill import ClipboardFillService
from jm_ufo_agent.backends.web_surface.coordinate_plan import CoordinatePlanner, Rect
from jm_ufo_agent.backends.web_surface.screenshot_ocr import OcrBlock, ScreenshotOcrService
from jm_ufo_agent.backends.web_surface.verifier import SurfaceVerifier


@dataclass(frozen=True)
class WebViewFieldLoopResult:
    """单字段 WebView 填写闭环结果。"""

    ok: bool
    field_name: str
    page_signature: str
    fill_message: str
    verify_reason: str
    screenshot_path: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


class LocalSimilarityVerifier:
    """局部截图相似度校验器。"""

    def compare_text_blocks(self, before: list[OcrBlock], after: list[OcrBlock]) -> float:
        """用 OCR 文本集合估算局部变化相似度。"""

        # 当前阶段还没有接入 OpenCV 图像差分，所以先用 OCR 文本集合做可测试近似。
        # 两次 OCR 完全一致返回 1.0；完全不同返回 0.0。
        # 后续接入真实局部截图相似度时，可以保持这个方法签名不变。
        before_text = {block.text for block in before}
        after_text = {block.text for block in after}
        if not before_text and not after_text:
            return 1.0
        union = before_text | after_text
        return len(before_text & after_text) / len(union)


class WebViewFormLoop:
    """执行截图、OCR、坐标、剪贴板、读回验证闭环。"""

    def __init__(
        self,
        ocr: ScreenshotOcrService | None = None,
        planner: CoordinatePlanner | None = None,
        clipboard: ClipboardFillService | None = None,
        verifier: SurfaceVerifier | None = None,
        similarity: LocalSimilarityVerifier | None = None,
    ):
        """初始化 WebView 表单闭环依赖。"""

        # 每个依赖都支持注入，真实 backend 和单元测试可以复用同一套编排逻辑。
        # 默认依赖全部是本地 dry-run 安全实现，不会访问真实桌面、剪贴板或 OCR 引擎。
        # 该类只负责单字段闭环，不直接修改 GraphState，避免状态推进和设备动作耦合。
        self.ocr = ocr or ScreenshotOcrService()
        self.planner = planner or CoordinatePlanner()
        self.clipboard = clipboard or ClipboardFillService()
        self.verifier = verifier or SurfaceVerifier()
        self.similarity = similarity or LocalSimilarityVerifier()

    async def fill_and_verify(self, field_name: str, label_rect: Rect, expected_value: object) -> WebViewFieldLoopResult:
        """填写一个字段并读回验证。"""

        # 第一步截图 OCR，得到页面签名和填写前的局部文本证据。
        # 第二步根据字段标签矩形生成坐标计划，再执行剪贴板填充。
        # 第三步重新截图 OCR，读回字段值并生成局部相似度证据。
        before = await self.ocr.capture_and_ocr()
        plan = self.planner.plan_from_label(field_name, label_rect)
        fill_result = await self.clipboard.apply_fill(plan, expected_value)
        after = await self.ocr.capture_and_ocr()
        observed = self._observed_value(field_name, after.blocks, expected_value)
        verify_result = self.verifier.verify_text(field_name, expected_value, observed)
        similarity_score = self.similarity.compare_text_blocks(before.blocks, after.blocks)
        ok = fill_result.ok and verify_result.ok and similarity_score >= 0.50
        return WebViewFieldLoopResult(
            ok=ok,
            field_name=field_name,
            page_signature=after.page_signature or before.page_signature,
            fill_message=fill_result.message,
            verify_reason=verify_result.reason,
            screenshot_path=str(after.screenshot_path) if after.screenshot_path else None,
            evidence={
                "coordinate_plan": {
                    "rect": plan.rect.__dict__,
                    "confidence": plan.confidence,
                    "source": plan.source,
                },
                "observed": observed,
                "local_similarity": similarity_score,
            },
        )

    def _observed_value(self, field_name: str, blocks: list[OcrBlock], expected_value: object) -> object:
        """从 OCR blocks 中读取字段值。"""

        # 先找期望值本身，避免字段标签 block 先出现时把空字符串误当作读回值。
        # 找不到期望值时，再用字段名所在 block 做兜底解析。
        # 最终仍找不到就返回空字符串，让 SurfaceVerifier 给出明确失败原因。
        expected = "" if expected_value is None else str(expected_value).strip()
        for block in blocks:
            if expected and expected in block.text:
                return expected
        for block in blocks:
            if field_name in block.text:
                return block.text.replace(field_name, "").strip()
        return ""
