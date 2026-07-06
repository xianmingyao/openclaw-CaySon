# UFO³ 架构深度学习笔记

## 项目来源
- **路径**: `E:\PY\UFO`
- **GitHub**: microsoft/UFO
- **论文**: arxiv:2511.11332 (UFO³), arxiv:2504.14603 (UFO²)

---

## 一、整体架构

```
UFO/
├── galaxy/          # 多设备编排（DAG工作流）
├── ufo/            # 核心框架
│   ├── agents/      # Agent模块
│   ├── automator/  # 自动化控制
│   ├── llm/        # LLM调用
│   ├── module/      # 核心模块
│   ├── prompter/   # Prompt管理
│   ├── rag/        # RAG检索
│   └── tools/       # 工具集
├── config/         # 配置
└── dataflow/       # 数据流
```

---

## 二、Agent架构

### 1. 基础Agent类层次
```
BasicAgent (ABC)
├── AppAgent        # 应用Agent
└── HostAgent       # 主机Agent（协调者）
```

### 2. BasicAgent核心结构
```python
class BasicAgent(ABC):
    def __init__(self, name: str):
        self._step = 0
        self._name = name
        self._memory = Memory()
        self._host = None
        self._processor = None
        
    @abstractmethod
    def get_prompter(self) -> str:
        """获取Prompt模板"""
        
    @abstractmethod
    async def context_provision(self) -> None:
        """提供执行上下文"""
```

### 3. Memory模块
```python
class Memory:
    def add_memory_item(item: MemoryItem)
    def delete_memory_item(step: int)
    def from_list_of_dicts(data: List[Dict])
    def clear()
```

---

## 三、Processor处理器框架

### 1. 核心设计模式：模板方法 + 策略模式

```python
class ProcessorTemplate(ABC):
    # 策略字典，按阶段分发
    strategies: Dict[ProcessingPhase, ProcessingStrategy] = {}
    
    # 中间件链
    middleware_chain: List[ProcessorMiddleware] = []
    
    def process(self):
        # 1. 执行中间件（前置处理）
        # 2. 遍历策略执行
        for phase in ProcessingPhase:
            strategy = self.strategies[phase]
            strategy.execute(context)
        # 3. 执行中间件（后置处理）
```

### 2. 处理阶段（ProcessingPhase）
```python
class ProcessingPhase(Enum):
    DATA_COLLECTION = "data_collection"      # 数据采集
    LLM_INTERACTION = "llm_interaction"      # LLM交互
    ACTION_EXECUTION = "action_execution"    # 动作执行
    MEMORY_UPDATE = "memory_update"          # 记忆更新
```

### 3. HostAgent处理策略
```python
strategies = {
    ProcessingPhase.DATA_COLLECTION: DesktopDataCollectionStrategy(fail_fast=True),
    ProcessingPhase.LLM_INTERACTION: HostLLMInteractionStrategy(fail_fast=True),
    ProcessingPhase.ACTION_EXECUTION: HostActionExecutionStrategy(fail_fast=False),
    ProcessingPhase.MEMORY_UPDATE: HostMemoryUpdateStrategy(fail_fast=False),
}
```

---

## 四、Context上下文管理

### 1. 上下文命名枚举
```python
class ContextNames(Enum):
    REQUEST = "REQUEST"           # 当前请求
    SUBTASK = "SUBTASK"           # 子任务
    HOST_MESSAGE = "HOST_MESSAGE" # Host→App消息
    APPLICATION_WINDOW = "APPLICATION_WINDOW"  # 应用窗口
    ROUND_RESULT = "ROUND_RESULT" # 轮次结果
    # ...更多
```

### 2. 全局+本地上下文
```python
class ProcessingContext:
    def __init__(self, global_context, local_context):
        self.global_context = global_context
        self.local_context = local_context
```

---

## 五、自动化控制（Automator）

### 1. UIControl架构
```
ui_control/
├── controller.py    # 控制器（click, type, drag...）
├── inspector.py      # 元素检查器（查找元素）
├── screenshot.py    # 截图
├── ui_tree.py       # UI树
└── grounding/       # 元素定位（AI识别）
```

### 2. Backend策略
```python
class BackendFactory:
    @staticmethod
    def create_backend(backend: str):
        if backend == "uia":
            return UIABackendStrategy()   # 推荐
        elif backend == "win32":
            return Win32BackendStrategy()
```

### 3. Receiver-Command模式
```python
# Receiver: 负责执行命令的接收者
class ControlReceiver(ReceiverBasic):
    def click_input(self, params): ...
    def set_edit_text(self, params): ...
    
# Command: 命令封装
class ClickCommand(CommandBasic):
    def execute(self):
        return self.receiver.click_input(self.params)
```

---

## 六、UI操作核心（controller.py）

### 1. 点击方法优先级
```python
# 最优：invoke() > click_input() > pyautogui
def click_input(self, params):
    api_name = ufo_config.system.click_api  # 配置选择
    if api_name == "click":
        self.control.click(params)
    else:
        self.control.click_input(params)
```

### 2. 坐标转换
```python
def transform_point(self, x, y):
    """相对坐标(0-1) → 绝对坐标"""
    rect = self.application.rectangle()
    abs_x = rect.left + int(x * (rect.right - rect.left))
    abs_y = rect.top + int(y * (rect.bottom - rect.top))
    return (abs_x, abs_y)
```

### 3. 文本输入
```python
def set_edit_text(self, params):
    text = params.get("text", "")
    
    # 优先使用set_text
    if ufo_config.system.input_text_api == "set_text":
        self.control.set_edit_text(text)
    else:
        # 回退到type_keys
        self.control.type_keys(text, pause=0.1, with_spaces=True)
```

---

## 七、Inspector元素查找

### 1. UIA后端查找
```python
class UIABackendStrategy:
    def find_control_elements_in_descendants(
        self, window, 
        control_type_list=[],  # Button, Hyperlink, Text...
        title_list=[],
        is_visible=True,
        depth=0
    ) -> List[UIAWrapper]:
```

### 2. 使用示例
```python
desktop = Desktop(backend="uia")
jingmai = desktop.windows(title="jd_465d1abd3ee76")[0]

# 查找所有按钮
buttons = jingmai.descendants(control_type="Button")

# 查找特定文字的链接
for link in jingmai.descendants(control_type="Hyperlink"):
    if "修改" in link.element_info.name:
        link.invoke()  # 点击
```

---

## 八、RAG检索模块

### 1. 检索器工厂
```python
class RetrieverFactory:
    @staticmethod
    def create_retriever(retriever_type):
        if retriever_type == "offline":
            return OfflineDocRetriever()  # 本地文档
        elif retriever_type == "experience":
            return ExperienceRetriever()   # 经验检索
        elif retriever_type == "online":
            return OnlineDocRetriever()    # 在线搜索
```

### 2. FAISS向量数据库
```python
from langchain_community.vectorstores import FAISS

db = FAISS.load_local(
    path, 
    get_hugginface_embedding(),  # HuggingFace嵌入
    allow_dangerous_deserialization=True
)

results = db.similarity_search(query, top_k=5)
```

---

## 九、中间件（Middleware）

### 1. 中间件链式调用
```python
class ProcessorTemplate:
    def process(self):
        # 前置中间件
        for mw in self.middleware_chain:
            mw.pre_process(context)
        
        # 执行策略
        strategy.execute(context)
        
        # 后置中间件
        for mw in reversed(self.middleware_chain):
            mw.post_process(context)
```

### 2. 日志中间件
```python
class HostAgentLoggingMiddleware(EnhancedLoggingMiddleware):
    def __init__(self):
        super().__init__(log_level=logging.INFO)
```

---

## 十、设计模式总结

| 模式 | 应用场景 |
|-----|---------|
| **模板方法** | ProcessorTemplate定义处理流程骨架 |
| **策略模式** | 不同阶段用不同Strategy执行 |
| **工厂模式** | RetrieverFactory, BackendFactory |
| **命令模式** | Receiver-Command解耦操作 |
| **单例模式** | Desktop获取窗口 |
| **装饰器模式** | PhotographerDecorator截图增强 |

---

## 十一、京麦自动化借鉴

### 1. 采用UIA后端
```python
from pywinauto import Desktop
desktop = Desktop(backend="uia")  # 比win32稳定
```

### 2. 策略模式处理不同阶段
```python
# 京麦发布流程
strategies = {
    "DATA_COLLECTION": JingmaiDataCollectionStrategy(),  # 采集页面
    "ELEMENT_FIND": JingmaiElementFindStrategy(),        # 找元素
    "ACTION_EXECUTION": JingmaiActionStrategy(),         # 执行点击
    "VERIFICATION": JingmaiVerifyStrategy(),             # 验证结果
}
```

### 3. 中间件链
```python
middleware_chain = [
    JingmaiLoggingMiddleware(),     # 日志
    JingmaiScreenshotMiddleware(),  # 截图
    JingmaiRetryMiddleware(),       # 重试
]
```

### 4. 上下文管理
```python
class JingmaiContext:
    CURRENT_STEP = "jingmai_current_step"
    PRODUCT_DATA = "jingmai_product_data"
    WINDOW_HANDLE = "jingmai_window_handle"
```

---

## 十二、关键代码片段

### 查找京麦窗口
```python
desktop = Desktop(backend="uia")
for w in desktop.windows():
    if "jd_465d1abd3ee76" in w.window_text():
        rect = w.rectangle()
        if rect.width() == 2560 and rect.height() == 1392:
            return w
```

### 点击链接
```python
links = jingmai.descendants(control_type="Hyperlink")
for link in links:
    if "修改" in link.element_info.name:
        link.invoke()  # 比pyautogui稳定
        break
```

### 查找按钮并点击
```python
buttons = jingmai.descendants(control_type="Button")
for btn in buttons:
    if "确定" in btn.element_info.name:
        btn.invoke()
```

---

## 十三、学习心得

1. **模块化设计**: UFO各模块职责清晰，易于扩展
2. **策略+中间件**: 灵活替换处理逻辑和增强功能
3. **Context统一管理**: 全局+本地上下文避免数据混乱
4. **UIA > Win32**: 现代Windows应用用UIA后端更可靠
5. **invoke() > click_input()**: 优先调用元素方法而非坐标

---

## 更新记录
- **2026-04-24**: 首次深度学习，京麦UIA控制成功
