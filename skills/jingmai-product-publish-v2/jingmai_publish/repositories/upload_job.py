"""导入任务相关 Repository。"""

from __future__ import annotations

from sqlalchemy.orm import Session

from jingmai_publish.models import UploadJob, UploadJobItem


class UploadJobRepository:
    """导入批次与行数据读写仓库。"""

    def __init__(self, session: Session) -> None:
        """注入数据库会话。"""

        self.session = session

    def create_job(
        self,
        job_id: str,
        source_type: str,
        source_file_path: str,
        source_file_name: str,
        file_sha256: str | None,
        business_type: str | None,
    ) -> UploadJob:
        """创建导入批次。"""

        job = UploadJob(
            job_id=job_id,
            source_type=source_type,
            source_file_path=source_file_path,
            source_file_name=source_file_name,
            file_sha256=file_sha256,
            business_type=business_type,
        )
        self.session.add(job)
        self.session.flush()
        return job

    def get_job_by_job_id(self, job_id: str) -> UploadJob | None:
        """按业务主键查询批次。"""

        return self.session.query(UploadJob).filter(UploadJob.job_id == job_id).one_or_none()

    def update_job_status(
        self,
        job_id: str,
        status: str,
        *,
        total_rows: int | None = None,
        success_rows: int | None = None,
        failed_rows: int | None = None,
    ) -> None:
        """更新批次状态与计数信息。"""

        job = self.get_job_by_job_id(job_id)
        if job is None:
            raise ValueError(f"未找到导入批次: {job_id}")

        job.status = status
        if total_rows is not None:
            job.total_rows = total_rows
        if success_rows is not None:
            job.success_rows = success_rows
        if failed_rows is not None:
            job.failed_rows = failed_rows
        self.session.flush()

    def create_job_item(self, **kwargs) -> UploadJobItem:
        """创建 Excel 单行商品记录。"""

        item = UploadJobItem(**kwargs)
        self.session.add(item)
        self.session.flush()
        return item

    def list_job_items(self, job_id: str) -> list[UploadJobItem]:
        """列出批次下所有商品行。"""

        return (
            self.session.query(UploadJobItem)
            .filter(UploadJobItem.job_id == job_id)
            .order_by(UploadJobItem.row_no.asc())
            .all()
        )

    def get_job_item(self, job_item_id: int) -> UploadJobItem | None:
        """按主键查询单条商品行。"""

        return self.session.query(UploadJobItem).filter(UploadJobItem.id == job_item_id).one_or_none()
