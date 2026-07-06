# -*- coding: utf-8 -*-
"""
冲突检测模块 - 检测同一概念的矛盾说法

解决 Karpathy LLM Wiki 的"自我矛盾"问题：
- 同一实体在不同时间点有矛盾的说法
- 同一因果链中的逻辑冲突
- 时间线上的事实不一致
"""
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import re


class ConflictType(Enum):
    """冲突类型"""
    TEMPORAL_CONTRADICTION = "temporal_contradiction"    # 时间矛盾（前后不一致）
    CAUSAL_LOOP = "causal_loop"                          # 因果循环
    ENTITY_CONFLICT = "entity_conflict"                  # 实体属性冲突
    SEMANTIC_CONFLICT = "semantic_conflict"              # 语义矛盾
    DUPLICATE = "duplicate"                               # 重复内容


@dataclass
class Conflict:
    """冲突信息"""
    type: ConflictType
    node_ids: List[str]
    description: str
    severity: str  # high / medium / low
    resolution: str = ""  # 建议的解决方案


@dataclass
class EntityState:
    """实体的状态快照（用于追踪历史变化）"""
    entity: str
    attribute: str
    value: str
    node_id: str
    temporal_date: str
    is_current: bool = True


class ConflictDetector:
    """冲突检测器"""
    
    def __init__(self, graph):
        self.graph = graph
        # 实体状态历史：entity -> attribute -> List[EntityState]
        self.entity_history: Dict[str, Dict[str, List[EntityState]]] = {}
    
    def scan_all(self) -> List[Conflict]:
        """
        全量扫描所有潜在冲突
        
        Returns:
            冲突列表
        """
        conflicts = []
        conflicts.extend(self._detect_temporal_conflicts())
        conflicts.extend(self._detect_causal_loops())
        conflicts.extend(self._detect_entity_conflicts())
        conflicts.extend(self._detect_duplicates())
        return conflicts
    
    def _detect_temporal_conflicts(self) -> List[Conflict]:
        """检测时间矛盾：同一实体属性在不同时期说法不同"""
        conflicts = []
        
        # 按实体聚合节点
        entity_nodes: Dict[str, List] = {}
        for node_id, node in self.graph.nodes.items():
            for entity in node.entity_subjects:
                if entity not in entity_nodes:
                    entity_nodes[entity] = []
                entity_nodes[entity].append((node_id, node))
        
        # 检查同一实体在不同时间点的说法
        for entity, nodes in entity_nodes.items():
            if len(nodes) < 2:
                continue
            
            # 按时间排序
            nodes.sort(key=lambda x: x[1].temporal_sequence)
            
            # 检查相邻节点是否有矛盾
            for i in range(len(nodes) - 1):
                nid1, node1 = nodes[i]
                nid2, node2 = nodes[i + 1]
                
                # 检查是否有时序矛盾
                if self._has_temporal_contradiction(node1, node2):
                    conflicts.append(Conflict(
                        type=ConflictType.TEMPORAL_CONTRADICTION,
                        node_ids=[nid1, nid2],
                        description=f"实体「{entity}」在不同时期说法矛盾：\n"
                                   f"  [{node1.temporal_date}] {node1.content[:80]}...\n"
                                   f"  [{node2.temporal_date}] {node2.content[:80]}...",
                        severity="medium",
                        resolution=f"保留最新 [{node2.temporal_date}] 的说法，或合并两者"
                    ))
        
        return conflicts
    
    def _has_temporal_contradiction(self, node1, node2) -> bool:
        """检测两条记忆是否存在时间矛盾"""
        # 检测否定词变化（之前说"是"，后来又说"不是"）
        negations = ["不是", "没有", "不", "否", "无", "非", "取消", "停止", "删除"]
        
        content1 = node1.content
        content2 = node2.content
        
        # 检查第一条是否有否定
        has_neg1 = any(neg in content1 for neg in negations)
        has_neg2 = any(neg in content2 for neg in negations)
        
        # 如果前后出现否定词变化，且内容有重叠关键词，可能是矛盾
        if has_neg1 != has_neg2:
            # 检查关键词重叠
            kw1 = set(node1.semantic_keywords)
            kw2 = set(node2.semantic_keywords)
            if kw1 & kw2:  # 有共同关键词
                return True
        
        return False
    
    def _detect_causal_loops(self) -> List[Conflict]:
        """检测因果循环：A导致B，B导致A"""
        conflicts = []
        
        for node_id, node in self.graph.nodes.items():
            if not node.causal_effects:
                continue
            
            # DFS 检测循环
            visited = set()
            path = []
            
            def dfs(current_id: str, path: List) -> Optional[List[str]]:
                if current_id in path:
                    # 发现循环
                    cycle_start = path.index(current_id)
                    return path[cycle_start:] + [current_id]
                
                if current_id in visited:
                    return None
                
                visited.add(current_id)
                current_node = self.graph.get_node(current_id)
                
                if not current_node or not current_node.causal_effects:
                    return None
                
                for effect_id in current_node.causal_effects:
                    result = dfs(effect_id, path + [current_id])
                    if result:
                        return result
                
                return None
            
            cycle = dfs(node_id, [])
            if cycle:
                conflicts.append(Conflict(
                    type=ConflictType.CAUSAL_LOOP,
                    node_ids=cycle,
                    description=f"发现因果循环：{' → '.join(cycle[:5])}...",
                    severity="high",
                    resolution="断开其中一条因果链接"
                ))
        
        return conflicts
    
    def _detect_entity_conflicts(self) -> List[Conflict]:
        """检测实体属性冲突：同一实体的同一属性出现矛盾"""
        conflicts = []
        
        # 收集所有实体状态
        for node_id, node in self.graph.nodes.items():
            for entity in node.entity_subjects:
                # 提取实体属性（从内容中简单提取）
                attrs = self._extract_attributes(node.content)
                for attr, value in attrs.items():
                    if entity not in self.entity_history:
                        self.entity_history[entity] = {}
                    if attr not in self.entity_history[entity]:
                        self.entity_history[entity][attr] = []
                    
                    self.entity_history[entity][attr].append(EntityState(
                        entity=entity,
                        attribute=attr,
                        value=value,
                        node_id=node_id,
                        temporal_date=node.temporal_date,
                        is_current=True
                    ))
        
        # 检测矛盾
        for entity, attrs in self.entity_history.items():
            for attr, states in attrs.items():
                if len(states) < 2:
                    continue
                
                # 检查是否有不同的值
                unique_values = set(s.value for s in states)
                if len(unique_values) > 1:
                    # 找到了矛盾
                    latest = max(states, key=lambda s: s.temporal_date)
                    conflicts.append(Conflict(
                        type=ConflictType.ENTITY_CONFLICT,
                        node_ids=[s.node_id for s in states],
                        description=f"实体「{entity}」的属性「{attr}」存在矛盾：\n"
                                   f"  历史值: {', '.join(unique_values)}\n"
                                   f"  最新值: {latest.value} ({latest.temporal_date})",
                        severity="medium",
                        resolution=f"确认最新值 {latest.value} 是否正确"
                    ))
        
        return conflicts
    
    def _extract_attributes(self, content: str) -> Dict[str, str]:
        """从内容中提取属性（简单版）"""
        attrs = {}
        
        # 匹配模式：实体是/在/有 + 属性
        patterns = [
            r'([\w]+)是([\w]+)',      # X是Y
            r'([\w]+)在([\w]+)',      # X在Y
            r'([\w]+)有([\w]+)',      # X有Y
            r'([\w]+)位于([\w]+)',    # X位于Y
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) == 2:
                    attrs[match[1]] = match[1]
        
        return attrs
    
    def _detect_duplicates(self) -> List[Conflict]:
        """检测重复内容"""
        conflicts = []
        
        # 按关键词指纹去重
        fingerprints: Dict[str, List] = {}
        
        for node_id, node in self.graph.nodes.items():
            # 简单指纹：关键词集合的哈希
            fingerprint = frozenset(node.semantic_keywords[:5])
            if fingerprint not in fingerprints:
                fingerprints[fingerprint] = []
            fingerprints[fingerprint].append(node_id)
        
        # 找出重复的
        for fingerprint, node_ids in fingerprints.items():
            if len(node_ids) >= 3:
                # 超过3条相似内容的，可能是重复
                conflicts.append(Conflict(
                    type=ConflictType.DUPLICATE,
                    node_ids=node_ids,
                    description=f"发现 {len(node_ids)} 条高度相似的内容（关键词指纹相同）",
                    severity="low",
                    resolution="合并重复内容，保留信息最完整的一条"
                ))
        
        return conflicts
    
    def get_conflict_report(self) -> Dict:
        """获取冲突报告"""
        conflicts = self.scan_all()
        
        return {
            "total_conflicts": len(conflicts),
            "by_type": {
                ct.value: len([c for c in conflicts if c.type == ct])
                for ct in ConflictType
            },
            "by_severity": {
                "high": len([c for c in conflicts if c.severity == "high"]),
                "medium": len([c for c in conflicts if c.severity == "medium"]),
                "low": len([c for c in conflicts if c.severity == "low"])
            },
            "conflicts": [
                {
                    "type": c.type.value,
                    "node_ids": c.node_ids,
                    "description": c.description,
                    "severity": c.severity,
                    "resolution": c.resolution
                }
                for c in conflicts
            ]
        }
