import json

from jm_ufo_agent.cli.command import main
from jm_ufo_agent.cli.command import _load_product_json
from jm_ufo_agent.runtime.app import run_dryrun
from jm_ufo_agent.workflow.state import WorkflowStatus


def _complete_product():
    return {
        "title": "测试商品",
        "category": "工业品",
        "brand": "测试品牌",
        "sku": "sku-1",
        "jd_price": "100.00",
        "purchase_price": "95.00",
        "market_price": "117.65",
        "main_image": "main.png",
        "sub_images": ["sub-1.png"],
        "description": "测试描述",
        "weight": "1kg",
        "stock": "10",
    }


async def test_dryrun_workflow_saves_draft_for_complete_product():
    state = await run_dryrun(task_id="task-1", row_index=82, product=_complete_product())

    assert state.status == WorkflowStatus.SAVED_DRAFT
    assert state.review_decision == "save_draft"
    assert state.completion_score == 1.0
    assert "save_draft" in state.evidence
    assert "verify_draft" in state.evidence


async def test_dryrun_workflow_halts_for_missing_required_field():
    product = _complete_product()
    product["title"] = ""

    state = await run_dryrun(task_id="task-1", row_index=82, product=product)

    assert state.status == WorkflowStatus.HALTED
    assert any("title" in blocker for blocker in state.blockers)
    assert "save_draft" not in state.evidence


def test_cli_dryrun_outputs_state_json(capsys):
    code = main(
        [
            "dry-run",
            "--task-id",
            "task-1",
            "--row-index",
            "82",
            "--product-json",
            json.dumps(_complete_product(), ensure_ascii=False),
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 0
    assert payload["status"] == "saved_draft"
    assert payload["row_index"] == 82


def test_cli_run_command_defaults_to_safe_dryrun(capsys):
    code = main(
        [
            "run",
            "--task-id",
            "task-1",
            "--product-json",
            json.dumps(_complete_product(), ensure_ascii=False),
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 0
    assert payload["status"] == "saved_draft"
    assert payload["row_index"] == 82


def test_cli_loads_product_json_from_file(tmp_path):
    path = tmp_path / "product.json"
    path.write_text(json.dumps(_complete_product(), ensure_ascii=False), encoding="utf-8")

    product = _load_product_json(f"@{path}")

    assert product["title"] == "测试商品"


def test_cli_loads_product_json_from_windows_utf8_bom_file(tmp_path):
    path = tmp_path / "product.json"
    path.write_text("\ufeff" + json.dumps(_complete_product(), ensure_ascii=False), encoding="utf-8")

    product = _load_product_json(f"@{path}")

    assert product["brand"] == "测试品牌"
