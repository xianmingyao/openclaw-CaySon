#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书写入：OpenViking字节跳动Agent开源记忆系统"""
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

result = create_doc(token, "OpenViking：字节跳动的Agent开源记忆系统（第36集）")
doc_token = result.get("data", {}).get("document", {}).get("document_id")
print(f"Doc ID: {doc_token}")

all_blocks = [
    heading_block("来源信息", 2),
    bullet_block("视频: https://v.douyin.com/PWSBOoqNyPM/"),
    bullet_block("博主: 每日AI评论 (3.2万粉/13.8万赞)"),
    bullet_block("时长: 08:59 | 日期: 2026-05-19"),
    bullet_block("数据: 1113赞 25评论 1158转发 204收藏"),
    bullet_block("合集: Agent从原理到落地（第36集）"),
    bullet_block("标签: #ai #技术分享 #Agent"),
    divider_block(),

    heading_block("核心观点", 2),
    text_block("字节跳动开源的OpenViking记忆系统采用虚拟文件系统和层级结构，解决了当前Agent记忆系统的五大痛点，通过三层分级加载、目录递归检索等方法，任务完成率提升43%-49%，输入TOKEN成本降低83%-96%。"),
    divider_block(),

    heading_block("章节详解", 2),

    heading_block("00:13 - 当前Agent记忆系统的五大问题", 3),
    bullet_block("记忆量有限 — 受限于上下文窗口大小"),
    bullet_block("检索缺乏探索能力 — 只能做平面向量搜索，无法递归探索"),
    bullet_block("记忆无结构 — 所有记忆平铺，无法组织成层级"),
    bullet_block("Token消耗无精细控制 — 无法按需控制"),
    bullet_block("经验不会自动沉淀 — Agent执行经验无法自动积累"),

    heading_block("02:30 - OpenViking的解决思路", 3),
    ordered_block("虚拟文件系统统一管理上下文 — 将Agent的上下文组织成层级结构的虚拟文件系统"),
    ordered_block("三层分级加载 — 按需加载，而非一次性加载全部上下文"),
    ordered_block("目录递归检索替代平面向量搜索 — 沿层级结构递归下钻检索"),
    ordered_block("检索轨迹可视化 — 可以追踪检索路径，便于分析和调试"),
    ordered_block("自动记忆提取和自我迭代 — Agent执行经验自动沉淀为记忆，系统可以自我优化"),

    heading_block("07:06 - 效果数据", 3),
    bullet_block("任务完成率：提升 43%-49%"),
    bullet_block("输入TOKEN成本：降低 83%-96%"),

    heading_block("07:28 - 总结", 3),
    text_block("OpenViking核心思路：将Agent上下文组织成有层级结构的虚拟文件系统，按需加载，检索时沿层级结构递归下钻。"),

    heading_block("07:42 - 级联更新问题", 3),
    text_block("OpenViking不能直接解决级联更新问题，但层级结构部分缓解了该问题，目前没有记忆系统能从根本解决，依赖Agent的推理能力。"),

    divider_block(),

    heading_block("核心架构：虚拟文件系统类比", 2),
    bullet_block("OS层面 ↔ OpenViking层面"),
    bullet_block("文件系统 ↔ Agent记忆系统"),
    bullet_block("目录/文件夹 ↔ 记忆分类/主题"),
    bullet_block("文件 ↔ 单条记忆"),
    bullet_block("递归遍历 ↔ 递归检索"),

    heading_block("评论金句", 3),
    text_block("memory更像计算机的外存了。os依靠文件树来维护全部文件，agent靠llm读取每个文件夹的摘要维护记忆。", True),
    text_block("用这个模型多了你的所有习惯和特点就都被记录了。— 隐私担忧", True),
    divider_block(),

    heading_block("关联知识", 2),
    bullet_block("与Hermes Agent：有用户指出OpenViking借鉴了Hermes的思路"),
    bullet_block("与内部大脑四大核心（第140集）：OpenViking解决的是记忆与上下文管理模块"),
    bullet_block("与京麦智能体：层级记忆结构非常适合电商场景，TOKEN成本降低83%-96%对业务很重要"),

    heading_block("一句话总结", 2),
    text_block("OpenViking将Agent记忆系统类比OS文件系统，通过层级结构+递归检索+按需加载，解决了记忆量、检索能力、结构化、Token成本、经验沉淀五大问题，任务完成率提升43%-49%，成本降低83%-96%。", True),
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
