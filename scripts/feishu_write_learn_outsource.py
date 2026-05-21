#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书写入：别把学习外包-认知债务"""
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

# 创建文档
result = create_doc(token, "google技术总监：别把学习外包，这会让你欠下认知债务")
doc_token = result.get("data", {}).get("document", {}).get("document_id")
print(f"Doc ID: {doc_token}")

# 分批写入，每批不超过50个block
all_blocks = [
    heading_block("来源信息", 2),
    bullet_block("视频: https://v.douyin.com/4YbeE6xupfw/"),
    bullet_block("博主: 慢学AI (粉丝5.0万/获赞15.7万)"),
    bullet_block("时长: 07:35 | 日期: 2026-05-19"),
    bullet_block("数据: 68赞 1评论 34转发 14收藏"),
    bullet_block("标签: #大模型开发 #人工智能 #学习外包 #认知债务 #vibecoding"),
    divider_block(),

    heading_block("核心观点", 2),
    text_block("AI写代码最危险的情况，不是它写错了，而是它写对了——Bug消失了，项目跑起来了，但你的mental model可能完全没动。"),
    text_block("Addy Osmani在《Don't Outsource the Learning》里提醒：AI默认优化的是完成任务，不是让你变强。"),
    divider_block(),

    heading_block("章节详解", 2),

    heading_block("00:00 - AI对认知模型的影响", 3),
    text_block("AI修复Bug后，认知模型可能未改变，学习过程被跳过。"),

    heading_block("02:14 - 学习与任务的区分", 3),
    text_block("任务完成 ≠ 学习，放弃主动理解 = 欠下认知债务。"),

    heading_block("03:13 - AI工具的局限性", 3),
    text_block("AI默认优化的是交付，不是学习。学习藏在摩擦里（the learning is in the friction）。"),

    heading_block("03:41 - 可交给AI的任务", 3),
    text_block("重复样板代码、胶水代码、格式化/重构、简单CRUD、查文档/示例。"),

    heading_block("03:54 - 不能纯委托的任务", 3),
    text_block("系统架构设计、核心业务逻辑、性能调优决策、安全关键代码、任何你必须理解才能演进的东西。"),

    heading_block("04:19 - 把学习重新嵌入工作流（六个动作）", 3),
    ordered_block("形成假说 — 先自己想一遍，再问AI"),
    ordered_block("解释后要代码 — 我来解释我想做什么，你来写"),
    ordered_block("打开学习模式 — 不要只给代码，给我讲原理"),
    ordered_block("评审AI输出 — 这段代码在做什么？为什么这样设计？"),
    ordered_block("手写重推 — 理解后合上AI，自己写一遍"),
    ordered_block("让模型解释 — 为什么这个Bug这样修？背后的原因是什么？"),

    heading_block("06:50 - 结语", 3),
    text_block("交付和学习是两张账，不要把学习外包给AI。"),
    divider_block(),

    heading_block("理论支撑", 2),
    bullet_block("Addy Osmani《Don't Outsource the Learning》(Google技术总监)"),
    bullet_block("Anthropic 研究"),
    bullet_block("MIT 研究"),
    bullet_block("CHI (ACM CHI Conference) 研究"),
    divider_block(),

    heading_block("关联知识", 2),

    heading_block("与Matt Pocock Skills的关联", 3),
    text_block("Matt Pocock主张正确使用AI工具的理念与本文高度一致。六个动作 ≈ Matt Pocock的AI辅助学习最佳实践。核心：AI是放大镜，不是替代品。"),

    heading_block("与Vibe Coding话题的关联", 3),
    text_block("Vibe Coding：感觉在写代码，实际是AI在写。本视频：感觉在完成任务，实际学习被外包了。本质都是：交付 vs 成长的张力。"),

    heading_block("与京麦智能体的关联", 3),
    text_block("跨境电商Agent开发中，需要明确哪些逻辑必须人理解、哪些可以委托AI。核心业务逻辑（定价/库存/物流）→ 不能纯委托。标准化流程（商品上架/回复模板）→ 可交给AI。"),
    divider_block(),

    heading_block("金句摘录", 2),
    text_block("AI写代码最危险的情况，可能不是它写错了，而是它写对了。", True),
    text_block("AI默认优化的是完成任务，不是让你变强。", True),
    text_block("交付和学习是两张账，不要把学习外包给AI。", True),
    text_block("学习藏在摩擦中。", True),
    divider_block(),

    heading_block("相关资源", 2),
    bullet_block("Addy Osmani: https://x.com/addyosmani/status/2056078124346228860"),
    bullet_block("慢学AI频道: 抖音@慢学AI"),
]

# 分批：每批50条
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
