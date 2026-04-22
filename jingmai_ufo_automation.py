# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
京麦商品上架 - UFO直接自动化
基于截图描述的智能点击

原理：
1. 截取京麦窗口
2. 用qwen3-vl描述截图内容
3. 根据描述定位元素并点击
4. 循环直到完成上架
"""
import asyncio
import base64
import json
import time
import win32gui
import win32ui
import win32con
from pathlib import Path
from PIL import Image
import requests
import sys
sys.path.insert(0, r'E:\workspace\skills\desktop-control-cli\desktop-control')

# 配置文件
JINGMAI_WINDOW_TITLE = "jd_465d1abd3ee76"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3-vl:8b"

class JingmaiAutomator:
    def __init__(self):
        self.hwnd = None
        self.screenshot_path = None

    def find_window(self):
        """查找京麦窗口"""
        self.hwnd = win32gui.FindWindow(None, JINGMAI_WINDOW_TITLE)
        if self.hwnd:
            print(f"✅ 找到京麦窗口: HWND={self.hwnd}")
            return True
        else:
            print("❌ 未找到京麦窗口")
            return False

    def screenshot(self, save_path=None):
        """截取窗口截图"""
        if not self.hwnd:
            return None

        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        width = right - left
        height = bottom - top

        hwindc = win32gui.GetWindowDC(self.hwnd)
        mfcdc = win32ui.CreateDCFromHandle(hwindc)
        savedc = mfcdc.CreateCompatibleDC()
        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfcdc, width, height)
        savedc.SelectObject(bitmap)
        savedc.BitBlt((0, 0), (width, height), mfcdc, (0, 0), win32con.SRCCOPY)

        if save_path is None:
            save_path = Path(tempfile.gettempdir()) / "jingmai_screenshot.png"

        bitmap.SaveBitmapFile(savedc, str(save_path))

        win32gui.DeleteObject(bitmap.GetHandle())
        savedc.DeleteDC()
        mfcdc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hwindc)

        self.screenshot_path = save_path
        print(f"📸 截图保存: {save_path}")
        return save_path

    def describe_screenshot(self, image_path):
        """使用qwen3-vl描述截图"""
        img_data = Path(image_path).read_bytes()
        img_base64 = base64.b64encode(img_data).decode('utf-8')

        prompt = '''Describe this screenshot briefly in Chinese. Focus on:
1. What page/screen is shown
2. Where are the main buttons/menus located (top, bottom, left, right)
3. Any prominent action buttons visible

Respond in 50 words or less, in Chinese.'''

        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    'model': MODEL,
                    'prompt': prompt,
                    'images': [img_base64],
                    'stream': False
                },
                timeout=15
            )
            result = response.json()
            return result.get('response', '')
        except Exception as e:
            print(f"❌ 描述失败: {e}")
            return None

    def find_element_by_description(self, description, target_element):
        """
        根据描述推断元素位置
        返回: (x, y) 坐标或None
        """
        # 这是一个简化的实现 - 实际使用时需要根据具体UI调整
        desc_lower = description.lower()

        # 基于描述的启发式定位
        # 实际项目中应该结合UI布局知识
        common_positions = {
            '商品管理': (200, 100),
            '发布商品': (400, 100),
            '新建商品': (350, 150),
            '下一步': (1200, 800),
            '提交': (1200, 850),
            '确认': (1200, 850),
        }

        # 检查描述中是否提到目标元素
        if target_element in desc_lower or any(char in desc_lower for char in ['menu', 'button', '按钮', '菜单']):
            # 返回默认位置（实际需要根据UI调整）
            return common_positions.get(target_element, (800, 500))

        return None

    def click(self, x, y):
        """发送点击事件"""
        if not self.hwnd:
            return False

        # 先将窗口带到前台
        win32gui.SetForegroundWindow(self.hwnd)

        # 发送鼠标点击
        import win32api
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

        print(f"🖱️ 点击: ({x}, {y})")
        return True

    def run(self, product_name, category, price):
        """运行自动化流程"""
        print(f"\n{'='*60}")
        print(f"🚀 京麦商品上架自动化")
        print(f"{'='*60}")
        print(f"商品: {product_name}")
        print(f"分类: {category}")
        print(f"价格: {price}")
        print(f"{'='*60}\n")

        # 1. 查找窗口
        if not self.find_window():
            print("请先启动京麦应用")
            return False

        # 2. 截取当前屏幕
        screenshot = self.screenshot()
        if not screenshot:
            return False

        # 3. 描述当前页面
        print("\n🔍 分析当前页面...")
        description = self.describe_screenshot(screenshot)
        if description:
            print(f"📝 页面描述: {description}")
        else:
            print("⚠️ 无法描述页面")

        # 4. 智能决策
        print("\n🤖 智能决策中...")
        # 这里应该根据描述判断当前页面，决定下一步操作
        # 实际实现需要更复杂的逻辑

        print("\n✅ 自动化流程演示完成")
        print("注意: 实际元素定位需要结合具体UI布局知识")
        return True

if __name__ == "__main__":
    import tempfile

    automator = JingmaiAutomator()

    # 测试流程
    automator.run(
        product_name="蓝牙耳机",
        category="数码配件",
        price=299
    )
