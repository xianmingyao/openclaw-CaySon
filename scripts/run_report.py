#!/usr/bin/env python3
"""内容捕手 - 生成抓取报告"""
import re
from datetime import datetime

DATA_DIR = r"E:\workspace\content-hunter-data\data"

with open(f"{DATA_DIR}\\bilibili.md", 'r', encoding='utf-8') as f:
    b_content = f.read()
with open(f"{DATA_DIR}\\douyin.md", 'r', encoding='utf-8') as f:
    d_content = f.read()

b_old = re.findall(r'^### 第(\d+)条', b_content, re.MULTILINE)
b_new = re.findall(r'^## 第(\d+)条', b_content, re.MULTILINE)
b_bvs = re.findall(r'(BV\w{10})', b_content)

d_old = re.findall(r'^### 第(\d+)条', d_content, re.MULTILINE)
d_new = re.findall(r'^## 第(\d+)条', d_content, re.MULTILINE)
d_urls = re.findall(r'https://www\.douyin\.com/video/(\d+)', d_content)

b_old_max = max(int(x) for x in b_old) if b_old else 0
b_new_max = max(int(x) for x in b_new) if b_new else 0
d_old_max = max(int(x) for x in d_old) if d_old else 0

report = f"""内容捕手抓取报告 {datetime.now().strftime('%Y-%m-%d %H:%M')}

B站（bilibili.md）
  历史条目: {len(b_old)} 条 (编号001-{b_old_max})
  本次新增: {len(b_new)} 条 (编号{b_new_max - len(b_new) + 1}-{b_new_max})
  唯一BV号: {len(set(b_bvs))} 个
  数据来源: B站科技分区API(rid=36) + AI关键词搜索
  状态: [OK] 成功

抖音（douyin.md）
  现有条目: {len(d_old)} 条 (编号001-{d_old_max})
  本次新增: {len(d_new)} 条
  唯一视频URL: {len(set(d_urls))} 个
  数据来源: 早期批次(14:00)
  状态: [WARN] API和浏览器均被反爬拦截，无法新增

总结
  B站: +{len(b_new)}条，唯一视频{len(set(b_bvs))}个
  抖音: +0条(被反爬拦截)，现有{d_old_max}条
  抖音反爬: 搜索API返回空，浏览器触发验证码，HTML由JS渲染
  建议: 抖音需要手机APP或手动登录后抓取
"""

with open(f"{DATA_DIR}\\crawl-report-{datetime.now().strftime('%Y%m%d-%H%M')}.md", 'w', encoding='utf-8') as f:
    f.write(report)

print("报告已保存")
print(f"B站: {len(b_new)}条新增，总{len(set(b_bvs))}个唯一BV")
print(f"抖音: {len(d_old)}条现有，新增0条(反爬拦截)")
