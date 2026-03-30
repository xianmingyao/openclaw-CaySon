import sys
import time
import pyperclip
sys.path.insert(0, r"E:\workspace\skills\desktop-control-1-0-0")
from __init__ import DesktopController
import win32gui
import win32con

dc = DesktopController(failsafe=True)

# Get Chrome window info
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

# Find the Youdao Chrome window
print("Finding Chrome windows...")
chrome_windows = get_window_info("有道云笔记")
if not chrome_windows:
    chrome_windows = get_window_info("Chrome")

if chrome_windows:
    title, rect, hwnd = chrome_windows[0]
    left, top, right, bottom = rect
    print(f"Window: {title}")
    
    # Activate the window
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.5)
    
    # Click on the editor area
    editor_x = left + 600
    editor_y = top + 400
    print(f"Clicking on editor at ({editor_x}, {editor_y})...")
    dc.click(editor_x, editor_y)
    time.sleep(1)
    
    # Select all and delete existing content
    print("Selecting all content...")
    dc.hotkey("ctrl", "a")
    time.sleep(0.5)
    dc.press("delete")
    time.sleep(0.5)
    
    # Copy content to clipboard
    content = """claude-code-action 使用指南

来源：程序员Sunday 第57集
整理时间：2026-03-28

✅ 这是什么
claude-code-action 是将 Claude Code 集成到 GitHub Actions CI/CD 工作流的官方 Action

核心数据：
• Star：6.5k
• Fork：1.6k
• Releases：140个版本
• Deployments：600+次部署
• 最新版本：Claude Code 2.1.81 / Agent SDK 0.2.81

✅ 关键功能点

1. 核心能力
• 将 Claude AI 编码能力集成到 GitHub 工作流
• 自动分析 Pull Request
• 代码审查与 Bug 修复
• 根据指令重构代码
• 利用 Agent SDK 以代理身份执行复杂开发任务

2. 源码结构
┌─ 项目结构 ─────────────────────────────────┐
│ .claude          - Claude 配置文件          │
│ .github          - GitHub 工作流定义         │
│ base-action      - 核心逻辑代码              │
│ docs             - 文档                     │
│ examples         - 使用示例                  │
│ scripts          - 脚本工具                  │
│ src              - 源代码                   │
│ test             - 测试套件                  │
│ CLAUDE.md        - Claude 指令规范          │
└────────────────────────────────────────────┘

✅ 怎么使用

第一步：安装配置
1. 在 GitHub 仓库中创建 .github/workflows/ 目录
2. 创建 yml 配置文件
3. 在仓库 Settings > Secrets 中添加 ANTHROPIC_API_KEY
4. 提交代码触发 workflow

第二步：编写工作流
┌─ yaml 工作流示例 ─────────────────────────────────┐
│ name: Claude Code Review                       │
│ on: [pull_request]                             │
│ jobs:                                          │
│   review:                                     │
│     runs-on: ubuntu-latest                    │
│     steps:                                     │
│       - uses: actions/checkout@v4              │
│       - uses: anthropic/claude-code-action@v1 │
│         with:                                  │
│           # 你的 Claude API Key                │
└─────────────────────────────────────────────────┘

第三步：运行验证
• 查看 Actions 日志
• 检查 Claude 的 PR 评论
• 根据反馈调整指令

✅ 优点
• 官方出品，稳定性高（140个版本迭代）
• 深度集成 GitHub 生态
• 支持 PR 自动审查
• Agent SDK 支持复杂任务执行
• 部署规模大（600+生产环境验证）
• 持续更新（2天前刚更新到 Claude Code 2.1.81）

❌ 缺点
• 需要配置 Claude API Key，有成本
• 国内访问 GitHub Actions 可能受限
• 配置有一定学习成本
• 需要编写 CLAUDE.md 提示词
• Agent SDK 版本需要同步更新

✅ 使用场景
• PR 代码审查自动化
• Bug 自动修复
• 代码重构建议
• 文档自动生成
• 测试用例编写
• CI/CD 质量门禁

🔧 运行依赖环境
┌─ 环境要求 ─────────────────────────────────┐
│ 运行时                                 │
│   • GitHub Actions 运行器               │
│   • Ubuntu / Windows / macOS           │
│                                         │
│ 依赖项                                 │
│   • Claude Code 2.1.81+               │
│   • Agent SDK 0.2.81+                  │
│   • Git                                 │
│                                         │
│ 网络要求                                 │
│   • 能访问 Anthropic API               │
│   • GitHub Actions 网络                 │
│                                         │
│ 认证要求                                 │
│   • ANTHROPIC_API_KEY (Secrets)        │
└─────────────────────────────────────────┘

✅ 部署使用注意点

配置注意点
• API Key 必须存放在 GitHub Secrets
• 不要硬编码在代码中
• CLAUDE.md 需要精心编写
• 设置合理的超时时间
• 配置合适的触发条件避免浪费

成本注意点
• Claude API 按 token 计费
• PR 审查可能消耗较多 tokens
• 建议设置预算限制
• 大文件可能超时

安全注意点
• API Key 权限最小化
• 工作流文件权限控制
• 避免处理敏感代码
• 审查输出需要人工确认

🕳️ 避坑指南

🔴 坑1：API Key 泄露
问题：把 API Key 硬编码到 workflow 文件
解决：使用 GitHub Secrets

🔴 坑2：超时失败
问题：大仓库或复杂任务超时
解决：配置 timeout-minutes 或拆分任务

🔴 坑3：Cost 爆表
问题：没有限制预算，API 费用飙升
解决：设置 cost-limits 或 use-built-in-cost-protection

🔴 坑4：触发频繁
问题：每次 push 都触发，浪费资源
解决：配置合适的触发条件（only: [pull_request]）

🔴 坑5：指令冲突
问题：CLAUDE.md 和 inline 指令冲突
解决：统一管理 CLAUDE.md，明确优先级

🔴 坑6：国内访问
问题：GitHub Actions 网络超时
解决：使用代理或 Gitea/GitLab 替代

✅ 总结

值得安装的场景：
• 团队有 CI/CD 质量门禁需求
• 需要自动化代码审查
• 已经在使用 GitHub Actions

不值得的场景：
• 个人项目，自动化收益不高
• 国内网络访问受限
• 预算有限

学习价值：⭐⭐⭐⭐⭐（5星）
实用价值：⭐⭐⭐⭐（4星）
推荐指数：⭐⭐⭐⭐（4星）"""

    pyperclip.copy(content)
    print("Content copied to clipboard")
    
    # Paste using Ctrl+V
    print("Pasting content...")
    dc.hotkey("ctrl", "v")
    print("Content pasted!")
    
    time.sleep(2)
    dc.screenshot(filename="claude_code_action_guide.png")
    print("Screenshot saved")
    
else:
    print("No Chrome window found!")
