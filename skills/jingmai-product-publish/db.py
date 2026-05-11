"""
京麦商品发布自动化 - 数据库管理器
MySQL 优先，SQLite 兜底。
"""
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from models import Base, Product, PublishTask, TaskStep


def _to_dict(obj) -> Optional[Dict[str, Any]]:
    """将 ORM 对象转成字典，避免 detached instance 问题。"""
    if obj is None:
        return None

    result: Dict[str, Any] = {}
    for col in obj.__table__.columns:
        value = getattr(obj, col.name, None)
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        result[col.name] = value
    return result


class DatabaseManager:
    """数据库管理器。"""

    def __init__(self, settings=None, mysql_url: str = "", sqlite_url: str = ""):
        self._engine = None
        self._session_factory = None
        self._db_type = "none"
        self._mysql_pool_size = 10
        self._mysql_max_overflow = 20

        # 支持 settings 对象或独立参数
        if settings is not None:
            mysql_url = getattr(settings, "MYSQL_URL", "") or mysql_url
            sqlite_url = getattr(settings, "SQLITE_URL", "") or sqlite_url
            self._mysql_pool_size = int(getattr(settings, "MYSQL_POOL_SIZE", 10) or 10)
            self._mysql_max_overflow = int(getattr(settings, "MYSQL_MAX_OVERFLOW", 20) or 20)

        if mysql_url:
            try:
                engine = create_engine(
                    mysql_url,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    pool_size=self._mysql_pool_size,
                    max_overflow=self._mysql_max_overflow,
                    echo=False,
                )
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                self._engine = engine
                self._db_type = "mysql"
            except Exception as exc:
                print(f"[DB] MySQL 连接失败: {exc}，降级到 SQLite")

        if self._engine is None and sqlite_url:
            engine = create_engine(sqlite_url, echo=False)
            self._engine = engine
            self._db_type = "sqlite"

        if self._engine is not None:
            self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

    @property
    def db_type(self) -> str:
        return self._db_type

    def create_tables(self) -> None:
        if self._engine is not None:
            Base.metadata.create_all(self._engine)
            self._sync_schema()

    @contextmanager
    def session(self) -> Session:
        if self._session_factory is None:
            raise RuntimeError("数据库未初始化")

        sess = self._session_factory()
        try:
            yield sess
            sess.commit()
        except Exception:
            sess.rollback()
            raise
        finally:
            sess.close()

    def save_product(self, product: Product) -> Product:
        """按 product_id upsert 商品。"""
        with self.session() as sess:
            existing = sess.query(Product).filter(Product.product_id == product.product_id).first()
            if existing is None:
                sess.add(product)
                sess.flush()
                sess.refresh(product)
                return product

            for field in (
                "title",
                "source_url",
                "category",
                "category_path",
                "price",
                "stock",
                "status",
                "source",
                "attributes",
                "images",
                "detail_images",
                "source_meta",
                "raw_data",
            ):
                setattr(existing, field, getattr(product, field))
            existing.updated_at = datetime.now()
            sess.flush()
            sess.refresh(existing)
            return existing

    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        with self.session() as sess:
            obj = sess.query(Product).filter(Product.product_id == product_id).first()
            return _to_dict(obj)

    def list_products(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self.session() as sess:
            query = sess.query(Product)
            if status:
                query = query.filter(Product.status == status)
            return [_to_dict(row) for row in query.order_by(Product.created_at.desc()).limit(limit).all()]

    def create_task(self, task: PublishTask) -> PublishTask:
        with self.session() as sess:
            sess.add(task)
            sess.flush()
            sess.refresh(task)
            return task

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self.session() as sess:
            obj = sess.query(PublishTask).filter(PublishTask.task_id == task_id).first()
            return _to_dict(obj)

    def update_task_status(
        self,
        task_id: str,
        status: str,
        error: str = "",
        result: Optional[dict] = None,
    ) -> None:
        with self.session() as sess:
            task = sess.query(PublishTask).filter(PublishTask.task_id == task_id).first()
            if task is None:
                return

            task.status = status
            if error:
                task.error_message = error
            if result is not None:
                task.result = result

            if status in {"planning", "running", "in_progress"} and task.started_at is None:
                task.started_at = datetime.now()
            if status in {"success", "failed"}:
                task.finished_at = datetime.now()
            sess.flush()

    def list_tasks(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        with self.session() as sess:
            query = sess.query(PublishTask)
            if status:
                query = query.filter(PublishTask.status == status)
            return [_to_dict(row) for row in query.order_by(PublishTask.created_at.desc()).limit(limit).all()]

    def save_step(self, step: TaskStep) -> TaskStep:
        with self.session() as sess:
            sess.add(step)
            sess.flush()
            sess.refresh(step)
            return step

    def update_step_status(
        self,
        task_id: str,
        step_index: int,
        status: str,
        error: str = "",
        screenshot: str = "",
        decision: Optional[dict] = None,
        result: Optional[dict] = None,
    ) -> None:
        with self.session() as sess:
            step = sess.query(TaskStep).filter(
                TaskStep.task_id == task_id,
                TaskStep.step_index == step_index,
            ).first()
            if step is None:
                return

            step.status = status
            if error:
                step.error_message = error
            if screenshot:
                step.screenshot_path = screenshot
            if decision is not None:
                step.llm_decision = decision
            if result is not None:
                step.result = result

            if status == "running" and step.started_at is None:
                step.started_at = datetime.now()
            if status in {"success", "failed", "skipped"}:
                step.finished_at = datetime.now()
            sess.flush()

    def get_steps(self, task_id: str) -> List[Dict[str, Any]]:
        with self.session() as sess:
            rows = sess.query(TaskStep).filter(TaskStep.task_id == task_id).order_by(TaskStep.step_index).all()
            return [_to_dict(row) for row in rows]

    def list_steps(self, task_id: str) -> List[Dict[str, Any]]:
        return self.get_steps(task_id)

    def _sync_schema(self) -> None:
        """为已有库补齐新版本缺失列。"""
        if self._engine is None:
            return

        inspector = inspect(self._engine)
        table_defs = {
            "products": {
                "source_url": self._column_sql("source_url"),
                "category_path": self._column_sql("category_path"),
                "attributes": self._column_sql("attributes"),
                "images": self._column_sql("images"),
                "detail_images": self._column_sql("detail_images"),
                "source_meta": self._column_sql("source_meta"),
            },
            "task_steps": {
                "result": self._column_sql("result"),
            },
        }

        with self._engine.begin() as conn:
            for table_name, columns in table_defs.items():
                try:
                    existing = {col["name"] for col in inspector.get_columns(table_name)}
                except Exception:
                    continue
                for column_name, ddl in columns.items():
                    if column_name in existing:
                        continue
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {ddl}"))

    def _column_sql(self, column_name: str) -> str:
        if self._db_type == "mysql":
            mapping = {
                "source_url": "source_url VARCHAR(1024) NOT NULL DEFAULT ''",
                "category_path": "category_path VARCHAR(512) NOT NULL DEFAULT ''",
                "attributes": "attributes JSON NULL",
                "images": "images JSON NULL",
                "detail_images": "detail_images JSON NULL",
                "source_meta": "source_meta JSON NULL",
                "result": "result JSON NULL",
            }
        else:
            mapping = {
                "source_url": "source_url VARCHAR(1024) DEFAULT ''",
                "category_path": "category_path VARCHAR(512) DEFAULT ''",
                "attributes": "attributes JSON DEFAULT '{}'",
                "images": "images JSON DEFAULT '[]'",
                "detail_images": "detail_images JSON DEFAULT '[]'",
                "source_meta": "source_meta JSON DEFAULT '{}'",
                "result": "result JSON DEFAULT '{}'",
            }
        return mapping[column_name]
