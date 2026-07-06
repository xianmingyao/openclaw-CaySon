"""字段验证策略。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jm_ufo_agent.strategies.plan import FieldPlan


@dataclass(frozen=True)
class VerificationResult:
    """字段验证结果。"""

    ok: bool
    field_name: str
    reason: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)


class VerifyStrategy:
    """基于证据验证字段是否完成。"""

    def verify_field(self, plan: FieldPlan, readback: Any | None = None, evidence: dict | None = None) -> VerificationResult:
        """验证单字段结果。

        # readback 优先使用真实读回值。
        # dry-run 没有读回值时，使用计划值作为可验证占位。
        # required 字段为空时必须失败，不能把动作成功当作字段成功。
        """

        observed = plan.value if readback is None else readback
        if plan.required and observed in (None, ""):
            return VerificationResult(ok=False, field_name=plan.field_name, reason="必填字段为空", evidence=evidence or {})
        return VerificationResult(ok=True, field_name=plan.field_name, reason="字段证据通过", evidence=evidence or {})

    def verify_draft_saved(self, evidence: dict | None = None) -> VerificationResult:
        """验证草稿保存结果。"""

        # Phase 2 dry-run 只验证是否存在保存动作证据。
        # 真实实现应检查列表页跳转、草稿 ID 或页面提示。
        # 没有证据时返回失败，保持“无证据不推进”的原则。
        data = evidence or {}
        if not data:
            return VerificationResult(ok=False, field_name="draft", reason="缺少草稿保存证据", evidence={})
        return VerificationResult(ok=True, field_name="draft", reason="草稿保存证据通过", evidence=data)
