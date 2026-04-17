# -*- coding: utf-8 -*-
"""
MAGMA 核心数据结构和图谱管理
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json
import uuid
import numpy as np


@dataclass
class MemoryNode:
    """记忆节点 - 四维图谱的核心单元"""
    id: str = ""
    content: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    # 语义维度
    semantic_keywords: List[str] = field(default_factory=list)
    semantic_embedding: Optional[List[float]] = None
    
    # 时间维度
    temporal_sequence: int = 0
    temporal_period: str = ""  # morning/afternoon/evening/night
    temporal_date: str = ""    # YYYY-MM-DD
    
    # 因果维度
    causal_causes: List[str] = field(default_factory=list)   # 原因节点ID
    causal_effects: List[str] = field(default_factory=list)  # 结果节点ID
    causal_strength: float = 0.5  # 因果强度 0-1
    
    # 实体维度
    entity_subjects: List[str] = field(default_factory=list)  # 主语实体
    entity_objects: List[str] = field(default_factory=list)   # 宾语实体
    entity_concepts: List[str] = field(default_factory=list) # 概念实体
    
    # 元数据
    source: str = "manual"  # 来源：wechat/douyin/doc/manual
    importance: float = 1.0  # 重要性 0-1
    verified: bool = False
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MemoryNode':
        return cls(**data)


class MemoryGraph:
    """四维记忆图谱"""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self.nodes: Dict[str, MemoryNode] = {}
        self.sequence_counter = 0
        
        # 四维索引
        self.keyword_index: Dict[str, set] = {}  # keyword -> node_ids
        self.sequence_index: Dict[int, str] = {}  # sequence -> node_id
        self.entity_index: Dict[str, set] = {}   # entity -> node_ids
        self.causal_index: Dict[str, Tuple[set, set]] = {}  # node_id -> (causes, effects)
        
        if storage_path and Path(storage_path).exists():
            self.load()
    
    def add_node(self, node: MemoryNode) -> str:
        """添加记忆节点"""
        # 序列号
        self.sequence_counter += 1
        node.temporal_sequence = self.sequence_counter
        
        # 时间周期
        dt = datetime.now()
        hour = dt.hour
        if 5 <= hour < 12:
            node.temporal_period = "morning"
        elif 12 <= hour < 18:
            node.temporal_period = "afternoon"
        elif 18 <= hour < 22:
            node.temporal_period = "evening"
        else:
            node.temporal_period = "night"
        node.temporal_date = dt.strftime("%Y-%m-%d")
        
        # 存储节点
        self.nodes[node.id] = node
        
        # 更新索引
        self._update_indices(node)
        
        return node.id
    
    def _update_indices(self, node: MemoryNode):
        """更新四维索引"""
        # 语义索引
        for kw in node.semantic_keywords:
            if kw not in self.keyword_index:
                self.keyword_index[kw] = set()
            self.keyword_index[kw].add(node.id)
        
        # 时间索引
        self.sequence_index[node.temporal_sequence] = node.id
        
        # 实体索引
        for entity in node.entity_subjects + node.entity_objects + node.entity_concepts:
            if entity not in self.entity_index:
                self.entity_index[entity] = set()
            self.entity_index[entity].add(node.id)
        
        # 因果索引
        self.causal_index[node.id] = (set(node.causal_causes), set(node.causal_effects))
    
    def get_node(self, node_id: str) -> Optional[MemoryNode]:
        return self.nodes.get(node_id)
    
    def get_recent_nodes(self, limit: int = 10) -> List[MemoryNode]:
        """获取最近的记忆节点"""
        sequences = sorted(self.sequence_index.keys(), reverse=True)
        result = []
        for seq in sequences[:limit]:
            node_id = self.sequence_index.get(seq)
            if node_id and node_id in self.nodes:
                result.append(self.nodes[node_id])
        return result
    
    def search_by_keyword(self, keyword: str, limit: int = 10) -> List[MemoryNode]:
        """语义检索：按关键词"""
        node_ids = self.keyword_index.get(keyword, set())
        return [self.nodes[nid] for nid in list(node_ids)[:limit] if nid in self.nodes]
    
    def search_by_entity(self, entity: str, limit: int = 10) -> List[MemoryNode]:
        """实体检索：按实体名"""
        node_ids = self.entity_index.get(entity, set())
        return [self.nodes[nid] for nid in list(node_ids)[:limit] if nid in self.nodes]
    
    def search_by_time_range(self, start_seq: int, end_seq: int) -> List[MemoryNode]:
        """时间检索：按序列范围"""
        result = []
        for seq in range(start_seq, end_seq + 1):
            node_id = self.sequence_index.get(seq)
            if node_id and node_id in self.nodes:
                result.append(self.nodes[node_id])
        return result
    
    def get_causal_chain(self, node_id: str, depth: int = 3) -> Dict:
        """获取因果链"""
        node = self.nodes.get(node_id)
        if not node:
            return {}
        
        chain = {
            "node": node.to_dict(),
            "causes": [],
            "effects": []
        }
        
        # 递归获取原因
        visited = set()
        self._collect_causal(node.causal_causes, chain["causes"], visited, depth, "cause")
        
        # 递归获取结果
        visited = set()
        self._collect_causal(node.causal_effects, chain["effects"], visited, depth, "effect")
        
        return chain
    
    def _collect_causal(self, node_ids: List[str], target: list, visited: set, depth: int, direction: str):
        """递归收集因果节点"""
        if depth <= 0:
            return
        for nid in node_ids:
            if nid in visited:
                continue
            visited.add(nid)
            node = self.nodes.get(nid)
            if node:
                target.append({
                    "id": node.id,
                    "content": node.content[:100],
                    "direction": direction
                })
                if direction == "cause":
                    self._collect_causal(node.causal_causes, target, visited, depth - 1, direction)
                else:
                    self._collect_causal(node.causal_effects, target, visited, depth - 1, direction)
    
    def save(self):
        """保存到磁盘"""
        if not self.storage_path:
            return
        
        data = {
            "nodes": {k: v.to_dict() for k, v in self.nodes.items()},
            "sequence_counter": self.sequence_counter,
            "keyword_index": {k: list(v) for k, v in self.keyword_index.items()},
            "entity_index": {k: list(v) for k, v in self.entity_index.items()},
        }
        
        Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self):
        """从磁盘加载"""
        if not self.storage_path or not Path(self.storage_path).exists():
            return
        
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.nodes = {k: MemoryNode.from_dict(v) for k, v in data.get("nodes", {}).items()}
        self.sequence_counter = data.get("sequence_counter", 0)
        self.keyword_index = {k: set(v) for k, v in data.get("keyword_index", {}).items()}
        self.entity_index = {k: set(v) for k, v in data.get("entity_index", {}).items()}
        
        # 重建sequence索引
        for node in self.nodes.values():
            self.sequence_index[node.temporal_sequence] = node.id
        
        # 重建causal索引
        for node in self.nodes.values():
            self.causal_index[node.id] = (set(node.causal_causes), set(node.causal_effects))
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "total_nodes": len(self.nodes),
            "sequence_counter": self.sequence_counter,
            "keywords": len(self.keyword_index),
            "entities": len(self.entity_index),
        }
