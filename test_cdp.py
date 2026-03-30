from playwright.sync_api import sync_playwright
import time

# Try to connect to existing Chrome with debugging port
ws_url = "http://localhost:9222"

with sync_playwright() as p:
    try:
        print(f"Connecting to Chrome at {ws_url}...")
        browser = p.chromium.connect_over_cdp(ws_url)
        print("Connected!")
        
        # Get all contexts and pages
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.pages[0] if context.pages else context.new_page()
        
        print(f"Current URL: {page.url}")
        time.sleep(2)
        page.screenshot(path="cdp_step1.png")
        print("Screenshot 1 saved")
        
        # Try to find and click 新建 button
        try:
            # Click on text containing 新建
            page.locator("text=新建").click(timeout=5000)
            print("Clicked 新建")
        except Exception as e:
            print(f"Click 新建 failed: {e}")
        
        time.sleep(2)
        page.screenshot(path="cdp_step2.png")
        
        # Try clicking in the sidebar area
        try:
            # Find the new note button by partial text match
            page.get_by_text("新建", exact=False).click(timeout=5000)
            print("Clicked 新建 (partial)")
        except Exception as e:
            print(f"Click 新建 partial failed: {e}")
            
        time.sleep(2)
        page.screenshot(path="cdp_step3.png")
        
    except Exception as e:
        print(f"Error: {e}")
    
    input("Press Enter to close...")
    browser.close()
