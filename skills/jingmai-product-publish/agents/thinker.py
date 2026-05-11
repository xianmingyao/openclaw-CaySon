"""
京麦商品发布自动化 - Thinker Agent
负责截图分析和问题推理。
"""
import json
from pathlib import Path
from typing import Any, Dict, Optional

from agents.base import BaseAgent


class ThinkerAgent(BaseAgent):
    """截图分析与问题推理 Agent。"""

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
            self._remember(f"思考: {question} -> {response[:200]}", importance=0.6)
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

        try:
            resolved_screenshot = self._resolve_screenshot_path(screenshot_path)
        except Exception as exc:
            self._log("error", f"截图路径无效: {exc}")
            return {"success": False, "error": str(exc)}

        prompt = f"""分析这张京麦客户端截图。请只返回 JSON。
问题:
{question or "当前页面状态是什么，需要执行什么操作？"}

上下文:
{json.dumps(context or {}, ensure_ascii=False, indent=2)}

返回格式:
{{"page_status": "...", "visible_elements": [], "next_action": "...", "action_params": {{"target_text": "", "center_x": 0, "center_y": 0, "bbox": [0,0,0,0], "drag": false}}}}"""

        try:
            raw = self._llm.invoke_multimodal(prompt, resolved_screenshot)
            response = self._enrich_visual_response(self._validate_response(raw), resolved_screenshot)
            self._remember(f"截图分析: {response[:200]}", importance=0.7)
            return {"success": True, "response": response}
        except Exception as exc:
            self._log("warning", f"截图 JSON 分析失败，尝试纯文本回退: {exc}")
            fallback_prompt = f"""请分析这张京麦截图，直接返回简洁中文，不要返回 JSON。
问题:
{question or "当前页面状态是什么，需要执行什么操作？"}

上下文:
{json.dumps(context or {}, ensure_ascii=False, indent=2)}

请至少包含三点：
1. 当前页面是什么
2. 最明显的未完成区域
3. 下一步最应该做什么"""
            try:
                response = self._enrich_visual_response(
                    self._validate_response(
                        self._llm.invoke_multimodal(fallback_prompt, resolved_screenshot),
                        allow_plain_text=True,
                    ),
                    resolved_screenshot,
                )
                self._remember(f"截图分析: {response[:200]}", importance=0.7)
                return {"success": True, "response": response}
            except Exception as fallback_exc:
                self._log("error", f"截图分析失败: {fallback_exc}")
                return {"success": False, "error": str(fallback_exc)}

    def diagnose_error(self, error: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.think(f"执行出错: {error}。请分析原因并给出修复方案。", context)

    def _resolve_screenshot_path(self, screenshot_path: str) -> str:
        raw = str(screenshot_path or "").strip()
        if not raw:
            raise FileNotFoundError("未提供截图路径")

        root = Path(__file__).resolve().parent.parent
        candidates = [
            Path(raw),
            Path.cwd() / raw,
            root / raw,
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate.resolve())

        screenshots_dir = root / "resources" / "screenshots"
        basename = Path(raw).name

        exact = screenshots_dir / basename
        if exact.exists():
            return str(exact.resolve())

        exact_matches = sorted(screenshots_dir.rglob(basename))
        if exact_matches:
            chosen = exact_matches[-1].resolve()
            self._log("warning", f"截图路径缺失，使用精确同名回退: {chosen.name}")
            return str(chosen)

        stem = Path(raw).stem
        prefix = stem.split("_")[0] if "_" in stem else stem
        if prefix:
            prefix_matches = sorted(
                screenshots_dir.glob(f"{prefix}*.png"),
                key=lambda item: item.stat().st_mtime,
            )
            if prefix_matches:
                chosen = prefix_matches[-1].resolve()
                self._log("warning", f"截图缺失，回退到同批次最新截图: {chosen.name}")
                return str(chosen)

        raise FileNotFoundError(f"截图文件不存在: {raw}")

    def _enrich_visual_response(self, response: str, screenshot_path: str) -> str:
        text = (response or "").strip()
        if not text:
            return text
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return text
        if not isinstance(payload, dict):
            return text

        payload.update(self._build_visual_diagnostics(payload, screenshot_path))
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def _build_visual_diagnostics(self, payload: Dict[str, Any], screenshot_path: str) -> Dict[str, Any]:
        actual_width = actual_height = None
        ref_width = ref_height = None
        scale_x = scale_y = None
        mapped_x = mapped_y = None

        try:
            from PIL import Image

            with Image.open(screenshot_path) as img:
                actual_width, actual_height = img.size
        except Exception:
            actual_width = actual_height = None

        try:
            from settings import get_settings

            settings = get_settings()
            ref_width = int(settings.SCREENSHOT_MAX_WIDTH)
            ref_height = int(settings.SCREENSHOT_MAX_HEIGHT)
        except Exception:
            ref_width, ref_height = 2560, 1392

        if actual_width and actual_height:
            scale_x = round(ref_width / actual_width, 4)
            scale_y = round(ref_height / actual_height, 4)

        action_params = payload.get("action_params") if isinstance(payload.get("action_params"), dict) else {}
        llm_x = action_params.get("center_x")
        llm_y = action_params.get("center_y")
        if isinstance(llm_x, (int, float)) and isinstance(llm_y, (int, float)):
            try:
                from infrastructure.locator import JingmaiLocator

                locator = JingmaiLocator(log=self.log)
                locator.find_window()
                mapped_x, mapped_y = locator.llm_to_screen(int(llm_x), int(llm_y), image_path=screenshot_path)
            except Exception:
                if actual_width and actual_height:
                    mapped_x = int(llm_x * ref_width / actual_width)
                    mapped_y = int(llm_y * ref_height / actual_height)

        return {
            "actual_vision_size": [actual_width, actual_height] if actual_width and actual_height else None,
            "scale_x": scale_x,
            "scale_y": scale_y,
            "mapped_x": mapped_x,
            "mapped_y": mapped_y,
        }

    @staticmethod
    def _validate_response(response: Any, allow_plain_text: bool = False) -> str:
        text = (response or "").strip()
        if not text:
            raise ValueError("LLM 返回为空")
        if text == "{}":
            raise ValueError("LLM 返回空对象")
        try:
            payload = json.loads(text)
            if isinstance(payload, dict) and not payload:
                raise ValueError("LLM 返回空对象")
        except json.JSONDecodeError:
            if allow_plain_text:
                return text
        return text
