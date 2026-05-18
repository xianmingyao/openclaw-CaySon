"""发布任务与步骤审计 Repository。"""

from __future__ import annotations

from datetime import datetime
from jingmai_publish.models import PublishTask, PublishTaskStep
from sqlalchemy.orm import Session


class PublishTaskRepository:
    """商品上架任务仓储。"""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_task(
            self,
            task_id: str,
            job_id: str,
            job_item_id: int,
            session_id: str,
            mode: str,
            store_id: str | None = None,
    ) -> PublishTask:
        task = PublishTask(
            task_id=task_id,
            job_id=job_id,
            job_item_id=job_item_id,
            session_id=session_id,
            mode=mode,
            store_id=store_id,
        )
        self.session.add(task)
        self.session.flush()
        return task

    def get_task_by_task_id(self, task_id: str) -> PublishTask | None:
        return self.session.query(PublishTask).filter(PublishTask.task_id == task_id).one_or_none()

    def update_task_status(self, task_id: str, status: str, **kwargs) -> None:
        task = self.get_task_by_task_id(task_id)
        if task is None:
            raise ValueError(f"未找到任务: {task_id}")

        task.status = status
        for key, value in kwargs.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)
        self.session.flush()

    def list_tasks_by_job_id(self, job_id: str) -> list[PublishTask]:
        return self.session.query(PublishTask).filter(PublishTask.job_id == job_id).all()


class PublishTaskStepRepository:
    """任务步骤审计仓储。"""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_step(
            self,
            task_id: str,
            step_id: str,
            step_name: str,
            sequence_no: int,
            primary_lane: str | None,
            chosen_operator: str | None,
            attempt_no: int,
            *,
            status: str = "running",
            action_payload_json: str | None = None,
            before_screenshot_path: str | None = None,
    ) -> PublishTaskStep:
        step = PublishTaskStep(
            task_id=task_id,
            step_id=step_id,
            step_name=step_name,
            sequence_no=sequence_no,
            primary_lane=primary_lane,
            chosen_operator=chosen_operator,
            attempt_no=attempt_no,
            status=status,
            action_payload_json=action_payload_json,
            before_screenshot_path=before_screenshot_path,
        )
        self.session.add(step)
        self.session.flush()
        return step

    def get_step(self, task_id: str, step_id: str, sequence_no: int) -> PublishTaskStep | None:
        return (
            self.session.query(PublishTaskStep)
            .filter(PublishTaskStep.task_id == task_id)
            .filter(PublishTaskStep.step_id == step_id)
            .filter(PublishTaskStep.sequence_no == sequence_no)
            .one_or_none()
        )

    def update_step_status(
            self,
            task_id: str,
            step_id: str,
            sequence_no: int,
            *,
            status: str,
            validator_result_json: str | None = None,
            failure_signature: str | None = None,
            after_screenshot_path: str | None = None,
            finished_at: datetime | None = None,
    ) -> PublishTaskStep:
        step = self.get_step(task_id, step_id, sequence_no)
        if step is None:
            raise ValueError(f"未找到任务步骤: {task_id}/{step_id}/{sequence_no}")

        step.status = status
        if validator_result_json is not None:
            step.validator_result_json = validator_result_json
        if failure_signature is not None:
            step.failure_signature = failure_signature
        if after_screenshot_path is not None:
            step.after_screenshot_path = after_screenshot_path
        step.finished_at = finished_at or datetime.now()
        self.session.flush()
        return step

    def list_steps_by_task_id(self, task_id: str) -> list[PublishTaskStep]:
        return (
            self.session.query(PublishTaskStep)
            .filter(PublishTaskStep.task_id == task_id)
            .order_by(PublishTaskStep.sequence_no.asc(), PublishTaskStep.id.asc())
            .all()
        )
