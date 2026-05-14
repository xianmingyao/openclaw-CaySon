"""数据库 ORM 模型定义。"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    DECIMAL,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.mysql import JSON, LONGTEXT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from jingmai_publish.db.base import Base


class UploadJob(Base):
    """导入批次主表。"""

    __tablename__ = "upload_jobs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    source_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_sha256: Mapped[Optional[str]] = mapped_column(String(64))
    business_type: Mapped[Optional[str]] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    items: Mapped[list["UploadJobItem"]] = relationship(back_populates="job", cascade="all, delete-orphan")


class UploadJobItem(Base):
    """Excel 单行商品数据。"""

    __tablename__ = "upload_job_items"
    __table_args__ = (
        UniqueConstraint("job_id", "row_no", name="uk_upload_job_items_job_row"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("upload_jobs.job_id", ondelete="CASCADE", onupdate="CASCADE"))
    row_no: Mapped[int] = mapped_column(Integer, nullable=False)
    apply_business: Mapped[Optional[str]] = mapped_column(String(32))
    product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String(255))
    model: Mapped[Optional[str]] = mapped_column(String(255))
    length_mm: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    width_mm: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    height_mm: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    weight_kg: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 3))
    unit_name: Mapped[Optional[str]] = mapped_column(String(64))
    jd_sale_price: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    purchase_price: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    market_price: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    jd_item_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    qualification_pdf_path: Mapped[Optional[str]] = mapped_column(String(1024))
    product_summary: Mapped[Optional[str]] = mapped_column(Text)
    remark: Mapped[Optional[str]] = mapped_column(Text)
    item_type: Mapped[Optional[str]] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    job: Mapped["UploadJob"] = relationship(back_populates="items")
    snapshots: Mapped[list["JDProductSnapshot"]] = relationship(
        back_populates="job_item", cascade="all, delete-orphan"
    )
    images: Mapped[list["ProductImage"]] = relationship(back_populates="job_item", cascade="all, delete-orphan")
    publish_tasks: Mapped[list["PublishTask"]] = relationship(
        back_populates="job_item", cascade="all, delete-orphan"
    )


class JDProductSnapshot(Base):
    """京东商品抓取快照。"""

    __tablename__ = "jd_product_snapshots"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_item_id: Mapped[int] = mapped_column(ForeignKey("upload_job_items.id", ondelete="CASCADE", onupdate="CASCADE"))
    jd_item_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    jd_item_id: Mapped[Optional[str]] = mapped_column(String(64))
    title: Mapped[Optional[str]] = mapped_column(String(500))
    brand: Mapped[Optional[str]] = mapped_column(String(255))
    model: Mapped[Optional[str]] = mapped_column(String(255))
    price: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    attributes_json: Mapped[Optional[dict]] = mapped_column(JSON)
    detail_html: Mapped[Optional[str]] = mapped_column(LONGTEXT)
    detail_text: Mapped[Optional[str]] = mapped_column(LONGTEXT)
    source_payload_json: Mapped[Optional[str]] = mapped_column(LONGTEXT)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    job_item: Mapped["UploadJobItem"] = relationship(back_populates="snapshots")


class ProductImage(Base):
    """商品图片本地化记录。"""

    __tablename__ = "product_images"
    __table_args__ = (
        UniqueConstraint("image_sha256", "image_role", name="uk_product_images_sha_role"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    job_item_id: Mapped[int] = mapped_column(ForeignKey("upload_job_items.id", ondelete="CASCADE", onupdate="CASCADE"))
    image_role: Mapped[str] = mapped_column(String(32), nullable=False)
    image_source_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    image_local_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    image_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    image_format: Mapped[Optional[str]] = mapped_column(String(32))
    image_width: Mapped[Optional[int]] = mapped_column(Integer)
    image_height: Mapped[Optional[int]] = mapped_column(Integer)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    is_valid: Mapped[int] = mapped_column(TINYINT, default=0, nullable=False)
    is_converted: Mapped[int] = mapped_column(TINYINT, default=0, nullable=False)
    converted_from_format: Mapped[Optional[str]] = mapped_column(String(32))
    download_status: Mapped[str] = mapped_column(String(32), default="downloaded", nullable=False)
    downloaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    job_item: Mapped["UploadJobItem"] = relationship(back_populates="images")


class PublishTask(Base):
    """单商品上架任务。"""

    __tablename__ = "publish_tasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    job_id: Mapped[str] = mapped_column(ForeignKey("upload_jobs.job_id", ondelete="CASCADE", onupdate="CASCADE"))
    job_item_id: Mapped[int] = mapped_column(ForeignKey("upload_job_items.id", ondelete="CASCADE", onupdate="CASCADE"))
    session_id: Mapped[str] = mapped_column(String(64), nullable=False)
    store_id: Mapped[Optional[str]] = mapped_column(String(64))
    window_handle: Mapped[Optional[str]] = mapped_column(String(128))
    mode: Mapped[str] = mapped_column(String(32), nullable=False)
    current_step: Mapped[Optional[str]] = mapped_column(String(64))
    page_state: Mapped[Optional[str]] = mapped_column(String(128))
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retry_count: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    failure_signature: Mapped[Optional[str]] = mapped_column(String(255))
    before_publish_screenshot: Mapped[Optional[str]] = mapped_column(String(1024))
    final_report_path: Mapped[Optional[str]] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    job_item: Mapped["UploadJobItem"] = relationship(back_populates="publish_tasks")
    steps: Mapped[list["PublishTaskStep"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    logs: Mapped[list["RuntimeLog"]] = relationship(back_populates="task")


class PublishTaskStep(Base):
    """上架任务步骤执行记录。"""

    __tablename__ = "publish_task_steps"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(ForeignKey("publish_tasks.task_id", ondelete="CASCADE", onupdate="CASCADE"))
    step_id: Mapped[str] = mapped_column(String(64), nullable=False)
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    primary_lane: Mapped[Optional[str]] = mapped_column(String(32))
    chosen_operator: Mapped[Optional[str]] = mapped_column(String(32))
    attempt_no: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="running", nullable=False)
    action_payload_json: Mapped[Optional[str]] = mapped_column(LONGTEXT)
    validator_result_json: Mapped[Optional[str]] = mapped_column(LONGTEXT)
    failure_signature: Mapped[Optional[str]] = mapped_column(String(255))
    before_screenshot_path: Mapped[Optional[str]] = mapped_column(String(1024))
    after_screenshot_path: Mapped[Optional[str]] = mapped_column(String(1024))
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    task: Mapped["PublishTask"] = relationship(back_populates="steps")


class RuntimeLog(Base):
    """运行日志记录表。"""

    __tablename__ = "runtime_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), nullable=False)
    task_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("publish_tasks.task_id", ondelete="SET NULL", onupdate="CASCADE")
    )
    job_id: Mapped[Optional[str]] = mapped_column(String(64))
    job_item_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    product_id: Mapped[Optional[str]] = mapped_column(String(64))
    step_id: Mapped[Optional[str]] = mapped_column(String(64))
    log_type: Mapped[str] = mapped_column(String(32), nullable=False)
    log_level: Mapped[str] = mapped_column(String(16), default="INFO", nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    detail_path: Mapped[Optional[str]] = mapped_column(String(1024))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    expire_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    task: Mapped[Optional["PublishTask"]] = relationship(back_populates="logs")

    @staticmethod
    def default_expire_at(now: Optional[datetime] = None) -> datetime:
        """计算日志默认过期时间。"""

        return (now or datetime.now()) + timedelta(days=3)
