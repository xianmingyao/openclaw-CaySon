---
name: jingmai-product-publish
description: |
  京麦商品发布自动化技能，面向 Windows 环境下的京麦客户端商品发布、草稿保存、批量导入、商品抓取、任务跟踪与记忆管理。
---

# jingmai-product-publish

京麦商品发布自动化技能，面向 Windows 环境下的京麦客户端商品发布、草稿保存、批量导入、商品抓取、任务跟踪与记忆管理。

## 触发词

- 京麦发布
- jingmai publish
- jingmai
- 京麦自动化
- 批量上架

## 环境要求

- Windows 10/11
- 已安装并登录京麦客户端
- 建议分辨率 `2560x1392`
- Python 3.10+ with venv
- 需要 `pip install -e .[dev]`
- 需要 `playwright install chromium`

## CLI 命令

### 环境检查

```bash
python cli.py check-config --root .
jingmai-publish check-config --root .
```

### 初始化数据库

```bash
python cli.py init-db
jingmai-publish init-db --root .
```

### 导入商品（草稿模式）

```bash
python cli.py run-import --excel ".\湖南上架表格.xlsx" --mode draft --root .
jingmai-publish run-import --excel ".\湖南上架表格.xlsx" --mode draft --root .
```

### 桌面执行检查

```bash
python cli.py run-desktop-check --step both --debug --root .
jingmai-publish run-desktop-check --step both --debug --root .
```

### 正式发布（有人工守卫）

```bash
python cli.py run-desktop-check --step t8-publish-product --confirm-publish --root .
jingmai-publish run-desktop-check --step t8-publish-product --confirm-publish --root .
```

### 检查证据

```bash
python cli.py check-evidence --root .
```

### 清理运行时日志

```bash
python cli.py cleanup-runtime-logs --root .
```

## v2 相对于 v1 的改进

1. **文档驱动规划**：先解析 `京麦上架流程.docx` 正文段落，再从真实段落生成步骤
2. **Precheck + Postcheck**：执行前截图预检，执行后截图复核
3. **偏差恢复矩阵**：按偏差类型执行恢复动作（recover_locator / force_relocate / navigate_to / select_category / wait）
4. **页面态细分恢复策略**：覆盖登录页 / 商品列表页 / 类目页 / 商品信息页 / 规格描述页 / 发布确认页
5. **Session1 Helper**：在用户桌面 Session 运行 Win32 操作，解决 Session 0 无法操作京麦的问题
6. **MySQL 持久化**：支持 `MYSQL_HOST / MYSQL_PORT / MYSQL_USER / MYSQL_PASSWORD / MYSQL_DATABASE` 自动拼接连接
7. **批量场景分治**：通过 `publish_mode` 区分 single / batch

## 执行模型

```
Plan-and-Solve（文档驱动规划）
  └─ 解析京麦上架流程.docx正文 → 生成带workflow元数据的步骤
        ↓
ReAct（每步完整循环）
  └─ Precheck(截图预检) → Act(执行动作) → Screenshot(截图) → Observe(LLM视觉分析) → Postcheck(截图复核)
        ↓
Reflection（递进式重试，最多3次）
```

## 调试选项

```bash
--verbose          # 详细输出
--log-file logs/cli-debug.log  # 日志文件
```

## Session1 Helper

京麦客户端运行在 Session 1，而脚本运行在 Session 0。Session 0 发出的操作无法传递到 Session 1 的京麦窗口。

**启动 Helper：**
```bash
cd E:\workspace\skills\jingmai-product-publish-v2
python session1_helper.py
# 或双击 start_helper.bat
```

## 故障排查

- `check-config` 失败 → 检查 Python 环境、playwright、.env 配置
- 桌面操作失败 → 确认京麦客户端已登录、Helper 已启动
- MySQL 连接失败 → 检查 MYSQL_* 环境变量，脚本会自动降级到 SQLite
