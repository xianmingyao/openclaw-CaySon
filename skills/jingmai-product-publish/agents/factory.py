"""
京麦商品发布自动化 - Agent 工厂
统一创建和装配 Agent，注入所有依赖
支持关键词匹配和别名
"""
from typing import Optional, List

from agents.base import BaseAgent
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.thinker import ThinkerAgent
from infrastructure import JingmaiLogger
from memory.manager import MemoryManager
from llm.manager import LLMManager
from db import DatabaseManager


# 别名映射：支持模糊匹配
ALIASES = {
    "planner": ["planner", "plan", "规划", "计划", "planning"],
    "executor": ["executor", "execute", "执行", "exec", "running", "runner"],
    "thinker": ["thinker", "think", "思考", "分析", "analyze", "analysis"],
}


class AgentFactory:
    """Agent 工厂 — 创建装配好的 Agent，支持别名匹配"""

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
            llm = None
            try:
                llm = self._ensure_llm()
            except Exception:
                pass
            self._memory = MemoryManager(self.settings, llm=llm)
        return self._memory

    def _ensure_llm(self) -> LLMManager:
        if self._llm is None:
            self._llm = LLMManager(self.settings)
        return self._llm

    def _ensure_db(self) -> DatabaseManager:
        if self._db is None:
            self._db = DatabaseManager(settings=self.settings)
            self._db.create_tables()
        return self._db

    def _inject(self, agent: BaseAgent) -> BaseAgent:
        """注入所有依赖"""
        agent.set_logger(self._ensure_logger())
        agent.set_memory(self._ensure_memory())
        agent.set_llm(self._ensure_llm())
        agent.set_db(self._ensure_db())
        return agent

    # ── 创建方法 ──────────────────────────────────

    def create_planner(self) -> PlannerAgent:
        """创建规划 Agent"""
        return self._inject(PlannerAgent(self.settings))

    def create_executor(self) -> ExecutorAgent:
        """创建执行 Agent"""
        return self._inject(ExecutorAgent(self.settings))

    def create_thinker(self) -> ThinkerAgent:
        """创建思考 Agent"""
        return self._inject(ThinkerAgent(self.settings))

    # ── 别名匹配 ──────────────────────────────────

    @staticmethod
    def _resolve_agent_type(agent_type: str) -> str:
        """将输入解析为标准 Agent 类型（支持别名和模糊匹配）"""
        agent_type_lower = agent_type.lower().strip()

        # 精确匹配
        if agent_type_lower in ("planner", "executor", "thinker"):
            return agent_type_lower

        # 别名匹配
        for standard_type, aliases in ALIASES.items():
            if agent_type_lower in aliases:
                return standard_type

        # 模糊匹配：包含关系
        for standard_type, aliases in ALIASES.items():
            for alias in aliases:
                if alias in agent_type_lower or agent_type_lower in alias:
                    return standard_type

        return ""

    @staticmethod
    def list_available() -> List[str]:
        """列出所有可用的 Agent 类型及其别名"""
        result = []
        for standard_type, aliases in ALIASES.items():
            result.append(f"{standard_type}: {', '.join(aliases[:3])}")
        return result

    def create(self, agent_type: str) -> BaseAgent:
        """按名称或别名创建 Agent"""
        resolved = self._resolve_agent_type(agent_type)
        if not resolved:
            available = ", ".join(ALIASES.keys())
            raise ValueError(f"未知 Agent 类型: '{agent_type}'，可选: {available}")

        mapping = {
            "planner": self.create_planner,
            "executor": self.create_executor,
            "thinker": self.create_thinker,
        }
        return mapping[resolved]()
