"""数据库引擎与会话工厂。"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy.orm import sessionmaker

from ..config import Settings


def create_engine_from_settings(settings: Settings) -> Engine:
    """根据配置创建 SQLAlchemy 数据库引擎。"""

    return create_engine(
        settings.mysql_url,
        pool_pre_ping=True,
        pool_size=settings.mysql_pool_size,
        max_overflow=settings.mysql_max_overflow,
        future=True,
    )


def create_session_factory(engine: Engine) -> sessionmaker:
    """创建数据库会话工厂。"""

    return sessionmaker(bind=engine, expire_on_commit=False, class_=OrmSession)
