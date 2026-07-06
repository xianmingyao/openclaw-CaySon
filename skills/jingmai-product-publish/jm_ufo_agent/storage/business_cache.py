"""Redis/Milvus 业务缓存封装。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CacheEntry:
    """缓存条目。"""

    key: str
    value: dict[str, Any]


class RedisBusinessCache:
    """封装 OCR/VLM/locator 的 Redis 缓存键。"""

    def __init__(self, redis: Any, prefix: str = "jm_ufo_agent:v2"):
        """保存 Redis 客户端和 key 前缀。"""

        # redis 可以是真实 redis.asyncio client，也可以是测试 fake。
        # prefix 统一隔离本项目缓存，避免污染其它业务 key。
        # 该类不创建连接，只使用外部传入的 client。
        self.redis = redis
        self.prefix = prefix

    async def set_ocr_cache(self, page_signature: str, payload: dict[str, Any], ttl_sec: int = 86400) -> None:
        """写入 OCR cache。"""

        # OCR cache 以 page_signature 为键，避免同一页面重复识别。
        # JSON 使用 ensure_ascii=False，保留中文 OCR 结果。
        # TTL 默认 24 小时，符合设计文档中短期缓存定位。
        await self._set_json(f"ocr:{page_signature}", payload, ttl_sec)

    async def get_ocr_cache(self, page_signature: str) -> dict[str, Any] | None:
        """读取 OCR cache。"""

        # 找不到返回 None，让上层重新截图/OCR。
        # 解析错误直接抛出，缓存损坏需要尽早暴露。
        # page_signature 必须由截图/OCR 层生成，不能用空字符串。
        return await self._get_json(f"ocr:{page_signature}")

    async def set_vlm_cache(self, asset_hash: str, payload: dict[str, Any], ttl_sec: int = 86400) -> None:
        """写入 VLM cache。"""

        # VLM cache 使用图片 hash，避免同一图片重复调用模型。
        # payload 可保存转换路径、模型名、耗时和结果摘要。
        # TTL 可由调用方按成本策略调整。
        await self._set_json(f"vlm:{asset_hash}", payload, ttl_sec)

    async def get_vlm_cache(self, asset_hash: str) -> dict[str, Any] | None:
        """读取 VLM cache。"""

        # 命中缓存时，图片处理 worker 可以跳过真实 VLM 调用。
        # 未命中返回 None，由上层决定是否调用模型。
        # 该方法不判断业务有效性，只负责读缓存。
        return await self._get_json(f"vlm:{asset_hash}")

    async def set_locator_cache(self, field_key: str, page_signature: str, payload: dict[str, Any], ttl_sec: int = 86400) -> None:
        """写入 locator cache。"""

        # Redis locator cache 是热缓存，MySQL locator_cache 是持久层。
        # key 同时包含字段和页面签名，避免跨页面误用坐标。
        # payload 通常包含 rect、confidence、source。
        await self._set_json(f"locator:{page_signature}:{field_key}", payload, ttl_sec)

    async def get_locator_cache(self, field_key: str, page_signature: str) -> dict[str, Any] | None:
        """读取 locator cache。"""

        # 找不到时上层应进入 CALIBRATE_LOCATORS。
        # 只返回 JSON 字典，不实例化 CoordinatePlan，避免 storage 依赖 backend。
        # 调用方负责检查 confidence 阈值。
        return await self._get_json(f"locator:{page_signature}:{field_key}")

    async def _set_json(self, key: str, payload: dict[str, Any], ttl_sec: int) -> None:
        """以 JSON 字符串写入 Redis。"""

        # Redis 真实 client 和 fake client 都通常支持 set(name, value, ex=ttl)。
        # 完整 key 在这里拼装，调用方只关心业务 key。
        # sort_keys=True 让测试断言更稳定。
        await self.redis.set(f"{self.prefix}:{key}", json.dumps(payload, ensure_ascii=False, sort_keys=True), ex=ttl_sec)

    async def _get_json(self, key: str) -> dict[str, Any] | None:
        """从 Redis 读取 JSON 字典。"""

        # redis.asyncio decode_responses=True 时返回 str，默认可能返回 bytes。
        # 空值表示缓存未命中。
        # JSON 顶层必须是 dict，避免缓存结构漂移。
        value = await self.redis.get(f"{self.prefix}:{key}")
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        data = json.loads(value)
        if not isinstance(data, dict):
            raise ValueError("Redis cache payload must be a JSON object")
        return data


class MilvusReflectionStore:
    """Milvus failure reflections 写入边界。"""

    def __init__(self, collection: Any):
        """保存 Milvus collection-like 对象。"""

        # collection 可以是真实 pymilvus Collection，也可以是测试 fake。
        # 该类只封装 failure reflection 的字段形状。
        # 向量如何生成由上层模型服务负责，不在 storage 层调用 LLM/VLM。
        self.collection = collection

    async def add_failure_reflection(self, task_id: str, row_index: int, reason: str, vector: list[float], metadata: dict[str, Any]) -> None:
        """写入一条失败反思。"""

        # F17/F19 的失败原因可以进入 Milvus 供后续检索。
        # vector 由外部传入，避免该方法隐藏模型调用成本。
        # metadata 保留节点、页面签名、截图路径等定位信息。
        await self.collection.insert(
            [
                {
                    "task_id": task_id,
                    "row_index": row_index,
                    "reason": reason,
                    "vector": vector,
                    "metadata_json": json.dumps(metadata, ensure_ascii=False, sort_keys=True),
                }
            ]
        )
