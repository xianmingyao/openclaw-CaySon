"""
上传AI热点速递到Milvus云端
"""
import sys
sys.path.insert(0, 'E:/workspace/scripts')

from mem0_dual_write import init_mem0, init_milvus, add_memory

memory_client = init_mem0()
milvus_client = init_milvus()

# AI热点速递内容
memories = [
    "2026-04-15 AI热点速递：MiniMax Agent上线Pocket+Computer Use，四工具域（Desktop/WM/Browser/Clipboard），60+工具，截图-验证-行动循环",
    "2026-04-15 面壁智能推出Lantay类Cursor文档智能体工作台",
    "2026-04-15 谷歌DeepMind设立AI哲学家岗位，人选Henry Shevlin，研究机器意识/人机关系/AGI准备度",
    "2026-04-15 智在无界发布Being-H0.7最强具身世界模型，20万小时人类视频预训练，屠榜6大国际评测",
    "2026-04-15 OpenAI内部备忘录炮轰Anthropic：批评恐惧叙事+营收注水80亿美元，战略从卖模型转型平台生态"
]

print(f"开始上传 {len(memories)} 条AI热点到Milvus...")

for i, text in enumerate(memories, 1):
    result = add_memory(memory_client, milvus_client, text)
    print(f"{i}. ✅ {result}")

print(f"\n✅ 成功上传 {len(memories)} 条AI热点到云端Milvus！")
