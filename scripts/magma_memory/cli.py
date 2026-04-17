# -*- coding: utf-8 -*-
"""
MAGMA 记忆系统命令行工具
"""
import sys
import argparse
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from magma_memory.core import MemoryGraph
from magma_memory.retrieval import RetrievalEngine
from magma_memory.writer import MemoryWriter
from magma_memory.hybrid import MAGMAMem0Hybrid, get_hybrid


def cmd_add(args):
    """添加记忆"""
    hybrid = get_hybrid()
    node_id = hybrid.add(
        content=args.content,
        source=args.source or "manual",
        keywords=args.keywords.split(',') if args.keywords else None
    )
    print(f"[OK] Added memory: {node_id}")
    print(f"     Content: {args.content[:80]}...")

def cmd_search(args):
    """检索记忆"""
    hybrid = get_hybrid()
    results = hybrid.search(args.query, top_k=args.top)
    
    if not results:
        print("[EMPTY] No results found")
        return
    
    print(f"\nFound {len(results)} results:\n")
    for i, r in enumerate(results, 1):
        node = r['node']
        print(f"--- Result {i} (score: {r['score']}) ---")
        print(f"ID: {node.id}")
        print(f"Time: {node.temporal_date} {node.temporal_period}")
        print(f"Content: {node.content[:100]}...")
        print(f"Reason: {r['reason']}")
        print()

def cmd_recent(args):
    """近期记忆"""
    hybrid = get_hybrid()
    nodes = hybrid.get_recent(limit=args.limit)
    
    if not nodes:
        print("[EMPTY] No memories yet")
        return
    
    print(f"\nRecent {len(nodes)} memories:\n")
    for i, node in enumerate(nodes, 1):
        print(f"{i}. [{node.temporal_date}] {node.content[:80]}...")

def cmd_stats(args):
    """统计信息"""
    hybrid = get_hybrid()
    stats = hybrid.stats()
    
    print("\n=== MAGMA Memory Stats ===")
    print(f"Total nodes: {stats['total_nodes']}")
    print(f"Sequence counter: {stats['sequence_counter']}")
    print(f"Keywords indexed: {stats['keywords']}")
    print(f"Entities indexed: {stats['entities']}")
    print(f"Total searches: {stats['total_searches']}")

def cmd_explain(args):
    """解释节点"""
    hybrid = get_hybrid()
    info = hybrid.explain_node(args.node_id)
    
    if not info:
        print(f"[ERROR] Node not found: {args.node_id}")
        return
    
    print("\n=== Node Details ===")
    print(f"ID: {info['id']}")
    print(f"Content: {info['content'][:100]}...")
    print(f"Created: {info['created']}")
    print(f"Source: {info['source']}")
    
    print("\n--- Four Dimensions ---")
    dim = info['four_dimensions']
    
    print("\n[Semantic]")
    print(f"  Keywords: {', '.join(dim['semantic']['keywords'])}")
    
    print("\n[Temporal]")
    print(f"  Sequence: {dim['temporal']['sequence']}")
    print(f"  Period: {dim['temporal']['period']}")
    print(f"  Date: {dim['temporal']['date']}")
    
    print("\n[Causal]")
    print(f"  Strength: {dim['causal']['strength']}")
    print(f"  Causes: {dim['causal']['causes'][:3]}")
    print(f"  Effects: {dim['causal']['effects'][:3]}")
    
    print("\n[Entity]")
    print(f"  Subjects: {dim['entity']['subjects']}")
    print(f"  Objects: {dim['entity']['objects']}")
    print(f"  Concepts: {dim['entity']['concepts']}")

def cmd_causal(args):
    """查看因果链"""
    hybrid = get_hybrid()
    chain = hybrid.get_causal_chain(args.node_id, depth=args.depth)
    
    if not chain:
        print(f"[ERROR] Node not found: {args.node_id}")
        return
    
    print(f"\n=== Causal Chain for {args.node_id} ===\n")
    print(f"Node: {chain['node']['content'][:80]}...")
    
    print(f"\nCauses ({len(chain['causes'])}):")
    for c in chain['causes'][:5]:
        print(f"  <- {c['id']}: {c['content']}...")
    
    print(f"\nEffects ({len(chain['effects'])}):")
    for e in chain['effects'][:5]:
        print(f"  -> {e['id']}: {e['content']}...")

def cmd_link(args):
    """建立因果链接"""
    hybrid = get_hybrid()
    hybrid.link_causal(args.cause, args.effect, args.strength or 0.5)
    print(f"[OK] Linked: {args.cause} -> {args.effect}")

def main():
    parser = argparse.ArgumentParser(description="MAGMA Memory System")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # add
    p_add = subparsers.add_parser('add', help='Add memory')
    p_add.add_argument('content', help='Memory content')
    p_add.add_argument('--source', '-s', help='Source (wechat/douyin/doc/manual)')
    p_add.add_argument('--keywords', '-k', help='Keywords (comma separated)')
    p_add.set_defaults(func=cmd_add)
    
    # search
    p_search = subparsers.add_parser('search', help='Search memory')
    p_search.add_argument('query', help='Search query')
    p_search.add_argument('--top', '-n', type=int, default=5, help='Top N results')
    p_search.set_defaults(func=cmd_search)
    
    # recent
    p_recent = subparsers.add_parser('recent', help='Recent memories')
    p_recent.add_argument('--limit', '-n', type=int, default=10, help='Limit')
    p_recent.set_defaults(func=cmd_recent)
    
    # stats
    p_stats = subparsers.add_parser('stats', help='Memory statistics')
    p_stats.set_defaults(func=cmd_stats)
    
    # explain
    p_exp = subparsers.add_parser('explain', help='Explain node')
    p_exp.add_argument('node_id', help='Node ID')
    p_exp.set_defaults(func=cmd_explain)
    
    # causal
    p_causal = subparsers.add_parser('causal', help='Show causal chain')
    p_causal.add_argument('node_id', help='Node ID')
    p_causal.add_argument('--depth', '-d', type=int, default=3, help='Depth')
    p_causal.set_defaults(func=cmd_causal)
    
    # link
    p_link = subparsers.add_parser('link', help='Link causal relation')
    p_link.add_argument('cause', help='Cause node ID')
    p_link.add_argument('effect', help='Effect node ID')
    p_link.add_argument('--strength', type=float, help='Causal strength')
    p_link.set_defaults(func=cmd_link)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)

if __name__ == '__main__':
    main()
