"""Redis 行级锁。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RowLock:
    """行级锁结果。"""

    task_id: str
    row_index: int
    owner: str
    acquired: bool


class RedisRowLock:
    """基于 Redis NX EX 的行级锁封装。"""

    def __init__(self, redis_client: Any, ttl_sec: int = 600, key_prefix: str = "jm_ufo_agent:row_lock"):
        """初始化行锁。"""

        # redis_client 是外部注入对象，测试可用 fake client。
        # ttl_sec 控制崩溃后自动释放时间。
        # key_prefix 隔离本项目锁空间，避免污染其他 Redis key。
        self.redis_client = redis_client
        self.ttl_sec = ttl_sec
        self.key_prefix = key_prefix

    def key(self, task_id: str, row_index: int) -> str:
        """生成 Redis 锁 key。"""

        # key 中包含 task_id 和 row_index，保证行级互斥。
        # 不包含商品标题等敏感信息。
        # 统一入口便于测试和后续迁移 key 格式。
        return f"{self.key_prefix}:{task_id}:{row_index}"

    async def acquire(self, task_id: str, row_index: int, owner: str) -> RowLock:
        """尝试获取行级锁。"""

        # Redis SET key value NX EX 是原子操作。
        # fake client 只需实现 set(..., nx=True, ex=ttl)。
        # 返回 RowLock，调用方可直接判断 acquired。
        key = self.key(task_id, row_index)
        acquired = await self.redis_client.set(key, owner, nx=True, ex=self.ttl_sec)
        return RowLock(task_id=task_id, row_index=row_index, owner=owner, acquired=bool(acquired))

    async def release(self, lock: RowLock) -> bool:
        """释放当前 owner 持有的锁。"""

        # 先读 owner，避免删除其他 worker 后来拿到的锁。
        # fake client 需要实现 get/delete 即可测试。
        # owner 不匹配时返回 False，不做破坏性删除。
        key = self.key(lock.task_id, lock.row_index)
        current_owner = await self.redis_client.get(key)
        if current_owner != lock.owner:
            return False
        deleted = await self.redis_client.delete(key)
        return bool(deleted)
