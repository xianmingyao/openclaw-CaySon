from __future__ import annotations

import json
from datetime import datetime, timedelta

from jingmai_publish.services.channel_ingress import FeishuPathChannelService, LocalPathChannelService
from jingmai_publish.services.retention_service import RuntimeRetentionService


def test_local_path_channel_service_reads_excel_path(tmp_path):
    message_file = tmp_path / "message.txt"
    message_file.write_text('"E:\\demo\\products.xlsx"\nsecond line', encoding="utf-8")

    result = LocalPathChannelService.read_excel_path_from_message(message_file)

    assert result == r"E:\demo\products.xlsx"


def test_runtime_retention_service_cleanup_removes_old_files(tmp_path):
    expired_detail = tmp_path / "expired-detail.txt"
    expired_detail.write_text("x", encoding="utf-8")

    old_screenshot_dir = tmp_path / "screenshots"
    old_screenshot_dir.mkdir()
    old_screenshot = old_screenshot_dir / "old.png"
    old_screenshot.write_text("img", encoding="utf-8")
    very_old = datetime.now() - timedelta(days=5)
    timestamp = very_old.timestamp()
    old_screenshot.touch()
    import os
    os.utime(old_screenshot, (timestamp, timestamp))

    class FakeQuery:
        def __init__(self, rows):
            self.rows = rows

        def filter(self, *args, **kwargs):
            return self

        def order_by(self, *args, **kwargs):
            return self

        def all(self):
            return self.rows

    class FakeSession:
        def __init__(self):
            self.deleted = False
            self.committed = False

        def query(self, model):
            row = type("RuntimeLogRow", (), {"detail_path": str(expired_detail)})()
            return FakeQuery([row])

        def commit(self):
            self.committed = True

    fake_session = FakeSession()
    service = RuntimeRetentionService(fake_session, old_screenshot_dir)
    service.runtime_log_repo = type(
        "FakeRepo",
        (),
        {"delete_expired_logs": staticmethod(lambda current_time: 1)},
    )()

    result = service.cleanup(now=datetime.now())

    assert result["deleted_log_count"] == 1
    assert str(expired_detail) in result["deleted_detail_paths"]
    assert str(old_screenshot) in result["deleted_orphan_screenshots"]
    assert fake_session.committed is True


def test_feishu_path_channel_service_parses_payload(tmp_path):
    payload_file = tmp_path / "feishu.json"
    payload = {
        "header": {"event_id": "evt-1"},
        "event": {
            "message": {
                "message_id": "om_123",
                "chat_id": "oc_456",
                "content": json.dumps({"text": '"E:\\demo\\products.xlsx"'}),
            },
            "sender": {"sender_id": {"open_id": "ou_789"}},
        },
    }
    payload_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    parsed = FeishuPathChannelService.parse_feishu_payload(payload_file)

    assert parsed.message_id == "om_123"
    assert parsed.chat_id == "oc_456"
    assert parsed.sender_id == "ou_789"
    assert parsed.excel_path == r"E:\demo\products.xlsx"
