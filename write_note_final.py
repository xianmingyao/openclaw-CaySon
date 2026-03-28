from pywinauto import Application
import time
import pyautogui
import win32gui
import win32con
import pyperclip

def activate_window_hwnd(hwnd):
    """使用 Win32 API 激活窗口"""
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.3)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    win32gui.BringWindowToTop(hwnd)
    time.sleep(0.3)

Hwnd = 5639224

print('=== 写入有道云笔记 ===')

print('Step 1: 激活窗口...')
activate_window_hwnd(Hwnd)
time.sleep(0.3)

# 复制内容到剪贴板
content = '''# 今日学习总结 2026-03-27

## 今日GitHub项目推荐

### 1. deer-flow（字节跳动 SuperAgent）
- Star数/今日增量：46,212 ⭐ / +5,472
- 链接：https://github.com/bytedance/deer-flow
- 核心功能：集研究·编码·创作于一体，支持沙箱+记忆+多级子代理协同
- 学习价值：⭐⭐⭐⭐⭐ 必研究

### 2. litellm（LLM网关）
- Star数/今日增量：40,651 ⭐ / +6,717（今日增量冠军）
- 链接：https://github.com/BerriAI/litellm
- 核心功能：统一调用100+ LLM API，OpenAI格式兼容，成本追踪，负载均衡
- 学习价值：⭐⭐⭐⭐⭐ 基础设施必学

### 3. TradingAgents-CN（金融多Agent）
- Star数/今日增量：21,309 ⭐ / +4,427
- 链接：https://github.com/hsliuping/TradingAgents-CN
- 核心功能：多智能体LLM中文金融框架，支持A股·港股·美股
- 学习价值：⭐⭐⭐⭐ 多Agent实战案例

## 今日Skills学习

### 1. agent-browser
- 功能描述：浏览器自动化CLI，支持点击/填表/截图/抓取
- 安装日期：2026-03-27
- 掌握程度：🔰 刚装，待实践

### 2. skill-vetter
- 功能描述：安装前安全审查，扫描恶意代码/权限越界/隐私泄露
- 安装日期：2026-03-27
- 掌握程度：🔰 刚装，待实践

### 3. self-improving
- 功能描述：自我反思/自学习/持续优化，错误自修复
- 安装日期：2026-03-27
- 掌握程度：🔰 刚装，待实践

### 4. windows-control
- 功能描述：Windows UI自动化，基于UFO源码改进，支持鼠标/键盘/窗口
- 安装日期：2026-03-27
- 掌握程度：🔰 刚装，已能基础使用

## 技术架构/方法论

### 多智能体架构三大流派
1. **层级协同**（deer-flow）：Supervisor + 多级子代理
2. **角色分工**（Eigent/TradingAgents-CN）：专业角色各司其职
3. **公司模拟**（agency-agents）：模拟整个部门协作

### 2026年AI竞争核心方向
- 从单模型能力 → 多模型协作 + 垂直场景落地
- 多智能体、记忆层、技能市场、工作流自动化

### Skill编写公式
好的Skill = 定场景 + 立目标 + 理规则 + 给示例 + 划边界

## 下一步学习计划

### 待学习项目
- deer-flow 源码研究（字节SuperAgent架构）
- litellm LLM网关实现
- Eigent 多Agent协作实战

### 计划实践场景
1. 在实际任务中使用新装的4个Skill
2. 用windows-control完成更多桌面自动化任务
3. Clone 1-2个核心项目研究源码
'''

pyperclip.copy(content)
print('已复制内容到剪贴板')

print('Step 2: 粘贴内容...')
activate_window_hwnd(Hwnd)
time.sleep(0.3)

# 粘贴
pyautogui.hotkey('ctrl', 'v')
time.sleep(1)

# 截图确认
screenshot = pyautogui.screenshot()
screenshot.save('E:\\workspace\\note_content.png')
print('截图已保存')

print('=== 完成 ===')
