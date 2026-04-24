# 京麦商品发布自动化 Skill v3.0

## 📋 概述

基于 **UFO³ Processor框架** 实现的京麦商家后台商品发布自动化。

## 🏗️ 架构设计（UFO风格）

```
JingmaiPublishProcessor
    │
    ├── Strategies (策略模式)
    │   ├── EnvironmentCheckStrategy   # 环境检查
    │   ├── WindowLocateStrategy       # 窗口定位
    │   ├── ElementFindStrategy        # 元素查找
    │   ├── ActionExecuteStrategy      # 动作执行
    │   └── VerificationStrategy      # 结果验证
    │
    └── MiddlewareChain (中间件)
        ├── LoggingMiddleware          # 日志记录
        ├── ScreenshotMiddleware       # 截图存档
        └── RetryMiddleware           # 失败重试
```

### ProcessingPhase 流程阶段

| 阶段 | 策略类 | 失败策略 | 说明 |
|------|--------|---------|------|
| ENVIRONMENT_CHECK | EnvironmentCheckStrategy | fail_fast=False | 检查依赖和屏幕 |
| WINDOW_LOCATE | WindowLocateStrategy | fail_fast=True | 查找京麦窗口 |
| ELEMENT_FIND | ElementFindStrategy | fail_fast=True | 查找UI元素 |
| ACTION_EXECUTE | ActionExecuteStrategy | fail_fast=False | 执行点击/输入 |
| VERIFICATION | VerificationStrategy | fail_fast=False | 验证结果 |

### MiddlewareChain 中间件链

| 中间件 | 功能 |
|--------|------|
| LoggingMiddleware | 打印阶段header和结果 |
| ScreenshotMiddleware | 每阶段截图保存 |
| RetryMiddleware | 失败时自动重试(最多3次) |

## 📁 目录结构

```
jingmai-product-publish/
├── SKILL.md                          # 本文件
├── scripts/
│   ├── jingmai_processor.py          # UFO风格Processor (18KB) ⭐NEW
│   ├── jingmai_publisher.py         # 主发布脚本
│   ├── jingmai_logger.py            # 日志模块
│   ├── jingmai_locator.py           # 元素定位器
│   ├── jingmai_monitor.py           # 监听重试机制
│   └── screenshot_now.py            # 实时截图
├── config/
│   └── product_template.json         # 商品配置模板
└── logs/                            # 日志目录
```

## 🚀 使用方法

### 方式1: UFO Processor (推荐)
```python
from jingmai_processor import create_publisher, run_simple_publish

# 简单模式
run_simple_publish("公牛插座 B5440")

# 自定义模式
processor = create_publisher({"product": {"title": "商品名称"}})

# 添加动作
action_strategy = processor.get_action_strategy()
action_strategy.add_action("click", {"name": "修改", "x": 979, "y": 225})
action_strategy.add_action("input", {"name": "商品标题", "text": "商品名称"})
action_strategy.add_action("wait", {"duration": 2})

# 执行
processor.process()
```

### 方式2: 命令行
```bash
python scripts\jingmai_processor.py
```

### 方式3: OpenClaw触发
```
@CaySon 执行京麦商品发布
```

## 🔑 核心组件

### JingmaiContext - 上下文
```python
@dataclass
class JingmaiContext:
    current_phase: ProcessingPhase
    config: Dict[str, Any]
    window_hwnd: int
    found_elements: Dict[str, Any]  # 按钮、链接、编辑框
    success: bool
    screenshot_path: str
```

### ProcessingStrategy - 策略基类
```python
class ProcessingStrategy(ABC):
    def __init__(self, fail_fast: bool = True)
    @abstractmethod
    def execute(self, context: JingmaiContext) -> bool
```

### ActionExecuteStrategy - 动作执行
支持的动作类型：
- `click`: 点击元素 `{"name": "按钮名"}` 或坐标 `{"x": 100, "y": 200}`
- `input`: 输入文本 `{"name": "编辑框名", "text": "内容"}`
- `wait`: 等待 `{"duration": 2}`

## 📊 UIA元素定位

### 京麦窗口特征
- 标题: `jd_465d1abd3ee76`
- 尺寸: 2560x1392 (全屏)
- 后端: `uia` (UIAutomation)

### 已发现元素

| 元素类型 | 数量 | 示例 |
|---------|------|------|
| Button | ~22 | "下一步"、"确定"、"取消" |
| Hyperlink | ~15+ | "修改"、类目链接 |
| Edit | 2 | 搜索框(1724x23)、类目搜索(1449x40) |

### 关键坐标
- X关闭按钮: (2137, 18)
- "修改"链接: (979, 225)
- 确认"确定": (1314, 800)
- 确认"取消": (1386, 800)

## 🐛 已知问题

1. **CEF输入框**: pyautogui无法输入CEF搜索框，需用`set_edit_text()`
2. **类目导航**: 点击一级类目后需等待页面刷新
3. **坐标转换**: UIA返回的是屏幕坐标，无需转换

## 📜 变更日志

### v3.0 (2026-04-24)
- ⭐ **全新**: UFO³ Processor框架架构
- ⭐ **新增**: ProcessingPhase 5阶段流程
- ⭐ **新增**: MiddlewareChain 中间件链
- ⭐ **新增**: Strategy策略模式实现
- ⭐ **新增**: JingmaiContext统一上下文
- 🐛 **修复**: CEF输入框问题（使用set_edit_text）

### v2.0 (2026-04-24)
- 新增: 实际元素坐标配置
- 新增: 四级类目选择支持
- 新增: 商品信息页面完整坐标

### v1.0 (2026-04-24)
- 初始版本
- 基本发布流程
