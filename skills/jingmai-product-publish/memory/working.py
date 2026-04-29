"""
京麦商品发布自动化 - Working Memory（进程内 dict）
"""
from typing import Optional, List, Dict, Any

from memory.base import MemoryStore, MemoryItem, MemoryType


class WorkingMemory(MemoryStore):
    """进程内 dict 工作记忆，无 IO 开销"""

    def __init__(self):
        self._store: Dict[str, MemoryItem] = {}

    def create(self, item: MemoryItem) -> str:
        item.type = MemoryType.WORKING
        self._store[item.id] = item
        return item.id

    def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        item = self._store.get(item_id)
        if item:
            item.access_count += 1
        return item

    def search(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """简单关键词匹配"""
        results = []
        query_lower = query.lower()
        for item in self._store.values():
            if query_lower in item.content.lower():
                results.append(item)
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:top_k]

    def update(self, item_id: str, **kwargs) -> bool:
        item = self._store.get(item_id)
        if not item:
            return False
        for k, v in kwargs.items():
            if hasattr(item, k):
                setattr(item, k, v)
        return True

    def delete(self, item_id: str) -> bool:
        return self._store.pop(item_id, None) is not None

    def clear(self):
        self._store.clear()

    def count(self) -> int:
        return len(self._store)
