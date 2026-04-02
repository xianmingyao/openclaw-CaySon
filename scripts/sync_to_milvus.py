#!/usr/bin/env python3
"""同步记忆到Milvus云端"""
import warnings
warnings.filterwarnings('ignore')

from pymilvus import MilvusClient
import requests
import time

MILVUS_HOST = '8.137.122.11'
MILVUS_PORT = 19530
COLLECTION = 'CaySon_db'

print('[1] 连接Milvus...')
client = MilvusClient(uri=f'http://{MILVUS_HOST}:{MILVUS_PORT}')
print('[OK] 已连接')

print('[2] 加载Collection...')
try:
    client.load_collection(COLLECTION)
    print('[OK] Collection已加载')
except Exception as e:
    print(f'[WARN] {e}')

memories = [
    'browser-use CLI 2.0 是YC孵化的AI浏览器自动化工具，GitHub 78000+ Stars，版本0.12.5',
    'browser-use --mcp 是官方MCP服务器方案，比第三方mcp-browser-use更稳定',
    'WebMCP是Chrome官方2026年2月发布的Web标准，让网站暴露结构化工具给AI Agent',
    'browser-use CLI Windows环境需要设置 PYTHONIOENCODING=utf-8 避免UnicodeEncodeError错误',
    'agent-browser 和 browser-use CLI 互补：前者Windows友好截图精准，后者Token高效MCP原生',
    'instructkr/claw-code 是GitHub史上最快50K Stars仓库，Claude Code架构清洁室重写',
    'OpenSwarm 是多Claude Code实例编排器，适合Linear项目管理的AI开发团队',
    'sanbuphy/claude-code-source-code 是Claude Code泄露源码存档，Fork超41500，法律风险高',
]

print('[3] 开始同步记忆到云端...')
success = 0
for m in memories:
    print(f'  {m[:45]}...')
    try:
        resp = requests.post(
            'http://localhost:11434/api/embeddings',
            json={'model': 'nomic-embed-text', 'prompt': m},
            timeout=60
        )
        emb = resp.json()['embedding']
        mid = int(str(int(time.time()*1000)) + str(abs(hash(m)))[-4:])
        client.insert(COLLECTION, [{
            'id': mid,
            'vector': emb,
            'text': m,
            'user_id': 'ningcaison'
        }])
        print(f'    [OK] ID={mid}')
        success += 1
    except Exception as e:
        print(f'    [FAIL] {str(e)[:40]}')

print(f'\n[OK] 云端Milvus同步完成! 成功: {success}/{len(memories)}')
