"""速率限制器 — 令牌桶算法实现。

用于限制 LLM API 调用、GUI 操作等场景的请求频率，
防止因过快调用触发服务端限流或桌面操作堆积。
"""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass


@dataclass
class RateLimiterConfig:
    """速率限制器配置。"""

    # max_tokens: 令牌桶容量
    # refill_rate: 每秒补充的令牌数
    max_tokens: float = 10.0
    refill_rate: float = 1.0


class RateLimiter:
    """令牌桶速率限制器。

    # 经典令牌桶算法：桶有最大容量，按固定速率补充令牌。
    # 每次操作消耗一个令牌，桶空时阻塞等待。
    # 线程安全，使用 threading.Lock 保护共享状态。
    # 适用于限制 LLM API 调用频率、GUI 操作间隔等。
    """

    def __init__(self, config: RateLimiterConfig | None = None):
        """初始化速率限制器。"""
        cfg = config or RateLimiterConfig()
        self._max_tokens = cfg.max_tokens
        self._refill_rate = cfg.refill_rate
        self._tokens = self._max_tokens
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    @classmethod
    def from_rps(cls, requests_per_second: float, burst: int = 1) -> "RateLimiter":
        """从每秒请求数创建限制器。

        # requests_per_second 是稳态速率。
        # burst 是允许的突发请求数（令牌桶容量）。
        """
        return cls(RateLimiterConfig(max_tokens=float(burst), refill_rate=requests_per_second))

    def acquire(self, tokens: float = 1.0, timeout: float | None = None) -> bool:
        """获取令牌，成功返回 True。

        # tokens 是本次需要消耗的令牌数。
        # timeout 为 None 时阻塞直到获取令牌。
        # timeout 为 0 时非阻塞，获取失败立即返回 False。
        # timeout > 0 时最多等待 timeout 秒。
        """
        deadline = None if timeout is None else time.monotonic() + timeout

        while True:
            with self._lock:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True

            if deadline is not None and time.monotonic() >= deadline:
                return False

            # 等待一个令牌的补充时间
            wait_time = tokens / self._refill_rate if self._refill_rate > 0 else 0.1
            time.sleep(min(wait_time * 0.5, 0.1))

    def try_acquire(self, tokens: float = 1.0) -> bool:
        """非阻塞尝试获取令牌。"""
        return self.acquire(tokens=tokens, timeout=0)

    @property
    def available_tokens(self) -> float:
        """当前可用令牌数。"""
        with self._lock:
            self._refill()
            return self._tokens

    def _refill(self) -> None:
        """补充令牌（调用方需持有锁）。"""
        now = time.monotonic()
        elapsed = now - self._last_refill
        new_tokens = elapsed * self._refill_rate
        self._tokens = min(self._max_tokens, self._tokens + new_tokens)
        self._last_refill = now
