# -*- coding: utf-8 -*-
"""
MAGMA 四维检索引擎
"""
import re
from typing import List, Dict, Optional, Tuple
from .core import MemoryGraph, MemoryNode


class RetrievalEngine:
    """四维检索引擎"""
    
    def __init__(self, graph: MemoryGraph):
        self.graph = graph
        # 四维权重配置
        self.weights = {
            'semantic': 0.3,   # 语义权重
            'temporal': 0.2,   # 时间权重
            'causal': 0.3,     # 因果权重
            'entity': 0.2      # 实体权重
        }
    
    def set_weights(self, semantic: float = 0.3, temporal: float = 0.2, 
                   causal: float = 0.3, entity: float = 0.2):
        """设置检索权重"""
        total = semantic + temporal + causal + entity
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        self.weights = {
            'semantic': semantic,
            'temporal': temporal,
            'causal': causal,
            'entity': entity
        }
    
    def retrieve(self, query: str, top_k: int = 10, 
                 time_weight: str = "recent") -> List[Dict]:
        """
        四维检索主入口
        
        Args:
            query: 查询文本
            top_k: 返回前K个结果
            time_weight: 时间权重模式
                - "recent": 优先近期记忆
                - - "all": 不考虑时间
                - "decay": 时间衰减
        
        Returns:
            List of retrieval results with scores
        """
        # 1. 提取查询关键词和实体
        query_keywords = self._extract_keywords(query)
        query_entities = self._extract_entities(query)
        
        # 2. 并行四维检索
        semantic_scores = self._semantic_search(query_keywords)
        temporal_scores = self._temporal_search(time_weight)
        causal_scores = self._causal_search(query_keywords + query_entities)
        entity_scores = self._entity_search(query_entities)
        
        # 3. 加权融合
        final_scores = {}
        all_node_ids = set()
        for scores in [semantic_scores, temporal_scores, causal_scores, entity_scores]:
            all_node_ids.update(scores.keys())
        
        for node_id in all_node_ids:
            score = (
                self.weights['semantic'] * semantic_scores.get(node_id, 0) +
                self.weights['temporal'] * temporal_scores.get(node_id, 0) +
                self.weights['causal'] * causal_scores.get(node_id, 0) +
                self.weights['entity'] * entity_scores.get(node_id, 0)
            )
            final_scores[node_id] = score
        
        # 4. 排序返回
        ranked = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for node_id, score in ranked[:top_k]:
            node = self.graph.get_node(node_id)
            if node:
                results.append({
                    "node": node,
                    "score": round(score, 3),
                    "dimensions": {
                        "semantic": semantic_scores.get(node_id, 0),
                        "temporal": temporal_scores.get(node_id, 0),
                        "causal": causal_scores.get(node_id, 0),
                        "entity": entity_scores.get(node_id, 0)
                    },
                    "reason": self._explain_score(node, query_keywords, query_entities)
                })
        
        return results
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单分词 + 停用词过滤
        stopwords = {'的', '了', '是', '在', '和', '与', '或', '以及', '等', '这', '那', '有', '没有'}
        words = re.findall(r'[\w]+', text)
        return [w for w in words if len(w) >= 2 and w not in stopwords]
    
    def _extract_entities(self, text: str) -> List[str]:
        """提取实体（简单版：人名、机构名等）"""
        # 识别引号内的内容作为实体
        entities = re.findall(r'[""]([^""]+)[""]', text)
        # 识别@提及
        mentions = re.findall(r'@(\w+)', text)
        return entities + mentions
    
    def _semantic_search(self, keywords: List[str]) -> Dict[str, float]:
        """语义维度检索"""
        scores = {}
        for kw in keywords:
            node_ids = self.graph.keyword_index.get(kw, set())
            for nid in node_ids:
                scores[nid] = scores.get(nid, 0) + 1.0 / len(keywords)
        return scores
    
    def _temporal_search(self, mode: str = "recent") -> Dict[str, float]:
        """时间维度检索"""
        scores = {}
        if mode == "recent":
            # 近期记忆得分更高
            max_seq = self.graph.sequence_counter
            for node in self.graph.nodes.values():
                if max_seq > 0:
                    # 指数衰减
                    scores[node.id] = 0.5 ** ((max_seq - node.temporal_sequence) / 10)
        elif mode == "all":
            # 所有记忆等权重
            for node in self.graph.nodes:
                scores[node] = 1.0
        return scores
    
    def _causal_search(self, keywords: List[str]) -> Dict[str, float]:
        """因果维度检索"""
        scores = {}
        for node in self.graph.nodes.values():
            # 检查因果链中是否有匹配的节点
            causal_score = 0.0
            if node.causal_causes or node.causal_effects:
                # 检查原因/结果节点的内容
                for cause_id in node.causal_causes:
                    cause_node = self.graph.get_node(cause_id)
                    if cause_node:
                        for kw in keywords:
                            if kw in cause_node.content:
                                causal_score += 0.3
                for effect_id in node.causal_effects:
                    effect_node = self.graph.get_node(effect_id)
                    if effect_node:
                        for kw in keywords:
                            if kw in effect_node.content:
                                causal_score += 0.3
            if causal_score > 0:
                scores[node.id] = min(causal_score, 1.0)
        return scores
    
    def _entity_search(self, entities: List[str]) -> Dict[str, float]:
        """实体维度检索"""
        scores = {}
        for entity in entities:
            node_ids = self.graph.entity_index.get(entity, set())
            for nid in node_ids:
                scores[nid] = scores.get(nid, 0) + 1.0
        return scores
    
    def _explain_score(self, node: MemoryNode, 
                      query_keywords: List[str], 
                      query_entities: List[str]) -> str:
        """解释得分原因"""
        reasons = []
        
        # 检查语义匹配
        matched_kw = [kw for kw in query_keywords if kw in node.semantic_keywords]
        if matched_kw:
            reasons.append(f"语义匹配: {', '.join(matched_kw)}")
        
        # 检查实体匹配
        matched_ent = [e for e in query_entities 
                      if e in node.entity_subjects + node.entity_objects + node.entity_concepts]
        if matched_ent:
            reasons.append(f"实体匹配: {', '.join(matched_ent)}")
        
        # 检查因果关系
        if node.causal_causes or node.causal_effects:
            reasons.append(f"因果关联: {len(node.causal_causes)}个原因, {len(node.causal_effects)}个结果")
        
        # 时间信息
        reasons.append(f"时间: {node.temporal_date} {node.temporal_period}")
        
        return " | ".join(reasons) if reasons else "基础匹配"


def retrieve(query: str, graph: MemoryGraph, top_k: int = 10) -> List[Dict]:
    """便捷检索函数"""
    engine = RetrievalEngine(graph)
    return engine.retrieve(query, top_k=top_k)
