"""
京麦商品发布自动化 - vLLM Provider (Tier 2)
借鉴 jingmai-putaway 的 HuggingfaceProvider (httpx AsyncClient)
"""
import base64
import json
from pathlib import Path

from llm.base import LLMProvider


class VLLMProvider(LLMProvider):
    """vLLM 远程模型 Provider（OpenAI 兼容 API）"""

    def __init__(self, base_url: str = "http://localhost:8000",
                 model: str = "qwen3-vl", timeout: int = 120):
        super().__init__("vllm", base_url, model, timeout)

    def invoke(self, prompt: str, **kwargs) -> str:
        """调用 vLLM OpenAI 兼容 API"""
        try:
            import httpx

            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", 4096),
                "temperature": kwargs.get("temperature", 0.7),
            }

            resp = httpx.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            raise RuntimeError(f"vLLM 调用失败: {e}") from e

    def invoke_multimodal(self, prompt: str, image_path: str, **kwargs) -> str:
        """多模态调用"""
        try:
            import httpx
            from PIL import Image
            import io

            # 准备图片
            img = Image.open(image_path)
            max_size = 1024
            ratio = min(max_size / max(img.size), 1.0)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=75)
            img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

            payload = {
                "model": self.model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                    ],
                }],
                "max_tokens": kwargs.get("max_tokens", 4096),
            }

            resp = httpx.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            raise RuntimeError(f"vLLM 多模态调用失败: {e}") from e

    def embed_text(self, text: str) -> list:
        """文本向量化"""
        try:
            import httpx
            resp = httpx.post(
                f"{self.base_url}/v1/embeddings",
                json={"model": self.model, "input": text},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]
        except Exception as e:
            raise RuntimeError(f"vLLM embed 失败: {e}") from e

    def health_check(self) -> bool:
        """健康检查"""
        try:
            import httpx
            resp = httpx.get(f"{self.base_url}/v1/models", timeout=8)
            return resp.status_code == 200
        except Exception:
            return False
