#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书同步今日知识 2026-05-18 - 修复版"""
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

def make_text(text):
    return {
        "block_type": 2,
        "text": {
            "elements": [{"text_run": {"content": text}}],
            "style": {}
        }
    }

def make_heading(text, level=1):
    key = f"heading{level}"
    return {
        "block_type": 2 + level,  # 3=h1, 4=h2, 5=h3
        key: {
            "elements": [{"text_run": {"content": text}}],
            "style": {}
        }
    }

def make_bullet(text):
    return {
        "block_type": 12,
        "bullet": {
            "elements": [{"text_run": {"content": text}}],
            "style": {"indent_level": 1}
        }
    }

def make_divider():
    return {"block_type": 25, "divider": {}}

# 内容
title = "📚 抖音学习 2026-05-18 | CaySon知识库"

content = [
    make_heading("📅 今日抖音学习汇总", 1),
    make_divider(),
    
    make_heading("1️⃣ Omni-SimpleMem 多模态记忆框架", 2),
    make_text("来源: 抖音 - Agent创世纪 / AutoResearch"),
    make_bullet("核心: MAU冷热记忆解耦 + 新颖性过滤器 + 金字塔检索"),
    make_bullet("效果: LoCoMo基准 准确率+411%，速度3.5倍"),
    make_divider(),
    
    make_heading("2️⃣ GitHub AI热榜汇总（两个版本整合）", 2),
    make_text("来源: 抖音@赛博笔记 + @不露声色"),
    make_heading("高光项目", 3),
    make_bullet("🏦 anthropics/financial-services - Claude金融行业官方方案"),
    make_bullet("📡 RuView - WiFi透墙感知57.9K Stars"),
    make_bullet("🔥 Bun - 90.8K Stars JavaScript全能运行时新上榜"),
    make_bullet("🔒 CloakBrowser - 12.3K Stars隐身反检测浏览器"),
    make_bullet("💰 AiToEarn - 14.2K Stars AI变现多平台自动化"),
    make_bullet("🎮 supersplat - 3D AI场景编辑器，高斯泼溅技术"),
    make_divider(),
    
    make_heading("3️⃣ 一周AI大事（产品君第443集）", 2),
    make_text("核心: Google三连发 + 国产MiniCPM-V 4.6 + Sakana双产品 + 视频3D生成工具"),
    make_heading("Google系列", 3),
    make_bullet("Gemini Intelligence - Android系统级AI大脑"),
    make_bullet("Gemini Cursor - AI编程工具，对标Cursor/Copilot"),
    make_bullet("Veo 4 - 视频生成，9秒电影级画质"),
    make_heading("国产/其他", 3),
    make_bullet("MiniCPM-V 4.6 - 面壁智能，端侧运行/离线OCR"),
    make_bullet("Sakana Conductor - AI指挥官，开源工作流编排"),
    make_bullet("Sakana Fugu - 旗舰商业多Agent编排系统"),
    make_heading("视频工具", 3),
    make_bullet("Just-Dub-It - 视频配音翻译"),
    make_bullet("Articraft - 3D交互模型"),
    make_bullet("Pixal3D - 3D生成模型"),
    make_bullet("Kimi WebBridge - 浏览器扩展"),
    make_divider(),
    
    make_heading("4️⃣ Crawl4AI - GitHub 63K Star AI爬虫", 2),
    make_text("来源: 抖音@IT小圈"),
    make_bullet("项目: unclecode/crawl4ai, 63.6K Stars"),
    make_bullet("特点: LLM Friendly网页爬虫，一行Python代码搞定"),
    make_bullet("适用: RAG知识库构建、AI Agent网页信息获取"),
    make_divider(),
    
    make_heading("📊 本期趋势总结", 1),
    make_bullet("1. AI工具热度开始降温，实用工具和安全类项目重新受重视"),
    make_bullet("2. 垂直领域爆发：金融AI、交易Agent、WiFi感知等"),
    make_bullet("3. 端侧AI：MiniCPM-V等小模型持续火热"),
    make_bullet("4. 视频生成工具全面开花：配音、3D、打光、运镜"),
]

# 执行
token = get_token()
print(f"Token获取: {'成功' if token else '失败'}")

result = create_doc(token, title)
print(f"文档创建: {result}")

if result.get("code") == 0:
    doc_token = result["data"]["document"]["document_id"]
    print(f"文档ID: {doc_token}")
    
    # 分批添加（每批20条）
    batch_size = 20
    for i in range(0, len(content), batch_size):
        batch = content[i:i+batch_size]
        r = add_blocks(token, doc_token, batch)
        status = '成功' if r.get('code') == 0 else f"失败({r.get('code')})"
        print(f"批次 {i//batch_size + 1}: {status}")
    
    print(f"\n✅ 飞书文档创建成功!")
    print(f"📎 链接: https://feishu.cn/docx/{doc_token}")
else:
    print(f"❌ 失败: {result}")
