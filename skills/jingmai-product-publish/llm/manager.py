"""
京麦商品发布自动化 - LLM 管理器
多模态 + 调用兜底
"""
from typing import Optional

from llm.base import LLMProvider
from llm.ollama import OllamaProvider
from llm.vllm import VLLMProvider
from llm.router import MoERouter


class LLMManager:
    """LLM 管理器 — 路由 + 调用 + 兜底"""

    def __init__(self, settings=None):
        if settings is None:
            from settings import get_settings
            settings = get_settings()

        # 初始化 providers
        self.ollama = OllamaProvider(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            timeout=settings.LLM_TIMEOUT,
        )
        self.vllm = VLLMProvider(
            base_url=settings.VLLM_BASE_URL,
            model=settings.VLLM_MODEL,
            timeout=settings.LLM_TIMEOUT,
        )

        # 路由器
        self.router = MoERouter([self.ollama, self.vllm])

    def invoke(self, prompt: str, **kwargs) -> str:
        """调用 LLM，双层兜底"""
        provider = self.router.route()
        try:
            return provider.invoke(prompt, **kwargs)
        except Exception as e:
            fallback = self.router.fallback()
            if fallback:
                return fallback.invoke(prompt, **kwargs)
            raise RuntimeError(f"LLM 全部不可用: {e}") from e

    def invoke_multimodal(self, prompt: str, image_path: str, **kwargs) -> str:
        """多模态调用"""
        provider = self.router.route()
        try:
            return provider.invoke_multimodal(prompt, image_path, **kwargs)
        except Exception as e:
            fallback = self.router.fallback()
            if fallback:
                return fallback.invoke_multimodal(prompt, image_path, **kwargs)
            raise RuntimeError(f"LLM 多模态全部不可用: {e}") from e

    def embed_text(self, text: str) -> list:
        """文本向量化"""
        provider = self.router.route()
        try:
            return provider.embed_text(text)
        except Exception:
            fallback = self.router.fallback()
            if fallback:
                return fallback.embed_text(text)
            raise RuntimeError("LLM embed 全部不可用")
