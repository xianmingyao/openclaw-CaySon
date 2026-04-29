# 京麦商品发布自动化 v2.0 设计文档

> **日期：** 2026-04-30
> **状态：** 已确认，待实施
> **作者：** CaySon (by 宁兄指令)

---

## 1. 背景与目标

### 1.1 当前问题

`jingmai-product-publish` 项目积累了 302 个脚本，存在以下痛点：

| 痛点 | 影响 |
|------|------|
| 302 个脚本无统一入口 | 无法批量执行、无法复用 |
| 硬编码坐标散落各处 | 分辨率变化就全部失效 |
| 无 LLM 智能决策 | 弹窗处理、类目选择全靠硬编码规则 |
| 无持久化存储 | 发布结果无法追踪、无法回溯 |
| 无记忆系统 | 每次启动都从零开始，不积累经验 |

### 1.2 目标

借鉴 `jingmai-putaway` 的架构思想（不追求结构对齐），以现有 `jingmai_processor.py` 的 Processor（Strategy + Middleware）模式为核心，升级为框架化 2.0 架构：

- **302→28**：通过 ActionRegistry 将 302 个脚本合并为 28 个参数化 Action
- **统一 CLI**：Click 命令行入口，所有功能可独立调用
- **LLM 兜底**：Ollama → vLLM 双层本地模型调用链
- **ORM 持久化**：MySQL 主 + SQLite 备的双引擎数据库
- **Agent 分离**：Planner/Executor/Thinker 三个独立 Agent，各自 CLI 可调用
- **三层记忆**：Working（dict）+ Short-term（JSON 文件）+ Long-term（Milvus）

### 1.3 设计原则

- **保持所有现有逻辑**：不删除任何操作场景，只重组结构
- **以 Processor 为核心**：Strategy + Middleware 管道不变，是整个框架的骨架
- **只借鉴思想，不对齐结构**：从 putaway 学模式，不搬目录
- **依赖最小化**：不用 Redis（用 JSON 文件替代），不用 DI 容器

---

## 2. 目录结构

```
jingmai-product-publish/
├── cli.py                        # Click CLI 统一入口
├── config.py                     # Settings 配置类
├── exceptions.py                 # 异常层级体系
├── models.py                     # SQLAlchemy ORM 模型
├── db.py                         # DatabaseManager（MySQL/SQLite 双引擎）
├── init_db.py                    # 建表脚本
├── scraper.py                    # 京东商品抓取（独立）
├── requirements.txt
│
├── agents/                       # Agent 模块（各自 CLI 可调用）
│   ├── __init__.py
│   ├── base.py                   # BaseAgent + CircuitBreaker + 记忆集成
│   ├── planner.py                # PlannerAgent：任务分解
│   ├── executor.py               # ExecutorAgent：策略管道执行（规则驱动）
│   ├── thinker.py                # ThinkerAgent：LLM 视觉分析
│   └── factory.py                # AgentFactory：创建/注册/推荐
│
├── actions/                      # 28 个参数化 Action（覆盖 302 个脚本）
│   ├── __init__.py
│   ├── registry.py               # ActionRegistry：装饰器注册 + 动态发现
│   ├── window.py                 # 窗口操作（6 个函数）
│   ├── form.py                   # 表单操作（6 个函数）
│   ├── popup.py                  # 弹窗操作（3 个函数）
│   ├── navigation.py             # 导航操作（6 个函数）
│   └── verification.py           # 验证操作（3 个函数）
│
├── llm/                          # LLM 调用层
│   ├── __init__.py
│   ├── base.py                   # LLMProvider ABC
│   ├── ollama.py                 # OllamaProvider（Tier 1）
│   ├── vllm.py                   # VLLMProvider（Tier 2）
│   ├── router.py                 # MoERouter：健康检查 + 路由
│   └── manager.py                # LLMManager：多模态 + 调用兜底
│
├── memory/                       # 三层记忆系统
│   ├── __init__.py
│   ├── base.py                   # MemoryStore ABC + MemoryType/MemoryItem
│   ├── short_term.py             # JSON 文件短期记忆
│   ├── long_term.py              # Milvus 长期记忆
│   ├── working.py                # 进程内 dict 工作记忆
│   └── manager.py                # 统一管理器 + Agent 集成
│
├── infrastructure/               # 基础设施（从现有代码平移）
│   ├── __init__.py
│   ├── locator.py                # 双引擎定位器（UIA + 坐标 fallback）
│   ├── monitor.py                # 重试 + 熔断器
│   └── logger.py                 # JingmaiLogger（保持不变）
│
├── config/
│   ├── coords.py                 # 坐标配置（2560x1392）
│   └── product_template.json     # 商品模板
│
├── scripts/archive/              # 302 个旧脚本归档
├── logs/
└── SKILL.md
```

---

## 3. 核心架构

### 3.1 Processor 管道（保留现有核心）

保持 `jingmai_processor.py` 的 Strategy + Middleware 管道不变，作为 ExecutorAgent 的执行引擎：

```python
# 现有管道流程（不改变）
EnvironmentCheck → WindowLocate → ElementFind → ActionExecute → Verification
    ↓                 ↓               ↓              ↓              ↓
  LoggingMW        LoggingMW       LoggingMW      LoggingMW      LoggingMW
  ScreenshotMW     ScreenshotMW    ScreenshotMW   ScreenshotMW   ScreenshotMW
  RetryMW          RetryMW         RetryMW        RetryMW        RetryMW
```

ExecutorAgent 在外层包裹：
- **执行前**：读取记忆 → 加载配置 → 初始化 Context
- **执行后**：写入记忆 → 更新数据库 → 通知回调

### 3.2 BaseAgent 循环

借鉴 putaway 的 Think-Act-Observe-Reflect 四阶段循环：

```python
class BaseAgent:
    def execute(self, task: str) -> AgentResult:
        """主循环：Think → Act → Observe → Reflect"""
        while not self._is_done():
            # Think：读取记忆 + 规划下一步
            plan = self.think(task)

            # Act：执行策略管道
            result = self.act(plan)

            # Observe：观察结果（截图/元素/状态）
            observation = self.observe(result)

            # Reflect：写入记忆 + 决策是否继续
            self.reflect(observation)

        return self._aggregate_results()
```

**安全机制**（借鉴 putaway base.py）：
- 最大递归深度：10
- 同一 Action 连续重复：3 次后熔断
- 执行超时：600 秒
- 熔断器冷却：60s → 120s → 240s → 480s → 600s
- 连续 3 次成功后恢复

### 3.3 三个独立 Agent

| Agent | 职责 | CLI 入口 | LLM 需求 |
|-------|------|----------|----------|
| **PlannerAgent** | 任务分解为子任务 | `jingmai plan <描述>` | 需要（理解自然语言） |
| **ExecutorAgent** | 策略管道执行 | `jingmai execute --config xxx` | 不需要（规则驱动） |
| **ThinkerAgent** | 视觉分析 + 智能决策 | `jingmai think --screenshot xxx` | 需要（多模态） |

**AgentFactory**：创建/注册/推荐 Agent，支持关键词匹配和别名映射。

### 3.4 记忆与 Agent 集成

这是超越 putaway 的关键设计——putaway 的 memory 和 agent 是分离的，我们直接集成：

```python
class BaseAgent:
    def think(self, task: str) -> Plan:
        # 1. 从记忆中检索相关上下文
        memories = self.memory.search(task, top_k=5)

        # 2. 注入到规划上下文
        context = {"task": task, "memories": memories}

        # 3. 生成计划
        return self._plan(context)

    def reflect(self, observation: Observation):
        # 1. 记录步骤结果（短期记忆）
        self.memory.create(
            type=MemoryType.SHORT_TERM,
            content=f"步骤{self.step_count}: {observation.summary}",
            metadata={"success": observation.success}
        )

        # 2. 如果失败，记录教训（长期记忆）
        if not observation.success:
            self.memory.create(
                type=MemoryType.LONG_TERM,
                content=f"失败教训: {observation.error}",
                importance=0.8
            )
```

---

## 4. LLM 层

### 4.1 双层 Fallback 链

```
MoERouter（健康检查路由）
    ├── OllamaProvider（Tier 1）— 本地 Ollama，延迟低
    │     └── qwen3-vl thinking 提取（3 层响应恢复）
    │           ├── 正常 JSON 响应
    │           ├── thinking 标签内提取
    │           └── HTTP 直接请求兜底
    └── VLLMProvider（Tier 2）— 远程 vLLM，吞吐高
          └── httpx AsyncClient，OpenAI 兼容 API
```

### 4.2 LLMManager

```python
class LLMManager:
    def invoke(self, prompt: str, **kwargs) -> str:
        """调用 LLM，双层兜底"""
        # 1. 路由到健康 Provider
        provider = self.router.route()

        # 2. 调用，失败则 fallback
        try:
            return provider.invoke(prompt, **kwargs)
        except Exception:
            fallback = self.router.fallback()
            return fallback.invoke(prompt, **kwargs)

    def invoke_multimodal(self, prompt: str, image_path: str) -> str:
        """多模态调用（截图分析）"""
        # 图片缩放到 1024px，JPEG quality=75，base64
        image_data = self._prepare_image(image_path)
        return self.invoke(prompt, image=image_data)
```

### 4.3 LLM 使用场景

| 场景 | Agent | 说明 |
|------|-------|------|
| 类目选择 | ThinkerAgent | 分析商品关键词，选择京东类目 |
| 弹窗识别 | ThinkerAgent | 截图分析弹窗内容，决定处理方式 |
| 元素定位 | ThinkerAgent | 截图分析找到目标元素坐标 |
| 发布验证 | ThinkerAgent | 截图判断发布是否成功 |
| 任务分解 | PlannerAgent | 自然语言描述 → 子任务列表 |

---

## 5. ORM / 数据库

### 5.1 双引擎

```python
class DatabaseManager:
    """MySQL 主 + SQLite 备"""
    def __init__(self, settings: Settings):
        try:
            self.engine = create_engine(settings.mysql_url)
            self._test_connection()
        except Exception:
            self.engine = create_engine(settings.sqlite_url)
            logger.warning("MySQL 不可用，fallback 到 SQLite")
```

### 5.2 数据模型

```python
class Product(DBModel):
    """商品信息"""
    source_url: str              # 京东商品 URL
    title: str                   # 商品标题
    category_path: str           # 类目路径
    attributes: JSON             # 属性键值对
    images: JSON                 # 图片 URL 列表
    status: str                  # draft/ready/published/failed

class PublishTask(DBModel):
    """发布任务"""
    product_id: int              # FK → Product
    status: str                  # PENDING/PLANNING/IN_PROGRESS/COMPLETED/FAILED
    plan: JSON                   # 执行计划
    result: JSON                 # 执行结果
    error_message: str           # 错误信息

class TaskStep(DBModel):
    """任务步骤"""
    task_id: int                 # FK → PublishTask
    step_order: int              # 步骤顺序
    action_name: str             # Action 名称
    params: JSON                 # Action 参数
    status: str                  # PENDING/RUNNING/SUCCESS/FAILED
    screenshot_path: str         # 截图路径
    result: JSON                 # 步骤结果
```

---

## 6. 记忆系统

### 6.1 三层架构

| 层级 | 存储 | 生命周期 | 用途 |
|------|------|----------|------|
| Working | 进程内 dict | 单次执行 | 上下文传递、中间结果 |
| Short-term | JSON 文件 | 7 天 TTL | 步骤记录、会话状态 |
| Long-term | Milvus | 永久 | 失败教训、成功经验、类目知识 |

### 6.2 存储实现

```python
class WorkingMemory(MemoryStore):
    """进程内 dict，无 IO 开销"""
    def __init__(self):
        self._store: Dict[str, MemoryItem] = {}

class ShortTermMemory(MemoryStore):
    """JSON 文件存储，7 天 TTL"""
    BASE_DIR = "logs/memory/short_term"

    def create(self, item: MemoryItem) -> str:
        path = self.BASE_DIR / f"{item.id}.json"
        path.write_text(item.model_dump_json())

    def cleanup_expired(self):
        """清理过期记忆"""

class LongTermMemory(MemoryStore):
    """Milvus 向量存储（8.137.122.11:19530）"""
    COLLECTION = "jingmai_publish_memory"

    def search(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        embedding = self.llm.embed_text(query)
        results = self.collection.search(embedding, top_k=top_k)
```

### 6.3 统一管理器

```python
class MemoryManager:
    def __init__(self, llm: LLMManager, settings: Settings):
        self.working = WorkingMemory()
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(llm, settings)

    def create(self, type: MemoryType, content: str, **kwargs) -> str:
        """统一写入，根据类型路由到对应存储"""

    def search(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """跨层检索：working → short_term → long_term"""

    def promote_to_long_term(self, item_id: str):
        """将短期记忆提升为长期记忆"""
```

---

## 7. Action 层（302→28）

### 7.1 ActionRegistry

```python
class ActionRegistry:
    """装饰器注册 + 动态发现"""
    _actions: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, category: str):
        """装饰器：注册 Action"""
        def decorator(func):
            cls._actions[name] = {
                "func": func,
                "category": category,
                "doc": func.__doc__
            }
            return func
        return decorator

    @classmethod
    def execute(cls, name: str, **kwargs) -> Any:
        """执行 Action"""
        action = cls._actions.get(name)
        if not action:
            raise ValueError(f"未知 Action: {name}")
        return action["func"](**kwargs)
```

### 7.2 28 个 Action 清单

#### window.py（6 个函数，覆盖 43 个脚本）

| Action | 覆盖脚本类型 | 说明 |
|--------|-------------|------|
| `find_window` | 9 个窗口操作脚本 | 查找京麦窗口 |
| `activate_window` | 含在窗口操作中 | 激活并调整窗口 |
| `navigate_to` | 29 个导航脚本 | 导航到指定页面 |
| `take_screenshot` | 含在窗口操作中 | 窗口截图 |
| `inspect_elements` | 177 个 UIA 脚本 | UIA 元素扫描 |
| `set_focus` | 含在窗口操作中 | 设置窗口焦点 |

#### form.py（6 个函数，覆盖 102 个脚本）

| Action | 覆盖脚本类型 | 说明 |
|--------|-------------|------|
| `fill_text` | 含在表单填充中 | 4 层输入 fallback（set_edit_text → win32clipboard → pyperclip → pyautogui） |
| `select_dropdown` | 含在表单填充中 | ComboBox 下拉选择 |
| `paste_and_search` | 6 个搜索脚本 | 粘贴并搜索 |
| `fill_product_info` | 6 个表单填充脚本 | 批量填充商品信息 |
| `click_element` | 18 个通用点击脚本 | 点击指定元素 |
| `fix_field` | 含在表单填充中 | 修正表单字段 |

#### popup.py（3 个函数，覆盖 56 个脚本）

| Action | 覆盖脚本类型 | 说明 |
|--------|-------------|------|
| `dismiss_popup` | 38 个弹窗关闭脚本 | 关闭弹窗 |
| `handle_dialog` | 含在弹窗中 | 处理对话框 |
| `dismiss_cef_popup` | 含在弹窗中 | 关闭 CEF 弹窗 |

#### navigation.py（6 个函数，覆盖 57 个脚本）

| Action | 覆盖脚本类型 | 说明 |
|--------|-------------|------|
| `select_category` | 29 个类目导航脚本 | 选择商品类目 |
| `scroll_page` | 含在导航中 | 滚动页面 |
| `save_draft` | 含在导航中 | 保存草稿 |
| `publish_product` | 含在导航中 | 发布商品 |
| `click_modify` | 含在导航中 | 点击修改 |
| `go_back` | 含在导航中 | 返回上一页 |

#### verification.py（3 个函数，覆盖 15 个脚本）

| Action | 覆盖脚本类型 | 说明 |
|--------|-------------|------|
| `verify_result` | 5 个数据读取 + 5 个图片分析 | 验证执行结果 |
| `find_element_by_image` | 5 个图片分析脚本 | 图像识别定位 |
| `check_status` | 含在验证中 | 检查发布状态 |

**覆盖率：28 个 Action 覆盖全部 302 个脚本（100%）**

---

## 8. CLI 入口

```bash
# 发布相关
jingmai publish --config product.json          # 完整发布流程
jingmai batch --file products.xlsx             # 批量发布

# Agent 独立调用
jingmai plan <任务描述>                         # PlannerAgent：任务分解
jingmai execute --config xxx [--phase xxx]     # ExecutorAgent：策略执行
jingmai think [--screenshot xxx] [--question]  # ThinkerAgent：视觉分析

# 数据操作
jingmai scrape <url>                           # 抓取京东商品 → Product 表
jingmai tasks [--status xxx]                   # 查看任务状态
jingmai products                               # 查看商品列表
jingmai init-db                                # 初始化数据库

# 系统
jingmai status                                 # 环境检查
jingmai memory create/search/stats/clear       # 记忆管理
```

---

## 9. 异常体系

```python
class JingmaiError(Exception):
    """基础异常"""

class WindowNotFoundError(JingmaiError):
    """窗口未找到"""

class ElementNotFoundError(JingmaiError):
    """元素未找到"""

class ActionFailedError(JingmaiError):
    """Action 执行失败"""

class LLMError(JingmaiError):
    """LLM 调用失败"""

class DatabaseError(JingmaiError):
    """数据库错误"""

class MemoryError(JingmaiError):
    """记忆系统错误"""
```

---

## 10. 配置管理

```python
class Settings:
    """统一配置，支持环境变量 + .env 文件"""

    # 窗口
    WINDOW_TITLES: List[str] = ["jd_", "京麦", "jingmai"]
    WINDOW_WIDTH: int = 1280
    WINDOW_HEIGHT: int = 800

    # 数据库
    MYSQL_URL: str = "mysql+pymysql://..."
    SQLITE_URL: str = "sqlite:///data/jingmai.db"

    # LLM
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3-vl"
    VLLM_BASE_URL: str = "http://localhost:8000"
    VLLM_MODEL: str = "qwen3-vl"

    # Milvus
    MILVUS_HOST: str = "8.137.122.11"
    MILVUS_PORT: int = 19530

    # 记忆
    SHORT_TERM_TTL_DAYS: int = 7
    MEMORY_BASE_DIR: str = "logs/memory"

    # Agent 安全
    MAX_RECURSION_DEPTH: int = 10
    MAX_SAME_ACTION_REPEATS: int = 3
    EXECUTION_TIMEOUT: int = 600
    CIRCUIT_BREAKER_BASE_DELAY: int = 60

    # 重试
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_BASE_DELAY: float = 2.0
```

---

## 11. 依赖清单

```
# requirements.txt
click>=8.0
sqlalchemy>=2.0
pymysql>=1.1
httpx>=0.25
pyautogui>=0.9
pywinauto>=0.6
Pillow>=10.0
pyperclip>=1.8
win32gui; sys_platform == 'win32'
python-dotenv>=1.0
pymilvus>=2.3
```

---

## 12. 迁移路径

1. **阶段 1**：创建目录结构 + 基础模块（exceptions, config, logger）
2. **阶段 2**：迁移 infrastructure（locator, monitor）
3. **阶段 3**：创建 ActionRegistry + 28 个 Action
4. **阶段 4**：创建 LLM 层（provider → router → manager）
5. **阶段 5**：创建 Memory 层（working → short_term → long_term → manager）
6. **阶段 6**：创建 ORM 层（models → db → init_db）
7. **阶段 7**：创建 Agent 层（base → executor → thinker → planner → factory）
8. **阶段 8**：创建 CLI 入口 + 归档旧脚本
9. **阶段 9**：集成测试 + 文档更新

---

## 13. 与 putaway 的对比

| 维度 | putaway | publish v2 | 说明 |
|------|---------|------------|------|
| Agent 循环 | Think-Act-Observe-Reflect | 相同 | 借鉴 |
| LLM 兜底 | Ollama → vLLM | 相同 | 借鉴 |
| 数据库 | MySQL/SQLite 双引擎 | 相同 | 借鉴 |
| 短期记忆 | Redis | JSON 文件 | 简化，减少依赖 |
| 记忆-Agent 集成 | 未集成 | 已集成 | 超越 putaway |
| CLI 框架 | Click | 相同 | 借鉴 |
| 核心执行 | UFO screenshot pipeline | Processor Strategy 管道 | 不同，保持自有架构 |
| Action 数量 | 21 个 | 28 个 | 场景更多 |

---

## 14. 验收标准

- [ ] 302 个脚本全部归档到 `scripts/archive/`
- [ ] 28 个 Action 通过 ActionRegistry 注册并可独立调用
- [ ] CLI 所有命令正常工作
- [ ] ExecutorAgent 能完成一次完整的商品发布流程
- [ ] ThinkerAgent 能通过截图分析页面状态
- [ ] PlannerAgent 能分解自然语言任务
- [ ] LLM 双层 fallback 正常工作
- [ ] MySQL/SQLite 双引擎正常工作
- [ ] 三层记忆系统正常读写
- [ ] Agent 与记忆集成正常（think 读、reflect 写）
