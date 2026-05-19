import json, requests, sys
sys.stdout.reconfigure(encoding='utf-8')
APP_ID = "cli_a9324982073a1bc8"
APP_SECRET = "2tOQnQmwk2bHOUAHPsHCjfcv4zLreFWE"
BASE = "https://open.feishu.cn/open-apis"
token = requests.post(BASE+"/auth/v3/tenant_access_token/internal", json={"app_id": APP_ID, "app_secret": APP_SECRET}).json()["tenant_access_token"]
title = "Workflow Agent Process Control 2026-05-19"
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
    h(1, "Workflow Agent Process Control"),
    p("Source: Douyin Jiangge #74 | 2026-05-18"),
    div(),
    h(2, "1. Core: Process Control Rights"),
    bl("Workflow: Human defines process, AI executes"),
    bl("Agent: AI defines process, AI executes"),
    bl("They are complementary, not competing"),
    div(),
    h(2, "2. Why Hybrid Mode is Needed"),
    bl("Pure Workflow: Cannot handle business exceptions"),
    bl("Pure Agent: Unpredictable paths, cannot guarantee rigid rules"),
    bl("Hybrid: Big process=Workflow (stable), Key decisions=Agent (intelligent)"),
    div(),
    h(2, "3. LangGraph: Hybrid Engineering"),
    code("graph = StateGraph(OrderState)"),
    code("graph.add_node('validate', workflow_fn)  # Fixed flow"),
    code("graph.add_node('calculate', agent_fn)    # AI decides"),
    div(),
    h(2, "4. Ontology Rule Safety Net"),
    code("RULE ApprovalRequired:"),
    code("    IF Order.amount > 1000000"),
    code("    THEN Order.needs_approval = True"),
    bl("Both Workflow and Agent must pass this check"),
    div(),
    h(2, "5. In 7-Layer Architecture (Episode 67)"),
    bl("Layer 6 Orchestration: Hybrid core"),
    bl("Layer 4 Rules: Ontology rigid constraints"),
    bl("Layer 3 Data: Ontology-based queries"),
    div(),
    h(2, "6. Summary"),
    p("Workflow = Human defines + AI executes"),
    p("Agent = AI defines + AI executes"),
    p("Enterprise AI = Workflow(stable) + Agent(intelligent) + Ontology(safe)"),
]
r2 = requests.post(BASE+"/docx/v1/documents/"+doc_id+"/blocks/"+doc_id+"/children", headers={"Authorization": "Bearer "+token}, json={"children": blocks, "index": -1})
print("code=", r2.json().get("code"), "blocks=", len(blocks))
print("URL:", url)
