#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书写入：GitHub周趋势DeepSeek黑马"""
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

result = create_doc(token, "GitHub最新周趋势：DeepSeek-TUI成黑马")
doc_token = result.get("data", {}).get("document", {}).get("document_id")
print(f"Doc ID: {doc_token}")

all_blocks = [
    heading_block("来源信息", 2),
    bullet_block("视频: https://v.douyin.com/KZLQYvHFPGU/"),
    bullet_block("类型: 图文作品"),
    bullet_block("博主: Ai工具实战派 (237粉/1098赞)"),
    bullet_block("日期: 2026-05-17"),
    bullet_block("数据: 329赞 6评论 268转发 41收藏"),
    bullet_block("标签: #github #ai #Agent #工具 #ai工具"),
    divider_block(),

    heading_block("本周趋势亮点", 2),

    heading_block("1. 本周最大黑马：DeepSeek-TUI", 3),
    bullet_block("Stars增量: +21,752"),
    bullet_block("技术栈: Rust编写"),
    bullet_block("定位: DeepSeek终端界面"),
    bullet_block("影响: 在开发者圈引发强烈关注"),

    heading_block("2. AI Agent生态主导", 3),
    text_block("AI Agent工具链和编码助手类项目持续占据排行榜核心位置，基础设施类或非AI项目几乎难以进入前列。"),
    text_block("趋势判断: AI原生项目正在全面压制传统基础设施项目。"),

    heading_block("3. 官方项目受到追捧", 3),
    bullet_block("Anthropic官方金融服务仓库本周大涨12,088颗星"),
    text_block("显示机构正在认真评估Claude在合规金融领域的应用。"),
    text_block("信号: 企业级AI应用正在从概念走向落地。"),

    heading_block("4. 老将重登场：Redis创始人antirez", 3),
    bullet_block("项目: ds4（纯C语言实现的本地DeepSeek推理引擎）"),
    bullet_block("成绩: Hacker News获得497点赞、157条评论"),
    bullet_block("特点: 新仓库未进总星数前10，但技术圈口碑爆棚"),

    divider_block(),

    heading_block("趋势分析", 2),
    heading_block("为什么DeepSeek-TUI能爆？", 3),
    ordered_block("Rust性能加持: 高性能终端体验"),
    ordered_block("DeepSeek品牌效应: DeepSeek系列持续火热"),
    ordered_block("开发者刚需: 终端AI交互是真实需求"),
    ordered_block("开源光环: 开发者社区的强烈关注"),

    heading_block("AI Agent赛道为什么持续火热？", 3),
    ordered_block("工具链成熟: MCP等协议标准化"),
    ordered_block("场景落地: 从概念到实际应用"),
    ordered_block("资本追捧: 机构资金持续流入"),
    ordered_block("开发者热情: 工具类项目天然受开发者关注"),

    heading_block("Claude金融应用为什么受关注？", 3),
    ordered_block("合规需求: 金融行业对AI合规性要求高"),
    ordered_block("Anthropic品牌: Claude在推理能力上的口碑"),
    ordered_block("企业级市场: 金融是AI企业级应用的标杆行业"),

    divider_block(),

    heading_block("一句话总结", 2),
    text_block("DeepSeek-TUI成为本周最大黑马，AI Agent工具链全面主导GitHub趋势，Anthropic官方项目受机构追捧，老将antirez用纯C语言再创开源奇迹。", True),

    heading_block("推荐视频", 2),
    bullet_block("Claude Code接入DeepSeek V4（8079赞）— 康老狮-AI实战"),
    bullet_block("DeepSeek V4万亿参数100万上下文（1.8万赞）— 内部看美国"),
    bullet_block("AI炼丹时代KK对话（8.2万赞）— 学院派Academia"),
    bullet_block("李想推荐Claude Code（3.4万赞）— 财经网科技"),
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
