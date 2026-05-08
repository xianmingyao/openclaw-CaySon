# -*- coding: utf-8 -*-
"""
京麦 Session1 Helper - 在用户 Session (Session 1) 运行的辅助程序

功能：
- 接收命名管道命令（点击、输入、快捷键等）
- 在 Session 1 执行 Win32 操作，解决 Session 0 无法操作京麦的问题

运行方式：
- 手动启动：`python session1_helper.py`
- 或开机自启（首次运行会创建快捷方式）

依赖：
    pip install pywin32 pypiwin32
"""
import sys
import os
import time
import threading
import json
import struct
import tempfile

# 确保 pywin32 的 win32pipe 等可用
try:
    import win32pipe
    import win32file
    import win32con
    import win32api
    import win32gui
    import win32clipboard
    import win32process
except ImportError as e:
    print(f"请先安装 pywin32: pip install pywin32")
    print(f"错误: {e}")
    sys.exit(1)

PIPE_NAME = r"\\.\pipe\jingmai_session1"
RUNTIME_LOG = os.path.join(os.path.dirname(__file__), "logs", "session1_helper_runtime.log")

# 命令协议
# 发送: JSON + \n
# 接收: JSON + \n

def log(msg):
    """日志输出"""
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def runtime_log(msg):
    try:
        os.makedirs(os.path.dirname(RUNTIME_LOG), exist_ok=True)
        with open(RUNTIME_LOG, "a", encoding="utf-8") as fh:
            fh.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def release_mouse_buttons():
    try:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    except Exception:
        pass


class Session1Helper:
    """Session 1 辅助程序 - 处理来自 cli 的命令"""

    def __init__(self):
        self.running = True
        self.hwnd = None  # Helper 窗口句柄

    def _create_window(self):
        """创建隐藏窗口（用于接收消息）"""
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.lpszClassName = "JingmaiSession1Helper"
        wc.hInstance = win32api.GetModuleHandle(None)
        class_atom = win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow(
            class_atom,
            "JingmaiSession1Helper",
            win32con.WS_OVERLAPPEDWINDOW,
            0, 0, 400, 300,
            0, 0,
            wc.hInstance,
            None
        )
        win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def _handle_command(self, cmd: dict) -> dict:
        """处理命令并返回结果"""
        action = cmd.get("action", "")
        params = cmd.get("params", {})

        try:
            if action == "click":
                x = params.get("x", 0)
                y = params.get("y", 0)
                delay = params.get("delay", 0.3)
                self._click(x, y)
                time.sleep(delay)
                return {"success": True, "action": action, "x": x, "y": y}

            elif action == "type":
                text = params.get("text", "")
                interval = params.get("interval", 0.08)
                self._type_text(text, interval)
                return {"success": True, "action": action, "text": text[:20]}

            elif action == "paste":
                text = params.get("text", "")
                self._paste(text)
                return {"success": True, "action": action, "text": text[:20]}

            elif action == "hotkey":
                keys = params.get("keys", [])
                self._hotkey(keys)
                return {"success": True, "action": action, "keys": keys}

            elif action == "press":
                key = params.get("key", "")
                self._press(key)
                return {"success": True, "action": action, "key": key}

            elif action == "wait":
                seconds = params.get("seconds", 1.0)
                time.sleep(seconds)
                return {"success": True, "action": action, "waited": seconds}

            elif action == "activate_window":
                title = params.get("title", "")
                hwnd = self._find_window(title)
                if hwnd:
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.3)
                    return {"success": True, "action": action, "hwnd": hwnd}
                return {"success": False, "action": action, "error": f"窗口未找到: {title}"}

            elif action == "screenshot":
                path = params.get("path", "")
                success = self._screenshot(path)
                return {"success": success, "action": action, "path": path}

            elif action == "get_foreground":
                hwnd = win32gui.GetForegroundWindow()
                title = win32gui.GetWindowText(hwnd)
                rect = win32gui.GetWindowRect(hwnd)
                return {
                    "success": True,
                    "action": action,
                    "hwnd": hwnd,
                    "title": title,
                    "rect": rect
                }

            elif action == "find_jingmai":
                hwnd = self._find_window("jd_")
                if hwnd:
                    title = win32gui.GetWindowText(hwnd)
                    rect = win32gui.GetWindowRect(hwnd)
                    return {"success": True, "hwnd": hwnd, "title": title, "rect": rect}
                return {"success": False, "error": "京麦窗口未找到"}

            else:
                return {"success": False, "error": f"未知动作: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e), "action": action}

    def _click(self, x, y):
        """点击指定坐标"""
        release_mouse_buttons()
        try:
            import pyautogui

            runtime_log(f"click path=pyautogui x={x} y={y}")
            pyautogui.moveTo(x, y, duration=0.12)
            time.sleep(0.05)
            pyautogui.click(x, y)
        except Exception:
            runtime_log(f"click path=win32-fallback x={x} y={y}")
            win32api.SetCursorPos((x, y))
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def _type_text(self, text, interval=0.08):
        """逐字输入文本"""
        for char in text:
            code = ord(char)
            # 处理可打印ASCII
            if 32 <= code <= 126:
                vk = win32api.VkKeyScan(char)
                if vk != -1:
                    vk_code = vk & 0xFF
                    scan = win32api.MapVirtualKey(vk_code, 0)
                    win32api.keybd_event(vk_code, scan, 0, 0)
                    time.sleep(interval)
                    win32api.keybd_event(vk_code, scan, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(interval)

    def _paste(self, text):
        """剪贴板粘贴（最可靠的中文输入方式）"""
        # 保存当前剪贴板内容
        old_clipboard = ""
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                old_clipboard = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        except:
            pass
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass

        # 设置新内容
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass

        time.sleep(0.1)

        # Ctrl+V 粘贴
        vk_v = ord('V')
        scan_v = win32api.MapVirtualKey(vk_v, 0)
        win32api.keybd_event(win32api.VkKeyScan('v') & 0xFF, scan_v, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(win32api.VkKeyScan('v') & 0xFF, scan_v, win32con.KEYEVENTF_KEYUP, 0)

        time.sleep(0.2)

        # 恢复原剪贴板内容
        if old_clipboard:
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(old_clipboard, win32clipboard.CF_UNICODETEXT)
            finally:
                try:
                    win32clipboard.CloseClipboard()
                except:
                    pass

    def _hotkey(self, keys):
        """发送快捷键"""
        # keys: list of key names like ['ctrl', 'a']
        for key in keys:
            key_upper = key.upper()
            vk = win32api.VkKeyScan(key_upper)
            if vk != -1:
                vk_code = vk & 0xFF
                scan = win32api.MapVirtualKey(vk_code, 0)
                win32api.keybd_event(vk_code, scan, 0, 0)
                time.sleep(0.1)
        # 释放
        for key in reversed(keys):
            key_upper = key.upper()
            vk = win32api.VkKeyScan(key_upper)
            if vk != -1:
                vk_code = vk & 0xFF
                scan = win32api.MapVirtualKey(vk_code, 0)
                win32api.keybd_event(vk_code, scan, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)

    def _press(self, key):
        """按单个键"""
        vk_map = {
            'TAB': 0x09, 'ENTER': 0x0D, 'ESCAPE': 0x1B, 'SPACE': 0x20,
            'DELETE': 0x2E, 'BACK': 0x08, 'END': 0x23, 'HOME': 0x24,
            'LEFT': 0x25, 'UP': 0x26, 'RIGHT': 0x27, 'DOWN': 0x28,
            'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4': 0x73,
            'F5': 0x74, 'F6': 0x75, 'F7': 0x76, 'F8': 0x77,
            'A': ord('A'), 'B': ord('B'), 'C': ord('C'), 'D': ord('D'),
            'V': ord('V'),
        }
        vk = vk_map.get(key.upper())
        if vk is not None:
            scan = win32api.MapVirtualKey(vk, 0)
            win32api.keybd_event(vk, scan, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(vk, scan, win32con.KEYEVENTF_KEYUP, 0)

    def _find_window(self, title_keyword):
        """查找包含关键词的窗口"""
        result = []

        def enum_handler(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and title_keyword.lower() in title.lower():
                    results.append(hwnd)

        win32gui.EnumWindows(enum_handler, result)
        if result:
            return result[0]
        return None

    def _screenshot(self, path):
        """截图"""
        if not path:
            return False
        try:
            import win32ui
            from PIL import Image

            hwnd = win32gui.GetForegroundWindow()
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top

            hwindc = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwindc)
            saveDC = mfcDC.CreateCompatibleDC()
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(bitmap)
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

            bmpinfo = bitmap.GetInfo()
            bmpstr = bitmap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGBX', 0, 1
            )

            win32gui.DeleteObject(bitmap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwindc)

            os.makedirs(os.path.dirname(path), exist_ok=True)
            img.save(path)
            return True
        except Exception as e:
            log(f"截图失败: {e}")
            return False

    def _create_pipe_server(self):
        """创建命名管道服务器"""
        log(f"创建命名管道: {PIPE_NAME}")

        while self.running:
            try:
                pipe = win32pipe.CreateNamedPipe(
                    PIPE_NAME,
                    win32pipe.PIPE_ACCESS_DUPLEX,
                    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
                    1,  # max instances
                    65536,  # out buffer size
                    65536,  # in buffer size
                    0,  # timeout
                    None  # security
                )
                log("等待客户端连接...")
                win32pipe.ConnectNamedPipe(pipe, None)
                log("客户端已连接")

                # 读取命令
                while self.running:
                    try:
                        data = win32file.ReadFile(pipe, 65536, None)
                        if data:
                            _, received = data
                            received = received.decode('utf-8', errors='replace').strip()
                            if not received:
                                break

                            # 解析命令
                            try:
                                cmd = json.loads(received)
                                log(f"收到命令: {cmd.get('action')} {cmd.get('params', {})}")
                            except json.JSONDecodeError:
                                cmd = {"action": "raw", "params": {"data": received}}

                            # 处理命令
                            result = self._handle_command(cmd)

                            # 发送响应
                            response = json.dumps(result, ensure_ascii=False) + "\n"
                            win32file.WriteFile(pipe, response.encode('utf-8'))
                    except Exception as e:
                        log(f"管道读写错误: {e}")
                        break

                win32file.CloseHandle(pipe)
                log("管道已关闭")

            except Exception as e:
                log(f"管道创建错误: {e}")
                time.sleep(1)

    def run(self):
        """启动 Helper"""
        log("=" * 50)
        log("京麦 Session1 Helper 启动")
        log(f"Pipe: {PIPE_NAME}")
        log("=" * 50)

        # 创建窗口
        self._create_window()
        log("隐藏窗口已创建")

        # 启动管道服务器
        pipe_thread = threading.Thread(target=self._create_pipe_server, daemon=True)
        pipe_thread.start()
        log("管道服务器已启动")

        # 消息循环
        log("进入消息循环...")
        try:
            while self.running:
                win32gui.PumpWaitingMessages()
                time.sleep(0.1)
        except KeyboardInterrupt:
            log("收到中断信号")
        finally:
            self.running = False
            log("Helper 已停止")


if __name__ == "__main__":
    helper = Session1Helper()
    helper.run()
