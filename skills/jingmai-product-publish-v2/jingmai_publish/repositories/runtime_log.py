"""运行日志 Repository。"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from jingmai_publish.models import RuntimeLog


class RuntimeLogRepository:
    """运行日志写入与清理仓库。"""

    def __init__(self, session: Session) -> None:
        """注入数据库会话。"""

        self.session = session

    def append_log(
        self,
        session_id: str,
        log_type: str,
        message: str,
        *,
        task_id: str | None = None,
        job_id: str | None = None,
        job_item_id: int | None = None,
        product_id: str | None = None,
        step_id: str | None = None,
        log_level: str = "INFO",
        detail_path: str | None = None,
        expire_at: datetime | None = None,
    ) -> RuntimeLog:
        """追加一条运行日志。"""

        log = RuntimeLog(
            session_id=session_id,
            task_id=task_id,
            job_id=job_id,
            job_item_id=job_item_id,
            product_id=product_id,
            step_id=step_id,
            log_type=log_type,
            log_level=log_level,
            message=message,
            detail_path=detail_path,
            expire_at=expire_at or RuntimeLog.default_expire_at(),
        )
        self.session.add(log)
        self.session.flush()
        return log

    def delete_expired_logs(self, now: datetime) -> int:
        """删除已过期日志，并返回删除数量。"""

        result = self.session.query(RuntimeLog).filter(RuntimeLog.expire_at < now).delete()
        self.session.flush()
        return int(result)
