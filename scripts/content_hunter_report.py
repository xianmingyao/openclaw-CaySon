#!/usr/bin/env python3
"""内容捕手 - 生成抓取报告"""
import re
from datetime import datetime

DATA_DIR = r"C:\Users\Administrator\.openclaw\workspace\content-hunter\data"

def count_file(filepath, old_pattern, new_pattern):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    old = re.findall(old_pattern, content, re.MULTILINE)
    new = re.findall(new_pattern, content, re.MULTILINE)
    bvs = re.findall(r'(BV\w{10})', content)
    urls = re.findall(r'https://www\.douyin\.com/video/(\d+)', content)
    old_max = max(int(x) for x in old) if old else 0
    new_max = max(int(x) for x in new) if new else 0
    return {
        'old_items': len(old),
        'new_items': len(new),
        'old_max': old_max,
        'new_max': new_max,
        'total': len(set(bvs)) + len(set(urls)),
        'unique_bv': len(set(bvs)),
        'unique_dy': len(set(urls)),
    }

b_info = count_file(
    f"{DATA_DIR}\\bilibili.md",
    r'^### 第(\d+)条',
    r'^## 第(\d+)条'
)
d_info = count_file(
    f"{DATA_DIR}\\douyin.md",
    r'^### 第(\d+)条',
    r'^## 第(\d+)条'
)

report = f"""# 内容捕手抓取报告

**抓取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**任务**: 每平台100条AI技术热门内容（追加模式）

---

## B站（哔哩哔哩）

| 指标 | 数值 |
|------|------|
| 历史条目 | {b_info['old_items']} 条 |
| 本次新增 | {b_info['new_items']} 条 |
| 本次编号范围 | {b_info['new_max'] - b_info['new_items'] + 1} ~ {b_info['new_max']} |
| 唯一BV号 | {b_info['unique_bv']} 个 |

**数据来源**: B站科技数码分区排行榜API (rid=36) + AI关键词搜索
**状态**: ✅ 成功

---

## 抖音

| 指标 | 数值 |
|------|------|
| 现有条目 | {d_info['old_items']} 条 |
| 本次新增 | {d_info['new_items']} 条 |
| 唯一视频URL | {d_info['unique_dy']} 个 |

**数据来源**: 早期浏览器抓取（14:00批次）
**状态**: ⚠️ API + 浏览器均被反爬拦截

### 抖音反爬说明
1. **搜索API** (`aweme/v1/web/search/item/`): HTTP 200 但返回空数据
2. **浏览器访问**: 触发滑块验证码 (iframe captcha)
3. **直接HTML抓取**: 内容由JS渲染，HTML中无视频数据
4. **话题/标签页**: 同样被重定向或触发验证

---

## 总结

- B站: ✅ 本次新增 {b_info['new_items']} 条，总计 {b_info['unique_bv']} 个唯一视频
- 抖音: ⚠️ 无法新增，现有 {d_info['old_items']} 条来自早期批次

**建议**: 抖音需要手动操作登录或使用手机APP抓取，PC网页反爬极严
"""

print(report)
