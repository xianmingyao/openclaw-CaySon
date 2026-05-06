"""
京麦商品发布自动化 - 元素定位器
智能元素定位 + 坐标fallback双重保障
"""
import sys
import time
import ctypes
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass

# 尝试导入win32gui
try:
    import win32gui
    import win32con
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("[WARN] win32gui not available, running in simulation mode")


@dataclass
class WindowInfo:
    """窗口信息"""
    hwnd: int
    title: str
    rect: Tuple[int, int, int, int]  # left, top, right, bottom
    width: int
    height: int
    is_visible: bool


@dataclass
class ElementPosition:
    """元素位置"""
    x: int  # 相对窗口的X坐标
    y: int  # 相对窗口的Y坐标
    width: int = 0
    height: int = 0
    confidence: float = 1.0  # 匹配置信度
    method: str = "fallback"  # 定位方法


class JingmaiLocator:
    """京麦元素定位器"""
    
    # 京麦窗口标题关键词
    WINDOW_TITLES = [
        'jd_465d1abd3ee76',  # 京麦主窗口
        '京麦',
        '京东商家',
        'jd售卖',
    ]
    
    # 左侧菜单坐标（相对窗口）
    MENU_COORDS = {
        '商品': (34, 145),
        '商品管理': (34, 170),
        '发布商品': (34, 195),
        '我的商品': (34, 220),
        '库存': (34, 245),
        '订单': (120, 145),
        '物流': (120, 170),
        '售后': (120, 195),
        '客服': (120, 220),
    }
    
    def __init__(self, log=None):
        self.log = log
        self.hwnd: Optional[int] = None
        self.window_rect: Optional[Tuple[int, int, int, int]] = None
        
    def _log(self, level: str, msg: str):
        """日志辅助"""
        if self.log:
            getattr(self.log, level.lower())(msg)
        else:
            print(f"[{level}] {msg}")
    
    # ==================== 窗口操作 ====================
    
    def find_window(self) -> Optional[WindowInfo]:
        """查找京麦窗口"""
        self._log('info', "查找京麦窗口...")
        
        if not WIN32_AVAILABLE:
            self._log('warn', "win32gui不可用，返回模拟窗口")
            return WindowInfo(
                hwnd=0,
                title="模拟窗口",
                rect=(100, 100, 1380, 900),
                width=1280,
                height=700,
                is_visible=True
            )
        
        # 方法1：精确查找
        for title in self.WINDOW_TITLES:
            hwnd = win32gui.FindWindow(None, title)
            if hwnd:
                return self._get_window_info(hwnd)
        
        # 方法2：枚举查找
        result = []
        def enum_handler(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    for keyword in self.WINDOW_TITLES:
                        if keyword.lower() in title.lower():
                            results.append(hwnd)
                            break
        win32gui.EnumWindows(enum_handler, result)
        
        if result:
            return self._get_window_info(result[0])
        
        self._log('error', "未找到京麦窗口")
        return None
    
    def _get_window_info(self, hwnd: int) -> WindowInfo:
        """获取窗口详细信息"""
        title = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        left, top, right, bottom = rect
        width = right - left
        height = bottom - top
        is_visible = win32gui.IsWindowVisible(hwnd)
        
        self.hwnd = hwnd
        self.window_rect = rect
        
        return WindowInfo(
            hwnd=hwnd,
            title=title,
            rect=rect,
            width=width,
            height=height,
            is_visible=is_visible
        )
    
    def activate_window(self) -> bool:
        """激活并调整窗口"""
        if not self.hwnd or not WIN32_AVAILABLE:
            return True
        
        try:
            # 恢复最小化窗口
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            time.sleep(0.2)
            
            # 调整窗口位置和大小
            win32gui.SetWindowPos(
                self.hwnd, 0,
                100, 100, 1280, 800,
                0
            )
            time.sleep(0.2)
            
            # 置顶
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.3)
            
            # 刷新窗口信息
            self.window_rect = win32gui.GetWindowRect(self.hwnd)
            
            self._log('ok', f"窗口已激活: {self.window_rect}")
            return True
            
        except Exception as e:
            self._log('error', f"窗口激活失败: {e}")
            return False
    
    def window_to_screen(self, x: int, y: int) -> Tuple[int, int]:
        """窗口坐标转屏幕坐标"""
        if not self.window_rect:
            return x, y
        left, top = self.window_rect[0], self.window_rect[1]
        return left + x, top + y
    
    def screen_to_window(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """屏幕坐标转窗口坐标"""
        if not self.window_rect:
            return screen_x, screen_y
        left, top = self.window_rect[0], self.window_rect[1]
        return screen_x - left, screen_y - top
    
    # ==================== 点击操作 ====================
    
    def click(self, x: int, y: int, delay: float = 0.5) -> bool:
        """在窗口坐标处点击"""
        if not WIN32_AVAILABLE:
            self._log('debug', f"[模拟] 点击窗口坐标 ({x}, {y})")
            time.sleep(delay)
            return True
            
        if not self.hwnd:
            self._log('error', "窗口未找到，无法点击")
            return False
        
        try:
            # 确保窗口在前台
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.1)
            
            # 转换为屏幕坐标
            screen_x, screen_y = self.window_to_screen(x, y)
            
            # 移动鼠标
            win32api.SetCursorPos((screen_x, screen_y))
            time.sleep(0.05)
            
            # 点击
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            
            self._log('debug', f"点击屏幕坐标 ({screen_x}, {screen_y}) -> 窗口({x}, {y})")
            time.sleep(delay)
            return True
            
        except Exception as e:
            self._log('error', f"点击失败: {e}")
            return False
    
    def double_click(self, x: int, y: int, delay: float = 0.5) -> bool:
        """双击"""
        if not WIN32_AVAILABLE:
            self._log('debug', f"[模拟] 双击窗口坐标 ({x}, {y})")
            time.sleep(delay)
            return True
            
        if not self.hwnd:
            return False
        
        try:
            win32gui.SetForegroundWindow(self.hwnd)
            screen_x, screen_y = self.window_to_screen(x, y)
            win32api.SetCursorPos((screen_x, screen_y))
            time.sleep(0.05)
            
            # 双击
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(0.1)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            
            time.sleep(delay)
            return True
        except Exception as e:
            self._log('error', f"双击失败: {e}")
            return False
    
    def right_click(self, x: int, y: int, delay: float = 0.5) -> bool:
        """右键点击"""
        if not WIN32_AVAILABLE:
            self._log('debug', f"[模拟] 右键点击窗口坐标 ({x}, {y})")
            time.sleep(delay)
            return True
            
        if not self.hwnd:
            return False
        
        try:
            win32gui.SetForegroundWindow(self.hwnd)
            screen_x, screen_y = self.window_to_screen(x, y)
            win32api.SetCursorPos((screen_x, screen_y))
            time.sleep(0.05)
            
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            
            time.sleep(delay)
            return True
        except Exception as e:
            self._log('error', f"右键点击失败: {e}")
            return False
    
    # ==================== 键盘操作 ====================
    
    def type_text(self, text: str, delay: float = 0.1) -> bool:
        """输入文本"""
        if not WIN32_AVAILABLE:
            self._log('debug', f"[模拟] 输入文本: {text}")
            time.sleep(len(text) * delay)
            return True
            
        if not self.hwnd:
            return False
        
        try:
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.2)
            
            for char in text:
                # 发送字符
                win32api.SendMessage(
                    self.hwnd, win32con.WM_CHAR,
                    ord(char), 0
                )
                time.sleep(delay)
            
            self._log('debug', f"输入文本: {text[:20]}...")
            return True
        except Exception as e:
            self._log('error', f"输入文本失败: {e}")
            return False
    
    def press_key(self, vk_code: int, delay: float = 0.1) -> bool:
        """按键"""
        if not WIN32_AVAILABLE:
            self._log('debug', f"[模拟] 按键: {vk_code}")
            time.sleep(delay)
            return True
            
        if not self.hwnd:
            return False
        
        try:
            win32gui.SetForegroundWindow(self.hwnd)
            win32api.keybd_event(vk_code, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(delay)
            return True
        except Exception as e:
            self._log('error', f"按键失败: {e}")
            return False
    
    def press_enter(self, delay: float = 0.3) -> bool:
        """按回车"""
        return self.press_key(0x0D, delay)  # VK_RETURN
    
    def press_tab(self, delay: float = 0.3) -> bool:
        """按Tab"""
        return self.press_key(0x09, delay)  # VK_TAB
    
    def press_escape(self, delay: float = 0.3) -> bool:
        """按Escape"""
        return self.press_key(0x1B, delay)  # VK_ESCAPE
    
    # ==================== 预定义菜单导航 ====================
    
    def click_menu(self, menu_name: str, delay: float = 1.0) -> bool:
        """点击左侧菜单"""
        coords = self.MENU_COORDS.get(menu_name)
        if coords:
            self._log('info', f"点击菜单「{menu_name}」坐标 {coords}")
            return self.click(coords[0], coords[1], delay)
        else:
            self._log('warn', f"未知菜单: {menu_name}")
            return False
    
    def navigate_to_publish(self) -> bool:
        """导航到发布商品页面"""
        self._log('step', "导航到发布商品页面")
        
        # 步骤1：点击商品菜单
        self._log('sub', "点击「商品」菜单")
        if not self.click_menu('商品'):
            return False
        
        # 步骤2：点击发布商品
        self._log('sub', "点击「发布商品」子菜单")
        if not self.click_menu('发布商品', delay=2.0):
            return False
        
        self._log('ok', "已进入发布商品页面")
        return True


if __name__ == "__main__":
    # 测试定位器
    from jingmai_logger import init_logger
    
    log = init_logger("locator_test")
    locator = JingmaiLocator(log)
    
    log.header("元素定位器测试")
    
    # 查找窗口
    window_info = locator.find_window()
    if window_info:
        log.ok(f"找到窗口: {window_info.title}")
        log.info(f"  句柄: {window_info.hwnd}")
        log.info(f"  位置: {window_info.rect}")
        log.info(f"  大小: {window_info.width}x{window_info.height}")
        
        # 激活窗口
        locator.activate_window()
        
        # 测试点击
        log.info("测试点击商品菜单...")
        locator.click_menu('商品')
        time.sleep(1)
        
        log.info("测试点击发布商品...")
        locator.click_menu('发布商品')
    else:
        log.error("未找到窗口，测试终止")
