"""
京麦商品发布自动化 - Thinker Agent
LLM 辅助决策：分析截图、判断状态、生成修正方案
"""
import json
from typing import Dict, Any, Optional

from agents.base import BaseAgent


class ThinkerAgent(BaseAgent):
    """思考 Agent — LLM 辅助判断与修正"""

    def __init__(self, settings=None):
        super().__init__(name="Thinker", settings=settings)

    def run(self, **kwargs) -> Dict[str, Any]:
        """入口 — 分析当前状态并给出建议"""
        question = kwargs.get("question", "")
        screenshot = kwargs.get("screenshot_path", "")
        context = kwargs.get("context", {})

        if screenshot:
            return self.analyze_screenshot(screenshot, question, context)
        elif question:
            return self.think(question, context)
        return {"success": False, "error": "需要 question 或 screenshot_path"}

    def think(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """纯文本推理"""
        if not self._llm:
            return {"success": False, "error": "LLM 未注入"}

        # 搜索相关记忆
        memories = self._recall(question, top_k=3)
        memory_text = "\n".join([f"- {m.content}" for m in memories]) if memories else "无相关记忆"

        prompt = f"""你是京麦商品发布助手的决策模块。根据以下信息回答问题。

## 当前上下文
{json.dumps(context or {}, ensure_ascii=False, indent=2)}

## 相关记忆
{memory_text}

## 问题
{question}

请用 JSON 格式回答：
{{"analysis": "分析", "decision": "决策", "action": "建议动作", "params": {{}}}}"""

        try:
            response = self._llm.invoke(prompt)
            self._remember(f"思考: {question} -> {response[:200]}", importance=0.6)
            return {"success": True, "response": response}
        except Exception as e:
            self._log("error", f"LLM 推理失败: {e}")
            return {"success": False, "error": str(e)}

    def analyze_screenshot(self, screenshot_path: str, question: str = "",
                           context: Dict[str, Any] = None) -> Dict[str, Any]:
        """截图分析"""
        if not self._llm:
            return {"success": False, "error": "LLM 未注入"}

        prompt = f"""分析这张京麦客户端截图。

## 问题
{question or "当前页面状态是什么？需要执行什么操作？"}

## 上下文
{json.dumps(context or {}, ensure_ascii=False, indent=2)}

请用 JSON 格式回答：
{{"page_status": "页面状态", "visible_elements": ["可见元素"], "next_action": "建议动作", "action_params": {{}}}}"""

        try:
            response = self._llm.invoke_multimodal(prompt, screenshot_path)
            self._remember(f"截图分析: {response[:200]}", importance=0.7)
            return {"success": True, "response": response}
        except Exception as e:
            self._log("error", f"截图分析失败: {e}")
            return {"success": False, "error": str(e)}

    def diagnose_error(self, error: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """错误诊断 — 给出修复建议"""
        return self.think(
            f"执行出错: {error}。请分析原因并给出修复方案。",
            context,
        )
