#!/usr/bin/env python
"""有道云笔记JS调试脚本"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

COOKIES_FILE = Path(__file__).parent.parent / ".cache" / "youdao_cookies.json"

CONTENT = """
## OpenClaw 抖音视频学习（完整版 2026-03-27）

### 视频情报汇总表（13条）

| 视频主题 | UP主 | 评分 |
|---------|------|------|
| OpenClaw天天失忆？一个Skill彻底解决 | 唐斩AI编程 | ⭐8.74 |
| OpenCode实测：从零开发AI应用 | 废才Club | ⭐4.64 |
| 盘点一周AI大事(3月8日) | 产品君 | ⭐7.48 |
| 强烈推荐三个超级进化技巧 | 土木AI提效 | ⭐5.69 |
| Claude Code封号？开源方案替代 | 程序员阿江 | ⭐8.92 |
| OpenClaw调度多个AI编程工具 | 自说自话的江哥 | ⭐5.10 |
| OpenClaw进化成多Agent模式 | 唐斩AI编程 | ⭐7.99 |
| OpenCode+Skill实战原理 | 王赛博 | ⭐8.94 |
| GLM-4.7-Flash本地封神 | OpenClaw社区 | ⭐8.76 |

### 核心主题总结

**1. 记忆持久化方案（mem0 + COS Vectors）**
- 痛点：每次新建会话就失忆
- 解法：Auto-Recall + Auto-Capture
- 安装：openclaw skills install mem0

**2. 多Agent协作架构**
- 单Gateway + 多分身
- Token减半，效率翻倍
- Agent A（数据猎手）+ Agent B（批判家）+ Agent C（创意Writer）+ Agent D（排版师）

**3. Skills生态**
- 插件化扩展，灵活定制
- 已安装：agent-browser、skill-vetter、self-improving等

**4. 8个Agent保姆级教程**
- 搜索Agent + 阅读Agent + 写作Agent + 校对Agent
- 排版Agent + 图片Agent + 发布Agent + 统计Agent

**5. OpenClaw + 飞书机器人集成**
- 飞书作为统一入口，OpenClaw调度多个AI编程工具

**6. OpenCode 开源替代方案**
- Claude Code的免费替代，本地运行，支持多种模型后端

### 学习结论

1. 记忆持久化解决AI失忆痛点
2. 多Agent协作是复杂任务最优解
3. Skills生态是OpenClaw的核心优势
"""

def main():
    with open(COOKIES_FILE, "r") as f:
        cookies = json.load(f)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()
        
        page.goto("https://note.youdao.com/web/#/file/WEBa2b687261f801b0d8ba1335e93450410/note/WEB3f60fdbb1ff187554ffbe864d9c3c833/")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        # 尝试用JS注入内容
        js_code = """
        () => {
            // 查找所有iframe
            const iframes = document.querySelectorAll("iframe");
            console.log("找到" + iframes.length + "个iframe");
            
            // 尝试在主文档中查找编辑器
            const editors = document.querySelectorAll("[contenteditable]");
            console.log("找到" + editors.length + "个contenteditable元素");
            
            // 遍历所有iframe尝试找到编辑器
            for (let iframe of iframes) {
                try {
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    const editable = doc.querySelectorAll("[contenteditable]");
                    if (editable.length > 0) {
                        console.log("在iframe中找到editor:", iframe.src);
                        editable[0].focus();
                        return "found_in_iframe";
                    }
                } catch(e) {
                    console.log("iframe访问失败:", e.message);
                }
            }
            return "not_found";
        }
        """
        
        result = page.evaluate(js_code)
        print(f"JS执行结果: {result}")
        
        page.screenshot(path="youdao_debug.png")
        print("截图已保存: youdao_debug.png")
        
        input("按回车继续...")

if __name__ == "__main__":
    main()
