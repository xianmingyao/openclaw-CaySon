import requests
import json

api_key = '265454fb9c21c51b86f3201bf6a0c52a0082fbb7c12c5cdb'
base_url = 'http://127.0.0.1:50325'

headers = {
    'Content-Type': 'application/json',
    'api-key': api_key
}

# 获取所有账号（多页）
accounts = []
for page in range(1, 10):
    resp = requests.get(
        base_url + '/api/v1/user/list',
        params={'page': page, 'page_size': 100},
        headers=headers,
        timeout=10
    )
    data = resp.json()
    page_accounts = data.get('data', {}).get('list', [])
    if not page_accounts:
        break
    accounts.extend(page_accounts)
    print(f'第{page}页: 获取 {len(page_accounts)} 个账号')

print(f'\n总账号数: {len(accounts)}')

# 找 Browser ID 83 或昵称 @Auto416
found = False
for acc in accounts:
    serial = acc.get('serial_number', '')
    name = acc.get('name', '')
    user_id = acc.get('user_id', '')
    if '83' in str(serial) or 'Auto416' in name or 'suduehdakis5' in name:
        print(f'\n找到目标账号:')
        print(json.dumps(acc, indent=2, ensure_ascii=False))
        found = True
        break

# 打印所有账号
print(f'\n所有 {len(accounts)} 个账号:')
for acc in accounts:
    sn = acc.get('serial_number', '')
    name = acc.get('name', '')
    user_id = acc.get('user_id', '')
    print(f"  [{sn}] {name} (user_id: {user_id})")
