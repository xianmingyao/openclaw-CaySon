#!/usr/bin/env python3
"""测试 feishu-smart-doc-writer 技能的简单脚本"""

import asyncio
import sys
import os

# 添加技能路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'skills', 'feishu-smart-doc-writer'))

# 加载配置
from __init__ import UserConfig
config = UserConfig.load()
print(f"当前配置:")
print(f"  OpenID: {config.owner_openid}")
print(f"  首次使用: {config.first_time}")
print(f"  权限已确认: {config.permission_noted}")

# 检查配置是否完整
if config.first_time or not config.owner_openid:
    print("\n⚠️ 未完成首次配置！")
    print("请先配置 OpenID：")
    print("  /feishu-smart-doc-writer configure openid=ou_你的OpenID permission_checked=true")
    sys.exit(1)

print("\n✅ 配置完整，可以创建文档")
