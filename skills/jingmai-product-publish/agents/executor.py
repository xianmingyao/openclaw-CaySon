"""
京麦商品发布自动化 - Executor Agent
动作执行引擎，复用 Processor Pipeline + ActionRegistry
"""
from typing import Dict, Any, List, Optional

from agents.base import BaseAgent
from actions import ActionRegistry


class ExecutorAgent(BaseAgent):
    """执行 Agent — 按计划逐步执行动作"""

    def __init__(self, settings=None):
        super().__init__(name="Executor", settings=settings)
        self._plan: List[Dict[str, Any]] = []
        self._step_index: int = 0

    def run(self, plan: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        执行计划
        plan: [{"action": "fill_text", "params": {...}}, ...]
        """
        self._plan = plan
        self._step_index = 0
        self.start()
        self._log("info", f"开始执行 {len(plan)} 个步骤")

        results = []
        for i, step in enumerate(plan):
            self._step_index = i
            self.state.step_index = i + 1
            self.state.total_steps = len(plan)
            action_name = step.get("action", "")
            params = step.get("params", {})

            self._log("info", f"步骤 {i+1}/{len(plan)}: {action_name}")
            self.state.current_action = action_name

            # 安全检查
            if not self._check_safety(action_name):
                self.finish(False, f"安全拦截: {action_name}")
                return {"success": False, "results": results, "error": "安全拦截"}

            # 熔断检查
            if not self._circuit_breaker.can_execute():
                self.finish(False, "熔断器开启，暂停执行")
                return {"success": False, "results": results, "error": "熔断器开启"}

            # 执行动作
            try:
                result = ActionRegistry.execute(action_name, **params)
                step_result = {
                    "step": i + 1,
                    "action": action_name,
                    "success": True,
                    "result": result,
                }
                self._circuit_breaker.record_success()
                self._log("info", f"步骤 {i+1} 完成")
            except Exception as e:
                step_result = {
                    "step": i + 1,
                    "action": action_name,
                    "success": False,
                    "error": str(e),
                }
                self._circuit_breaker.record_failure()
                self._log("error", f"步骤 {i+1} 失败: {e}")

                # 记录到 DB
                if self._db:
                    self._db.update_step_status(
                        task_id=kwargs.get("task_id", ""),
                        step_index=i,
                        status="failed",
                        error=str(e),
                    )

                # 失败策略：记录后继续（非 fail-fast）
                if step.get("required", True):
                    results.append(step_result)
                    self.finish(False, f"步骤 {i+1} 失败: {e}")
                    return {"success": False, "results": results, "error": str(e)}

            results.append(step_result)

            # 记忆关键步骤
            self._remember(
                f"步骤 {i+1} {action_name}: {'成功' if step_result['success'] else '失败'}",
                importance=0.7 if not step_result.get("success", True) else 0.3,
            )

        self.finish(True)
        self._log("info", f"执行完成，共 {len(results)} 步")
        return {"success": True, "results": results}

    @property
    def progress(self) -> str:
        """进度描述"""
        if not self.state.started_at:
            return "未开始"
        return f"步骤 {self.state.step_index}/{self.state.total_steps} - {self.state.current_action}"
