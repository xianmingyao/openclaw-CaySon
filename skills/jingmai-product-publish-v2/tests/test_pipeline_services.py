from decimal import Decimal
from pathlib import Path

from jingmai_publish.services.excel_ingest import ExcelIngestService
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
