from decimal import Decimal
from pathlib import Path

from jingmai_publish.services import import_pipeline as import_pipeline_module
from jingmai_publish.services.excel_ingest import ExcelIngestService
from jingmai_publish.services.import_pipeline import ImportPipelineService
from jingmai_publish.services.task_ingress import TaskIngressService


class DummyUploadJobRepo:
    def __init__(self):
        self.jobs = []
        self.items = []
        self.status_updates = []

    def create_job(self, **kwargs):
        self.jobs.append(kwargs)
        return kwargs

    def create_job_item(self, **kwargs):
        item_id = len(self.items) + 1
        record = type("JobItem", (), {"id": item_id, **kwargs})
        self.items.append(record)
        return record

    def update_job_status(self, job_id, status, **kwargs):
        self.status_updates.append((job_id, status, kwargs))


class DummyRuntimeLogRepo:
    def __init__(self):
        self.logs = []

    def append_log(self, **kwargs):
        self.logs.append(kwargs)
        return kwargs


def test_task_ingress_create_job_from_local_path():
    upload_repo = DummyUploadJobRepo()
    log_repo = DummyRuntimeLogRepo()
    service = TaskIngressService(upload_repo, log_repo)

    job_id = service.create_job_from_local_path(Path("湖南上架表格.xlsx"), session_id="session-demo")
    assert job_id.startswith("job-")
    assert len(upload_repo.jobs) == 1
    assert len(log_repo.logs) == 1


def test_excel_ingest_parse_real_template():
    service = ExcelIngestService(DummyUploadJobRepo())
    rows = service.parse_rows("湖南上架表格.xlsx")

    assert len(rows) >= 1
    first_row = rows[0]
    assert first_row.product_name
    assert first_row.jd_sale_price == Decimal("70.00")
    assert first_row.purchase_price == Decimal("66.50")
    assert first_row.market_price == Decimal("82.35")


def test_excel_ingest_ingest_rows_updates_job_status():
    repo = DummyUploadJobRepo()
    service = ExcelIngestService(repo)
    rows = service.parse_rows("湖南上架表格.xlsx")

    item_ids = service.ingest_rows("job-demo", rows)
    assert item_ids
    assert repo.status_updates[-1][1] == "prepared"


def test_import_pipeline_wires_task_step_repo(monkeypatch):
    captured = {}

    class DummySession:
        pass

    class DummyPublishTaskService:
        def __init__(self, task_repo, upload_job_repo, runtime_log_repo, task_step_repo=None):
            captured["task_step_repo"] = task_step_repo

    monkeypatch.setattr(import_pipeline_module, "UploadJobRepository", lambda session: "upload_repo")
    monkeypatch.setattr(import_pipeline_module, "RuntimeLogRepository", lambda session: "runtime_log_repo")
    monkeypatch.setattr(import_pipeline_module, "PublishTaskRepository", lambda session: "task_repo")
    monkeypatch.setattr(import_pipeline_module, "PublishTaskStepRepository", lambda session: "task_step_repo")
    monkeypatch.setattr(import_pipeline_module, "JDProductSnapshotRepository", lambda session: "snapshot_repo")
    monkeypatch.setattr(import_pipeline_module, "ProductImageRepository", lambda session: "image_repo")
    monkeypatch.setattr(import_pipeline_module, "TaskIngressService", lambda *args: "task_ingress")
    monkeypatch.setattr(import_pipeline_module, "ExcelIngestService", lambda *args: "excel_ingest")
    monkeypatch.setattr(import_pipeline_module, "PublishTaskService", DummyPublishTaskService)
    monkeypatch.setattr(import_pipeline_module, "JDProductFetchService", lambda *args: "jd_fetch")
    monkeypatch.setattr(import_pipeline_module, "ProductDataPrepareService", lambda *args, **kwargs: "product_prepare")

    import_pipeline_module.ImportPipelineService(DummySession())

    assert captured["task_step_repo"] == "task_step_repo"


def test_import_pipeline_runs_fetch_prepare_before_task_creation(monkeypatch):
    fake_session = type(
        "DummySession",
        (),
        {
            "commit": lambda self: None,
        },
    )()
    fake_runtime_log_repo = DummyRuntimeLogRepo()

    class DummyIngressService:
        def create_job_from_local_path(self, excel_path, session_id):
            return "job-123"

    class DummyExcelService:
        def parse_rows(self, excel_path):
            return ["row-1"]

        def ingest_rows(self, job_id, rows):
            return [101]

    class DummyFetchService:
        def __init__(self):
            self.calls = []

        def build_snapshot_for_job_item(self, job_item_id):
            self.calls.append(job_item_id)

    class DummyPrepareService:
        def __init__(self):
            self.calls = []

        def prepare_for_job_item(self, job_item_id):
            self.calls.append(job_item_id)
            return type(
                "Prepared",
                (),
                {
                    "product_name": "测试商品",
                    "brand": "公牛",
                    "model": "B5440",
                    "jd_sale_price": Decimal("70.00"),
                    "purchase_price": Decimal("66.50"),
                    "market_price": Decimal("82.35"),
                    "unit_name": "个",
                    "product_summary": "摘要",
                    "jd_item_id": "16793098028",
                    "jd_item_url": "https://item.jd.com/16793098028.html",
                    "category_path": "工业品 > 插座",
                    "detail_html": None,
                    "qualification_pdf_path": None,
                    "remark": None,
                    "item_type": "single",
                    "length_mm": Decimal("250.00"),
                    "width_mm": Decimal("76.00"),
                    "height_mm": Decimal("42.00"),
                    "weight_kg": Decimal("0.85"),
                    "images": [],
                },
            )()

    class DummyPublishTaskService:
        def create_tasks_for_job(self, job_id, mode="draft", store_id=None):
            return ["task-1"]

    pipeline = ImportPipelineService.__new__(ImportPipelineService)
    pipeline.session = fake_session
    pipeline.runtime_log_repo = fake_runtime_log_repo
    pipeline.task_ingress_service = DummyIngressService()
    pipeline.excel_ingest_service = DummyExcelService()
    pipeline.jd_fetch_service = DummyFetchService()
    pipeline.product_prepare_service = DummyPrepareService()
    pipeline.publish_task_service = DummyPublishTaskService()

    result = pipeline.run_from_local_excel_path("demo.xlsx")

    assert pipeline.jd_fetch_service.calls == [101]
    assert pipeline.product_prepare_service.calls == [101]
    assert result["prepared_products"][0]["job_item_id"] == 101
    assert result["prepared_products"][0]["jd_sale_price"] == "70.00"
    assert result["task_ids"] == ["task-1"]
