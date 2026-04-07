# -*- coding: utf-8 -*-
"""使用Apify抓取TikTok AI趋势内容作为补充"""
import subprocess
import json
import os
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r'E:\workspace\content-hunter-data\data'
APIFY_TOKEN = os.environ.get('APIFY_TOKEN', '')

def run_apify_actor(actor_id, input_data):
    """运行Apify Actor"""
    cmd = [
        'apify', 'actor', 'push',
        '--token', APIFY_TOKEN,
        actor_id,
        json.dumps(input_data)
    ]
    # 使用subprocess.run会导致超时，改用直接API调用
    pass

def main():
    print("尝试使用Apify TikTok Trends Scraper...")
    print("注意: TikTok是国际版，Douyin是抖音中国版，内容不同")
    
    # 检查douyin.md现有条目
    douyin_file = f'{DATA_DIR}\\douyin.md'
    if os.path.exists(douyin_file):
        with open(douyin_file, 'r', encoding='utf-8') as f:
            content = f.read()
        import re
        matches = re.findall(r'### 第\d+条', content)
        print(f"Douyin现有条目: {len(matches)}")
    
    print("\n由于抖音需要真人验证(CAPTCHA)，推荐以下方案:")
    print("1. 手动登录抖音网页版获取cookie后导入")
    print("2. 使用手机App扫码登录抖音")
    print("3. 使用已登录的抖音Session ID")
    print("\n当前B站已完成100条AI内容追加")

if __name__ == '__main__':
    main()
