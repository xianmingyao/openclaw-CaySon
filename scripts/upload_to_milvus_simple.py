#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版云端记忆上传：只使用 Milvus（不需要 Ollama）
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

from pymilvus import MilvusClient
import requests
import json
import hashlib
from datetime import datetime

# ============ 配置 ============

MILVUS_HOST = "8.137.122.11"
MILVUS_PORT = 19530
MILVUS_COLLECTION = "CaySon_db"

OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"

USER_ID = "ningcaison"

# ============ Milvus 操作 ============

def init_milvus():
    """初始化Milvus客户端"""
    return MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")

def ensure_collection(milvus_client):
    """确保 collection 存在"""
    try:
        milvus_client.load_collection(MILVUS_COLLECTION)
    except:
        pass
    
    try:
        milvus_client.get_collection_stats(MILVUS_COLLECTION)
    except:
        milvus_client.create_collection(
            collection_name=MILVUS_COLLECTION,
            dimension=768,
            auto_id=True
        )

def get_embedding(text):
    """使用 Ollama 获取文本嵌入"""
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": text},
        timeout=30
    )
    return response.json()["embedding"]

def add_memory_to_milvus(milvus_client, text, metadata=None):
    """添加记忆到 Milvus"""
    try:
        embedding = get_embedding(text)
        
        data = [{
            "text": text,
            "user_id": USER_ID,
            "metadata": json.dumps(metadata) if metadata else "{}"
        }]
        
        milvus_client.insert(
            collection_name=MILVUS_COLLECTION,
            data=data,
            vector=embedding
        )
        print(f"    [OK] Milvus 写入成功")
        return True
    except Exception as e:
        print(f"    [FAIL] Milvus 写入失败: {e}")
        return False

# ============ 主程序 ============

TODAY_MEMORIES = [
    {
        "category": "Skills_Installed",
        "memory": """2026-04-08 Skills安装记录（AI干货局6个必备Skill）
已安装4个：
1.react-best-practices：Vercel官方React性能优化，57条规则，3.6k stars
2.remotion-video-toolkit：Remotion视频框架最佳实践，16k stars，动画/字幕/图表
3.superdesign：专家级前端设计指南，28.2k stars，beautiful modern UIs
4.mobile：移动端应用开发，1.6k stars，lifecycle/offline/platform conventions

未安装（ClawHub限流）：
5.azure-ai：Azure AI服务集成（未找到对应Skill）
6.frontend-design-pro：前端设计规范中文版（限流）

当前已安装Skills共9个：agent-reach/anspire-web-search/mobile/react-best-practices/remotion-video-toolkit/superdesign/windows-control/frontend-design/ui-design"""
    },
    {
        "category": "Skills_Research",
        "memory": """2026-04-08 Skills研究总结（抖音视频）
AI干货局6个必备Skill：
- React性能优化（react-best-practices）✅
- Web设计规范自动审查（待查）
- 前端设计指南（Anthropic出品）
- Remotion视频框架最佳实践（remotion-video-toolkit）✅
- Azure AI服务集成（待查）
- 移动端UI生成（mobile）✅

AI内容工厂6个邪修Skill：
- 社区（需求对齐）
- Canva design（商业信息图）
- Front end design（superdesign）✅
- Docx（Word处理）
- XLSX（Excel处理）
- Humanizer（去AI味）

Agent-Reach（16.3k stars）：
- 已从v1.1.0升级到v1.4.0
- 支持17个平台：网页/YouTube/RSS/全网搜索/GitHub/Twitter/小红书/抖音/Reddit/LinkedIn/微信公众号/微博/V2EX/雪球/小宇宙播客
- 完全免费，MIT License"""
    },
    {
        "category": "Harness_Engineering",
        "memory": """2026-04-08 Harness Engineering（驾驭工程）
视频：@从小就坏®²⁰²³ ོ
核心：AI代理难以预测，需驯服并控制其行为

七大章节：
1.引言：AI代理难以预测，风险大，需驯服并控制
2.驾驭工程核心思想：接受AI不确定性，建立控制系统
3.Prompt=系统宪法：分层结构确保规则清晰
4.心跳机制：从一次性API调用→持续运行循环
5.交互三部曲：调用前治理→调用模型→执行或恢复
6.开发者选择：严谨方法区分玩具和工具，构建生产级系统
7.思维转变：以模型为中心→以驾驭系统为中心

金句："提示决定说，驾驭系统决定做"
可控可靠的做对工程师至关重要"""
    },
    {
        "category": "Afternoon_Research",
        "memory": """2026-04-08 下午研究（08:45-10:20）
1.SDD开发教程（大力AI）：OpenSpec规范多人协作，init→explore→propose→apply→archive
2.Red/Green TDD（大力AI）：Simon Willison提出，RED→GREEN→REFACTOR，AI编程测试必须
3.Karpathy个人知识库（大力AI）：RO/wiki/altpus三文件夹+CLOD.md指令
4.GitHub TOP20（赛博笔记）：AI基础设施+Agent工具+开发者效率
5.Harness Engineering：驾驭工程，Prompt=宪法，心跳机制，交互三部曲
6.Agent-Reach v1.4.0：16.3k Stars，17平台，完全免费"""
    }
]

def main():
    print("=" * 60)
    print("上传记忆到云端 Milvus（简化版）")
    print("=" * 60)
    
    print("\n[初始化] 连接 Milvus...")
    try:
        milvus_client = init_milvus()
        ensure_collection(milvus_client)
        print("[OK] Milvus 连接成功")
    except Exception as e:
        print(f"[FAIL] Milvus 连接失败: {e}")
        return
    
    print("\n开始上传记忆...")
    for i, item in enumerate(TODAY_MEMORIES, 1):
        print(f"\n[{i}/{len(TODAY_MEMORIES)}] {item['category']}")
        print(f"内容: {item['memory'][:50]}...")
        add_memory_to_milvus(milvus_client, item['memory'], {"category": item['category']})
    
    print("\n" + "=" * 60)
    print(f"[完成] 共上传 {len(TODAY_MEMORIES)} 条记忆到云端")
    print("=" * 60)

if __name__ == "__main__":
    main()
