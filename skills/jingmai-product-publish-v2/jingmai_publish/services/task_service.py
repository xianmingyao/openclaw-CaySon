"""上架任务创建服务。"""

from __future__ import annotations

import json
import uuid

from jingmai_publish.repositories.publish_task import PublishTaskRepository, PublishTaskStepRepository
from jingmai_publish.repositories.runtime_log import RuntimeLogRepository
from jingmai_publish.repositories.upload_job import UploadJobRepository


class PublishTaskService:
    """负责生成单商品上架任务，并写入首个步骤审计记录。"""

    def __init__(
        self,
        task_repo: PublishTaskRepository,
        upload_job_repo: UploadJobRepository,
        runtime_log_repo: RuntimeLogRepository | None = None,
        task_step_repo: PublishTaskStepRepository | None = None,
    ) -> None:
        self.task_repo = task_repo
        self.upload_job_repo = upload_job_repo
        self.runtime_log_repo = runtime_log_repo
        self.task_step_repo = task_step_repo

    def create_task_for_job_item(
        self,
        job_id: str,
        job_item_id: int,
        mode: str,
        store_id: str | None = None,
    ):
        task_id = f"task-{uuid.uuid4().hex[:12]}"
        session_id = f"session-{uuid.uuid4().hex[:12]}"
        task = self.task_repo.create_task(
            task_id=task_id,
            job_id=job_id,
            job_item_id=job_item_id,
            session_id=session_id,
            mode=mode,
            store_id=store_id,
        )

        if self.task_step_repo is not None:
            action_payload = json.dumps(
                {
                    "job_id": job_id,
                    "job_item_id": job_item_id,
                    "mode": mode,
                    "store_id": store_id,
                },
                ensure_ascii=False,
            )
            self.task_step_repo.create_step(
                task_id=task.task_id,
                step_id="TASK_CREATED",
                step_name="创建上架任务",
                sequence_no=1,
                primary_lane="system",
                chosen_operator="publish_task_service",
                attempt_no=1,
                action_payload_json=action_payload,
            )
            self.task_step_repo.update_step_status(
                task_id=task.task_id,
                step_id="TASK_CREATED",
                sequence_no=1,
                status="succeeded",
                validator_result_json=json.dumps(
                    {
                        "task_id": task.task_id,
                        "session_id": task.session_id,
                        "status": "task_created",
                    },
                    ensure_ascii=False,
                ),
            )
            self.task_repo.update_task_status(
                task.task_id,
                "pending",
                current_step="TASK_CREATED",
                page_state="task_created",
            )

        return task

    def create_tasks_for_job(
        self,
        job_id: str,
        mode: str = "draft",
        store_id: str | None = None,
    ) -> list[str]:
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
