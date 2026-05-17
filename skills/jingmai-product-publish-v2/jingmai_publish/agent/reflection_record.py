"""ReflectionRecord: 失败反思结构化记录（BL-094A）。

用于 JSONL 持久化和 Milvus 向量存储的结构化数据类。
从 RuntimeEventLoop 的 REFLECTION_RECORDED 事件 payload 构造。
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class ReflectionRecord:
    """单次反射决策的结构化记录。

    字段与 AgentReflection._emit() 发出的 REFLECTION_RECORDED
    事件 payload 一一对应。可用于 JSONL 持久化和向量检索。
    """

    step_name: str
    category: str
    attempt_no: int
    max_retry: int
    success: bool
    decision: str
    reason: str
    message: str = ""
    lane_count: int = 0
    vision_analysis: dict[str, Any] | None = None
    recorded_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    @classmethod
    def from_event_payload(cls, payload: dict[str, Any]) -> ReflectionRecord:
        """从 RuntimeEventLoop REFLECTION_RECORDED 事件构造。"""
        return cls(
            step_name=payload.get("step_name", ""),
            category=payload.get("category", ""),
            attempt_no=payload.get("attempt_no", 0),
            max_retry=payload.get("max_retry", 0),
            success=payload.get("success", False),
            decision=payload.get("decision", ""),
            reason=payload.get("reason", ""),
            message=payload.get("message", ""),
            lane_count=payload.get("lane_count", 0),
            vision_analysis=payload.get("vision_analysis"),
        )

    def to_dict(self) -> dict[str, Any]:
        """转为可 JSON 序列化的 dict。"""
        return asdict(self)

    @property
    def is_failure(self) -> bool:
        """该记录是否代表一次失败（非 CONTINUE 决策）。"""
        return self.decision != "continue"
