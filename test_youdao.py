from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    # Launch a new browser
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # Navigate to Youdao
    print("Opening Youdao...")
    page.goto("https://note.youdao.com/web/")
    page.wait_for_load_state("networkidle")
    time.sleep(5)
    
    # Take initial screenshot
    page.screenshot(path="pw_step1.png")
    print("Step 1: Page loaded")
    
    # Find and click the 新建 button
    try:
        # Try clicking text that contains 新建
        try:
            page.locator("text=新建").first.click(timeout=3000)
            print("Clicked 新建")
        except Exception as e:
            print(f"Could not click 新建: {e}")
        
        time.sleep(2)
        page.screenshot(path="pw_step2.png")
        print("Step 2: After click")
        
        # Now try to find and click 新建笔记 in dropdown
        try:
            page.locator("text=新建笔记").click(timeout=3000)
            print("Clicked 新建笔记")
        except Exception as e:
            print(f"Could not click 新建笔记: {e}")
            
        time.sleep(2)
        page.screenshot(path="pw_step3.png")
        print("Step 3: Final state")
        
        # Try to type in editor if it exists
        try:
            # Find any textarea or contenteditable
            editor = page.locator("textarea, [contenteditable=true]").first
            if editor.is_visible():
                editor.click()
                print("Clicked editor")
                # Type some test content
                editor.fill("test content from playwright")
                print("Filled editor")
        except Exception as e:
            print(f"Could not type in editor: {e}")
            
        time.sleep(2)
        page.screenshot(path="pw_step4.png")
        print("Step 4: After typing")
        
    except Exception as e:
        print(f"Error: {e}")
        page.screenshot(path="pw_error.png")
    
    input("Press Enter to close...")
    browser.close()
