# -*- coding: utf-8 -*-
"""
遗忘机制模块 - 基于时间衰减和访问频率的智能遗忘

解决 Karpathy LLM Wiki 的"数字坟墓"问题：
- 超过 N 天未访问的知识自动降权
- 长期未使用但重要的知识保留（重要性加权）
- 可配置衰减速率
"""
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import math


@dataclass
class DecayConfig:
    """遗忘配置"""
    max_idle_days: int = 30          # 最大空闲天数（超过此天数权重降至50%）
    decay_base: float = 0.5           # 衰减底数
    decay_rate: float = 0.1           # 每日衰减率
    importance_boost: float = 0.5      # 重要性加分（防止重要知识被遗忘）
    min_decay_score: float = 0.1      # 最低衰减分数（永远不完全消失）


class ForgettingManager:
    """遗忘管理器"""
    
    def __init__(self, graph, config: DecayConfig = None):
        self.graph = graph
        self.config = config or DecayConfig()
    
    def calculate_decay(self, node) -> float:
        """
        计算单条记忆的衰减分数
        
        公式: decay = max(min_score, importance * base^(days_since_access) + boost)
        
        Returns:
            0.0 ~ 1.0 的衰减分数，1.0=最新鲜，0.1=几乎遗忘但保留
        """
        if not node.accessed_at:
            # 从未访问过，用 created_at 计算
            last_access = datetime.fromisoformat(node.created_at)
        else:
            last_access = datetime.fromisoformat(node.accessed_at)
        
        days_since = (datetime.now() - last_access).days
        
        if days_since <= 0:
            return 1.0  # 今天刚访问，完全新鲜
        
        # 基础衰减：base^(days)
        decay = self.config.decay_base ** (days_since * self.config.decay_rate)
        
        # 重要性加权：重要知识衰减更慢
        decay = decay * (1 - node.importance * self.config.importance_boost)
        
        # 确保不低于最低分数
        return max(self.config.min_decay_score, min(1.0, decay))
    
    def update_access(self, node_id: str) -> bool:
        """
        更新访问记录 + 刷新衰减分数
        
        Returns:
            True if node exists and was updated
        """
        node = self.graph.get_node(node_id)
        if not node:
            return False
        
        node.accessed_at = datetime.now().isoformat()
        node.access_count += 1
        node.decay_score = self.calculate_decay(node)
        node.updated_at = datetime.now().isoformat()
        
        self.graph.save()
        return True
    
    def get_decay_report(self) -> Dict:
        """
        获取全局衰减报告
        
        Returns:
            包含各衰减等级节点数量的统计
        """
        fresh = []        # 1.0 ~ 0.8
        normal = []       # 0.8 ~ 0.5
        aging = []        # 0.5 ~ 0.2
        fading = []       # 0.2 ~ min
        
        for node_id, node in self.graph.nodes.items():
            decay = self.calculate_decay(node)
            node.decay_score = decay  # 更新内存中的分数
            
            info = {
                "id": node_id,
                "content_preview": node.content[:50],
                "decay": round(decay, 3),
                "days_since_access": self._days_since(node),
                "access_count": node.access_count
            }
            
            if decay >= 0.8:
                fresh.append(info)
            elif decay >= 0.5:
                normal.append(info)
            elif decay >= 0.2:
                aging.append(info)
            else:
                fading.append(info)
        
        return {
            "total": len(self.graph.nodes),
            "fresh": len(fresh),
            "normal": len(normal),
            "aging": len(aging),
            "fading": len(fading),
            "fresh_nodes": fresh[:5],
            "aging_nodes": aging[:5],
            "fading_nodes": fading[:10]
        }
    
    def _days_since(self, node) -> int:
        """计算距离上次访问的天数"""
        if not node.accessed_at:
            last = datetime.fromisoformat(node.created_at)
        else:
            last = datetime.fromisoformat(node.accessed_at)
        return max(0, (datetime.now() - last).days)
    
    def prune_fading(self, threshold: float = None) -> List[str]:
        """
        清理即将遗忘的知识（软删除，不是真删）
        
        Args:
            threshold: 衰减分数阈值，默认 0.15
        
        Returns:
            被标记为 fading 的 node_id 列表
        """
        threshold = threshold or self.config.min_decay_score * 1.5
        pruned = []
        
        for node_id, node in self.graph.nodes.items():
            decay = self.calculate_decay(node)
            if decay < threshold:
                # 标记为 verified=False（表示"已遗忘但保留"）
                node.verified = False
                node.decay_score = decay
                pruned.append(node_id)
        
        if pruned:
            self.graph.save()
        
        return pruned
    
    def boost_importance(self, node_id: str, boost: float = 0.2) -> bool:
        """手动提升某条知识的重要性，防止被遗忘"""
        node = self.graph.get_node(node_id)
        if not node:
            return False
        
        node.importance = min(1.0, node.importance + boost)
        node.decay_score = self.calculate_decay(node)
        self.graph.save()
        return True
