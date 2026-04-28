# HEARTBEAT.md

## 每日自动任务

### 🌙 00:30 - 每日安全扫描
使用edgeone-clawscan对所有已安装技能进行安全体检
- 扫描技能目录：E:\workspace\skills\
- 异常处理：发现问题立即通知宁兄

## 待处理任务

### ⚠️ knowledge-pull cron 异常（待调查）
- **问题**：`knowledge-base/sync_pull_notion.py` 多次被 SIGKILL 终止
- **影响**：凌晨3点多5个实例全部失败，cron状态却显示"ok"
- **可能原因**：内存不足 / 进程挂起 / 超时
- **建议**：检查脚本是否正常，可能需要添加超时或重试机制
- **Cron Job ID**: 67e39d09-e4b9-405e-88d5-b877739c6b3d
- **最近状态**：2026-04-28 20:00 cron 正常完成（报告已发送）

### 📊 2026-04-28 20:12 更新
- SIGKILL 模式：多个 exec 会话被系统强制终止（可能是 cron timeout 或内存不足）
- knowledge-base-sync cron 已完成：报告已生成（Milvus ~250/422 条因超时中断）
- 旧失败记录（4月25日）已过期，清理

## 心跳检查
- 上次检查：HEARTBEAT_OK
