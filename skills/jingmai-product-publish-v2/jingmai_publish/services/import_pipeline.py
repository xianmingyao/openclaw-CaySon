"""导入与任务创建主链路服务。"""

from __future__ import annotations

from pathlib import Path
import uuid

from sqlalchemy.orm import Session

from jingmai_publish.repositories.runtime_log import RuntimeLogRepository
from jingmai_publish.repositories.upload_job import UploadJobRepository
from jingmai_publish.repositories.publish_task import PublishTaskRepository
from jingmai_publish.services.excel_ingest import ExcelIngestService
from jingmai_publish.services.task_ingress import TaskIngressService
from jingmai_publish.services.task_service import PublishTaskService


class ImportPipelineService:
    """协调“本地文件路径 -> Excel 入库 -> 创建上架任务”的主链路。"""

    def __init__(self, session: Session) -> None:
        """按数据库会话组装主链路依赖。"""

        upload_job_repo = UploadJobRepository(session)
        runtime_log_repo = RuntimeLogRepository(session)
        task_repo = PublishTaskRepository(session)

        self.session = session
        self.upload_job_repo = upload_job_repo
        self.runtime_log_repo = runtime_log_repo
        self.task_ingress_service = TaskIngressService(upload_job_repo, runtime_log_repo)
        self.excel_ingest_service = ExcelIngestService(upload_job_repo)
        self.publish_task_service = PublishTaskService(task_repo, upload_job_repo, runtime_log_repo)

    def run_from_local_excel_path(
        self,
        excel_path: str | Path,
        *,
        mode: str = "draft",
        store_id: str | None = None,
    ) -> dict[str, object]:
        """执行 Excel 导入入库并创建上架任务。"""

        session_id = f"ingress-{uuid.uuid4().hex[:12]}"
        job_id = self.task_ingress_service.create_job_from_local_path(excel_path, session_id=session_id)

        rows = self.excel_ingest_service.parse_rows(excel_path)
        item_ids = self.excel_ingest_service.ingest_rows(job_id, rows)
        task_ids = self.publish_task_service.create_tasks_for_job(job_id, mode=mode, store_id=store_id)

        self.runtime_log_repo.append_log(
            session_id=session_id,
            job_id=job_id,
            log_type="success",
            message=f"导入完成，已创建 {len(item_ids)} 条商品行和 {len(task_ids)} 个任务",
        )
        self.session.commit()

        return {
            "job_id": job_id,
            "session_id": session_id,
            "row_count": len(rows),
            "item_ids": item_ids,
            "task_ids": task_ids,
        }
