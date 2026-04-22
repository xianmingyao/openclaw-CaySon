#!/usr/bin/env python3
"""同步CLAUDE.md v1.1 (Harness章节) 到Milvus"""
import warnings
warnings.filterwarnings('ignore')

from pymilvus import MilvusClient
import requests
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

MILVUS_HOST = '8.137.122.11'
MILVUS_PORT = 19530
COLLECTION = 'CaySon_db'
OLLAMA_URL = 'http://localhost:11434'
EMBEDDING_MODEL = 'nomic-embed-text'
USER_ID = 'ningcaison'

print('[1] 连接Milvus...')
client = MilvusClient(uri=f'http://{MILVUS_HOST}:{MILVUS_PORT}')

print('[2] 加载Collection...')
try:
    client.load_collection(COLLECTION)
except:
    pass

# CLAUDE.md v1.1 新增的 Harness Engineering 核心要点
memories = [
    # 8. Harness Engineering 需求分析
    'CLAUDE.md v1.1 新增章节：Harness Engineering需求分析规范 - 来源抖音@MrMaMaker + Practical-Guide-to-Context-Engineering',
    
    'Harness Engineering三板斧：架构约束(要求写清楚规则写细致) + 环境闭环(每阶段审核未通过重新生成) + 知识治理(每阶段只参考上一阶段产物)',
    
    'Harness Engineering核心思维：不是束缚Agent，而是给它建造工作空间 - 定义边界和协作协议，而不是控制每一步执行',
    
    'Harness Engineering vs 束缚：束缚=控制每步执行让Agent沿骨架走，Harness=定义边界让Agent在空间内自由发挥+运行空间随模型升级变化',
    
    '多阶段任务执行模板：[阶段N]→审核→通过?→是→[阶段N+1]，否则→[根据审核结果重新生成]→[审核]',
    
    '快速审核清单四问：完整性(覆盖所有需求点?) + 一致性(与上一阶段无冲突?) + 可执行性(技术能实现?) + 可测试性(能写验收测试?)',
    
    'Harness Engineering本质：不是在限制模型能做什么，而是在创造条件让模型能做到原本做不到的事',
    
    '需求文档最低要求：背景(为什么) + 目标(解决什么) + 范围(做什么不做什么) + 功能点+验收标准 + 非功能需求',
]

print(f'[3] 开始同步CLAUDE.md v1.1 Harness章节 ({len(memories)}条)...')
success = 0
for i, m in enumerate(memories):
    print(f'  [{i}] {m[:50]}...')
    try:
        resp = requests.post(
            f'{OLLAMA_URL}/api/embeddings',
            json={'model': EMBEDDING_MODEL, 'prompt': m},
            timeout=60
        )
        emb = resp.json()['embedding']
        mid = int(str(int(time.time()*1000)) + str(abs(hash(m)))[-4:])
        client.insert(COLLECTION, [{
            'id': mid,
            'vector': emb,
            'text': m,
            'user_id': USER_ID
        }])
        print(f'    [OK] ID={mid}')
        success += 1
    except Exception as e:
        print(f'    [FAIL] {str(e)[:60]}')
    time.sleep(0.3)

print(f'\n[OK] 云端Milvus同步完成! 成功: {success}/{len(memories)}')
