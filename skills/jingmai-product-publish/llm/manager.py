"""
京麦商品发布自动化 - LLM 管理器
统一管理和调度不同的 LLM 提供者

三级回退链: Ollama → vLLM → 抛异常（由上层降级处理）
- route() 健康检查缓存 30s
- _call_text 遍历所有 provider 逐个尝试调用
- 都不可用时抛 RuntimeError，由 Agent 层走降级模式
"""
from typing import Any, List, Optional

from loguru import logger

from llm.ollama import OllamaProvider
from llm.router import MoERouter
from llm.vllm import VLLMProvider


class LLMManager:
    """LLM 路由、调用和兜底。"""

    # 标记是否有任何健康的 provider（供 Agent 层快速判断）
    _llm_available: bool = True

    def __init__(self, settings=None):
        if settings is None:
            from settings import get_settings
            settings = get_settings()

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
        self.router = MoERouter([self.ollama, self.vllm])

    def invoke(self, prompt: str, **kwargs) -> str:
        """同步调用 LLM（纯文本）"""
        return self._call_text("invoke", prompt, **kwargs)

    def invoke_multimodal(self, prompt: str, image_path: str, **kwargs) -> str:
        """同步调用 LLM（多模态：文本 + 图片）"""
        return self._call_text("invoke_multimodal", prompt, image_path, **kwargs)

    def embed_text(self, text: str) -> list:
        """文本向量化（遍历所有 provider）"""
        providers = self._all_providers_ordered()
        last_error = None
        for provider in providers:
            try:
                embedding = provider.embed_text(text)
                if embedding:
                    return embedding
                last_error = RuntimeError(f"{provider.name} 返回空 embedding")
            except Exception as exc:
                last_error = exc
                logger.debug(f"[LLMManager] {provider.name} embed 失败: {exc}")
        raise RuntimeError(f"LLM embed 全部不可用: {last_error}")

    def is_available(self) -> bool:
        """快速检查是否有可用的 LLM provider"""
        return self.router.route() is not None

    def get_health_status(self) -> dict:
        """获取所有 provider 健康状态（诊断用）"""
        return self.router.get_health_status()

    def _call_text(self, method_name: str, *args, **kwargs) -> str:
        """
        带完整 fallback 的 LLM 调用

        策略：
        1. route() 找健康的 provider → 优先调用
        2. 失败/不健康 → 遍历剩余 provider 逐个尝试
        3. 全部失败 → 抛 RuntimeError

        这样即使 route() 缓存过期或 provider 在调用时恢复，
        也能兜底成功。
        """
        providers = self._all_providers_ordered()
        errors = []

        for provider in providers:
            try:
                response = getattr(provider, method_name)(*args, **kwargs)
                text = (response or "").strip()
                if text:
                    logger.debug(f"[LLMManager] {provider.name} 调用成功")
                    self._llm_available = True
                    return text
                errors.append(f"{provider.name}: 空响应")
                logger.warning(f"[LLMManager] {provider.name} 返回空响应")
            except Exception as exc:
                err_msg = str(exc)[:200]
                errors.append(f"{provider.name}: {err_msg}")
                logger.warning(f"[LLMManager] {provider.name} 调用失败: {err_msg}")

        self._llm_available = False
        error_summary = "; ".join(errors)
        logger.error(f"[LLMManager] 所有 LLM 提供者不可用: {error_summary}")
        raise RuntimeError(f"所有 LLM 提供者不可用: {error_summary}")

    def _all_providers_ordered(self) -> List[Any]:
        """
        返回有序的 provider 列表（健康的在前）

        route() 返回健康的排第一，其余按原顺序追加。
        如果 route() 返回 None（全部不健康），仍返回所有 provider
        让 _call_text 逐个尝试。
        """
        primary = self.router.route()
        if primary is None:
            # 全部不健康，仍按原顺序尝试（可能在调用时已恢复）
            return list(self.router.providers)

        ordered = [primary]
        for provider in self.router.providers:
            if provider.name != primary.name:
                ordered.append(provider)
        return ordered
