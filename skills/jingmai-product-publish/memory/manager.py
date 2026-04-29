"""
京麦商品发布自动化 - 统一记忆管理器
三层记忆协调：Working → Short-term → Long-term
"""
from typing import Optional, List

from memory.base import MemoryItem, MemoryType
from memory.working import WorkingMemory
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory


class MemoryManager:
    """三层记忆管理器 — Agent 可通过此类统一读写所有记忆"""

    def __init__(self, settings=None):
        if settings is None:
            from settings import get_settings
            settings = get_settings()

        # 三层存储
        self.working = WorkingMemory()
        self.short_term = ShortTermMemory(
            base_dir=settings.MEMORY_BASE_DIR,
            ttl_days=settings.SHORT_TERM_TTL_DAYS,
        )
        self.long_term = LongTermMemory(
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT,
        )

        self._embed_fn = None

    def set_embed_fn(self, fn):
        """注入 embedding 函数（由 Agent 层调用，连接 LLM）"""
        self._embed_fn = fn
        self.long_term.set_embed_fn(fn)

    # ── 写入 ──────────────────────────────────────

    def remember(self, content: str, memory_type: MemoryType = MemoryType.WORKING,
                 importance: float = 0.5, metadata: dict = None) -> str:
        """写入记忆，返回 ID"""
        item = MemoryItem(
            type=memory_type,
            content=content,
            importance=importance,
            metadata=metadata or {},
        )
        store = self._get_store(memory_type)
        return store.create(item)

    def remember_working(self, content: str, importance: float = 0.5, **meta) -> str:
        """快捷：写入工作记忆"""
        return self.remember(content, MemoryType.WORKING, importance, meta)

    def remember_short_term(self, content: str, importance: float = 0.6, **meta) -> str:
        """快捷：写入短期记忆"""
        return self.remember(content, MemoryType.SHORT_TERM, importance, meta)

    def remember_long_term(self, content: str, importance: float = 0.8, **meta) -> str:
        """快捷：写入长期记忆"""
        return self.remember(content, MemoryType.LONG_TERM, importance, meta)

    # ── 检索 ──────────────────────────────────────

    def recall(self, query: str, top_k: int = 5,
               layers: List[MemoryType] = None) -> List[MemoryItem]:
        """跨层搜索记忆"""
        if layers is None:
            layers = [MemoryType.WORKING, MemoryType.SHORT_TERM, MemoryType.LONG_TERM]

        results = []
        for layer in layers:
            store = self._get_store(layer)
            try:
                items = store.search(query, top_k=top_k)
                results.extend(items)
            except Exception:
                continue

        # 按重要度排序
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:top_k]

    def get(self, item_id: str, memory_type: MemoryType = None) -> Optional[MemoryItem]:
        """按 ID 获取记忆"""
        if memory_type:
            return self._get_store(memory_type).retrieve(item_id)

        # 逐层查找
        for layer in [MemoryType.WORKING, MemoryType.SHORT_TERM, MemoryType.LONG_TERM]:
            item = self._get_store(layer).retrieve(item_id)
            if item:
                return item
        return None

    # ── 升级/降级 ──────────────────────────────────

    def promote(self, item_id: str, from_type: MemoryType, to_type: MemoryType) -> bool:
        """记忆升级：低层 → 高层"""
        item = self._get_store(from_type).retrieve(item_id)
        if not item:
            return False
        self._get_store(to_type).create(item)
        return True

    def forget(self, item_id: str, memory_type: MemoryType = None) -> bool:
        """删除记忆"""
        if memory_type:
            return self._get_store(memory_type).delete(item_id)
        # 逐层删除
        deleted = False
        for layer in [MemoryType.WORKING, MemoryType.SHORT_TERM, MemoryType.LONG_TERM]:
            if self._get_store(layer).delete(item_id):
                deleted = True
        return deleted

    # ── 维护 ──────────────────────────────────────

    def cleanup(self) -> dict:
        """清理过期记忆，返回统计"""
        return {
            "short_term_cleaned": self.short_term.cleanup_expired(),
            "working_count": self.working.count(),
        }

    def clear_working(self):
        """清空工作记忆（每次新任务开始时调用）"""
        self.working.clear()

    # ── 内部 ──────────────────────────────────────

    def _get_store(self, memory_type: MemoryType):
        mapping = {
            MemoryType.WORKING: self.working,
            MemoryType.SHORT_TERM: self.short_term,
            MemoryType.LONG_TERM: self.long_term,
        }
        return mapping[memory_type]
