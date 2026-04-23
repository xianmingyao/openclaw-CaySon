# -*- coding: utf-8 -*-
"""
MAGMA 记忆写入接口 v2.1
集成遗忘机制 + 冲突检测 + 检索验证

解决 Karpathy LLM Wiki 的五大缺陷：
1. ✅ 时间戳（created_at/updated_at/accessed_at）- 已集成
2. ✅ 遗忘机制（decay_score）- 已集成
3. ✅ 冲突检测（写入时自动检测）- 已集成
4. ✅ 检索验证（存后验证可检索性）- 已集成
"""
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from .core import MemoryGraph, MemoryNode
from .entity import EntityExtractor, CausalExtractor, KeywordExtractor
from .forgetting import ForgettingManager, DecayConfig
from .conflict_detector import ConflictDetector


class MemoryWriter:
    """记忆写入器 v2.1 - 集成遗忘+冲突检测+检索验证"""
    
    def __init__(self, graph: MemoryGraph, 
                 enable_forgetting: bool = True,
                 enable_conflict_check: bool = True,
                 enable_verification: bool = True,
                 decay_config: DecayConfig = None):
        self.graph = graph
        self.entity_extractor = EntityExtractor()
        self.causal_extractor = CausalExtractor()
        self.keyword_extractor = KeywordExtractor()
        
        # P0: 遗忘机制
        self.forgetting = ForgettingManager(graph, decay_config) if enable_forgetting else None
        
        # P1: 冲突检测
        self.conflict_detector = ConflictDetector(graph) if enable_conflict_check else None
        
        # P2: 检索验证（存后验证可检索性）
        self.verification_enabled = enable_verification
    
    def add(self, content: str, 
            source: str = "manual",
            keywords: List[str] = None,
            entities: Dict[str, List[str]] = None,
            causal_links: Dict = None,
            importance: float = 1.0) -> Tuple[str, Dict]:
        """
        添加记忆（集成遗忘+冲突检测+检索验证）
        
        Args:
            content: 记忆内容
            source: 来源 (wechat/douyin/doc/manual)
            keywords: 额外关键词（可选）
            entities: 额外实体（可选）
            causal_links: 因果链接（可选）
            importance: 重要性 0-1（影响遗忘速度）
        
        Returns:
            Tuple[node_id, report]
            report 包含: created, forgetting_score, conflicts, verified
        """
        now = datetime.now().isoformat()
        
        # 1. 提取关键词
        extracted_keywords = self.keyword_extractor.extract(content)
        if keywords:
            extracted_keywords.extend(keywords)
        extracted_keywords = list(set(extracted_keywords))[:10]
        
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
        
        # 4. 创建节点（P0: 时间戳已由 core.py 自动处理）
        node = MemoryNode(
            content=content,
            source=source,
            semantic_keywords=extracted_keywords,
            entity_subjects=extracted_entities.get('subjects', []),
            entity_objects=extracted_entities.get('objects', []),
            entity_concepts=extracted_entities.get('concepts', []),
            causal_causes=causal_info.get('causes', []),
            causal_effects=causal_info.get('effects', []),
            causal_strength=causal_info.get('strength', 0.5),
            importance=importance,
            accessed_at=now  # P0: 初始化访问时间
        )
        
        # 5. 写入图谱
        node_id = self.graph.add_node(node)
        
        # 6. 计算遗忘分数（P0）
        decay_score = self.forgetting.calculate_decay(node) if self.forgetting else 1.0
        
        # 7. 冲突检测（P1: 写入后立即检测）
        conflicts = []
        if self.conflict_detector:
            all_conflicts = self.conflict_detector.scan_all()
            # 只返回与新节点相关的冲突
            conflicts = [c for c in all_conflicts if node_id in c.node_ids]
        
        # 8. 检索验证（P2: 验证知识是否真的可被检索）
        verified = True
        if self.verification_enabled and self.forgetting:
            # 用内容关键词检索，看能不能找到自己
            test_results = self._verify_retrievability(node_id, extracted_keywords)
            verified = test_results
        
        # 9. 保存
        self.graph.save()
        
        report = {
            "created": True,
            "node_id": node_id,
            "decay_score": round(decay_score, 3),
            "conflicts": [
                {"type": c.type.value, "severity": c.severity, "description": c.description[:100]}
                for c in conflicts
            ],
            "verified": verified,  # P2: 是否可被检索
            "timestamp": now
        }
        
        return node_id, report
    
    def _verify_retrievability(self, node_id: str, keywords: List[str]) -> bool:
        """
        P2: 验证写入的知识是否真的可被检索到
        
        原理：用新节点的关键词做一次检索，看能否找回自己
        """
        from .retrieval import RetrievalEngine
        
        if not keywords:
            return True
        
        engine = RetrievalEngine(self.graph)
        
        # 用关键词检索
        query = " ".join(keywords[:5])
        results = engine.retrieve(query, top_k=5)
        
        # 检查自己是否在结果中
        result_ids = [r['node'].id for r in results]
        return node_id in result_ids
    
    def add_batch(self, items: List[Dict]) -> List[Tuple[str, Dict]]:
        """
        批量添加记忆
        
        Args:
            items: List of {
                'content': str,
                'source': str,
                'keywords': List[str],
                'entities': Dict,
                'causal_links': Dict,
                'importance': float
            }
        
        Returns:
            List of (node_id, report)
        """
        results = []
        for item in items:
            node_id, report = self.add(
                content=item['content'],
                source=item.get('source', 'manual'),
                keywords=item.get('keywords'),
                entities=item.get('entities'),
                causal_links=item.get('causal_links'),
                importance=item.get('importance', 1.0)
            )
            results.append((node_id, report))
        return results
    
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
            cause_node.updated_at = datetime.now().isoformat()
            effect_node.updated_at = datetime.now().isoformat()
            
            self.graph.save()
    
    def delete(self, node_id: str):
        """删除记忆"""
        if node_id in self.graph.nodes:
            del self.graph.nodes[node_id]
            self.graph.save()
    
    def get_full_report(self) -> Dict:
        """
        获取完整报告（整合三大模块）
        
        Returns:
            包含遗忘+冲突+检索统计的综合报告
        """
        report = {
            "timestamp": datetime.now().isoformat()
        }
        
        # 遗忘报告
        if self.forgetting:
            decay_report = self.forgetting.get_decay_report()
            report["forgetting"] = {
                "total": decay_report["total"],
                "fresh": decay_report["fresh"],
                "normal": decay_report["normal"],
                "aging": decay_report["aging"],
                "fading": decay_report["fading"]
            }
        
        # 冲突报告
        if self.conflict_detector:
            conflict_report = self.conflict_detector.get_conflict_report()
            report["conflicts"] = {
                "total": conflict_report["total_conflicts"],
                "by_severity": conflict_report["by_severity"]
            }
        
        return report
