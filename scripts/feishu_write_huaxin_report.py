#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书写入：华人清洗BU分润小程序需求评估报告"""
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
result = create_doc(token, "华人清洗·BU分润小程序需求评估报告")
doc_token = result.get("data", {}).get("document", {}).get("document_id")
print(f"Doc ID: {doc_token}")

all_blocks = [
    heading_block("项目概述", 2),
    heading_block("项目背景", 3),
    text_block("华人清洗已制定《N级BU/SU双轨裂变收益制度》，对标ASEA成熟商业模型。目前依赖Excel手工核算与钉钉有成业财系统，亟需开发专用分润小程序。"),
    heading_block("建设目标", 3),
    bullet_block("自动化：业绩数据从有成CRM自动同步，奖金自动计算、自动发放"),
    bullet_block("可视化：为每位BU/SU提供个人双轨树形图（无限代）、收益看板"),
    bullet_block("合规化：所有计算逻辑严格对齐制度文件，内置风控与封顶规则"),
    bullet_block("生态化：完全基于钉钉微应用开发，使用有成CRM开放API进行数据读写"),
    heading_block("技术定性", 3),
    text_block("系统类型：钉钉H5微应用（小程序），不是Web系统", True),
    text_block("基于勾股OA开发：否，勾股OA是PHP Web系统，无法做钉钉小程序集成", True),
    text_block("复用率：仅约5%（权限模型思路可借鉴）", True),
    divider_block(),

    heading_block("业务规则核心", 2),
    heading_block("双轨架构", 3),
    bullet_block("一级BU：无限推荐，直推数量不限"),
    bullet_block("二级BU及以后：每人仅左、右两条主线"),
    bullet_block("自动滑落：第3人及以后自动向下滑落至最深空位"),
    bullet_block("深度：无限代"),
    heading_block("积分体系", 3),
    bullet_block("PV：个人业绩（合同回款不含税）"),
    bullet_block("RV左/右线：左/右线所有下级PV之和"),
    bullet_block("GV：所有下级PV之和（无限代）"),
    bullet_block("PGV：达成职级条件的GV"),
    heading_block("五大奖金", 3),
    bullet_block("直推奖：直推BU首年利润x5% + 次年利润x2%"),
    bullet_block("对碰奖：MIN(左线RV, 右线RV) x 2%，月封顶=PVx30%"),
    bullet_block("代数奖：1-10代x1%，11-20代x0.5%，21代+x0.2%"),
    bullet_block("滑落奖：滑落BU首年利润x1%"),
    bullet_block("职级分红：白金/钻石/总统钻石按季度瓜分奖金池"),
    divider_block(),

    heading_block("技术架构方案", 2),
    heading_block("技术选型", 3),
    bullet_block("前端：钉钉H5微应用（Vue3/uni-app）"),
    bullet_block("后端：Python FastAPI"),
    bullet_block("数据库：MySQL 8.0 + Redis"),
    bullet_block("定时任务：Celery + Redis"),
    heading_block("自动滑落算法核心", 3),
    text_block("1. 检查目标线上级节点是否满员（左右各2人）"),
    text_block("2. 若满，递归向下找空位"),
    text_block("3. 优先滑落到较浅的子树（保持平衡）"),
    text_block("4. 返回最终安置节点ID"),
    heading_block("对碰奖算法", 3),
    text_block("MIN(左线RV, 右线RV) x 2%，与 PVx30% 取小"),
    text_block("小区业绩归零，大区剩余业绩自动结转到下月"),
    divider_block(),

    heading_block("开发周期评估", 2),
    heading_block("MVP精简版（方案A）", 3),
    bullet_block("工期：约82个工作日"),
    bullet_block("费用：¥141,000（含6%增值税专票）"),
    bullet_block("包含：核心奖金+树展示+CRM对接"),
    heading_block("全功能版（方案B）", 3),
    bullet_block("工期：约116个工作日"),
    bullet_block("费用：¥201,400（含6%增值税专票）"),
    bullet_block("包含：完整5大奖金+完整集成+职级分红"),
    heading_block("运维费用", 3),
    bullet_block("首年运维：¥20,000-36,000/年（服务器+监控+故障响应）"),
    divider_block(),

    heading_block("Excel公式问题", 2),
    text_block("直推奖公式Bug：推荐人=A3会匹配自身，应为匹配推荐人ID列（严重度高）", True),
    text_block("代数奖公式Bug：3个SUM条件都基于同一利润列，无视代数筛选（严重度高）", True),
    text_block("代数奖梯度缺失：11-20代0.5%、21代+0.2%没有正确体现（严重度高）", True),
    text_block("无限代无法实现：Excel SUM无法递归遍历（严重度中）", True),
    text_block("结论：Excel只能作为数据模板，实际奖金计算必须由后端代码实现", True),
    divider_block(),

    heading_block("验收标准", 2),
    bullet_block("成功从有成CRM测试环境拉取回款数据，自动生成PV"),
    bullet_block("构造3层双轨树，手工验算5大奖金，误差<0.01元"),
    bullet_block("测试自动滑落：新注册用户自动出现在最深空位"),
    bullet_block("月度对碰奖封顶生效：超过PVx30%时提示截留"),
    bullet_block("100人并发访问双轨树，平均响应<2秒"),
    bullet_block("所有操作留存日志，PU管理员可追溯"),
    divider_block(),

    heading_block("供应商必须能回答的问题", 2),
    bullet_block("递归计算方案：无限代向上遍历祖先节点，SQL怎么写？"),
    bullet_block("性能方案：5000节点双轨树，对碰奖全量核算如何在30秒内完成？"),
    bullet_block("滑落算法：如何找到最深空位？并发注册时冲突如何处理？"),
    bullet_block("数据一致性：并发注册时，两个用户同时绑定同一节点如何处理？"),
    divider_block(),

    heading_block("交付物清单", 2),
    bullet_block("钉钉H5微应用包（前端+后端）"),
    bullet_block("源代码（含注释）"),
    bullet_block("数据库脚本（建表语句、初始化数据）"),
    bullet_block("部署与运维手册"),
    bullet_block("用户操作手册（分角色）"),
    bullet_block("API接口文档"),
    divider_block(),

    heading_block("本地文件位置", 2),
    text_block("E:\\workspace\\knowledge\\华人清洗-BU分润小程序-需求评估报告.md", True),
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
