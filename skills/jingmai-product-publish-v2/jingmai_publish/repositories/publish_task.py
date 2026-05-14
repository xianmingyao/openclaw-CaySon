"""发布任务 Repository。"""

from __future__ import annotations

from sqlalchemy.orm import Session

from jingmai_publish.models import PublishTask, PublishTaskStep


class PublishTaskRepository:
    """商品上架任务仓库。"""

    def __init__(self, session: Session) -> None:
        """注入数据库会话。"""

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
        """创建单商品上架任务。"""

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
        """按任务 ID 查询任务。"""

        return self.session.query(PublishTask).filter(PublishTask.task_id == task_id).one_or_none()

    def update_task_status(self, task_id: str, status: str, **kwargs) -> None:
        """更新任务状态。"""

        task = self.get_task_by_task_id(task_id)
        if task is None:
            raise ValueError(f"未找到任务: {task_id}")

        task.status = status
        for key, value in kwargs.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)
        self.session.flush()

    def list_tasks_by_job_id(self, job_id: str) -> list[PublishTask]:
        """查询一个导入批次下的所有上架任务。"""

        return self.session.query(PublishTask).filter(PublishTask.job_id == job_id).all()


class PublishTaskStepRepository:
    """任务步骤记录仓库。"""

    def __init__(self, session: Session) -> None:
        """注入数据库会话。"""

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
    ) -> PublishTaskStep:
        """创建步骤执行记录。"""

        step = PublishTaskStep(
            task_id=task_id,
            step_id=step_id,
            step_name=step_name,
            sequence_no=sequence_no,
            primary_lane=primary_lane,
            chosen_operator=chosen_operator,
            attempt_no=attempt_no,
        )
        self.session.add(step)
        self.session.flush()
        return step
