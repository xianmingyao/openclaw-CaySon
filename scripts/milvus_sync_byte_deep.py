import sys; sys.stdout.reconfigure(encoding='utf-8')
"""Sync 字节Agent面试深度分析 to Milvus using existing dual-write approach"""
import requests, time

MILVUS_HOST = "8.137.122.11"
MILVUS_PORT = 19530
MILVUS_COLLECTION = "CaySon_db"
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"
USER_ID = "ningcaison"

def get_embedding(text):
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": text}
    )
    return response.json()["embedding"]

records = [
    ("MCP适配层：统一协议解决工具调用碎片化问题，可插拔（动态注册/下线）、可治理（权限/审计/限流）、可扩展（新工具无需改核心代码）。与传统Function Calling区别：Function Calling是能力，MCP是生态。", "MCP", "面试考点"),
    ("模型写库五层校验：Schema参数校验→RBAC权限校验→本体规则引擎兜底（金额超限/客户黑名单）→高风险操作二次确认→事务控制+审计日志。AI生成意图，后端执行保障。", "模型写库", "面试考点"),
    ("RAG全链路7节点：数据接入→清洗→切块→Embedding→向量召回→Rerank→生成。切块策略选500-1000 tokens语义切块。Rerank用Cross-Encoder弥补双编码器局限，MRR@10提升20-30%。", "RAG", "面试考点"),
    ("Agent记忆系统：短期记忆用上下文压缩（机械裁剪/模型摘要/混合），触发条件token>80%上限/轮次>20/任务切换。长期记忆存Milvus向量库+Neo4j图谱，召回时语义相似度×时间衰减×重要性权重。", "记忆系统", "面试考点"),
    ("Agent熔断三层保护：max_steps=20防死循环、step_timeout=30s防单步卡死、total_timeout=300s防资源耗尽。熔断器状态机CLOSE→OPEN→HALF_OPEN连续成功恢复。错误处理：超时重试/权限拒绝返回/工具不存在返回。", "熔断机制", "面试考点"),
]

from pymilvus import MilvusClient
client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")

# 确保collection已加载
try:
    client.load_collection(MILVUS_COLLECTION)
except:
    pass

base_id = int(time.time() * 1000) % 1000000 * 100  # 制造一个基准ID

for i, (text, topic, mtype) in enumerate(records):
    try:
        embedding = get_embedding(text)
        milvus_id = base_id + i
        data = [{
            "id": milvus_id,
            "vector": embedding,
            "text": text,
            "user_id": f"{USER_ID}|douyin-byte-agent|{topic}",
        }]
        client.insert(collection_name=MILVUS_COLLECTION, data=data)
        print(f"[OK] {milvus_id}: {topic}")
    except Exception as e:
        print(f"[ERROR] {topic}: {e}")

print(f"\nDone: {len(records)} records synced")
