"""
京麦商品发布自动化 - Agent 基类
所有 Agent 的公共接口、安全约束、Think-Act-Observe-Reflect 循环
"""
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from infrastructure import JingmaiLogger, CircuitBreaker
from memory.manager import MemoryManager
from memory.base import MemoryType
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
    """Agent 基类 — 安全约束 + Think-Act-Observe-Reflect 循环"""

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

    # ── Think-Act-Observe-Reflect 循环 ────────────

    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Think 阶段：读取记忆 + LLM 分析，决定下一步动作
        记忆参与决策：检索相关历史经验注入 LLM 上下文
        """
        # 1. 从记忆中检索相关上下文
        memory_hints = []
        action_name = context.get("action", "")
        if self._memory and action_name:
            try:
                memories = self._recall(f"步骤 {action_name}", top_k=3)
                for m in memories:
                    memory_hints.append(f"- [{m.type.value}] {m.content[:80]}")
            except Exception:
                pass

        memory_block = "\n".join(memory_hints) if memory_hints else "无相关记忆"

        # 2. 用 LLM 分析（注入记忆上下文）
        if self._llm:
            try:
                prompt = f"""你是京麦商品发布自动化 Agent [{self.name}]。
当前状态：步骤 {self.state.step_index}/{self.state.total_steps}
当前动作：{self.state.current_action}
上下文：{context}

相关历史记忆：
{memory_block}

请分析当前状态，决定下一步最优动作。返回 JSON：
{{"next_action": "动作名", "reason": "原因", "confidence": 0.0-1.0}}"""
                response = self._llm.invoke(prompt)
                import json
                return json.loads(response)
            except Exception:
                pass

        # 3. 降级：记忆影响决策（有失败记忆时降低 confidence）
        confidence = 0.5
        if memory_hints and any("失败" in h for h in memory_hints):
            confidence = 0.3

        return {"next_action": context.get("action", ""), "reason": "降级模式", "confidence": confidence}

    def act(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Act 阶段：执行动作
        子类必须覆写以定义具体执行逻辑
        """
        return {"success": False, "error": "act() 未实现"}

    def observe(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Observe 阶段：收集执行结果和环境反馈
        """
        observation = {
            "action_success": action_result.get("success", False),
            "timestamp": time.time(),
            "error": action_result.get("error", ""),
            "result": action_result,
        }

        # 截图记录当前状态（如果可能）
        if self._logger:
            self._log("debug", f"观察结果: {'成功' if observation['action_success'] else '失败'}")

        return observation

    def reflect(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reflect 阶段：评估结果，决定是否需要重试或调整
        - 步骤结果写入短期记忆（会话状态追踪）
        - 失败时写入长期记忆（经验沉淀）
        """
        success = observation.get("action_success", False)
        reflection = {
            "should_retry": False,
            "should_adjust": False,
            "lesson": "",
        }

        action = self.state.current_action
        step_info = f"步骤 {self.state.step_index}/{self.state.total_steps} {action}"

        # 步骤结果写入短期记忆
        if self._memory:
            try:
                self._memory.remember_short_term(
                    f"[{self.name}] {step_info}: {'成功' if success else '失败'}",
                    importance=0.5 if success else 0.7,
                    agent=self.name,
                    action=action,
                    success=success,
                )
            except Exception:
                pass

        if not success:
            error = observation.get("error", "未知错误")
            self.state.error_count += 1
            reflection["lesson"] = f"动作失败: {error}"

            # 失败教训写入长期记忆（经验沉淀）
            if self._memory:
                try:
                    self._memory.remember_long_term(
                        f"[{self.name}] 失败教训: {action} → {error}",
                        importance=0.8,
                        agent=self.name,
                        action=action,
                        error=error,
                    )
                except Exception:
                    pass

            # 错误次数 < 3 时建议重试
            if self.state.error_count < 3:
                reflection["should_retry"] = True

        return reflection

    def run_tao_loop(self, steps: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Think-Act-Observe-Reflect 主循环
        遍历步骤列表，每步执行完整的 4 阶段循环
        """
        self._plan = steps
        self._step_index = 0
        self.start()
        self._log("info", f"开始 TAO 循环，{len(steps)} 个步骤")

        results = []
        for i, step in enumerate(steps):
            self._step_index = i
            self.state.step_index = i + 1
            self.state.total_steps = len(steps)
            action_name = step.get("action", "")
            params = step.get("params", {})
            self.state.current_action = action_name

            self._log("info", f"步骤 {i+1}/{len(steps)}: {action_name}")

            # 安全检查
            if not self._check_safety(action_name):
                self.finish(False, f"安全拦截: {action_name}")
                return {"success": False, "results": results, "error": "安全拦截"}

            # 熔断检查
            if not self._circuit_breaker.can_execute():
                self.finish(False, "熔断器开启，暂停执行")
                return {"success": False, "results": results, "error": "熔断器开启"}

            # ── Think ──
            think_result = self.think({
                "action": action_name,
                "params": params,
                "step_index": i,
                "total_steps": len(steps),
                "previous_results": results[-3:] if results else [],
            })

            # ── Act ──
            try:
                act_result = self.act(action_name, params)
                self._circuit_breaker.record_success()
            except Exception as e:
                act_result = {"success": False, "error": str(e)}
                self._circuit_breaker.record_failure()
                self._log("error", f"步骤 {i+1} 执行异常: {e}")

            # ── Observe ──
            observation = self.observe(act_result)

            # ── Reflect ──
            reflection = self.reflect(observation)

            # 失败重试逻辑
            if reflection.get("should_retry") and not observation.get("action_success"):
                self._log("info", f"步骤 {i+1} 重试中...")
                try:
                    retry_result = self.act(action_name, params)
                    retry_obs = self.observe(retry_result)
                    if retry_obs.get("action_success"):
                        act_result = retry_result
                        observation = retry_obs
                except Exception:
                    pass

            # 组装步骤结果
            step_result = {
                "step": i + 1,
                "action": action_name,
                "success": observation.get("action_success", False),
                "result": act_result,
            }
            results.append(step_result)

            # 记忆关键步骤
            self._remember(
                f"步骤 {i+1} {action_name}: {'成功' if step_result['success'] else '失败'}",
                importance=0.7 if not step_result.get("success") else 0.3,
            )

            # 必需步骤失败则中止
            if not step_result["success"] and step.get("required", True):
                self.finish(False, f"步骤 {i+1} 失败: {act_result.get('error', '')}")
                return {"success": False, "results": results, "error": act_result.get("error", "")}

        self.finish(True)
        self._log("info", f"TAO 循环完成，共 {len(results)} 步")
        return {"success": True, "results": results}

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
        """写入短期记忆（步骤记录持久化）"""
        if self._memory:
            self._memory.remember_short_term(content, importance, **meta)

    def _recall(self, query: str, top_k: int = 3):
        """搜索记忆"""
        if self._memory:
            return self._memory.recall(query, top_k)
        return []
