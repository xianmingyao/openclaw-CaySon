# -*- coding: utf-8 -*-
"""
京麦 Session1 Helper 管道客户端
供 cli.py 调用，在 Session 0 中向 Session 1 的 Helper 发送命令
"""
import json
import time
import win32pipe
import win32file
import win32con
import win32api
import win32clipboard

PIPE_NAME = r"\\.\pipe\jingmai_session1"
DEFAULT_TIMEOUT = 10  # 秒


class PipeClient:
    """Named Pipe 客户端 - 连接 Session1 Helper"""

    def __init__(self, timeout=DEFAULT_TIMEOUT):
        self.timeout = timeout
        self.pipe = None

    def _connect(self):
        """连接到 Helper"""
        try:
            self.pipe = win32pipe.CreateFile(
                PIPE_NAME,
                win32con.GENERIC_READ | win32con.GENERIC_WRITE,
                0,  # no sharing
                None,
                win32con.OPEN_EXISTING,
                0,
                None
            )
            return True
        except Exception as e:
            return False

    def _send(self, cmd: dict) -> dict:
        """发送命令并等待响应"""
        if not self.pipe:
            if not self._connect():
                return {"success": False, "error": "无法连接到 Helper"}

        try:
            # 发送命令
            data = json.dumps(cmd, ensure_ascii=False) + "\n"
            win32file.WriteFile(self.pipe, data.encode('utf-8'))

            # 读取响应
            _, response = win32file.ReadFile(self.pipe, 65536, None)
            response = response.decode('utf-8', errors='replace').strip()
            if response:
                return json.loads(response)
            return {"success": False, "error": "无响应"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def close(self):
        """关闭连接"""
        if self.pipe:
            try:
                win32file.CloseHandle(self.pipe)
            except:
                pass
            self.pipe = None

    # ── 命令方法 ──

    def click(self, x, y, delay=0.3) -> dict:
        """点击坐标"""
        return self._send({"action": "click", "params": {"x": x, "y": y, "delay": delay}})

    def type_text(self, text, interval=0.08) -> dict:
        """逐字输入文本"""
        return self._send({"action": "type", "params": {"text": text, "interval": interval}})

    def paste(self, text: str) -> dict:
        """剪贴板粘贴（推荐用于中文）"""
        return self._send({"action": "paste", "params": {"text": text}})

    def hotkey(self, *keys) -> dict:
        """快捷键，如 hotkey('ctrl', 'a')"""
        return self._send({"action": "hotkey", "params": {"keys": list(keys)}})

    def press(self, key: str) -> dict:
        """按单个键，如 press('ENTER'), press('TAB')"""
        return self._send({"action": "press", "params": {"key": key}})

    def wait(self, seconds: float) -> dict:
        """等待"""
        return self._send({"action": "wait", "params": {"seconds": seconds}})

    def activate_window(self, title_keyword: str = "") -> dict:
        """激活窗口"""
        return self._send({"action": "activate_window", "params": {"title": title_keyword}})

    def find_jingmai(self) -> dict:
        """查找京麦窗口"""
        return self._send({"action": "find_jingmai"})

    def get_foreground(self) -> dict:
        """获取前台窗口"""
        return self._send({"action": "get_foreground"})

    def screenshot(self, path: str) -> dict:
        """截图"""
        return self._send({"action": "screenshot", "params": {"path": path}})

    def is_helper_running(self) -> bool:
        """检查 Helper 是否在运行"""
        result = self._send({"action": "ping", "params": {}})
        return result.get("success", False)


def create_client() -> PipeClient:
    """创建客户端（带重试）"""
    client = PipeClient(timeout=5)
    for attempt in range(3):
        if client._connect():
            return client
        time.sleep(1)
    return client
