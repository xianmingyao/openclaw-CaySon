"""
京麦商品发布自动化 - MoE 路由器
健康检查 + 路由 + Fallback 链
"""
from typing import Optional, List

from llm.base import LLMProvider


class MoERouter:
    """MoE 路由器 — 健康检查优先，fallback 链保底"""

    def __init__(self, providers: List[LLMProvider]):
        self.providers = providers
        self._health_cache = {}
        self._cache_ttl = 30  # 健康检查缓存 30 秒
        self._last_check = 0

    def route(self) -> LLMProvider:
        """路由到健康的 Provider"""
        import time
        now = time.time()

        # 缓存过期时刷新
        if now - self._last_check > self._cache_ttl:
            self._health_cache.clear()
            for provider in self.providers:
                self._health_cache[provider.name] = provider.health_check()
            self._last_check = now

        # 选择第一个健康的
        for provider in self.providers:
            if self._health_cache.get(provider.name, False):
                return provider

        # 全部不健康，返回第一个（让调用方处理错误）
        return self.providers[0]

    def fallback(self) -> Optional[LLMProvider]:
        """获取 fallback Provider"""
        for provider in self.providers[1:]:
            if self._health_cache.get(provider.name, True):
                return provider
        return None
