#!/usr/bin/env python3
"""同步GitHub AI Skills榜单到Milvus"""
import requests
from pymilvus import MilvusClient

OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"

def get_embedding(text):
    resp = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": text[:8000]},
        timeout=30
    )
    return resp.json()["embedding"]

# 连接Milvus
client = MilvusClient(uri="http://8.137.122.11:19530", token="root:Milvus2025")
collection = "CaySon_db"

# 内容分段
sections = [
    ("GitHub AI Skills榜单第3集", "本周变化：hermes agent成为最大黑马冲到第二名，financial services和deepseatrade新晋上榜，三个老面孔告别榜单。排名：1.skills(mattpocock)8.5万Stars实用工程师技能 2.hermes agent15.2万Stars与用户一同成长的智能体 3.andrej karpathy skills13.1万Stars改善Cloud Code表现 5.deepseatrade3.0万Stars终端运行DeepSEA模型编码智能体 6.c switch7.2万Stars多模型跨平台桌面一体化助手 7.agent skills4.2万Stars AI编码生产级工程技能 8.openyou9.1万Stars私人AI超级智能 9.agentmary9.7万Stars最佳持久内存 10.helloagents5.0万Stars智能体原理与实践"),
    ("OpenHuman强势登顶三大顶流对比", "龙虾和爱马仕都不香了，OpenHuman强势登顶，三大顶流Agent终极对比。痛点：OpenClaw(龙虾)依赖交互记忆有冷启动难题，HermesAgent(爱马仕)需要教才能了解用户，OpenHuman打破冷启动无需教即可了解一切。OpenHuman三步原理：一键连接、20分钟无感抓取、生成记忆树。选型：OpenClaw适合跨平台执行网关，HermesAgent适合自我成长型员工，OpenHuman适合贴身助理。"),
    ("OpenHuman三大创新机制", "1.TokenJuice机制：减少Token消耗，记住高达10亿Token信息。2.潜意识循环：Agent可自主决定待办事项，化身虚拟形象加入线上会议。结语：Agent发展方向等于执行力加学习力加记忆力。Skills系统核心价值：工程实践技能包告别vibe coding，用工程思维驾驭AI编程。典型代表mattpocock/skills(91.8k Stars)。"),
    ("GitHub链接参考", "主要GitHub项目链接：mattpocock/skills(91.8k) https://github.com/mattpocock/skills、anthropics/financial-services(25.3k) https://github.com/anthropics/financial-services、bytedance/UI-TARS-desktop(34.6k) https://github.com/bytedance/UI-TARS-desktop、CloakHQ/CloakBrowser(15.2k) https://github.com/CloakHQ/CloakBrowser、rohitg00/agentmemory(12.8k) https://github.com/rohitg00/agentmemory、Imbad0202/academic-research-skills(11.7k) https://github.com/Imbad0202/academic-research-skills。"),
]

print(f"Embedding {len(sections)} sections...")
vectors = [get_embedding(s[1]) for s in sections]
print(f"Got {len(vectors)} vectors, dim={len(vectors[0]) if vectors else 0}")

print("Inserting to Milvus...")
for i, (title, content) in enumerate(sections):
    rec_id = 2026051900 + i
    text_field = f"{title}：{content}"[:4000]
    client.insert(
        collection_name=collection,
        data=[{
            "id": rec_id,
            "text": text_field,
            "user_id": "cayson",
            "vector": vectors[i]
        }]
    )
    print(f"  Inserted id={rec_id} ({title})")

print(f"\n✅ Done! {len(sections)} sections synced to Milvus")
