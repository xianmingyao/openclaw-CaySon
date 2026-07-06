"""BusinessCache 方法完整性验证测试。"""

from unittest.mock import AsyncMock

import pytest

from jm_ufo_agent.storage.business_cache import (
    MilvusReflectionStore,
    RedisBusinessCache,
)


class TestRedisBusinessCacheMethods:
    """验证 RedisBusinessCache 所有缓存方法存在且签名正确。"""

    def test_has_ocr_cache_methods(self):
        cache = RedisBusinessCache.__new__(RedisBusinessCache)
        assert hasattr(cache, "set_ocr_cache")
        assert hasattr(cache, "get_ocr_cache")
        assert callable(cache.set_ocr_cache)
        assert callable(cache.get_ocr_cache)

    def test_has_vlm_cache_methods(self):
        cache = RedisBusinessCache.__new__(RedisBusinessCache)
        assert hasattr(cache, "set_vlm_cache")
        assert hasattr(cache, "get_vlm_cache")
        assert callable(cache.set_vlm_cache)
        assert callable(cache.get_vlm_cache)

    def test_has_locator_cache_methods(self):
        cache = RedisBusinessCache.__new__(RedisBusinessCache)
        assert hasattr(cache, "set_locator_cache")
        assert hasattr(cache, "get_locator_cache")
        assert callable(cache.set_locator_cache)
        assert callable(cache.get_locator_cache)

    @pytest.mark.asyncio
    async def test_ocr_cache_roundtrip(self):
        """OCR 缓存 set+get 应能正确往返。"""
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock(return_value=True)
        mock_redis.get = AsyncMock(return_value='{"signature": "abc", "text": "测试"}')

        cache = RedisBusinessCache(redis=mock_redis, prefix="jm_ufo_agent:v2")
        await cache.set_ocr_cache("sig1", {"text": "测试", "signature": "abc"})
        result = await cache.get_ocr_cache("sig1")
        assert result is not None
        assert result["text"] == "测试"
        mock_redis.set.assert_called_once()
        mock_redis.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_miss_returns_none(self):
        """缓存未命中应返回 None。"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        cache = RedisBusinessCache(redis=mock_redis)
        result = await cache.get_ocr_cache("missing_sig")
        assert result is None


class TestMilvusReflectionStoreMethods:
    """验证 MilvusReflectionStore 方法完整性。"""

    def test_has_add_failure_reflection(self):
        store = MilvusReflectionStore.__new__(MilvusReflectionStore)
        assert hasattr(store, "add_failure_reflection")
        assert callable(store.add_failure_reflection)

    @pytest.mark.asyncio
    async def test_add_failure_reflection_calls_insert(self):
        """add_failure_reflection 应调用 collection.insert。"""
        mock_collection = AsyncMock()
        store = MilvusReflectionStore(collection=mock_collection)
        await store.add_failure_reflection(
            task_id="t1",
            row_index=0,
            reason="字段验证不通过",
            vector=[0.1] * 768,
            metadata={"node": "VERIFY_FIELD"},
        )
        mock_collection.insert.assert_called_once()
        # 验证插入的数据结构
        inserted = mock_collection.insert.call_args[0][0]
        assert isinstance(inserted, list)
        assert len(inserted) == 1
        assert inserted[0]["task_id"] == "t1"
        assert inserted[0]["reason"] == "字段验证不通过"
