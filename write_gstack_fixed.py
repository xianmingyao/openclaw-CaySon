import sys
import time
import pyperclip
sys.path.insert(0, r"E:\workspace\skills\desktop-control-1-0-0")
from __init__ import DesktopController
import win32gui
import win32con

dc = DesktopController(failsafe=True)

def get_window_info(title_substring):
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title_substring in title and "Chrome" in title:
                rect = win32gui.GetWindowRect(hwnd)
                windows.append((title, rect, hwnd))
        return True
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows

print("Finding Chrome windows...")
chrome_windows = get_window_info("有道云笔记")
if not chrome_windows:
    chrome_windows = get_window_info("Chrome")

if chrome_windows:
    title, rect, hwnd = chrome_windows[0]
    left, top, right, bottom = rect
    
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.5)
    
    editor_x = left + 600
    editor_y = top + 400
    dc.click(editor_x, editor_y)
    time.sleep(1)
    
    dc.hotkey("ctrl", "a")
    time.sleep(0.5)
    dc.press("delete")
    time.sleep(0.5)
    
    content = """gstack 使用指南

来源：@阿博粒 抖音视频
整理时间：2026-03-28

✅ 这是什么
gstack 是 Y Combinator CEO Garry Tan 开源的创业方法论封装工具

核心数据：
• Star：33.2k（两周狂揽3万+）
• Fork：4k
• 创始人：Garry Tan（YC CEO）
• License：MIT
• 分支：76个

核心定位：
使用 Garry Tan 的 Claude Code 设置：
15个具有主见的工具担任：
• CEO（首席执行官）
• Designer（设计师）
• Eng Manager（工程经理）
• Release Manager（发布经理）
• Doc Engineer（文档工程师）
• QA（测试工程师）

✅ 关键功能点

1. 核心能力
• 将YC创业方法论封装成AI Agent
• 15个专业角色分工协作
• 支持Claude Code、Codex、Gemini等多Agent
• 创业导师：人手一个YC导师
• 打造一人公司独角兽

2. 源码结构
agents/sdk         - Agent SDK核心
github/workflows   - CI/CD集成
bin               - 入口脚本
browse            - 浏览器自动化
config            - 配置管理
codex             - Codex集成
design-consultant - 设计顾问
design-review     - 设计审查
docs              - 文档
guard             - 安全守卫

3. 技术特性
• 多Agent支持（Codex, Gemini, Claude）
• 安全Hook技能（技能使用遥测）
• Windows支持（Node.js Playwright fallback）
• 自动化工作流

✅ 怎么使用

第一步：安装配置
1. git clone https://github.com/garrytan/gstack.git
2. cd gstack
3. 安装依赖
4. 配置API Key

第二步：启动服务
┌─ bash ──────────────────────────────────────┐
│ python -m gstack.cli serve                   │
│ ./bin/gstack serve                          │
└─────────────────────────────────────────────┘

第三步：使用Agent
• /ship  - 发布产品
• /review - 代码审查
• /design - 设计咨询
• /doc    - 文档生成

✅ 优点
• YC CEO背书，方法论权威
• 15个专业角色，覆盖创业全流程
• 两周3万+ stars，验证度极高
• MIT协议，完全开源
• 多Agent协作（Codex/Gemini/Claude）
• Windows支持友好
• 持续活跃更新

❌ 缺点
• 学习成本较高（15个Agent协作）
• 需要配置多个API Key
• 国内访问GitHub可能受限
• 文档主要英文
• 角色分工复杂，调试困难
• 资源消耗大（多Agent）

✅ 使用场景
• 创业公司：一人公司快速启动
• 产品发布：从0到1的完整流程
• 代码审查：多角色把关质量
• 设计评审：专业设计顾问
• 文档建设：自动化文档生成
• 团队协作：模拟大型公司分工

🔧 运行依赖环境

运行时：
• Python 3.8+
• Node.js 18+（Windows支持）
• Claude Code / Codex / Gemini

依赖项：
• Playwright（浏览器自动化）
• API Keys（Claude/Codex/Gemini）

认证要求：
• ANTHROPIC_API_KEY
• OPENAI_API_KEY（Codex）
• GOOGLE_API_KEY（Gemini）

✅ 部署使用注意点

配置注意点：
• API Key必须配置在环境变量
• 支持多API轮询（成本优化）
• 默认使用Claude Code审查

成本注意点：
• 多Agent消耗大量tokens
• 建议设置API预算限制
• /review默认启用会增加成本

安全注意点：
• Hook技能有使用遥测
• 代码安全需要人工确认

🕳️ 避坑指南

🔴 坑1：API Key未配置
问题：启动报认证错误
解决：配置ANTHROPIC_API_KEY等环境变量

🔴 坑2：Windows Playwright失败
问题：Windows下浏览器自动化失败
解决：项目有Node.js fallback，会自动降级

🔴 坑3：多Agent冲突
问题：15个Agent同时工作可能指令冲突
解决：明确分工，使用/ship或/review单独调用

🔴 坑4：成本爆表
问题：多Agent大量调用API
解决：配置预算限制，审查使用频率

🔴 坑5：网络超时
问题：国内访问GitHub/API超时
解决：配置代理或使用国内镜像

✅ 总结

值得安装的场景：
• 创业者需要方法论指导
• 想要模拟大公司分工流程
• 研究多Agent协作架构
• 需要快速产品发布流程

不值得的场景：
• 个人简单项目（杀鸡用牛刀）
• 预算有限
• 国内网络受限

核心价值：
💡 把YC多年创业经验
💡 封装成15个AI Agent
💡 让每个人都能拥有YC导师

学习价值：⭐⭐⭐⭐⭐（5星）
实用价值：⭐⭐⭐⭐（4星）
推荐指数：⭐⭐⭐⭐⭐（5星）
项目热度：🔥🔥🔥🔥🔥（现象级）"""

    pyperclip.copy(content)
    dc.hotkey("ctrl", "v")
    time.sleep(2)
    dc.screenshot(filename="gstack_final.png")
    print("Done!")
else:
    print("No Chrome window found!")
