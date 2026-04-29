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

    def invoke(self, prompt: str, **kwargs) -> str:
        """调用 Ollama API，含 qwen3 thinking 提取"""
        try:
            import httpx

            # 强制 JSON 输出（抑制 qwen3 思考文本干扰）
            payload = {
                "model": self.model,
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
            raw = resp.json().get("response", "")

            return self._extract_content(raw)

        except Exception as e:
            raise RuntimeError(f"Ollama 调用失败: {e}") from e

    def invoke_multimodal(self, prompt: str, image_path: str, **kwargs) -> str:
        """多模态调用（图片 + 文本）"""
        try:
            import httpx

            # 读取并 base64 编码图片
            image_data = self._prepare_image(image_path)

            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "images": [image_data],
            }

            resp = httpx.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            raw = resp.json().get("response", "")

            return self._extract_content(raw)

        except Exception as e:
            raise RuntimeError(f"Ollama 多模态调用失败: {e}") from e

    def embed_text(self, text: str) -> list:
        """文本向量化"""
        try:
            import httpx
            resp = httpx.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json().get("embedding", [])
        except Exception as e:
            raise RuntimeError(f"Ollama embed 失败: {e}") from e

    def health_check(self) -> bool:
        """健康检查"""
        try:
            import httpx
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=8)
            return resp.status_code == 200
        except Exception:
            return False

    def _prepare_image(self, image_path: str) -> str:
        """准备图片数据（缩放 + base64）"""
        try:
            from PIL import Image
            import io

            img = Image.open(image_path)
            # 缩放到 1024px
            max_size = 1024
            ratio = min(max_size / max(img.size), 1.0)
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
