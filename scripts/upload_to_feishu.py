#!/usr/bin/env python3
"""快速上传文档到飞书"""
import asyncio
import sys
import os

# 添加skill路径
sys.path.insert(0, r'E:\workspace\skills\feishu-smart-doc-writer')

from feishu_smart_doc_writer import FeishuDocWriter, ChunkConfig

# 读取文档内容
doc_path = r'E:\workspace\knowledge\千问创享日参会准备清单-2026-04-28.md'
with open(doc_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 读取配置获取openid
config_path = r'E:\workspace\skills\feishu-smart-doc-writer\user_config.json'
import json
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
owner_openid = config.get('owner_openid', '')

async def main():
    title = '千问创享日参会准备清单-2026-04-28'
    chunk_config = ChunkConfig(show_progress=True)
    writer = FeishuDocWriter(None, chunk_config)
    
    try:
        result = await writer.write_document_with_transfer(
            title=title,
            content=content,
            owner_openid=owner_openid
        )
        print(f"\n{'='*50}")
        print(f"✅ 文档创建成功!")
        print(f"📄 标题: {title}")
        print(f"🔗 链接: {result['doc_url']}")
        print(f"📦 分块数: {result['chunks_count']}")
        print(f"👤 所有权转移: {'是' if result['owner_transferred'] else '否'}")
        print(f"{'='*50}")
    except Exception as e:
        print(f"❌ 创建失败: {e}")

if __name__ == '__main__':
    asyncio.run(main())
