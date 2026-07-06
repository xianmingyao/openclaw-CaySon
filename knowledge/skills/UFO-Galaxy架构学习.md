# UFO³ Galaxy 架构深度学习

## 核心定位
Galaxy是UFO³的**多设备编排框架**，支持DAG工作流、跨设备任务调度。

---

## 一、Core模块 (依赖注入)

### 1. DI容器 (di_container.py)
```python
class LifecycleScope(Enum):
    SINGLETON = "singleton"    # 单例
    TRANSIENT = "transient"    # 每次创建
    SCOPED = "scoped"          # 作用域内单例

class ServiceDescriptor:
    def __init__(self, service_type, implementation_type=None, 
                 factory=None, instance=None, scope=LifecycleScope.TRANSIENT):
```

### 2. 接口设计 (interfaces.py)
```python
class ITask(ABC):
    @property
    @abstractmethod
    def task_id(self) -> TaskId: pass
    
    @abstractmethod
    async def execute(self, context: Optional[ProcessingContext]) -> ExecutionResult:
        pass

class ITaskFactory(ABC):
    @abstractmethod
    def create_task(self, name, description, config=None, **kwargs) -> ITask:
        pass
```

---

## 二、Constellation模块 (DAG编排)

### 1. TaskConstellation (task_constellation.py)
```python
class TaskConstellation:
    """
    DAG管理器，支持：
    - DAG验证和循环检测
    - 动态任务/依赖管理
    - LLM集成
    - 执行状态跟踪
    """
    def __init__(self, constellation_id=None, name=None):
        self._tasks: Dict[str, TaskStar] = {}
        self._dependencies: Dict[str, TaskStarLine] = {}
        self._state: ConstellationState = ConstellationState.CREATED
    
    def add_task(self, task: TaskStar) -> None
    def add_dependency(self, from_task: str, to_task: str, dep_type: DependencyType)
    def validate_dag(self) -> bool  # 检测循环
    async def execute(self) -> ConstellationResult
```

### 2. TaskStar (任务节点)
```python
class TaskStar:
    """
    任务节点，支持：
    - 多种设备类型
    - 优先级调度
    - 状态跟踪
    """
    @property
    def status(self) -> TaskStatus
    @property
    def priority(self) -> TaskPriority
```

### 3. TaskStarLine (依赖边)
```python
class TaskStarLine:
    """
    DAG边，表示任务间依赖关系
    """
    def __init__(self, from_task: str, to_task: str, dep_type: DependencyType):
```

### 4. 依赖类型 (enums.py)
```python
class DependencyType(Enum):
    UNCONDITIONAL = "unconditional"      # 无条件执行
    CONDITIONAL = "conditional"          # 条件执行
    SUCCESS_ONLY = "success_only"        # 仅成功后执行
    COMPLETION_ONLY = "completion_only"  # 仅完成后执行

class ConstellationState(Enum):
    CREATED = "created"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_FAILED = "partially_failed"

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_DEPENDENCY = "waiting_dependency"
```

---

## 三、执行引擎

### 1. 执行流程
```
TaskConstellation.execute()
    ├── validate_dag()           # DAG验证
    ├── topological_sort()      # 拓扑排序
    ├── for each task:
    │   ├── check_dependencies()  # 检查依赖
    │   ├── allocate_device()      # 分配设备
    │   └── execute_task()         # 执行任务
    └── collect_results()        # 收集结果
```

### 2. 状态机
```
CREATED -> READY -> EXECUTING -> COMPLETED
                         ↓
                      FAILED / PARTIALLY_FAILED
```

---

## 四、京麦自动化借鉴

### 1. DAG工作流
```python
# 京麦发布流程可以建模为DAG
class JingmaiConstellation(TaskConstellation):
    def __init__(self):
        super().__init__(name="京麦商品发布")
        
        # 添加任务节点
        self.add_task(TaskStar("环境检查", priority=Priority.HIGH))
        self.add_task(TaskStar("窗口定位", priority=HIGH))
        self.add_task(TaskStar("类目选择", priority=HIGH))
        self.add_task(TaskStar("信息填写", priority=MEDIUM))
        self.add_task(TaskStar("图片上传", priority=MEDIUM))
        self.add_task(TaskStar("发布确认", priority=HIGH))
        
        # 添加依赖边
        self.add_dependency("环境检查", "窗口定位", SUCCESS_ONLY)
        self.add_dependency("窗口定位", "类目选择", SUCCESS_ONLY)
        self.add_dependency("类目选择", "信息填写", SUCCESS_ONLY)
        self.add_dependency("信息填写", "图片上传", SUCCESS_ONLY)
        self.add_dependency("图片上传", "发布确认", SUCCESS_ONLY)
```

### 2. 策略+状态机
```python
class JingmaiTaskState(Enum):
    PENDING = "pending"
    LOCATING = "locating"      # 定位窗口
    SELECTING_CATEGORY = "selecting_category"  # 选择类目
    FILLING_INFO = "filling_info"  # 填写信息
    UPLOADING_IMAGES = "uploading_images"  # 上传图片
    CONFIRMING = "confirming"    # 确认发布
    COMPLETED = "completed"
    FAILED = "failed"
```

---

## 五、DI容器在UFO的应用

```python
# UFO的DI容器用法
container = DependencyInjectionContainer()

# 注册服务
container.register_singleton(ILogger, FileLogger)
container.register_transient(ITaskFactory, TaskFactory)
container.register_scoped(IContext, ProcessingContext)

# 获取服务
logger = container.resolve(ILogger)
task_factory = container.resolve(ITaskFactory)
```

---

## 六、关键设计模式

| 模式 | 应用 |
|-----|------|
| **DI容器** | 解耦依赖管理 |
| **策略模式** | 不同执行策略 |
| **状态机** | 任务状态转换 |
| **DAG编排** | 多任务依赖管理 |
| **工厂模式** | Task创建 |
| **观察者模式** | 进度回调 |

---

## 七、与UFO Agent的关系

```
UFO Agent (ufo/)
    │
    ├── HostAgent          # 主机协调
    │   └── HostAgentProcessor
    │       ├── DesktopDataCollectionStrategy
    │       ├── HostLLMInteractionStrategy
    │       ├── HostActionExecutionStrategy
    │       └── HostMemoryUpdateStrategy
    │
    └── AppAgent           # 应用执行
        └── AppAgentProcessor

Galaxy (galaxy/)
    │
    ├── TaskConstellation  # DAG编排
    │   ├── TaskStar       # 任务节点
    │   └── TaskStarLine   # 依赖边
    │
    └── Core
        ├── DependencyInjection  # DI容器
        └── Interfaces         # 接口定义
```

---

## 八、学习心得

1. **DI容器** - 解耦组件依赖，便于测试和替换
2. **DAG编排** - 复杂工作流建模，支持条件依赖
3. **状态机** - 清晰的任务生命周期管理
4. **接口隔离** - ISP原则，每个接口单一职责
5. **生命周期管理** - SINGLETON/TRANSIENT/SCOPED三种作用域

---

## 更新记录
- **2026-04-24**: 首次深度学习Galaxy架构
