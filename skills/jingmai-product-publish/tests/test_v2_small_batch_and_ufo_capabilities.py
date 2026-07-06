import json

from jm_ufo_agent.backends.ufo_capabilities import UfoCapabilityScanner
from jm_ufo_agent.cli.command import main
from jm_ufo_agent.runtime.small_batch import ProductionSmallBatchValidator, SmallBatchRowEvidence, validate_small_batch_payload


def _passing_row(row_index: int) -> SmallBatchRowEvidence:
    return SmallBatchRowEvidence(
        row_index=row_index,
        jd={"title": "商品标题", "price": "12.30", "image_urls": ["https://img.example/a.jpg"]},
        assets={"downloaded_count": 2, "transformed_count": 2, "failed": False},
        draft={"ok": True, "draft_id": f"draft-{row_index}", "toast_text": "保存成功"},
        readback={"verification_result": "passed"},
        minimax={"decision": "save_draft", "overall_score": 95},
        artifacts={"screenshot_path": f"row-{row_index}.png"},
    )


def test_small_batch_validator_allows_row82_when_seed_rows_pass():
    validator = ProductionSmallBatchValidator()

    report = validator.validate("task-1", [_passing_row(5), _passing_row(6), _passing_row(7)])

    assert report.allow_target_row is True
    assert report.next_row == 82
    assert [row.ok for row in report.rows] == [True, True, True]


def test_small_batch_validator_blocks_row82_when_evidence_is_missing():
    row5 = _passing_row(5)
    bad_row6 = SmallBatchRowEvidence(
        row_index=6,
        jd={"title": "商品标题", "price": "12.30", "image_urls": ["https://img.example/a.jpg"]},
        assets={"downloaded_count": 1, "transformed_count": 0, "failed": False},
        draft={"ok": True, "draft_id": "draft-6"},
        readback={"verification_result": "failed"},
        minimax={"decision": "revise", "overall_score": 88},
        artifacts={},
    )

    report = ProductionSmallBatchValidator().validate("task-1", [row5, bad_row6])

    assert report.allow_target_row is False
    assert report.next_row is None
    assert report.rows[1].missing == [
        "assets_download_transform",
        "draft_readback_passed",
        "minimax_save_draft_decision",
        "screenshot_or_log_artifact",
    ]
    assert report.rows[2].missing == ["row_evidence_missing"]


def test_validate_small_batch_cli_outputs_row82_decision(capsys, tmp_path):
    payload = {
        "task_id": "task-1",
        "rows": [_passing_row(5).to_dict(), _passing_row(6).to_dict(), _passing_row(7).to_dict()],
    }
    path = tmp_path / "small-batch.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    code = main(["validate-small-batch", "--evidence-json", f"@{path}"])
    output = json.loads(capsys.readouterr().out)

    assert code == 0
    assert output["allow_target_row"] is True
    assert output["next_row"] == 82


def test_ufo_capability_scanner_reports_observe_and_write_readiness(tmp_path):
    root = tmp_path / "ufo"
    ui_control = root / "automator" / "ui_control"
    ui_control.mkdir(parents=True)
    (root / "automator").mkdir(exist_ok=True)
    (root / "automator" / "action_execution.py").write_text("# click action\n", encoding="utf-8")
    (ui_control / "controller.py").write_text("def hotkey(): pass\n# clipboard\n", encoding="utf-8")
    (ui_control / "inspector.py").write_text("# inspector\n", encoding="utf-8")
    (ui_control / "screenshot.py").write_text("# screenshot\n", encoding="utf-8")
    (ui_control / "ui_tree.py").write_text("# ui tree\n", encoding="utf-8")
    (root / "automator" / "path_validator.py").write_text("# native dialog path\n", encoding="utf-8")

    report = UfoCapabilityScanner(root).scan()

    assert report.ready_for_observe() is True
    assert report.ready_for_write() is True
    assert report.capabilities["clipboard"] is True
    assert report.missing_capabilities == []


def test_validate_small_batch_payload_uses_default_seed_rule():
    report = validate_small_batch_payload(
        {
            "task_id": "task-1",
            "rows": [_passing_row(5).to_dict(), _passing_row(6).to_dict(), _passing_row(7).to_dict()],
        }
    )

    assert report.seed_rows == (5, 6, 7)
    assert report.target_row == 82
    assert report.allow_target_row is True
