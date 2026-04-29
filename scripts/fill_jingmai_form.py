import pyautogui
import time
import sys

print("脚本开始执行", file=sys.stderr)
print(f"Python: {sys.executable}", file=sys.stderr)

try:
    import win32clipboard
    import win32con
    print("win32clipboard imported", file=sys.stderr)
except Exception as e:
    print(f"win32clipboard import error: {e}", file=sys.stderr)
    sys.exit(1)

def paste_text(text):
    """通过剪贴板粘贴文本（支持中文）"""
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        print(f"paste_text('{text}') done", file=sys.stderr)
    except Exception as e:
        print(f"paste_text error: {e}", file=sys.stderr)

# 商品信息
brand = "公牛"
jd_price = "70"

try:
    print("1. 点击品牌下拉框 (378, 316)...", file=sys.stderr)
    pyautogui.click(378, 316)
    time.sleep(1.5)

    print("2. 输入品牌...", file=sys.stderr)
    paste_text(brand)
    time.sleep(1)

    print("3. 按回车确认品牌...", file=sys.stderr)
    pyautogui.press('enter')
    time.sleep(0.5)

    print("4. 点击京东价输入框 (478, 626)...", file=sys.stderr)
    pyautogui.click(478, 626)
    time.sleep(0.5)

    print("5. 清空并输入价格...", file=sys.stderr)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    paste_text(jd_price)
    time.sleep(0.5)

    print("6. 截图确认...", file=sys.stderr)
    pyautogui.screenshot("E:\\workspace\\scripts\\screenshots\\after_fill.png")
    print("截图已保存", file=sys.stderr)

    print("自动化填写完成！", file=sys.stderr)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
