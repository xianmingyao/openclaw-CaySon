"""运行时证据标准化工具。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class HaltEvidenceSnapshot:
    """异常中止现场证据快照。"""

    node: str
    reason: str
    screenshot_path: str | None = None
    log_path: str | None = None
    ocr_summary: dict[str, Any] = field(default_factory=dict)
    page_signature: str | None = None
    window_summary: dict[str, Any] = field(default_factory=dict)
    details: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """转换为可落库的 JSON 字典。"""

        # halt 证据要能直接写入 GraphState、MySQL 和日志文件。
        # 空字段保留为 None/{}，便于人工判断“没有采集”而不是“采集成功为空”。
        # created_at 使用 UTC ISO 字符串，避免跨机器时区混乱。
        return {
            "node": self.node,
            "reason": self.reason,
            "screenshot_path": self.screenshot_path,
            "log_path": self.log_path,
            "ocr_summary": dict(self.ocr_summary),
            "page_signature": self.page_signature,
            "window_summary": dict(self.window_summary),
            "details": dict(self.details),
            "created_at": self.created_at,
        }


@dataclass(frozen=True)
class DraftVerificationSnapshot:
    """保存草稿后的验证证据快照。"""

    ok: bool
    reason: str
    draft_id: str | None = None
    draft_url: str | None = None
    toast_text: str | None = None
    list_page_hit: bool = False
    readback: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为草稿验证证据字典。"""

        # F07 不能只看按钮点击返回成功，必须有草稿 ID、跳转、toast 或读回证据。
        # dry-run 可以把 ok=True 作为本地占位，但真实 backend 需要补充 draft_id/toast/list_page_hit。
        # readback 保存列表页或详情页读回字段，用于后续 diff。
        return {
            "ok": self.ok,
            "reason": self.reason,
            "draft_id": self.draft_id,
            "draft_url": self.draft_url,
            "toast_text": self.toast_text,
            "list_page_hit": self.list_page_hit,
            "readback": dict(self.readback),
        }


def normalize_halt_evidence(node: str, reason: str, evidence: dict[str, Any]) -> dict[str, Any]:
    """把任意 halt details 规范化为统一现场证据。"""

    # 上游节点可能传入截图路径、OCR 摘要、页面签名或窗口摘要。
    # 这里统一字段名，避免不同节点各写各的 JSON 结构。
    # details 保留完整原始 evidence，兼容旧测试和旧日志消费者。
    details = dict(evidence)
    snapshot = HaltEvidenceSnapshot(
        node=node,
        reason=reason,
        screenshot_path=evidence.get("screenshot_path"),
        log_path=evidence.get("log_path"),
        ocr_summary=dict(evidence.get("ocr_summary") or {}),
        page_signature=evidence.get("page_signature"),
        window_summary=dict(evidence.get("window_summary") or {}),
        details=details,
    )
    return snapshot.to_dict()


def draft_verification_from_save_evidence(save_evidence: dict[str, Any] | None) -> DraftVerificationSnapshot:
    """根据保存动作证据生成草稿验证快照。"""

    # 真实保存草稿至少应提供 draft_id、toast_text、draft_url 或 list_page_hit 之一。
    # 兼容当前 dry-run：只有 ok=True 时仍返回通过，但 reason 明确标记为 dry-run evidence。
    # 如果保存动作本身失败或缺失，则验证失败，不允许推进到 saved_draft。
    evidence = dict(save_evidence or {})
    if not evidence.get("ok"):
        return DraftVerificationSnapshot(ok=False, reason="缺少成功的保存草稿动作证据")
    has_real_proof = bool(evidence.get("draft_id") or evidence.get("draft_url") or evidence.get("toast_text") or evidence.get("list_page_hit"))
    return DraftVerificationSnapshot(
        ok=True,
        reason="草稿保存证据通过" if has_real_proof else "dry-run 保存草稿证据通过",
        draft_id=evidence.get("draft_id"),
        draft_url=evidence.get("draft_url"),
        toast_text=evidence.get("toast_text"),
        list_page_hit=bool(evidence.get("list_page_hit", False)),
        readback=dict(evidence.get("readback") or {}),
    )
