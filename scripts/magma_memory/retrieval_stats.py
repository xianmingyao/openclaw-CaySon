# -*- coding: utf-8 -*-
"""
检索统计模块 - 追踪检索命中率，验证知识是否真的被记住

解决 Karpathy LLM Wiki 的"无法验证"问题：
- 每次检索后记录"知识是否被命中"
- 长期未被命中的知识标记为"可能已遗忘"
- 为遗忘机制提供数据支撑
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json


@dataclass
class RetrievalHit:
    """检索命中记录"""
    query: str
    node_id: str
    rank: int           # 在结果中的排名
    score: float        # 相关性得分
    retrieved_at: str   # 检索时间


@dataclass
class RetrievalMiss:
    """检索未命中记录（曾被查询但未返回）"""
    query: str
    node_id: str
    query_time: str     # 查询时间
    reason: str        # 未命中原因


@dataclass
class NodeRetrievalStats:
    """单条知识的检索统计"""
    node_id: str
    hit_count: int = 0          # 命中次数
    miss_count: int = 0         # 未命中次数
    last_hit_at: str = ""       # 上次命中时间
    last_miss_at: str = ""      # 上次未命中时间
    total_queries: int = 0      # 被查询的总次数
    hit_rate: float = 0.0       # 命中率
    avg_rank: float = 0.0       # 平均排名
    is_forgotten: bool = False   # 是否已被遗忘
    
    # 新增字段
    queries: List[str] = field(default_factory=list)  # 触发检索的查询


class RetrievalStats:
    """检索统计管理器"""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path
        # node_id -> NodeRetrievalStats
        self.stats: Dict[str, NodeRetrievalStats] = {}
        # 每次检索的详细记录
        self.hits: List[RetrievalHit] = []
        self.misses: List[RetrievalMiss] = []
        
        if storage_path and Path(storage_path).exists():
            self.load()
    
    def record_retrieval(self, results: List[Dict], query: str):
        """
        记录一次检索结果
        
        Args:
            results: retrieve() 返回的结果列表
            query: 查询文本
        """
        now = datetime.now().isoformat()
        
        # 记录命中的节点
        retrieved_node_ids = set()
        for rank, result in enumerate(results):
            node = result["node"]
            retrieved_node_ids.add(node.id)
            
            # 更新或创建统计
            if node.id not in self.stats:
                self.stats[node.id] = NodeRetrievalStats(node_id=node.id)
            
            stat = self.stats[node.id]
            stat.hit_count += 1
            stat.last_hit_at = now
            stat.total_queries += 1
            stat.queries.append(query)
            stat.queries = stat.queries[-10:]  # 保留最近10次查询
            
            # 更新平均排名
            stat.avg_rank = (stat.avg_rank * (stat.hit_count - 1) + rank + 1) / stat.hit_count
            
            # 更新命中率
            if stat.total_queries > 0:
                stat.hit_rate = stat.hit_count / stat.total_queries
            
            # 记录命中
            self.hits.append(RetrievalHit(
                query=query,
                node_id=node.id,
                rank=rank + 1,
                score=result.get("score", 0),
                retrieved_at=now
            ))
        
        # 记录未命中的节点（之前存在但这次没被命中的）
        for node_id, stat in self.stats.items():
            if node_id not in retrieved_node_ids:
                stat.miss_count += 1
                stat.last_miss_at = now
                stat.total_queries += 1
                stat.hit_rate = stat.hit_count / stat.total_queries
                
                self.misses.append(RetrievalMiss(
                    query=query,
                    node_id=node_id,
                    query_time=now,
                    reason="not_in_top_k"
                ))
        
        # 清理历史记录（只保留最近1000条）
        self.hits = self.hits[-1000:]
        self.misses = self.misses[-1000:]
        
        self.save()
    
    def get_forgotten_knowledge(self, threshold_hits: int = 5, 
                                threshold_rate: float = 0.2,
                                days_threshold: int = 7) -> List[str]:
        """
        获取"被遗忘"的知识列表
        
        条件：命中次数 < threshold_hits AND 命中率 < threshold_rate AND 多天未被命中
        
        Returns:
            node_id 列表
        """
        forgotten = []
        now = datetime.now()
        
        for node_id, stat in self.stats.items():
            if stat.total_queries < 3:  # 查询次数太少，不判定
                continue
            
            # 检查是否长期未命中
            if stat.last_hit_at:
                last_hit = datetime.fromisoformat(stat.last_hit_at)
                days_since_hit = (now - last_hit).days
                
                if days_since_hit > days_threshold and stat.hit_rate < threshold_rate:
                    stat.is_forgotten = True
                    forgotten.append(node_id)
        
        return forgotten
    
    def get_hot_knowledge(self, top_n: int = 10) -> List[Dict]:
        """获取最热门（最常被命中）的知识"""
        sorted_stats = sorted(
            self.stats.items(),
            key=lambda x: (x[1].hit_count, x[1].avg_rank),
            reverse=True
        )
        
        result = []
        for node_id, stat in sorted_stats[:top_n]:
            result.append({
                "node_id": node_id,
                "hit_count": stat.hit_count,
                "hit_rate": round(stat.hit_rate, 3),
                "avg_rank": round(stat.avg_rank, 1),
                "last_hit_at": stat.last_hit_at,
                "is_forgotten": stat.is_forgotten
            })
        
        return result
    
    def get_cold_knowledge(self, top_n: int = 10) -> List[Dict]:
        """获取最冷门（很少被命中）的知识"""
        sorted_stats = sorted(
            self.stats.items(),
            key=lambda x: (x[1].hit_count, -x[1].miss_count)
        )
        
        result = []
        for node_id, stat in sorted_stats[:top_n]:
            if stat.total_queries > 0:  # 只返回被查询过的
                result.append({
                    "node_id": node_id,
                    "hit_count": stat.hit_count,
                    "miss_count": stat.miss_count,
                    "hit_rate": round(stat.hit_rate, 3),
                    "avg_rank": round(stat.avg_rank, 1),
                    "last_hit_at": stat.last_hit_at,
                    "is_forgotten": stat.is_forgotten
                })
        
        return result
    
    def get_report(self) -> Dict:
        """获取完整统计报告"""
        total_nodes = len(self.stats)
        total_queries = sum(s.total_queries for s in self.stats.values())
        total_hits = sum(s.hit_count for s in self.stats.values())
        
        forgotten = self.get_forgotten_knowledge()
        hot = self.get_hot_knowledge(5)
        cold = self.get_cold_knowledge(5)
        
        return {
            "summary": {
                "total_tracked_nodes": total_nodes,
                "total_queries": total_queries,
                "total_hits": total_hits,
                "overall_hit_rate": round(total_hits / total_queries, 3) if total_queries > 0 else 0,
                "forgotten_count": len(forgotten),
                "forgotten_rate": round(len(forgotten) / total_nodes, 3) if total_nodes > 0 else 0
            },
            "forgotten_knowledge": forgotten,
            "hot_knowledge": hot,
            "cold_knowledge": cold,
            "recent_hits": [
                {"node_id": h.node_id, "query": h.query[:50], "rank": h.rank, "at": h.retrieved_at}
                for h in self.hits[-10:]
            ]
        }
    
    def save(self):
        """保存到磁盘"""
        if not self.storage_path:
            return
        
        data = {
            "stats": {
                k: {
                    "node_id": v.node_id,
                    "hit_count": v.hit_count,
                    "miss_count": v.miss_count,
                    "last_hit_at": v.last_hit_at,
                    "last_miss_at": v.last_miss_at,
                    "total_queries": v.total_queries,
                    "hit_rate": v.hit_rate,
                    "avg_rank": v.avg_rank,
                    "is_forgotten": v.is_forgotten,
                    "queries": v.queries
                }
                for k, v in self.stats.items()
            }
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
        
        self.stats = {
            k: NodeRetrievalStats(**v)
            for k, v in data.get("stats", {}).items()
        }
