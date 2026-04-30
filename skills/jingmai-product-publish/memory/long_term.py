"""
京麦商品发布自动化 - Long-term Memory
Milvus 向量存储，失败时自动降级而不阻塞主流程。
"""
import json
import time
from typing import List, Optional

from memory.base import MemoryItem, MemoryStore, MemoryType


class LongTermMemory(MemoryStore):
    """Milvus 长期记忆。"""

    def __init__(
        self,
        host: str = "8.137.122.11",
        port: int = 19530,
        collection_name: str = "jingmai_publish_memory",
        dim: int = 768,
    ):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.dim = dim
        self._client = None
        self._embed_fn = None
        self._disabled_until = 0.0

    def set_embed_fn(self, fn) -> None:
        self._embed_fn = fn

    def is_available(self) -> bool:
        return self._connect()

    def _connect(self) -> bool:
        if time.time() < self._disabled_until:
            return False
        if self._client is not None:
            return True

        try:
            from pymilvus import MilvusClient

            self._client = MilvusClient(uri=f"http://{self.host}:{self.port}")
            self._ensure_collection()
            return self._client is not None
        except Exception as exc:
            print(f"[LongTermMemory] Milvus 连接失败: {exc}")
            self._mark_unavailable()
            return False

    def _ensure_collection(self) -> None:
        if self._client is None:
            return

        try:
            from pymilvus import CollectionSchema, DataType, FieldSchema

            if not self._client.has_collection(self.collection_name):
                schema = CollectionSchema(
                    fields=[
                        FieldSchema("id", DataType.VARCHAR, max_length=64, is_primary=True),
                        FieldSchema("content", DataType.VARCHAR, max_length=4096),
                        FieldSchema("memory_type", DataType.VARCHAR, max_length=32),
                        FieldSchema("importance", DataType.FLOAT),
                        FieldSchema("created_at", DataType.VARCHAR, max_length=64),
                        FieldSchema("metadata_json", DataType.VARCHAR, max_length=4096),
                        FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=self.dim),
                    ]
                )
                self._client.create_collection(collection_name=self.collection_name, schema=schema)

            indexes = self._safe_list_indexes()
            if not indexes:
                index_params = self._client.prepare_index_params()
                index_params.add_index(
                    field_name="embedding",
                    index_type="IVF_FLAT",
                    metric_type="COSINE",
                    params={"nlist": 128},
                )
                self._client.create_index(
                    collection_name=self.collection_name,
                    index_params=index_params,
                )

            self._client.load_collection(self.collection_name)
        except Exception as exc:
            print(f"[LongTermMemory] collection 初始化失败: {exc}")
            self._mark_unavailable()

    def create(self, item: MemoryItem) -> str:
        if not self._connect():
            return item.id

        item.type = MemoryType.LONG_TERM
        payload = {
            "id": item.id,
            "content": item.content,
            "memory_type": item.type.value,
            "importance": item.importance,
            "created_at": item.created_at,
            "metadata_json": json.dumps(item.metadata, ensure_ascii=False),
            "embedding": self._get_embedding(item.content),
        }
        try:
            self._client.insert(collection_name=self.collection_name, data=[payload])
        except Exception as exc:
            print(f"[LongTermMemory] 插入失败: {exc}")
            self._mark_unavailable()
        return item.id

    def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        if not self._connect():
            return None

        try:
            rows = self._client.get(
                collection_name=self.collection_name,
                ids=[item_id],
                output_fields=["content", "memory_type", "importance", "created_at", "metadata_json"],
            )
            if not rows:
                return None
            row = rows[0]
            return MemoryItem(
                id=row["id"],
                type=MemoryType(row.get("memory_type", MemoryType.LONG_TERM.value)),
                content=row["content"],
                importance=row.get("importance", 0.5),
                created_at=row.get("created_at", ""),
                metadata=json.loads(row.get("metadata_json", "{}")),
            )
        except Exception:
            return None

    def search(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        if not self._connect():
            return []

        try:
            results = self._client.search(
                collection_name=self.collection_name,
                data=[self._get_embedding(query)],
                limit=top_k,
                output_fields=["content", "memory_type", "importance", "created_at", "metadata_json"],
                search_params={"metric_type": "COSINE"},
            )
        except Exception as exc:
            print(f"[LongTermMemory] 搜索失败: {exc}")
            self._mark_unavailable()
            return []

        items: List[MemoryItem] = []
        for hit in results[0]:
            row = hit["entity"]
            items.append(
                MemoryItem(
                    id=hit["id"],
                    type=MemoryType(row.get("memory_type", MemoryType.LONG_TERM.value)),
                    content=row["content"],
                    importance=row.get("importance", 0.5),
                    created_at=row.get("created_at", ""),
                    metadata=json.loads(row.get("metadata_json", "{}")),
                )
            )
        return items

    def update(self, item_id: str, **kwargs) -> bool:
        item = self.retrieve(item_id)
        if item is None:
            return False
        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
        self.delete(item_id)
        self.create(item)
        return True

    def delete(self, item_id: str) -> bool:
        if not self._connect():
            return False
        try:
            self._client.delete(collection_name=self.collection_name, ids=[item_id])
            return True
        except Exception:
            self._mark_unavailable()
            return False

    def _get_embedding(self, text: str) -> list:
        if self._embed_fn:
            try:
                embedding = self._embed_fn(text)
                if embedding:
                    return embedding
            except Exception:
                pass
        return [0.0] * self.dim

    def _safe_list_indexes(self) -> List[str]:
        try:
            indexes = self._client.list_indexes(self.collection_name)
            return list(indexes or [])
        except Exception:
            return []

    def _mark_unavailable(self) -> None:
        self._client = None
        self._disabled_until = time.time() + 30
