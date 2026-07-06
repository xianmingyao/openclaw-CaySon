"""安全审计 — 记录和追溯所有 SafetyPolicy 决策。

为每次安全策略校验（通过或拒绝）生成审计记录，
支持按时间范围、任务 ID、决策结果等维度查询。
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jm_ufo_agent.commands.base import Command

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AuditRecord:
    """单次安全审计记录。

    # 记录 SafetyPolicy.assert_allowed 的每次调用结果。
    # timestamp 是 Unix 时间戳，便于时间范围查询。
    # decision 为 "allowed" 或 "blocked"。
    # command_snapshot 保存被校验命令的完整快照。
    # reason 在 blocked 时记录阻断原因。
    """

    timestamp: float
    task_id: str
    decision: str  # "allowed" | "blocked"
    action: str
    target: str
    reason: str = ""
    command_snapshot: dict[str, Any] = field(default_factory=dict)


class SafetyAuditLog:
    """安全审计日志 — 收集、持久化和查询审计记录。

    # 所有 SafetyPolicy 决策都应记录到审计日志。
    # 内存缓存 + 可选文件持久化，避免影响主流程性能。
    # 支持按时间、任务、决策类型过滤查询。
    # 审计记录不可篡改（frozen dataclass），保证追溯可靠性。
    """

    def __init__(self, persist_dir: Path | None = None, max_records: int = 10000):
        """初始化审计日志。"""
        self._records: list[AuditRecord] = []
        self._persist_dir = persist_dir
        self._max_records = max_records

    def record_allowed(self, command: Command, task_id: str = "") -> None:
        """记录通过校验的命令。"""
        record = AuditRecord(
            timestamp=time.time(),
            task_id=task_id,
            decision="allowed",
            action=command.action,
            target=command.target,
            command_snapshot=self._snapshot_command(command),
        )
        self._append(record)

    def record_blocked(self, command: Command, reason: str, task_id: str = "") -> None:
        """记录被阻断的命令。"""
        record = AuditRecord(
            timestamp=time.time(),
            task_id=task_id,
            decision="blocked",
            action=command.action,
            target=command.target,
            reason=reason,
            command_snapshot=self._snapshot_command(command),
        )
        self._append(record)

    def query(
        self,
        task_id: str | None = None,
        decision: str | None = None,
        since: float | None = None,
        until: float | None = None,
        limit: int = 100,
    ) -> list[AuditRecord]:
        """查询审计记录。"""
        results: list[AuditRecord] = []
        for r in reversed(self._records):
            if task_id and r.task_id != task_id:
                continue
            if decision and r.decision != decision:
                continue
            if since and r.timestamp < since:
                continue
            if until and r.timestamp > until:
                continue
            results.append(r)
            if len(results) >= limit:
                break
        return results

    def count_blocked(self, task_id: str | None = None) -> int:
        """统计被阻断的命令数量。"""
        return sum(
            1 for r in self._records
            if r.decision == "blocked" and (task_id is None or r.task_id == task_id)
        )

    def flush(self) -> None:
        """将内存中的审计记录持久化到文件。"""
        if self._persist_dir is None or not self._records:
            return

        self._persist_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        path = self._persist_dir / f"audit_{ts}.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            for r in self._records:
                data = {
                    "timestamp": r.timestamp,
                    "task_id": r.task_id,
                    "decision": r.decision,
                    "action": r.action,
                    "target": r.target,
                    "reason": r.reason,
                    "command_snapshot": r.command_snapshot,
                }
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        self._records.clear()

    def _append(self, record: AuditRecord) -> None:
        """添加审计记录，超出上限时淘汰最旧的。"""
        self._records.append(record)
        while len(self._records) > self._max_records:
            self._records.pop(0)

    @staticmethod
    def _snapshot_command(command: Command) -> dict[str, Any]:
        """保存命令快照。"""
        return {
            "action": command.action,
            "target": command.target,
            "label": command.label,
            "value_type": type(command.value).__name__ if command.value is not None else "None",
        }
