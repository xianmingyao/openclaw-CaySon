"""Repository 公共工具。"""

from __future__ import annotations

import json
from typing import Any


class SQLRepository:
    """基于异步连接的轻量 Repository 基类。"""

    def __init__(self, connection: Any):
        """保存外部传入的连接对象。"""

        self.connection = connection

    async def execute(self, sql: str, params: tuple[Any, ...] = ()) -> Any:
        """执行写入 SQL。

        # Repository 不直接创建连接，方便测试传入 fake connection。
        # 兼容两类连接：带 execute 方法的对象，或需要 cursor 上下文的连接。
        # 返回底层执行结果，调用方可按需要读取影响行数。
        """

        if hasattr(self.connection, "execute"):
            return await self.connection.execute(sql, params)
        async with self.connection.cursor() as cursor:
            return await cursor.execute(sql, params)

    async def fetchone(self, sql: str, params: tuple[Any, ...] = ()) -> Any:
        """查询单行数据。"""

        if hasattr(self.connection, "fetchone"):
            return await self.connection.fetchone(sql, params)
        async with self.connection.cursor() as cursor:
            await cursor.execute(sql, params)
            return await cursor.fetchone()

    async def fetchall(self, sql: str, params: tuple[Any, ...] = ()) -> list[Any]:
        """查询多行数据。"""

        # fake connection 可以直接实现 fetchall，单元测试更简单。
        # 默认数据库连接走 cursor.fetchall。
        # 返回值统一转 list，方便调用方重复遍历。
        if hasattr(self.connection, "fetchall"):
            return list(await self.connection.fetchall(sql, params))
        async with self.connection.cursor() as cursor:
            await cursor.execute(sql, params)
            return list(await cursor.fetchall())

    def dumps_json(self, value: dict[str, Any]) -> str:
        """把字典稳定序列化为 JSON。"""

        # ensure_ascii=False 保留中文证据，方便人工排查。
        # sort_keys=True 让测试和 checkpoint diff 更稳定。
        # Repository 层统一处理 JSON，避免各调用点格式不一致。
        return json.dumps(value, ensure_ascii=False, sort_keys=True)

    def loads_json(self, value: str | bytes | None) -> dict[str, Any]:
        """把 JSON 字段还原为字典。"""

        # 空值按空字典处理，兼容旧数据或初始化状态。
        # bytes 先按 UTF-8 解码，适配部分数据库驱动返回类型。
        # JSON 解析错误不吞掉，坏状态必须尽早暴露。
        if value in (None, ""):
            return {}
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return json.loads(value)
