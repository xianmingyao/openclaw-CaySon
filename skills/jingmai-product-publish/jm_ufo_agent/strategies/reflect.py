"""失败反思策略。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FailureReflection:
    """失败反思结果。"""

    category: str
    retryable: bool
    evidence: dict[str, Any] = field(default_factory=dict)
    message: str = ""


class FailureReflectionStrategy:
    """把异常和失败证据分类。"""

    def reflect(self, error: BaseException | str, evidence: dict[str, Any] | None = None) -> FailureReflection:
        """生成失败反思结果。

        # SafetyViolation 和包含“安全”的错误不可重试。
        # 其他错误先按 retryable 处理，交给 RetryPolicy 限制次数。
        # evidence 原样带回，便于 HALT 节点落库和人工排查。
        """

        message = str(error)
        if "SafetyViolation" in message or "安全" in message or "禁止" in message:
            return FailureReflection(category="safety", retryable=False, evidence=evidence or {}, message=message)
        return FailureReflection(category="transient", retryable=True, evidence=evidence or {}, message=message)
