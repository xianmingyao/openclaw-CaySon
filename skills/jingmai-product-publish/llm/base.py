"""
京麦商品发布自动化 - LLM Provider 基类
借鉴 jingmai-putaway 的 LLMProvider ABC
"""
from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """LLM Provider 抽象基类"""

    def __init__(self, name: str, base_url: str, model: str, timeout: int = 120):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    @abstractmethod
    def invoke(self, prompt: str, **kwargs) -> str:
        """同步调用"""
        pass

    @abstractmethod
    def invoke_multimodal(self, prompt: str, image_path: str, **kwargs) -> str:
        """多模态调用（文本 + 图片）"""
        pass

    @abstractmethod
    def embed_text(self, text: str) -> list:
        """文本向量化"""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """健康检查"""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, model={self.model})"
