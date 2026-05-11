"""
Jingmai product publishing database manager.
MySQL first, SQLite fallback.
"""
from contextlib import contextmanager
from datetime import datetime
import time
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from models import AcceptanceRun, Base, Product, PublishTask, TaskStep


def _to_dict(obj) -> Optional[Dict[str, Any]]:
    """Convert an ORM object into a plain dict."""
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
    """Database manager with MySQL preflight and SQLite fallback."""

    def __init__(self, settings=None, mysql_url: str = "", sqlite_url: str = ""):
        self._engine = None
        self._session_factory = None
        self._db_type = "none"
        self._mysql_pool_size = 10
        self._mysql_max_overflow = 20
        self._mysql_connect_timeout = 8
        self._mysql_read_timeout = 15
        self._mysql_write_timeout = 15
        self._mysql_init_retries = 3
        self._mysql_retry_delay_sec = 1.5

        if settings is not None:
            mysql_url = getattr(settings, "MYSQL_URL", "") or mysql_url
            sqlite_url = getattr(settings, "SQLITE_URL", "") or sqlite_url
            self._mysql_pool_size = int(getattr(settings, "MYSQL_POOL_SIZE", 10) or 10)
            self._mysql_max_overflow = int(getattr(settings, "MYSQL_MAX_OVERFLOW", 20) or 20)
            self._mysql_connect_timeout = int(getattr(settings, "MYSQL_CONNECT_TIMEOUT", 8) or 8)
            self._mysql_read_timeout = int(getattr(settings, "MYSQL_READ_TIMEOUT", 15) or 15)
            self._mysql_write_timeout = int(getattr(settings, "MYSQL_WRITE_TIMEOUT", 15) or 15)
            self._mysql_init_retries = int(getattr(settings, "MYSQL_INIT_RETRIES", 3) or 3)
            self._mysql_retry_delay_sec = float(getattr(settings, "MYSQL_RETRY_DELAY_SEC", 1.5) or 1.5)

        if mysql_url:
            engine = self._connect_mysql_with_retry(mysql_url)
            if engine is not None:
                self._engine = engine
                self._db_type = "mysql"

        if self._engine is None and sqlite_url:
            self._engine = create_engine(sqlite_url, echo=False)
            self._db_type = "sqlite"

        if self._engine is not None:
            self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

    @property
    def db_type(self) -> str:
        return self._db_type

    def probe(self) -> Dict[str, Any]:
        details = {
            "db_type": self._db_type,
            "mysql_pool_size": self._mysql_pool_size,
            "mysql_max_overflow": self._mysql_max_overflow,
            "mysql_connect_timeout": self._mysql_connect_timeout,
            "mysql_read_timeout": self._mysql_read_timeout,
            "mysql_write_timeout": self._mysql_write_timeout,
            "mysql_init_retries": self._mysql_init_retries,
            "mysql_retry_delay_sec": self._mysql_retry_delay_sec,
            "reachable": False,
            "error": "",
        }
        if self._engine is None:
            details["error"] = "engine-not-initialized"
            return details

        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            details["reachable"] = True
        except Exception as exc:
            details["error"] = str(exc)
        return details

    def _connect_mysql_with_retry(self, mysql_url: str):
        attempts = max(1, int(self._mysql_init_retries or 1))
        last_error = ""
        for attempt in range(1, attempts + 1):
            try:
                engine = create_engine(
                    mysql_url,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    pool_size=self._mysql_pool_size,
                    max_overflow=self._mysql_max_overflow,
                    connect_args={
                        "connect_timeout": self._mysql_connect_timeout,
                        "read_timeout": self._mysql_read_timeout,
                        "write_timeout": self._mysql_write_timeout,
                    },
                    echo=False,
                )
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                if attempt > 1:
                    print(f"[DB] MySQL connected on retry {attempt}/{attempts}")
                return engine
            except Exception as exc:
                last_error = str(exc)
                if attempt < attempts:
                    delay = max(0.2, float(self._mysql_retry_delay_sec or 1.5)) * attempt
                    print(
                        f"[DB] MySQL connect failed: attempt={attempt}/{attempts}, "
                        f"retry_in={delay:.1f}s, error={last_error}"
                    )
                    time.sleep(delay)
                else:
                    print(f"[DB] MySQL 连接失败: {last_error}，降级到 SQLite")
        return None

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
        """Upsert a product by product_id."""
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

    def create_acceptance_run(self, run: AcceptanceRun) -> AcceptanceRun:
        with self.session() as sess:
            sess.add(run)
            sess.flush()
            sess.refresh(run)
            return run

    def get_acceptance_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        with self.session() as sess:
            obj = sess.query(AcceptanceRun).filter(AcceptanceRun.run_id == run_id).first()
            return _to_dict(obj)

    def list_acceptance_runs(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self.session() as sess:
            rows = (
                sess.query(AcceptanceRun)
                .order_by(AcceptanceRun.created_at.desc())
                .limit(limit)
                .all()
            )
            return [_to_dict(row) for row in rows]

    def update_acceptance_run(
        self,
        run_id: str,
        *,
        status: str = "",
        success_count: Optional[int] = None,
        fail_count: Optional[int] = None,
        total_items: Optional[int] = None,
        summary: Optional[dict] = None,
        error: str = "",
        summary_file: str = "",
        progress_file: str = "",
        plan_dir: str = "",
    ) -> None:
        with self.session() as sess:
            run = sess.query(AcceptanceRun).filter(AcceptanceRun.run_id == run_id).first()
            if run is None:
                return

            if status:
                run.status = status
            if success_count is not None:
                run.success_count = int(success_count)
            if fail_count is not None:
                run.fail_count = int(fail_count)
            if total_items is not None:
                run.total_items = int(total_items)
            if summary is not None:
                run.summary = summary
            if error:
                run.error_message = error
            if summary_file:
                run.summary_file = summary_file
            if progress_file:
                run.progress_file = progress_file
            if plan_dir:
                run.plan_dir = plan_dir
            if run.status in {"running", "in_progress"} and run.started_at is None:
                run.started_at = datetime.now()
            if run.status in {"success", "failed"}:
                run.finished_at = datetime.now()
            sess.flush()

    def _sync_schema(self) -> None:
        """Backfill missing columns for existing databases."""
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
