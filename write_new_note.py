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
    
    # Click on "新建" button multiple times
    for i in range(3):
        new_btn_x = left + 75
        new_btn_y = top + 185 + i * 5
        print(f"Clicking 新建 button at ({new_btn_x}, {new_btn_y})...")
        dc.click(new_btn_x, new_btn_y)
        time.sleep(1)
        dc.screenshot(filename=f"new_note_{i}.png")
    
    # Now type to create new note
    time.sleep(2)
    
    # Click in the editor area to focus
    editor_x = left + 600
    editor_y = top + 400
    print(f"Clicking editor at ({editor_x}, {editor_y})...")
    dc.click(editor_x, editor_y)
    time.sleep(1)
    
    # Type the content
    content = """skill-vetter 使用指南

来源：@AI干货局 抖音视频
整理时间：2026-03-28

✅ 这是什么
skill-vetter 是 OpenClaw 的安全审查工具

核心定位：装技能前先过安全扫描，必装安全基石

核心数据：
• 来源：AI干货局推荐
• 点赞：2.1万
• 收藏：2.8万
• 评论：736

四大核心功能：
┌─ 安全扫描 ─────────────────────────────────┐
│ 恶意代码检测   - 扫描skill源码防注入        │
│ 隐私泄露预警   - 阻止偷传敏感数据           │
│ 权限越界拦截   - 识别超出范围的权限调用     │
│ 安全评分报告   - 安装前出具报告             │
└────────────────────────────────────────────┘

✅ 关键功能点

1. 恶意代码检测
• 扫描 skill 源码
• 防止注入攻击
• 检测可疑代码模式
• 识别恶意函数调用

2. 隐私泄露预警
• 阻止偷传敏感数据
• 检测网络请求
• 识别数据外发
• 保护本地文件访问

3. 权限越界拦截
• 识别超出范围的权限调用
• 权限使用审计
• 异常行为检测
• 权限最小化验证

4. 安全评分报告
• 每个 skill 安装前出具报告
• 风险等级评估
• 详细问题列表
• 修复建议提供

✅ 怎么使用

第一步：安装
┌─ bash ──────────────────────────────────────┐
│ openclaw skills install skill-vetter           │
└─────────────────────────────────────────────┘

第二步：扫描 Skill
┌─ bash ──────────────────────────────────────┐
│ openclaw skill-vetter scan <skill-name>       │
└─────────────────────────────────────────────┘

第三步：查看报告
• 查看安全评分
• 审阅问题列表
• 根据建议修复
• 确认安全后安装

✅ 优点
• 主动安全防御
• 安装前发现风险
• 防止恶意代码注入
• 保护隐私数据
• 权限使用透明化
• 降低系统风险

❌ 缺点
• 增加安装步骤
• 可能有误报
• 依赖规则库更新
• 不能100%保证安全
• 可能影响安装速度

✅ 使用场景
• 新 Skill 安装前必扫描
• 安全敏感环境
• 第三方 Skill 审查
• 生产环境部署前检查
• 团队共享 Skill 审核

🔧 运行依赖环境

┌─ 环境要求 ─────────────────────────────────┐
│ 运行时                                    │
│   • OpenClaw 已安装                       │
│                                          │
│ 依赖项                                    │
│   • skill-vetter 已安装                  │
│   • 安全规则库                            │
│                                          │
│ 系统要求                                  │
│   • 足够的扫描权限                        │
│   • 网络访问（规则库更新）               │
└─────────────────────────────────────────┘

✅ 部署使用注意点

安装注意点：
• 优先安装安全基石类 Skill
• 建议设为必检流程
• 定期更新规则库
• 关注扫描报告

扫描注意点：
• 扫描所有来源的 Skill
• 重点关注网络请求类
• 检查权限申请
• 审阅评分报告

安全注意点：
• 不要跳过安全报告
• 高风险 Skill 不要安装
• 关注误报情况
• 保持规则库最新

🕳️ 避坑指南

🔴 坑1：跳过扫描直接安装
问题：觉得麻烦跳过安全扫描
解决：安全无小事，必须扫描后再安装

🔴 坑2：高风险评分不处理
问题：看到高风险报告但仍安装
解决：高风险必须修复或放弃

🔴 坑3：规则库过期
问题：规则库太久没更新
解决：定期运行更新命令

🔴 坑4：误报导致误判
问题：正常 Skill 被标记为风险
解决：仔细审阅报告，确认是否为误报

🔴 坑5：权限申请不审查
问题：看到权限申请直接通过
解决：结合报告审阅权限是否合理

✅ 总结

值得安装的场景：
• 所有 OpenClaw 用户必装
• 生产环境必须检查
• 第三方 Skill 必须扫描
• 安全敏感场景

核心价值：
💡 装技能前先过安全扫描
💡 恶意代码检测防注入
💡 隐私泄露预警保护数据
💡 权限越界拦截保安全

学习价值：⭐⭐⭐⭐（4星）
实用价值：⭐⭐⭐⭐⭐（5星）
推荐指数：⭐⭐⭐⭐⭐（5星）
安全等级：🔒🔒🔒🔒🔒（必装）"""

    pyperclip.copy(content)
    dc.hotkey("ctrl", "v")
    time.sleep(2)
    dc.screenshot(filename="skill_vetter_new.png")
    print("Done!")
else:
    print("No Chrome window found!")
