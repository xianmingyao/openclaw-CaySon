# UFO Windows自动化技能学习笔记

## 项目信息
- **项目**: UFO³ (微软桌面智能体框架)
- **路径**: `E:\PY\UFO`
- **GitHub**: microsoft/UFO

---

## 一、核心架构

### 1. 模块结构
```
ufo/
├── agents/          # AI Agent模块
│   ├── agent/       # Agent基类
│   ├── cognitive/   # 认知模块
│   ├── memory/      # 记忆模块
│   └── processors/  # 处理器
├── automator/       # 自动化控制
│   ├── ui_control/  # UI控制核心
│   └── app_apis/    # 应用API
├── llm/            # LLM调用
├── prompter/       # Prompt管理
├── rag/            # RAG检索
└── tools/          # 工具集
```

### 2. 关键依赖
```python
# Windows UI自动化
import pywinauto
from pywinauto import Desktop
from pywinauto.controls.uiawrapper import UIAWrapper

# 坐标操作
import pyautogui

# 后端支持
backend = "uia"  # 推荐：UIAutomation
backend = "win32"  # 备选：Win32 API
```

---

## 二、UIA后端操作（推荐）

### 1. 连接窗口
```python
from pywinauto import Desktop

# 获取UIA后端的桌面
desktop = Desktop(backend="uia")

# 列出所有窗口
all_windows = desktop.windows()

# 查找目标窗口（京麦案例）
jingmai = None
for w in all_windows:
    title = w.window_text()
    rect = w.rectangle()
    # 找2560x1392的京麦主窗口
    if "jd_465d1abd3ee76" in title and rect.width() == 2560:
        jingmai = w
        break

# 激活窗口
jingmai.set_focus()
```

### 2. 查找元素
```python
# 查找所有按钮
buttons = jingmai.descendants(control_type="Button")
print(f"Found {len(buttons)} buttons")

# 查找所有链接
links = jingmai.descendants(control_type="Hyperlink")

# 查找特定元素
for btn in buttons:
    name = btn.element_info.name or ""
    rect = btn.rectangle()
    print(f"'{name}' at ({rect.left}, {rect.top})")
```

### 3. 点击元素（关键！）
```python
# 方法1: invoke() - 推荐！
xiugai_link.invoke()

# 方法2: click_input()
btn.click_input()

# 方法3: 直接调用()
elem()

# 备选: pyautogui
pyautogui.click(rect.left, rect.top)
```

---

## 三、坐标系统

### 1. 窗口坐标 vs 屏幕坐标
```python
# 窗口坐标 (0,0) 在窗口左上角
# 屏幕坐标 (0,0) 在屏幕左上角

rect = window.rectangle()
# rect.left, rect.top     # 窗口左上角屏幕坐标
# rect.right, rect.bottom # 窗口右下角屏幕坐标
```

### 2. 相对坐标转绝对坐标
```python
# 如果窗口不在(0,0)，需要加上窗口偏移
abs_x = rect.left + relative_x
abs_y = rect.top + relative_y
```

### 3. 京麦案例坐标
```
京麦窗口标题: jd_465d1abd3ee76
窗口大小: 2560x1392 (全屏)
窗口位置: (0, 0) - 左上角

已发现元素:
- X按钮 (关闭弹窗): (2137, 18) - 右上角
- "修改"链接: (979, 225)
- 确认弹窗"确定": (1314, 800)
- 确认弹窗"取消": (1386, 800)
```

---

## 四、UI树遍历

```python
# 获取直接子元素
children = window.children()

# 递归获取所有后代
all_descendants = window.descendants()

# 打印UI树
def print_tree(element, level=0, max_level=5):
    if level > max_level:
        return
    try:
        name = element.element_info.name or ""
        ctype = element.element_info.control_type or ""
        rect = element.rectangle()
        indent = "  " * level
        print(f"{indent}{ctype}: {name[:40]}")
        
        for child in element.children():
            print_tree(child, level + 1, max_level)
    except:
        pass
```

---

## 五、京麦CEF应用控制要点

### 问题
京麦使用CEF (Chromium Embedded Framework)，Win32鼠标事件无法穿透到内部渲染层

### 解决方案
使用 **pywinauto UIA后端**：
1. 直接获取UI元素引用
2. 调用元素的`invoke()`或`click_input()`方法
3. 不依赖坐标模拟

### 关键代码
```python
from pywinauto import Desktop

desktop = Desktop(backend="uia")
jingmai = desktop.windows()[...]  # 找到京麦窗口

# 查找"修改"链接
links = jingmai.descendants(control_type="Hyperlink")
for link in links:
    if "修改" in link.element_info.name:
        link.invoke()  # 直接调用，比坐标点击稳定
```

---

## 六、RAG检索模块

```python
from ufo.rag.retriever import RetrieverFactory

# 创建离线文档检索器
retriever = RetrieverFactory.create_retriever("offline", app_name="notepad")
results = retriever.retrieve(query="如何保存文件", top_k=5)

# 创建在线搜索检索器
retriever = RetrieverFactory.create_retriever("online", query="...", top_k=5)

# 使用FAISS向量数据库
from langchain_community.vectorstores import FAISS
db = FAISS.load_local(path, embedding)
```

---

## 七、Agent基类结构

```python
class BasicAgent(ABC):
    def __init__(self, name: str):
        self._step = 0
        self._name = name
        self._memory = Memory()
        self._host = None
        self._processor = None
        
    @abstractmethod
    def get_prompter(self):
        pass
    
    @abstractmethod
    async def context_provision(self):
        pass
```

---

## 八、Command-Receiver模式

```python
# Command执行
command = puppeteer.create_command("click", {"x": 100, "y": 200})
result = command.execute()

# 命令队列
puppeteer.add_command("click", {"x": 100, "y": 200})
results = puppeteer.execute_all_commands()
```

---

## 九、实战技巧

### 1. 窗口激活
```python
window.set_focus()
time.sleep(0.5)  # 等待窗口激活
```

### 2. 查找元素超时处理
```python
max_attempts = 3
for attempt in range(max_attempts):
    try:
        elem = window.child_window(title="目标")
        if elem.exists(timeout=5):
            break
    except:
        time.sleep(1)
```

### 3. 多种点击方式备选
```python
def safe_click(element):
    try:
        element.invoke()
    except:
        try:
            element.click_input()
        except:
            rect = element.rectangle()
            pyautogui.click(rect.left, rect.top)
```

---

## 十、UFO vs 我的jingmai自动化对比

| 维度 | UFO | 我的方案 |
|-----|-----|---------|
| 窗口查找 | pywinauto UIA | pywinauto + CDP |
| 点击方式 | invoke()/click_input() | CDP JS + Win32 |
| 元素识别 | UIAutomation | OCR + 坐标 |
| 适用场景 | 原生Windows应用 | CEF/Web应用 |

---

## 十一、学习心得

1. **UIA后端比Win32更可靠** - 特别是对于现代Windows应用
2. **invoke() > click_input() > pyautogui** - 按优先级尝试
3. **先set_focus()再操作** - 确保窗口激活
4. **descendants() vs children()** - descendants包含所有后代
5. **京麦CEF需要用UIA** - Win32事件无法穿透CEF渲染层

---

## 相关文件
- `E:\PY\UFO\ufo\automator\ui_control\controller.py` - 控制器
- `E:\PY\UFO\ufo\automator\ui_control\inspector.py` - 元素检查器
- `E:\PY\UFO\ufo\automator\ui_control\screenshot.py` - 截图
- `E:\PY\UFO\ufo\automator\ui_control\ui_tree.py` - UI树
- `E:\PY\UFO\ufo\automator\puppeteer.py` - 命令执行器
- `E:\PY\UFO\ufo\rag\retriever.py` - RAG检索器
- `E:\PY\UFO\ufo\agents\agent\basic.py` - Agent基类

---

## 更新记录
- **2026-04-24**: 京麦弹窗关闭成功，使用UIA后端invoke()方法
