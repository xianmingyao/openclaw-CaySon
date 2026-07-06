"""MySQL 连接池封装。"""

from __future__ import annotations

from typing import Any

from jm_ufo_agent.core.settings import MySQLSettings


class AsyncMySQLClient:
    """延迟创建的 asyncmy 连接池客户端。"""

    def __init__(self, settings: MySQLSettings):
        """保存配置但不立即连接数据库。"""

        # 只保存配置对象，不在构造函数里做网络 IO。
        # pool 初始为空，首次 connect 时再创建。
        # 这样 CLI 的 --help、单元测试和配置校验都不会误连数据库。
        self.settings = settings
        self.pool: Any | None = None

    async def connect(self) -> Any:
        """创建并缓存 asyncmy 连接池。

        # asyncmy 是可选依赖，只有真实连接时才导入。
        # 如果依赖未安装，会给出明确错误，单元测试不受影响。
        # 重复调用会复用已有 pool，避免创建多组连接。
        """

        if self.pool is not None:
            return self.pool
        try:
            import asyncmy
        except ImportError as exc:
            raise RuntimeError("缺少 asyncmy，无法连接 MySQL") from exc
        self.pool = await asyncmy.create_pool(
            host=self.settings.host,
            port=self.settings.port,
            user=self.settings.user,
            password=self.settings.password,
            db=self.settings.database,
            charset=self.settings.charset,
            minsize=self.settings.min_size,
            maxsize=self.settings.max_size,
        )
        return self.pool

    async def close(self) -> None:
        """关闭连接池。"""

        # 如果从未连接，close 是幂等空操作。
        # wait_closed 确保底层连接真正释放。
        # 关闭后清空 pool，允许后续重新 connect。
        if self.pool is None:
            return
        self.pool.close()
        await self.pool.wait_closed()
        self.pool = None
