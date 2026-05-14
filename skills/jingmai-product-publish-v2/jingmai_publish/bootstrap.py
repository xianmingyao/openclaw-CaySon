"""数据库初始化入口。"""

from __future__ import annotations

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
