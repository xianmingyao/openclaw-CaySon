#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Karpathy 知识库 → Obsidian 导出工具
实现双向链接和Graph图谱可视化
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import re

# ========== 配置 ==========
WIKI_DIR = Path(__file__).parent / "wiki"
OUTPUT_DIR = Path.home() / "Obsidian Vaults" / "Karpathy Wiki"
TEMPLATE_DIR = OUTPUT_DIR / ".templates"

# ========== Obsidian配置模板 ==========

VAULT_CONFIG = """# Karpathy Wiki

> 由 CaySon AI 知识库系统自动生成
> 生成时间：{timestamp}

## 使用说明

1. 安装 Obsidian
2. 打开本文件夹作为 Vault
3. 享受双向链接和Graph图谱！

## 目录结构

- [[概念/]] - 原理/方法论/术语
- [[实体/]] - 人/公司/产品/工具
- [[来源/]] - 每篇原始资料的提炼

## 快捷命令

- `Ctrl+O` 快速打开文件
- `Ctrl+Shift+F` 全局搜索
- `Ctrl+G` 打开Graph图谱
"""

CONCEPTS_INDEX = """# 概念索引

> 分类：概念
> 生成时间：{timestamp}

## 全部概念

{concepts_list}

---
*由 Karpathy 知识库系统自动生成*
"""

ENTITIES_INDEX = """# 实体索引

> 类型：实体
> 生成时间：{timestamp}

## 全部实体

{entities_list}

---
*由 Karpathy 知识库系统自动生成*
"""

SOURCES_INDEX = """# 来源索引

> 分类：来源
> 生成时间：{timestamp}

## 最近来源

{sources_list}

## 全部来源

{all_sources_list}

---
*由 Karpathy 知识库系统自动生成*
"""

# ========== 图谱数据生成 ==========

def generate_graph_data() -> Dict:
    """生成Obsidian Graph视图数据"""
    nodes = []
    links = []
    seen_nodes = set()
    seen_links = set()
    
    def add_node(name: str, node_type: str):
        if name in seen_nodes:
            return
        seen_nodes.add(name)
        nodes.append({
            "id": name,
            "label": name,
            "type": node_type
        })
    
    def add_link(source: str, target: str):
        link_id = f"{source}->{target}"
        if link_id in seen_links:
            return
        seen_links.add(link_id)
        links.append({
            "source": source,
            "target": target
        })
    
    # 处理概念页
    concepts_dir = WIKI_DIR / "概念"
    if concepts_dir.exists():
        for md_file in concepts_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            add_node(md_file.stem, "concept")
            
            # 提取链接
            for link in re.findall(r'\[\[([^\]]+)\]\]', content):
                add_node(link.strip(), "linked")
                add_link(md_file.stem, link.strip())
    
    # 处理实体页
    entities_dir = WIKI_DIR / "实体"
    if entities_dir.exists():
        for md_file in entities_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            add_node(md_file.stem, "entity")
            
            for link in re.findall(r'\[\[([^\]]+)\]\]', content):
                add_node(link.strip(), "linked")
                add_link(md_file.stem, link.strip())
    
    # 处理来源页
    sources_dir = WIKI_DIR / "来源"
    if sources_dir.exists():
        for md_file in sources_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            add_node(md_file.stem, "source")
            
            for link in re.findall(r'\[\[([^\]]+)\]\]', content):
                add_node(link.strip(), "linked")
                add_link(md_file.stem, link.strip())
    
    return {
        "nodes": nodes,
        "links": links,
        "stats": {
            "total_nodes": len(nodes),
            "total_links": len(links),
            "concepts": len([n for n in nodes if n['type'] == 'concept']),
            "entities": len([n for n in nodes if n['type'] == 'entity']),
            "sources": len([n for n in nodes if n['type'] == 'source']),
        }
    }

# ========== Obsidian格式转换 ==========

def convert_to_obsidian_format(content: str, file_name: str) -> str:
    """将内容转换为Obsidian兼容格式"""
    # 清理YAML frontmatter
    content = re.sub(r'^---\n[\s\S]*?\n---\n', '', content)
    
    # 确保标题格式正确
    if not content.strip().startswith('#'):
        content = f"# {file_name}\n\n{content}"
    
    # Obsidian标签支持
    content = re.sub(r'`([^`]+)`', r'`\1`', content)  # 保持代码块
    
    # 添加元数据
    if 'created' not in content.lower():
        content = content.strip()
        content += f"\n\n---\n> 📅 创建: {datetime.now().strftime('%Y-%m-%d')}\n> 🔗 来源: [[{file_name}]]\n"
    
    return content

# ========== 导出流程 ==========

def create_directory_structure():
    """创建Obsidian目录结构"""
    dirs = [
        OUTPUT_DIR,
        OUTPUT_DIR / "概念",
        OUTPUT_DIR / "实体", 
        OUTPUT_DIR / "来源",
        OUTPUT_DIR / ".obsidian",
        TEMPLATE_DIR,
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    
    print(f"      [OK] 目录结构已创建")

def export_concepts():
    """导出概念页"""
    concepts_dir = WIKI_DIR / "概念"
    if not concepts_dir.exists():
        print(f"      [SKIP] 概念目录不存在")
        return []
    
    concepts = []
    for md_file in concepts_dir.glob("*.md"):
        content = md_file.read_text(encoding='utf-8')
        obsidian_content = convert_to_obsidian_format(content, md_file.stem)
        
        output_file = OUTPUT_DIR / "概念" / md_file.name
        output_file.write_text(obsidian_content, encoding='utf-8')
        concepts.append(md_file.stem)
    
    print(f"      [OK] 导出 {len(concepts)} 个概念页")
    return concepts

def export_entities():
    """导出实体页"""
    entities_dir = WIKI_DIR / "实体"
    if not entities_dir.exists():
        print(f"      [SKIP] 实体目录不存在")
        return []
    
    entities = []
    for md_file in entities_dir.glob("*.md"):
        content = md_file.read_text(encoding='utf-8')
        obsidian_content = convert_to_obsidian_format(content, md_file.stem)
        
        output_file = OUTPUT_DIR / "实体" / md_file.name
        output_file.write_text(obsidian_content, encoding='utf-8')
        entities.append(md_file.stem)
    
    print(f"      [OK] 导出 {len(entities)} 个实体页")
    return entities

def export_sources():
    """导出来源页"""
    sources_dir = WIKI_DIR / "来源"
    if not sources_dir.exists():
        print(f"      [SKIP] 来源目录不存在")
        return []
    
    sources = []
    for md_file in sources_dir.glob("*.md"):
        content = md_file.read_text(encoding='utf-8')
        obsidian_content = convert_to_obsidian_format(content, md_file.stem)
        
        output_file = OUTPUT_DIR / "来源" / md_file.name
        output_file.write_text(obsidian_content, encoding='utf-8')
        sources.append(md_file.stem)
    
    print(f"      [OK] 导出 {len(sources)} 个来源页")
    return sources

def generate_index_files(concepts: List, entities: List, sources: List):
    """生成Obsidian索引页"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 主索引
    main_index = VAULT_CONFIG.format(timestamp=timestamp)
    (OUTPUT_DIR / "Karpathy Wiki 索引.md").write_text(main_index, encoding='utf-8')
    
    # 概念索引
    concepts_list = '\n'.join([f"- [[{c}]]" for c in sorted(concepts)])
    concepts_index = CONCEPTS_INDEX.format(
        timestamp=timestamp,
        concepts_list=concepts_list or "*（暂无概念）*"
    )
    (OUTPUT_DIR / "概念" / "概念索引.md").write_text(concepts_index, encoding='utf-8')
    
    # 实体索引
    entities_list = '\n'.join([f"- [[{e}]]" for e in sorted(entities)])
    entities_index = ENTITIES_INDEX.format(
        timestamp=timestamp,
        entities_list=entities_list or "*（暂无实体）*"
    )
    (OUTPUT_DIR / "实体" / "实体索引.md").write_text(entities_index, encoding='utf-8')
    
    # 来源索引
    recent_sources = sorted(sources, reverse=True)[:10]
    sources_list = '\n'.join([f"- [[{s}]]" for s in recent_sources])
    all_sources_list = '\n'.join([f"- [[{s}]]" for s in sorted(sources)])
    sources_index = SOURCES_INDEX.format(
        timestamp=timestamp,
        sources_list=sources_list or "*（暂无来源）*",
        all_sources_list=all_sources_list or "*（暂无来源）*"
    )
    (OUTPUT_DIR / "来源" / "来源索引.md").write_text(sources_index, encoding='utf-8')
    
    print(f"      [OK] 索引文件已生成")

def generate_graph_file(graph_data: Dict):
    """生成Graph图谱数据文件"""
    # 保存JSON格式的图谱数据（Obsidian可以导入）
    graph_file = OUTPUT_DIR / "graph-data.json"
    graph_file.write_text(json.dumps(graph_data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    # 生成一个展示页面
    stats = graph_data['stats']
    graph_html = f"""# 知识图谱

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 统计

| 类型 | 数量 |
|------|------|
| 总节点 | {stats['total_nodes']} |
| 总链接 | {stats['total_links']} |
| 概念 | {stats['concepts']} |
| 实体 | {stats['entities']} |
| 来源 | {stats['sources']} |

## Graph可视化

在 Obsidian 中按 `Ctrl+G` 打开Graph视图。

或查看 [[graph-data.json]] 获取原始数据。

## 热门节点

{generate_top_nodes(graph_data)}

---
*由 Karpathy 知识库系统自动生成*
"""
    
    top_nodes_file = OUTPUT_DIR / "图谱统计.md"
    top_nodes_file.write_text(graph_html, encoding='utf-8')
    print(f"      [OK] 图谱数据已生成")

def generate_top_nodes(graph_data: Dict) -> str:
    """生成热门节点列表"""
    # 计算每个节点的连接数
    connection_count = {}
    for link in graph_data['links']:
        for node_id in [link['source'], link['target']]:
            connection_count[node_id] = connection_count.get(node_id, 0) + 1
    
    # 排序取前10
    top_nodes = sorted(connection_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    result = "| 节点 | 连接数 |\n|------|--------|\n"
    for node_id, count in top_nodes:
        result += f"| [[{node_id}]] | {count} |\n"
    
    return result

def create_obsidian_config():
    """创建Obsidian配置文件"""
    config = {
        "vault": "Karpathy Wiki",
        "created": datetime.now().isoformat(),
        "source_knowledge_base": str(WIKI_DIR.parent)
    }
    
    meta_file = OUTPUT_DIR / ".karpathy-meta.json"
    meta_file.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    
    # 创建.obsidian配置文件
    obsidian_config = {
        "plugin": {
            "enabled": True
        }
    }
    
    print(f"      [OK] Obsidian配置已创建")

# ========== 主流程 ==========

def export_to_obsidian():
    """执行Obsidian导出"""
    print("=" * 60)
    print("Karpathy Wiki → Obsidian 导出工具")
    print("=" * 60)
    print(f"\n源目录: {WIKI_DIR}")
    print(f"目标目录: {OUTPUT_DIR}")
    
    # 备份现有vault
    if OUTPUT_DIR.exists() and any(OUTPUT_DIR.iterdir()):
        backup_dir = OUTPUT_DIR.parent / f"Karmahty Wiki_backup_{datetime.now().strftime('%Y%m%d_%H%M')}"
        print(f"\n[BACKUP] 备份现有Vault到 {backup_dir}")
        shutil.move(str(OUTPUT_DIR), str(backup_dir))
    
    print("\n[1/6] 创建目录结构...")
    create_directory_structure()
    
    print("\n[2/6] 导出概念页...")
    concepts = export_concepts()
    
    print("\n[3/6] 导出实体页...")
    entities = export_entities()
    
    print("\n[4/6] 导出来源页...")
    sources = export_sources()
    
    print("\n[5/6] 生成索引文件...")
    generate_index_files(concepts, entities, sources)
    
    print("\n[6/6] 生成图谱数据...")
    graph_data = generate_graph_data()
    generate_graph_file(graph_data)
    
    create_obsidian_config()
    
    print(f"\n" + "=" * 60)
    print("[DONE] 导出完成!")
    print(f"=" * 60)
    print(f"\n📁 Vault位置: {OUTPUT_DIR}")
    print(f"📊 统计:")
    print(f"   - 概念: {len(concepts)}")
    print(f"   - 实体: {len(entities)}")
    print(f"   - 来源: {len(sources)}")
    print(f"   - 节点: {graph_data['stats']['total_nodes']}")
    print(f"   - 链接: {graph_data['stats']['total_links']}")
    print(f"\n🚀 下一步:")
    print(f"   1. 打开 Obsidian")
    print(f"   2. 选择 '打开本地Vault'")
    print(f"   3. 选择目录: {OUTPUT_DIR}")
    print(f"   4. 按 Ctrl+G 查看Graph图谱")

# ========== CLI ==========

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Karpathy Wiki → Obsidian 导出工具')
    parser.add_argument('--output', '-o', type=str, help='输出目录路径')
    parser.add_argument('--open', action='store_true', help='导出后自动打开')
    
    args = parser.parse_args()
    
    if args.output:
        OUTPUT_DIR = Path(args.output)
    
    export_to_obsidian()
    
    if args.open:
        import webbrowser
        webbrowser.open(OUTPUT_DIR.as_uri())
