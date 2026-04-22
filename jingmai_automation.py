# -*- coding: utf-8 -*-
"""
京麦商品上架 - UFO智能自动化
基于页面描述的启发式点击

工作流程：
1. 截图当前页面
2. qwen3-vl描述页面内容
3. 根据描述中的位置信息智能点击
4. 循环直到上架完成
"""
import asyncio
import base64
import json
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

# UI布局知识库 - 基于常见后台系统布局
# 格式: 描述关键词 -> 相对位置映射
UI_LAYOUTS = {
    # 首页布局
    "首页": {
        "左侧菜单": {"x_offset": 0.1, "y_offset": 0.3},
        "顶部导航": {"x_offset": 0.5, "y_offset": 0.05},
        "右侧功能": {"x_offset": 0.8, "y_offset": 0.5},
    },
    # 商品管理页面
    "商品管理": {
        "发布商品": {"x_offset": 0.8, "y_offset": 0.15},
        "新建商品": {"x_offset": 0.8, "y_offset": 0.2},
        "商品列表": {"x_offset": 0.2, "y_offset": 0.4},
    },
    # 发布页面
    "发布": {
        "下一步": {"x_offset": 0.85, "y_offset": 0.92},
        "提交": {"x_offset": 0.85, "y_offset": 0.92},
        "确认": {"x_offset": 0.85, "y_offset": 0.92},
        "保存": {"x_offset": 0.7, "y_offset": 0.92},
    }
}

# 常见按钮的典型位置（作为fallback）
COMMON_BUTTONS = {
    "发布商品": (1280, 150),
    "新建商品": (1280, 200),
    "商品管理": (150, 200),
    "下一步": (1150, 820),
    "提交": (1150, 850),
    "确认": (1150, 850),
    "保存": (1000, 850),
    "取消": (900, 850),
}


class JingmaiAutomator:
    def __init__(self):
        self.hwnd = None
        self.window_rect = None
        self.screenshot_path = None
        self.window_width = 0
        self.window_height = 0

    def find_window(self):
        """查找京麦窗口"""
        self.hwnd = win32gui.FindWindow(None, JINGMAI_WINDOW_TITLE)
        if self.hwnd:
            self.window_rect = win32gui.GetWindowRect(self.hwnd)
            self.window_width = self.window_rect[2] - self.window_rect[0]
            self.window_height = self.window_rect[3] - self.window_rect[1]
            print(f"[OK] 找到京麦窗口: HWND={self.hwnd}, 尺寸={self.window_width}x{self.window_height}")
            return True
        print("[FAIL] 未找到京麦窗口")
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

        self.screenshot_path = Path(tempfile.gettempdir()) / f"jingmai_{int(time.time())}.png"
        bitmap.SaveBitmapFile(savedc, str(self.screenshot_path))

        win32gui.DeleteObject(bitmap.GetHandle())
        savedc.DeleteDC()
        mfcdc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hwindc)

        print(f"[OK] 截图: {self.screenshot_path}")
        return str(self.screenshot_path)

    def bring_to_front(self):
        """将窗口带到前台"""
        if self.hwnd:
            win32gui.SetForegroundWindow(self.hwnd)
            win32gui.ShowWindow(self.hwnd, 9)  # SW_RESTORE
            time.sleep(0.3)

    def describe_page(self, image_path):
        """使用qwen3-vl描述页面"""
        img_data = Path(image_path).read_bytes()
        img_base64 = base64.b64encode(img_data).decode('utf-8')

        prompt = """分析这个软件截图，用中文回答：

1. 这是什么页面？（如：首页、商品管理、发布商品页面）
2. 列出所有能看到的按钮或菜单项（如：发布商品、新建商品、订单管理等）
3. 这些按钮大概在什么位置？（左上、右上、左侧、右侧、底部）

回答格式：
页面：[页面名称]
元素：[元素1]在[位置]，[元素2]在[位置]...
"""

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
            description = result.get('response', '')
            print(f"[OK] 页面描述: {description[:200]}")
            return description
        except Exception as e:
            print(f"[FAIL] 描述失败: {e}")
            return None

    def parse_description(self, description):
        """解析描述，提取页面类型和元素位置"""
        if not description:
            return None, []

        desc_lower = description.lower()
        page_type = None

        # 识别页面类型
        if '首页' in description or '主页' in description or 'dashboard' in desc_lower:
            page_type = "首页"
        elif '商品' in description and ('管理' in description or '列表' in description):
            page_type = "商品管理"
        elif '发布' in description or '新建' in description:
            page_type = "发布"
        elif '类目' in description or '分类' in description:
            page_type = "类目选择"

        # 提取元素
        elements = []
        element_keywords = [
            "发布商品", "新建商品", "商品管理", "订单管理", "库存管理",
            "下一步", "提交", "确认", "保存", "取消",
            "类目", "分类", "品牌", "型号", "价格", "图片"
        ]

        for keyword in element_keywords:
            if keyword in description:
                # 尝试提取位置信息
                pos = None
                if '左侧' in description or '左边' in description:
                    pos = 'left'
                elif '右侧' in description or '右边' in description:
                    pos = 'right'
                elif '顶部' in description or '上方' in description or '上面' in description:
                    pos = 'top'
                elif '底部' in description or '下方' in description or '下面' in description:
                    pos = 'bottom'
                elif '中间' in description or '中部' in description:
                    pos = 'center'

                elements.append((keyword, pos))

        return page_type, elements

    def calculate_click_position(self, element_name, page_type=None, position_hint=None):
        """计算点击坐标"""
        # 基础位置：窗口右下角（发布按钮通常在那里）
        base_x = int(self.window_width * 0.85)
        base_y = int(self.window_height * 0.92)

        # 根据元素名称调整
        element_lower = element_name.lower()

        if '发布商品' in element_name or '新建' in element_name:
            base_x = int(self.window_width * 0.8)
            base_y = int(self.window_height * 0.15)
        elif '下一步' in element_name or '提交' in element_name or '确认' in element_name:
            base_x = int(self.window_width * 0.88)
            base_y = int(self.window_height * 0.93)
        elif '商品管理' in element_name:
            base_x = int(self.window_width * 0.1)
            base_y = int(self.window_height * 0.25)
        elif '类目' in element_name or '分类' in element_name:
            base_x = int(self.window_width * 0.3)
            base_y = int(self.window_height * 0.35)
        elif '价格' in element_name:
            base_x = int(self.window_width * 0.4)
            base_y = int(self.window_height * 0.45)
        elif '图片' in element_name:
            base_x = int(self.window_width * 0.5)
            base_y = int(self.window_height * 0.35)

        # 根据位置提示微调
        if position_hint == 'left':
            base_x = int(self.window_width * 0.15)
        elif position_hint == 'right':
            base_x = int(self.window_width * 0.85)
        elif position_hint == 'top':
            base_y = int(self.window_height * 0.1)
        elif position_hint == 'bottom':
            base_y = int(self.window_height * 0.9)
        elif position_hint == 'center':
            base_x = int(self.window_width * 0.5)
            base_y = int(self.window_height * 0.5)

        return base_x, base_y

    def click(self, x, y, button='left'):
        """点击指定坐标"""
        if not self.hwnd:
            return False

        self.bring_to_front()
        time.sleep(0.2)

        # 使用pyautogui点击（更可靠）
        try:
            pyautogui.click(x, y, button=button, duration=0.2)
            print(f"[OK] 点击: ({x}, {y})")
            return True
        except Exception as e:
            print(f"[FAIL] 点击失败: {e}")
            return False

    def click_element(self, element_name, page_type=None, position_hint=None):
        """根据元素名称智能点击"""
        x, y = self.calculate_click_position(element_name, page_type, position_hint)
        return self.click(x, y)

    def wait_for_page_load(self, seconds=2):
        """等待页面加载"""
        print(f"[WAIT] 等待 {seconds} 秒...")
        time.sleep(seconds)

    def run_workflow(self, product_info):
        """执行上架工作流"""
        print(f"\n{'='*60}")
        print(f"京麦商品上架自动化")
        print(f"{'='*60}")
        print(f"商品: {product_info}")
        print(f"{'='*60}\n")

        # 1. 查找窗口
        if not self.find_window():
            print("请先启动京麦应用")
            return False

        # 2. 工作流程 - 基于状态的自动化
        workflow = [
            {"step": 1, "name": "找到发布入口", "target": "发布商品"},
            {"step": 2, "name": "点击发布商品", "target": "发布商品"},
            {"step": 3, "name": "选择类目", "target": "下一步"},
            {"step": 4, "name": "填写商品信息", "target": "价格"},
            {"step": 5, "name": "上传图片", "target": "图片"},
            {"step": 6, "name": "提交商品", "target": "提交"},
        ]

        current_step = 0
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- 第 {iteration} 次迭代 ---")

            # 截图
            screenshot = self.screenshot()
            if not screenshot:
                break

            # 描述页面
            description = self.describe_page(screenshot)
            if description:
                page_type, elements = self.parse_description(description)
                print(f"[INFO] 页面类型: {page_type}, 检测到元素: {[e[0] for e in elements]}")

                # 检查是否完成
                if '成功' in description or '完成' in description:
                    print("\n[OK] 上架流程完成!")
                    return True

                # 根据当前状态决定下一步
                if current_step < len(workflow):
                    next_action = workflow[current_step]
                    target = next_action["target"]
                    print(f"[INFO] 下一步: {next_action['name']} -> {target}")

                    # 查找位置提示
                    pos_hint = None
                    for elem_name, elem_pos in elements:
                        if elem_name in target or target in elem_name:
                            pos_hint = elem_pos
                            break

                    # 点击目标元素
                    if self.click_element(target, page_type, pos_hint):
                        current_step += 1
                        self.wait_for_page_load()

                        # 如果是点击发布商品，尝试直接点击
                        if target == "发布商品":
                            # 尝试点击更可能的位置
                            pyautogui.click(int(self.window_width * 0.75), int(self.window_height * 0.08))
                            current_step += 1
                else:
                    # 所有步骤完成，检查是否成功
                    print("[INFO] 工作流步骤完成，等待页面响应...")
                    self.wait_for_page_load(3)
            else:
                print("[WARN] 无法描述页面，尝试点击常见位置")
                # Fallback: 点击常见位置
                pyautogui.click(1280, 150)  # 发布商品位置
                self.wait_for_page_load()

        print(f"\n[INFO] 完成 {iteration} 次迭代")
        return False


if __name__ == "__main__":
    automator = JingmaiAutomator()
    automator.run_workflow("蓝牙耳机 299元")
