# -*- coding: utf-8 -*-
"""
MAGMA + Mem0 混合架构
"""
import sys
from pathlib import Path
from typing import List, Dict, Optional

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from magma_memory.core import MemoryGraph, MemoryNode
from magma_memory.retrieval import RetrievalEngine
from magma_memory.writer import MemoryWriter


class MAGMAMem0Hybrid:
    """
    MAGMA四维图谱 + Mem0 混合记忆系统
    
    设计理念：
    - Mem0: 快速向量检索，适合粗筛
    - MAGMA: 四维精排，适合精准召回
    """
    
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or str(Path(__file__).parent / "magma_graph.json")
        
        # MAGMA 四维图谱
        self.magma = MemoryGraph(self.storage_path)
        
        # 检索引擎
        self.retriever = RetrievalEngine(self.magma)
        
        # 写入器
        self.writer = MemoryWriter(self.magma)
        
        # 检索统计
        self.search_stats = {
            'total_searches': 0,
            'cache_hits': 0
        }
    
    def add(self, content: str, 
            source: str = "manual",
            keywords: List[str] = None,
            entities: Dict[str, List[str]] = None) -> str:
        """
        添加记忆（同时写入MAGMA）
        
        注意：与Mem0的双写需要调用mem0_dual_write.py
        """
        node_id = self.writer.add(
            content=content,
            source=source,
            keywords=keywords,
            entities=entities
        )
        return node_id
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        检索记忆
        
        使用四维检索：语义 + 时间 + 因果 + 实体
        """
        self.search_stats['total_searches'] += 1
        return self.retriever.retrieve(query, top_k=top_k)
    
    def get_recent(self, limit: int = 10) -> List[MemoryNode]:
        """获取近期记忆"""
        return self.magma.get_recent_nodes(limit=limit)
    
    def get_causal_chain(self, node_id: str, depth: int = 3) -> Dict:
        """获取因果链"""
        return self.magma.get_causal_chain(node_id, depth=depth)
    
    def link_causal(self, cause_node_id: str, effect_node_id: str, strength: float = 0.5):
        """建立因果链接"""
        self.writer.update_causal_link(cause_node_id, effect_node_id, strength)
    
    def stats(self) -> dict:
        """获取统计信息"""
        base_stats = self.magma.get_stats()
        base_stats.update(self.search_stats)
        return base_stats
    
    def explain_node(self, node_id: str) -> Dict:
        """解释单个记忆节点"""
        node = self.magma.get_node(node_id)
        if not node:
            return {}
        
        causal_chain = self.magma.get_causal_chain(node_id, depth=2)
        
        return {
            "id": node.id,
            "content": node.content,
            "created": node.created_at,
            "four_dimensions": {
                "semantic": {
                    "keywords": node.semantic_keywords
                },
                "temporal": {
                    "sequence": node.temporal_sequence,
                    "period": node.temporal_period,
                    "date": node.temporal_date
                },
                "causal": {
                    "causes": [self.magma.get_node(nid).content[:50] if self.magma.get_node(nid) else nid 
                              for nid in node.causal_causes],
                    "effects": [self.magma.get_node(nid).content[:50] if self.magma.get_node(nid) else nid 
                               for nid in node.causal_effects],
                    "strength": node.causal_strength
                },
                "entity": {
                    "subjects": node.entity_subjects,
                    "objects": node.entity_objects,
                    "concepts": node.entity_concepts
                }
            },
            "source": node.source,
            "importance": node.importance
        }


# 全局实例
_global_hybrid = None

def get_hybrid() -> MAGMAMem0Hybrid:
    """获取全局混合实例"""
    global _global_hybrid
    if _global_hybrid is None:
        _global_hybrid = MAGMAMem0Hybrid()
    return _global_hybrid


def add_memory(content: str, source: str = "manual", keywords: List[str] = None) -> str:
    """便捷添加记忆"""
    return get_hybrid().add(content, source, keywords)

def search_memory(query: str, top_k: int = 10) -> List[Dict]:
    """便捷检索记忆"""
    return get_hybrid().search(query, top_k)

def get_memory_stats() -> dict:
    """获取记忆统计"""
    return get_hybrid().stats()
