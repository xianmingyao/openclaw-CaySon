"""WebSurface 验证服务。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SurfaceVerificationResult:
    """WebSurface 局部验证结果。"""

    ok: bool
    field_name: str
    reason: str


class SurfaceVerifier:
    """基于读回值或 OCR 文本验证字段。"""

    def verify_text(self, field_name: str, expected: object, observed: object) -> SurfaceVerificationResult:
        """验证文本是否匹配。"""

        # 两边都转字符串并去空白，适配 OCR/读回的轻微格式差异。
        # expected 为空时仍然失败，避免必填字段误通过。
        # 该方法是纯函数，后续可直接用于真实 backend。
        expected_text = "" if expected is None else str(expected).strip()
        observed_text = "" if observed is None else str(observed).strip()
        if not expected_text:
            return SurfaceVerificationResult(ok=False, field_name=field_name, reason="期望值为空")
        if expected_text != observed_text:
            return SurfaceVerificationResult(ok=False, field_name=field_name, reason="读回值不匹配")
        return SurfaceVerificationResult(ok=True, field_name=field_name, reason="读回值匹配")
