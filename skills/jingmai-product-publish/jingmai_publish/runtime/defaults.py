"""Default runtime providers used by the host runtime."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from jingmai_publish.repositories.runtime_log import RuntimeLogRepository
from pathlib import Path
from typing import Any


class RuntimeLogPersistenceProvider:
    """Persist runtime events into runtime logs."""

    def __init__(
            self,
            runtime_log_repo: RuntimeLogRepository | None,
            *,
            session_id: str = "runtime-host",
    ) -> None:
        self.runtime_log_repo = runtime_log_repo
        self.session_id = session_id

    def persist_event(self, event_type: str, payload: dict[str, Any]) -> None:
        if self.runtime_log_repo is None:
            return
        compact_payload = json.dumps(payload, ensure_ascii=False, default=str)
        self.runtime_log_repo.append_log(
            session_id=self.session_id,
            log_type="runtime",
            step_id=event_type,
            message=f"{event_type}: {compact_payload[:900]}",
        )


class JsonlMemoryProvider:
    """Store short-term episodic memory in a local JSONL file."""

    def __init__(self, target_file: str | Path) -> None:
        self.target_file = Path(target_file)
        self.target_file.parent.mkdir(parents=True, exist_ok=True)

    def remember(self, memory_type: str, payload: dict[str, Any]) -> None:
        record = {
            "memory_type": memory_type,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "payload": self._normalize(payload),
        }
        with self.target_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        if not self.target_file.exists():
            return []

        matched: list[dict[str, Any]] = []
        lowered = query.lower()
        lines = self.target_file.read_text(encoding="utf-8").splitlines()
        for raw_line in reversed(lines):
            if not raw_line.strip():
                continue
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            haystack = json.dumps(record, ensure_ascii=False).lower()
            if lowered in haystack:
                matched.append(record)
            if len(matched) >= limit:
                break
        return matched

    @staticmethod
    def _normalize(payload: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for key, value in payload.items():
            if is_dataclass(value):
                normalized[key] = asdict(value)
            elif isinstance(value, Path):
                normalized[key] = str(value)
            else:
                normalized[key] = value
        return normalized


class LocalPathChannelProvider:
    """Normalize local-path ingress payload."""

    def normalize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        path_file = payload.get("path_file")
        excel_path = payload.get("excel_path")
        return {
            **payload,
            "source_channel": payload.get("source_channel", "local_path_message"),
            "path_file": str(path_file) if path_file is not None else None,
            "excel_path": str(excel_path) if excel_path is not None else None,
        }


class FeishuChannelProvider:
    """Normalize a Feishu/Lark event payload into the host contract."""

    def normalize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(payload)
        normalized["source_channel"] = payload.get("source_channel", "feishu")
        normalized["feishu_message_id"] = (
                payload.get("message_id")
                or payload.get("event", {}).get("message", {}).get("message_id")
                or payload.get("header", {}).get("event_id")
        )
        return normalized
