import os

log_path = r"E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\artifacts\manual\logs\skill_run.log"
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8') as f:
        content = f.read()
    print(content[-8000:])  # last 8000 chars
else:
    print(f"File not found: {log_path}")
