# -*- coding: utf-8 -*-
"""
使用 Selenium 操作有道云笔记
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pyperclip

print('=== 使用 Selenium 操作有道云笔记 ===')

# 设置 Chrome 选项
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

print('Step 1: 连接到 Chrome...')
driver = None
try:
    driver = webdriver.Chrome(options=options)
    print('  已连接到 Chrome')
except Exception as e:
    print(f'  连接失败: {e}')

if driver:
    print('Step 2: 导航到技术知识库...')
    driver.get('https://note.youdao.com/web/#/file/WEBa2b687261f801b0d8ba1335e93450410/empty')
    time.sleep(3)
    driver.save_screenshot('E:\\workspace\\selenium_1.png')
    print('  截图已保存')
    
    print('Step 3: 查找并点击新建笔记按钮...')
    try:
        buttons = driver.find_elements(By.XPATH, "//*[contains(text(),'新建笔记')]")
        print(f'  找到 {len(buttons)} 个包含"新建笔记"的元素')
        
        if buttons:
            buttons[0].click()
            time.sleep(2)
            print('  已点击新建笔记')
            driver.save_screenshot('E:\\workspace\\selenium_2.png')
    except Exception as e:
        print(f'  点击失败: {e}')
    
    print('Step 4: 输入笔记内容...')
    # 复制内容到剪贴板
    content = """# 今日学习总结 2026-03-27

## 今日GitHub项目推荐

### 1. deer-flow（字节跳动 SuperAgent）
- Star数/今日增量：46,212 ⭐ / +5,472
- 链接：https://github.com/bytedance/deer-flow
- 核心功能：集研究·编码·创作于一体，支持沙箱+记忆+多级子代理协同
- 学习价值：⭐⭐⭐⭐⭐ 必研究

### 2. litellm（LLM网关）
- Star数/今日增量：40,651 ⭐ / +6,717
- 链接：https://github.com/BerriAI/litellm
- 核心功能：统一调用100+ LLM API
- 学习价值：⭐⭐⭐⭐⭐ 基础设施必学

### 3. TradingAgents-CN（金融多Agent）
- Star数/今日增量：21,309 ⭐ / +4,427
- 链接：https://github.com/hsliuping/TradingAgents-CN
- 学习价值：⭐⭐⭐⭐

## 今日Skills学习

### 1. agent-browser
- 功能：浏览器自动化CLI，支持点击/填表/截图/抓取
- 安装日期：2026-03-27

### 2. skill-vetter
- 功能：安装前安全审查，扫描恶意代码/权限越界
- 安装日期：2026-03-27

### 3. self-improving
- 功能：自我反思/自学习/持续优化
- 安装日期：2026-03-27

### 4. windows-control
- 功能：Windows UI自动化，基于UFO源码改进
- 安装日期：2026-03-27

## 技术架构/方法论

### 多智能体架构三大流派
1. 层级协同（deer-flow）
2. 角色分工（Eigent/TradingAgents-CN）
3. 公司模拟（agency-agents）

### Skill编写公式
好的Skill = 定场景 + 立目标 + 理规则 + 给示例 + 划边界

## 下一步学习计划

### 待学习项目
- deer-flow 源码研究
- litellm LLM网关实现

### 计划实践场景
1. 在实际任务中使用新装的Skill
2. Clone 核心项目研究源码"""
    
    pyperclip.copy(content)
    print('  内容已复制到剪贴板')
    
    # 尝试找到内容输入框
    try:
        # 尝试多种选择器
        selectors = [
            "div[contenteditable='true']",
            "[role='textbox']",
            ".note-content",
            "textarea"
        ]
        
        for selector in selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                elem.click()
                elem.send_keys(Keys.CONTROL, 'v')
                print(f'  已粘贴到: {selector}')
                break
            except:
                continue
    except Exception as e:
        print(f'  粘贴失败: {e}')
    
    time.sleep(2)
    driver.save_screenshot('E:\\workspace\\selenium_3.png')
    print('  截图已保存')
    
    print('=== 完成 ===')
    time.sleep(10)
else:
    print('无法连接到 Chrome，请确保已开启调试模式')
