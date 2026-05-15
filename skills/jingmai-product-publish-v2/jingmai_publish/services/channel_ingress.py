"""Channel/local-path task ingress service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from sqlalchemy.orm import Session

from jingmai_publish.repositories.runtime_log import RuntimeLogRepository
from jingmai_publish.services.import_pipeline import ImportPipelineService


@dataclass(slots=True)
class FeishuPathMessage:
    """Normalized Feishu local-path message."""

    message_id: str | None
    chat_id: str | None
    sender_id: str | None
    excel_path: str
    raw_payload: dict[str, object]


class LocalPathChannelService:
    """Normalize local-path messages and execute the import pipeline."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.runtime_log_repo = RuntimeLogRepository(session)
        self.import_pipeline = ImportPipelineService(session)

    @staticmethod
    def read_excel_path_from_message(path_file: str | Path) -> str:
        """Read the Excel path string from a local message file."""

        raw_text = Path(path_file).read_text(encoding="utf-8").strip()
        if not raw_text:
            raise ValueError("path message file is empty")
        return raw_text.splitlines()[0].strip().strip('"')

    def run_from_local_message(
        self,
        path_file: str | Path,
        *,
        mode: str = "draft",
        store_id: str | None = None,
        source_channel: str = "local_path_message",
    ) -> dict[str, object]:
        """Run the full import flow from a local message file."""

        excel_path = self.read_excel_path_from_message(path_file)
        result = self.import_pipeline.run_from_local_excel_path(excel_path, mode=mode, store_id=store_id)
        self.runtime_log_repo.append_log(
            session_id=result["session_id"],
            job_id=result["job_id"],
            log_type="process",
            message=f"accepted {source_channel} task: {path_file} -> {excel_path}",
        )
        self.session.commit()
        return {
            "source_channel": source_channel,
            "path_file": str(path_file),
            "excel_path": excel_path,
            **result,
        }


class FeishuPathChannelService(LocalPathChannelService):
    """Parse Feishu payloads and run the same import pipeline contract."""

    @staticmethod
    def _extract_text_block(payload: dict[str, object]) -> str:
        candidates = [
            payload.get("excel_path"),
            payload.get("local_path"),
            payload.get("text"),
        ]
        event = payload.get("event", {})
        if isinstance(event, dict):
            message = event.get("message", {})
            if isinstance(message, dict):
                candidates.extend(
                    [
                        message.get("content"),
                        message.get("text"),
                    ]
                )
        content = payload.get("content")
        if isinstance(content, dict):
            candidates.extend([content.get("text"), content.get("content")])
        else:
            candidates.append(content)

        for candidate in candidates:
            if candidate is None:
                continue
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
        raise ValueError("feishu payload does not contain a usable text block")

    @classmethod
    def parse_feishu_payload(cls, payload_file: str | Path) -> FeishuPathMessage:
        payload = json.loads(Path(payload_file).read_text(encoding="utf-8"))
        raw_text = cls._extract_text_block(payload)
        if raw_text.startswith("{"):
            try:
                nested = json.loads(raw_text)
            except json.JSONDecodeError:
                nested = None
            if isinstance(nested, dict):
                raw_text = str(nested.get("text") or nested.get("excel_path") or nested.get("local_path") or "").strip()
        excel_path = raw_text.splitlines()[0].strip().strip('"')
        event = payload.get("event", {}) if isinstance(payload.get("event"), dict) else {}
        message = event.get("message", {}) if isinstance(event.get("message"), dict) else {}
        sender = event.get("sender", {}) if isinstance(event.get("sender"), dict) else {}
        sender_id = None
        sender_sender_id = sender.get("sender_id") if isinstance(sender.get("sender_id"), dict) else {}
        if isinstance(sender_sender_id, dict):
            sender_id = sender_sender_id.get("open_id") or sender_sender_id.get("user_id") or sender_sender_id.get("union_id")
        return FeishuPathMessage(
            message_id=message.get("message_id") if isinstance(message, dict) else None,
            chat_id=message.get("chat_id") if isinstance(message, dict) else None,
            sender_id=sender_id,
            excel_path=excel_path,
            raw_payload=payload,
        )

    def run_from_feishu_payload(
        self,
        payload_file: str | Path,
        *,
        mode: str = "draft",
        store_id: str | None = None,
    ) -> dict[str, object]:
        normalized = self.parse_feishu_payload(payload_file)
        result = self.import_pipeline.run_from_local_excel_path(normalized.excel_path, mode=mode, store_id=store_id)
        self.runtime_log_repo.append_log(
            session_id=result["session_id"],
            job_id=result["job_id"],
            log_type="process",
            message=f"accepted feishu task: {payload_file} -> {normalized.excel_path}",
        )
        self.session.commit()
        return {
            "source_channel": "feishu",
            "payload_file": str(payload_file),
            "feishu_message_id": normalized.message_id,
            "feishu_chat_id": normalized.chat_id,
            "feishu_sender_id": normalized.sender_id,
            "excel_path": normalized.excel_path,
            **result,
        }
