#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""追加DD讲AI内容到企业AI本体Ontology文件"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'E:\workspace\knowledge-base\wiki\概念\企业AI本体Ontology-从工具到Agent的关键.md'

with open(filepath, encoding='utf-8') as f:
    content = f.read()

old_text = '最后更新：2026-05-12（已追加"企业AI本体化闭环流程"内容，并完成乱码清理）'
old_text_match = None
for line in content.split('\n'):
    if '企业AI本体化闭环流程' in line and '最后更新' in line:
        old_text_match = line.strip()
        break
if old_text_match:
    old_text = old_text_match
    print(f'找到目标行: {old_text[:80]}')

new_section = '''*最后更新：2026-05-14（已整合DD讲AI五步法与企业AI本体映射）*

---

## 12. 📺 DD讲AI五步法与企业AI本体的深度整合

> 来源：抖音 @DD讲AI《现在大厂AI落地的思路，一共五个关键环节》
> 链接：https://www.douyin.com/video/7639407124979764480
> 发布：2026-05-14 | 数据：292👍 247收藏 54转发

### 12.1 DD讲AI五步法 vs 企业AI本体阶段 映射表

| DD讲AI五步 | 对应企业AI本体阶段 | 核心内容 |
|-----------|-----------------|---------|
| 第1步：AI落地基建 | 数字化基础设施层 | 算力/云服务/开发环境 |
| 第2步：招聘关键角色 | 本体团队组建 | 必须有开发，业务+AI双懂 |
| 第3步：业务流程梳理 | 本体建模(TBox+ABox) | 知识梳理脱层皮，最费力 |
| 第4步：AI复利在哪里 | Agent价值场景选择 | 高频×上下文积累×自动化 |
| 第5步：AI技术方案选择 | Agent框架+工具封装 | 前几步ready后，技术选型容易 |

### 12.2 核心观点与本体印证

#### 观点1："必须有开发，无可替代"
- AI落地不是买工具，是建能力
- 外部工具只能解决单点，无法形成业务闭环
- 本体团队（含开发能力）是企业AI核心资产

#### 观点2："知识和业务梳理脱了层皮"
- 对应本体的业务调研+本体建模阶段
- 服务体验边界复杂、动态 → 需要状态机建模
- 业务梳理清楚后，技术方案选择变得容易

#### 观点3："AI复利在哪里"
复利效应 = 高频场景 × 可积累的上下文 × 自动化执行

**复利高场景**：客服/报价/审批/预警/报表
**复利低场景**：一次性分析/复杂决策/创意任务

### 12.3 企业AI落地自测：你卡在哪一步？

| 卡住步骤 | 症状 | 解决 |
|---------|------|------|
| 第1步 | 还在用Excel，数据散乱 | 先上飞书/钉钉，数字化先行 |
| 第2步 | 买了工具没人用 | 招聘或培养懂业务又懂AI的人 |
| 第3步 | 说不清业务逻辑，需求反复 | 用本体建模方法，邀业务方参与 |
| 第4步 | 做了很多AI，看不出明显价值 | 用复利公式筛选 |
| 第5步 | 上了Agent系统，效果不稳定 | 第3步做扎实后，技术方案自然清晰 |

### 12.4 与本文"企业落地五步循环"的关系

本文原有的"企业Agent落地五步循环"与DD讲AI五步法的侧重点差异：

| 本文五步循环 | DD讲AI五步法 | 差异 |
|------------|-------------|-----|
| 场景选择 | AI落地基建 | 本文偏业务痛点，DD偏基础设施 |
| 本体建模 | 业务流程梳理 | 基本一致 |
| 工具封装 | 招聘关键角色 | DD强调人，本文强调工具 |
| 兜底规则 | AI技术方案选择 | DD强调选型后执行 |
| 运营迭代 | AI复利在哪里 | DD的复利=持续验证价值 |

**融合**：DD讲AI的第2步（招聘关键角色）应穿插整个流程，每个步骤都需要有开发能力的人参与。

*最后更新：2026-05-14（已整合DD讲AI五步法）*
'''

if old_text in content:
    new_content = content.replace(old_text, new_section)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('SUCCESS: 文件已更新')
else:
    print('WARNING: 未找到目标文本')
    # 尝试找最后一个包含"最后更新"的行
    for i, line in enumerate(content.split('\n')):
        if '最后更新' in line:
            print(f'  第{i+1}行: {line[:80]}')
