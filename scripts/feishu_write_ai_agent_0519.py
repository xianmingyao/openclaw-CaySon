#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接通过飞书Open API创建GitHub AI Skills与OpenHuman分析文档"""
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
        "text": {
            "elements": [{"text_run": {"content": text}}],
            "style": {}
        }
    }

def heading_block(text, level=1):
    key = f"heading{level}"
    return {
        "block_type": 2 + level,
        key: {
            "elements": [{"text_run": {"content": text}}],
            "style": {}
        }
    }

def bullet_block(text):
    return {
        "block_type": 12,
        "bullet": {
            "elements": [{"text_run": {"content": text}}],
            "style": {}
        }
    }

def ordered_block(text):
    return {
        "block_type": 13,
        "ordered": {
            "elements": [{"text_run": {"content": text}}],
            "style": {}
        }
    }

def divider_block():
    return {"block_type": 22, "divider": {}}

def get_table_cell(text):
    return {"text_run": {"content": text}}

def table_block():
    return {
        "block_type": 100,
        "table": {
            "cells": [],
            "property": {
                "row_size": 5,
                "column_size": 3,
                "column_width": [150, 150, 200],
                "merge_info": [],
                "header_row": True
            }
        }
    }

token = get_token()
print(f"Token: {token[:20]}...")

# 创建文档
result = create_doc(token, "GitHub AI Skills榜单与OpenHuman分析 2026-05-19")
print("Create result:", result)
doc_token = result.get("data", {}).get("document", {}).get("document_id")
print(f"Doc ID: {doc_token}")

if not doc_token:
    print("Failed to create doc")
    exit(1)

# 添加内容
blocks = [
    heading_block("GitHub AI Skills榜单（第3集）", 1),
    text_block("日期: 2026-05-19 | 来源: 抖音 - 完全AI"),
    divider_block(),
    heading_block("本周变化", 2),
    text_block("hermes agent成为最大黑马冲到第二名，financial services和deepseatrade新晋上榜，三个老面孔告别榜单"),
    divider_block(),
    heading_block("榜单排名", 2),
    ordered_block("mattpocock/skills - 8.5万Stars - 实用工程师技能"),
    ordered_block("hermes agent - 15.2万Stars - 与用户一同成长的智能体"),
    ordered_block("andrej karpathy skills - 13.1万Stars - 改善Cloud Code表现"),
    ordered_block("deepseatrade - 3.0万Stars - 终端运行DeepSEA模型编码智能体"),
    ordered_block("c switch - 7.2万Stars - 多模型跨平台桌面一体化助手"),
    ordered_block("agent skills - 4.2万Stars - AI编码生产级工程技能"),
    ordered_block("openyou - 9.1万Stars - 私人AI超级智能"),
    ordered_block("agentmary - 9.7万Stars - 最佳持久内存"),
    ordered_block("helloagents - 5.0万Stars - 智能体原理与实践"),
    divider_block(),
    heading_block("OpenHuman强势登顶", 1),
    text_block("来源: 抖音 - AI有点聊 | 时长: 4:18 | 作者: @opengod"),
    divider_block(),
    heading_block("痛点分析", 2),
    text_block("OpenClaw(龙虾): 依赖交互记忆，有冷启动难题"),
    text_block("HermesAgent(爱马仕): 需要\"教\"才能了解用户"),
    text_block("OpenHuman: 打破冷启动，无需教即可了解一切"),
    divider_block(),
    heading_block("OpenHuman三步原理", 2),
    ordered_block("一键连接"),
    ordered_block("20分钟无感抓取"),
    ordered_block("生成记忆树"),
    divider_block(),
    heading_block("三大创新机制", 2),
    bullet_block("TokenJuice: 减少Token消耗，记住高达10亿Token信息"),
    bullet_block("潜意识循环: Agent可自主决定待办事项，化身虚拟形象加入线上会议"),
    divider_block(),
    heading_block("选型指南", 2),
    text_block("OpenClaw(龙虾): 适合跨平台执行网关"),
    text_block("HermesAgent(爱马仕): 适合自我成长型员工"),
    text_block("OpenHuman: 适合贴身助理"),
    divider_block(),
    heading_block("结语", 2),
    text_block("Agent发展方向 = 执行力 + 学习力 + 记忆力"),
]

result = add_blocks(token, doc_token, blocks)
print(f"Blocks added: {len(blocks)}")
print(f"Result: {result}")
print(f"\n✅ 文档地址: https://feishu.cn/docx/{doc_token}")
