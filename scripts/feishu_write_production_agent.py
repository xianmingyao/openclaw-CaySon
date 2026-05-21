#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书写入：生产级AI Agent架构详解"""
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

result = create_doc(token, "第140集 | 生产级AI Agent架构详解（AI大模型学习）")
doc_token = result.get("data", {}).get("document", {}).get("document_id")
print(f"Doc ID: {doc_token}")

all_blocks = [
    heading_block("来源信息", 2),
    bullet_block("视频: https://v.douyin.com/QqCzcYXh-w8/"),
    bullet_block("博主: AI大模型学习 (粉丝13.9万/获赞28.0万)"),
    bullet_block("时长: 16:03 | 日期: 2026-05-19"),
    bullet_block("数据: 258赞 10评论 202转发 34收藏"),
    bullet_block("合集: 每天讲透一个知识点（第140集）"),
    bullet_block("标签: #人工智能 #大模型 #AI大模型 #大模型学习 #Agent"),
    divider_block(),

    heading_block("核心观点", 2),
    text_block("生产级AI Agent架构详解，包括MCP的危机与定位、降低成本的方法、真实案例、内部大脑的运作以及未来的生态蓝图。"),
    text_block("MCP在云端环境中具有重要价值，通过工具搜索和程序化工具调用降低成本，配合内部的十二大Agent模式和外部skill，实现安全高效的生产级Agent架构。"),
    divider_block(),

    heading_block("章节详解", 2),

    heading_block("00:00 - 引言", 3),
    text_block("介绍本期主题：生产级AI Agent架构"),

    heading_block("01:17 - MCP的危机与定位", 3),
    text_block("MCP面临的问题：成本高、占用上下文多、协议臃肿。"),
    text_block("Anthropic的判断：MCP适用于云端环境，提供强安全隔离的标准化远程接入层。"),

    heading_block("04:21 - 降低成本的方法", 3),
    bullet_block("Tool Search：减少工具定义的TOKEN消耗"),
    bullet_block("程序化工具调用：减少数据搬运开销"),
    text_block("核心思路：用技术手段降低MCP的使用成本"),

    heading_block("06:46 - 真实案例", 3),
    text_block("Cloud Fail案例：通过MCP暴露两个工具，实现高效的API调用，显著降低TOKEN消耗。"),

    heading_block("07:56 - 内部大脑的运作（四大核心）", 3),
    ordered_block("记忆与上下文管理 — Agent维护长期记忆，上下文窗口管理，会话状态保持"),
    ordered_block("工作流编排 — 任务分解与调度，多步骤协作，条件分支处理"),
    ordered_block("工具权限切分 — 细粒度权限控制，安全隔离，最小权限原则"),
    ordered_block("确定性自动化 — 可预测的执行路径，错误处理与恢复，审计日志"),

    heading_block("13:08 - 未来的生态蓝图", 3),
    bullet_block("CLI + Skills：适合本地/轻量场景"),
    bullet_block("MCP + Skills：适合云端/企业场景"),
    text_block("核心是十二大Agent模式"),

    heading_block("15:17 - 总结", 3),
    text_block("MCP在云端找到定位，通过技术降低成本，配合内部模式和外部skill，实现安全的生产级Agent架构。"),
    divider_block(),

    heading_block("MCP技术解析", 2),
    heading_block("什么是MCP（Model Context Protocol）", 3),
    bullet_block("全称：Model Context Protocol"),
    bullet_block("定位：AI模型与外部工具之间的标准化连接协议"),
    bullet_block("解决的问题：工具调用碎片化、上下文膨胀、安全隔离"),

    heading_block("MCP的痛点与解决方案", 3),
    bullet_block("成本高 → Tool Search"),
    bullet_block("上下文占用多 → 程序化工具调用"),
    bullet_block("协议臃肿 → 精简协议栈"),

    heading_block("MCP适用场景", 3),
    bullet_block("云端环境（强安全隔离）"),
    bullet_block("标准化远程接入"),
    bullet_block("企业级Agent部署"),
    divider_block(),

    heading_block("关联知识", 2),
    heading_block("与Matt Pocock Skills的关联", 3),
    text_block("Skills是外部能力的扩展机制，MCP是云端标准化的工具调用协议，两者结合：MCP+Skills = 生产级Agent架构。"),
    heading_block("与之前学过的Agent知识的关联", 3),
    text_block("第139集：Agent三大核心概念（ReAct/Plan+Execute/Multi-Agent）。第135集：Claude Code上下文架构。本集是Agent知识的生产级落地实践。"),
    heading_block("与京麦智能体的关联", 3),
    text_block("跨境电商Agent需要：记忆管理+工作流编排+工具权限切分。MCP协议适合云端部署场景，十二大Agent模式可能指导架构设计。"),
    divider_block(),

    heading_block("一句话总结", 2),
    text_block("MCP在云端找到了自己的精准定位，通过Tool Search和程序化调用解决成本问题，配合内部四大核心模块（记忆/工作流/权限/自动化）和外部Skills，形成完整的生产级Agent架构。", True),
    divider_block(),

    heading_block("待深挖", 2),
    bullet_block("十二大Agent模式的具体内容"),
    bullet_block("Cloud Fail案例的详细实现"),
    bullet_block("MCP协议的具体规范"),
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
