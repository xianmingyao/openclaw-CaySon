#!/usr/bin/env python
"""
有道云笔记追加内容脚本
使用Playwright + 保存的cookies
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_FILE = Path(__file__).parent.parent / ".cache" / "youdao_cookies.json"
NOTE_URL = "https://note.youdao.com/web/#/file/WEBa2b687261f801b0d8ba1335e93450410/note/WEB3f60fdbb1ff187554ffbe864d9c3c833/"

CONTENT = """
## OpenClaw 抖音视频学习（完整版 2026-03-27）

### 📌 视频情报汇总表（13条）

| 视频主题 | UP主 | 评分 |
|---------|------|------|
| OpenClaw天天失忆？一个Skill彻底解决 | 唐斩AI编程 | ⭐8.74 |
| OpenCode实测：从零开发AI应用 | 废才Club | ⭐4.64 |
| 盘点一周AI大事(3月8日) | 产品君 | ⭐7.48 |
| 强烈推荐三个超级进化技巧 | 土木AI提效 | ⭐5.69 |
| Claude Code封号？开源方案替代 | 程序员阿江 | ⭐8.92 |
| OpenClaw调度多个AI编程工具 | 自说自话的江哥 | ⭐5.10 |
| OpenClaw搭配飞书机器人 | 唐斩AI编程 | ⭐0.07 |
| OpenClaw Skills实战-文档图片 | 根谷老师 | ⭐2.30 |
| 8个Agent保姆级教程 | 璐璐Veronica | ⭐2.00 |
| OpenClaw进化成多Agent模式 | 唐斩AI编程 | ⭐7.99 |
| OpenCode+Skill实战原理 | 王赛博 | ⭐8.94 |
| GLM-4.7-Flash本地封神 | OpenClaw社区 | ⭐8.76 |

### 📌 核心主题总结

**1. 记忆持久化方案（mem0 + COS Vectors）**
- 痛点：每次新建会话就失忆
- 解法：Auto-Recall + Auto-Capture
- 安装：openclaw skills install mem0
- 三层独立记忆体系：上下文窗口→自动召回→长期存储

**2. 多Agent协作架构**
- 单Gateway + 多分身
- Token减半，效率翻倍
- 解决上下文污染问题
- Agent A（数据猎手）+ Agent B（批判家）+ Agent C（创意Writer）+ Agent D（排版师）

**3. Skills生态**
- 插件化扩展，灵活定制
- 已安装：agent-browser、skill-vetter、self-improving、windows-control等
- 好Skill = 定场景 + 立目标 + 理规则 + 给示例 + 划边界

**4. 8个Agent保姆级教程（璐璐Veronica）**
- 搜索Agent + 阅读Agent + 写作Agent + 校对Agent
- 排版Agent + 图片Agent + 发布Agent + 统计Agent
- 适合内容创作团队、自媒体运营、营销自动化

**5. OpenClaw + 飞书机器人集成**
- 飞书作为统一入口
- OpenClaw调度多个AI编程工具
- 企业AI助手集成、团队协作自动化

**6. OpenCode 开源替代方案**
- Claude Code的免费替代
- 本地运行，支持多种模型后端
- 适合不想被API限制的开发者

### 💡 学习结论

**OpenClaw生态核心价值**：
1. **记忆持久化** → 解决AI失忆痛点，跨会话保持连贯性
2. **多Agent协作** → 专业化分工，Token减半，效率翻倍
3. **Skills生态** → 插件化扩展，灵活定制
4. **多渠道接入** → 微信、飞书、Telegram统一入口

**与我当前工作的关联**：
- 记忆持久化：解决我每次新会话需要重新学习上下文的问题
- 多Agent协作：与宁兄讨论的多智能体架构高度相关
- Skills生态：与AGENTS.md中的技能学习准则一致

**下一步行动**：
- [ ] 调研 openclaw-mem0 插件安装和使用
- [ ] 研究多Agent模式的实际配置方法
- [ ] 参考8个Agent配置设计自己的Agent团队
- [ ] 关注唐斩AI编程、王赛博、程序员阿江的更新
"""

def main():
    # 加载cookies
    with open(COOKIES_FILE, "r", encoding="utf-8") as f:
        cookies = json.load(f)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.add_cookies(cookies)
        
        page = context.new_page()
        print("打开笔记...")
        page.goto(NOTE_URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        # 截图保存状态
        page.screenshot(path="youdao_note_before.png")
        print("已保存截图: youdao_note_before.png")
        
        # 尝试点击编辑区域
        try:
            # 查找iframe内的编辑区域
            frame = page.frame_locator("iframe[src*='editor']")
            if frame:
                print("找到编辑器iframe")
                # 点击内容末尾
                editor = frame.locator("[contenteditable='true']").last
                editor.click()
                editor.press("End")
                for _ in range(50):
                    editor.press("Shift+Home")
                editor.press("Delete")
        except Exception as e:
            print(f"尝试备用方案: {e}")
            try:
                # 直接在主页面找编辑区域
                page.click("body")
                page.keyboard.press("End")
            except Exception as e2:
                print(f"备用方案也失败: {e2}")
        
        # 输入内容
        page.keyboard.type(CONTENT)
        page.wait_for_timeout(1000)
        
        # 截图保存结果
        page.screenshot(path="youdao_note_after.png")
        print("已保存截图: youdao_note_after.png")
        
        print("\n请在浏览器窗口中检查内容是否正确，然后手动点击保存按钮")
        print("按回车键结束...")
        input()
        
        browser.close()

if __name__ == "__main__":
    main()
