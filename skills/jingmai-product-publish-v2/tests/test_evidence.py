from __future__ import annotations

import json

from jingmai_publish.services.evidence import ScreenshotEvidenceService


def test_collects_present_and_missing_screenshot_paths(tmp_path):
    memory_dir = tmp_path / "resources" / "memory"
    screenshot_dir = tmp_path / "resources" / "screenshots"
    memory_dir.mkdir(parents=True)
    screenshot_dir.mkdir(parents=True)
    existing = screenshot_dir / "present.png"
    existing.write_bytes(b"png")
    runtime_file = memory_dir / "runtime-memory.jsonl"
    runtime_file.write_text(
        "\n".join(
            [
                json.dumps({"payload": {"after_state": {"screenshot_path": "resources/screenshots/present.png"}}}),
                json.dumps({"payload": {"after_state": {"screenshot_path": "resources\\screenshots\\missing.png"}}}),
                "{not-json",
            ]
        ),
        encoding="utf-8",
    )

    result = ScreenshotEvidenceService(tmp_path).collect()

    assert result["success"] is False
    assert result["artifact_count"] == 2
    assert result["present_count"] == 1
    assert result["missing_count"] == 1
    assert result["artifacts"][0]["path"] == "resources/screenshots/present.png"
    assert result["artifacts"][0]["exists"] is True
    assert result["artifacts"][1]["path"] == "resources/screenshots/missing.png"
    assert result["artifacts"][1]["exists"] is False


def test_collect_success_requires_at_least_one_artifact(tmp_path):
    result = ScreenshotEvidenceService(tmp_path).collect()

    assert result["success"] is False
    assert result["artifact_count"] == 0
