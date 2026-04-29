"""
京麦商品发布自动化 - Agent 基类
所有 Agent 的公共接口和安全约束
"""
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from infrastructure import JingmaiLogger, CircuitBreaker
from memory.manager import MemoryManager
from llm.manager import LLMManager
from db import DatabaseManager


@dataclass
class AgentState:
    """Agent 运行状态"""
    name: str = ""
    status: str = "idle"  # idle / running / success / failed / paused
    current_action: str = ""
    step_index: int = 0
    total_steps: int = 0
    error_count: int = 0
    last_error: str = ""
    started_at: float = 0.0
    finished_at: float = 0.0

    @property
    def elapsed(self) -> float:
        if self.finished_at and self.started_at:
            return self.finished_at - self.started_at
        if self.started_at:
            return time.time() - self.started_at
        return 0.0


class BaseAgent(ABC):
    """Agent 基类 — 安全约束 + 公共能力"""

    def __init__(self, name: str, settings=None):
        self.name = name
        self.state = AgentState(name=name)

        if settings is None:
            from settings import get_settings
            settings = get_settings()
        self.settings = settings

        self._logger: Optional[JingmaiLogger] = None
        self._memory: Optional[MemoryManager] = None
        self._llm: Optional[LLMManager] = None
        self._db: Optional[DatabaseManager] = None
        self._circuit_breaker = CircuitBreaker(
            base_delay=settings.CIRCUIT_BREAKER_BASE_DELAY,
        )

        # 安全约束
        self._max_depth = settings.MAX_RECURSION_DEPTH
        self._max_same_action = settings.MAX_SAME_ACTION_REPEATS
        self._timeout = settings.EXECUTION_TIMEOUT
        self._action_history: List[str] = []

    # ── 依赖注入（由 factory 统一设置）──

    def set_logger(self, logger: JingmaiLogger):
        self._logger = logger

    def set_memory(self, memory: MemoryManager):
        self._memory = memory

    def set_llm(self, llm: LLMManager):
        self._llm = llm

    def set_db(self, db: DatabaseManager):
        self._db = db

    # ── 生命周期 ─────────────────────────────────

    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """Agent 主入口，子类必须实现"""
        pass

    def start(self):
        """开始执行"""
        self.state.status = "running"
        self.state.started_at = time.time()

    def finish(self, success: bool, error: str = ""):
        """结束执行"""
        self.state.status = "success" if success else "failed"
        self.state.finished_at = time.time()
        if error:
            self.state.last_error = error

    # ── 安全检查 ─────────────────────────────────

    def _check_safety(self, action_name: str) -> bool:
        """安全检查：递归深度 + 重复动作"""
        # 重复动作检测
        recent = self._action_history[-self._max_same_action:]
        if len(recent) >= self._max_same_action and all(a == action_name for a in recent):
            self._log("error", f"安全拦截：连续 {self._max_same_action} 次相同动作 '{action_name}'")
            return False

        # 递归深度检测
        if len(self._action_history) >= self._max_depth:
            self._log("error", f"安全拦截：超过最大步数 {self._max_depth}")
            return False

        # 超时检测
        if self.state.started_at and (time.time() - self.state.started_at) > self._timeout:
            self._log("error", f"安全拦截：超过超时 {self._timeout}s")
            return False

        self._action_history.append(action_name)
        return True

    # ── 日志 ─────────────────────────────────────

    def _log(self, level: str, msg: str):
        """统一日志"""
        text = f"[{self.name}] {msg}"
        if self._logger:
            getattr(self._logger, level, self._logger.info)(text)
        else:
            print(text)

    # ── 记忆 ─────────────────────────────────────

    def _remember(self, content: str, importance: float = 0.5, **meta):
        """写入工作记忆"""
        if self._memory:
            self._memory.remember_working(content, importance, **meta)

    def _recall(self, query: str, top_k: int = 3):
        """搜索记忆"""
        if self._memory:
            return self._memory.recall(query, top_k)
        return []
