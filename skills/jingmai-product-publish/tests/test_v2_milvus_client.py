"""MilvusClient 补全方法测试。"""

from unittest.mock import MagicMock, patch

import pytest

from jm_ufo_agent.core.settings import MilvusSettings
from jm_ufo_agent.storage.milvus_client import MilvusClient


@pytest.fixture
def settings():
    return MilvusSettings(host="localhost", port=19530, db="default")


@pytest.fixture
def client(settings):
    return MilvusClient(settings)


class TestMilvusClientCollection:
    @patch("jm_ufo_agent.storage.milvus_client.MilvusClient.connect")
    def test_create_collection_if_not_exists(self, mock_connect, client):
        """create_collection 应调用 pymilvus Collection。"""
        client.connected = True
        with patch("pymilvus.Collection") as MockColl:
            MockColl.exists.return_value = False
            mock_coll_instance = MagicMock()
            MockColl.return_value = mock_coll_instance
            client.create_collection(
                name="test_col",
                dimension=128,
                description="测试集合",
            )
            MockColl.assert_called_once()

    @patch("jm_ufo_agent.storage.milvus_client.MilvusClient.connect")
    def test_create_collection_skip_if_exists(self, mock_connect, client):
        """已有 collection 时应跳过创建。"""
        client.connected = True
        with patch("pymilvus.Collection") as MockColl:
            MockColl.exists.return_value = True
            client.create_collection(name="existing_col", dimension=128)
            MockColl.assert_called_once()  # 仍会调用构造函数获取已有集合


class TestMilvusClientSearch:
    @patch("jm_ufo_agent.storage.milvus_client.MilvusClient.connect")
    def test_search_returns_results(self, mock_connect, client):
        """search 应返回搜索结果列表。"""
        client.connected = True
        with patch("pymilvus.Collection") as MockColl:
            mock_coll = MagicMock()
            MockColl.return_value = mock_coll
            mock_hit = MagicMock()
            mock_hit.id = "vec1"
            mock_hit.distance = 0.1
            mock_hit.entity._row_data = {"text": "hello"}
            mock_coll.search.return_value = [[mock_hit]]
            results = client.search(
                collection_name="test_col",
                query_vector=[0.1] * 128,
                top_k=5,
            )
            assert isinstance(results, list)
            assert len(results) == 1
            assert results[0]["id"] == "vec1"
            assert results[0]["distance"] == 0.1

    def test_search_before_connect_raises(self, client):
        """未连接时搜索应抛出异常。"""
        client.connected = False
        with pytest.raises(RuntimeError, match="未连接"):
            client.search(collection_name="test_col", query_vector=[0.1] * 128, top_k=5)

    def test_create_collection_before_connect_raises(self, client):
        """未连接时创建集合应抛出异常。"""
        client.connected = False
        with pytest.raises(RuntimeError, match="未连接"):
            client.create_collection(name="test_col", dimension=128)
