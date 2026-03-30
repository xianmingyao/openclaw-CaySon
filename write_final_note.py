import sys
import time
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
    width = right - left
    height = bottom - top
    print(f"Window: {title}")
    
    # Activate the window
    win32gui.SetForegroundWindow(hwnd)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.5)
    
    # Click on the editor area (center-right of the window)
    editor_x = left + 600
    editor_y = top + 400
    print(f"Clicking on editor at ({editor_x}, {editor_y})...")
    dc.click(editor_x, editor_y)
    time.sleep(1)
    
    # Type the content
    content = """# 今日学习总结 2026-03-28

## Claude Code生态爆发！5个必知的新工具

> 来源：程序员Sunday 第57集

### 1. claude-code-action
- **Star数：6.5k**
- **功能：** GitHub Action，将Claude Code集成到CI/CD工作流
- **特点：** 140个发布版本，500+部署
- **源码结构：**
  - `.claude`: gh.sh包装器
  - `.github`: 非写权限用户检查工作流
  - `base-action`: Claude Code 2.1.81更新
  - `docs`: 行内注释确认参数
  - `examples`: 标签操作包装脚本
  - `scripts`: 硬化标签模式工具权限
  - `src`: Claude Code与Agent SDK版本更新
  - `test`: 移除冗余git状态/差异逻辑
  - `CLAUDE.md`: 重构简化模式系统

### 2. get-shit-done
- **Star数：39.3k**
- **功能：** 元提示+上下文工程

### 3. learn-claude-code
- **Star数：36.5k**
- **功能：** 框架教程

### 4. claude-hud
- **Star数：11.6k**
- **功能：** 状态可视化

### 5. claude-subconscious
- **功能：** 记忆增强

---

## gstack - YC CEO开源项目
- **Star数：33.2k**
- **作者：** Garry Tan（Y Combinator CEO）
- **功能：** YC创业孵化管理平台，15个AI Agent

---

## Claude Code生态核心要点
- 从单工具 → 平台生态
- Agent间协作（Handoff机制）
- CI/CD深度集成（claude-code-action）
- 上下文管理（claude-hud可视化）
- 元提示工程（get-shit-done）

---

## OpenClaw必装Skills
| 技能 | 安装量 | 状态 |
|------|--------|------|
| agent-browser | 607K+ | 已安装 |
| self-improving | 380K+ | 已安装 |
| skill-vetter | - | 已安装 |

---

## 记忆系统配置
- **首选：** 云端Milvus (8.137.122.11:19530)
- **备选：** 本地ChromaDB
- **检索：** `python E:\\workspace\\scripts\\mem0_dual_write.py search "查询"`

---

## 下一步学习计划
- [ ] claude-code-action 源码研究
- [ ] gstack 15个AI Agent架构
- [ ] 测试 Milvus 双写同步"""

    print("Typing content...")
    dc.type_text(content, interval=0.002)
    print("Content typed!")
    
    time.sleep(2)
    dc.screenshot(filename="final_note.png")
    print("Screenshot saved")
    
else:
    print("No Chrome window found!")
