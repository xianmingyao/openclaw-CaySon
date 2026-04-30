"""
京麦商品发布自动化 - MoE 路由器
健康检查 + 路由 + Fallback 链

三级回退策略:
  Ollama (Tier 1) → vLLM (Tier 2) → 无可用 Provider
健康检查带 30s 缓存，避免频繁探测
"""
import time
from typing import Optional, List

from loguru import logger

from llm.base import LLMProvider


class MoERouter:
    """MoE 路由器 — 健康检查优先，fallback 链保底"""

    def __init__(self, providers: List[LLMProvider]):
        self.providers = providers
        self._health_cache: dict = {}
        self._cache_ttl = 30  # 健康检查缓存 30 秒
        self._last_check = 0.0

    def _refresh_health(self):
        """刷新所有 provider 的健康状态"""
        now = time.time()
        if now - self._last_check > self._cache_ttl:
            self._health_cache.clear()
            for provider in self.providers:
                try:
                    self._health_cache[provider.name] = provider.health_check()
                    status = "健康" if self._health_cache[provider.name] else "不可用"
                    logger.info(f"[MoERouter] {provider.name}: {status}")
                except Exception as e:
                    self._health_cache[provider.name] = False
                    logger.warning(f"[MoERouter] {provider.name} 健康检查异常: {e}")
            self._last_check = now

    def route(self) -> LLMProvider:
        """
        路由到健康的 Provider

        按优先级: Ollama → vLLM
        返回第一个健康的 provider。
        全部不健康时返回 None，由调用方决定降级策略。
        """
        self._refresh_health()

        # 选择第一个健康的
        for provider in self.providers:
            if self._health_cache.get(provider.name, False):
                logger.debug(f"[MoERouter] 路由到: {provider.name}")
                return provider

        # 全部不健康 — 尝试实时检查一次（可能是缓存过期）
        logger.warning("[MoERouter] 缓存显示所有 provider 不健康，实时检查...")
        for provider in self.providers:
            try:
                if provider.health_check():
                    self._health_cache[provider.name] = True
                    self._last_check = time.time()
                    logger.info(f"[MoERouter] 实时检查发现 {provider.name} 已恢复")
                    return provider
            except Exception:
                pass

        logger.error(f"[MoERouter] 所有 {len(self.providers)} 个 provider 均不可用")
        return None

    def fallback(self) -> Optional[LLMProvider]:
        """
        获取 fallback Provider（不依赖缓存）

        在 route() 失败后调用，强制实时检查每个 provider
        """
        for provider in self.providers:
            try:
                if provider.health_check():
                    self._health_cache[provider.name] = True
                    return provider
            except Exception:
                pass
        return None

    def get_health_status(self) -> dict:
        """获取所有 provider 的健康状态（供诊断用）"""
        self._refresh_health()
        return dict(self._health_cache)
