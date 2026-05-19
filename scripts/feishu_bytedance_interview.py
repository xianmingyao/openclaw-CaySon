import sys; sys.stdout.reconfigure(encoding='utf-8')
import requests, json

APP_ID = "cli_a9324982073a1bc8"
APP_SECRET = "2tOQnQmwk2bHOUAHPsHCjfcv4zLreFWE"
BASE = "https://open.feishu.cn/open-apis"

token = requests.post(BASE+"/auth/v3/tenant_access_token/internal", json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()["tenant_access_token"]
title = "字节Agent面试高频题 MCP RAG 熔断 2026-05-19"
doc = requests.post(BASE+"/docx/v1/documents", headers={"Authorization": "Bearer "+token}, json={"title": title}).json()
doc_id = doc["data"]["document"]["document_id"]
url = "https://feishu.cn/docx/" + doc_id
print("Doc:", url)

def h(lv, t):
    key = f"heading{lv}"
    return {"block_type": 2+lv, key: {"elements": [{"text_run": {"content": t}}], "style": {}}}
def p(t):
    return {"block_type": 2, "text": {"elements": [{"text_run": {"content": t}}], "style": {}}}
def div():
    return {"block_type": 22, "divider": {}}
def code(t):
    return {"block_type": 14, "code": {"elements": [{"text_run": {"content": t}}], "style": {"language": "python"}}}
def bl(t):
    return {"block_type": 12, "bullet": {"elements": [{"text_run": {"content": t}}], "style": {}}}

blocks = [
    h(1, "字节Agent面试高频题：MCP RAG 熔断"),
    p("来源：小哲讲面经 | 2026-05-11 | 3分12秒 | 3691赞"),
    p("考察：MCP适配层、ReAct Agent、工具调用、RAG、文档切片、Embedding、rerank、长期记忆、短期记忆、上下文压缩、多智能体选型、熔断降级"),
    div(),
    h(2, "1. MCP适配层"),
    p("职责：工具协议、参数校验、权限控制、超时、审计"),
    bl("可插拔：工具可动态接入/退出"),
    bl("可治理：调用记录、权限管控"),
    bl("可扩展：新工具无需改核心代码"),
    div(),
    h(2, "2. 模型写库 vs 读库"),
    p("写库：模型→外部系统（生成意图+参数，后端校验+权限+事务+审计）"),
    p("读库：外部知识→模型（RAG向量召回+rerank+生成）"),
    div(),
    h(2, "3. Agent工作模式"),
    bl("ReAct：推理+执行交替，适合复杂推理"),
    bl("Plan and Execute：计划与执行分离，适合多步骤"),
    bl("Workflow：固定流程，适合线上业务（越靠近业务越不自由）"),
    div(),
    h(2, "4. RAG链路"),
    p("数据接入→清洗→切块→Embedding→向量召回→rerank重排→生成"),
    div(),
    h(2, "5. 短期记忆 vs 长期记忆"),
    p("短期：当前会话，上下文窗口，受限于token上限"),
    p("长期：跨会话，持久化存储，解决'下次还记得你'"),
    p("压缩触发：token接近上限 / 会话轮次太长 / 任务进入新阶段"),
    p("压缩方式：智能压缩（模型总结）+ 机械压缩（规则裁剪），生产中混合使用"),
    div(),
    h(2, "6. 多智能体模型选型"),
    p("分层使用：简单任务→小模型（快+便宜）；复杂任务→强模型（准）"),
    div(),
    h(2, "7. 熔断机制"),
    bl("最大执行步数：防止无限循环"),
    bl("单次调用超时：防止单步卡死"),
    bl("总任务超时：防止资源耗尽"),
    p("熔断后：根据错误类型处理（超时重试/权限拒绝返回/工具不存在返回）"),
    div(),
    h(2, "8. 面试速记"),
    p("MCP=工具治理层（可插拔+可治理+可扩展）"),
    p("Agent模式：ReAct/Plan/Workflow，越靠近业务越不自由"),
    p("RAG链路：接入→清洗→切块→Embedding→召回→rerank→生成"),
    p("记忆：短期=这轮别断片，长期=下次还记得你"),
    p("熔断：限制步数+超时+总时长，根据错误类型处理"),
]

r2 = requests.post(BASE+"/docx/v1/documents/"+doc_id+"/blocks/"+doc_id+"/children", headers={"Authorization": "Bearer "+token}, json={"children": blocks, "index": -1})
print("code=", r2.json().get("code"), "blocks=", len(blocks))
print("Done:", url)
