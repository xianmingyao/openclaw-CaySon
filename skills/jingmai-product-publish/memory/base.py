"""
京麦商品发布自动化 - Memory 存储基类与数据类型
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class MemoryType(Enum):
    """记忆类型"""
    WORKING = "working"         # 进程内
    SHORT_TERM = "short_term"   # JSON 文件，7 天 TTL
    LONG_TERM = "long_term"     # Milvus 向量存储


@dataclass
class MemoryItem:
    """记忆条目"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: MemoryType = MemoryType.WORKING
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    embedding_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "metadata": self.metadata,
            "importance": self.importance,
            "created_at": self.created_at,
            "access_count": self.access_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryItem":
        data["type"] = MemoryType(data.get("type", "working"))
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class MemoryStore(ABC):
    """记忆存储抽象基类"""

    @abstractmethod
    def create(self, item: MemoryItem) -> str:
        """创建记忆，返回 ID"""
        pass

    @abstractmethod
    def retrieve(self, item_id: str) -> Optional[MemoryItem]:
        """获取记忆"""
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """搜索记忆"""
        pass

    @abstractmethod
    def update(self, item_id: str, **kwargs) -> bool:
        """更新记忆"""
        pass

    @abstractmethod
    def delete(self, item_id: str) -> bool:
        """删除记忆"""
        pass
