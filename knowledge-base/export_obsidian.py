#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
export_obsidian.py - 导出到 Obsidian Vault

功能：
1. 将 wiki/ 目录导出到 Obsidian Vault
2. 确保双向链接完整
3. 生成 Graph View 所需的关系数据

使用说明：
    python export_obsidian.py                    # 增量导出
    python export_obsidian.py --full             # 全量导出
    python export_obsidian.py --vault "路径"     # 指定 Vault 路径
"""

import os
import re
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

# ============== 配置 ==============
WIKI_DIR = Path(__file__).parent / "wiki"
OBSIDIAN_VAULT = Path(os.environ.get('OBSIDIAN_VAULT', r"E:\Obsidian Vault\Karpathy"))
GRAPH_DATA_FILE = Path(__file__).parent / ".graph_data.json"


# ============== 导出逻辑 ==============

def extract_links(content: str) -> List[str]:
    """从 Markdown 内容中提取双向链接"""
    # 匹配 [[链接]] 格式
    links = re.findall(r'\[\[([^\]]+)\]\]', content)
    return [l.strip() for l in links]


def build_graph_data() -> Dict:
    """构建知识图谱数据"""
    print("[1/3] 构建知识图谱...")
    
    graph = {
        'nodes': [],
        'edges': [],
        'last_updated': datetime.now().isoformat()
    }
    
    nodes_set = set()
    edges_set = set()
    
    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file.name in ["index.md", "log.md"]:
            continue
        
        # 节点
        node_id = md_file.stem
        if node_id not in nodes_set:
            nodes_set.add(node_id)
            graph['nodes'].append({
                'id': node_id,
                'name': md_file.stem,
                'path': str(md_file.relative_to(WIKI_DIR)),
                'type': get_node_type(md_file)
            })
        
        # 边（链接关系）
        try:
            content = md_file.read_text(encoding='utf-8')
        except:
            continue
        
        links = extract_links(content)
        for link in links:
            link_id = link.replace(' ', '-')  # 规范化
            edge_id = f"{node_id}->{link_id}"
            
            if edge_id not in edges_set:
                edges_set.add(edge_id)
                graph['edges'].append({
                    'source': node_id,
                    'target': link_id,
                    'type': 'links_to'
                })
    
    print(f"      节点: {len(graph['nodes'])} / 边: {len(graph['edges'])}")
    
    return graph


def get_node_type(filepath: Path) -> str:
    """根据路径判断节点类型"""
    path_str = str(filepath).lower()
    
    if '实体' in path_str or '公司' in path_str or '产品' in path_str:
        return 'entity'
    elif '概念' in path_str or '原理' in path_str:
        return 'concept'
    elif '来源' in path_str:
        return 'source'
    else:
        return 'page'


def export_to_vault(vault_path: Path, full: bool = False) -> Dict:
    """
    导出到 Obsidian Vault
    
    Args:
        vault_path: Obsidian Vault 路径
        full: 是否全量导出
    
    Returns:
        {exported: int, skipped: int, errors: int}
    """
    print(f"[2/3] 导出到 Obsidian Vault...")
    print(f"      目标: {vault_path}")
    
    vault_path.mkdir(parents=True, exist_ok=True)
    
    # 创建必要的目录结构
    (vault_path / "00-Inbox").mkdir(exist_ok=True)
    (vault_path / "01-Concepts").mkdir(exist_ok=True)
    (vault_path / "02-Entities").mkdir(exist_ok=True)
    (vault_path / "03-Sources").mkdir(exist_ok=True)
    (vault_path / "04-Projects").mkdir(exist_ok=True)
    
    exported = 0
    skipped = 0
    errors = 0
    
    # 跟踪已导出的文件
    export_state_file = vault_path / ".export_state.json"
    if export_state_file.exists():
        export_state = json.loads(export_state_file.read_text(encoding='utf-8'))
    else:
        export_state = {}
    
    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file.name in ["index.md", "log.md"]:
            continue
        
        # 检查是否需要导出
        if not full:
            file_mtime = md_file.stat().st_mtime
            last_exported = export_state.get(str(md_file), 0)
            if last_exported >= file_mtime:
                skipped += 1
                continue
        
        # 确定目标路径
        rel_path = md_file.relative_to(WIKI_DIR)
        target_path = vault_path / rel_path
        
        # 根据类型放到对应目录
        node_type = get_node_type(md_file)
        if node_type == 'concept':
            target_path = vault_path / "01-Concepts" / md_file.name
        elif node_type == 'entity':
            target_path = vault_path / "02-Entities" / md_file.name
        elif node_type == 'source':
            target_path = vault_path / "03-Sources" / md_file.name
        else:
            target_path = vault_path / md_file.name
        
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(md_file, target_path)
            exported += 1
            export_state[str(md_file)] = md_file.stat().st_mtime
        except Exception as e:
            print(f"      ❌ {md_file.name}: {e}")
            errors += 1
    
    # 保存导出状态
    export_state_file.write_text(json.dumps(export_state, ensure_ascii=False), encoding='utf-8')
    
    print(f"      导出: {exported} / 跳过: {skipped} / 错误: {errors}")
    
    return {"exported": exported, "skipped": skipped, "errors": errors}


def generate_graph_json(graph_data: Dict, vault_path: Path):
    """生成 Obsidian Graph View 所需的 JSON"""
    print("[3/3] 生成图谱数据...")
    
    # Obsidian 使用的格式
    graph_json = {
        "nodes": [],
        "links": []
    }
    
    for node in graph_data['nodes']:
        graph_json["nodes"].append({
            "id": node['id'],
            "name": node['name'],
            "type": node.get('type', 'page')
        })
    
    for edge in graph_data['edges']:
        graph_json["links"].append({
            "source": edge['source'],
            "target": edge['target']
        })
    
    # 保存到 vault
    graph_file = vault_path / ".obsidian" / "graph.json"
    graph_file.parent.mkdir(exist_ok=True)
    graph_file.write_text(json.dumps(graph_json, ensure_ascii=False, indent=2), encoding='utf-8')
    
    # 同时保存到 knowledge-base 作为备份
    GRAPH_DATA_FILE.write_text(json.dumps(graph_data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    print(f"      图谱数据已保存")


# ============== 主流程 ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="导出到 Obsidian Vault")
    parser.add_argument('--vault', default=str(OBSIDIAN_VAULT), help='Obsidian Vault 路径')
    parser.add_argument('--full', action='store_true', help='全量导出')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault)
    
    print("=" * 50)
    print("OBSIDIAN EXPORT - 知识库导出")
    print("=" * 50)
    print(f"Vault: {vault_path}")
    print(f"模式: {'全量' if args.full else '增量'}")
    print()
    
    # 构建图谱数据
    graph_data = build_graph_data()
    
    # 导出到 Vault
    export_result = export_to_vault(vault_path, full=args.full)
    
    # 生成图谱 JSON
    generate_graph_json(graph_data, vault_path)
    
    print()
    print("=" * 50)
    print(f"[DONE] 导出完成")
    print(f"       导出: {export_result['exported']} 文件")
    print(f"       Vault: file://{vault_path}")
    print("=" * 50)


if __name__ == '__main__':
    main()
