#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书写入：产品经理AI工具清单"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
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
    resp = requests.post(f"{BASE_URL}/docx/v1/documents", headers={"Authorization": f"Bearer {token}"}, json={"title": title})
    return resp.json()

def add_blocks(token, doc_token, blocks):
    resp = requests.post(
        f"{BASE_URL}/docx/v1/documents/{doc_token}/blocks/{doc_token}/children",
        headers={"Authorization": f"Bearer {token}"},
        json={"children": blocks, "index": -1}
    )
    return resp.json()

def text_block(content, bold=False):
    style = {"bold": True} if bold else {}
    return {
        "block_type": 2,
        "text": {
            "elements": [{"text_run": {"content": content, "text_run_style": style}}],
            "style": {}
        }
    }

def heading_block(content, level):
    return {
        "block_type": 2 + level,
        f"heading{level}": {
            "elements": [{"text_run": {"content": content, "text_run_style": {}}}],
            "style": {}
        }
    }

def bullet_block(content, indent=0):
    return {
        "block_type": 12,
        "bullet": {
            "elements": [{"text_run": {"content": content, "text_run_style": {}}}],
            "style": {"indent_level": indent}
        }
    }

def ordered_block(content, indent=0):
    return {
        "block_type": 13,
        "ordered": {
            "elements": [{"text_run": {"content": content, "text_run_style": {}}}],
            "style": {"indent_level": indent}
        }
    }

def divider_block():
    return {"block_type": 22, "divider": {}}

token = get_token()
print(f"Token OK: {bool(token)}")

result = create_doc(token, "产品经理AI工具清单：Loable原型神器")
doc_token = result.get("data", {}).get("document", {}).get("document_id")
print(f"Doc ID: {doc_token}")

all_blocks = [
    heading_block("来源信息", 2),
    bullet_block("视频: https://v.douyin.com/gGZ5oSYo7N4/"),
    bullet_block("博主: 吃土说AI"),
    bullet_block("时长: 00:32 | 日期: 2026-03-03"),
    bullet_block("数据: 5410赞 79评论 6649转发 772收藏"),
    bullet_block("标签: #ai #人工智能 #ai工具 #产品经理 #效率"),
    divider_block(),

    heading_block("评论区工具清单", 2),

    heading_block("1. Loable — AI原型工具（强烈推荐）", 3),
    bullet_block("定位: AI驱动的产品原型生成工具"),
    bullet_block("用户评价: 原型用Loable就行了，哪里需要这么麻烦"),
    bullet_block("核心优势: 自然语言描述生成原型、快速迭代、多人协作"),
    bullet_block("缺点: 除了贵都是优点"),
    bullet_block("适合场景: 快速原型验证、MVP阶段"),

    heading_block("2. Stitch — AI原型替代品", 3),
    bullet_block("定位: Loable的替代方案"),
    bullet_block("用户评价: stitch也不错"),
    bullet_block("核心优势: 类似Loable的原型生成能力，可能有价格优势"),

    heading_block("3. Figma Make — Figma官方AI", 3),
    bullet_block("定位: Figma内置的AI原型生成"),
    bullet_block("核心优势: 与Figma无缝集成、设计到原型一体化"),
    bullet_block("适合场景: 已经在用Figma的团队"),

    heading_block("4. Claude Code — 编码助手", 3),
    bullet_block("定位: AI编程/代码生成工具"),
    bullet_block("用户评价: 用Claude一把梭"),
    bullet_block("核心优势: 代码生成能力强、支持多轮对话、上下文理解能力强"),
    bullet_block("适合场景: 需要写代码验证想法的PM"),

    heading_block("5. 龙虾 — 评论区提及", 3),
    bullet_block("来源: 多位评论区用户提及，具体功能未知"),
    divider_block(),

    heading_block("工具对比分析", 2),
    heading_block("原型工具横向对比", 3),
    bullet_block("Loable: 贵 | 上手⭐⭐ | AI能力⭐⭐⭐⭐⭐ | 适合MVP/原型"),
    bullet_block("Stitch: 中 | 上手⭐⭐ | AI能力⭐⭐⭐⭐ | 适合原型"),
    bullet_block("Figma Make: 含在Figma里 | 上手⭐⭐⭐ | AI能力⭐⭐⭐ | 适合设计团队"),
    bullet_block("Claude Code: 免费/付费 | 上手⭐⭐⭐ | AI能力⭐⭐⭐⭐ | 适合技术PM"),

    heading_block("PM工作流中的AI工具使用场景", 3),
    ordered_block("需求分析阶段: Claude Code写脚本、ChatGPT润色文档"),
    ordered_block("原型设计阶段: Loable生成原型、Figma Make设计转原型、Stitch快速迭代"),
    ordered_block("文档撰写阶段: Claude Code生成PRD模板、Notion AI整理文档"),
    ordered_block("项目管理阶段: Cursor代码片段、GitHub Copilot评审技术方案"),

    divider_block(),

    heading_block("评论区金句", 2),
    text_block("原型用Loable就行了，哪里需要这么麻烦", True),
    text_block("用Loable [流泪] 除了贵都是优点，stitch也不错", True),
    text_block("用Claude一把梭", True),
    divider_block(),

    heading_block("一句话总结", 2),
    text_block("Loable是原型神器（贵但值），Stitch是平替方案，Figma Make适合设计团队，Claude Code是技术PM的瑞士军刀。", True),

    heading_block("待深挖", 2),
    bullet_block("Loable详细功能和定价"),
    bullet_block("龙虾AI工具的具体信息"),
    bullet_block("Stitch vs Loable详细对比"),
]

batch_size = 50
for i in range(0, len(all_blocks), batch_size):
    batch = all_blocks[i:i+batch_size]
    r = add_blocks(token, doc_token, batch)
    code = r.get('code')
    if code != 0:
        print(f"Batch {i//batch_size} error {code}: {r.get('msg', '')}")
    else:
        print(f"Batch {i//batch_size} OK ({len(batch)} blocks)")

print(f"\n✅ 飞书文档: https://feishu.cn/docx/{doc_token}")
