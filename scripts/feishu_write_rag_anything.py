#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接通过飞书Open API创建RAG-Anything文档"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import requests

APP_ID = "cli_a9324982073a1bc8"
APP_SECRET = "2tOQnQmwk2bHOUAHPsHCjfcv4zLreFWE"
BASE_URL = "https://open.feishu.cn/open-apis"

def get_token():
    resp = requests.post(f"{BASE_URL}/auth/v3/tenant_access_token/internal", json={
        "app_id": APP_ID, "app_secret": APP_SECRET
    })
    return resp.json().get("tenant_access_token")

def create_doc(token, title):
    resp = requests.post(f"{BASE_URL}/docx/v1/documents", headers={"Authorization": f"Bearer {token}"}, json={
        "title": title
    })
    return resp.json()

def add_blocks(token, doc_token, blocks):
    resp = requests.post(
        f"{BASE_URL}/docx/v1/documents/{doc_token}/blocks/{doc_token}/children",
        headers={"Authorization": f"Bearer {token}"},
        json={"children": blocks, "index": -1}
    )
    return resp.json()

def text_block(text):
    return {
        "block_type": 2,
        "text": {"elements": [{"text_run": {"content": text}}], "style": {}}
    }

def heading_block(text, level=1):
    key = f"heading{level}"
    return {"block_type": 2 + level, key: {"elements": [{"text_run": {"content": text}}], "style": {}}}

def bullet_block(text):
    return {"block_type": 12, "bullet": {"elements": [{"text_run": {"content": text}}], "style": {}}}

def ordered_block(text):
    return {"block_type": 13, "ordered": {"elements": [{"text_run": {"content": text}}], "style": {}}}

def divider_block():
    return {"block_type": 22, "divider": {}}

def code_block(text, lang=""):
    return {
        "block_type": 9,
        "code": {
            "elements": [{"text_run": {"content": text}}],
            "style": {"language": 1}
        }
    }

token = get_token()
print(f"Token: {token[:20]}...")

result = create_doc(token, "港大开源万物皆可RAG：RAG-Anything")
print("Create result:", result)
doc_token = result.get("data", {}).get("document", {}).get("document_id")
print(f"Doc ID: {doc_token}")

if not doc_token:
    print("Failed to create doc")
    exit(1)

blocks = [
    heading_block("项目概览", 1),
    text_block("RAG-Anything - 港大数据科学团队出品 | 20.3k Stars ⭐"),
    text_block("定位: All-in-One Multimodal RAG Framework（万物皆可RAG）"),
    text_block("arXiv: 2510.12323 | 基于: LightRAG"),
    divider_block(),
    heading_block("核心问题解决", 2),
    text_block("痛点: 现代文档包含多模态内容（文本/图片/表格/公式），传统纯文本RAG无法有效处理"),
    text_block("解决方案: 统一的全链路多模态文档处理RAG系统"),
    divider_block(),
    heading_block("架构流程（5阶段）", 2),
    ordered_block("文档解析 - MinerU高保真提取，自适应内容分解"),
    ordered_block("内容分析 - 自主分类路由，并发多Pipeline架构"),
    ordered_block("多模态分析引擎 - 视觉/表格/公式/可扩展处理器"),
    ordered_block("知识图谱索引 - 多模态实体，跨模态关系，加权评分"),
    ordered_block("智能检索 - 向量+图融合，模态感知排名"),
    divider_block(),
    heading_block("三种查询模式", 2),
    text_block("1. 纯文本查询 - Text Query (hybrid/local/global/naive)"),
    text_block("2. VLM增强查询 - 自动分析图像，综合文本+视觉分析"),
    text_block("3. 多模态查询 - 带表格/公式的增强查询"),
    divider_block(),
    heading_block("安装使用", 2),
    text_block("PyPI安装: pip install raganything"),
    text_block("源码安装: git clone → uv sync --all-extras"),
    text_block("依赖: LibreOffice / Pillow / ReportLab"),
    divider_block(),
    heading_block("关键链接", 2),
    text_block("GitHub: https://github.com/HKUDS/RAG-Anything"),
    text_block("arXiv: https://arxiv.org/abs/2510.12323"),
    text_block("PyPI: https://pypi.org/project/raganything/"),
    text_block("Discord: https://discord.gg/yF2MmDJyGJ"),
    divider_block(),
    heading_block("学习价值", 2),
    text_block("工程价值: ⭐⭐⭐⭐⭐（5星）- 多模态RAG标准框架"),
    text_block("研究价值: ⭐⭐⭐⭐⭐（5星）- arXiv论文支撑"),
    text_block("实用价值: ⭐⭐⭐⭐⭐（5星）- 统一多格式文档处理"),
]

result = add_blocks(token, doc_token, blocks)
print(f"Blocks added: {len(blocks)}")
print(f"\n✅ 文档地址: https://feishu.cn/docx/{doc_token}")
