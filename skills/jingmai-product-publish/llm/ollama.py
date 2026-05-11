"""
京麦商品发布自动化 - Ollama Provider (Tier 1)
借鉴 jingmai-putaway 的 qwen3 thinking 提取（3 层响应恢复）
"""
import json
import re
import base64
from pathlib import Path
from typing import Optional

from llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    """Ollama 本地模型 Provider"""

    def __init__(self, base_url: str = "http://localhost:11434",
                 model: str = "qwen3-vl", timeout: int = 120):
        super().__init__("ollama", base_url, model, timeout)
        self._resolved_model: Optional[str] = None

    def invoke(self, prompt: str, **kwargs) -> str:
        """调用 Ollama API，含 qwen3 thinking 提取"""
        try:
            import httpx

            # 强制 JSON 输出（抑制 qwen3 思考文本干扰）
            payload = {
                "model": self._resolve_model_name(),
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": kwargs.get("options", {}),
            }

            resp = httpx.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            raw = self._extract_generate_text(resp.json())

            return self._extract_content(raw)

        except Exception as e:
            raise RuntimeError(f"Ollama 调用失败: {e}") from e

    def invoke_multimodal(self, prompt: str, image_path: str, **kwargs) -> str:
        """多模态调用（图片 + 文本）"""
        try:
            import httpx

            image_paths = [image_path]
            extra_image_paths = kwargs.get("extra_image_paths") or kwargs.get("image_paths") or []
            image_paths.extend([path for path in extra_image_paths if path and path not in image_paths])
            image_data = [self._prepare_image(path) for path in image_paths if path]

            payload = {
                "model": self._resolve_model_name(),
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "images": image_data,
            }

            resp = httpx.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            raw = self._extract_generate_text(resp.json())

            return self._extract_content(raw)

        except Exception as e:
            raise RuntimeError(f"Ollama 多模态调用失败: {e}") from e

    def embed_text(self, text: str) -> list:
        """文本向量化"""
        try:
            import httpx
            resp = httpx.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self._resolve_model_name(), "prompt": text},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json().get("embedding", [])
        except Exception as e:
            raise RuntimeError(f"Ollama embed 失败: {e}") from e

    def health_check(self) -> bool:
        """健康检查：服务可达且配置模型可解析。"""
        try:
            return bool(self._resolve_model_name(force_refresh=True))
        except Exception:
            return False

    def _list_models(self) -> list[str]:
        import httpx

        resp = httpx.get(f"{self.base_url}/api/tags", timeout=8)
        resp.raise_for_status()
        data = resp.json()
        return [item.get("name", "") for item in data.get("models", []) if item.get("name")]

    def _resolve_model_name(self, force_refresh: bool = False) -> str:
        """把配置模型名解析为本机实际已安装的 Ollama 模型名。"""
        if self._resolved_model and not force_refresh:
            return self._resolved_model

        names = self._list_models()
        if self.model in names:
            self._resolved_model = self.model
            return self._resolved_model

        base_name = self.model.split(":", 1)[0].lower()
        candidates = [name for name in names if name.lower().split(":", 1)[0] == base_name]
        if not candidates:
            raise RuntimeError(f"Ollama 模型不存在: {self.model}")

        preferred = self._pick_preferred_model(candidates)
        self._resolved_model = preferred
        return preferred

    @staticmethod
    def _pick_preferred_model(candidates: list[str]) -> str:
        """同系列模型优先挑常见轻量版本，避免环境里有多个别名时随机命中。"""
        for suffix in (":8b", ":7b", ":latest"):
            for name in candidates:
                if name.lower().endswith(suffix):
                    return name
        return sorted(candidates, key=len)[0]

    def _prepare_image(self, image_path: str) -> str:
        """准备图片数据（缩放到 LLM 识别图尺寸 + base64）"""
        try:
            from PIL import Image
            import io

            # 从配置读取 LLM 识别图最大尺寸（默认 1120x560）
            try:
                from settings import get_settings
                s = get_settings()
                max_w = s.SCREENSHOT_PLAN_MAX_WIDTH
                max_h = s.SCREENSHOT_PLAN_MAX_HEIGHT
            except Exception:
                max_w, max_h = 1024, 550

            img = Image.open(image_path)
            # 按比例缩放到识别图尺寸范围内
            ratio = min(max_w / img.size[0], max_h / img.size[1], 1.0)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size)

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=75)
            return base64.b64encode(buf.getvalue()).decode("utf-8")
        except ImportError:
            # PIL 不可用时直接读取文件
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")

    def _extract_content(self, raw: str) -> str:
        """
        3 层响应恢复（借鉴 putaway ollama_provider.py）：
        1. 直接是 JSON
        2. thinking 标签内提取
        3. 正则兜底提取 JSON
        """
        raw = raw.strip()

        # 层1: 直接 JSON
        try:
            result = json.loads(raw)
            if isinstance(result, dict):
                return raw
        except json.JSONDecodeError:
            pass

        # 层2: 提取 <think...</think 之后的内容
        think_pattern = re.compile(r'</think\s*>\s*(.*)', re.DOTALL)
        match = think_pattern.search(raw)
        if match:
            content = match.group(1).strip()
            try:
                json.loads(content)
                return content
            except json.JSONDecodeError:
                pass
            # 尝试从内容中提取 JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    json.loads(json_match.group())
                    return json_match.group()
                except json.JSONDecodeError:
                    pass

        # 层3: 正则兜底
        json_match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
        if json_match:
            try:
                json.loads(json_match.group())
                return json_match.group()
            except json.JSONDecodeError:
                pass

        # 全部失败，返回原始内容
        return raw

    @staticmethod
    def _extract_generate_text(payload: dict) -> str:
        """兼容 qwen3 系列把结构化结果放进 thinking 字段的返回格式。"""
        response = (payload.get("response") or "").strip()
        thinking = (payload.get("thinking") or "").strip()
        if response and thinking:
            return f"{thinking}\n{response}"
        return response or thinking
