#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书写入：DD讲AI-大厂AI落地五步法"""
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

def h1(text):
    return {"block_type": 3, "heading1": {"elements": [{"text_run": {"content": text}}], "style": {}}}
def h2(text):
    return {"block_type": 4, "heading2": {"elements": [{"text_run": {"content": text}}], "style": {}}}
def h3(text):
    return {"block_type": 5, "heading3": {"elements": [{"text_run": {"content": text}}], "style": {}}}
def p(text):
    return {"block_type": 2, "text": {"elements": [{"text_run": {"content": text}}], "style": {}}}
def bullet(text):
    return {"block_type": 12, "bullet": {"elements": [{"text_run": {"content": text}}], "style": {}}}
def divider():
    return {"block_type": 22, "divider": {}}

CONTENT = [
    h1("@DD讲AI - 大厂AI落地五步法"),
    p("来源：抖音 @DD讲AI | 发布时间：2026-05-14 | 数据：292👍 247收藏 54转发"),
    divider(),
    h2("主题"),
    p("现在大厂AI落地的思路，一共五个关键环节。创业者、企业管理者和老板，希望AI落地降本增效、把业务流自动化升级，你核心要关注的5件事。"),
    divider(),
    h2("五个关键环节（章节）"),
    bullet("00:17 - 1. AI落地基建"),
    bullet("01:15 - 2. 招聘关键角色"),
    bullet("01:54 - 3. 业务流程梳理"),
    bullet("02:21 - 4. AI复利在哪里"),
    bullet("02:56 - 5. AI技术方案的选择"),
    divider(),
    h2("核心观点"),
    h3("观点1：必须有开发，无可替代"),
    bullet("AI落地不是买工具，是建能力"),
    bullet("外部工具只能解决单点，无法形成业务闭环"),
    bullet("本体团队（含开发能力）是企业AI核心资产"),
    h3("观点2：知识和业务梳理脱了层皮"),
    bullet("对应本体的业务调研+本体建模阶段"),
    bullet("服务体验边界复杂、动态，需要状态机建模"),
    bullet("业务梳理清楚后，技术方案选择变得容易"),
    h3("观点3：AI复利在哪里"),
    p("复利效应 = 高频场景 × 可积累的上下文 × 自动化执行"),
    bullet("复利高：客服/报价/审批/预警/报表"),
    bullet("复利低：一次性分析/复杂决策/创意任务"),
    divider(),
    h2("DD讲AI五步法 vs 企业AI本体 映射"),
    p("第1步：AI落地基建 → 数字化基础设施层"),
    p("第2步：招聘关键角色 → 本体团队组建"),
    p("第3步：业务流程梳理 → 本体建模(TBox+ABox)"),
    p("第4步：AI复利在哪里 → Agent价值场景选择"),
    p("第5步：AI技术方案选择 → Agent框架+工具封装"),
    divider(),
    h2("企业AI落地自测：你卡在哪一步？"),
    bullet("第1步卡住：还在用Excel，数据散乱 → 先上飞书/钉钉"),
    bullet("第2步卡住：买了工具没人用 → 招聘懂业务又懂AI的人"),
    bullet("第3步卡住：说不清业务逻辑 → 用本体建模方法"),
    bullet("第4步卡住：做了很多AI看不出价值 → 用复利公式筛选"),
    bullet("第5步卡住：Agent效果不稳定 → 第3步做扎实后技术方案自然清晰"),
    divider(),
    p("视频链接：https://www.douyin.com/video/7639407124979764480"),
    p("原始文件：E:\\workspace\\knowledge-base\\raw\\DD讲AI-大厂AI落地五步法-2026-05-14.md"),
    p("已整合到知识库：E:\\workspace\\knowledge-base\\wiki\\概念\\企业AI本体Ontology-从工具到Agent的关键.md（第12节）"),
]

def main():
    print("=" * 50)
    print("创建飞书文档: DD讲AI - 大厂AI落地五步法")
    print("=" * 50)

    token = get_token()
    if not token:
        print("[ERROR] 获取token失败")
        return
    print("[OK] token获取成功")

    result = create_doc(token, "DD讲AI - 大厂AI落地五步法")
    doc_token = result.get("data", {}).get("document", {}).get("document_id")
    if not doc_token:
        print(f"[ERROR] 创建文档失败: {result}")
        return
    doc_url = f"https://feishu.cn/docx/{doc_token}"
    print(f"[OK] 文档创建成功: {doc_url}")

    # 分批写入
    batch_size = 50
    for i in range(0, len(CONTENT), batch_size):
        batch = CONTENT[i:i+batch_size]
        r = add_blocks(token, doc_token, batch)
        if r.get("code") != 0:
            print(f"[WARN] 批次{i//batch_size+1}写入有问题: {r}")
    print(f"[OK] 内容写入完成 ({len(CONTENT)}个block)")
    print(f"\n✅ 文档地址: {doc_url}")
    print("=" * 50)

if __name__ == "__main__":
    main()
