# -*- coding: utf-8 -*-
"""
京麦商品上架 - UFO快速自动化
最小Ollama调用版本

策略：
1. 首次调用描述页面
2. 根据描述判断当前状态
3. 使用预设坐标直接点击
4. 减少Ollama调用次数
"""
import time
import tempfile
from pathlib import Path
import win32gui
import win32ui
import win32con
import win32api
import pyautogui
import requests
import sys

# 解决Windows控制台编码问题
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 配置
JINGMAI_WINDOW_TITLE = "jd_465d1abd3ee76"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3-vl:8b"

# 京东商家后台预设坐标（基于常见布局）
# 这些坐标需要根据实际京麦界面调整
PRESET_COORDS = {
    # 首页顶部导航
    "商品管理_menu": (180, 105),
    "商品管理_link": (180, 145),

    # 右侧主操作区
    "发布商品_btn": (2100, 145),
    "新建商品_btn": (2100, 185),

    # 发布流程 - 类目选择页
    "工业品_cate": (400, 280),
    "元器件_cate": (400, 350),
    "传感器_cate": (400, 420),
    "气体传感器_cate": (400, 480),
    "下一步_btn": (2200, 1000),

    # 发布流程 - 商品信息页
    "商品名称_input": (600, 380),
    "价格_input": (600, 520),
    "库存_input": (600, 600),
    "图片上传_btn": (400, 750),
    "提交_btn": (2200, 1000),
}


class SimpleJingmaiAutomator:
    def __init__(self):
        self.hwnd = None
        self.window_width = 2560
        self.window_height = 1392

    def find_window(self):
        """查找京麦窗口"""
        self.hwnd = win32gui.FindWindow(None, JINGMAI_WINDOW_TITLE)
        if self.hwnd:
            rect = win32gui.GetWindowRect(self.hwnd)
            self.window_width = rect[2] - rect[0]
            self.window_height = rect[3] - rect[1]
            print('[OK] 京麦窗口: HWND={}, 尺寸={}x{}'.format(
                self.hwnd, self.window_width, self.window_height))
            return True
        print('[FAIL] 未找到京麦窗口')
        return False

    def screenshot(self):
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

        save_path = Path(tempfile.gettempdir()) / 'jingmai_auto.png'
        bitmap.SaveBitmapFile(savedc, str(save_path))

        win32gui.DeleteObject(bitmap.GetHandle())
        savedc.DeleteDC()
        mfcdc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hwindc)

        return str(save_path)

    def describe_page(self, image_path):
        """快速描述页面（可选）"""
        try:
            img_data = Path(image_path).read_bytes()
            img_base64 = base64.b64encode(img_data).decode('utf-8')

            prompt = '这是京东商家后台的截图。用20个字描述当前页面主要内容和能看到的按钮。'

            response = requests.post(
                OLLAMA_URL,
                json={
                    'model': MODEL,
                    'prompt': prompt,
                    'images': [img_base64],
                    'stream': False
                },
                timeout=10
            )
            result = response.json()
            return result.get('response', '')
        except Exception as e:
            print('[WARN] 描述失败: {}'.format(e))
            return None

    def bring_to_front(self):
        """将窗口带到前台"""
        if self.hwnd:
            win32gui.SetForegroundWindow(self.hwnd)
            win32gui.ShowWindow(self.hwnd, 9)
            time.sleep(0.3)

    def click_preset(self, key):
        """点击预设坐标"""
        if key not in PRESET_COORDS:
            print('[WARN] 未知按键: {}'.format(key))
            return False

        x, y = PRESET_COORDS[key]
        self.bring_to_front()
        time.sleep(0.2)

        try:
            pyautogui.click(x, y, duration=0.2)
            print('[OK] 点击 {}: ({}, {})'.format(key, x, y))
            return True
        except Exception as e:
            print('[FAIL] 点击失败: {}'.format(e))
            return False

    def click_relative(self, x_percent, y_percent):
        """点击相对位置"""
        x = int(self.window_width * x_percent)
        y = int(self.window_height * y_percent)
        self.bring_to_front()
        time.sleep(0.2)

        try:
            pyautogui.click(x, y, duration=0.2)
            print('[OK] 点击相对位置: ({}, {}) = {}% x {}%'.format(x, y, x_percent, y_percent))
            return True
        except Exception as e:
            print('[FAIL] 点击失败: {}'.format(e))
            return False

    def wait(self, seconds=1):
        """等待"""
        print('[WAIT] 等待 {} 秒...'.format(seconds))
        time.sleep(seconds)

    def run_publish_flow(self, product_name, price):
        """执行发布流程"""
        print('\n' + '='*60)
        print('京麦商品上架')
        print('='*60)
        print('商品: {}'.format(product_name))
        print('价格: {}'.format(price))
        print('='*60 + '\n')

        if not self.find_window():
            return False

        # 步骤1: 点击商品管理
        print('\n[Step 1] 进入商品管理...')
        self.click_preset('商品管理_link')
        self.wait(2)

        # 步骤2: 点击发布商品
        print('\n[Step 2] 点击发布商品...')
        self.click_preset('发布商品_btn')
        self.wait(3)

        # 步骤3: 截图描述当前页面
        print('\n[Step 3] 分析当前页面...')
        screenshot = self.screenshot()
        if screenshot:
            desc = self.describe_page(screenshot)
            if desc:
                print('[INFO] 页面: {}'.format(desc[:100]))

        # 步骤4: 选择类目（根据描述判断位置）
        print('\n[Step 4] 选择类目...')
        # 默认选择工业品 > 元器件 > 传感器 > 气体传感器
        self.click_relative(0.156, 0.201)  # 工业品
        self.wait(1)
        self.click_relative(0.156, 0.251)  # 元器件
        self.wait(1)
        self.click_relative(0.156, 0.302)  # 传感器
        self.wait(1)
        self.click_relative(0.156, 0.345)  # 气体传感器
        self.wait(1)

        # 步骤5: 点击下一步
        print('\n[Step 5] 点击下一步...')
        self.click_preset('下一步_btn')
        self.wait(3)

        # 步骤6: 填写商品信息
        print('\n[Step 6] 填写商品信息...')
        # 商品名称
        self.click_preset('商品名称_input')
        pyautogui.typewrite(product_name, interval=0.1)
        self.wait(0.5)

        # 价格
        self.click_preset('价格_input')
        pyautogui.typewrite(str(price), interval=0.1)
        self.wait(0.5)

        print('\n[INFO] 基本信息已填写')
        print('[INFO] 请手动完成图片上传和最终提交')

        return True


if __name__ == "__main__":
    import base64

    automator = SimpleJingmaiAutomator()
    automator.run_publish_flow("蓝牙耳机", 299)
