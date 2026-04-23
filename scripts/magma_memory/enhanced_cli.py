#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MAGMA 增强版 CLI
整合：遗忘机制 + 冲突检测 + 检索统计 + 检索验证

用法:
  python enhanced_cli.py --forgetting-report    # 遗忘报告
  python enhanced_cli.py --conflict-report       # 冲突报告
  python enhanced_cli.py --stats-report          # 检索统计
  python enhanced_cli.py --verify-all            # 完整验证报告
  python enhanced_cli.py --prune                # 清理被遗忘知识
  python enhanced_cli.py --search "查询"         # 检索并记录统计
"""
import sys
import io
import argparse
from pathlib import Path
import sys

# UTF-8 输出修复
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到 path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.magma_memory.core import MemoryGraph
from scripts.magma_memory.retrieval import RetrievalEngine
from scripts.magma_memory.forgetting import ForgettingManager, DecayConfig
from scripts.magma_memory.conflict_detector import ConflictDetector
from scripts.magma_memory.retrieval_stats import RetrievalStats


def get_storage_dir():
    """获取存储目录"""
    return project_root / "scripts" / "magma_memory" / "data"


def main():
    parser = argparse.ArgumentParser(description='MAGMA 增强工具')
    parser.add_argument('--forgetting-report', action='store_true', help='遗忘报告')
    parser.add_argument('--conflict-report', action='store_true', help='冲突检测报告')
    parser.add_argument('--stats-report', action='store_true', help='检索统计报告')
    parser.add_argument('--verify-all', action='store_true', help='完整验证报告')
    parser.add_argument('--prune', action='store_true', help='清理被遗忘知识')
    parser.add_argument('--search', type=str, help='检索并记录统计')
    parser.add_argument('--top-k', type=int, default=10, help='检索返回数量')
    
    args = parser.parse_args()
    
    # 初始化组件
    storage_dir = get_storage_dir()
    graph_path = storage_dir / "magma_graph.json"
    stats_path = storage_dir / "retrieval_stats.json"
    
    graph = MemoryGraph(str(graph_path) if graph_path.exists() else None)
    stats = RetrievalStats(str(stats_path))
    engine = RetrievalEngine(graph, stats)
    forgetting = ForgettingManager(graph)
    detector = ConflictDetector(graph)
    
    print("\n" + "="*60)
    print("🔍 MAGMA 知识验证系统")
    print("="*60)
    
    if args.forgetting_report or args.verify_all:
        print("\n📊 【遗忘报告】")
        print("-" * 40)
        decay_report = forgetting.get_decay_report()
        print(f"总记忆数: {decay_report['total']}")
        print(f"  🟢 新鲜 (0.8-1.0): {decay_report['fresh']}")
        print(f"  🟡 正常 (0.5-0.8): {decay_report['normal']}")
        print(f"  🟠 老化 (0.2-0.5): {decay_report['aging']}")
        print(f"  🔴 衰减 (<0.2):   {decay_report['fading']}")
        
        if decay_report['fading_nodes']:
            print("\n⚠️ 即将被遗忘的知识:")
            for node in decay_report['fading_nodes'][:5]:
                print(f"  [{node['decay']}] {node['content_preview']}...")
    
    if args.conflict_report or args.verify_all:
        print("\n⚖️ 【冲突检测报告】")
        print("-" * 40)
        conflict_report = detector.get_conflict_report()
        print(f"总冲突数: {conflict_report['total_conflicts']}")
        
        by_type = conflict_report['by_type']
        print(f"  时间矛盾: {by_type.get('temporal_contradiction', 0)}")
        print(f"  因果循环: {by_type.get('causal_loop', 0)}")
        print(f"  实体冲突: {by_type.get('entity_conflict', 0)}")
        print(f"  重复内容: {by_type.get('duplicate', 0)}")
        
        if conflict_report['conflicts']:
            print("\n⚠️ 冲突详情 (前5条):")
            for c in conflict_report['conflicts'][:5]:
                print(f"\n  [{c['severity'].upper()}] {c['type']}")
                print(f"  {c['description'][:150]}...")
    
    if args.stats_report or args.verify_all:
        print("\n📈 【检索统计报告】")
        print("-" * 40)
        stats_report = stats.get_report()
        summary = stats_report['summary']
        print(f"追踪节点数: {summary['total_tracked_nodes']}")
        print(f"总检索次数: {summary['total_queries']}")
        print(f"总命中次数: {summary['total_hits']}")
        print(f"整体命中率: {summary['overall_hit_rate']:.1%}")
        print(f"被遗忘知识: {summary['forgotten_count']} ({summary['forgotten_rate']:.1%})")
        
        if stats_report['hot_knowledge']:
            print("\n🔥 最热门知识 (Top 5):")
            for item in stats_report['hot_knowledge']:
                print(f"  [{item['hit_count']}次命中] rank={item['avg_rank']:.1f} | {item['node_id']}")
        
        if stats_report['cold_knowledge']:
            print("\n🥶 最冷门知识 (Top 5):")
            for item in stats_report['cold_knowledge']:
                print(f"  [{item['hit_count']}次命中/{item['miss_count']}次未命中] | {item['node_id']}")
    
    if args.prune:
        print("\n🗑️ 【清理被遗忘知识】")
        print("-" * 40)
        pruned = forgetting.prune_fading()
        print(f"已标记 {len(pruned)} 条知识为「已遗忘」")
        print(f"被遗忘的知识ID: {pruned[:10]}")
    
    if args.search:
        print(f"\n🔎 【检索: {args.search}】")
        print("-" * 40)
        results = engine.retrieve(args.search, top_k=args.top_k)
        
        if results:
            print(f"找到 {len(results)} 条相关记忆:\n")
            for i, r in enumerate(results, 1):
                node = r['node']
                print(f"{i}. [{r['score']:.3f}] {node.content[:80]}...")
                print(f"   维度: 语义={r['dimensions']['semantic']:.2f} "
                      f"因果={r['dimensions']['causal']:.2f} "
                      f"实体={r['dimensions']['entity']:.2f}")
                print(f"   时间: {node.temporal_date} {node.temporal_period}")
                print(f"   衰减: {node.decay_score:.3f}")
                print()
        else:
            print("未找到相关记忆")
        
        # 输出统计
        print("📊 本次检索统计:")
        print(f"  记忆节点总数: {len(graph.nodes)}")
        print(f"  遗忘报告已更新")
    
    if not any(vars(args).values()):
        parser.print_help()
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
