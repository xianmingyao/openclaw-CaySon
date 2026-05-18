"""导入、抓取、准备与任务创建主链路服务。"""

from __future__ import annotations

import uuid
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

from jingmai_publish.repositories.jd_snapshot import JDProductSnapshotRepository
from jingmai_publish.repositories.product_image import ProductImageRepository
from jingmai_publish.repositories.publish_task import PublishTaskRepository, PublishTaskStepRepository
from jingmai_publish.repositories.runtime_log import RuntimeLogRepository
from jingmai_publish.repositories.upload_job import UploadJobRepository
from jingmai_publish.services.excel_ingest import ExcelIngestService
from jingmai_publish.services.jd_fetch import JDProductFetchService
from jingmai_publish.services.product_prepare import ProductDataPrepareService
from jingmai_publish.services.task_ingress import TaskIngressService
from jingmai_publish.services.task_service import PublishTaskService


class ImportPipelineService:
    """协调“本地 Excel -> 入库 -> 抓取 -> 标准化准备 -> 创建上架任务”的主链路。"""

    def __init__(self, session: Session) -> None:
        upload_job_repo = UploadJobRepository(session)
        runtime_log_repo = RuntimeLogRepository(session)
        task_repo = PublishTaskRepository(session)
        task_step_repo = PublishTaskStepRepository(session)
        snapshot_repo = JDProductSnapshotRepository(session)
        image_repo = ProductImageRepository(session)

        self.session = session
        self.upload_job_repo = upload_job_repo
        self.runtime_log_repo = runtime_log_repo
        self.task_ingress_service = TaskIngressService(upload_job_repo, runtime_log_repo)
        self.excel_ingest_service = ExcelIngestService(upload_job_repo)
        self.jd_fetch_service = JDProductFetchService(upload_job_repo, snapshot_repo, runtime_log_repo)
        self.product_prepare_service = ProductDataPrepareService(
            upload_job_repo,
            snapshot_repo,
            runtime_log_repo,
            image_repo=image_repo,
        )
        self.publish_task_service = PublishTaskService(
            task_repo,
            upload_job_repo,
            runtime_log_repo,
            task_step_repo,
        )

    def run_from_local_excel_path(
            self,
            excel_path: str | Path,
            *,
            mode: str = "draft",
            store_id: str | None = None,
    ) -> dict[str, object]:
        session_id = f"ingress-{uuid.uuid4().hex[:12]}"
        job_id = self.task_ingress_service.create_job_from_local_path(excel_path, session_id=session_id)

        rows = self.excel_ingest_service.parse_rows(excel_path)
        item_ids = self.excel_ingest_service.ingest_rows(job_id, rows)
        prepared_products = self._prepare_job_items(item_ids)
        task_ids = self.publish_task_service.create_tasks_for_job(job_id, mode=mode, store_id=store_id)

        self.runtime_log_repo.append_log(
            session_id=session_id,
            job_id=job_id,
            log_type="success",
            message=(
                f"导入完成，已创建 {len(item_ids)} 条商品行、"
                f"{len(prepared_products)} 条标准化数据和 {len(task_ids)} 个任务"
            ),
        )
        self.session.commit()

        return {
            "job_id": job_id,
            "session_id": session_id,
            "row_count": len(rows),
            "item_ids": item_ids,
            "prepared_products": prepared_products,
            "task_ids": task_ids,
        }

    def _prepare_job_items(self, item_ids: list[int]) -> list[dict[str, object]]:
        prepared_products: list[dict[str, object]] = []
        for job_item_id in item_ids:
            self.jd_fetch_service.build_snapshot_for_job_item(job_item_id)
            prepared = self.product_prepare_service.prepare_for_job_item(job_item_id)
            prepared_products.append(self._serialize_prepared_product(job_item_id, prepared))
        return prepared_products

    @staticmethod
    def _serialize_prepared_product(job_item_id: int, prepared) -> dict[str, object]:
        if is_dataclass(prepared):
            payload = asdict(prepared)
        else:
            payload = ImportPipelineService._object_to_dict(prepared)
        payload["job_item_id"] = job_item_id
        return ImportPipelineService._normalize_value(payload)

    @staticmethod
    def _object_to_dict(value) -> dict[str, object]:
        instance_payload = dict(vars(value))
        if instance_payload:
            return instance_payload

        payload: dict[str, object] = {}
        for name in dir(value):
            if name.startswith("_"):
                continue
            attr_value = getattr(value, name)
            if callable(attr_value):
                continue
            payload[name] = attr_value
        return payload

    @staticmethod
    def _normalize_value(value):
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, list):
            return [ImportPipelineService._normalize_value(item) for item in value]
        if isinstance(value, dict):
            return {key: ImportPipelineService._normalize_value(item) for key, item in value.items()}
        return value
