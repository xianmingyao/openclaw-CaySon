# -*- coding: utf-8 -*-
"""
MAGMA + Mem0 + Milvus 三写整合版
Multi-Atlas Generative Memory Agent with Hybrid Storage

功能：
1. 三写：MAGMA图谱 + Mem0向量 + Milvus向量
2. 向量检索融合：语义+图谱+向量三重召回
3. 自动因果学习：基于共现统计的因果关系发现
"""
import json
import time
import re
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid

# Mem0客户端
try:
    from mem0 import Memory
    HAS_MEM0 = True
except ImportError:
    HAS_MEM0 = False

# Milvus客户端
try:
    from pymilvus import MilvusClient
    HAS_MILVUS = True
except ImportError:
    HAS_MILVUS = False


@dataclass
class MemoryNode:
    """记忆节点"""
    id: str = ""
    content: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    # 语义维度
    semantic_keywords: List[str] = field(default_factory=list)
    semantic_embedding: Optional[List[float]] = None
    
    # 时间维度
    temporal_sequence: int = 0
    temporal_period: str = ""
    temporal_date: str = ""
    
    # 因果维度
    causal_causes: List[str] = field(default_factory=list)
    causal_effects: List[str] = field(default_factory=list)
    causal_strength: float = 0.5
    causal_auto_learned: bool = False  # 标记是否自动学习到的因果
    
    # 实体维度
    entity_subjects: List[str] = field(default_factory=list)
    entity_objects: List[str] = field(default_factory=list)
    entity_concepts: List[str] = field(default_factory=list)
    
    # 元数据
    source: str = "manual"
    importance: float = 1.0
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
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class CausalLearner:
    """
    自动因果关系学习器
    
    基于以下假设：
    1. 共现频率高的记忆可能存在因果关系
    2. 时间上连续的记忆可能存在因果关系
    3. 实体共享度高的记忆可能存在因果关系
    """
    
    def __init__(self, graph: 'MemoryGraphV2'):
        self.graph = graph
        self.causal_patterns = {
            'if_then': ['如果', '那么', '只要', '就'],
            'cause_effect': ['因为', '所以', '导致', '造成', '因此'],
            'sequence': ['然后', '接着', '之后', '于是'],
            'contain': ['包含', '含有', '具有']
        }
    
    def learn_from_content(self, content: str) -> Tuple[List[str], List[str], float]:
        """
        从内容中学习因果关系
        
        Returns:
            (causes, effects, strength)
        """
        causes = []
        effects = []
        strength = 0.0
        
        # 模式匹配
        content_lower = content.lower()
        
        for pattern_type, keywords in self.causal_patterns.items():
            for kw in keywords:
                if kw in content:
                    strength += 0.15
        
        # 检查是否包含条件句
        if re.search(r'如果.*那么|如果.*就', content):
            causes.append('condition_pattern')
            effects.append('result_pattern')
            strength += 0.2
        
        return causes, effects, min(strength, 1.0)
    
    def learn_from_cooccurrence(self, node: MemoryNode, window_size: int = 5) -> Dict:
        """
        基于共现学习因果关系
        
        原理：如果两个记忆经常在短时间内出现，可能存在因果关系
        """
        # 获取时间窗口内的邻居节点
        neighbors = []
        seq = node.temporal_sequence
        
        for other_node in self.graph.nodes.values():
            if other_node.id == node.id:
                continue
            # 时间距离
            time_dist = abs(other_node.temporal_sequence - seq)
            if time_dist <= window_size:
                neighbors.append({
                    'node': other_node,
                    'distance': time_dist,
                    'shared_entities': self._count_shared_entities(node, other_node)
                })
        
        # 排序：优先考虑时间近且实体共享多的
        neighbors.sort(key=lambda x: (x['distance'], -x['shared_entities']))
        
        potential_causes = []
        potential_effects = []
        
        for n in neighbors[:3]:
            other = n['node']
            # 如果共享实体多，可能是因果关系
            if n['shared_entities'] >= 2:
                if other.temporal_sequence < seq:
                    potential_causes.append(other.id)
                else:
                    potential_effects.append(other.id)
        
        return {
            'causes': potential_causes,
            'effects': potential_effects,
            'confidence': len(potential_causes) + len(potential_effects) > 0
        }
    
    def _count_shared_entities(self, node1: MemoryNode, node2: MemoryNode) -> int:
        """计算两个节点的实体共享数量"""
        entities1 = set(node1.entity_subjects + node1.entity_objects + node1.entity_concepts)
        entities2 = set(node2.entity_subjects + node2.entity_objects + node2.entity_concepts)
        return len(entities1 & entities2)


class MemoryGraphV2:
    """四维记忆图谱 v2 - 带自动因果学习"""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path
        self.nodes: Dict[str, MemoryNode] = {}
        self.sequence_counter = 0
        
        # 索引
        self.keyword_index: Dict[str, set] = {}
        self.sequence_index: Dict[int, str] = {}
        self.entity_index: Dict[str, set] = {}
        
        # 因果学习器
        self.causal_learner = CausalLearner(self)
        
        # Mem0客户端
        self.mem0_client = None
        if HAS_MEM0:
            try:
                import os
                os.environ.pop("OPENAI_API_KEY", None)
                config = {
                    "vector_store": {
                        "provider": "chroma",
                        "config": {
                            "collection_name": "clawdbot_memories",
                            "path": str(Path.home() / ".mem0/chroma")
                        }
                    },
                    "llm": {
                        "provider": "ollama",
                        "config": {
                            "model": "llama3.2",
                            "temperature": 0.0,
                            "ollama_base_url": "http://localhost:11434"
                        }
                    },
                    "embedder": {
                        "provider": "ollama",
                        "config": {
                            "model": "nomic-embed-text",
                            "ollama_base_url": "http://localhost:11434"
                        }
                    }
                }
                self.mem0_client = Memory.from_config(config)
            except Exception as e:
                print(f"Mem0 init failed: {e}")
                pass
        
        # Milvus客户端
        self.milvus_client = None
        self.milvus_collection = "magma_memories"
        if HAS_MILVUS:
            try:
                self.milvus_client = MilvusClient(uri="http://8.137.122.11:19530")
                # 确保集合存在
                if self.milvus_client.has_collection(self.milvus_collection):
                    pass
                else:
                    self.milvus_client.create_collection(
                        collection_name=self.milvus_collection,
                        dimension=768
                    )
            except:
                pass
        
        if storage_path and Path(storage_path).exists():
            self.load()
    
    def add_node(self, node: MemoryNode, enable_causal_learn: bool = True) -> str:
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
        
        # 自动因果学习
        if enable_causal_learn:
            self._auto_learn_causal(node)
        
        # 存储节点
        self.nodes[node.id] = node
        
        # 更新索引
        self._update_indices(node)
        
        # 写入Mem0
        self._write_mem0(node)
        
        # 写入Milvus
        self._write_milvus(node)
        
        return node.id
    
    def _auto_learn_causal(self, node: MemoryNode):
        """自动学习因果关系"""
        # 1. 从内容模式学习
        causes, effects, strength = self.causal_learner.learn_from_content(node.content)
        if causes:
            node.causal_causes.extend(causes)
            node.causal_auto_learned = True
        if effects:
            node.causal_effects.extend(effects)
            node.causal_auto_learned = True
        
        # 2. 从共现学习
        cooccurrence = self.causal_learner.learn_from_cooccurrence(node)
        if cooccurrence['confidence']:
            node.causal_causes.extend(cooccurrence['causes'])
            node.causal_effects.extend(cooccurrence['effects'])
            node.causal_auto_learned = True
        
        # 3. 去重
        node.causal_causes = list(set(node.causal_causes))
        node.causal_effects = list(set(node.causal_effects))
    
    def _write_mem0(self, node: MemoryNode):
        """写入Mem0"""
        if not self.mem0_client:
            return
        try:
            self.mem0_client.add(
                messages=[{"role": "user", "content": node.content}],
                user_id="magma_hybrid"
            )
        except:
            pass
    
    def _write_milvus(self, node: MemoryNode):
        """写入Milvus"""
        if not self.milvus_client or not node.semantic_embedding:
            return
        try:
            self.milvus_client.insert(
                collection_name=self.milvus_collection,
                data=[{
                    "id": node.id,
                    "content": node.content[:500],
                    "vector": node.semantic_embedding,
                    "source": node.source,
                    "created_at": node.created_at
                }]
            )
        except:
            pass
    
    def _update_indices(self, node: MemoryNode):
        """更新索引"""
        for kw in node.semantic_keywords:
            if kw not in self.keyword_index:
                self.keyword_index[kw] = set()
            self.keyword_index[kw].add(node.id)
        
        self.sequence_index[node.temporal_sequence] = node.id
        
        for entity in node.entity_subjects + node.entity_objects + node.entity_concepts:
            if entity not in self.entity_index:
                self.entity_index[entity] = set()
            self.entity_index[entity].add(node.id)
    
    def get_node(self, node_id: str) -> Optional[MemoryNode]:
        return self.nodes.get(node_id)
    
    def get_recent_nodes(self, limit: int = 10) -> List[MemoryNode]:
        sequences = sorted(self.sequence_index.keys(), reverse=True)
        result = []
        for seq in sequences[:limit]:
            node_id = self.sequence_index.get(seq)
            if node_id and node_id in self.nodes:
                result.append(self.nodes[node_id])
        return result
    
    def save(self):
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
        if not self.storage_path or not Path(self.storage_path).exists():
            return
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.nodes = {k: MemoryNode.from_dict(v) for k, v in data.get("nodes", {}).items()}
        self.sequence_counter = data.get("sequence_counter", 0)
        self.keyword_index = {k: set(v) for k, v in data.get("keyword_index", {}).items()}
        self.entity_index = {k: set(v) for k, v in data.get("entity_index", {}).items()}
        
        for node in self.nodes.values():
            self.sequence_index[node.temporal_sequence] = node.id


class HybridRetrievalV2:
    """
    三写混合检索引擎
    
    检索流程：
    1. MAGMA四维检索（语义+时间+因果+实体）
    2. Mem0向量检索（快速粗筛）
    3. Milvus向量检索（精准匹配）
    4. 三路结果加权融合
    """
    
    def __init__(self, graph: MemoryGraphV2):
        self.graph = graph
        # 权重配置
        self.weights = {
            'magma': 0.4,    # MAGMA图谱权重
            'mem0': 0.3,      # Mem0权重
            'milvus': 0.3    # Milvus权重
        }
    
    def retrieve(self, query: str, query_embedding: List[float] = None,
                 top_k: int = 10) -> List[Dict]:
        """
        三路检索融合
        """
        # 1. MAGMA四维检索
        magma_results = self._magma_search(query, top_k * 2)
        
        # 2. Mem0检索（如果可用）
        mem0_results = []
        if self.graph.mem0_client:
            mem0_results = self._mem0_search(query, top_k * 2)
        
        # 3. Milvus检索（如果可用）
        milvus_results = []
        if self.graph.milvus_client and query_embedding:
            milvus_results = self._milvus_search(query_embedding, top_k * 2)
        
        # 4. 加权融合
        fused_results = self._fuse_results(
            query, 
            magma_results, 
            mem0_results, 
            milvus_results,
            top_k
        )
        
        return fused_results
    
    def _magma_search(self, query: str, top_k: int) -> Dict[str, float]:
        """MAGMA四维检索"""
        scores = {}
        
        # 提取关键词
        stopwords = {'的', '了', '是', '在', '和', '与'}
        words = re.findall(r'[\w]+', query)
        keywords = [w for w in words if len(w) >= 2 and w not in stopwords]
        
        # 关键词匹配
        for kw in keywords:
            node_ids = self.graph.keyword_index.get(kw, set())
            for nid in node_ids:
                scores[nid] = scores.get(nid, 0) + 0.25
        
        # 时间衰减
        max_seq = self.graph.sequence_counter
        for node in self.graph.nodes.values():
            if max_seq > 0:
                recency = 0.5 ** ((max_seq - node.temporal_sequence) / 10)
                scores[node.id] = scores.get(node.id, 0) + 0.15 * recency
        
        # 实体匹配
        for node in self.graph.nodes.values():
            entities = set(node.entity_subjects + node.entity_objects + node.entity_concepts)
            matched = [w for w in keywords if w in entities]
            if matched:
                scores[node.id] = scores.get(node.id, 0) + 0.2 * len(matched)
        
        return scores
    
    def _mem0_search(self, query: str, top_k: int) -> List[str]:
        """Mem0检索"""
        try:
            results = self.graph.mem0_client.search(
                query=query,
                user_id="magma_hybrid",
                limit=top_k
            )
            return [r.get('id') or r.get('memory_id') for r in results]
        except:
            return []
    
    def _milvus_search(self, query_embedding: List[float], top_k: int) -> List[str]:
        """Milvus向量检索"""
        try:
            results = self.graph.milvus_client.search(
                collection_name=self.graph.milvus_collection,
                data=[query_embedding],
                limit=top_k
            )
            return [r['id'] for r in results[0]] if results else []
        except:
            return []
    
    def _fuse_results(self, query: str, magma_scores: Dict[str, float],
                    mem0_results: List[str], milvus_results: List[str],
                    top_k: int) -> List[Dict]:
        """三路结果加权融合"""
        # 归一化MAGMA得分
        if magma_scores:
            max_score = max(magma_scores.values())
            if max_score > 0:
                magma_scores = {k: v / max_score for k, v in magma_scores.items()}
        
        # 计算综合得分
        final_scores = {}
        all_ids = set(magma_scores.keys())
        
        # 添加Mem0结果
        for i, nid in enumerate(mem0_results[:top_k]):
            all_ids.add(nid)
            final_scores[nid] = final_scores.get(nid, 0) + self.weights['mem0'] * (1.0 - i * 0.05)
        
        # 添加Milvus结果
        for i, nid in enumerate(milvus_results[:top_k]):
            all_ids.add(nid)
            final_scores[nid] = final_scores.get(nid, 0) + self.weights['milvus'] * (1.0 - i * 0.05)
        
        # 添加MAGMA结果
        for nid, score in magma_scores.items():
            final_scores[nid] = final_scores.get(nid, 0) + self.weights['magma'] * score
        
        # 排序
        ranked = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 构建结果
        results = []
        for nid, score in ranked[:top_k]:
            node = self.graph.get_node(nid)
            if node:
                results.append({
                    "node": node,
                    "score": round(score, 3),
                    "source": self._get_score_sources(nid, magma_scores, mem0_results, milvus_results)
                })
        
        return results
    
    def _get_score_sources(self, node_id: str, magma_scores: Dict, 
                         mem0_results: List, milvus_results: List) -> List[str]:
        sources = []
        if node_id in magma_scores and magma_scores[node_id] > 0:
            sources.append("magma")
        if node_id in mem0_results:
            sources.append("mem0")
        if node_id in milvus_results:
            sources.append("milvus")
        return sources


class MAGMAHybridV2:
    """MAGMA + Mem0 + Milvus 三写混合系统"""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or str(Path(__file__).parent / "magma_hybrid.json")
        self.graph = MemoryGraphV2(self.storage_path)
        self.retriever = HybridRetrievalV2(self.graph)
    
    def add(self, content: str, source: str = "manual",
            keywords: List[str] = None,
            entities: Dict[str, List[str]] = None,
            embedding: List[float] = None) -> str:
        """添加记忆（三写）"""
        # 提取关键词
        stopwords = {'的', '了', '是', '在', '和', '与', '或', '以及'}
        words = re.findall(r'[\w]+', content)
        extracted_kw = [w for w in words if len(w) >= 2 and w not in stopwords]
        if keywords:
            extracted_kw.extend(keywords)
        extracted_kw = list(set(extracted_kw))[:10]
        
        # 提取实体
        extracted_entities = {'subjects': [], 'objects': [], 'concepts': []}
        if entities:
            for k in ['subjects', 'objects', 'concepts']:
                if k in entities:
                    extracted_entities[k] = entities[k]
        
        # 创建节点
        node = MemoryNode(
            content=content,
            source=source,
            semantic_keywords=extracted_kw,
            semantic_embedding=embedding,
            entity_subjects=extracted_entities.get('subjects', []),
            entity_objects=extracted_entities.get('objects', []),
            entity_concepts=extracted_entities.get('concepts', [])
        )
        
        # 三写
        node_id = self.graph.add_node(node, enable_causal_learn=True)
        self.graph.save()
        
        return node_id
    
    def search(self, query: str, query_embedding: List[float] = None, 
               top_k: int = 10) -> List[Dict]:
        """检索记忆（三路融合）"""
        return self.retriever.retrieve(query, query_embedding, top_k)
    
    def get_recent(self, limit: int = 10) -> List[MemoryNode]:
        return self.graph.get_recent_nodes(limit)
    
    def get_causal_chain(self, node_id: str, depth: int = 3) -> Dict:
        node = self.graph.get_node(node_id)
        if not node:
            return {}
        
        chain = {"node": node.to_dict(), "causes": [], "effects": []}
        
        # 收集原因
        visited = set()
        self._collect_causal(node.causal_causes, chain["causes"], visited, depth - 1, "cause")
        
        # 收集结果
        visited = set()
        self._collect_causal(node.causal_effects, chain["effects"], visited, depth - 1, "effect")
        
        return chain
    
    def _collect_causal(self, node_ids: List[str], target: list, 
                      visited: set, depth: int, direction: str):
        if depth <= 0:
            return
        for nid in node_ids:
            if nid in visited:
                continue
            visited.add(nid)
            other = self.graph.get_node(nid)
            if other:
                target.append({
                    "id": other.id,
                    "content": other.content[:80],
                    "auto_learned": other.causal_auto_learned
                })
                if direction == "cause":
                    self._collect_causal(other.causal_causes, target, visited, depth - 1, direction)
                else:
                    self._collect_causal(other.causal_effects, target, visited, depth - 1, direction)
    
    def stats(self) -> dict:
        auto_learned = sum(1 for n in self.graph.nodes.values() if n.causal_auto_learned)
        return {
            "total_nodes": len(self.graph.nodes),
            "sequence_counter": self.graph.sequence_counter,
            "keywords": len(self.graph.keyword_index),
            "entities": len(self.graph.entity_index),
            "auto_learned_causal": auto_learned,
            "mem0_connected": self.graph.mem0_client is not None,
            "milvus_connected": self.graph.milvus_client is not None
        }


# 全局实例
_global_v2 = None

def get_hybrid_v2() -> MAGMAHybridV2:
    global _global_v2
    if _global_v2 is None:
        _global_v2 = MAGMAHybridV2()
    return _global_v2
