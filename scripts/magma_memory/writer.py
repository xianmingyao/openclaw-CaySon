# -*- coding: utf-8 -*-
"""
MAGMA 记忆写入接口
"""
from typing import Optional, List, Dict
from .core import MemoryGraph, MemoryNode
from .entity import EntityExtractor, CausalExtractor, KeywordExtractor


class MemoryWriter:
    """记忆写入器"""
    
    def __init__(self, graph: MemoryGraph):
        self.graph = graph
        self.entity_extractor = EntityExtractor()
        self.causal_extractor = CausalExtractor()
        self.keyword_extractor = KeywordExtractor()
    
    def add(self, content: str, 
            source: str = "manual",
            keywords: List[str] = None,
            entities: Dict[str, List[str]] = None,
            causal_links: Dict = None) -> str:
        """
        添加记忆
        
        Args:
            content: 记忆内容
            source: 来源 (wechat/douyin/doc/manual)
            keywords: 额外关键词（可选）
            entities: 额外实体（可选）
            causal_links: 因果链接（可选）
        
        Returns:
            node_id
        """
        # 1. 提取关键词
        extracted_keywords = self.keyword_extractor.extract(content)
        if keywords:
            extracted_keywords.extend(keywords)
        extracted_keywords = list(set(extracted_keywords))[:10]  # 最多10个
        
        # 2. 提取实体
        extracted_entities = self.entity_extractor.extract(content)
        if entities:
            for key in ['subjects', 'objects', 'concepts']:
                if key in entities:
                    extracted_entities[key].extend(entities[key])
                    extracted_entities[key] = list(set(extracted_entities[key]))
        
        # 3. 推断因果
        causal_info = self.causal_extractor.extract(content, {'keywords': extracted_keywords})
        if causal_links:
            causal_info.update(causal_links)
        
        # 4. 创建节点
        node = MemoryNode(
            content=content,
            source=source,
            semantic_keywords=extracted_keywords,
            entity_subjects=extracted_entities.get('subjects', []),
            entity_objects=extracted_entities.get('objects', []),
            entity_concepts=extracted_entities.get('concepts', []),
            causal_causes=causal_info.get('causes', []),
            causal_effects=causal_info.get('effects', []),
            causal_strength=causal_info.get('strength', 0.5)
        )
        
        # 5. 写入图谱
        node_id = self.graph.add_node(node)
        
        # 6. 保存
        self.graph.save()
        
        return node_id
    
    def add_batch(self, items: List[Dict]) -> List[str]:
        """
        批量添加记忆
        
        Args:
            items: List of {
                'content': str,
                'source': str,
                'keywords': List[str],
                'entities': Dict,
                'causal_links': Dict
            }
        
        Returns:
            List of node_ids
        """
        node_ids = []
        for item in items:
            node_id = self.add(
                content=item['content'],
                source=item.get('source', 'manual'),
                keywords=item.get('keywords'),
                entities=item.get('entities'),
                causal_links=item.get('causal_links')
            )
            node_ids.append(node_id)
        return node_ids
    
    def update_causal_link(self, cause_node_id: str, effect_node_id: str, strength: float = 0.5):
        """更新因果链接"""
        cause_node = self.graph.get_node(cause_node_id)
        effect_node = self.graph.get_node(effect_node_id)
        
        if cause_node and effect_node:
            if effect_node_id not in cause_node.causal_effects:
                cause_node.causal_effects.append(effect_node_id)
            if cause_node_id not in effect_node.causal_causes:
                effect_node.causal_causes.append(cause_node_id)
            
            cause_node.causal_strength = max(cause_node.causal_strength, strength)
            effect_node.causal_strength = max(effect_node.causal_strength, strength)
            
            self.graph.save()
    
    def delete(self, node_id: str):
        """删除记忆"""
        if node_id in self.graph.nodes:
            del self.graph.nodes[node_id]
            self.graph.save()
