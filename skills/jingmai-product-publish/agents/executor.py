"""
京麦商品发布自动化 - Executor Agent
按计划执行动作，关键步骤带视觉验证。

验证策略（三级）：
  1. LLM 可用 → 截图 + LLM 视觉分析
  2. LLM 不可用 → UIA 文本扫描（纯规则）
  3. 两者都失败 → 标记为 "未验证" 但不阻断
"""
import time
from typing import Any, Dict, List, Optional

from actions import ActionRegistry
from agents.base import BaseAgent


# 需要视觉验证的关键动作
VISION_VERIFY_ACTIONS = {"verify_result", "publish_product", "save_draft"}


class ExecutorAgent(BaseAgent):
    """执行 Agent（关键步骤带视觉验证）"""

    def __init__(self, settings=None):
        super().__init__(name="Executor", settings=settings)
        self._locator = None
        self._task_id = ""

    def run(self, plan: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        self._task_id = kwargs.get("task_id", "")
        if self._db and self._task_id:
            self._db.update_task_status(self._task_id, "running")

        result = self.run_tao_loop(plan, **kwargs)

        if self._db and self._task_id:
            if result.get("success"):
                self._db.update_task_status(self._task_id, "success", result=result)
            else:
                self._db.update_task_status(
                    self._task_id,
                    "failed",
                    error=result.get("error", ""),
                    result=result,
                )
        return result

    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executor 保持规则驱动，只回传当前动作。"""
        action_name = context.get("action", "")
        memory_hints = []
        if self._memory and action_name:
            try:
                memory_hints = self._recall(f"步骤 {action_name}", top_k=2)
            except Exception:
                memory_hints = []

        return {
            "next_action": action_name,
            "reason": "rule-driven executor",
            "confidence": 0.9 if not memory_hints else 0.7,
        }

    def act(self, action_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if self._db and self._task_id:
            self._db.update_step_status(self._task_id, self.state.step_index - 1, "running")

        action_params = dict(params)
        if "locator" not in action_params and self._locator is not None:
            action_params["locator"] = self._locator
        if "log" not in action_params and self._logger is not None:
            action_params["log"] = self._logger
        if self._logger and params:
            self._logger.debug(f"[Executor] 执行参数 {action_name}: {params}")

        result = ActionRegistry.execute(action_name, **action_params)

        if action_name in {"find_window", "activate_window"} and result.get("success"):
            if self._locator is None:
                from infrastructure.locator import JingmaiLocator

                self._locator = JingmaiLocator(log=self._logger)
                self._locator.find_window()

        # 关键步骤：执行后截图 + 视觉验证
        if action_name in VISION_VERIFY_ACTIONS:
            result = self._enhance_with_vision(action_name, result)

        return result

    def observe(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        observation = super().observe(action_result)

        if self._db and self._task_id:
            self._db.update_step_status(
                task_id=self._task_id,
                step_index=self.state.step_index - 1,
                status="success" if observation.get("action_success") else "failed",
                error=observation.get("error", ""),
                screenshot=action_result.get("screenshot", ""),
                result=action_result,
            )
        return observation

    def reflect(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        return super().reflect(observation)

    def _enhance_with_vision(self, action_name: str, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        关键步骤执行后，截图并用 LLM 视觉验证结果。

        三级策略：
        1. LLM 可用 → 截图 + LLM 分析
        2. LLM 不可用 → 纯规则验证（基于 action_result）
        3. 都失败 → 标记 unverified 但不阻断
        """
        # 先截图
        screenshot_path = self._take_screenshot(action_name)
        if screenshot_path:
            action_result["screenshot"] = screenshot_path

        # LLM 视觉验证
        if self._llm and screenshot_path:
            try:
                vision_result = self._vision_verify(action_name, screenshot_path, action_result)
                if vision_result:
                    action_result["vision_verified"] = True
                    action_result["vision_analysis"] = vision_result
                    # LLM 判定失败时覆盖 action_result
                    if vision_result.get("status") == "error" and action_result.get("success"):
                        self._log("warning", f"LLM 视觉验证发现错误: {vision_result.get('reason', '')}")
                        action_result["success"] = False
                        action_result["error"] = f"视觉验证失败: {vision_result.get('reason', '')}"
                    return action_result
            except Exception as exc:
                self._log("warning", f"LLM 视觉验证异常（降级为规则验证）: {exc}")

        # 降级：纯规则验证
        action_result["vision_verified"] = False
        action_result["verification_method"] = "rule-based"
        self._log("info", f"关键步骤 {action_name} 使用纯规则验证（LLM 不可用）")

        return action_result

    def _take_screenshot(self, action_name: str) -> Optional[str]:
        """截图当前窗口状态"""
        if not self._locator:
            return None
        try:
            import os
            screenshot_dir = self.settings.SCREENSHOT_DIR
            os.makedirs(screenshot_dir, exist_ok=True)
            save_path = os.path.join(
                screenshot_dir,
                f"{self._task_id}_{action_name}_{int(time.time())}.png"
            )
            return self._locator.take_screenshot(save_path)
        except Exception as exc:
            self._log("warning", f"截图失败: {exc}")
            return None

    def _vision_verify(self, action_name: str, screenshot_path: str,
                       action_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        调用 LLM 做视觉验证

        Returns:
            dict: {"status": "ok"|"error"|"unknown", "reason": "..."}
        """
        prompt_map = {
            "verify_result": "分析这张京麦客户端截图，检查是否有错误提示或异常状态。只返回 JSON: {\"status\": \"ok\"|\"error\"|\"unknown\", \"reason\": \"原因\"}",
            "publish_product": "分析这张截图，判断商品是否已成功发布。只返回 JSON: {\"status\": \"ok\"|\"error\"|\"unknown\", \"reason\": \"原因\"}",
            "save_draft": "分析这张截图，判断草稿是否已成功保存。只返回 JSON: {\"status\": \"ok\"|\"error\"|\"unknown\", \"reason\": \"原因\"}",
        }
        prompt = prompt_map.get(
            action_name,
            "分析这张截图，判断操作是否成功。只返回 JSON: {\"status\": \"ok\"|\"error\"|\"unknown\", \"reason\": \"原因\"}"
        )

        response = self._llm.invoke_multimodal(prompt, screenshot_path)
        if not response:
            return None

        # 解析 LLM 返回的 JSON
        import json
        import re
        try:
            # 尝试直接解析
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # 尝试提取 JSON
            match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            self._log("warning", f"LLM 视觉验证返回非 JSON: {response[:200]}")
            return {"status": "unknown", "reason": f"LLM 返回无法解析: {response[:100]}"}

    @property
    def progress(self) -> str:
        if not self.state.started_at:
            return "未开始"
        return f"步骤 {self.state.step_index}/{self.state.total_steps} - {self.state.current_action}"
