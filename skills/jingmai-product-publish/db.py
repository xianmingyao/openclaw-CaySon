"""
京麦商品发布自动化 - 数据库管理器
MySQL 主 + SQLite 备用，SQLAlchemy 统一接口
"""
from typing import Optional, List
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models import Base, Product, PublishTask, TaskStep


class DatabaseManager:
    """数据库管理器 — MySQL 优先，SQLite 兜底"""

    def __init__(self, mysql_url: str = "", sqlite_url: str = ""):
        self._engine = None
        self._session_factory = None
        self._db_type = "none"

        # 尝试 MySQL
        if mysql_url:
            try:
                engine = create_engine(mysql_url, pool_pre_ping=True, pool_recycle=3600, echo=False)
                with engine.connect() as conn:
                    conn.execute("SELECT 1")
                self._engine = engine
                self._db_type = "mysql"
            except Exception as e:
                print(f"[DB] MySQL 连接失败: {e}，降级到 SQLite")

        # 降级 SQLite
        if self._engine is None and sqlite_url:
            try:
                engine = create_engine(sqlite_url, echo=False)
                self._engine = engine
                self._db_type = "sqlite"
            except Exception as e:
                print(f"[DB] SQLite 初始化失败: {e}")

        if self._engine:
            self._session_factory = sessionmaker(bind=self._engine)

    @property
    def db_type(self) -> str:
        return self._db_type

    def create_tables(self):
        """建表"""
        if self._engine:
            Base.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> Session:
        """获取数据库会话（上下文管理器）"""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ── Product CRUD ──────────────────────────────

    def save_product(self, product: Product) -> Product:
        """保存商品"""
        with self.session() as s:
            s.add(product)
            s.flush()
            s.refresh(product)
            return product

    def get_product(self, product_id: str) -> Optional[Product]:
        """按 product_id 获取商品"""
        with self.session() as s:
            return s.query(Product).filter(Product.product_id == product_id).first()

    def list_products(self, status: str = None, limit: int = 50) -> List[Product]:
        """列出商品"""
        with self.session() as s:
            q = s.query(Product)
            if status:
                q = q.filter(Product.status == status)
            return q.order_by(Product.created_at.desc()).limit(limit).all()

    # ── PublishTask CRUD ──────────────────────────

    def create_task(self, task: PublishTask) -> PublishTask:
        """创建发布任务"""
        with self.session() as s:
            s.add(task)
            s.flush()
            s.refresh(task)
            return task

    def get_task(self, task_id: str) -> Optional[PublishTask]:
        """按 task_id 获取任务"""
        with self.session() as s:
            return s.query(PublishTask).filter(PublishTask.task_id == task_id).first()

    def update_task_status(self, task_id: str, status: str, error: str = "", result: dict = None):
        """更新任务状态"""
        from datetime import datetime
        with self.session() as s:
            task = s.query(PublishTask).filter(PublishTask.task_id == task_id).first()
            if not task:
                return
            task.status = status
            if error:
                task.error_message = error
            if result:
                task.result = result
            if status == "running":
                task.started_at = datetime.now()
            elif status in ("success", "failed"):
                task.finished_at = datetime.now()
            s.flush()

    def list_tasks(self, status: str = None, limit: int = 50) -> List[PublishTask]:
        """列出任务"""
        with self.session() as s:
            q = s.query(PublishTask)
            if status:
                q = q.filter(PublishTask.status == status)
            return q.order_by(PublishTask.created_at.desc()).limit(limit).all()

    # ── TaskStep CRUD ─────────────────────────────

    def save_step(self, step: TaskStep) -> TaskStep:
        """保存步骤"""
        with self.session() as s:
            s.add(step)
            s.flush()
            s.refresh(step)
            return step

    def update_step_status(self, task_id: str, step_index: int, status: str,
                           error: str = "", screenshot: str = "", decision: dict = None):
        """更新步骤状态"""
        from datetime import datetime
        with self.session() as s:
            step = s.query(TaskStep).filter(
                TaskStep.task_id == task_id,
                TaskStep.step_index == step_index,
            ).first()
            if not step:
                return
            step.status = status
            if error:
                step.error_message = error
            if screenshot:
                step.screenshot_path = screenshot
            if decision:
                step.llm_decision = decision
            if status == "running":
                step.started_at = datetime.now()
            elif status in ("success", "failed", "skipped"):
                step.finished_at = datetime.now()
            s.flush()

    def get_steps(self, task_id: str) -> List[TaskStep]:
        """获取任务的所有步骤"""
        with self.session() as s:
            return s.query(TaskStep).filter(
                TaskStep.task_id == task_id,
            ).order_by(TaskStep.step_index).all()
