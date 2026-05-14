"""上架任务服务。"""

from __future__ import annotations

import uuid

from jingmai_publish.repositories.runtime_log import RuntimeLogRepository
from jingmai_publish.repositories.publish_task import PublishTaskRepository
from jingmai_publish.repositories.upload_job import UploadJobRepository


class PublishTaskService:
    """负责生成单商品上架任务。"""

    def __init__(
        self,
        task_repo: PublishTaskRepository,
        upload_job_repo: UploadJobRepository,
        runtime_log_repo: RuntimeLogRepository | None = None,
    ) -> None:
        """注入任务仓库、导入仓库和日志仓库。"""

        self.task_repo = task_repo
        self.upload_job_repo = upload_job_repo
        self.runtime_log_repo = runtime_log_repo

    def create_task_for_job_item(
        self,
        job_id: str,
        job_item_id: int,
        mode: str,
        store_id: str | None = None,
    ):
        """根据导入行创建上架任务。"""

        task_id = f"task-{uuid.uuid4().hex[:12]}"
        session_id = f"session-{uuid.uuid4().hex[:12]}"
        return self.task_repo.create_task(
            task_id=task_id,
            job_id=job_id,
            job_item_id=job_item_id,
            session_id=session_id,
            mode=mode,
            store_id=store_id,
        )

    def create_tasks_for_job(
        self,
        job_id: str,
        mode: str = "draft",
        store_id: str | None = None,
    ) -> list[str]:
        """为导入批次下的所有商品行批量创建上架任务。"""

        task_ids: list[str] = []
        for item in self.upload_job_repo.list_job_items(job_id):
            task = self.create_task_for_job_item(
                job_id=job_id,
                job_item_id=item.id,
                mode=mode,
                store_id=store_id,
            )
            task_ids.append(task.task_id)
            if self.runtime_log_repo is not None:
                self.runtime_log_repo.append_log(
                    session_id=task.session_id,
                    task_id=task.task_id,
                    job_id=job_id,
                    job_item_id=item.id,
                    log_type="prepare",
                    message=f"已为第 {item.row_no} 行创建上架任务",
                )
        return task_ids
