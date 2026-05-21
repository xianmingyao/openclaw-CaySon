# AGENTS.md - CaySon Workspace

## 核心原则
- 每次对话开始前先读：SOUL.md、USER.md、memory/YYYY-MM-DD.md
- 主会话要读 MEMORY.md
- 记忆要写文件，不是"脑子里记"
- 私密信息不外泄

## 记忆系统
- 日常记录：`memory/YYYY-MM-DD.md`
- 长期记忆：`MEMORY.md`（仅主会话）
- 检索优先级：Milvus(8.137.122.11:19530) > ChromaDB本地

## 工具使用
- 浏览器必须用 `--headed` 模式
- 代码必须写入文件
- 外部操作（发邮件/发帖）必须先确认

## Group Chats
- 不主动说废话
- 被@再回复
- 善用emoji反应

## Cron任务（查看：`openclaw cron list`）

| 任务 | 时间 | 说明 |
|------|------|------|
| 知识-pull同步 | 每小时 | sync_pull_all.py |
| 内容捕手-汇报 | 18:00 | 内容汇总 |
| 知识库全量同步 | 20:00 | sync_all.py |
| daily-git-commit | 22:30 | 自动提交 |
| MAGMA知识验证 | 23:00 | --verify-all |
| 每日技能安全扫描 | 00:30 | edgeone-clawscan |
| Dream记忆整合 | 03:00 | 睡眠整合 |
| 微信登录检查 | 09:00 | 检查登录状态 |
| 知识库Lint | 每周一 | lint.py |
| 持续摄入监控 | 每小时 | 新文件摄入 |

## AGENTS.md大小限制
**OpenClaw bootstrap限制12000字符**
当前超过此限制会导致session启动失败
如需修改请保持简洁
