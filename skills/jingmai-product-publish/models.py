"""
京麦商品发布自动化 - SQLAlchemy ORM 模型
商品、发布任务、任务步骤
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """ORM 基类"""
    pass


class Product(Base):
    """商品信息"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(64), unique=True, nullable=False, comment="商品编号")
    title = Column(String(512), nullable=False, comment="商品标题")
    category = Column(String(256), default="", comment="类目路径")
    price = Column(Float, default=0.0, comment="价格")
    stock = Column(Integer, default=0, comment="库存")
    status = Column(String(32), default="draft", comment="状态: draft/published/failed")
    source = Column(String(64), default="manual", comment="来源: manual/scrape/api")
    raw_data = Column(JSON, default=dict, comment="原始数据")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<Product {self.product_id} '{self.title[:20]}'>"


class PublishTask(Base):
    """发布任务"""
    __tablename__ = "publish_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(64), unique=True, nullable=False, comment="任务编号")
    product_id = Column(String(64), nullable=False, comment="关联商品编号")
    status = Column(String(32), default="pending", comment="状态: pending/running/success/failed")
    plan = Column(JSON, default=dict, comment="执行计划（Planner 生成）")
    result = Column(JSON, default=dict, comment="执行结果")
    error_message = Column(Text, default="", comment="错误信息")
    retry_count = Column(Integer, default=0, comment="重试次数")
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    finished_at = Column(DateTime, nullable=True, comment="完成时间")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<PublishTask {self.task_id} [{self.status}]>"


class TaskStep(Base):
    """任务步骤"""
    __tablename__ = "task_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(64), nullable=False, comment="关联任务编号")
    step_index = Column(Integer, nullable=False, comment="步骤序号")
    action_name = Column(String(128), nullable=False, comment="动作名称")
    params = Column(JSON, default=dict, comment="动作参数")
    status = Column(String(32), default="pending", comment="状态: pending/running/success/failed/skipped")
    screenshot_path = Column(String(512), default="", comment="截图路径")
    error_message = Column(Text, default="", comment="错误信息")
    llm_decision = Column(JSON, default=dict, comment="LLM 决策记录")
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<TaskStep {self.task_id}:{self.step_index} {self.action_name} [{self.status}]>"
