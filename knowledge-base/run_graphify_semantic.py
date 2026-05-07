#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Graphify 语义提纯脚本 (方案B) - 支持断点续传
"""
import os
import sys
import json
import time
import re
from pathlib import Path
from openai import OpenAI

# MiniMax 配置
MINIMAX_API_KEY = "sk-cp-3b3Ek6Vdna7iLAYz2kD6JiZL_W8x0j5TX8XIlqKex4JobdGEea4SESTayaD3FfAbc3HNteY8QZyFx9QeFm533E3pXQ4-ZW1iPEpGnr5Rl8DpmdgQX4B-xU8"
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"
MODEL = "MiniMax-M2.5-highspeed"

INPUT_DIR = Path(r"E:\workspace\knowledge-base")
OUTPUT_DIR = INPUT_DIR / "graphify-out"
WIKI_DIR = INPUT_DIR / "wiki"
STATE_FILE = OUTPUT_DIR / "semantic_state.json"

SYSTEM_PROMPT = """You are a knowledge graph extractor. Output ONLY valid JSON - no thinking, no explanation, no markdown fences.

Extract key concepts and relationships from the document.
Output format:
{"nodes":[{"id":"concept_name","label":"Concept Name"}],"edges":[{"source":"concept1","target":"concept2","relation":"related_to"}]}

Rules:
- id must be unique and contain only letters, numbers, underscores
- label is human readable
- relation should be one of: related_to, mentions, implements, part_of, depends_on, similar_to
- Only extract 3-8 most important concepts per document
- Use simple concept names as IDs (no spaces, no special chars)"""

def log(msg):
    print(msg, flush=True)

def load_state():
    """加载断点状态"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8", errors="replace"))
    return {"processed": [], "all_nodes": [], "all_edges": [], "errors": 0}

def save_state(state):
    """保存断点状态"""
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    log(f"  State saved: {len(state['processed'])} processed")

def extract_concepts_from_file(file_path: Path, client: OpenAI) -> dict:
    """从单个文件提取概念关系"""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except:
        return {"nodes": [], "edges": [], "hyperedges": []}
    
    if len(content) > 15000:
        content = content[:15000] + "\n... [truncated]"
    
    file_rel = file_path.relative_to(INPUT_DIR)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Extract concepts from this file:\n\n=== FILE: {file_rel} ===\n{content}"}
    ]
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.1,
            max_tokens=2048,
            timeout=60  # 60 second timeout
        )
        raw = response.choices[0].message.content or ""
        
        # 剥离推理内容
        raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
        raw = re.sub(r"```json\s*", "", raw)
        raw = re.sub(r"```\s*$", "", raw)
        
        json_start = raw.find("{")
        if json_start == -1:
            return {"nodes": [], "edges": [], "hyperedges": []}
        
        json_str = raw[json_start:]
        
        # 找配对括号
        brace_count = 0
        json_end = 0
        in_string = False
        escape_next = False
        
        for i, c in enumerate(json_str):
            if escape_next:
                escape_next = False
                continue
            if c == "\\":
                escape_next = True
                continue
            if c == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if c == "{":
                brace_count += 1
            elif c == "}":
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break
        
        if json_end > 0:
            json_str = json_str[:json_end]
        
        result = json.loads(json_str)
        
        for node in result.get("nodes", []):
            node["id"] = re.sub(r"[^a-zA-Z0-9_\u4e00-\u9fff]", "_", str(node.get("id", "")))
            if not node.get("label"):
                node["label"] = node["id"]
            node["source_file"] = str(file_rel)
        
        for edge in result.get("edges", []):
            edge["source_file"] = str(file_rel)
            edge["confidence"] = "INFERRED"
            edge["confidence_score"] = 0.7
        
        return result
    except Exception as e:
        log(f"  Error processing {file_path}: {e}")
        return {"nodes": [], "edges": [], "hyperedges": []}

def main():
    log("=" * 60)
    log("Graphify 语义提纯 (方案B) - 断点续传版")
    log("=" * 60)
    
    state = load_state()
    log(f"  已有进度: {len(state['processed'])} 个文件已处理")
    log(f"  已提取: {len(state['all_nodes'])} 节点, {len(state['all_edges'])} 边")
    
    client = OpenAI(api_key=MINIMAX_API_KEY, base_url=MINIMAX_BASE_URL)
    
    # 测试 API
    log("  测试 MiniMax API...")
    try:
        test = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10,
            timeout=30
        )
        log("  API 测试成功!")
    except Exception as e:
        log(f"  API 测试失败: {e}")
        return
    
    # 收集文件
    log("\n[1] 收集文件...")
    files_to_process = []
    concept_dir = WIKI_DIR / "概念"
    if concept_dir.exists():
        files_to_process.extend(list(concept_dir.glob("*.md")))
    entity_dir = WIKI_DIR / "实体"
    if entity_dir.exists():
        files_to_process.extend(list(entity_dir.glob("*.md")))
    
    total = len(files_to_process)
    processed_set = set(state["processed"])
    remaining = [f for f in files_to_process if str(f) not in processed_set]
    
    log(f"  总计: {total} 个, 待处理: {len(remaining)} 个")
    
    if not remaining:
        log("  所有文件已处理完成!")
    else:
        log(f"\n[2] 开始语义提取 ({len(remaining)} 个剩余)...")
        for idx, f in enumerate(remaining):
            result = extract_concepts_from_file(f, client)
            if not result.get("nodes"):
                state["errors"] += 1
            state["all_nodes"].extend(result.get("nodes", []))
            state["all_edges"].extend(result.get("edges", []))
            state["processed"].append(str(f))
            
            # 每10个文件打印进度
            if (idx + 1) % 10 == 0:
                log(f"  进度: {idx + 1}/{len(remaining)} ({len(state['all_nodes'])} 节点)")
                save_state(state)
            
            # 每20个文件暂停一下
            if (idx + 1) % 20 == 0:
                time.sleep(0.5)
        
        # 最终保存
        save_state(state)
    
    # 合并到图谱
    log("\n[3] 合并到现有图谱...")
    graph_file = OUTPUT_DIR / "graph.json"
    if graph_file.exists():
        existing = json.loads(graph_file.read_text(encoding="utf-8", errors="replace"))
        existing_nodes = existing.get("nodes", [])
        existing_edges = existing.get("edges", [])
    else:
        existing_nodes = []
        existing_edges = []
    
    existing_ids = {n["id"] for n in existing_nodes}
    new_nodes = [n for n in state["all_nodes"] if n["id"] not in existing_ids]
    merged_nodes = existing_nodes + new_nodes
    
    # 转换 edges -> links
    merged_links = existing_edges + state["all_edges"]
    
    merged_graph = {"nodes": merged_nodes, "links": merged_links}
    graph_file.write_text(json.dumps(merged_graph, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # 删除状态文件（完成）
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    
    log(f"\n  新增节点: {len(new_nodes)}")
    log(f"  新增边: {len(state['all_edges'])}")
    log(f"  合并后节点: {len(merged_nodes)}")
    log(f"  合并后边: {len(merged_links)}")
    log("\n" + "=" * 60)
    log("语义提纯完成!")
    log("=" * 60)

if __name__ == "__main__":
    main()
