"""
京麦商品发布自动化 - Short-term Memory（JSON 文件，7 天 TTL）
替代 Redis，减少依赖
"""
import json
import time
from pathlib import Path
from typing import Optional, List

from memory.base import MemoryStore, MemoryItem, MemoryType


class ShortTermMemory(MemoryStore):
    """JSON 文件短期记忆"""

    def __init__(self, base_dir: str = None, ttl_days: int = 7):
        if base_dir:
            self.base_dir = Path(base_dir) / "short_term"
        else:
            self.base_dir = Path("logs/memory/short_term")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_days * 86400

    def create(self, item: MemoryItem) -> str:
        item.type = MemoryType.SHORT_TERM
        path = self.base_dir / f"{item.id}.json"
        path.write_text(json.dumps(item.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return item.id

    def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        path = self.base_dir / f"{item_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            item = MemoryItem.from_dict(data)
            item.access_count += 1
            # 更新访问计数
            path.write_text(json.dumps(item.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
            return item
        except Exception:
            return None

    def search(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """简单关键词搜索"""
        results = []
        query_lower = query.lower()

        for path in self.base_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                item = MemoryItem.from_dict(data)
                if query_lower in item.content.lower():
                    results.append(item)
            except Exception:
                continue

        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:top_k]

    def update(self, item_id: str, **kwargs) -> bool:
        path = self.base_dir / f"{item_id}.json"
        if not path.exists():
            return False
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            item = MemoryItem.from_dict(data)
            for k, v in kwargs.items():
                if hasattr(item, k):
                    setattr(item, k, v)
            path.write_text(json.dumps(item.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
            return True
        except Exception:
            return False

    def delete(self, item_id: str) -> bool:
        path = self.base_dir / f"{item_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def cleanup_expired(self) -> int:
        """清理过期记忆，返回清理数量"""
        now = time.time()
        cleaned = 0
        for path in self.base_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                created = data.get("created_at", "")
                if created:
                    from datetime import datetime
                    created_time = datetime.fromisoformat(created).timestamp()
                    if now - created_time > self.ttl_seconds:
                        path.unlink()
                        cleaned += 1
            except Exception:
                continue
        return cleaned

    def count(self) -> int:
        """返回当前记忆条数"""
        return len(list(self.base_dir.glob("*.json")))
