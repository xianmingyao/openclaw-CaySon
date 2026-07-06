"""工作流状态定义。"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from jm_ufo_agent.runtime.evidence import normalize_halt_evidence


class WorkflowStatus(str, Enum):
    """工作流状态枚举。"""

    PENDING = "pending"
    RUNNING = "running"
    SAVED_DRAFT = "saved_draft"
    HALTED = "halted"
    COMMITTED = "committed"


@dataclass
class GraphState:
    """可持久化的工作流状态。"""

    task_id: str
    row_index: int
    product: dict[str, Any]
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_node: str = "BOOTSTRAP"
    evidence: dict[str, Any] = field(default_factory=dict)
    verified_fields: set[str] = field(default_factory=set)
    blockers: list[str] = field(default_factory=list)
    completion_score: float = 0.0
    review_decision: str = ""
    evaluation_loop_count: int = 0

    def add_evidence(self, key: str, value: Any) -> None:
        """追加节点证据。"""

        # evidence 是推进状态的唯一依据之一，节点不能只靠返回值判断成功。
        # key 使用节点或字段名称，避免不同节点之间互相覆盖。
        # value 保持原始结构，Repository 层负责 JSON 序列化和落库。
        self.evidence[key] = value

    def verify_field(self, field_name: str) -> None:
        """标记字段已验证。"""

        # 只有 VerifyStrategy 通过后才应调用该方法。
        # set 天然去重，重复恢复不会重复计数。
        # 字段级断点后续会同步写入 FieldProgressRepository。
        self.verified_fields.add(field_name)

    def restore_verified_fields(self, fields: set[str]) -> None:
        """从持久化进度恢复已验证字段。"""

        # 字段级恢复只能增加 verified 集合，不能清空当前内存状态。
        # Repository 只返回 status=verified 的字段，因此这里不再二次判断状态。
        # 使用 set 合并可以保证崩溃恢复和重复启动结果稳定。
        self.verified_fields.update(fields)

    def halt(self, reason: str, evidence: dict[str, Any] | None = None) -> None:
        """中止工作流并记录可追溯证据。"""

        # halt 不是普通异常，它代表当前 row 已经不能继续自动推进。
        # blockers 用于路由判断，halt_evidence 用于人工复盘和恢复定位。
        # evidence 参数保持可选，兼容旧节点里只传 reason 的调用方式。
        self.blockers.append(reason)
        self.status = WorkflowStatus.HALTED
        self.record_halt_evidence(reason, evidence or {})

    def record_halt_evidence(self, reason: str, evidence: dict[str, Any]) -> None:
        """把中止原因、节点和现场证据写入 state.evidence。"""

        # halt 证据使用列表保存，避免多次失败时互相覆盖。
        # current_node 是最关键的定位字段，能直接映射到 workflow/nodes 下的节点。
        # 真实 GUI 接入后，screenshot_path、ocr_summary、page_signature 等都放在 details 中。
        halt_items = list(self.evidence.get("halt_evidence") or [])
        if _is_normalized_halt_evidence(evidence):
            halt_items.append(evidence)
        else:
            halt_items.append(normalize_halt_evidence(self.current_node, reason, evidence))
        self.evidence["halt_evidence"] = halt_items

    def to_dict(self) -> dict[str, Any]:
        """转换为可 JSON 序列化的字典。"""

        # Enum 转 value，避免 JSON 序列化失败。
        # verified_fields 转排序列表，保证 checkpoint 稳定。
        # product/evidence 保持原结构，便于恢复。
        return {
            "task_id": self.task_id,
            "row_index": self.row_index,
            "product": self.product,
            "status": self.status.value,
            "current_node": self.current_node,
            "evidence": self.evidence,
            "verified_fields": sorted(self.verified_fields),
            "blockers": self.blockers,
            "completion_score": self.completion_score,
            "review_decision": self.review_decision,
            "evaluation_loop_count": self.evaluation_loop_count,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GraphState":
        """从 checkpoint 字典恢复 `GraphState`。"""

        # checkpoint 中的 status 可能是字符串，也可能已经是 Enum。
        # verified_fields 在 JSON 中保存为列表，恢复时转回 set 便于去重。
        # 缺失字段全部使用当前 dataclass 默认值，兼容旧版本 checkpoint。
        return cls(
            task_id=payload["task_id"],
            row_index=int(payload["row_index"]),
            product=dict(payload.get("product") or {}),
            status=WorkflowStatus(payload.get("status", WorkflowStatus.PENDING.value)),
            current_node=str(payload.get("current_node", "BOOTSTRAP")),
            evidence=dict(payload.get("evidence") or {}),
            verified_fields=set(payload.get("verified_fields") or []),
            blockers=list(payload.get("blockers") or []),
            completion_score=float(payload.get("completion_score", 0.0)),
            review_decision=str(payload.get("review_decision", "")),
            evaluation_loop_count=int(payload.get("evaluation_loop_count", 0)),
        )


def _is_normalized_halt_evidence(evidence: dict[str, Any]) -> bool:
    """判断 halt evidence 是否已经是标准结构。"""

    # HaltEvidenceCollector 会生成 node/reason/created_at/log_path 等标准字段。
    # 如果再次 normalize，会把标准字段塞进 details，造成证据重复嵌套。
    # 旧节点传入的普通 details 不含 created_at，仍按原逻辑标准化。
    return {"node", "reason", "created_at"}.issubset(evidence)
