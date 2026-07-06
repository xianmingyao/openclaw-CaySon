"""统计 audit 数据"""
import json

with open(r'E:\workspace\geo_audit_services_admin.json', 'r', encoding='utf-8') as f:
    admin_services = json.load(f)
with open(r'E:\workspace\geo_audit_db_schema.json', 'r', encoding='utf-8') as f:
    db_schema = json.load(f)

print('=== admin_services ===')
print(f'  scanned_files: {len(admin_services["scanned_files"])}')
print(f'  function_issues: {len(admin_services["function_issues"])}')
total = sum(len(fi['issues']) for fi in admin_services['function_issues'])
print(f'  total_issues: {total}')
sev_count = {}
for fi in admin_services['function_issues']:
    for issue in fi['issues']:
        s = issue.get('severity', '?')
        sev_count[s] = sev_count.get(s, 0) + 1
print(f'  severity: {sev_count}')

print()
print('=== db_schema ===')
print(f'  migration_issues: {len(db_schema["migration_issues"])}')
print(f'  recommendations: {len(db_schema["recommendations"])}')
print(f'  total_issues: {db_schema["statistics"]["total_issues"]}')
print(f'  by_severity: {db_schema["statistics"]["by_severity"]}')
