# -*- coding: utf-8 -*-
"""
使用CDP直接关闭弹窗
"""
import subprocess
import json
import time

# Chrome DevTools Protocol - 使用PowerShell执行
# 首先获取Chrome的调试端口

# 方法1: 使用PowerShell获取Chrome窗口并执行CDP命令
ps_script = r'''
$chromeHwnd = Get-Process chrome | Where-Object {$_.MainWindowHandle -ne 0} | Select-Object -First 1 | ForEach-Object {$_.MainWindowHandle}
Write-Output "Chrome HWND: $chromeHwnd"

# 尝试连接到Chrome的DevTools
$port = 9222

# 获取页面信息
$response = Invoke-RestMethod "http://localhost:$port/json" -TimeoutSec 3 -ErrorAction SilentlyContinue
Write-Output ($response | ConvertTo-Json)
'''

result = subprocess.run(
    ['powershell', '-Command', ps_script],
    capture_output=True,
    text=True,
    timeout=15
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)

# 方法2: 直接用Python CDP
print("\n\nTrying Python CDP approach...")

try:
    import websocket
    
    ws_url = "ws://localhost:9222/devtools/page/2A2B3C4D5E6F"
    
    # 获取Chrome DevTools可用端点
    import urllib.request
    resp = urllib.request.urlopen("http://localhost:9222/json")
    pages = json.loads(resp.read().decode())
    print(f"Found {len(pages)} pages")
    for p in pages[:3]:
        print(f"  - {p.get('title', 'No title')[:50]}: {p.get('id')}")
        
except Exception as e:
    print(f"CDP connection failed: {e}")
    print("Trying alternative...")

# 方法3: 直接向Chrome注入JS关闭弹窗
print("\n\nInjecting JS to close popup...")

js_script = '''
// 尝试关闭所有弹窗
var popups = document.querySelectorAll('[class*="popup"], [class*="modal"], [class*="dialog"]');
popups.forEach(function(popup) {
    var closeBtn = popup.querySelector('[class*="close"], [class*="x"], button[aria-label*="close"]');
    if (closeBtn) {
        closeBtn.click();
        console.log("Closed popup via close button");
    }
});

// 或者直接移除弹窗
var overlay = document.querySelector('[class*="overlay"], [class*="mask"]');
if (overlay) {
    overlay.style.display = 'none';
    console.log("Hid overlay");
}
'''

print("JS would be injected:")
print(js_script[:200] + "...")

# 尝试使用selenium风格的截图来识别元素
print("\n\nTaking screenshot to identify close button...")

# 保存截图供分析
from PIL import ImageGrab
img = ImageGrab.grab()
img.save(r'E:\workspace\skills\jingmai-product-publish\logs\full_screen.png')
print("Full screen saved")
