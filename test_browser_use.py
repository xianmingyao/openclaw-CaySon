"""
browser-use 深度使用示例
演示如何用 Python 代码直接操控 browser-use 库
"""
import asyncio
import json
from browser_use import Controller, Browser

async def main():
    print("=" * 60)
    print("browser-use Python API 测试")
    print("=" * 60)
    
    # 1. 创建浏览器控制器
    browser = Browser()
    controller = Controller(browser=browser)
    
    print("\n[1] 初始化成功！")
    
    # 2. 打开百度
    await controller.navigate("https://www.baidu.com")
    print("[2] 已打开百度")
    
    # 3. 等待页面加载
    await asyncio.sleep(1)
    
    # 4. 执行 JavaScript 提取热搜
    hot_search = await controller.execute_javascript("""
        Array.from(document.querySelectorAll('#hotsearch-content-wrapper li'))
        .map((li, i) => ({ rank: i+1, title: li.innerText.split('\\n')[0] }))
    """)
    print(f"[3] 提取到 {len(hot_search)} 条热搜")
    
    for item in hot_search[:5]:
        print(f"  {item['rank']}. {item['title']}")
    
    # 5. 获取页面截图
    screenshot_path = await controller.screenshot()
    print(f"[4] 截图保存到: {screenshot_path}")
    
    # 6. 获取完整 DOM 状态
    state = await controller.get_page_state()
    print(f"[5] 页面状态获取成功，URL: {state.get('url', 'unknown')}")
    
    # 7. 清理
    await browser.close()
    print("\n[6] 测试完成！")
    
    return hot_search

if __name__ == "__main__":
    results = asyncio.run(main())
    print(f"\n最终结果: {json.dumps(results[:3], ensure_ascii=False, indent=2)}")
