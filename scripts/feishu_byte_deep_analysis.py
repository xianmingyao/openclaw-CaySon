import sys; sys.stdout.reconfigure(encoding='utf-8')
import requests, json

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
def code(lang, t):
    return {"block_type": 14, "code": {"elements": [{"text_run": {"content": t}}], "style": {"language": lang}}}
def bl(t):
    return {"block_type": 12, "bullet": {"elements": [{"text_run": {"content": t}}], "style": {}}}
def ordered(t):
    return {"block_type": 13, "ordered": {"elements": [{"text_run": {"content": t}}], "style": {}}}
def quote(t):
    return {"block_type": 34, "quote": {"elements": [{"text_run": {"content": t}}], "style": {}}}

blocks = [
    h(1, "字节跳动Agent面试深度分析"),
    p("来源：小哲讲面经 | https://www.douyin.com/video/7638153068667768099"),
    p("发布时间：2026-05-11 | 时长：3:12 | 3691赞"),
    p("深度关联：Ontology文档 + Workflow vs Agent融合模式"),
    div(),

    h(2, "一、MCP适配层深度分析"),
    h(3, "1.1 为什么字节必问MCP？"),
    p("MCP是2024-2025年工具调用领域的重大演进。字节作为工具平台型公司，考察MCP是在看候选人对工具治理的理解深度。"),
    div(),
    h(3, "1.2 传统Function Calling vs MCP"),
    bl("协议标准：各家私有 vs 统一协议，一次开发到处运行"),
    bl("工具发现：硬编码工具列表 vs 动态发现，工具主动注册"),
    bl("权限控制：业务代码散落 vs 协议层统一管理"),
    bl("调用审计：无标准化日志 vs 内置调用记录"),
    bl("超时治理：手动处理 vs 协议层统一处理"),
    bl("版本管理：无 vs 工具版本化，可回滚"),
    div(),
    h(3, "1.3 MCP三大特性"),
    bl("可插拔：工具随时注册/下线，Agent无需重启"),
    bl("可治理：权限/审计/限流在协议层统一管理"),
    bl("可扩展：新工具无需修改Agent核心代码"),
    div(),
    h(3, "1.4 面试回答模板"),
    quote("MCP本质上是工具调用的'USB-C接口'——把工具调用的复杂性从应用层抽离到协议层。具体解决三个问题：协议统一、治理内聚、动态治理。Function Calling是'能力'，MCP是'生态'。"),
    div(),

    h(2, "二、模型写库：工具执行的工程实践"),
    h(3, "2.1 读库 vs 写库的本质区别"),
    bl("读库：无副作用，查错最多白跑，可幂等重试"),
    bl("写库：有副作用，写错会破坏数据，需要事务控制"),
    p("AI只生成意图，人工/系统校验后执行。后端必须二次校验。"),
    div(),
    h(3, "2.2 写库五层校验架构"),
    ordered("第一层：参数Schema校验 - 类型/必填/格式"),
    ordered("第二层：业务权限校验 - RBAC：用户角色 → 工具权限矩阵"),
    ordered("第三层：业务规则校验 - 本体规则引擎兜底：金额>100万→总监审批"),
    ordered("第四层：风险确认 - 高风险操作（删除/大额/跨系统）需用户二次确认"),
    ordered("第五层：事务控制+审计日志 - 写操作必须在事务内执行"),
    div(),
    h(3, "2.3 面试回答模板"),
    quote("核心观点：AI生成意图，后端负责执行和保障。AI的强项是'想'，但'做'必须有人兜底。"),
    div(),

    h(2, "三、RAG全链路深度分析"),
    h(3, "3.1 RAG不只是向量检索：7个关键节点"),
    p("数据接入 → 数据清洗 → 文档切块 → Embedding → 向量召回 → Rerank → 生成"),
    div(),
    h(3, "3.2 文档切块策略"),
    bl("固定大小切块：简单但可能切断句子/段落语义"),
    bl("语义切块（推荐生产）：按语义段落切，保持上下文完整"),
    bl("层级切块（适合长文档）：先按章节切，再按段落切，保留文档层级结构"),
    p("chunk_size经验值：500-1000 tokens。关键不是固定值，是'保持语义完整性'。"),
    div(),
    h(3, "3.3 Rerank：最被忽略的环节"),
    bl("向量检索是双编码器：上下文融合不够"),
    bl("Rerank是Cross-Encoder：效果更准"),
    bl("工程价值：向量召回快速海选（<50ms），Rerank精挑细选（<100ms）"),
    bl("效果提升：MRR@10通常提升20-30%"),
    div(),
    h(3, "3.4 面试回答模板"),
    quote("向量召回是'广撒网'，Rerank是'精准捞'。向量相似度≠语义相关性，Cross-Encoder的Rerank能弥补双编码器的局限。"),
    div(),

    h(2, "四、记忆系统分层架构"),
    h(3, "4.1 短期记忆：上下文压缩"),
    bl("触发条件：token接近上限 / 会话轮次太多 / 任务切换"),
    bl("机械压缩：按规则裁剪，快但糙（保留首尾，删除中间重复）"),
    bl("智能压缩：让模型总结历史，准但贵且慢"),
    bl("混合压缩（生产推荐）：先用规则快速过滤，再用模型精修"),
    div(),
    h(3, "4.2 长期记忆：跨会话持久化"),
    bl("Milvus向量库：存储用户偏好/历史摘要（语义检索）"),
    bl("Neo4j图数据库：存储关系（组织架构/产业链/业务实体关系）"),
    bl("召回策略：语义相似度 × 时间衰减（指数衰减） × 重要性权重"),
    p("每次会话结束时用LLM抽取关键信息（实体/偏好/关系）存到向量库。"),
    div(),
    h(3, "4.3 面试回答模板"),
    quote("短期记忆解决'这轮别断片'，长期记忆解决'下次还认识你'。新会话开始时从长期记忆召回相关内容组装到短期记忆中，Agent既'记得过去'又'专注当下'。"),
    div(),

    h(2, "五、多智能体模型选型"),
    h(3, "5.1 分层模型选型策略"),
    bl("简单任务→小模型（gpt-4o-mini）：快+便宜"),
    bl("中等任务→中等模型（gpt-4o）：平衡"),
    bl("复杂推理→强模型（gpt-4-turbo）：准"),
    bl("创意生成→强模型（claude-3-5-sonnet）：创意能力强"),
    div(),
    h(3, "5.2 模型网关设计"),
    bl("统一入口：路由/限流/熔断/降级"),
    bl("兜底链：openai超时 → anthropic → azure → 返回降级响应"),
    div(),

    h(2, "六、熔断机制：生产级Agent必备"),
    h(3, "6.1 Agent失控的三大场景"),
    bl("无限循环：Agent反复查询工具每次都觉得信息不够"),
    bl("单步卡死：LLM API不返回（超时/网络问题）"),
    bl("资源耗尽：内存溢出/Token爆炸/费用失控"),
    div(),
    h(3, "6.2 三层熔断保护"),
    ordered("最大执行步数：max_steps=20，防止死循环"),
    ordered("单步超时：step_timeout=30秒，防止单步卡死"),
    ordered("总任务超时：total_timeout=300秒（5分钟），防止资源耗尽"),
    div(),
    h(3, "6.3 熔断器状态机"),
    bl("CLOSED（正常）：请求通过，失败计数累积"),
    bl("OPEN（熔断）：请求直接拒绝，超过恢复时间后进入HALF_OPEN"),
    bl("HALF_OPEN（探测）：放行少量请求，连续成功N次后恢复CLOSED"),
    div(),
    h(3, "6.4 错误处理策略"),
    bl("超时 → 可以重试一次，还是超时就返回降级响应"),
    bl("权限拒绝 → 返回'无权操作，请联系管理员'"),
    bl("工具不存在 → 返回'该功能暂时不可用'"),
    bl("超过最大步数 → 返回'任务过于复杂，已达到最大执行步数'"),
    div(),

    h(2, "七、综合面试题库（15道）"),
    h(3, "基础题（5道）"),
    bl("Q1: MCP和Function Calling的区别是什么？"),
    bl("Q2: RAG链路有哪些关键节点？"),
    bl("Q3: 短期记忆和长期记忆分别解决什么问题？"),
    bl("Q4: 为什么需要Rerank？直接用向量召回不行吗？"),
    bl("Q5: 什么是熔断机制？Agent需要哪些熔断？"),
    div(),
    h(3, "进阶题（5道）"),
    bl("Q6: 文档切块策略有哪些？chunk_size怎么选？"),
    bl("Q7: 模型写库需要哪些校验层？"),
    bl("Q8: 多Agent场景下模型怎么选型？"),
    bl("Q9: 上下文压缩有哪些方式？各自优缺点？"),
    bl("Q10: 模型网关需要具备哪些能力？"),
    div(),
    h(3, "高难题（5道）"),
    bl("Q11: 如何设计一个企业级的Agent系统？"),
    bl("Q12: Agent的记忆系统和Ontology是什么关系？"),
    bl("Q13: Workflow和Agent什么时候用？怎么融合？"),
    bl("Q14: 生产环境中RAG最大的坑是什么？怎么解决？"),
    bl("Q15: 如何保证Agent系统的可观测性和运维？"),
    div(),

    h(2, "八、关联知识索引"),
    bl("Ontology文档 → knowledge-base/wiki/概念/企业AI本体Ontology-从工具到Agent的关键.md"),
    bl("Workflow vs Agent → douyin-knowledge/2026-05-19-Workflow与Agent的本质区别-知识沉淀.md"),
    bl("视频来源 → https://www.douyin.com/video/7638153068667768099"),
    div(),

    h(2, "九、学习价值"),
    bl("工程价值：⭐⭐⭐⭐⭐ 覆盖RAG/Agent/熔断的生产级实践"),
    bl("面试价值：⭐⭐⭐⭐⭐ 字节/美团/快手Agent岗位高频考察点"),
    bl("知识贯通：⭐⭐⭐⭐⭐ 串联Ontology + Workflow + Agent三大概念"),
    bl("代码深度：⭐⭐⭐⭐ Python/LangChain代码示例可落地"),
    bl("实用价值：⭐⭐⭐⭐⭐ 直接用于面试准备和技术方案设计"),
    p("整理：CaySon | 2026-05-19"),
]

# 分批写入（Feishu单次最多50个block）
batch_size = 40
for i in range(0, len(blocks), batch_size):
    batch = blocks[i:i+batch_size]
    r2 = requests.post(BASE+"/docx/v1/documents/"+doc_id+"/blocks/"+doc_id+"/children",
                       headers={"Authorization": "Bearer "+token},
                       json={"children": batch, "index": -1})
    print(f"batch {i//batch_size + 1}: code={r2.json().get('code')}, blocks={len(batch)}")

print("Done:", url)
