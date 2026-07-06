import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 搜索 Harness Engineering 相关
r = requests.get('https://api.github.com/search/repositories?q=Harness+Engineering+Agent&sort=stars&per_page=10', headers={'User-Agent': 'Mozilla/5.0'})
data = r.json()
print('Total Harness Engineering repos:', data.get('total_count', 0))
for item in data.get('items', [])[:5]:
    print('  ' + item['full_name'] + ': ' + str(item['stargazers_count']) + ' stars')
    desc = item.get('description') or 'N/A'
    print('    ' + desc)
