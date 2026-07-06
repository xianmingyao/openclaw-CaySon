"""Redis 客户端封装。"""

from __future__ import annotations

from typing import Any

from jm_ufo_agent.core.settings import RedisSettings


class RedisClient:
    """延迟创建的 redis.asyncio 客户端。"""

    def __init__(self, settings: RedisSettings):
        """保存 Redis 配置。"""

        # 构造时不连接 Redis，避免导入模块产生外部副作用。
        # client 初始为空，connect 负责延迟初始化。
        # 这种模式也方便测试替换 client。
        self.settings = settings
        self.client: Any | None = None

    def connect(self) -> Any:
        """创建并缓存 Redis 客户端。

        # redis 是可选依赖，只有运行时需要锁/缓存时才导入。
        # decode_responses=True 让状态值以字符串形式返回，减少调用方转换。
        # 重复调用直接返回旧 client，保持单进程内连接复用。
        """

        if self.client is not None:
            return self.client
        try:
            from redis import asyncio as redis_asyncio
        except ImportError as exc:
            raise RuntimeError("缺少 redis，无法连接 Redis") from exc
        self.client = redis_asyncio.Redis(
            host=self.settings.host,
            port=self.settings.port,
            password=self.settings.password,
            db=self.settings.db,
            decode_responses=True,
        )
        return self.client

    async def close(self) -> None:
        """关闭 Redis 客户端。"""

        # 未连接时直接返回，保持幂等。
        # aclose 是 redis.asyncio 的异步关闭方法。
        # 关闭后置空，避免误复用已关闭连接。
        if self.client is None:
            return
        await self.client.aclose()
        self.client = None
