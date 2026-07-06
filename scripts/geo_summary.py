"""Quick summary of all audit JSONs"""
import json, os

files = [
    r'E:\workspace\geo_audit_services.json',
    r'E:\workspace\geo_audit_services_admin.json',
    r'E:\workspace\geo_audit_services_client.json',
    r'E:\workspace\geo_audit_db_schema.json',
    r'E:\workspace\geo_audit_frontend.json',
]

for f in files:
    if not os.path.exists(f):
        print(f'--- MISSING: {f} ---')
        continue
    print(f'=== {os.path.basename(f)} ===')
    with open(f, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    print(f'  Top keys: {list(data.keys())}')
    for k, v in data.items():
        if isinstance(v, list):
            print(f'  {k}: {len(v)} items')
        elif isinstance(v, dict):
            print(f'  {k}: dict with {len(v)} keys')
    print()
