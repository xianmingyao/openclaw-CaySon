"""
京麦商品发布自动化 - Thinker Agent
负责截图分析和问题推理。
"""
import json
from typing import Any, Dict, Optional

from agents.base import BaseAgent


class ThinkerAgent(BaseAgent):
    """思考 Agent。"""

    def __init__(self, settings=None):
        super().__init__(name="Thinker", settings=settings)

    def run(self, **kwargs) -> Dict[str, Any]:
        question = kwargs.get("question", "")
        screenshot = kwargs.get("screenshot_path", "")
        context = kwargs.get("context", {})

        if screenshot:
            return self.analyze_screenshot(screenshot, question, context)
        if question:
            return self.think(question, context)
        return {"success": False, "error": "需要 question 或 screenshot_path"}

    def think(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self._llm:
            return {"success": False, "error": "LLM 未注入"}

        memories = self._recall(question, top_k=3)
        memory_text = "\n".join(f"- {m.content}" for m in memories) if memories else "无相关记忆"
        prompt = f"""你是京麦商品发布助手的决策模块。请只返回 JSON。

上下文:
{json.dumps(context or {}, ensure_ascii=False, indent=2)}

相关记忆:
{memory_text}

问题:
{question}

返回格式:
{{"analysis": "...", "decision": "...", "action": "...", "params": {{}}}}"""

        try:
            response = self._validate_response(self._llm.invoke(prompt))
            self._remember(f"思考 {question} -> {response[:200]}", importance=0.6)
            return {"success": True, "response": response}
        except Exception as exc:
            self._log("error", f"LLM 推理失败: {exc}")
            return {"success": False, "error": str(exc)}

    def analyze_screenshot(
        self,
        screenshot_path: str,
        question: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self._llm:
            return {"success": False, "error": "LLM 未注入"}

        prompt = f"""分析这张京麦客户端截图。请只返回 JSON。

问题:
{question or "当前页面状态是什么，需要执行什么操作？"}

上下文:
{json.dumps(context or {}, ensure_ascii=False, indent=2)}

返回格式:
{{"page_status": "...", "visible_elements": [], "next_action": "...", "action_params": {{}}}}"""

        try:
            response = self._validate_response(self._llm.invoke_multimodal(prompt, screenshot_path))
            self._remember(f"截图分析: {response[:200]}", importance=0.7)
            return {"success": True, "response": response}
        except Exception as exc:
            self._log("error", f"截图分析失败: {exc}")
            return {"success": False, "error": str(exc)}

    def diagnose_error(self, error: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.think(f"执行出错: {error}。请分析原因并给出修复方案。", context)

    @staticmethod
    def _validate_response(response: Any) -> str:
        text = (response or "").strip()
        if not text:
            raise ValueError("LLM 返回为空")
        return text
