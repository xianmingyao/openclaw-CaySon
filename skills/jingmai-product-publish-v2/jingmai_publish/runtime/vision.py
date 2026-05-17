"""Ollama Vision Provider — 截图分析、元素定位、前后对比。

BL-092: 为 Phase C 视觉校验提供 VLM 能力。
- 输入：截图路径 + 分析提示词
- 输出：结构化的 VisionAnalysis（页面状态、控件候选、bbox/point、文本内容）
- 降级：Ollama 不可用时返回 error 状态，不阻塞主流程
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import base64
import json
import time
from typing import Any

import requests


# ── 结构化输出 ──────────────────────────────────────────────────────


@dataclass(slots=True)
class VisionAnalysis:
    """视觉分析结果。

    由 OllamaVisionProvider 产出，供 Reflection 和 Grounding 消费。
    """

    success: bool
    page_state: str | None = None           # 页面状态描述
    elements: list[dict[str, Any]] = field(default_factory=list)  # 控件候选列表
    text_content: str = ""                   # 页面文本内容
    bbox: tuple[int, int, int, int] | None = None  # 目标元素边界框 (left, top, right, bottom)
    point: tuple[int, int] | None = None     # 目标元素中心点 (x, y)
    confidence: float = 0.0                  # 分析置信度
    raw_response: str = ""                   # 模型原始输出
    model: str = ""                          # 使用的模型名
    elapsed_ms: float = 0.0                  # 调用耗时
    error: str | None = None                 # 错误信息

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "page_state": self.page_state,
            "elements": self.elements,
            "text_content": self.text_content,
            "bbox": list(self.bbox) if self.bbox else None,
            "point": list(self.point) if self.point else None,
            "confidence": self.confidence,
            "model": self.model,
            "elapsed_ms": self.elapsed_ms,
            "error": self.error,
        }


# ── Ollama Vision Provider ─────────────────────────────────────────


class OllamaVisionProvider:
    """通过 Ollama REST API 调用视觉语言模型分析截图。

    配置来源：
    - OLLAMA_BASE_URL: Ollama 服务地址（默认 http://localhost:11434）
    - OLLAMA_MODEL: 视觉模型名称（默认 qwen3-vl:8b）
    - VLLM_BASE_URL / VLLM_MODEL: 二级回退（vLLM 本地模型）

    降级策略：
    1. Ollama 不可用 → 尝试 vLLM 回退
    2. vLLM 也不可用 → 返回 error 状态（不抛异常）
    3. 模型返回非结构化输出 → 尽力解析，标记低置信度
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3-vl:8b",
        timeout: int = 120,
        fallback_base_url: str | None = None,
        fallback_model: str | None = None,
        max_image_size: int = 2048,  # 图片最大边长（像素），超过则等比缩放
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.fallback_base_url = fallback_base_url
        self.fallback_model = fallback_model
        self.max_image_size = max_image_size

    # ── 公开 API ─────────────────────────────────────────────────

    def analyze_screenshot(
        self,
        image_path: str | Path,
        prompt: str | None = None,
    ) -> VisionAnalysis:
        """分析单张截图，返回结构化视觉分析。

        参数:
            image_path: 截图文件路径
            prompt: 自定义分析提示词。默认使用通用页面分析提示词。
        """
        return self._call_vision_api(
            image_path=image_path,
            system_prompt=prompt or self._default_analysis_prompt(),
            parse_func=self._parse_analysis_response,
        )

    def compare_screenshots(
        self,
        before_path: str | Path,
        after_path: str | Path,
        prompt: str | None = None,
    ) -> VisionAnalysis:
        """对比两张截图，识别变化。

        用于 before/after 截图差异分析，判断动作是否成功。
        """
        return self._call_vision_api(
            image_path=before_path,
            second_image_path=after_path,
            system_prompt=prompt or self._default_comparison_prompt(),
            parse_func=self._parse_comparison_response,
        )

    def locate_element(
        self,
        image_path: str | Path,
        description: str,
    ) -> VisionAnalysis:
        """在截图中定位指定元素，返回 bbox/point。

        参数:
            image_path: 截图路径
            description: 目标元素的自然语言描述（如 "保存草稿按钮"）
        """
        prompt = self._default_location_prompt(description)
        return self._call_vision_api(
            image_path=image_path,
            system_prompt=prompt,
            parse_func=self._parse_location_response,
        )

    # ── 内部调用 ─────────────────────────────────────────────────

    def _call_vision_api(
        self,
        image_path: str | Path,
        system_prompt: str,
        second_image_path: str | Path | None = None,
        parse_func: Any = None,
    ) -> VisionAnalysis:
        """统一的 Ollama /chat API 调用封装。

        流程：
        1. 加载并编码图片为 base64
        2. 构造 Ollama chat 消息
        3. 调用 /api/chat，超时重试一次
        4. 解析响应为 VisionAnalysis
        5. 失败时尝试 vLLM 回退
        """
        start = time.perf_counter()
        image_path = Path(image_path)

        if not image_path.exists():
            return VisionAnalysis(
                success=False,
                error=f"截图文件不存在: {image_path}",
                elapsed_ms=(time.perf_counter() - start) * 1000,
            )

        try:
            images_b64 = [self._encode_image(image_path)]
            if second_image_path:
                second_path = Path(second_image_path)
                if second_path.exists():
                    images_b64.append(self._encode_image(second_path))
                else:
                    return VisionAnalysis(
                        success=False,
                        error=f"第二张截图不存在: {second_path}",
                        elapsed_ms=(time.perf_counter() - start) * 1000,
                    )
        except Exception as exc:
            return VisionAnalysis(
                success=False,
                error=f"图片编码失败: {exc}",
                elapsed_ms=(time.perf_counter() - start) * 1000,
            )

        # 构造消息（支持单图/双图）
        content_parts: list[dict[str, Any]] = []
        for img_b64 in images_b64:
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_b64}"},
            })
        content_parts.append({"type": "text", "text": "请按JSON格式输出分析结果。"})

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content_parts},
        ]

        # 尝试 Ollama
        response_text = self._try_ollama_chat(messages)
        model_used = self.model

        # Ollama 失败 → 尝试 vLLM 回退
        if response_text is None and self.fallback_base_url:
            response_text = self._try_vllm_chat(messages)
            model_used = self.fallback_model or "vllm-fallback"

        elapsed = (time.perf_counter() - start) * 1000

        if response_text is None:
            return VisionAnalysis(
                success=False,
                error="Ollama 和 vLLM 回退均不可用",
                elapsed_ms=elapsed,
            )

        # 解析响应
        if parse_func:
            result = parse_func(response_text)
        else:
            result = self._parse_analysis_response(response_text)

        result.model = model_used
        result.elapsed_ms = elapsed
        result.raw_response = response_text
        return result

    # ── Ollama / vLLM HTTP 调用 ──────────────────────────────────

    def _try_ollama_chat(self, messages: list[dict]) -> str | None:
        """调用 Ollama /api/chat，失败返回 None。"""
        try:
            resp = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0.1},
                },
                timeout=self.timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("message", {}).get("content", "")
        except (requests.ConnectionError, requests.Timeout):
            pass  # 回退到 vLLM 或返回 None
        except Exception:
            pass
        return None

    def _try_vllm_chat(self, messages: list[dict]) -> str | None:
        """调用 vLLM OpenAI-compatible /chat/completions，失败返回 None。"""
        if not self.fallback_base_url:
            return None
        try:
            # vLLM 使用 OpenAI 兼容格式，需要转换图片消息
            vllm_messages = self._convert_to_openai_format(messages)
            resp = requests.post(
                f"{self.fallback_base_url.rstrip('/')}/v1/chat/completions",
                json={
                    "model": self.fallback_model or "default",
                    "messages": vllm_messages,
                    "temperature": 0.1,
                    "max_tokens": 1024,
                },
                timeout=self.timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except (requests.ConnectionError, requests.Timeout):
            pass
        except Exception:
            pass
        return None

    @staticmethod
    def _convert_to_openai_format(messages: list[dict]) -> list[dict]:
        """将 Ollama 格式消息转为 OpenAI 兼容格式。

        Ollama 的 image_url 格式和 OpenAI 略有不同。
        """
        converted = []
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                converted.append(msg)
            elif isinstance(content, list):
                # 转换 content parts
                openai_content = []
                for part in content:
                    if part.get("type") == "image_url":
                        openai_content.append({
                            "type": "image_url",
                            "image_url": part["image_url"],
                        })
                    elif part.get("type") == "text":
                        openai_content.append(part)
                converted.append({"role": msg["role"], "content": openai_content})
        return converted

    # ── 图片编码 ─────────────────────────────────────────────────

    def _encode_image(self, image_path: Path) -> str:
        """将图片文件编码为 base64 字符串，必要时缩放。"""
        from PIL import Image
        img = Image.open(image_path)

        # 如果图片过大，等比缩放
        if max(img.size) > self.max_image_size:
            ratio = self.max_image_size / max(img.size)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # 转为 PNG base64（JPEG 截图也转 PNG 保证质量）
        import io
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    # ── 提示词模板 ───────────────────────────────────────────────

    @staticmethod
    def _default_analysis_prompt() -> str:
        return """你是一个UI自动化视觉分析器。分析给定的京麦商品发布页面截图，按JSON格式输出：

{
  "page_state": "当前页面状态描述（如: main_image_uploaded, form_filled, draft_saved, error_displayed, category_selection, basic_info, sku_info, image_upload, detail_editor, logistics, draft_list）",
  "text_content": "页面上可见的所有文本内容摘要",
  "elements": [
    {
      "type": "button/input/image/text/error/checkbox/select",
      "description": "元素描述",
      "text": "元素的文本内容",
      "bbox": [left, top, right, bottom],
      "state": "enabled/disabled/selected/visible/hidden"
    }
  ],
  "issues": ["发现的问题列表"],
  "confidence": 0.0到1.0之间的置信度
}

注意：
- bbox坐标使用相对比例（0-1），例如 [0.1, 0.2, 0.3, 0.4]
- 只输出JSON，不要有其他文本
- 重点关注：错误提示、必填字段标记、按钮状态、已上传图片"""

    @staticmethod
    def _default_comparison_prompt() -> str:
        return """你是一个UI自动化视觉对比器。对比两张京麦商品发布页面截图（第一张是操作前，第二张是操作后），按JSON格式输出：

{
  "changed": true/false,
  "changes": [
    {
      "region": "变化的区域描述",
      "before": "操作前的状态",
      "after": "操作后的状态",
      "significance": "critical/significant/minor"
    }
  ],
  "action_successful": true/false,
  "page_state_after": "操作后的页面状态",
  "confidence": 0.0到1.0之间的置信度
}

注意：
- 只输出JSON，不要有其他文本
- 重点关注：图片槽位变化、文本输入变化、按钮状态变化、错误提示出现/消失
- action_successful判断操作是否达到了预期效果"""

    @staticmethod
    def _default_location_prompt(description: str) -> str:
        return f"""你是一个UI元素定位器。在给定的京麦页面截图中，找到"{description}"元素，按JSON格式输出：

{{
  "found": true/false,
  "description": "找到的元素描述",
  "bbox": [left, top, right, bottom],
  "point": [x, y],
  "confidence": 0.0到1.0之间的置信度
}}

注意：
- bbox坐标使用相对比例（0-1），例如 [0.1, 0.2, 0.3, 0.4]
- point 是元素的中心点，同样使用相对比例 [x, y]
- 只输出JSON，不要有其他文本"""

    # ── 响应解析 ─────────────────────────────────────────────────

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any] | None:
        """从模型输出中提取 JSON 对象。"""
        if not text:
            return None
        # 尝试直接解析
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        # 尝试提取 ```json ... ``` 代码块
        import re
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass
        # 尝试找到第一个 { 和最后一个 }
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
        return None

    def _parse_analysis_response(self, text: str) -> VisionAnalysis:
        """解析单图分析响应。"""
        data = self._extract_json(text)
        if data is None:
            return VisionAnalysis(
                success=True,  # 模型有响应就算部分成功
                page_state="unknown",
                text_content=text[:500],
                confidence=0.1,
            )
        return VisionAnalysis(
            success=True,
            page_state=data.get("page_state", "unknown"),
            elements=data.get("elements", []),
            text_content=data.get("text_content", ""),
            confidence=float(data.get("confidence", 0.5)),
        )

    def _parse_comparison_response(self, text: str) -> VisionAnalysis:
        """解析双图对比响应。"""
        data = self._extract_json(text)
        if data is None:
            return VisionAnalysis(
                success=False,
                page_state="comparison_failed",
                text_content=text[:500],
                confidence=0.1,
            )
        action_successful = bool(data.get("action_successful", False))
        return VisionAnalysis(
            success=action_successful,
            page_state=data.get("page_state_after", "unknown"),
            elements=data.get("changes", []),
            text_content=json.dumps(data.get("changes", []), ensure_ascii=False),
            confidence=float(data.get("confidence", 0.5)),
        )

    def _parse_location_response(self, text: str) -> VisionAnalysis:
        """解析元素定位响应。"""
        data = self._extract_json(text)
        if data is None:
            return VisionAnalysis(
                success=False,
                error="无法解析定位结果",
                confidence=0.0,
            )
        bbox_raw = data.get("bbox")
        point_raw = data.get("point")
        found = bool(data.get("found", False))
        return VisionAnalysis(
            success=found,
            bbox=tuple(bbox_raw) if bbox_raw and len(bbox_raw) == 4 else None,
            point=tuple(point_raw) if point_raw and len(point_raw) == 2 else None,
            confidence=float(data.get("confidence", 0.3)),
            elements=[data] if found else [],
        )


# ── 工厂函数 ──────────────────────────────────────────────────────


def create_vision_provider_from_env() -> OllamaVisionProvider:
    """从环境变量创建 OllamaVisionProvider 实例。"""
    import os

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen3-vl:8b")
    timeout = int(os.getenv("LLM_TIMEOUT", "120"))
    fallback_url = os.getenv("VLLM_BASE_URL")
    fallback_model = os.getenv("VLLM_MODEL")

    return OllamaVisionProvider(
        base_url=base_url,
        model=model,
        timeout=timeout,
        fallback_base_url=fallback_url or None,
        fallback_model=fallback_model or None,
    )
