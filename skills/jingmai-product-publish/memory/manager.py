"""
京麦商品发布自动化 - 记忆管理器
"""
from typing import List, Optional

from memory.base import MemoryItem, MemoryType
from memory.long_term import LongTermMemory
from memory.short_term import ShortTermMemory
from memory.working import WorkingMemory


class MemoryManager:
    """统一管理工作、短期、长期记忆。"""

    def __init__(self, settings=None, llm=None):
        if settings is None:
            from settings import get_settings

            settings = get_settings()

        self.working = WorkingMemory()
        self.short_term = ShortTermMemory(
            base_dir=settings.MEMORY_BASE_DIR,
            ttl_days=settings.SHORT_TERM_TTL_DAYS,
        )
        self.long_term = LongTermMemory(
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
            collection_name=settings.MILVUS_COLLECTION,
            dim=settings.MILVUS_DIM,
        )

        # 自动注入 LLM embedding 函数
        if llm is not None and hasattr(llm, "embed_text"):
            self.long_term.set_embed_fn(llm.embed_text)

    def set_embed_fn(self, fn) -> None:
        self.long_term.set_embed_fn(fn)

    def remember(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.WORKING,
        importance: float = 0.5,
        metadata: Optional[dict] = None,
    ) -> str:
        item = MemoryItem(
            type=memory_type,
            content=content,
            importance=importance,
            metadata=metadata or {},
        )
        return self._get_store(memory_type).create(item)

    def remember_working(self, content: str, importance: float = 0.5, **meta) -> str:
        return self.remember(content, MemoryType.WORKING, importance, meta)

    def remember_short_term(self, content: str, importance: float = 0.6, **meta) -> str:
        return self.remember(content, MemoryType.SHORT_TERM, importance, meta)

    def remember_long_term(self, content: str, importance: float = 0.8, **meta) -> str:
        return self.remember(content, MemoryType.LONG_TERM, importance, meta)

    def recall(
        self,
        query: str,
        top_k: int = 5,
        layers: Optional[List[MemoryType]] = None,
    ) -> List[MemoryItem]:
        layers = layers or [MemoryType.WORKING, MemoryType.SHORT_TERM, MemoryType.LONG_TERM]
        results: List[MemoryItem] = []
        for layer in layers:
            try:
                results.extend(self._get_store(layer).search(query, top_k=top_k))
            except Exception:
                continue

        results.sort(key=lambda item: item.importance, reverse=True)
        return results[:top_k]

    def get(self, item_id: str, memory_type: Optional[MemoryType] = None) -> Optional[MemoryItem]:
        if memory_type is not None:
            return self._get_store(memory_type).retrieve(item_id)

        for layer in (MemoryType.WORKING, MemoryType.SHORT_TERM, MemoryType.LONG_TERM):
            item = self._get_store(layer).retrieve(item_id)
            if item is not None:
                return item
        return None

    def promote(self, item_id: str, from_type: MemoryType, to_type: MemoryType) -> bool:
        item = self._get_store(from_type).retrieve(item_id)
        if item is None:
            return False
        item.type = to_type
        self._get_store(to_type).create(item)
        return True

    def forget(self, item_id: str, memory_type: Optional[MemoryType] = None) -> bool:
        if memory_type is not None:
            return self._get_store(memory_type).delete(item_id)

        deleted = False
        for layer in (MemoryType.WORKING, MemoryType.SHORT_TERM, MemoryType.LONG_TERM):
            deleted = self._get_store(layer).delete(item_id) or deleted
        return deleted

    def cleanup(self) -> dict:
        return {
            "short_term_cleaned": self.short_term.cleanup_expired(),
            "working_count": self.working.count(),
            "long_term_available": self.long_term.is_available(),
        }

    def stats(self) -> dict:
        return {
            "working": self.working.count(),
            "short_term": self.short_term.count(),
            "long_term": "available" if self.long_term.is_available() else "degraded",
        }

    def clear_working(self) -> None:
        self.working.clear()

    def _get_store(self, memory_type: MemoryType):
        mapping = {
            MemoryType.WORKING: self.working,
            MemoryType.SHORT_TERM: self.short_term,
            MemoryType.LONG_TERM: self.long_term,
        }
        return mapping[memory_type]
