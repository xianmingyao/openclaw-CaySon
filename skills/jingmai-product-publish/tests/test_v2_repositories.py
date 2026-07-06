from jm_ufo_agent.storage.repositories.field_progress import FieldProgressRepository
from jm_ufo_agent.storage.repositories.assets import ProductAssetRepository
from jm_ufo_agent.storage.repositories.draft_verifications import DraftVerificationRepository
from jm_ufo_agent.storage.repositories.locator_cache import LocatorCacheRepository
from jm_ufo_agent.storage.repositories.models import (
    ArtifactRecord,
    DraftVerificationRecord,
    FieldProgressRecord,
    LocatorCacheRecord,
    ProductAssetRecord,
    ProductRecord,
    RowExecutionRecord,
    StepLogRecord,
    TaskRecord,
    VlmCallRecord,
)
from jm_ufo_agent.storage.repositories.products import ProductRepository
from jm_ufo_agent.storage.repositories.artifacts import ArtifactRepository
from jm_ufo_agent.storage.repositories.rows import RowExecutionRepository
from jm_ufo_agent.storage.repositories.step_logs import StepLogRepository
from jm_ufo_agent.storage.repositories.tasks import TaskRepository
from jm_ufo_agent.storage.repositories.vlm_calls import VlmCallRepository


class FakeConnection:
    def __init__(self):
        self.executed = []
        self.next_row = None

    async def execute(self, sql, params):
        self.executed.append((sql, params))
        return 1

    async def fetchone(self, sql, params):
        self.executed.append((sql, params))
        return self.next_row

    async def fetchall(self, sql, params):
        self.executed.append((sql, params))
        return self.next_row or []


async def test_task_repository_upsert_and_get_dict_row():
    connection = FakeConnection()
    repo = TaskRepository(connection)

    await repo.upsert(TaskRecord(task_id="task-1", status="running", current_row=82, state={"node": "SELECT_ROW"}))

    sql, params = connection.executed[-1]
    assert "INSERT INTO jm_tasks" in sql
    assert params[0] == "task-1"
    assert '"node": "SELECT_ROW"' in params[-1]

    connection.next_row = {
        "task_id": "task-1",
        "status": "running",
        "current_row": 82,
        "workflow_version": "v2.0.0",
        "state_json": '{"node": "SELECT_ROW"}',
    }

    record = await repo.get("task-1")

    assert record is not None
    assert record.current_row == 82
    assert record.state == {"node": "SELECT_ROW"}


async def test_product_repository_upsert_and_get_tuple_row():
    connection = FakeConnection()
    repo = ProductRepository(connection)

    await repo.upsert(ProductRecord(product_id="sku-1", row_index=5, title="测试商品", raw_data={"a": 1}))

    sql, params = connection.executed[-1]
    assert "INSERT INTO jm_products" in sql
    assert params[:3] == ("sku-1", 5, "测试商品")

    connection.next_row = ("sku-1", 5, "测试商品", '{"a": 1}', '{"price": 100}')

    record = await repo.get_by_row(5)

    assert record is not None
    assert record.raw_data == {"a": 1}
    assert record.enriched_data == {"price": 100}


async def test_field_progress_repository_mark_and_get():
    connection = FakeConnection()
    repo = FieldProgressRepository(connection)

    await repo.mark(FieldProgressRecord(task_id="task-1", row_index=82, field_name="title", status="verified", evidence={"ocr": "ok"}))

    sql, params = connection.executed[-1]
    assert "INSERT INTO jm_field_progress" in sql
    assert params[:4] == ("task-1", 82, "title", "verified")

    connection.next_row = {
        "task_id": "task-1",
        "row_index": 82,
        "field_name": "title",
        "status": "verified",
        "evidence_json": '{"ocr": "ok"}',
        "updated_at": None,
    }

    record = await repo.get("task-1", 82, "title")

    assert record is not None
    assert record.evidence == {"ocr": "ok"}


async def test_row_execution_repository_upsert_get_and_row82_rule():
    connection = FakeConnection()
    repo = RowExecutionRepository(connection)

    await repo.upsert(
        RowExecutionRecord(
            task_id="task-1",
            row_index=82,
            status="committed",
            completion_score=1.0,
            completion_passed=True,
            draft_evidence={"draft_id": "d-1"},
        )
    )

    sql, params = connection.executed[-1]
    assert "INSERT INTO jm_row_execution_states" in sql
    assert params[:3] == ("task-1", 82, "committed")

    connection.next_row = {
        "task_id": "task-1",
        "row_index": 5,
        "status": "committed",
        "completion_details_json": "{}",
        "review_details_json": "{}",
        "draft_evidence_json": '{"draft_id": "d-5"}',
    }

    record = await repo.get("task-1", 5)

    assert record is not None
    assert record.draft_evidence == {"draft_id": "d-5"}


async def test_row_execution_repository_lists_committed_rows():
    connection = FakeConnection()
    repo = RowExecutionRepository(connection)
    connection.next_row = [{"row_index": 5}, (6,)]

    rows = await repo.list_committed_rows("task-1")

    assert rows == {5, 6}


async def test_artifact_repository_adds_record():
    connection = FakeConnection()
    repo = ArtifactRepository(connection)

    await repo.add(ArtifactRecord(task_id="task-1", row_index=82, artifact_type="screenshot", storage_path="artifacts/a.png", metadata={"ok": True}))

    sql, params = connection.executed[-1]
    assert "INSERT INTO jm_artifacts" in sql
    assert params[:4] == ("task-1", 82, "screenshot", "artifacts/a.png")


async def test_product_asset_repository_upsert_and_list():
    connection = FakeConnection()
    repo = ProductAssetRepository(connection)

    await repo.upsert(
        ProductAssetRecord(
            product_id="sku-1",
            task_id="task-1",
            row_index=82,
            asset_type="main_image",
            remote_url="https://img.example/a.jpg",
            transform_status="done",
            metadata={"sha256": "abc"},
        )
    )

    sql, params = connection.executed[-1]
    assert "INSERT INTO jm_product_assets" in sql
    assert params[:4] == ("sku-1", "task-1", 82, "main_image")

    connection.next_row = [
        {
            "product_id": "sku-1",
            "task_id": "task-1",
            "row_index": 82,
            "asset_type": "main_image",
            "local_path": "tmp/a.jpg",
            "remote_url": "https://img.example/a.jpg",
            "transform_status": "done",
            "transformed_path": "tmp/a-out.jpg",
            "metadata_json": '{"sha256": "abc"}',
        }
    ]

    records = await repo.list_by_product("sku-1")

    assert records[0].metadata == {"sha256": "abc"}
    assert records[0].transform_status == "done"


async def test_step_log_repository_adds_record():
    connection = FakeConnection()
    repo = StepLogRepository(connection)

    await repo.add(StepLogRecord(task_id="task-1", row_index=82, node_name="SAVE_DRAFT", status="ok", metadata={"draft": True}))

    sql, params = connection.executed[-1]
    assert "INSERT INTO jm_step_logs" in sql
    assert params[:4] == ("task-1", 82, "SAVE_DRAFT", "ok")


async def test_locator_cache_repository_upsert_and_get():
    connection = FakeConnection()
    repo = LocatorCacheRepository(connection)

    await repo.upsert(LocatorCacheRecord(field_key="title", page_signature="sig-1", selector_type="ocr_rect", selector_value="1,2,3,4", confidence=0.91))

    sql, params = connection.executed[-1]
    assert "INSERT INTO jm_locator_cache" in sql
    assert params[:4] == ("title", "sig-1", "ocr_rect", "1,2,3,4")

    connection.next_row = ("title", "sig-1", "ocr_rect", "1,2,3,4", 0.91, 2)
    record = await repo.get("title", "sig-1")

    assert record is not None
    assert record.confidence == 0.91
    assert record.hit_count == 2


async def test_draft_verification_repository_adds_and_reads_latest():
    connection = FakeConnection()
    repo = DraftVerificationRepository(connection)

    await repo.add(DraftVerificationRecord(task_id="task-1", row_index=82, verification_result="passed", product_id="sku-1", diff={"ok": True}))

    sql, params = connection.executed[-1]
    assert "INSERT INTO jm_draft_verifications" in sql
    assert params[:3] == ("sku-1", "task-1", 82)

    connection.next_row = {
        "product_id": "sku-1",
        "task_id": "task-1",
        "row_index": 82,
        "draft_url": "jingmai://draft/1",
        "completion_score": 1.0,
        "verification_result": "passed",
        "diff_json": '{"ok": true}',
    }
    record = await repo.latest_for_row("task-1", 82)

    assert record is not None
    assert record.product_id == "sku-1"
    assert record.diff == {"ok": True}


async def test_vlm_call_repository_adds_record():
    connection = FakeConnection()
    repo = VlmCallRepository(connection)

    await repo.add(VlmCallRecord(task_id="task-1", row_index=82, call_type="image_transform", model="qwen3-vl", status="failed", cache_hit=True))

    sql, params = connection.executed[-1]
    assert "INSERT INTO jm_vlm_calls" in sql
    assert params[:4] == ("task-1", 82, "image_transform", "qwen3-vl")
    assert params[8] == 1


def test_mysql_schema_declares_twelve_tables():
    schema = __import__("pathlib").Path("jm_ufo_agent/storage/schema/mysql.sql").read_text(encoding="utf-8")

    assert schema.count("CREATE TABLE IF NOT EXISTS") == 12
    assert "jm_row_execution_states" in schema
    assert "jm_graph_pending_writes" in schema
