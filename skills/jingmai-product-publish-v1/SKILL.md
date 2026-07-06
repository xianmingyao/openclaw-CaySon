# 京麦商品发布自动化 Skill

## 概述
基于UFO架构的Windows自动化发布技能，模拟UFO的策略模式+阶段化处理

## 核心架构

### 1. ProcessingPhase（阶段枚举）
```python
class JingmaiPhase(Enum):
    WINDOW_LOCATE = "window_locate"      # 窗口定位
    ELEMENT_INSPECT = "element_inspect"  # 元素检测
    ACTION_EXECUTE = "action_execute"    # 动作执行
    RESULT_VERIFY = "result_verify"      # 结果验证
```

### 2. Strategy模式（策略基类）
```python
class JingmaiStrategy:
    @depends_on("window_hwnd")
    @provides("element_map", "ui_tree")
    async def execute(self, context):
        pass
```

### 3. Context共享
```python
class JingmaiContext:
    window_hwnd: int = None
    element_map: Dict = {}
    phase_results: Dict = {}
```

## 核心功能

### 1. 窗口定位
- 自动查找京麦客户端窗口
- 焦点管理
- 尺寸验证

### 2. 元素检测
- UIA扫描获取所有元素
- 按类型/名称/位置筛选
- 生成元素映射表

### 3. 动作执行
- Edit输入（set_edit_text + 剪贴板）
- ComboBox选择（下拉展开 + 选项点击）
- Button点击（invoke + 坐标点击）
- 滚轮滚动（pyautogui.scroll）

### 4. 结果验证
- 截图对比
- 元素存在性检查
- 报错反馈检测

## 使用方式

```bash
# 基本发布
python scripts\jingmai_publisher.py

# 指定配置
python scripts\jingmai_publisher.py --config config\product_001.json

# 调试模式
python scripts\jingmai_publisher.py --debug
```

## 关键技巧

### 1. CEF输入框处理
```python
# 方法1: set_edit_text
edit.set_edit_text("text")

# 方法2: 剪贴板粘贴（失败时）
pyperclip.copy("text")
pyautogui.hotkey('ctrl', 'v')
```

### 2. ComboBox下拉选择
```python
# 1. 点击展开
pyautogui.click(x, y)

# 2. 查找选项
for elem in elements:
    if "目标选项" in elem.name:
        elem.click()

# 3. 选择
pyautogui.click(option_x, option_y)
```

### 3. 焦点管理
```python
# 确保窗口在前
jingmai.set_focus()
time.sleep(0.5)
```

### 4. 滚轮滚动
```python
# 向下滚动3格
pyautogui.scroll(-3, x=1280, y=700)
```

## 京东数据字段映射

| 京东字段 | 京麦字段 | 示例值 |
|----------|----------|--------|
| 额定电压 | 额定电压 | 250V~ |
| 电流 | 电流 | 10A |
| 孔位 | 孔型配置 | 8位 |
| 电缆长度 | 电缆长度 | 5米 |
| 防护等级 | 防护等级 | IP55 |

## 文件结构
```
jingmai-product-publish/
├── SKILL.md
├── scripts/
│   ├── jingmai_publisher.py      # 主脚本
│   ├── jingmai_context.py       # 上下文管理
│   ├── jingmai_locator.py        # 元素定位
│   └── logs/                     # 日志目录
└── config/
    └── product_template.json     # 配置模板
```
