"""数据库初始化入口。"""

from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from jingmai_publish.db.base import Base
from jingmai_publish.models import (  # noqa: F401
    JDProductSnapshot,
    ProductImage,
    PublishTask,
    PublishTaskStep,
    RuntimeLog,
    UploadJob,
    UploadJobItem,
)


def init_database(engine: Engine) -> None:
    """初始化数据库表结构。"""

    Base.metadata.create_all(engine)
    _migrate_legacy_publish_tasks(engine)


def _migrate_legacy_publish_tasks(engine: Engine) -> None:
    """兼容旧版 publish_tasks 表结构。

    SQLAlchemy `create_all()` 只会创建不存在的表，不会为已有表补列。
    当前远端开发库存在旧版 `publish_tasks(product_id, plan, result...)`，
    因此这里做最小非破坏式迁移，补齐当前导入链路需要的字段。
    """

    if engine.dialect.name != "mysql":
        return

    inspector = inspect(engine)
    if not inspector.has_table("publish_tasks"):
        return

    columns = {column["name"]: column for column in inspector.get_columns("publish_tasks")}
    ddl_statements: list[str] = []
    column_specs = {
        "job_id": "VARCHAR(64) NULL",
        "job_item_id": "BIGINT NULL",
        "session_id": "VARCHAR(64) NULL",
        "store_id": "VARCHAR(64) NULL",
        "window_handle": "VARCHAR(128) NULL",
        "mode": "VARCHAR(32) NULL",
        "current_step": "VARCHAR(64) NULL",
        "page_state": "VARCHAR(128) NULL",
        "max_retry_count": "INT NOT NULL DEFAULT 3",
        "failure_signature": "VARCHAR(255) NULL",
        "before_publish_screenshot": "VARCHAR(1024) NULL",
        "final_report_path": "VARCHAR(1024) NULL",
    }
    for column_name, column_spec in column_specs.items():
        if column_name not in columns:
            ddl_statements.append(f"ALTER TABLE publish_tasks ADD COLUMN {column_name} {column_spec}")

    product_id = columns.get("product_id")
    if product_id is not None and not product_id.get("nullable", True):
        ddl_statements.append("ALTER TABLE publish_tasks MODIFY COLUMN product_id VARCHAR(64) NULL")

    if not ddl_statements:
        return

    with engine.begin() as connection:
        for statement in ddl_statements:
            connection.execute(text(statement))
