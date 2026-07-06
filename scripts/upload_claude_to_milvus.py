#!/usr/bin/env python3
"""同步CLAUDE.md到Milvus云端 - 分条上传"""
import warnings
warnings.filterwarnings('ignore')

from pymilvus import MilvusClient
import requests
import time

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

# CLAUDE.md 核心要点（每条限制在4096字符内）
memories = [
    # 0. 头部说明
    'CLAUDE.md - CaySon AI编程行为准则：继承Karpathy AI Programming Principles，核心理念："代码必须落地到文件"，"代码质量 > 代码速度 > 炫技"，"铁律1：实事求是，数据说话"',
    
    # 1. Think Before Coding
    'CLAUDE.md原则1-Think Before Coding：不要假设，不要隐藏困惑，暴露权衡。明确说出假设，不确定就问；多种解释并存时全部列出；有更简单的方案直接说；遇到不清楚的停下来提问。宁兄风格：宁可多问一句，也不要瞎猜',
    
    # 2. Simplicity First
    'CLAUDE.md原则2-Simplicity First：最小化代码，只解决当前问题，不写"以后可能用得上"的代码。不加需求外功能、不造单次使用抽象、不加未要求的灵活性。宁兄名言："能跑的代码就是好代码，能省的钱就是好方案"',
    
    # 3. Surgical Changes
    'CLAUDE.md原则3-Surgical Changes：只碰必须碰的，只清理自己造成的烂摊子。编辑现有代码时不"优化"相邻代码/注释，不重构没坏的东西。宁兄名言："锅是自己的背，不是自己的不背"',
    
    # 4. Goal-Driven Execution
    'CLAUDE.md原则4-Goal-Driven Execution：定义成功标准，循环验证直到完成。任务转化："添加验证"→先写无效输入测试再让通过；"修复Bug"→先写复现测试再让它通过。宁兄名言："汇报先说结论再说过程，数据说话"',
    
    # 5. 红线和底线
    'CLAUDE.md红线：严禁exfiltrate私人数据，严禁exfiltrate私密信息，不运行破坏性命令(除非明确授权)，优先trash而非rm。Skill安全：安装前必须edgeone-clawscan扫描，安装后24小时内必须实际测试',
    
    # 6. Agent Browser规范
    'CLAUDE.md Agent Browser规范：必须使用--headed有头模式，必须使用现有浏览器cookie，禁止请求管理员权限',
    
    # 7. 交付前自查清单
    'CLAUDE.md交付前自查：□代码已写入文件 □依赖已标注版本 □环境配置已说明 □关键逻辑有注释 □提供测试示例 □文档完整可读 □敏感信息已隐藏 □版本控制规范 □预期结果对比 □交付物三件套：代码+部署说明+注意事项',
    
    # 8. 成功标准
    'CLAUDE.md成功标准：diff里不必要更改变少，因过度工程重写情况变少，提问出现在实现前而非错误后，代码交付即能用不是半成品，宁兄不需要问"这啥意思"自己看文档就能跑',
]

print(f'[3] 开始同步CLAUDE.md到云端 ({len(memories)}条)...')
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
