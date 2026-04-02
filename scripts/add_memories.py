#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速添加记忆到双写系统
"""
import sys
sys.path.insert(0, 'E:/workspace/scripts')

from mem0_dual_write import init_mem0, init_milvus, add_memory
import warnings
warnings.filterwarnings("ignore")

def main():
    print("初始化客户端...")
    memory_client = init_mem0()
    milvus_client = init_milvus()

    memories = [
        "browser-use CLI 2.0 是YC孵化的AI浏览器自动化工具，GitHub 78000+ Stars，版本0.12.5，Token效率比Playwright高2倍",
        "browser-use --mcp 是官方MCP服务器方案，比第三方mcp-browser-use更稳定，browser-use extract命令暂未实现",
        "WebMCP是Chrome官方2026年2月发布的Web标准，让网站暴露结构化工具给AI Agent，可节省89% tokens",
        "browser-use CLI Windows环境需要设置 PYTHONIOENCODING=utf-8 避免UnicodeEncodeError错误",
        "agent-browser 和 browser-use CLI 互补：前者Windows友好截图精准，后者Token高效MCP原生支持",
        "mcp-browser-use 0.1.5 与 browser-use 0.12.5 存在API不兼容问题，建议使用官方browser-use --mcp",
        "WebMCP两种API模式：声明式（HTML属性）和命令式（JavaScript），Chrome 146+ Canary已支持",
    ]

    for m in memories:
        add_memory(memory_client, milvus_client, m)
        print("-" * 50)

    print("\n✅ 全部记忆添加完成!")

if __name__ == "__main__":
    main()
