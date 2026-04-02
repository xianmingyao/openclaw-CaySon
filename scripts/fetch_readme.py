# -*- coding: utf-8 -*-
import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

r = requests.get("https://raw.githubusercontent.com/particlefuture/1mcpserver/main/README.md")
print(r.text)
