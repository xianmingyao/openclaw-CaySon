# 🏥 OpenClaw 安全体检报告（第2次 - 12:45）

📅 2026-05-21 12:45 (Asia/Shanghai)
🖥️ OpenClaw 2026.5.19 · Node v22.22.1 · Windows_NT 10.0.22631
📦 综合评分：82/100

## 主要发现

| 检查项 | 状态 | 详情 |
|--------|------|------|
| **配置审计** | ⚠️ 风险 | 5项配置建议（Gateway超时、插件版本未固定、elevated tools、browser control） |
| **Skill 风险** | ⚠️ 需关注 | 113个技能中1个需关注（apify-ultimate-scraper potential-exfiltration） |
| **版本漏洞** | ✅ 无 | OpenClaw 2026.5.19 无已知漏洞 |
| **隐私泄露风险** | ⚠️ 需关注 | elevated tools + browser control + 飞书文档权限 |
| **SkillHub 更新** | ✅ 无 | 18个技能检查，0个更新 |

## 关键告警

1. **apify-ultimate-scraper**: `reference/scripts/run_actor.js:353` 检测到文件读取+网络发送组合，需关注后续版本
2. **3个插件版本未固定**: acpx / feishu / openclaw-weixin
3. **elevated tools + browser control 双叠加**: 扩大攻击面
4. **Gateway 探测超时**: 需排查网络连通性

## 上次扫描对比（08:17）
- 上午扫描18个SkillHub技能，无异常
- 中午全量113个技能，多发现 apify-ultimate-scraper 可疑代码问题
