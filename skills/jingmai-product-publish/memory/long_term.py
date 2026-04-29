"""
京麦商品发布自动化 - Long-term Memory（Milvus 向量存储）
语义搜索 + 持久化
"""
import time
from typing import Optional, List

from memory.base import MemoryStore, MemoryItem, MemoryType


class LongTermMemory(MemoryStore):
    """Milvus 向量长期记忆 — 语义搜索"""

    def __init__(self, host: str = "8.137.122.11", port: int = 19530,
                 collection_name: str = "jingmai_memory", dim: int = 768):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.dim = dim
        self._client = None
        self._embed_fn = None  # 延迟注入 embedding 函数

    def set_embed_fn(self, fn):
        """注入 embedding 函数（由 MemoryManager 统一设置）"""
        self._embed_fn = fn

    def _connect(self):
        """延迟连接 Milvus"""
        if self._client is not None:
            return True
        try:
            from pymilvus import MilvusClient
            self._client = MilvusClient(
                uri=f"http://{self.host}:{self.port}"
            )
            self._ensure_collection()
            return True
        except Exception as e:
            print(f"[LongTermMemory] Milvus 连接失败: {e}")
            self._client = None
            return False

    def _ensure_collection(self):
        """确保 collection 存在"""
        if self._client is None:
            return
        try:
            from pymilvus import CollectionSchema, FieldSchema, DataType
            if self._client.has_collection(self.collection_name):
                return

            schema = CollectionSchema(fields=[
                FieldSchema("id", DataType.VARCHAR, max_length=64, is_primary=True),
                FieldSchema("content", DataType.VARCHAR, max_length=4096),
                FieldSchema("memory_type", DataType.VARCHAR, max_length=32),
                FieldSchema("importance", DataType.FLOAT),
                FieldSchema("created_at", DataType.VARCHAR, max_length=64),
                FieldSchema("metadata_json", DataType.VARCHAR, max_length=4096),
                FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=self.dim),
            ])
            self._client.create_collection(
                collection_name=self.collection_name,
                schema=schema,
            )
            # 创建向量索引
            self._client.create_index(
                collection_name=self.collection_name,
                field_name="embedding",
                index_params={"index_type": "IVF_FLAT", "metric_type": "COSINE", "params": {"nlist": 128}},
            )
        except Exception as e:
            print(f"[LongTermMemory] 创建 collection 失败: {e}")

    def create(self, item: MemoryItem) -> str:
        """写入长期记忆"""
        if not self._connect():
            return item.id

        item.type = MemoryType.LONG_TERM
        embedding = self._get_embedding(item.content)

        import json
        data = {
            "id": item.id,
            "content": item.content,
            "memory_type": item.type.value,
            "importance": item.importance,
            "created_at": item.created_at,
            "metadata_json": json.dumps(item.metadata, ensure_ascii=False),
            "embedding": embedding,
        }
        try:
            self._client.insert(
                collection_name=self.collection_name,
                data=[data],
            )
        except Exception as e:
            print(f"[LongTermMemory] 插入失败: {e}")

        return item.id

    def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """按 ID 获取"""
        if not self._connect():
            return None
        try:
            results = self._client.get(
                collection_name=self.collection_name,
                ids=[item_id],
                output_fields=["content", "memory_type", "importance", "created_at", "metadata_json"],
            )
            if not results:
                return None
            row = results[0]
            import json
            return MemoryItem(
                id=row["id"],
                type=MemoryType(row.get("memory_type", "long_term")),
                content=row["content"],
                metadata=json.loads(row.get("metadata_json", "{}")),
                importance=row.get("importance", 0.5),
                created_at=row.get("created_at", ""),
            )
        except Exception:
            return None

    def search(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """语义搜索"""
        if not self._connect():
            return []

        query_vec = self._get_embedding(query)
        try:
            results = self._client.search(
                collection_name=self.collection_name,
                data=[query_vec],
                limit=top_k,
                output_fields=["content", "memory_type", "importance", "created_at", "metadata_json"],
                search_params={"metric_type": "COSINE"},
            )
            items = []
            for hit in results[0]:
                import json
                row = hit["entity"]
                items.append(MemoryItem(
                    id=hit["id"],
                    type=MemoryType(row.get("memory_type", "long_term")),
                    content=row["content"],
                    metadata=json.loads(row.get("metadata_json", "{}")),
                    importance=row.get("importance", 0.5),
                    created_at=row.get("created_at", ""),
                ))
            return items
        except Exception as e:
            print(f"[LongTermMemory] 搜索失败: {e}")
            return []

    def update(self, item_id: str, **kwargs) -> bool:
        """更新 — 删除后重建"""
        item = self.retrieve(item_id)
        if not item:
            return False
        for k, v in kwargs.items():
            if hasattr(item, k):
                setattr(item, k, v)
        self.delete(item_id)
        self.create(item)
        return True

    def delete(self, item_id: str) -> bool:
        """按 ID 删除"""
        if not self._connect():
            return False
        try:
            self._client.delete(
                collection_name=self.collection_name,
                ids=[item_id],
            )
            return True
        except Exception:
            return False

    def _get_embedding(self, text: str) -> list:
        """获取文本向量"""
        if self._embed_fn:
            try:
                return self._embed_fn(text)
            except Exception:
                pass
        # 降级：返回零向量
        return [0.0] * self.dim
