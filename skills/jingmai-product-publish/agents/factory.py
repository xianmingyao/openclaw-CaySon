"""
京麦商品发布自动化 - Agent 工厂
统一创建和装配 Agent，注入所有依赖
"""
from typing import Optional

from agents.base import BaseAgent
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.thinker import ThinkerAgent
from infrastructure import JingmaiLogger
from memory.manager import MemoryManager
from llm.manager import LLMManager
from db import DatabaseManager


class AgentFactory:
    """Agent 工厂 — 创建装配好的 Agent"""

    def __init__(self, settings=None):
        if settings is None:
            from settings import get_settings
            settings = get_settings()
        self.settings = settings

        self._logger: Optional[JingmaiLogger] = None
        self._memory: Optional[MemoryManager] = None
        self._llm: Optional[LLMManager] = None
        self._db: Optional[DatabaseManager] = None

    def _ensure_logger(self) -> JingmaiLogger:
        if self._logger is None:
            self._logger = JingmaiLogger(log_dir=self.settings.LOG_DIR)
        return self._logger

    def _ensure_memory(self) -> MemoryManager:
        if self._memory is None:
            self._memory = MemoryManager(self.settings)
        return self._memory

    def _ensure_llm(self) -> LLMManager:
        if self._llm is None:
            self._llm = LLMManager(self.settings)
            # 连接 LLM embed 到 Memory 长期存储
            memory = self._ensure_memory()
            memory.set_embed_fn(self._llm.embed_text)
        return self._llm

    def _ensure_db(self) -> DatabaseManager:
        if self._db is None:
            self._db = DatabaseManager(
                mysql_url=self.settings.MYSQL_URL,
                sqlite_url=self.settings.SQLITE_URL,
            )
            self._db.create_tables()
        return self._db

    def _inject(self, agent: BaseAgent) -> BaseAgent:
        """注入所有依赖"""
        agent.set_logger(self._ensure_logger())
        agent.set_memory(self._ensure_memory())
        agent.set_llm(self._ensure_llm())
        agent.set_db(self._ensure_db())
        return agent

    def create_planner(self) -> PlannerAgent:
        """创建规划 Agent"""
        return self._inject(PlannerAgent(self.settings))

    def create_executor(self) -> ExecutorAgent:
        """创建执行 Agent"""
        return self._inject(ExecutorAgent(self.settings))

    def create_thinker(self) -> ThinkerAgent:
        """创建思考 Agent"""
        return self._inject(ThinkerAgent(self.settings))

    def create(self, agent_type: str) -> BaseAgent:
        """按名称创建 Agent"""
        mapping = {
            "planner": self.create_planner,
            "executor": self.create_executor,
            "thinker": self.create_thinker,
        }
        factory_fn = mapping.get(agent_type)
        if not factory_fn:
            raise ValueError(f"未知 Agent 类型: {agent_type}，可选: {list(mapping.keys())}")
        return factory_fn()
