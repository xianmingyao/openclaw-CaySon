import pytest

from jm_ufo_agent.io.excel import ExcelProductParser
from jm_ufo_agent.storage.checkpointer import AsyncMySQLSaver
from jm_ufo_agent.storage.repositories.field_progress import FieldProgressRepository
from jm_ufo_agent.storage.repositories.models import RowExecutionRecord
from jm_ufo_agent.workflow.graph import DryRunWorkflow
from jm_ufo_agent.workflow.state import GraphState


class FakeFieldConnection:
    async def fetchall(self, sql, params):
        return [{"field_name": "title"}, ("brand",)]


class FakeSaver:
    def __init__(self):
        self.snapshots = []

    async def aput(self, state):
        self.snapshots.append(state.to_dict())


class FakeFieldProgressRepository:
    def __init__(self, verified_fields=None):
        self.verified_fields = set(verified_fields or [])
        self.marked = []

    async def list_verified_fields(self, task_id, row_index):
        return set(self.verified_fields)

    async def mark(self, record):
        self.marked.append(record)


class FakeRowExecutionRepository:
    def __init__(self):
        self.records = []
        self.draft_rows = set()

    async def next_row_after_seed(self, task_id, requested_row):
        return 82 if requested_row in {5, 6, 7} and self.draft_rows == {5, 6, 7} else requested_row

    async def upsert(self, record):
        self.records.append(record)


class FakeTaskRepository:
    def __init__(self):
        self.record = None

    async def upsert(self, record):
        self.record = record

    async def get(self, task_id):
        return self.record if self.record and self.record.task_id == task_id else None


def test_excel_product_parser_internal_row_mapping():
    parser = ExcelProductParser()
    raw = {"商品ID": 123, "商品标题": "测试商品"}

    record = parser._to_product_record(5, raw)

    assert record.product_id == "123"
    assert record.row_index == 5
    assert record.title == "测试商品"
    assert record.raw_data == raw


def test_excel_product_parser_real_xlsx_when_openpyxl_available(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    path = tmp_path / "products.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["商品ID", "商品标题"])
    sheet.append(["sku-1", "测试商品"])
    workbook.save(path)

    records = ExcelProductParser().parse(path)

    assert records[0].product_id == "sku-1"
    assert records[0].title == "测试商品"


async def test_field_progress_repository_lists_verified_fields():
    repo = FieldProgressRepository(FakeFieldConnection())

    fields = await repo.list_verified_fields("task-1", 82)

    assert fields == {"title", "brand"}


async def test_async_mysql_saver_get_returns_snapshot():
    repo = FakeTaskRepository()
    saver = AsyncMySQLSaver(repo)
    state = GraphState(task_id="task-1", row_index=82, product={"title": "测试"})

    await saver.aput(state)
    snapshot = await saver.aget("task-1")

    assert snapshot is not None
    assert snapshot["task_id"] == "task-1"


async def test_dryrun_workflow_calls_saver_after_nodes():
    saver = FakeSaver()
    workflow = DryRunWorkflow(saver=saver)
    state = GraphState(
        task_id="task-1",
        row_index=82,
        product={
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
        },
    )

    result = await workflow.run(state)

    assert result.status.value == "saved_draft"
    assert len(saver.snapshots) >= 8
    assert saver.snapshots[-1]["status"] == "saved_draft"


async def test_dryrun_workflow_recovers_verified_fields_and_marks_new_fields():
    field_repo = FakeFieldProgressRepository(verified_fields={"title", "category"})
    workflow = DryRunWorkflow(field_progress=field_repo)
    state = GraphState(
        task_id="task-1",
        row_index=82,
        product={
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
        },
    )

    result = await workflow.run(state)

    assert result.status.value == "saved_draft"
    assert result.evidence["recover_fields"]["verified_fields"] == ["category", "title"]
    assert {record.field_name for record in field_repo.marked}.isdisjoint({"title", "category"})
    assert len(field_repo.marked) == 10


async def test_dryrun_workflow_applies_row82_seed_rule_and_commits_row():
    row_repo = FakeRowExecutionRepository()
    row_repo.draft_rows = {5, 6, 7}
    workflow = DryRunWorkflow(row_progress=row_repo)
    state = GraphState(
        task_id="task-1",
        row_index=5,
        product={
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
        },
    )

    result = await workflow.run(state)

    assert result.row_index == 82
    assert result.evidence["select_row"] == {"requested_row": 5, "selected_row": 82}
    assert any(isinstance(record, RowExecutionRecord) and record.status == "committed" for record in row_repo.records)
