# MEMORY.md - 长期记忆

## 用户信息
- **称呼**：宁采臣 / 宁兄
- **身份**：CTO，24年技术老炮
- **时区**：Asia/Shanghai

## 核心铁律
- 代码必须落地到文件，不能只存在对话中
- 铁律1：实事求是，数据说话
- 铁律2：代码质量 > 代码速度 > 炫技
- TDD测试文件锁：Claude Code会改测试期望值让测试通过 → 测试文件需加锁不给AI修改权限

## 记忆检索铁律
1. 首选 → 云端 Milvus (8.137.122.11:19530, collection: CaySon_db)
2. 备选 → 本地 ChromaDB (Milvus 故障时降级)

## MAGMA 四维记忆系统 v2
- **三写机制**：同时写入 MAGMA四维图谱(JSON) + Mem0(ChromaDB) + Milvus(云端)
- **四维检索**：语义0.3 + 时间0.2 + 因果0.3 + 实体0.2
- **脚本位置**：`scripts/magma_memory/`（core.py/retrieval.py/entity.py/writer.py/hybrid.py/cli.py）
- **Cron验证**：每天 23:00 (Job ID: `5026d732-e146-4d71-a023-44323e676181`)

## 行为准则规范

### 🔴 红线行为规范
- 严禁 exfiltrate 私人/私密数据
- 严禁运行破坏性命令（执行前必须获得明确授权）
- 优先使用 trash 而非 rm（确保数据可恢复）
- 不确定的操作必须先获取明确指令

### 🌐 浏览器操作规范（agent-browser）
- 必须启用 --headed 有头模式（宁兄指令）
- 必须使用现有浏览器的 cookie 和地址，禁止开新标签
- 禁止请求管理员权限

### 🛡️ 技能安全规范
- 安装前：必须通过 edgeone-clawscan 安全风险评估
- 每日 0:30：自动执行所有已安装技能的安全检测 (Job ID: `5227d14e-ae2f-4a41-93c7-3f14b58b9cfc`)

### 📚 SkillHub CLI 操作规范
```bash
python ~/.skillhub/skills_store_cli.py search <关键词>
python ~/.skillhub/skills_store_cli.py install <技能名>
python ~/.skillhub/skills_store_cli.py update <技能名>
```

## 项目状态

### 京麦智能体
- **进度**：72%（2026-04-17确认）
- **文档**：`E:\文案\外包\运营\ELUCKY-技术架构设计.md`
- **Skill**：`E:\workspace\skills\jingmai-product-publish\`
- **坐标换算**：实际X = 识别X × 2，实际Y = 识别Y × 1.74（截图2560×1392，识别1280×800）
- **Bug已修复**：import timedelta / setup_file_logger() / aiohttp泄漏 / List未导入

### ELUCKY 账号矩阵
| 平台 | 账号数量 | 定位 |
|------|---------|------|
| TikTok | 230 | 主力平台 |
| Facebook | 150 | 社交引流 |
| Instagram | 120 | 视觉内容 |
| X (Twitter) | 80 | 资讯分发 |

## Karpathy 知识库系统
- **目录**：`E:\workspace\knowledge-base\`
- **核心脚本**：compile.py / sync_feishu.py / sync_notion.py / upload_mem0.py
- **Cron**：每天 20:00 同步 (Job ID: `7c7f5f69-f412-4694-b41b-c480692c9927`)
- **Milvus**：185,225 条（2026-04-29）
- **飞书Database ID**：33d2bb5417c380f6baaff3467dea91c8

## Cron 定时任务

| 任务 | ID | 时间 | 状态 |
|------|-----|------|------|
| continuous-ingest | f2199500 | */5 * * * * | ✅ ok |
| daily-git-commit | 1690b963 | 22:30 | ✅ ok |
| knowledge-base-sync | 7c7f5f69 | 20:00 | ✅ ok |
| knowledge-pull | 67e39d09 | 0 * * * * | ✅ ok |
| daily-skill-security-scan | 5227d14e | 00:30 | ✅ ok |
| dream-nightly | 421b1f35 | 03:00 | ✅ ok |
| MAGMA知识验证报告 | 5026d732 | 23:00 | ⚠️ error |
| morning-wechat-login-check | e1f7f495 | 09:00 | ✅ ok |
| 内容捕手-汇报 | f27317c4 | 18:00 | ✅ ok |

## 已安装 Skills

| 技能 | 版本 | 日期 | 用途 |
|------|------|------|------|
| summarize | 1.0.0 | 2026-04-02 | 网页/PDF/YouTube总结 |
| nano-banana-pro | 1.0.1 | 2026-04-02 | AI图片生成 |
| memory-dream | 1.0.3 | 2026-04-07 | 记忆整合 |
| huguanjin-libtv-skill | 1.0.4 | 2026-04-29 | LibTV AI视频生成 |

## 踩坑记录（重要）

### 京麦自动化 Session 隔离根因（04-28）
- **京麦应用**：CEF浏览器，运行在 Session 1（宁兄远程桌面）
- **jingmai-cli**：运行在 Session 0（Windows服务上下文）
- **根因**：Session 0 的鼠标点击无法传递到 Session 1 的京麦窗口
- **建议方案**：宁兄手动搜索"插座"并选择类目，CaySon 继续自动填写

### Notion 10000 页分批拉取（04-24~04-25）
- **根因**：一次性加载内存不足导致 SIGKILL
- **解决方案**：generator 模式分批处理
- **状态**：✅ 已解决

### qwen3-vl:8b JSON 模式不稳定（04-22~04-24）
- **现象**：简单描述请求3秒完成，JSON格式请求超时（>25秒）
- **解决方案**：改用 `format="text"` + 描述性方法 + 启发式定位

### OpenClaw 安全评分下降（04-28）
- **评分**：72/100
- **高危CVE**：GHSA-xmxx-7p24-h892（Gateway HTTP认证令牌缓存问题）
- **紧急**：升级 OpenClaw 至 2026.4.20

## Dream 整合记录（最近）

### 2026-04-28 整合
- Notion SIGKILL 问题已解决（generator 分批处理）
- 飞书 Token 问题持续（.feishu_token 缺失）

### 2026-04-27 整合
- code-review-graph 新增（Tree-sitter AST + 知识图谱 + MCP，6.8×/49× Token节省）

### 2026-04-25 整合
- Notion 10000 页分批拉取问题确认
- 京麦商品发布自动化4个Bug已修复

## 日报格式
```
YYYY.MM.DD(日报)
1、事项 + 完成进度%
2、事项 + 状态
...
```
