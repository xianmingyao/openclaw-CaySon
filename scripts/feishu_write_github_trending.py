#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接通过飞书Open API创建文档"""
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

def text_block(text, bold=False):
    t = {"content": text, "text_element": {}}
    if bold:
        t["text_element"]["text_run"] = {"content": text, "text_run_style": {"bold": True}}
    else:
        t["text_element"]["text_run"] = {"content": text}
    return {
        "block_type": 2,
        "text": t
    }

def heading_block(text, level=1):
    return {
        "block_type": 3,
        "heading1": {"elements": [{"text_run": {"content": text}}], "style": {}}
    } if level == 1 else {
        "block_type": 4 if level == 2 else 5,
        f"heading{level}": {"elements": [{"text_run": {"content": text}}], "style": {}}
    }

def divider_block():
    return {"block_type": 22, "divider": {}}

def quote_block(text):
    return {
        "block_type": 27,
        "quote_container": {
            "blocks": [{
                "block_type": 2,
                "text": {"content": text, "text_element": {"text_run": {"content": text}}}
            }]
        }
    }

CONTENT = [
    {"tag": "h1", "text": "GitHub一周热榜Top20 2026年第20周"},
    {"tag": "p", "text": "来源：抖音@AI爆款 / @数智AI日记 / 小红书JIED喵ai小王 | 整理时间：2026-05-14"},
    {"tag": "divider"},
    {"tag": "h2", "text": "🏆 完整榜单 Top 8"},
    {"tag": "table", "headers": ["排名", "项目", "Stars", "本周增长", "亮点"],
     "rows": [
        ["🥇", "Ruflo", "49,757", "+7,088", "多Agent协作开发团队"],
        ["🥈", "UI-TARS-desktop", "33,524", "+3,872", "字节开源/24h虚拟助理"],
        ["🥉", "PageIndex", "30,851", "+4,351", "轻量RAG/不用向量数据库"],
        ["4", "DeepSeek-TUI", "26,452", "—", "DeepSeek终端界面"],
        ["5", "Anthropic Financial", "21,515", "—", "金融Agent"],
        ["6", "9router", "9,352", "—", "字节跳动"],
        ["7", "CloakBrowser", "7,863", "+5,488", "反检测浏览器"],
        ["8", "Local Deep Research", "7,373", "—", "本地深度研究"],
    ]},
    {"tag": "divider"},
    {"tag": "h2", "text": "🔥 本周黑马项目"},
    {"tag": "h3", "text": "Obscura — Rust无头浏览器"},
    {"tag": "bullet", "text": "⭐ 9.9k stars（21天，即将破万）"},
    {"tag": "bullet", "text": "💡 内存仅30MB（Chrome 200MB的15%）"},
    {"tag": "bullet", "text": "⚡ 加载仅85ms（Chrome 500ms的17%）"},
    {"tag": "bullet", "text": "🤖 AI Native / AI Agent原生支持"},
    {"tag": "bullet", "text": "🔥 爬虫圈·硅谷刷屏"},
    {"tag": "divider"},
    {"tag": "h2", "text": "💡 本周趋势信号总结"},
    {"tag": "h3", "text": "1. AI Agent团队协作赛道爆发"},
    {"tag": "p", "text": 'Ruflo 49k stars断档第一，+7,088/周。核心叙事：从「AI写代码」→ 「AI像工程团队一样思考」'},
    {"tag": "h3", "text": "2. 浏览器自动化两极分化"},
    {"tag": "p", "text": "反检测（CloakBrowser）vs 轻量高速（Obscura）"},
    {"tag": "h3", "text": "3. 字节跳动多点开花"},
    {"tag": "p", "text": "UI-TARS-desktop（#2，33k stars）+ 9router（#6，9k stars）"},
    {"tag": "h3", "text": "4. RAG轻量化成刚需"},
    {"tag": "p", "text": "PageIndex：不用向量数据库，部署轻十倍"},
    {"tag": "h3", "text": "5. DeepSeek生态持续爆发"},
    {"tag": "p", "text": "DeepSeek-TUI稳居#4（26k stars）"},
    {"tag": "h3", "text": "6. 本地化AI研究成新热点"},
    {"tag": "p", "text": "Local Deep Research：本地深度研究工具"},
    {"tag": "divider"},
    {"tag": "h2", "text": "📊 互动数据"},
    {"tag": "table", "headers": ["项目", "点赞", "收藏", "转发"],
     "rows": [
        ["抖音@AI爆款（总览）", "740", "1262", "190"],
        ["Obscura（@数智AI日记）", "1312", "556", "3353"],
    ]},
    {"tag": "p", "text": "观察：收藏 > 点赞说明用户倾向先收藏以后用；Obscura转发3353 >> 点赞1312，大家抢着转给同事群友"},
    {"tag": "divider"},
    {"tag": "p", "text": "原文：E:\\workspace\\knowledge-base\\raw\\GitHub-Trending-2026-05-14-Week20.md"},
]

def build_blocks(content):
    blocks = []
    for item in content:
        tag = item["tag"]
        if tag == "h1":
            blocks.append({"block_type": 3, "heading1": {"elements": [{"text_run": {"content": item["text"]}}], "style": {}}})
        elif tag == "h2":
            blocks.append({"block_type": 4, "heading2": {"elements": [{"text_run": {"content": item["text"]}}], "style": {}}})
        elif tag == "h3":
            blocks.append({"block_type": 5, "heading3": {"elements": [{"text_run": {"content": item["text"]}}], "style": {}}})
        elif tag == "p":
            blocks.append({"block_type": 2, "text": {"elements": [{"text_run": {"content": item["text"]}}], "style": {}}})
        elif tag == "bullet":
            blocks.append({"block_type": 12, "bullet": {"elements": [{"text_run": {"content": item["text"]}}], "style": {}}})
        elif tag == "divider":
            blocks.append({"block_type": 22, "divider": {}})
        elif tag == "table":
            # 表格用paragraph模拟
            header_text = " | ".join(item["headers"])
            blocks.append({"block_type": 2, "text": {"elements": [{"text_run": {"content": header_text, "text_run_style": {"bold": True}}}], "style": {}}})
            for row in item["rows"]:
                blocks.append({"block_type": 2, "text": {"elements": [{"text_run": {"content": " | ".join(row)}}], "style": {}}})
    return blocks

def main():
    print("=" * 50)
    print("创建飞书文档: GitHub一周热榜Top20 2026年第20周")
    print("=" * 50)

    # 获取token
    print("\n[1] 获取访问令牌...")
    token = get_token()
    if not token:
        print("[ERROR] 获取token失败")
        return
    print(f"[OK] token获取成功")

    # 创建文档
    print("\n[2] 创建文档...")
    result = create_doc(token, "GitHub一周热榜Top20 2026年第20周")
    doc_token = result.get("data", {}).get("document", {}).get("document_id")
    if not doc_token:
        print(f"[ERROR] 创建文档失败: {result}")
        return
    doc_url = f"https://feishu.cn/docx/{doc_token}"
    print(f"[OK] 文档创建成功: {doc_url}")

    # 添加内容
    print("\n[3] 写入内容...")
    blocks = build_blocks(CONTENT)
    # 分批写入（每批50个block）
    batch_size = 50
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i+batch_size]
        r = add_blocks(token, doc_token, batch)
        if r.get("code") != 0:
            print(f"[WARN] 批次{i//batch_size+1}写入有问题: {r}")
    print(f"[OK] 内容写入完成 ({len(blocks)}个block)")

    print(f"\n✅ 文档地址: {doc_url}")
    print("=" * 50)

if __name__ == "__main__":
    main()
