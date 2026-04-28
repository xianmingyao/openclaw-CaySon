# Session 隔离问题修复设计

> 日期：2026-04-28
> 状态：待实现
> 范围：jingmai-cli Session 感知与自动对齐

---

## 问题背景

jingmai-cli 使用 `pyautogui` 进行截图和点击操作，这些操作作用于当前进程所在 Windows Session 的桌面。

**现状：**
- jingmai-cli 可能运行在 Session 0（Windows 服务上下文 / Claude Code SSH）
- 京麦 GUI 运行在 Session 1（远程桌面）
- `pyautogui.screenshot()` 截到 Session 0 的空白桌面
- `pyautogui.click()` 点击发到 Session 0，京麦不响应

**影响：** Agent 在 Session 0 运行时，所有 GUI 自动化操作失效，任务必然失败。

---

## 方案：Hybrid 混合方案（方案 C）

优先尝试同 Session 运行，失败时 fallback 到在当前 Session 启动京麦。

### 配置项

`config.py` 新增：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `SESSION_MODE` | `auto` | `auto` 自动检测 / `force_same` 强制同 Session / `manual` 不检查 |
| `TARGET_APP_PROCESS` | `Jingmai.exe` | 目标应用的进程名（用于 Session 检测） |

### 三种模式行为

| 场景 | auto | force_same | manual |
|------|------|------------|--------|
| cli.py 迁移失败 | warning + 继续 | error + 退出 | 不检查 |
| Session 不对齐 | warning + 尝试启动京麦 | error + 退出 | 不检查 |
| 京麦启动失败 | warning + 继续执行 | error + 退出 | 不检查 |
| 无管理员权限 | 降级到 warning | error + 退出 | 不检查 |

---

## 架构设计

### 1. SessionDetector 工具类

**文件：** `app/service/utils/session_detector.py`（新建，~150 行）

纯工具类，无状态，不依赖数据库/Redis。

```python
class SessionDetector:
    """Windows Session 检测与迁移工具"""

    def detect_current_session() -> int
        # ctypes.windll.kernel32.ProcessIdToSessionId()
        # 返回当前进程的 Session ID

    def find_interactive_session() -> Optional[int]
        # 解析 query session 命令输出
        # 返回有用户桌面的交互式 Session ID（通常是 1）

    def find_process_session(process_name: str) -> Optional[int]
        # tasklist /V /FI "IMAGENAME eq xxx" 解析 Session ID

    def is_same_session_as_process(process_name: str) -> bool
        # 判断当前进程与目标进程是否在同一 Session

    def try_migrate_to_interactive_session() -> bool
        # 通过 schtasks 创建计划任务在 Session 1 执行
        # 需要：管理员权限
        # 失败时返回 False

    def try_launch_in_target_session(exe_path: str, session_id: int) -> bool
        # 在指定 Session 启动目标程序
        # fallback：启动到当前 Session
```

**设计要点：**
- 所有方法同步（ctypes 调用），Agent 启动时调用一次
- 失败返回 False/None，不抛异常，不影响主流程

### 2. CLI 入口 Session 检查

**文件：** `cli.py`（修改，~25 行）

在 `cli()` 入口添加 Session 自动检测：

```python
def _ensure_interactive_session():
    """启动时检查 Session，必要时迁移"""
    detector = SessionDetector()
    current = detector.detect_current_session()
    interactive = detector.find_interactive_session()

    if current == interactive or interactive is None:
        return  # 已在正确 Session 或无法检测

    logger.warning(f"当前在 Session {current}，交互式桌面在 Session {interactive}")
    migrated = detector.try_migrate_to_interactive_session()
    if not migrated:
        logger.warning("Session 迁移失败，将在当前 Session 运行")

@click.group()
def cli():
    _ensure_interactive_session()  # 入口检查
    pass
```

**要点：**
- 只在入口调用一次
- 迁移失败不阻塞（用户可能执行 `status` 等非 GUI 命令）
- `run` / `interactive` 命令在 UFOAgent 中做二次检查

### 3. UFOAgent Session 对齐

**文件：** `app/service/agents/ufo_agent.py`（新增 ~60 行）

在 UFOAgent 中新增 `_ensure_session_alignment()` 方法：

```python
async def _ensure_session_alignment(self, task: Task) -> bool:
    """执行前确保 Session 对齐"""
    detector = SessionDetector()

    jingmai_session = detector.find_process_session("Jingmai.exe")
    current_session = detector.detect_current_session()

    if jingmai_session is not None and jingmai_session == current_session:
        return True  # 同 Session，正常

    if jingmai_session is not None and jingmai_session != current_session:
        # 京麦在其他 Session，尝试在当前 Session 启动
        if settings.SESSION_MODE == "force_same":
            return False
        return detector.try_launch_in_target_session("Jingmai.exe", current_session)

    # 京麦未运行，尝试启动
    return self._try_launch_jingmai()

def _try_launch_jingmai(self) -> bool:
    """启动京麦并等待窗口就绪（查找路径 → Popen → 轮询 tasklist 最多 30 秒）"""
    ...
```

**文件：** `app/service/agents/base.py`（修改 ~8 行）

在 `execute()` 的 for 循环前加检查：

```python
# Session 对齐检查（仅 UFOAgent 及其子类）
if hasattr(self, '_ensure_session_alignment'):
    aligned = await self._ensure_session_alignment(task)
    if not aligned and settings.SESSION_MODE == "force_same":
        execution.state = ExecutionState.FAILED
        execution.error_message = "Session 不对齐且 force_same 模式"
        return execution
```

**要点：**
- `hasattr` 检查，只对 UFOAgent 生效，不影响 RAGAgent/PlannerAgent
- 不改 execute() 签名，向后兼容

### 4. SKILL.md 文档更新

**文件：** `SKILL.md`（更新 ~30 行）

更新内容：
1. 关键配置表格新增 `SESSION_MODE` 行
2. 架构设计图中 Session 检测层
3. 新增"Session 隔离"章节

---

## 完整执行流程

```
jingmai run "京麦商品发布"
    │
    ▼
cli.py 入口
    ├─ detect_current_session()
    ├─ != 交互式 Session?
    │   ├─ Yes → try_migrate_to_interactive()
    │   │         ├─ 成功 → 进程重启到 Session 1
    │   │         └─ 失败 → warning，继续
    │   └─ No → 正常
    ▼
base.py execute()
    ├─ _ensure_session_alignment(task)
    │   ├─ 京麦同 Session → 继续
    │   ├─ 京麦不同 Session → 尝试启动京麦到当前 Session
    │   ├─ 京麦未运行 → 启动京麦
    │   └─ 全部失败 → auto 继续 / force 报错
    ▼
ReAct 循环 (think→act→observe→reflect)
```

---

## 修改文件清单

| 文件 | 操作 | 改动量 |
|------|------|--------|
| `app/service/utils/session_detector.py` | 新建 | ~150 行 |
| `cli.py` | 修改入口 | ~25 行 |
| `app/service/agents/ufo_agent.py` | 新增方法 | ~60 行 |
| `app/service/agents/base.py` | execute() 加检查 | ~8 行 |
| `config.py` | 新增配置项 | ~3 行 |
| `SKILL.md` | 更新文档 | ~30 行 |

**不修改：** `skill_aware_ufo_agent.py`（继承 UFOAgent 自动获得）、`runtime_bridge.py`（子进程继承父 Session）

---

## 验证标准

1. Session 1 终端运行 `jingmai run` → 正常执行，无 warning
2. Session 0 运行 `jingmai status` → 不触发 Session 检查
3. Session 0 运行 `jingmai run "京麦商品发布"` → 自动迁移或启动京麦
4. `SESSION_MODE=force_same` + Session 不对齐 → 报错退出
5. `SESSION_MODE=manual` → 不做任何 Session 检查
