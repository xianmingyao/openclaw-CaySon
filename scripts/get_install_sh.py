#!/usr/bin/env python3
import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

r = requests.get('https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/install.sh', timeout=15)
print(r.text)
