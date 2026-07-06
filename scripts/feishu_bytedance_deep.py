import sys; sys.stdout.reconfigure(encoding='utf-8')
import requests

APP_ID = "cli_a9324982073a1bc8"
APP_SECRET = "2tOQnQmwk2bHOUAHPsHCjfcv4zLreFWE"
BASE = "https://open.feishu.cn/open-apis"

token = requests.post(BASE+"/auth/v3/tenant_access_token/internal", json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()["tenant_access_token"]
title = "字节Agent面试深度分析 MCP RAG 熔断 2026-05-19"
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
def bl(t):
    return {"block_type": 12, "bullet": {"elements": [{"text_run": {"content": t}}], "style": {}}}

blocks = [
    h(1, "字节Agent面试深度分析"),
    p("来源：小哲讲面经 | 2026-05-11 | 3691赞 | 深度分析版"),
    div(),
    h(2, "面试考察全景"),
    p("底层能力：MCP适配层、工具协议、权限审计"),
    p("中层能力：Agent工作模式、RAG链路、记忆系统"),
    p("高层能力：多智能体编排、熔断降级、模型网关"),
    div(),
    h(2, "1. MCP适配层"),
    bl("MCP vs 传统工具调用：统一协议、动态发现、权限管控"),
    bl("核心价值：工具可插拔、可治理、可扩展"),
    bl("关联：MCP是工具层面的Ontology"),
    div(),
    h(2, "2. 模型写库 vs 读库"),
    bl("写库：模型生成意图+参数，后端校验+权限+事务+审计"),
    bl("读库：RAG向量召回+rerank+生成"),
    p("关键：模型只负责生成，后端必须完整校验"),
    div(),
    h(2, "3. Agent工作模式"),
    bl("ReAct：推理+执行交替，适合复杂推理"),
    bl("Plan+Execute：计划与执行分离"),
    bl("Workflow：固定流程，越靠近业务越不自由"),
    div(),
    h(2, "4. RAG全链路"),
    p("接入→清洗→切块→Embedding→向量召回→rerank→生成"),
    bl("切片策略：固定大小/语义/重叠"),
    bl("rerank重排：精排模型提升召回质量"),
    div(),
    h(2, "5. 记忆系统"),
    bl("短期记忆：当前会话，上下文窗口，受token限制"),
    bl("长期记忆：跨会话，持久化，解决'下次还记得你'"),
    bl("压缩：智能压缩（模型总结）+ 机械压缩（规则裁剪），生产混合用"),
    div(),
    h(2, "6. 多智能体模型选型"),
    p("分层：简单任务用小模型（快+便宜）；复杂任务用强模型（准）"),
    div(),
    h(2, "7. 熔断机制"),
    bl("三要素：最大步数 / 单次超时 / 总任务超时"),
    bl("错误处理：超时重试 / 权限拒绝 / 工具不存在 / 业务异常"),
    p("核心：防止Agent无限循环、资源耗尽"),
    div(),
    h(2, "8. 工程实现关键"),
    bl("MCP注册发现：工具版本化、可回滚、优雅下线"),
    bl("熔断参数：max_steps=10, timeout=30s, total_timeout=300s"),
    bl("RAG坑点：切片大小、召回阈值、rerank模型选择"),
    bl("记忆持久化：向量数据库存储+相似度检索"),
    div(),
    h(2, "9. 关联已有知识库"),
    bl("→ Ontology：MCP=工具层Ontology；熔断=规则引擎兜底"),
    bl("→ 江哥第74集：融合模式Workflow+Agent，LangGraph实现"),
    bl("→ 企业AI七层架构：MCP对应服务层，熔断对应规则层"),
    div(),
    h(2, "10. 面试速记"),
    p("MCP=统一工具协议（可插拔+可治理+可扩展）"),
    p("Agent模式：ReAct/Plan/Workflow，越靠近业务越不自由"),
    p("RAG链路：接入→清洗→切块→Embedding→召回→rerank→生成"),
    p("记忆：短期=这轮别断片，长期=下次还记得你"),
    p("熔断：限制步数+超时+总时长，根据错误类型处理"),
]

r2 = requests.post(BASE+"/docx/v1/documents/"+doc_id+"/blocks/"+doc_id+"/children", headers={"Authorization": "Bearer "+token}, json={"children": blocks, "index": -1})
print("code=", r2.json().get("code"), "blocks=", len(blocks))
print("Done:", url)
