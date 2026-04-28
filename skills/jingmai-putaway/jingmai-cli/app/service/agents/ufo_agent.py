#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UFO 自动化 Agent (v2)

参考 Agent-S (Simular AI) 架构改进:
- 截图捕获 → 多模态消息 → VLM 结构化推理管道
- 逐步反思: 操作前后截图对比, 循环检测

参考 Datawhale China 第四章 ReAct/Plan-and-Solve/Reflection 范式:
- ReAct: Thought-Action-Observation 动态循环
- Plan-and-Solve: 任务分解 + 步骤化执行
- Reflection: 执行-反思-优化迭代循环
"""
import json
import re
import sys
import asyncio
import base64
import io
import os
import random
import hashlib
import subprocess
import ctypes
import ctypes.wintypes
from datetime import datetime
from pathlib import Path
import pyautogui
import pyperclip
from typing import Optional, Dict, Any, List, Tuple
from loguru import logger
from PIL import Image as PILImage

# Win32 DPI 感知: 确保坐标系统一致 (在 import 时执行一次)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per Monitor V2
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from config import settings
from models.task import Task
from app.service.agents.base import BaseAgent
from app.service.llm.manager import LLMManager
from app.service.skills.skill_loader import SkillLoader
from app.service.skills.runtime_bridge import SkillRuntimeBridge
from app.service.utils.session_detector import SessionDetector
from app.service.utils.resource_path import get_resource_path


# UFO 标准可执行 Action 列表
UFO_AVAILABLE_ACTIONS = [
    {
        "name": "click",
        "description": "点击指定屏幕坐标 (x, y)",
        "params": ["x", "y", "button"],
    },
    {
        "name": "double_click",
        "description": "双击指定屏幕坐标 (x, y)",
        "params": ["x", "y"],
    },
    {
        "name": "type",
        "description": "使用 pyautogui 直接输入文本",
        "params": ["text", "interval"],
    },
    {
        "name": "set_edit_text",
        "description": "向文本框输入内容（先点击聚焦再输入）",
        "params": ["text", "clear_current_text"],
    },
    {
        "name": "keyboard_input",
        "description": "模拟键盘按键组合，如 Ctrl+C, Alt+Tab",
        "params": ["keys"],
    },
    {
        "name": "keypress",
        "description": "按下并释放单个按键",
        "params": ["keys"],
    },
    {
        "name": "scroll",
        "description": "在指定坐标处滚动鼠标滚轮",
        "params": ["scroll_x", "scroll_y", "x", "y"],
    },
    {
        "name": "move",
        "description": "移动鼠标到指定屏幕坐标",
        "params": ["x", "y"],
    },
    {
        "name": "drag",
        "description": "从起点拖拽到终点",
        "params": ["start_x", "start_y", "end_x", "end_y", "duration"],
    },
    {
        "name": "wait",
        "description": "等待指定秒数",
        "params": ["seconds"],
    },
    {
        "name": "run_command",
        "description": "执行系统命令（cmd/powershell），用于进程检测、应用启动等系统级操作",
        "params": ["command", "shell"],
    },
    {
        "name": "check_process",
        "description": "检查指定进程是否正在运行，返回进程信息",
        "params": ["process_name"],
    },
    {
        "name": "open_app",
        "description": "打开或切换到指定应用程序（自动检测进程、任务栏、系统托盘）",
        "params": ["app_name", "search_keyword"],
    },
    # ===== UFO 原生控件级 Actions (复刻 UFO API) =====
    {
        "name": "click_input",
        "description": "控件级点击，支持双击和修饰键（先聚焦再点击，适用于精确控件操作）",
        "params": ["x", "y", "button", "double", "pressed"],
    },
    {
        "name": "click_on_coordinates",
        "description": "分数坐标点击，坐标为相对于截图的归一化值 (0.0~1.0)，适合在不同分辨率下精确定位",
        "params": ["frac_x", "frac_y", "button", "double"],
    },
    {
        "name": "drag_on_coordinates",
        "description": "分数坐标拖拽，支持按住修饰键拖拽（如 Shift 选择区域）",
        "params": ["start_frac_x", "start_frac_y", "end_frac_x", "end_frac_y", "duration", "button", "key_hold"],
    },
    {
        "name": "wheel_mouse_input",
        "description": "鼠标滚轮滚动，不需要指定坐标（在当前鼠标位置滚动）",
        "params": ["wheel_dist"],
    },
    {
        "name": "texts",
        "description": "获取当前聚焦控件中的文本内容（通过剪贴板复制获取选中文本）",
        "params": [],
    },
    {
        "name": "summary",
        "description": "视觉摘要，让 LLM 对当前截图进行文字描述（用于信息获取和理解界面状态）",
        "params": ["text"],
    },
    {
        "name": "annotation",
        "description": "控件标注，标注界面中指定编号的控件（用于精确识别 UI 元素）",
        "params": ["control_labels"],
    },
    {
        "name": "no_action",
        "description": "空操作，不执行任何动作（用于步骤占位或跳过）",
        "params": [],
    },
]


class UFOAgent(BaseAgent):
    """
    UFO 自动化 Agent v2

    改进点:
    1. 截图管道: observe() 真实截图 + 多模态 LLM 分析 (Agent-S)
    2. 程序性记忆: 动态 Action 签名注入系统提示 (Agent-S)
    3. ReAct 历史: Thought-Action-Observation 轨迹累积 (Datawhale Ch4)
    4. 逐步反思: 循环检测 + 操作效果验证 (Agent-S + Datawhale Reflection)
    5. Plan-and-Solve: 初始任务分解 (Datawhale Ch4)
    """

    def __init__(self, llm_manager: LLMManager):
        super().__init__(llm_manager)

        # pyautogui 安全设置
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = True

        # 当前屏幕分辨率缓存
        self._screen_size: Tuple[int, int] = (0, 0)
        self._refresh_screen_size()

        # 操作前截图 (用于 Agent-S 逐步反思对比)
        self._pre_action_screenshot: Optional[PILImage.Image] = None
        # 操作后截图 (用于 reflect 阶段视觉验证)
        self._post_action_screenshot: Optional[PILImage.Image] = None
        # Agent-S: 截图缩放比例 (screenshot_coord / scale = screen_coord)
        self._screenshot_scale: float = 1.0
        self._screenshot_size: Tuple[int, int] = self._screen_size

        # 窗口上下文跟踪 (用于 ReAct 坐标分析的智能裁剪)
        self._active_window_rect: Optional[Tuple[int, int, int, int]] = None  # (left, top, right, bottom) 屏幕坐标
        self._active_window_title: str = ""

        # 步骤记录 (ReAct 历史轨迹 + 循环检测)
        self._step_records: List[Dict[str, Any]] = []

        # 技能内容缓存 (从 SKILL.md 加载，用于 prompt 注入)
        self._skill_content: str = ""
        self._skill_loader = SkillLoader()
        self._skill_loaded: bool = False

        # 系统提示词指导文件 (从 opinion.md 加载，作为总结意见和约束规则)
        self._opinion_content: str = ""
        self._opinion_loaded: bool = False

        # 特殊场景处理文件 (从 special.md 加载，针对特定任务的特殊指导)
        self._special_content: str = ""
        self._special_loaded: bool = False

        # Session 检测器（延迟初始化，仅在 Windows 上启用）
        self._session_detector: Optional[SessionDetector] = None

    async def _ensure_skills_loaded(self):
        """确保技能已加载 (延迟加载，首次调用时触发)"""
        if self._skill_loaded:
            return
        self._skill_loaded = True
        try:
            await self._skill_loader.initialize()
            skills = await self._skill_loader.load_builtin_skills()
            for skill in skills:
                if skill.content:
                    self._skill_content += f"\n\n{skill.content}"
                    logger.info(f"[UFOAgent] 加载技能 '{skill.name}', content={len(skill.content)} chars")
            if self._skill_content:
                logger.info(f"[UFOAgent] 技能内容总长度: {len(self._skill_content)} chars")
            else:
                logger.warning("[UFOAgent] 未加载到任何技能内容，将使用内置 Action 列表")
        except Exception as e:
            logger.error(f"[UFOAgent] 技能加载失败: {e}，将使用内置 Action 列表")

    def _load_opinion_content(self):
        """加载系统提示词指导文件 (opinion.md)"""
        if self._opinion_loaded:
            return
        self._opinion_loaded = True
        try:
            opinion_path = get_resource_path("resources/harness/opinion.md")
            if opinion_path.exists():
                with open(opinion_path, "r", encoding="utf-8") as f:
                    self._opinion_content = f.read()
                logger.info(f"[UFOAgent] 加载 opinion.md 成功, content={len(self._opinion_content)} chars")
            else:
                logger.warning(f"[UFOAgent] opinion.md 文件不存在: {opinion_path}")
        except Exception as e:
            logger.error(f"[UFOAgent] 加载 opinion.md 失败: {e}")

    def _load_special_content(self):
        """加载特殊场景处理文件 (special.md)"""
        if self._special_loaded:
            return
        self._special_loaded = True
        try:
            special_path = get_resource_path("resources/harness/special.md")
            if special_path.exists():
                with open(special_path, "r", encoding="utf-8") as f:
                    self._special_content = f.read()
                logger.info(f"[UFOAgent] 加载 special.md 成功, content={len(self._special_content)} chars")
            else:
                logger.warning(f"[UFOAgent] special.md 文件不存在: {special_path}")
        except Exception as e:
            logger.error(f"[UFOAgent] 加载 special.md 失败: {e}")

    def _refresh_screen_size(self):
        """刷新屏幕分辨率缓存"""
        try:
            self._screen_size = pyautogui.size()
            logger.debug(f"[UFOAgent] 屏幕分辨率: {self._screen_size[0]}x{self._screen_size[1]}")
        except Exception as e:
            logger.warning(f"[UFOAgent] 获取屏幕分辨率失败: {e}")

    # ==================== Session 对齐管理 ====================

    def _get_session_detector(self) -> Optional[SessionDetector]:
        """获取 Session 检测器实例（仅 Windows）"""
        if self._session_detector is None and sys.platform == 'win32':
            try:
                self._session_detector = SessionDetector()
            except Exception as e:
                logger.warning(f"[UFOAgent] SessionDetector 初始化失败: {e}")
        return self._session_detector

    async def _ensure_session_alignment(self, task: Task) -> bool:
        """
        执行前确保 Session 对齐。

        检查逻辑：
        1. 京麦在运行且同 Session → True
        2. 京麦在运行但不同 Session → 尝试在当前 Session 启动
        3. 京麦未运行 → 尝试启动
        """
        detector = self._get_session_detector()
        if detector is None:
            return True  # 非 Windows 环境，跳过检查

        target_process = settings.TARGET_APP_PROCESS
        current_session = detector.detect_current_session()
        target_session = detector.find_process_session(target_process)

        # 场景 1：目标进程与 Agent 在同一 Session
        if target_session is not None and target_session == current_session:
            logger.info(f"[UFOAgent] {target_process} 与 Agent 在同一 Session ({current_session})")
            return True

        # 场景 2：目标进程在其他 Session
        if target_session is not None and target_session != current_session:
            logger.warning(
                f"[UFOAgent] {target_process} 在 Session {target_session}，"
                f"Agent 在 Session {current_session}"
            )
            if settings.SESSION_MODE == "force_same":
                return False
            # auto 模式：尝试在当前 Session 启动目标应用
            launched = detector.try_launch_in_target_session(target_process, current_session)
            if launched:
                await asyncio.sleep(5)
                new_session = detector.find_process_session(target_process)
                if new_session == current_session:
                    logger.info(f"[UFOAgent] {target_process} 已在 Session {current_session} 启动")
                    return True
            logger.warning(f"[UFOAgent] 无法在 Session {current_session} 启动 {target_process}，继续执行（可能失败）")
            return True  # auto 模式不阻塞

        # 场景 3：目标进程未运行
        logger.info(f"[UFOAgent] {target_process} 未运行，尝试启动...")
        launched = self._try_launch_jingmai(target_process)
        return launched

    def _try_launch_jingmai(self, process_name: str) -> bool:
        """
        启动目标应用并等待窗口就绪。

        查找安装路径 → Popen 启动 → 轮询 tasklist 确认启动成功。
        """
        import time

        # 常见京麦安装路径
        possible_paths = [
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Jingmai", process_name),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Jingmai", process_name),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Jingmai", process_name),
            process_name,  # 尝试 PATH 查找
        ]

        exe_path = None
        for path in possible_paths:
            if path and os.path.isfile(path):
                exe_path = path
                break

        if exe_path is None:
            # 最后尝试 where 命令
            try:
                result = subprocess.run(
                    ["where", process_name],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0:
                    exe_path = result.stdout.strip().split("\n")[0]
            except Exception:
                pass

        if exe_path is None:
            logger.warning(f"[UFOAgent] 未找到 {process_name} 的安装路径")
            return False

        try:
            subprocess.Popen(
                [exe_path],
                creationflags=subprocess.DETACHED_PROCESS if sys.platform == 'win32' else 0,
            )
            logger.info(f"[UFOAgent] 已启动 {exe_path}")
        except Exception as e:
            logger.error(f"[UFOAgent] 启动 {exe_path} 失败: {e}")
            return False

        # 轮询等待进程出现（最多 30 秒）
        detector = self._get_session_detector()
        for i in range(15):
            time.sleep(2)
            session = detector.find_process_session(process_name) if detector else None
            if session is not None:
                logger.info(f"[UFOAgent] {process_name} 已在 Session {session} 运行")
                return True
            logger.debug(f"[UFOAgent] 等待 {process_name} 启动... ({i+1}/15)")

        logger.warning(f"[UFOAgent] {process_name} 启动超时（30 秒内未检测到进程）")
        return False

    async def execute(self, task, session, max_steps=10, context=None):
        """重写 execute，在 ReAct 循环前做 Session 对齐检查"""
        if self._get_session_detector() is not None:
            try:
                aligned = await self._ensure_session_alignment(task)
                if not aligned and settings.SESSION_MODE == "force_same":
                    from models.agent import AgentExecution, ExecutionState
                    from utils.helpers import generate_id
                    execution = AgentExecution(
                        id=generate_id("exec"),
                        task_id=task.id,
                        agent_type=self.__class__.__name__,
                        state=ExecutionState.FAILED,
                        error_message="Session 不对齐且 SESSION_MODE=force_same",
                        started_at=datetime.utcnow(),
                    )
                    session.add(execution)
                    await session.flush()
                    return execution
            except Exception as e:
                logger.warning(f"[UFOAgent] Session 检查异常（不影响执行）: {e}")

        return await super().execute(task, session, max_steps=max_steps, context=context)

    def _exec_id(self) -> str:
        """获取当前执行 ID"""
        execution = self.get_execution()
        return execution.id if execution else "unknown"

    # ==================== 窗口上下文管理 (智能裁剪) ====================

    def _update_window_context(self) -> bool:
        """
        获取当前前台窗口的边界和标题 (屏幕坐标空间)

        Returns:
            bool: 是否成功获取有效的窗口信息
        """
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                logger.warning("[UFOAgent] GetForegroundWindow 返回空句柄")
                return False

            rect = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.pointer(rect))

            left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
            w, h = right - left, bottom - top

            if w < 100 or h < 100:
                logger.warning(f"[UFOAgent] 窗口区域异常: ({w}x{h})，跳过裁剪")
                return False

            # 确保窗口在屏幕范围内 (允许 -10px 偏移，这是窗口阴影/边框的常见行为)
            sw, sh = self._screen_size
            if left < -10 or top < -10 or right > sw * 2 or bottom > sh * 2:
                logger.warning(f"[UFOAgent] 窗口坐标超出屏幕范围: ({left},{top})-({right},{bottom}), 屏幕={sw}x{sh}")
                return False

            self._active_window_rect = (left, top, right, bottom)

            # 获取窗口标题
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            self._active_window_title = buf.value

            logger.info(f"[UFOAgent] 前台窗口: '{self._active_window_title}', 区域=({left},{top})-({right},{bottom}), 尺寸={w}x{h}")
            return True

        except Exception as e:
            logger.warning(f"[UFOAgent] 获取窗口上下文失败: {e}")
            return False

    @staticmethod
    def _get_foreground_process_name() -> str:
        """
        获取当前前台窗口所属的进程名 (不含 .exe 后缀)

        Returns:
            str: 进程名 (如 "qqmusic", "chrome")，失败时返回空字符串
        """
        try:
            import ctypes.wintypes
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                return ""
            pid = ctypes.wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if not pid.value:
                return ""
            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_VM_READ = 0x0010
            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid.value
            )
            if not handle:
                return ""
            try:
                buf = ctypes.create_unicode_buffer(260)
                ctypes.windll.psapi.GetModuleFileNameExW(handle, None, buf, 260)
                exe_path = buf.value
                # 提取文件名 (不含后缀)
                import os
                proc_name = os.path.splitext(os.path.basename(exe_path))[0].lower()
                return proc_name
            finally:
                ctypes.windll.kernel32.CloseHandle(handle)
        except Exception:
            return ""

    async def _wait_for_target_window(self, title_contains: str = "", timeout: float = None,
                                       process_name: str = "") -> bool:
        """
        等待目标窗口成为前台窗口 (解决 open_app 后窗口焦点竞态条件)

        通过轮询 GetForegroundWindow + GetWindowTextW 匹配窗口标题。
        当标题匹配失败时，回退到进程名匹配 (解决如QQ音乐用歌曲名作窗口标题的问题)。
        轮询间隔使用配置值，最多等待 timeout 秒。

        Args:
            title_contains: 目标窗口标题的关键词 (不区分大小写)
            timeout: 最大等待时间 (秒)，默认使用配置值
            process_name: 目标进程名 (不含 .exe，如 "qqmusic")，作为标题匹配失败的回退

        Returns:
            bool: 是否成功匹配到目标窗口
        """
        import time
        if timeout is None:
            timeout = settings.AGENT_DEFAULT_TIMEOUT
        start = time.time()
        poll_interval = settings.AGENT_POLLING_INTERVAL
        title_lower = title_contains.lower() if title_contains else ""
        proc_lower = process_name.lower() if process_name else ""

        while time.time() - start < timeout:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if hwnd:
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                buf = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value.lower()
                matched = False
                match_method = ""

                # 优先: 标题匹配
                if title_lower and title_lower in title:
                    matched = True
                    match_method = "title"
                # 回退: 进程名匹配 (标题不包含关键词但进程名匹配)
                elif proc_lower:
                    fg_proc = self._get_foreground_process_name()
                    if fg_proc and proc_lower in fg_proc:
                        matched = True
                        match_method = "process"

                if matched:
                    # 匹配成功: 直接获取该窗口的 rect
                    rect = ctypes.wintypes.RECT()
                    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.pointer(rect))
                    left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
                    w, h = right - left, bottom - top
                    if w >= 100 and h >= 100:
                        self._active_window_rect = (left, top, right, bottom)
                        self._active_window_title = buf.value
                        elapsed = time.time() - start
                        logger.info(f"[UFOAgent] 窗口等待成功 (via {match_method}): '{buf.value}' (耗时 {elapsed:.1f}s)")
                        return True

            await asyncio.sleep(poll_interval)

        _hint = title_contains or process_name
        logger.warning(f"[UFOAgent] 窗口等待超时 ({timeout}s): 未匹配到 '{_hint}' (标题={title_contains!r}, 进程={process_name!r})")
        return False

    # 窗口裁剪扩展 padding (像素, 屏幕坐标空间)
    # 向下扩展更多空间以覆盖播放控件等底部 UI 元素
    _CROP_PADDING_LEFT = 5
    _CROP_PADDING_TOP = 5
    _CROP_PADDING_RIGHT = 5
    _CROP_PADDING_BOTTOM = None  # 使用配置值，在运行时设置

    def _crop_to_active_window(self, image: PILImage.Image) -> Tuple[PILImage.Image, Tuple[int, int]]:
        """
        将截图裁剪到当前前台窗口区域 (带 padding 扩展)

        Args:
            image: 已缩放的截图 (PIL.Image, 截图坐标空间)

        Returns:
            Tuple[PILImage.Image, Tuple[int, int]]:
                - 裁剪后的图像 (失败时返回原图)
                - 窗口左上角在截图坐标空间中的偏移 (失败时返回 (0,0))
        """
        if not self._active_window_rect:
            return image, (0, 0)

        try:
            sw, sh = image.size  # 截图像素尺寸 (已缩放)

            # 屏幕坐标 → 截图坐标
            left, top, right, bottom = self._active_window_rect
            scale = self._screenshot_scale
            crop_left = int((left - self._CROP_PADDING_LEFT) * scale)
            crop_top = int((top - self._CROP_PADDING_TOP) * scale)
            crop_right = int((right + self._CROP_PADDING_RIGHT) * scale)
            crop_padding_bottom = self._CROP_PADDING_BOTTOM if self._CROP_PADDING_BOTTOM is not None else settings.AGENT_CROP_PADDING_BOTTOM
            crop_bottom = int((bottom + crop_padding_bottom) * scale)

            # 边界修正: 确保裁剪区域在截图范围内
            crop_left = max(0, crop_left)
            crop_top = max(0, crop_top)
            crop_right = min(sw, crop_right)
            crop_bottom = min(sh, crop_bottom)

            crop_w = crop_right - crop_left
            crop_h = crop_bottom - crop_top

            if crop_w < 100 or crop_h < 100:
                logger.warning(f"[UFOAgent] 裁剪区域过小 ({crop_w}x{crop_h})，回退全屏")
                return image, (0, 0)

            cropped = image.crop((crop_left, crop_top, crop_right, crop_bottom))
            logger.info(f"[UFOAgent] 窗口裁剪: 截图({sw}x{sh}) → 裁剪({crop_w}x{crop_h}), 偏移=({crop_left},{crop_top})")
            return cropped, (crop_left, crop_top)

        except Exception as e:
            logger.warning(f"[UFOAgent] 窗口裁剪失败: {e}，回退全屏")
            return image, (0, 0)

    # ==================== 截图管道 (Agent-S) ====================

    def _save_screenshot_debug(self, image: PILImage.Image, label: str = ""):
        """
        DEBUG 模式下保存截图到 resources/screenshots/

        Args:
            image: PIL.Image 截图对象
            label: 截图标签 (如 plan/think/pre_act/post_act/coord)
        """
        if not settings.DEBUG:
            return
        try:
            save_dir = Path("resources/screenshots")
            save_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{timestamp}_{label}.{settings.SCREENSHOT_FORMAT.lower()}"
            filepath = save_dir / filename
            image.save(str(filepath), format=settings.SCREENSHOT_FORMAT)
            logger.debug(f"[UFOAgent] 调试截图已保存: {filepath}")
        except Exception as e:
            logger.warning(f"[UFOAgent] 调试截图保存失败: {e}")

    def _compute_image_hash(self, img: PILImage.Image) -> str:
        """计算图片的 MD5 哈希（缩小后），用于快速检测页面变化"""
        try:
            _w, _h = img.size
            _thumb = img.resize((min(_w, 120), min(_h, 68)), PILImage.LANCZOS)
            return hashlib.md5(_thumb.tobytes()).hexdigest()[:8]
        except Exception:
            return ""

    def _capture_screenshot(self, label: str = "", max_size: Optional[Tuple[int, int]] = None) -> Tuple[Optional[PILImage.Image], Optional[str]]:
        """
        截图 + 等比缩放 + base64 编码

        Agent-S 截图管道:
        1. pyautogui.screenshot() 捕获屏幕
        2. fit-in-box 等比缩放 (在指定宽高范围内，保留原始宽高比)
        3. 转换为 base64 data URL
        4. [DEBUG] 保存截图到 resources/screenshots/

        Args:
            label: 截图标签，用于 DEBUG 模式下的文件命名
            max_size: 自定义最大尺寸 (width, height)，None 则使用 SCREENSHOT_MAX_WIDTH/HEIGHT

        Returns:
            Tuple[Optional[PILImage.Image], Optional[str]]: (PIL.Image, data_url)
        """
        if not settings.SCREENSHOT_ENABLED:
            logger.warning("[UFOAgent] 截图功能未启用 (SCREENSHOT_ENABLED=False)")
            return None, None

        # Agent-S: 初始化缩放比例 (无缩放时为 1.0)
        self._screenshot_scale = 1.0

        try:
            raw = pyautogui.screenshot()
            raw_w, raw_h = raw.size
            logger.info(f"[UFOAgent] 截图成功: 原始尺寸 {raw_w}x{raw_h}")

            # 确定目标最大尺寸 (宽, 高)
            if max_size is not None:
                target_w, target_h = max_size
            else:
                target_w, target_h = settings.SCREENSHOT_MAX_WIDTH, settings.SCREENSHOT_MAX_HEIGHT

            # _screenshot_scale 始终基于 SCREENSHOT_MAX_WIDTH/HEIGHT (用于 _execute_action 坐标转换)
            # 即使本次调用使用了更小的尺寸 (如 Plan 阶段 1280x720)，
            # _screenshot_scale 仍按 SCREENSHOT_MAX 尺寸计算，因为后续坐标分析会重新截图
            _base_scale = min(settings.SCREENSHOT_MAX_WIDTH / raw_w, settings.SCREENSHOT_MAX_HEIGHT / raw_h)
            if _base_scale < 1.0:
                self._screenshot_scale = _base_scale

            # 实际缩放: fit-in-box，在 (target_w, target_h) 范围内等比缩放，不放大
            _actual_scale = min(target_w / raw_w, target_h / raw_h, 1.0)
            if _actual_scale < 1.0:
                w = int(raw_w * _actual_scale)
                h = int(raw_h * _actual_scale)
                raw = raw.resize((w, h), PILImage.LANCZOS)
                logger.info(f"[UFOAgent] 缩放后: {w}x{h}, 缩放比例: {_actual_scale:.4f}, 坐标缩放: {self._screenshot_scale:.4f}")

            self._screenshot_size = raw.size

            # base64 编码
            buf = io.BytesIO()
            raw.save(buf, format=settings.SCREENSHOT_FORMAT)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            data_url = f"data:image/{settings.SCREENSHOT_FORMAT.lower()};base64,{b64}"

            # DEBUG 模式下保存截图到磁盘
            self._save_screenshot_debug(raw, label=label or "screenshot")

            return raw, data_url

        except Exception as e:
            logger.error(f"[UFOAgent] 截图失败: {e}")
            return None, None

    # ==================== 程序性记忆 (Agent-S) ====================

    def _build_actions_description(self) -> str:
        """
        构建可用 Action 描述文本

        Agent-S: 动态系统提示注入所有可用 Action 签名
        Datawhale Ch4: ToolExecutor.getAvailableTools()
        """
        lines = ["可用操作列表:"]
        for action in UFO_AVAILABLE_ACTIONS:
            params = ", ".join(action["params"])
            lines.append(f"- {action['name']}({params}): {action['description']}")
        return "\n".join(lines)

    def _get_action_names(self) -> str:
        """获取可用 Action 名称的逗号分隔字符串"""
        return ", ".join(a["name"] for a in UFO_AVAILABLE_ACTIONS)

    def _build_system_prompt_suffix(self) -> str:
        """
        构造系统提示的后缀部分 (Action 清单 + 使用规则 + opinion.md 指导 + special.md 特殊场景)

        优先使用 SKILL.md 技能内容 (CoPaw 架构: Markdown body 作为 prompt 注入)
        回退到内置 UFO_AVAILABLE_ACTIONS 列表
        最后追加 opinion.md 和 special.md 的系统提示词指导
        """
        # 确保 opinion.md 和 special.md 已加载
        self._load_opinion_content()
        self._load_special_content()

        base_prompt = ""
        if self._skill_content:
            # 在技能内容后追加严格的 type 白名单约束
            _valid_type_names = ", ".join(sorted(a["name"] for a in UFO_AVAILABLE_ACTIONS))
            base_prompt = (
                self._skill_content
                + f"\n\n## ⚠️ 严格的操作类型约束\n\n"
                + f"**type 字段只允许使用以下 {len(UFO_AVAILABLE_ACTIONS)} 个值，严禁使用任何其他值**:\n"
                + f"`{_valid_type_names}`\n\n"
                + "常见错误示例（绝对不要这样写）:\n"
                + '- "type": "open_or_focus_app"  ✗ → 应为 "type": "open_app"\n'
                + '- "type": "search_song"  ✗ → 应为 "type": "type" + "text": "歌曲名"\n'
                + '- "type": "play_song"  ✗ → 应为 "type": "click"（点击播放按钮）\n'
                + '- "type": "navigate"  ✗ → 应为 "type": "click"（点击目标元素）\n'
                + '- "type": "find"  ✗ → 应为 "type": "scroll" 或 "type": "click"\n'
                + '- "type": "switch_tab"  ✗ → 应为 "type": "click"\n'
                + '- "type": "screenshot"  ✗ → 系统自动截图，无需此操作\n'
                + "- 如果上述列表中没有适合的操作，请拆分为多个基本操作的组合（如 click + type + click）\n"
            )
        else:
            # 回退: 使用内置 Action 列表
            actions_desc = self._build_actions_description()
            base_prompt = f"""
{actions_desc}

重要规则:
- 每个步骤必须选择上述列表中的一个操作
- 只能使用这些操作，不要自行创造新的操作
- 操作参数必须完整且准确
- 如果需要输入文本，中文文本会通过剪贴板粘贴
- 如果需要按回车确认，在文本末尾添加 {{ENTER}}
- type 输入时如果包含非ASCII字符，会自动使用剪贴板粘贴
"""

        # 追加 opinion.md 的系统提示词指导
        if self._opinion_content:
            base_prompt += f"\n\n## 📋 系统提示词指导与约束\n\n{self._opinion_content}"

        # 追加 special.md 的特殊场景处理
        if self._special_content:
            base_prompt += f"\n\n## 🎯 特殊场景处理指南\n\n{self._special_content}"

        return base_prompt

    # ==================== ReAct 历史轨迹 (Datawhale Ch4) ====================

    def _get_history_text(self) -> str:
        """
        获取 ReAct 风格的历史文本

        Datawhale Ch4 §4.2: 完整的 Thought-Action-Observation 轨迹
        History 字段累积每步的 (th_t, a_t, o_t)，形成不断增长的上下文
        注意: Reflection 的 next_steps/summary 以指令格式注入，避免 LLM 模仿反思 JSON 格式

        P5 优化: 超过 3 轮的旧记录压缩为单行摘要，最近 3 轮保留完整详情
        """
        if not self._step_records:
            return ""
        records = self._step_records
        _keep_recent = settings.AGENT_RECENT_STEPS_KEEP  # 保留最近的 N 条完整记录
        parts = []

        # 压缩旧记录 (> 3 轮)
        _old_records = records[:-_keep_recent] if len(records) > _keep_recent else []
        if _old_records:
            _summary_items = []
            for r in _old_records:
                _a = r.get("action_type") or "无操作"
                _d = f"({r.get('action_detail', '')[:30]})" if r.get("action_detail") else ""
                _s = "✓" if r.get("success") else "✗"
                _summary_items.append(f"{_a}{_d}{_s}")
            parts.append(f"[更早的操作摘要] {' → '.join(_summary_items)}")

        # 完整保留最近记录
        _recent_records = records[-_keep_recent:]
        _base_idx = len(_old_records)
        for i, r in enumerate(_recent_records):
            idx = _base_idx + i + 1
            parts.append(f"[步骤 {r.get('step', idx)}]")
            if r.get("thought"):
                parts.append(f"Thought: {r['thought']}")
            if r.get("action_type"):
                detail = f" ({r.get('action_detail')})" if r.get("action_detail") else ""
                parts.append(f"Action: {r['action_type']}{detail}")
            if r.get("observation"):
                parts.append(f"Observation: {r['observation']}")
            # 提取 reflection 中的 next_steps/summary，以简洁指令格式传递给 ReAct
            # 不直接输出 reflection JSON，避免 LLM 模仿反思格式
            if r.get("reflection"):
                _next = self._extract_reflection_hints(r["reflection"])
                if _next:
                    parts.append(f"上轮反思建议: {_next}")
        return "\n\n".join(parts)

    def _extract_reflection_hints(self, reflection_text: str) -> str:
        """
        从 reflection JSON 中提取 next_steps 和 summary，转为简洁指令文本

        设计目的: 让 ReAct Think 能看到上轮反思的改进建议，避免重复相同失败计划
        只提取可执行的指令性内容，不传递 JSON 结构化格式
        """
        try:
            json_match = re.search(r'\{[^{}]*\}', reflection_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                hints = []

                # 检测是否需要后退（错误恢复）
                needs_back = False
                back_reason = ""
                if data.get("next_steps"):
                    next_steps_text = " ".join(str(s) for s in data["next_steps"])
                    # 检测后退相关的关键词
                    back_keywords = ["后退", "返回", "back", "return", "上一页"]
                    if any(keyword in next_steps_text for keyword in back_keywords):
                        needs_back = True
                        back_reason = next_steps_text

                # 优先级1：如果需要后退，强制放在最前面
                if needs_back:
                    hints.append(f"🚨 强制要求 - {back_reason}")

                if data.get("summary"):
                    hints.append(data["summary"])
                if data.get("next_steps") and not needs_back:
                    hints.append("建议下一步: " + "; ".join(data["next_steps"]))
                feedback = data.get("feedback", {})
                if isinstance(feedback, dict):
                    for key, label in [
                        ("logic_gaps", "逻辑漏洞"),
                        ("factual_errors", "事实性错误"),
                        ("missing_info", "遗漏信息"),
                    ]:
                        val = feedback.get(key, "")
                        if val and val != "无":
                            hints.append(f"{label}: {val}")
                return " | ".join(hints) if hints else ""
        except (json.JSONDecodeError, TypeError):
            pass
        return ""

    def _get_recent_actions(self, window: int = 5) -> List[str]:
        """获取最近 N 步的 action 类型列表 (用于循环检测)"""
        recent = self._step_records[-window:]
        return [r.get("action_type") for r in recent if r.get("action_type")]

    def _detect_loop(self, recent_actions: List[str], threshold: int = 3) -> bool:
        """
        检测操作循环

        Agent-S per-step reflection: 如果最近 N 步中有 >= threshold 次相同操作
        """
        if len(recent_actions) < threshold:
            return False
        recent = recent_actions[-threshold:]
        return len(set(a for a in recent if a)) == 1

    def _get_failed_clicks(self, window: int = 10) -> List[Tuple[int, int]]:
        """
        获取最近失败操作的坐标列表 (用于坐标分析负反馈)

        优先从 _step_records 的 coordinates 字段提取结构化坐标，
        回退到从 action_detail 文本中 regex 提取。

        Args:
            window: 回溯的步骤数

        Returns:
            List[Tuple[int, int]]: 失败的 (x, y) 屏幕坐标列表
        """
        import re as _re
        _failed_coords = []
        for record in reversed(self._step_records[-window:]):
            if record.get("action_type") not in ("click", "double_click"):
                continue
            if record.get("success"):
                continue
            # 优先从结构化 coordinates 字段提取 (screenshot 空间坐标，供 LLM 参考)
            coords = record.get("coordinates", {})
            sx, sy = coords.get("screenshot_x"), coords.get("screenshot_y")
            if sx is not None and sy is not None:
                try:
                    _failed_coords.append((int(sx), int(sy)))
                    continue
                except (ValueError, TypeError):
                    pass
            # 回退: 从 description 文本中 regex 提取
            detail = record.get("action_detail", "")
            for pattern in [
                r'(?:坐标|x|点击).*?[\(\[](\d+)\s*[,\s]\s*(\d+)[\)\]]',
                r'\((\d+)\s*,\s*(\d+)\)',
            ]:
                m = _re.search(pattern, detail)
                if m:
                    try:
                        _failed_coords.append((int(m.group(1)), int(m.group(2))))
                        break
                    except (ValueError, IndexError):
                        continue
        return _failed_coords

    def _is_duplicate_action(self, action_step: Dict[str, Any], max_retries: int = 3) -> bool:
        """
        行为级去重 (语义化): 检查当前操作是否与最近已执行的操作完全重复

        改进点:
        - 仅统计"语义有效"的操作 (observe 确认效果达成的操作)
        - 检查最近的 observe 结果，如果 observe 指出操作未达预期效果，不计入去重计数
        - max_retries 从 2 提升到 3，允许更多重试机会
        - open_app 成功后重置关联操作的去重计数

        Args:
            action_step: 待执行的操作步骤
            max_retries: 同一操作最大重试次数

        Returns:
            bool: 是否为重复操作 (True=应跳过)
        """
        _action_key = action_step.get("type", "")
        _desc = action_step.get("description", "")
        _x = action_step.get("x")
        _y = action_step.get("y")

        if not _action_key:
            return False

        # 统计相同操作的执行次数 (仅统计语义成功的操作)
        _match_count = 0
        for record in reversed(self._step_records[-10:]):
            if record.get("action_type") != _action_key:
                continue
            # 只统计成功执行的操作
            if not record.get("success", True):
                continue

            # 语义效果检查: 如果 observe 指出该操作未达预期效果，不计入去重计数
            _obs = record.get("observation", "")
            _ineffective_keywords = [
                "未成功", "未生效", "未聚焦", "未完成", "未触发", "没有变化",
                "无效", "失败", "未能", "不正确", "未检测到", "未搜索",
                "文字丢失", "拼接", "多余字符", "新旧文本",
            ]
            if _obs and any(kw in _obs[:200] for kw in _ineffective_keywords):
                # 操作虽然机械执行成功，但 observe 确认其效果未达成，允许重试
                continue

            # 对于坐标操作，优先用结构化坐标匹配
            if _action_key in ("click", "double_click", "move", "drag") and _x is not None:
                _rc = record.get("coordinates", {})
                _rsx = _rc.get("screenshot_x")
                if _rsx is not None and abs(int(_rsx) - int(_x)) < 30:
                    _match_count += 1
                    continue
                # 回退: 描述文本匹配
                record_detail = record.get("action_detail", "")
                if str(_x) in record_detail:
                    _match_count += 1
                    continue
            # 对于非坐标操作，匹配描述文本
            if _desc:
                record_detail = record.get("action_detail", "")
                if _desc in record_detail:
                    _match_count += 1
                    continue

        if _match_count >= max_retries:
            logger.warning(f"[UFOAgent] 操作去重: '{_action_key}' (描述='{_desc[:50]}') 已有效执行 {_match_count} 次 (上限={max_retries})，跳过")
            return True
        return False

    # ==================== Plan-and-Solve: 规划阶段 ====================

    async def _plan(self, task: Task, context: Optional[Dict[str, Any]] = None) -> str:
        """
        规划阶段 (Plan-and-Solve 范式)

        Datawhale 第四章: Plan 阶段将复杂任务分解为清晰的步骤
        Agent-S: 初始规划时附带当前屏幕截图
        """
        context = context or {}
        eid = self._exec_id()

        # 规划重试计数: 跟踪已尝试次数，重试时跳过截图以降低 GPU 显存压力
        if not hasattr(self, '_plan_attempt_count'):
            self._plan_attempt_count = 0
        self._plan_attempt_count += 1
        _is_retry = self._plan_attempt_count > 1

        # 截图附加到初始规划 (Agent-S)
        # 首次规划携带截图，重试时跳过截图避免多模态消息占用过多 GPU 显存
        plan_image = None
        img_w, img_h = self._screen_size  # 重试时使用屏幕分辨率而非截图尺寸
        if not _is_retry:
            plan_image, _ = self._capture_screenshot(
                label="plan",
                max_size=(settings.SCREENSHOT_PLAN_MAX_WIDTH, settings.SCREENSHOT_PLAN_MAX_HEIGHT)
            )
            img_w, img_h = self._screenshot_size
            if plan_image:
                logger.info(f"[{eid}] 规划阶段: 已捕获当前屏幕截图 ({img_w}x{img_h}) 用于分析")
        else:
            logger.info(f"[{eid}] 规划重试第 {self._plan_attempt_count} 次，跳过截图以降低 GPU 内存压力")

        system_prompt = f"""你是一个 Windows UI 自动化规划专家。你的任务是将用户的 UI 自动化需求分解为一个清晰的、逐步执行的行动计划。

实际屏幕分辨率: {self._screen_size[0]}x{self._screen_size[1]}
截图显示分辨率: {img_w}x{img_h}
重要: 请基于截图实际像素输出坐标，系统会自动将截图坐标转换为屏幕坐标。

{self._build_system_prompt_suffix()}

**核心原则 — 应用操作前置检测**:
当任务需要操作某个应用程序时（如"打开QQ音乐"、"搜索发如雪"、"打开微信"等），
**第一步必须是使用 `open_app` 操作来确保应用已打开并可见**，而不是直接在截图上寻找应用界面。
`open_app` 会自动完成以下流程：
1. 检查系统进程中该应用是否运行
2. 如果运行中且有可见窗口 → 自动激活前置
3. 如果运行中但无可见窗口（最小化到系统托盘）→ 自动恢复到前台
4. 如果进程未运行 → 自动搜索快捷方式并启动
open_app 执行后会自动等待 3 秒让窗口加载完成。

请按照以下格式输出计划:
1. 任务理解: 简要描述对任务的理解
2. 执行步骤: 列出需要执行的具体步骤，每个步骤对应一个操作
3. 预期结果: 描述任务完成后的预期状态

输出 JSON 格式:
```json
{{
  "steps": [
    {{
      "type": "操作类型",
      "description": "操作描述",
      "target": "目标元素描述",
      "x": 100,
      "y": 200,
      "text": "要输入的文本",
      "keys": "快捷键",
      "scroll_y": -3,
      "seconds": 2,
      "clear_current_text": false,
      "app_name": "进程名",
      "search_keyword": "搜索关键词",
      "process_name": "进程名",
      "command": "系统命令",
      "shell": "cmd"
    }}
  ]
}}
```

重要规则:
- 每个步骤必须对应一个可用的操作类型
- 坐标值基于截图实际像素输出
- 只包含该步骤需要的参数
- 如果需要输入文本并在文本末尾按回车，在文本末尾添加 {{ENTER}}
- 操作步骤应该详细、具体、可执行
- **涉及某个应用时，第一步必须使用 open_app 确保应用已打开**，之后再进行 UI 操作

格式严格要求:
- 必须使用 "steps" 作为步骤数组的键名，不要使用 "step1"/"step2" 等编号键
- 每个步骤对象的 "type" 字段必须是操作类型名称（如 "open_app"、"click"、"type"），不要使用 "action" 作为类型值
- 不要在步骤中使用 "action" 字段表示操作类型，"type" 才是操作类型字段名
- **type 字段只允许以下值，禁止使用任何其他值（禁止自己发明操作类型）**:
  open_app, click, double_click, type, set_edit_text, keyboard_input, keypress, scroll, move, drag, wait, run_command, check_process
- **没有合适的操作类型时，请用基本操作组合实现**（如"搜索并播放歌曲"=click搜索框 + type输入关键词 + click搜索结果中的目标项 + click播放按钮）
- **搜索类操作必须包含结果选择步骤**: 输入搜索关键词后，通常会弹出搜索结果列表/下拉建议，必须增加一步从搜索结果中选择目标项，不要只点"搜索按钮"
- **考虑每步操作的 UI 后果**: 点击搜索栏会聚焦输入框、输入文字会出现搜索建议、点击搜索结果会进入详情页、进入详情页才能看到播放按钮
- **每个步骤必须包含该操作类型所需的全部必填参数，否则该步骤将无法执行！**
  - click / double_click: 必须有 "x" 和 "y" 坐标
  - type: 必须有 "text" 要输入的文本
  - keyboard_input: 必须有 "keys" 快捷键
  - scroll: 必须有 "scroll_y" 滚动量
  - open_app: 必须有 "app_name" 应用进程名

正确示例（打开QQ音乐搜索并播放歌曲）:
```json
{{
  "steps": [
    {{"type": "open_app", "app_name": "QQMusic", "description": "打开QQ音乐"}},
    {{"type": "click", "x": 500, "y": 100, "description": "点击搜索栏"}},
    {{"type": "type", "text": "发如雪", "description": "输入搜索关键词"}},
    {{"type": "click", "x": 500, "y": 200, "description": "在搜索结果中点击目标歌曲进入详情页"}},
    {{"type": "click", "x": 800, "y": 600, "description": "点击播放按钮"}}
  ]
}}
```"""

        user_parts = [
            f"任务标题: {task.title}",
            f"任务描述: {task.description}",
            f"任务复杂度: {task.complexity.value}",
            "",
            "当前屏幕截图已附加。请分析当前屏幕状态，然后制定执行计划。",
        ]

        # 使用 _get_history_text() 获取真实累积的历史记录
        # context.history 从未在 execute() 循环中被更新，直接读 self._step_records
        history_text = self._get_history_text()
        if history_text:
            user_parts.append(f"\n历史执行记录:\n{history_text}")

        user_prompt = "\n".join(user_parts)

        try:
            if plan_image:
                result = await self.llm.chat(
                    message=user_prompt,
                    system_prompt=system_prompt,
                    image=plan_image,
                    task_complexity=task.complexity
                )
            else:
                result = await self.llm.chat(
                    message=user_prompt,
                    system_prompt=system_prompt,
                    task_complexity=task.complexity
                )

            logger.info(f"[{eid}] 规划完成: {result[:150]}...")
            return result

        except Exception as e:
            logger.error(f"[{eid}] 规划阶段失败: {e}")
            return f"规划失败: {e}"

    # ==================== ReAct: 思考阶段 ====================

    async def think(
        self,
        task: Task,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        思考阶段 (Plan-and-Solve + ReAct Thought)

        Datawhale 第四章:
        - 步骤1 (step==0): Plan-and-Solve 规划阶段，完整分解任务
        - 步骤2+ (step>0): ReAct 轻量思考，基于 History + Observation 上下文决定下一步
        - 核心公式: (th_t, a_t) = π(q, (a_1,o_1), ..., (a_{t-1},o_{t-1}))
        """
        context = context or {}
        eid = self._exec_id()
        current_step = len(self._step_records)

        # 延迟加载技能内容
        await self._ensure_skills_loaded()

        if current_step == 0:
            # 第一步: Plan-and-Solve 完整规划 (Datawhale Ch4 §4.3)
            logger.info(f"[{eid}] 思考: Plan-and-Solve 规划阶段 (任务分解)")
            return await self._plan(task, context)

        # 后续步骤: ReAct 轻量思考 (Datawhale Ch4 §4.2)
        # 基于累积的 Action-Observation 历史和当前截图做轻量推理
        logger.info(f"[{eid}] 思考: ReAct 轻量推理 (第{current_step}步, 基于历史上下文)")

        # 截图附加到思考 (Agent-S: 当前屏幕状态感知)
        think_image, _ = self._capture_screenshot(label="think")
        img_w, img_h = self._screenshot_size
        if think_image:
            logger.info(f"[{eid}] ReAct 思考: 已捕获当前屏幕截图 ({img_w}x{img_h})")

        plan_text = context.get("plan_text", "")

        system_prompt = f"""你是一个 Windows UI 自动化操作专家。基于已执行的操作历史和当前屏幕状态，决定下一步操作。

实际屏幕分辨率: {self._screen_size[0]}x{self._screen_size[1]}
截图显示分辨率: {img_w}x{img_h}

{self._build_system_prompt_suffix()}

重要规则:
- 只需要输出尚未完成的剩余操作（1-3个），**绝对不要**重新规划已成功完成的步骤
- 基于操作历史和观察结果判断当前进度
- 如果上一步操作失败或效果不符预期，尝试不同的策略
- 如果检测到循环（重复相同操作），必须换一种方式
- **如果需要操作某个应用但截图上看不到该应用，使用 open_app 操作打开/切换到该应用**
- **type 字段只允许以下值，禁止使用任何其他值（禁止自己发明操作类型）**:
  open_app, click, double_click, type, set_edit_text, keyboard_input, keypress, scroll, move, drag, wait, run_command, check_process
- **没有合适的操作类型时，请用基本操作组合实现**（如"搜索并播放歌曲"=click搜索框 + type输入关键词 + click搜索结果中的目标项 + click播放按钮）
- **搜索类操作必须包含结果选择步骤**: 输入搜索关键词后，通常会弹出搜索结果列表/下拉建议，必须增加一步从搜索结果中选择目标项，不要只点"搜索按钮"
- **【关键】type/set_edit_text 输入文本前，必须先清空输入框！** 如果输入框中已有旧文本（如上轮输入的搜索词），必须先清空再输入，否则新旧文本会拼接在一起导致错误:
  - 方法1 (推荐): 在 type 之前增加一步 click 定位到输入框 → 再增加一步 keypress(keys="ctrl+a") 全选 → 再增加一步 keypress(keys="delete") 删除
  - 方法2: 使用 set_edit_text 类型（如果应用支持），它会直接替换文本
  - 当上一轮的 type 操作失败或效果不符（如搜索了错误的词），重新 type 时**务必先清空输入框**
- 每个步骤必须包含该操作类型所需的全部必填参数
- **【关键】click/double_click/scroll/move/drag 必须包含精确坐标！请仔细观察截图中目标元素的像素位置并输出坐标。没有坐标的操作无法执行。**
  - click/double_click: 必须有 "x" 和 "y"（目标元素在截图中的像素坐标）
  - scroll: 必须有 "scroll_y"（滚动量，负数向上, 正数向下）和可选 "x","y"
  - move: 必须有 "x" 和 "y"
  - drag: 必须有 "start_x","start_y","end_x","end_y"
  - 正确: {{"type": "click", "x": 350, "y": 80, "description": "点击搜索框"}}
  - 错误: {{"type": "click", "description": "点击搜索框"}} ← 缺少坐标，无法执行！
- **如果任务已完成，输出 "completed": true 和空 steps；如果未完成，必须输出 "steps" 数组**
- **绝对禁止输出 "feedback"、"progress"、"next_steps" 等反思格式字段，你是一个执行者不是评论员，必须输出具体的操作步骤**
- **上一步失败时的正确做法**: 直接在 steps 中重新输出修正后的操作（补全缺失参数），不要输出反思/分析/建议
  错误示例 ✗: "修正指令，为 open_app 添加 app_name 参数" — 这是反思，不是操作
  正确示例 ✓: {{"type": "open_app", "app_name": "qqmusic", "search_keyword": "QQ音乐", "description": "打开QQ音乐"}} — 这是操作

输出 JSON 格式:
```json
{{
  "thought": "对当前状态的分析和下一步理由",
  "steps": [
    {{
      "type": "操作类型",
      "description": "操作描述",
      "target": "目标元素描述",
      "x": 100,
      "y": 200,
      "text": "要输入的文本",
      "keys": "快捷键",
      "scroll_y": -3,
      "seconds": 2,
      "clear_current_text": false,
      "app_name": "进程名",
      "search_keyword": "搜索关键词",
      "process_name": "进程名",
      "command": "系统命令",
      "shell": "cmd"
    }}
  ]
}}
```

如果任务已经完成（观察结果确认目标已达成），输出:
```json
{{
  "thought": "任务已完成的分析",
  "completed": true,
  "steps": []
}}
```"""

        user_parts = [f"任务目标: {task.description}"]

        # O5: 强制注入最近反思的改进建议作为显式约束
        _latest_reflection = ""
        for _rec in reversed(self._step_records[-3:]):
            if _rec.get("reflection"):
                _latest_reflection = _rec["reflection"]
                break
        if _latest_reflection:
            _reflection_feedback = self._extract_reflection_hints(_latest_reflection)
            if _reflection_feedback:
                user_parts.append(
                    f"\n🚫 上轮反思的强制约束 (必须遵守，禁止重复相同失败策略):\n{_reflection_feedback}"
                )

        if plan_text:
            user_parts.append(f"\n初始规划:\n{plan_text[:800]}")

        # ReAct 核心: 注入 History (Datawhale Ch4 §4.2)
        history_text = self._get_history_text()
        if history_text:
            user_parts.append(f"\n操作历史 (Action-Observation 轨迹):\n{history_text}")

        # 跨轮去重: 注入上一轮完整操作序列，避免重复相同计划
        _last_cycle = context.get("last_cycle_actions", [])
        if _last_cycle:
            _cycle_str = " → ".join(
                f"{a.get('type','?')}({a.get('description','')[:30]})" for a in _last_cycle
            )
            user_parts.append(f"\n⚠️ 上一轮已执行的操作序列 (禁止重复相同计划):\n{_cycle_str}")

            # 增量规划: 提取已成功完成的步骤，引导 LLM 只规划剩余步骤
            _success_steps = [a for a in _last_cycle if a.get("success")]
            if _success_steps:
                _done_str = " → ".join(
                    f"{a.get('type','?')}({a.get('description','')[:30]})" for a in _success_steps
                )
                user_parts.append(f"\n✅ 上一轮已成功完成的步骤 (不要重复):\n{_done_str}")
                user_parts.append("\n⚠️ 重要: 请只规划尚未完成的剩余步骤，不要重复已成功完成的步骤！")

        user_parts.append("\n当前屏幕截图已附加。请基于当前状态决定下一步操作。")
        user_prompt = "\n".join(user_parts)

        try:
            if think_image:
                result = await self.llm.chat(
                    message=user_prompt,
                    system_prompt=system_prompt,
                    image=think_image,
                    task_complexity=task.complexity
                )
            else:
                result = await self.llm.chat(
                    message=user_prompt,
                    system_prompt=system_prompt,
                    task_complexity=task.complexity
                )

            logger.info(f"[{eid}] ReAct 思考完成: {result[:150]}...")
            return result

        except Exception as e:
            logger.error(f"[{eid}] ReAct 思考失败: {e}")
            return f"思考失败: {e}"

    # ==================== ReAct: 行动阶段 ====================

    async def act(
        self,
        thought: str,
        task: Task,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        行动阶段 (ReAct Action)

        Agent-S 改进:
        - 操作前截图保存 (用于逐步反思对比)
        - 坐标越界校验
        """
        context = context or {}
        eid = self._exec_id()
        result = {
            "success": False,
            "actions_performed": [],
            "screenshots": [],
            "error": None
        }

        try:
            # 操作前截图 (Agent-S 逐步反思)
            self._pre_action_screenshot, _ = self._capture_screenshot(label="pre_act")
            if self._pre_action_screenshot:
                logger.info(f"[{eid}] 行动前: 已保存操作前截图 (用于效果对比)")

            # 解析操作计划
            action_plan = await self._parse_action_plan(thought, task)
            logger.info(f"[{eid}] 解析到 {len(action_plan)} 个操作步骤")

            # ReAct 阶段: 对所有坐标操作强制标记 _needs_coord_analysis
            # (Plan 阶段保留仅对缺坐标步骤标记的逻辑，由 open_app 成功后触发)
            _phase = (context or {}).get("phase", "")
            if _phase == "react" and action_plan:
                _force_coord_types = {"click", "double_click", "move", "drag"}
                for _s in action_plan:
                    if isinstance(_s, dict) and _s.get("type") in _force_coord_types:
                        if _s.get("x") is not None:
                            _s["_needs_coord_analysis"] = True
                            logger.info(f"[{eid}] ReAct 阶段: 强制标记 {_s.get('type')} 步骤 '{_s.get('description', '')[:50]}' 待截图分析坐标")

            # 计划有效性预检: 如果所有步骤都缺少关键参数，提前标记失败避免空转
            if action_plan:
                _coord_required = {"click", "double_click", "scroll", "move", "drag"}
                _text_required = {"type", "set_edit_text"}
                _no_param_required = {"open_app", "run_command", "keyboard_input", "keypress", "wait", "check_process"}
                _all_lack_params = True
                for step in action_plan:
                    stype = step.get("type", "")
                    if stype in _no_param_required:
                        # open_app 等不一定缺参数（它们在 execute_action 中会检查 app_name 等），这里仅当 description 极短时才视为缺参数
                        if len(step.get("description", "")) > settings.AGENT_MIN_DESCRIPTION_LENGTH:
                            _all_lack_params = False
                            break
                    elif stype in _coord_required:
                        if step.get("x") is not None and step.get("y") is not None:
                            _all_lack_params = False
                            break
                    elif stype in _text_required:
                        if step.get("text"):
                            _all_lack_params = False
                            break
                    else:
                        # 未知类型，只要 description 足够详细就放过
                        if len(step.get("description", "")) > settings.AGENT_MIN_LONG_DESC_LENGTH:
                            _all_lack_params = False
                            break
                if _all_lack_params:
                    logger.warning(f"[{eid}] 计划有效性预检: 所有 {len(action_plan)} 个步骤均缺少关键参数（坐标/文本/app_name 等），跳过执行")
                    result["error"] = f"计划中所有步骤均缺少关键参数（共 {len(action_plan)} 步）"
                    return result

            # 执行每个操作 (使用 while 循环以支持 i-=1 步骤重试)
            i = 0
            _nav_retry_total = 0  # 导航重试全局计数 (跨 for 迭代持久化)
            while i < len(action_plan):
                action_step = action_plan[i]
                step_type = action_step.get("type", "unknown")
                step_desc = action_step.get("description", "")

                logger.info(f"[{eid}] 执行操作 {i+1}/{len(action_plan)}: {step_type} - {step_desc}")

                # 行为级去重: 同一操作最多重试 3 次，防止死循环
                if self._is_duplicate_action(action_step, max_retries=3):
                    result.setdefault("_skipped_count", 0)
                    result["_skipped_count"] += 1
                    logger.info(f"[{eid}] 操作被去重跳过: {step_type} - {step_desc[:50]}")
                    i += 1
                    continue

                # 截图坐标分析: 对缺少坐标的操作，通过截图+LLM分析获取精确坐标
                _window_hint = action_step.pop("_window_hint", None)
                if action_step.pop("_needs_coord_analysis", False):
                    # 等待 UI 完全渲染: 上一步操作（如 type+回车触发搜索）需要时间加载结果
                    # 根据上一步类型决定等待时长
                    _prev_type = action_plan[i-1].get("type", "") if i > 0 else ""
                    if _prev_type in ("type", "keyboard_input", "keypress", "set_edit_text"):
                        _wait_sec = settings.AGENT_ACTION_WAIT_AFTER_INPUT  # 输入操作后需等待搜索/导航加载
                    else:
                        _wait_sec = settings.AGENT_ACTION_WAIT_OTHER  # 其他操作后等待动画完成
                    logger.info(f"[{eid}] 步骤 {i+1}: {step_type} 缺少坐标，等待 {_wait_sec}s 后截图分析获取点位...")
                    await asyncio.sleep(_wait_sec)

                    # 窗口等待: 如果有 open_app 的窗口提示，智能等待目标窗口出现
                    if _window_hint:
                        # 快速检查: 如果前台进程已经匹配，跳过等待 (open_app 已验证)
                        _skip_wait = False
                        if isinstance(_window_hint, dict) and _window_hint.get("process"):
                            _wh_proc = _window_hint["process"].lower()
                            _fg_proc = self._get_foreground_process_name()
                            if _fg_proc and _wh_proc in _fg_proc:
                                logger.info(f"[{eid}] 步骤 {i+1}: 前台进程 '{_fg_proc}' 已匹配目标 '{_wh_proc}'，跳过窗口等待")
                                _skip_wait = True
                        if not _skip_wait:
                            if isinstance(_window_hint, dict):
                                _wh_title = _window_hint.get("title", "")
                                _wh_proc = _window_hint.get("process", "")
                                logger.info(f"[{eid}] 步骤 {i+1}: 等待目标窗口 (标题={_wh_title!r}, 进程={_wh_proc!r})...")
                                await self._wait_for_target_window(title_contains=_wh_title, timeout=settings.AGENT_WINDOW_WAIT_TIMEOUT, process_name=_wh_proc)
                            else:
                                # 兼容旧格式 (纯字符串)
                                logger.info(f"[{eid}] 步骤 {i+1}: 等待目标窗口 '{_window_hint}' 出现...")
                                await self._wait_for_target_window(title_contains=str(_window_hint), timeout=settings.AGENT_WINDOW_WAIT_TIMEOUT)

                    coord_image, _ = self._capture_screenshot(label="coord")
                    if coord_image:
                        # 智能窗口裁剪: 获取前台窗口边界，裁剪掉无关区域
                        _window_valid = self._update_window_context()
                        _crop_image, (_crop_offset_x, _crop_offset_y) = self._crop_to_active_window(coord_image)
                        _is_cropped = (_crop_offset_x > 0 or _crop_offset_y > 0)

                        _cw, _ch = self._screenshot_size
                        _img_actual = _crop_image.size  # 发送给 LLM 的实际像素尺寸
                        _target_desc = step_desc or action_step.get("target", "目标元素")
                        logger.info(
                            f"[{eid}] 坐标分析: 窗口裁剪={'是' if _is_cropped else '否'}, "
                            f"窗口='{self._active_window_title}', "
                            f"发送图像={_img_actual[0]}x{_img_actual[1]}, "
                            f"裁剪偏移=({_crop_offset_x},{_crop_offset_y}), "
                            f"scale={self._screenshot_scale:.4f}"
                        )
                        # 失败坐标负反馈: 注入历史失败坐标，避免重复命中同一位置
                        _failed_coords = self._get_failed_clicks(window=10)
                        _failed_note = ""
                        if _failed_coords:
                            _failed_str = ", ".join(f"({fx},{fy})" for fx, fy in _failed_coords[-5:])  # 最多展示最近 5 个
                            _failed_note = f"\n\n⚠️ 历史失败坐标（请避开这些位置）: {_failed_str}\n请选择与以上不同的坐标位置。\n"
                            logger.info(f"[{eid}] 坐标分析负反馈: 注入 {len(_failed_coords)} 个失败坐标")

                        # 计算窗口内容在裁剪图中的有效区域高度（不含 padding）
                        _content_h = _img_actual[1]  # 默认整个图像都是内容
                        if _is_cropped and self._active_window_rect:
                            _win_bottom_screen = self._active_window_rect[3]
                            _win_bottom_ss = int(_win_bottom_screen * self._screenshot_scale)
                            _content_h = max(100, _win_bottom_ss - _crop_offset_y)

                        _coord_prompt = (
                            f"精确屏幕坐标定位任务。\n\n"
                            f"截图分辨率: {_img_actual[0]}x{_img_actual[1]} 像素（此为截图实际分辨率，坐标必须基于此分辨率输出）\n"
                            f"任务目标: {task.description}\n"
                            f"需要定位的目标: {_target_desc}\n\n"
                            f"请仔细观察截图，找到 '{_target_desc}' 元素，输出其中心点的精确像素坐标。\n"
                            f"注意事项:\n"
                            f"- 坐标必须基于 {_img_actual[0]}x{_img_actual[1]} 分辨率\n"
                            f"- x 为水平像素位置（从左到右 0-{_img_actual[0]-1}）\n"
                            f"- y 为垂直像素位置（从上到下 0-{_content_h-1}）\n"
                            f"- 输出目标元素的中心点坐标\n"
                        )
                        if _is_cropped and _content_h < _img_actual[1]:
                            _coord_prompt += (
                                f"\n⚠️ 窗口内容边界: 截图中 y=0 到 y={_content_h-1} 为窗口实际内容区域，"
                                f"y≥{_content_h} 为窗口外的 padding 噪声区域。"
                                f"请确保坐标 y 值在 [0, {_content_h-1}] 范围内，不要将目标定位到 padding 区域。\n"
                            )
                        # 搜索结果定位增强: 当目标包含搜索结果相关关键词时，增加列表项定位指导
                        _search_hints = ["搜索结果", "搜索列表", "下拉建议", "搜索建议", "目标歌曲", "目标项"]
                        _is_search_result_click = any(kw in _target_desc for kw in _search_hints)
                        if _is_search_result_click:
                            # 提取任务描述中的搜索关键词，帮助 LLM 精确匹配
                            _skip_words = {"打开", "搜索", "播放", "点击", "找", "的", "来", "一", "个", "在", "进入", "歌曲"}
                            _search_keywords = []
                            for _word in task.description:
                                _w = _word.strip()
                                if len(_w) >= settings.AGENT_MIN_KEYWORD_LENGTH and _w not in _skip_words:
                                    _search_keywords.append(_w)
                            _kw_hint = ""
                            if _search_keywords:
                                _kw_hint = f"\n- 用户搜索的关键词: {', '.join(_search_keywords[:5])} — 请优先选择包含这些关键词的条目（如'{_search_keywords[0]}-周杰伦'比'{_search_keywords[0]}-DJ Rex'更匹配）"
                            _coord_prompt += (
                                f"\n⚠️ 重要: 区分搜索结果和其他列表\n"
                                f"- 【搜索结果特征】位于页面中上部，通常紧邻搜索框下方，有'搜索结果'、'相关歌曲'等标题，包含用户搜索词相关的条目\n"
                                f"- 【热门歌曲/推荐列表】位于页面较下位置，通常有'热门歌曲'、'推荐'等标签，是固定的推荐内容，与搜索无关\n"
                                f"- 【歌手页歌曲列表】在歌手详情页中，展示该歌手的热门作品，有头像、粉丝数等信息\n\n"
                                f"定位要求:\n"
                                f"- 必须优先选择【搜索结果】列表中的条目，而不是热门歌曲或歌手页歌曲\n"
                                f"- 如果搜索结果不可见，请明确说明，不要随意点击其他列表\n"
                                f"- 截图中可能显示一个搜索结果列表/下拉框，包含多个条目\n"
                                f"- 请找到【搜索结果】列表中与任务目标最匹配的条目{_kw_hint}\n"
                                f"- 输出该匹配条目的中心点坐标，不要输出列表外其他位置\n"
                                f"- 如果存在多个匹配条目，优先选择原始/官方/最知名版本（排除 DJ版/翻唱版/Remix版）\n"
                            )

                        # O4: 搜索结果内容校验 — 点击搜索结果前验证结果列表中包含目标关键词
                        if _is_search_result_click:
                            _task_keywords = task.description
                            # 提取任务中的目标关键词 (去掉常见动词)
                            _skip_words = {"打开", "搜索", "播放", "点击", "找", "播放", "的", "来", "一", "个", "在"}
                            _target_keywords = []
                            for _word in _task_keywords:
                                _w = _word.strip()
                                if len(_w) >= settings.AGENT_MIN_KEYWORD_LENGTH and _w not in _skip_words:
                                    _target_keywords.append(_w)
                            if _target_keywords:
                                _kw_list = ", ".join(f"'{w}'" for w in _target_keywords[:5])
                                _verify_prompt = (
                                    f"搜索结果校验: 请检查截图中是否显示了搜索结果列表。\n"
                                    f"任务目标关键词: {_kw_list}\n"
                                    f"只回答 JSON: {{\"found\": true/false, \"items\": [\"列表中可见的条目文字1\", \"条目文字2\"]}}\n"
                                    f"found=true 表示截图中可见搜索结果列表，found=false 表示未看到结果列表或列表为空。\n"
                                    f"items 列出结果列表中可见的条目文字（最多 5 个）。\n"
                                )
                                try:
                                    _verify_result = await self.llm.chat(
                                        message=_verify_prompt,
                                        system_prompt="你是搜索结果验证助手。只输出 JSON。",
                                        image=_crop_image,
                                        task_complexity=task.complexity
                                    )
                                    _found_match = re.search(r'"found"\s*:\s*(true|false)', _verify_result, re.IGNORECASE)
                                    _found = _found_match and _found_match.group(1).lower() == "true"
                                    if not _found:
                                        logger.warning(f"[{eid}] 搜索结果校验失败: 未在截图中找到搜索结果列表。任务关键词: {_kw_list}")
                                        # 不直接跳过，而是记录警告让后续流程处理
                                        _coord_prompt += (
                                            f"\n⚠️ 搜索结果校验警告: 当前截图中未检测到明显的搜索结果列表。"
                                            f"如果看到搜索建议或相关条目，请选择最匹配的目标。"
                                        )
                                    else:
                                        logger.info(f"[{eid}] 搜索结果校验通过: 检测到搜索结果列表")
                                        # 提取 items 传递给坐标分析
                                        _items_match = re.search(r'"items"\s*:\s*\[(.*?)\]', _verify_result, re.DOTALL)
                                        if _items_match:
                                            _items_str = _items_match.group(1)
                                            _items_list = re.findall(r'"([^"]+)"', _items_str)
                                            if _items_list:
                                                _coord_prompt += f"\n当前可见的搜索结果条目: {', '.join(_items_list[:5])}\n请从中选择与任务目标最匹配的条目坐标。"
                                except Exception as _verify_err:
                                    logger.debug(f"[{eid}] 搜索结果校验异常: {_verify_err}")
                        # P4: 注入最近一次 observe 结果作为上下文，帮助坐标分析理解当前 UI 状态
                        _last_obs = ""
                        for _rec in reversed(self._step_records[-5:]):
                            if _rec.get("observation"):
                                _last_obs = _rec["observation"][:300]
                                break
                        if _last_obs:
                            _coord_prompt += f"\n最近一次观察结果 (辅助定位):\n{_last_obs}\n"
                        _coord_prompt += f"{_failed_note}\n只输出 JSON: {{\"x\": 数字, \"y\": 数字, \"candidates\": [{{\"x\": 数字, \"y\": 数字, \"desc\": \"描述\"}}]}}\ncandidates 必须提供 2-3 个备选坐标，分别指向截图中不同可见元素的中心位置（如第二个可能的搜索结果、其他相似按钮等）。x,y 为首选最精确坐标。"
                        try:
                            # 构建坐标分析的系统提示词（根据任务类型动态调整）
                            _coord_system_prompt = f"你是精确的屏幕坐标定位助手。截图分辨率 {_img_actual[0]}x{_img_actual[1]}。只输出包含 x 和 y 的 JSON，不要输出其他任何内容。注意: x 必须在 [0, {_img_actual[0]-1}] 范围内, y 必须在 [0, {_img_actual[1]-1}] 范围内。坐标必须是单个数字，不要输出数组。"

                            # 针对音乐播放任务的特殊提示
                            if task.description and any(keyword in task.description.lower() for keyword in ["播放", "play", "音乐", "歌曲"]):
                                # 提取目标歌曲名称
                                song_name = task.description
                                for remove_word in ["播放", "play", "音乐", "歌曲", "来", "的", "搜索", "打开"]:
                                    song_name = song_name.replace(remove_word, " ").strip()

                                _coord_system_prompt += f"\n\n【音乐播放任务特殊说明】\n"
                                _coord_system_prompt += f"目标任务：播放《{song_name}》\n\n"
                                _coord_system_prompt += f"⚠️ 播放按钮识别关键特征：\n"
                                _coord_system_prompt += f"1. 【位置】位于歌曲条目的封面图上（左侧方形图片），通常在封面中央或右下角\n"
                                _coord_system_prompt += f"2. 【形状】白色三角形 ▶ 或 ▶️，有时外圈有半透明圆形背景\n"
                                _coord_system_prompt += f"3. 【状态】鼠标悬停时三角形变为绿色 ▶️ 或高亮显示，这是可点击状态\n"
                                _coord_system_prompt += f"4. 【区分】不是歌曲名文本、不是歌手名、不是底部播放栏按钮\n\n"
                                _coord_system_prompt += f"🚫 绝对不要点击：\n"
                                _coord_system_prompt += f"- 歌曲名称或歌手名称文本\n"
                                _coord_system_prompt += f"- 底部播放栏的播放/暂停按钮（那是控制当前播放的歌曲）\n"
                                _coord_system_prompt += f"- 封面图本身（要点击封面上的播放图标）\n\n"
                                _coord_system_prompt += f"✅ 正确操作流程：\n"
                                _coord_system_prompt += f"1. 在歌曲列表中找到《{song_name}》的封面图\n"
                                _coord_system_prompt += f"2. 在封面图上查找白色/绿色三角形播放图标\n"
                                _coord_system_prompt += f"3. 点击该播放图标的中心位置\n"
                                _coord_system_prompt += f"4. 如果看不到播放图标，先点击封面图中央区域触发图标显示\n"
                                _coord_system_prompt += f"5. 如果当前是歌手详情页，在热门歌曲列表中找到目标歌曲"

                            _coord_result = await self.llm.chat(
                                message=_coord_prompt,
                                system_prompt=_coord_system_prompt,
                                image=_crop_image,
                                task_complexity=task.complexity
                            )
                            logger.info(f"[{eid}] 坐标分析LLM返回: {_coord_result[:300]}")

                            def _parse_coord_result(result_text, img_w, img_h):
                                """解析 LLM 返回的坐标，支持多种格式"""
                                cx = cy = None
                                # 标准 JSON 正则
                                m = re.search(r'\{[^{}]*"x"\s*:\s*(\d+)[^{}]*"y"\s*:\s*(\d+)[^{}]*\}', result_text, re.IGNORECASE)
                                if m:
                                    cx, cy = int(m.group(1)), int(m.group(2))
                                else:
                                    # 尝试 JSON 解析兼容数组值、缺键名等 LLM 异常输出
                                    try:
                                        json_clean = re.search(r'\{.*\}', result_text, re.DOTALL)
                                        if json_clean:
                                            parsed = json.loads(json_clean.group(0))
                                            if isinstance(parsed, dict):
                                                def to_int(v):
                                                    if isinstance(v, (int, float)):
                                                        return int(v)
                                                    if isinstance(v, list) and v and isinstance(v[0], (int, float)):
                                                        return int(v[0])
                                                    return None
                                                cx = to_int(parsed.get("x"))
                                                cy = to_int(parsed.get("y"))
                                                if cx is not None and cy is None:
                                                    vals = parsed.get("y")
                                                    if isinstance(vals, list) and vals:
                                                        cy = to_int(vals)
                                    except (json.JSONDecodeError, TypeError, ValueError):
                                        pass

                                    # JSON 解析失败时退回正则宽松解析
                                    if cx is None or cy is None:
                                        any_num = re.findall(r'"x"\s*:\s*(\d+)', result_text, re.IGNORECASE)
                                        any_num_y = re.findall(r'"y"\s*:\s*(\d+)', result_text, re.IGNORECASE)
                                        if any_num and any_num_y:
                                            cx, cy = int(any_num[0]), int(any_num_y[0])
                                        elif any_num and not any_num_y:
                                            fallback_nums = re.findall(r'"x"\s*:\s*\d+[,\s]+(\d+)', result_text, re.IGNORECASE)
                                            if fallback_nums:
                                                cx = int(any_num[0])
                                                cy = int(fallback_nums[0])
                                return cx, cy

                            def _parse_candidates(result_text, img_w, img_h):
                                """解析 LLM 返回的候选坐标列表"""
                                _candidates = []
                                try:
                                    _cm = re.search(r'"candidates"\s*:\s*\[(.*?)\](?:\s*[,\}])', result_text, re.DOTALL)
                                    if _cm:
                                        for _item in re.finditer(r'\{[^{}]*\}', _cm.group(1)):
                                            _it = _item.group(0)
                                            _ix = re.search(r'"x"\s*:\s*(\d+)', _it, re.IGNORECASE)
                                            _iy = re.search(r'"y"\s*:\s*(\d+)', _it, re.IGNORECASE)
                                            _idesc = re.search(r'"desc"\s*:\s*"([^"]*)"', _it, re.IGNORECASE)
                                            if _ix and _iy:
                                                _cvx, _cvy = int(_ix.group(1)), int(_iy.group(1))
                                                if 0 <= _cvx < img_w and 0 <= _cvy < img_h:
                                                    _candidates.append({
                                                        "x": _cvx, "y": _cvy,
                                                        "desc": _idesc.group(1) if _idesc else ""
                                                    })
                                except Exception:
                                    pass
                                return _candidates

                            _cx, _cy = _parse_coord_result(_coord_result, _img_actual[0], _img_actual[1])
                            _candidates = _parse_candidates(_coord_result, _img_actual[0], _img_actual[1])
                            if _candidates:
                                logger.info(f"[{eid}] 解析到 {len(_candidates)} 个候选坐标: {_candidates[:3]}")

                            if _cx is not None and _cy is not None:
                                # 坐标范围校验: 超出裁剪图范围时改用全屏截图重新分析
                                _out_of_bounds = False
                                if _cx < 0 or _cx >= _img_actual[0] or _cy < 0 or _cy >= _img_actual[1]:
                                    _out_of_bounds = True
                                if _out_of_bounds and _is_cropped:
                                    # O7: 先尝试候选坐标中在范围内的坐标
                                    _candidate_used = False
                                    if _candidates:
                                        for _ci, _cand in enumerate(_candidates):
                                            if 0 <= _cand["x"] < _img_actual[0] and 0 <= _cand["y"] < _img_actual[1]:
                                                _cx, _cy = _cand["x"], _cand["y"]
                                                logger.info(f"[{eid}] 主坐标越界，使用候选坐标 #{_ci+1} ({_cx},{_cy}) desc='{_cand.get('desc','')}'")
                                                _candidate_used = True
                                                _out_of_bounds = False
                                                break
                                    if not _candidate_used:
                                        logger.warning(f"[{eid}] 坐标 ({_cx},{_cy}) 超出裁剪图范围 ({_img_actual[0]}x{_img_actual[1]})，候选坐标也不可用，改用全屏截图重新分析")
                                        # 用全屏截图重新分析坐标
                                        sw, sh = coord_image.size  # 使用截图实际尺寸，而非屏幕分辨率
                                        _img_actual = (sw, sh)  # 更新为全屏截图尺寸

                                        # 针对音乐播放任务的特殊提示
                                        _music_task_note = ""
                                        if task.description and any(keyword in task.description.lower() for keyword in ["播放", "play", "音乐", "歌曲"]):
                                            song_name = task.description
                                            for remove_word in ["播放", "play", "音乐", "歌曲", "来", "的", "搜索", "打开"]:
                                                song_name = song_name.replace(remove_word, " ").strip()
                                            _music_task_note = (
                                                f"\n\n【音乐播放任务特殊说明】\n"
                                                f"目标任务：播放《{song_name}》\n\n"
                                                f"⚠️ 播放按钮识别关键特征：\n"
                                                f"1. 【位置】位于歌曲条目的封面图上（左侧方形图片），通常在封面中央或右下角\n"
                                                f"2. 【形状】白色三角形 ▶ 或 ▶️，有时外圈有半透明圆形背景\n"
                                                f"3. 【状态】鼠标悬停时三角形变为绿色 ▶️ 或高亮显示，这是可点击状态\n"
                                                f"4. 【区分】不是歌曲名文本、不是歌手名、不是底部播放栏按钮\n\n"
                                                f"🚫 绝对不要点击：\n"
                                                f"- 歌曲名称或歌手名称文本\n"
                                                f"- 底部播放栏的播放/暂停按钮（那是控制当前播放的歌曲）\n"
                                                f"- 封面图本身（要点击封面上的播放图标）\n\n"
                                                f"✅ 正确操作流程：\n"
                                                f"1. 在歌曲列表中找到《{song_name}》的封面图\n"
                                                f"2. 在封面图上查找白色/绿色三角形播放图标\n"
                                                f"3. 点击该播放图标的中心位置\n"
                                                f"4. 如果看不到播放图标，先点击封面图中央区域触发图标显示\n"
                                                f"5. 如果当前是歌手详情页，在热门歌曲列表中找到目标歌曲\n"
                                            )

                                        _retry_coord_prompt = (
                                            f"精确屏幕坐标定位任务。\n\n"
                                            f"截图分辨率: {sw}x{sh} 像素（此为截图实际分辨率，坐标必须基于此分辨率输出）\n"
                                            f"任务目标: {task.description}\n"
                                            f"需要定位的目标: {_target_desc}\n\n"
                                            f"请仔细观察截图，找到 '{_target_desc}' 元素，输出其中心点的精确像素坐标。\n"
                                            f"注意事项:\n"
                                            f"- 坐标必须基于 {sw}x{sh} 分辨率\n"
                                            f"- x 为水平像素位置（从左到右 0-{sw-1}）\n"
                                            f"- y 为垂直像素位置（从上到下 0-{sh-1}）\n"
                                            f"- 输出目标元素的中心点坐标\n"
                                            f"{_music_task_note}"
                                        )
                                        _retry_coord_prompt += f"{_failed_note}\n只输出 JSON: {{\"x\": 数字, \"y\": 数字}}\n注意: 坐标必须在 [0, {sw-1}] x [0, {sh-1}] 范围内。"
                                        try:
                                            _retry_result = await self.llm.chat(
                                                message=_retry_coord_prompt,
                                                system_prompt=f"你是精确的屏幕坐标定位助手。截图分辨率 {sw}x{sh}。只输出包含 x 和 y 的 JSON，不要输出其他任何内容。注意: x 必须在 [0, {sw-1}] 范围内, y 必须在 [0, {sh-1}] 范围内。",
                                                image=coord_image,
                                                task_complexity=task.complexity
                                            )
                                            logger.info(f"[{eid}] 全屏重试坐标分析返回: {_retry_result[:200]}")
                                            _rcx, _rcy = _parse_coord_result(_retry_result, sw, sh)
                                            if _rcx is not None and _rcy is not None:
                                                # 全屏坐标直接使用 (无需偏移)
                                                _cx, _cy = _rcx, _rcy
                                                _is_cropped = False  # 切换为全屏坐标模式
                                                logger.info(f"[{eid}] 全屏重试成功: 坐标=({_cx},{_cy})")
                                            else:
                                                logger.warning(f"[{eid}] 全屏重试仍未能提取有效坐标，跳过")
                                                i += 1
                                                continue
                                        except Exception as _retry_err:
                                            logger.warning(f"[{eid}] 全屏重试失败: {_retry_err}，跳过")
                                            i += 1
                                            continue
                                elif _out_of_bounds:
                                    # 非裁剪模式下也 clamp
                                    _cx = max(0, min(_cx, _img_actual[0] - 1))
                                    _cy = max(0, min(_cy, _img_actual[1] - 1))
                                    logger.warning(f"[{eid}] 坐标超出范围，已 clamp: ({_cx},{_cy})")
                                else:
                                    pass  # 坐标在范围内，无需处理

                                if True:
                                    if _is_cropped:
                                        # 裁剪模式: 比例映射 —— 将 padding 区域的坐标映射回内容区
                                        _img_h = _img_actual[1]
                                        if _cy >= _content_h and _img_h > _content_h:
                                            # y 坐标落在 padding 区域，按比例缩放到内容区
                                            _cy_orig = _cy
                                            _cy = int(_cy * (_content_h - 1) / (_img_h - 1))
                                            logger.info(
                                                f"[{eid}] y 坐标 {_cy_orig} 在 padding 区域 "
                                                f"(content_h={_content_h}, img_h={_img_h})，"
                                                f"已自动比例映射为 y={_cy}"
                                            )
                                        # 裁剪坐标 → 截图坐标 (加上裁剪偏移)
                                        _ss_x = _cx + _crop_offset_x
                                        _ss_y = _cy + _crop_offset_y
                                        action_step["x"] = _ss_x
                                        action_step["y"] = _ss_y
                                        logger.info(
                                            f"[{eid}] 窗口裁剪坐标: 裁剪内({_cx},{_cy}) + 偏移({_crop_offset_x},{_crop_offset_y})"
                                            f" → 截图坐标({_ss_x},{_ss_y}), 屏幕=({_ss_x}/{self._screenshot_scale:.4f},{_ss_y}/{self._screenshot_scale:.4f})"
                                        )
                                    else:
                                        action_step["x"] = _cx
                                        action_step["y"] = _cy
                                        logger.info(f"[{eid}] 截图分析获取坐标: x={_cx}, y={_cy} (截图 {_img_actual[0]}x{_img_actual[1]})")
                                    # O7: 记录候选坐标到 step_records，供后续 think/reflect 使用
                                    if _candidates and hasattr(self, '_step_records') and self._step_records:
                                        self._step_records[-1]["coord_candidates"] = _candidates
                                else:
                                    logger.warning(f"[{eid}] 坐标超出裁剪图范围 ({_cx},{_cy}) vs ({_img_actual[0]}x{_img_actual[1]})，跳过")
                                    i += 1
                                    continue
                            else:
                                logger.warning(f"[{eid}] 截图分析未能提取有效坐标，跳过: {_coord_result[:200]}")
                                i += 1
                                continue
                        except Exception as _coord_err:
                            logger.warning(f"[{eid}] 截图分析获取坐标失败: {_coord_err}，跳过此步骤")
                            i += 1
                            continue
                    else:
                        logger.warning(f"[{eid}] 截图分析: 无法捕获截图，跳过缺坐标步骤")
                        i += 1
                        continue

                # 搜索结果下拉框 hover-then-click: 在 click 前动态插入 move+wait 步骤
                # 综合三重检测: 1)搜索结果关键词 2)导航关键词 3)下一步骤上下文推理
                _hover_search_hints = ["搜索结果", "搜索列表", "下拉建议", "搜索建议", "目标歌曲", "目标项"]
                _is_hover_insert = False
                if step_type in ("click", "double_click") and action_step.get("x") is not None:
                    _is_hover_insert = any(kw in step_desc for kw in _hover_search_hints)
                    if not _is_hover_insert:
                        # 复用导航关键词检测（覆盖"选中"/"选择"等场景）
                        _hover_nav_kw = ("选中", "选择", "进入", "打开", "切换")
                        _is_hover_insert = any(kw in step_desc for kw in _hover_nav_kw)
                    if not _is_hover_insert and i + 1 < len(action_plan):
                        # 上下文推理: 下一步含"播放"/"详情"等 → 当前可能是下拉框选中操作
                        _next_desc = str(action_plan[i + 1].get("description", ""))
                        _next_hover_hints = ("播放", "详情", "查看", "展开", "购买", "下载", "收藏", "评论")
                        if any(nh in _next_desc for nh in _next_hover_hints):
                            _is_hover_insert = True
                if _is_hover_insert and not action_step.get("_hover_injected"):
                    _move_x = int(action_step.get("x", 0))
                    _move_y = int(action_step.get("y", 0))
                    _move_step = {
                        "type": "move", "x": _move_x, "y": _move_y,
                        "description": f"[hover] 悬停到下拉框条目 (原始坐标={action_step.get('x')},{_move_y})",
                        "_hover_injected": True  # 防止 move 步骤本身递归触发
                    }
                    _wait_step = {
                        "type": "wait", "seconds": 0.8,
                        "description": "[hover] 等待下拉框条目高亮渲染",
                        "_hover_injected": True
                    }
                    # 动态插入 move + wait 到当前位置前面（后续步骤 index 全部 +2）
                    action_plan.insert(i, _move_step)
                    action_plan.insert(i + 1, _wait_step)
                    action_step["_hover_injected"] = True  # 标记原始 click 步骤已注入 hover
                    logger.info(f"[{eid}] hover-then-click: 插入 move({action_step.get('x')}={_move_x},{_move_y}) + wait(0.8) 在 click 前方")
                    continue  # 回到 while 顶部重新执行 move 步骤

                action_result = await self._execute_action(action_step, context)

                # O3: type 操作后验证文字是否正确输入（优化版：修复包含ENTER时的验证时序问题）
                if action_result.get("success") and step_type == "type":
                    _typed_text = str(action_step.get("text", ""))
                    _has_enter = bool(re.search(r'\{ENTER\}', _typed_text, re.IGNORECASE))
                    _expected_text = re.sub(r'\{[^}]+\}', '', _typed_text)  # 移除特殊键

                    if _expected_text.strip():  # 只对有实际文本内容的 type 做验证
                        if _has_enter:
                            # 包含ENTER的type操作：验证页面是否跳转（搜索结果/歌手页面是否出现）
                            await asyncio.sleep(1.5)  # 等待页面加载
                            _page_verify_img, _ = self._capture_screenshot(label="page_verify")
                            if _page_verify_img:
                                _page_verify_prompt = f"""请分析当前截图，判断页面是否因为搜索操作而发生了变化。

原始搜索词: '{_expected_text.strip()}'

请检查以下内容：
1. 页面是否显示了搜索结果列表？（注意：搜索结果通常包含歌曲名、歌手名，列表中会有'{_expected_text.strip()}'相关的内容）
2. 页面是否跳转到了歌手详情页？（注意：歌手页会有头像、姓名、粉丝数、作品数等信息）
3. 页面是否跳转到了歌曲播放页？（注意：播放页会有专辑封面、播放按钮、歌词等）

⚠️ 重要：
- 优先检查是否有搜索结果列表（这是搜索成功的标志）
- 如果是歌手详情页，说明搜索的是歌手名而不是歌曲名
- 如果是播放页，说明可能直接点击了某个歌曲

只回答JSON格式：{{"page_type": "search_result/artist_page/play_page/other", "search_success": true/false, "evidence": "判断依据"}}"""

                                try:
                                    _page_verify_result = await self.llm.chat(
                                        message=_page_verify_prompt,
                                        system_prompt="你是页面状态分析助手。准确判断页面类型和搜索是否成功。只输出 JSON。",
                                        image=_page_verify_img,
                                        task_complexity=task.complexity
                                    )

                                    # 解析验证结果
                                    _page_type = re.search(r'"page_type"\s*:\s*"([^"]*)"', _page_verify_result, re.IGNORECASE)
                                    _search_success = re.search(r'"search_success"\s*:\s*(true|false)', _page_verify_result, re.IGNORECASE)

                                    if _page_type and _search_success:
                                        _is_success = _search_success.group(1).lower() == 'true'
                                        _current_page = _page_type.group(1)

                                        if _is_success:
                                            logger.info(f"[{eid}] type验证成功: 页面已跳转到{_current_page}，搜索操作成功")
                                            # 记录验证成功状态，供反思阶段使用
                                            action_result["verification_success"] = True
                                            action_result["verification_type"] = "page_navigation"
                                            action_result["verification_detail"] = f"页面已跳转到{_current_page}"
                                        else:
                                            logger.warning(f"[{eid}] type验证失败: 页面未正确跳转，当前为{_current_page}")

                                            # 搜索失败，需要重试
                                            if action_step.get("_type_retry_count", 0) < settings.AGENT_MAX_TYPE_RETRIES:
                                                action_step["_type_retry_count"] = action_step.get("_type_retry_count", 0) + 1
                                                logger.info(f"[{eid}] 搜索未成功，执行重试 ({action_step['_type_retry_count']}/{settings.AGENT_MAX_TYPE_RETRIES})")

                                                # 重新聚焦搜索框
                                                await self._execute_action({
                                                    "type": "click",
                                                    "x": 320, "y": 100,  # 典型搜索框位置
                                                    "description": "重新点击搜索框"
                                                }, context)
                                                await asyncio.sleep(0.5)

                                                # 重新执行type操作
                                                action_result = await self._execute_action(action_step, context)

                                                if action_result.get("success"):
                                                    logger.info(f"[{eid}] type重试成功")
                                                    continue
                                                else:
                                                    logger.error(f"[{eid}] type重试失败，标记操作失败")
                                                    result["error"] = f"搜索验证失败：页面未正确跳转到搜索结果"
                                                    result["success"] = False
                                                    break
                                            else:
                                                logger.error(f"[{eid}] type验证重试次数已达上限，标记为失败")
                                                result["error"] = f"搜索验证失败（重试{action_step['_type_retry_count']}次后）"
                                                result["success"] = False
                                                break
                                except Exception as e:
                                    logger.warning(f"[{eid}] 页面验证失败，跳过验证: {e}")

                        else:
                            # 不包含ENTER的type操作：验证输入框文本
                            await asyncio.sleep(0.5)
                            _type_verify_img, _ = self._capture_screenshot(label="type_verify")
                            if _type_verify_img:
                                # 初始化验证结果变量
                                _type_verify_result = ""
                                _verify_processed = False

                                # 改进验证prompt，增加文本相似度判断
                                _type_verify_prompt = f"""请仔细检查截图中输入框内的实际文字内容。

期望输入的文字: '{_expected_text.strip()}'

请按以下步骤分析：
1. 截图中输入框内的实际文字是什么？（完整、准确地转录，包括每个字符）
2. 期望文字与实际文字是否完全一致？（区分大小写、空格、标点）
3. 如果不一致，差异在哪里？

⚠️ 重要：
- 必须逐字符对比，不要模糊判断
- 如果输入框内有其他文字（如搜索历史、自动补全），请明确指出
- 不要假设文字已正确输入，必须基于截图实际内容判断

只回答JSON格式：{{"match": true/false, "actual": "输入框中实际看到的完整文字", "difference": "如果不匹配，说明差异"}}"""

                                try:
                                    _type_verify_result = await self.llm.chat(
                                        message=_type_verify_prompt,
                                        system_prompt="你是文字内容验证助手。必须逐字符准确对比，不要模糊判断。只输出 JSON。",
                                        image=_type_verify_img,
                                        task_complexity=task.complexity
                                    )

                                    # 解析验证结果
                                    _match = re.search(r'"match"\s*:\s*(true|false)', _type_verify_result, re.IGNORECASE)
                                    _actual = re.search(r'"actual"\s*:\s*"([^"]*)"', _type_verify_result, re.IGNORECASE)

                                    if _match and _actual:
                                        _verify_processed = True  # 标记已成功处理
                                        _is_match = _match.group(1).lower() == 'true'
                                        _actual_text = _actual.group(1)

                                        if not _is_match:
                                            logger.warning(f"[{eid}] type验证失败: 期望='{_expected_text.strip()}' 实际='{_actual_text}'")

                                            # 清空输入框并重试（最多N次）
                                            if action_step.get("_type_retry_count", 0) < settings.AGENT_MAX_TYPE_RETRIES:
                                                action_step["_type_retry_count"] = action_step.get("_type_retry_count", 0) + 1

                                                logger.info(f"[{eid}] type验证失败，执行重试 ({action_step['_type_retry_count']}/{settings.AGENT_MAX_TYPE_RETRIES})")

                                                # 清空输入框（Ctrl+A + Delete）
                                                await self._execute_action({
                                                    "type": "keyboard_input",
                                                    "keys": "ctrl+a"
                                                }, context)
                                                await asyncio.sleep(0.2)
                                                await self._execute_action({
                                                    "type": "keypress",
                                                    "key": "delete"
                                                }, context)
                                                await asyncio.sleep(0.3)

                                                # 重新执行type操作
                                                action_result = await self._execute_action(action_step, context)

                                                # 如果重试成功，继续；否则跳出
                                                if action_result.get("success"):
                                                    logger.info(f"[{eid}] type重试成功")
                                                    continue
                                                else:
                                                    logger.error(f"[{eid}] type重试失败，标记操作失败")
                                                    result["error"] = f"输入验证失败：期望'{_expected_text.strip()}' 实际'{_actual_text}'"
                                                    result["success"] = False
                                                    break
                                            else:
                                                logger.error(f"[{eid}] type验证重试次数已达上限，标记为失败")
                                                result["error"] = f"输入验证失败（重试{action_step['_type_retry_count']}次后）：期望'{_expected_text.strip()}' 实际'{_actual_text}'"
                                                result["success"] = False
                                                break
                                        else:
                                            logger.info(f"[{eid}] type验证成功: 文本匹配")
                                            # 记录验证成功状态，供反思阶段使用
                                            action_result["verification_success"] = True
                                            action_result["verification_type"] = "text_match"
                                            action_result["verification_detail"] = f"文本'{_expected_text.strip()}'匹配成功"

                                except Exception as verify_error:
                                    logger.warning(f"[{eid}] type验证异常: {verify_error}")

                            # 只有在未成功解析时才执行fallback逻辑
                            if not _verify_processed and _type_verify_result:
                                logger.warning(f"[{eid}] type验证结果解析失败，回退到简单匹配: {_type_verify_result[:100]}")
                                if _match and _match.group(1).lower() == "false":
                                    logger.warning(f"[{eid}] type验证失败(简单模式): 期望'{_expected_text.strip()}'")
                                    action_result["success"] = False
                                    action_result["error"] = f"type 验证失败: 文字'{_expected_text.strip()}'未正确输入到目标位置"

                # 只记录实际执行（非跳过）的操作
                if action_result.get("success", True) or "缺少有效的" not in action_result.get("error", ""):
                    result["actions_performed"].append(action_result)
                else:
                    result.setdefault("_skipped_count", 0)
                    result["_skipped_count"] += 1

                if not action_result.get("success", True):
                    _err_msg = action_result.get("error", "Unknown error")
                    # 参数校验失败（缺少坐标/文本等）不中断，继续后续步骤
                    # 实际执行失败（如点击无响应）才中断执行
                    _is_validation_error = "缺少有效的" in _err_msg
                    if _is_validation_error:
                        logger.info(f"[{eid}] 操作跳过（参数校验失败）: {step_type} - {_err_msg}")
                        i += 1
                        continue
                    else:
                        logger.warning(f"[{eid}] 操作失败: {_err_msg}")
                        result["error"] = _err_msg
                        break

                logger.info(f"[{eid}] 操作成功: {step_type}")

                # open_app 成功后屏幕界面已发生变化，后续依赖坐标的步骤需要重新截图分析
                # P0: open_app 成功后，清除 type/click 等关联操作的去重计数，允许重新执行
                if step_type == "open_app" and action_result.get("success"):
                    # 从 _step_records 中移除与当前任务相关的历史记录中的 success 标记
                    # 这样后续的 type/click 等操作不会被去重误杀
                    _associated_types = {"type", "click", "double_click", "set_edit_text"}
                    for _rec in self._step_records:
                        if _rec.get("action_type") in _associated_types:
                            _rec["success"] = False  # 降级为"效果未验证"，允许重新执行
                    logger.info(f"[{eid}] open_app 成功后已重置关联操作的去重计数 ({len(self._step_records)} 条记录)")

                    # 保存 open_app 的目标信息供后续窗口等待使用
                    # _window_hint 同时携带标题关键词和进程名，用于窗口匹配回退
                    _app_hint_title = action_step.get("search_keyword") or action_step.get("app_name") or action_step.get("description", "")
                    _app_hint_proc = action_step.get("app_name") or ""
                    _coord_required = {"click", "double_click", "move", "drag"}
                    for _j in range(i + 1, len(action_plan)):
                        _rs = action_plan[_j]
                        if isinstance(_rs, dict) and _rs.get("type") in _coord_required:
                            if _rs.get("x") is not None:
                                _rs["_needs_coord_analysis"] = True
                                _rs["_window_hint"] = {"title": _app_hint_title, "process": _app_hint_proc}
                                logger.info(f"[{eid}] open_app 后屏幕已变化，标记步骤 {_j+1} ({_rs.get('type')}) 待截图分析坐标 (窗口标题提示: {_app_hint_title}, 进程: {_app_hint_proc})")

                # 导航类 click 后增加随机等待 + 截图变化检测 + 失败重试
                _max_nav_retries = settings.AGENT_MAX_NAV_RETRIES
                if action_result.get("success") and step_type in ("click", "double_click"):
                    # 导航关键词: 覆盖 "进入页面" + "点击搜索结果/目标项" 两类场景
                    _nav_keywords = (
                        "进入", "打开", "切换", "跳转", "展开", "导航", "详情",
                        "搜索结果", "目标歌曲", "目标项", "搜索列表", "下拉建议",
                        "选中", "选择",
                    )
                    _is_nav_click = any(kw in step_desc for kw in _nav_keywords)
                    # 上下文推理: 当下一步骤包含"播放"/"详情"等关键词时，
                    # 推断当前点击可能是进入页面/选中条目的导航操作
                    if not _is_nav_click and i + 1 < len(action_plan):
                        _next_desc = str(action_plan[i + 1].get("description", ""))
                        _next_nav_hints = ("播放", "详情", "查看", "展开", "购买", "下载", "收藏", "评论")
                        if any(nh in _next_desc for nh in _next_nav_hints):
                            logger.info(f"[{eid}] 上下文推理: 下一步 '{_next_desc[:30]}' 暗示当前步骤可能为导航操作")
                            _is_nav_click = True
                    if _is_nav_click:
                        # 记录点击前页面 hash，用于变化检测
                        _pre_nav_hash = action_result.get("screen_hash", "")
                        _nav_wait = round(random.uniform(3.0, 5.0), 1)
                        logger.info(f"[{eid}] 导航类 {step_type} 完成，等待 {_nav_wait}s 让页面响应...")
                        await asyncio.sleep(_nav_wait)

                        # 截图变化检测: 验证页面是否真的发生了跳转
                        while _nav_retry_total < _max_nav_retries:
                            _post_nav_img, _ = self._capture_screenshot(label=f"nav_verify_{_nav_retry_total}")
                            if _post_nav_img:
                                _post_nav_hash = self._compute_image_hash(_post_nav_img)
                                if _pre_nav_hash and _post_nav_hash != _pre_nav_hash:
                                    logger.info(f"[{eid}] 导航验证通过: 页面已变化 (pre={_pre_nav_hash} → post={_post_nav_hash})")
                                    _nav_retry_total = 0  # 成功后重置计数
                                    break
                                else:
                                    _nav_retry_total += 1
                                    if _nav_retry_total >= _max_nav_retries:
                                        logger.warning(f"[{eid}] 导航验证失败: 页面 {_max_nav_retries} 次检测均无变化，跳过重试")
                                        _nav_retry_total = 0  # 重置计数供后续步骤使用
                                        break
                                    logger.info(f"[{eid}] 导航验证: 页面未变化 (hash={_post_nav_hash}), 重试 {_nav_retry_total}/{_max_nav_retries}")
                                    # 标记重新需要坐标分析
                                    action_step["_needs_coord_analysis"] = True
                                    if _window_hint:
                                        action_step["_window_hint"] = _window_hint
                                    # 清除已有坐标，强制重新分析
                                    action_step.pop("x", None)
                                    action_step.pop("y", None)
                                    # 重新执行当前步骤 (while 循环中 i-=1 真正生效)
                                    logger.info(f"[{eid}] 导航重试 {_nav_retry_total}/{_max_nav_retries}: 重新截图分析坐标")
                                    i -= 1
                                    break
                            else:
                                break
                    else:
                        await asyncio.sleep(0.5)
                else:
                    await asyncio.sleep(0.5)

                # 正常完成当前步骤，前进到下一步
                i += 1

            # 只有实际执行了操作且无错误时才认为成功
            _skipped = result.pop("_skipped_count", 0)
            result["success"] = len(result["actions_performed"]) > 0 and result["error"] is None
            if not result["actions_performed"]:
                logger.warning(f"[{eid}] 行动阶段未执行任何操作 (思考结果中未能解析到有效步骤)")
            _summary = f"执行={len(result['actions_performed'])}"
            if _skipped:
                _summary += f", 跳过={_skipped}"
            logger.info(f"[{eid}] 行动完成: {_summary}, 成功={result['success']}")

            # 记录本轮操作序列到 context，供下一轮 think 跨轮去重使用
            if result["actions_performed"]:
                context["last_cycle_actions"] = result["actions_performed"]

        except Exception as e:
            logger.error(f"[{eid}] 行动阶段失败: {e}")
            result["error"] = str(e)

        return result

    # ==================== ReAct: 观察阶段 (核心改进) ====================

    async def observe(
        self,
        action_result: Dict[str, Any],
        task: Task,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        观察阶段 (ReAct Observation) - 核心改进

        Agent-S 截图管道:
        1. 操作后截图
        2. 构造多模态消息 (文本 + 截图) 通过 LLMManager.chat(image=...)
        3. VLM 分析屏幕状态变化

        Datawhale ReAct:
        - Observation 追加到历史记录
        - 为下一步 Thought 提供上下文
        """
        context = context or {}
        eid = self._exec_id()

        # 操作后截图
        post_image, post_data_url = self._capture_screenshot(label="post_act")
        if post_image:
            logger.info(f"[{eid}] observe: 操作后截图已捕获 ({post_image.size[0]}x{post_image.size[1]})")
            self._post_action_screenshot = post_image
        else:
            logger.warning(f"[{eid}] observe: 截图捕获失败，退回文本模式")

        # Agent-S 逐步反思: 构建操作前后对比图 (3张图模式)
        analysis_image = post_image
        comparison_note = ""
        _observe_images = None  # 多图模式

        # P3: 轻量化 observe — 仅在屏幕实际变化时才携带 pre-image 对比
        _observe_images = None
        comparison_note = ""

        if self._pre_action_screenshot and post_image:
            # 快速像素差异检测: 仅计算缩略图级别的相似度，避免全尺寸比较
            _plan_w, _plan_h = settings.SCREENSHOT_PLAN_MAX_WIDTH, settings.SCREENSHOT_PLAN_MAX_HEIGHT

            def _fit_to_plan(img):
                """将图片缩放到 PLAN 分辨率内 (等比缩放，不放大)"""
                scale = min(_plan_w / img.size[0], _plan_h / img.size[1], 1.0)
                if scale < 1.0:
                    return img.resize((int(img.size[0] * scale), int(img.size[1] * scale)), PILImage.LANCZOS)
                return img

            pre_thumb = _fit_to_plan(self._pre_action_screenshot)
            post_thumb = _fit_to_plan(post_image)

            # P3: 像素差异检测 — 如果两张截图几乎相同，只发送操作后截图 (省 1 张图的 LLM token)
            _has_changed = True
            try:
                import hashlib
                _pre_hash = hashlib.md5(pre_thumb.tobytes()).hexdigest()[:8]
                _post_hash = hashlib.md5(post_thumb.tobytes()).hexdigest()[:8]
                _has_changed = (_pre_hash != _post_hash)
                logger.info(f"[{eid}] observe: 屏幕变化检测 pre_hash={_pre_hash} post_hash={_post_hash} changed={_has_changed}")
            except Exception:
                pass  # 哈希计算失败时保守认为有变化

            if _has_changed:
                # 屏幕有变化: 发送操作后截图 + 操作前截图 (2张, 移除拼接对比图以节省 token)
                _observe_images = [post_thumb, pre_thumb]
                comparison_note = (
                    "\n截图说明 (共 2 张):"
                    "\n1. 第1张(最重要): 操作后截图 — 请以此为基准分析当前屏幕状态和新出现的UI元素"
                    "\n2. 第2张: 操作前截图 (仅用于辅助对比参考，观察UI变化)"
                    "\n⚠️ 你的分析必须以第1张(操作后截图)为准，不要被操作前的截图内容干扰"
                )
            else:
                # 屏幕无变化: 只发送操作后截图 (1张, 最大程度节省 token)
                _observe_images = [post_thumb]
                comparison_note = "\n截图说明: 操作后截图 (操作前后屏幕无明显变化)"

        # 构造观察提示
        actions = action_result.get("actions_performed", [])
        actions_summary = "\n".join(
            f"  - {a.get('action_type', 'unknown')}: {a.get('description', '')} -> "
            f"{'成功' if a.get('success') else '失败: ' + a.get('error', '')}"
            for a in actions
        ) if actions else "  (无操作执行)"

        system_prompt = """你是一个 UI 状态分析专家。请基于操作后截图分析当前屏幕状态。

⚠️ 核心原则：
1. **如实描述，禁止臆测** - 只描述截图中明确可见的内容，不要假设或推测
2. **文本内容准确性** - 如果涉及文字内容（搜索词、输入框、列表项等），必须逐字准确地识别
3. **客观判断** - 不要为了"任务完成"而强行解释，基于截图实际内容判断

🔍 页面类型识别（必须首先判断）：
请先识别当前页面属于以下哪种类型：
1. **搜索页面** - 有搜索框，显示搜索结果列表，结果紧邻搜索框下方
2. **歌手详情页** - 有歌手头像、姓名、粉丝数、作品数，显示热门歌曲列表
3. **播放页面** - 有专辑封面、播放控制按钮（播放/暂停/上一曲/下一曲）、歌词区域
4. **主页/推荐页** - 有推荐内容、轮播图、分类导航
5. **其他** - 请具体说明

分析要点：
1. 【必须】首先明确当前页面类型（从上述5种中选择）
2. 以操作后截图为唯一基准，描述当前页面/UI的真实状态
3. 已执行的操作是否产生了可见的UI变化
4. 任务目标的完成进度（基于实际UI状态，非假设）
5. 如果未达成，下一步需要执行什么操作（考虑页面类型）

⚠️ 文本识别重点（必须准确识别）：
- 输入框内的文字：必须完整、准确地转录，包括每个字符
- 搜索结果：列表中的每一项文字内容，特别是与你搜索目标相关的项
- 歌曲列表：区分搜索结果列表和热门歌曲列表
- 按钮文字：按钮上显示的具体文字
- 标题/标签：页面标题、标签文字

⚠️ 动态 UI 元素检测（必须检查）：
- 是否出现了下拉菜单/搜索建议列表/自动补全列表？→ 必须列出其中可点击的项及其文字
- 是否弹出了对话框/模态框/确认窗口/Toast 提示？
- 是否有新的标签页/页面打开？
- 按钮或输入框的状态是否发生变化（如出现清除按钮、展开箭头）？
- 列表/表格中是否出现了新的数据项？

⚠️ 搜索操作特别注意：
- 如果操作是"输入搜索关键词"，必须检查：
  1. 输入框内的实际文字是否与期望一致
  2. 是否出现了搜索建议/结果列表（注意：搜索结果在搜索框下方，热门歌曲在页面下方）
  3. 搜索结果中是否包含目标项（列出前3-5项的文字内容）
  4. 如果跳转到歌手详情页，说明搜索的是歌手名而不是歌曲名

⚠️ 列表类型区分：
- **搜索结果列表**：包含用户搜索词相关的条目，通常有"搜索结果"、"相关歌曲"等标题
- **热门歌曲列表**：固定的推荐内容，有"热门歌曲"、"推荐"等标签，与搜索无关
- **歌手作品列表**：展示该歌手的热门作品，有歌手头像、粉丝数等信息

注意：
- 以操作后截图(第1张)为分析基准，不要被操作前截图干扰
- 不要凭空假设操作已成功，基于截图的实际内容来判断
- 如果看到的内容与期望不符，必须如实报告
- 在分析开头明确页面类型，这对后续决策至关重要"""

        user_prompt = f"""任务目标: {task.description}

已执行的操作:
{actions_summary}
执行状态: {"成功" if action_result.get("success") else "失败: " + str(action_result.get("error"))}

请仔细分析当前屏幕截图，描述你看到的内容，并评估任务进度。{comparison_note}"""

        try:
            if _observe_images:
                # 多模态: 文本 + 3张图 (对比图 + 操作前独立 + 操作后独立)
                observation_text = await self.llm.chat(
                    message=user_prompt,
                    system_prompt=system_prompt,
                    images=_observe_images,
                    task_complexity=task.complexity
                )
            elif analysis_image:
                # 回退: 单图模式 (仅操作后截图)
                observation_text = await self.llm.chat(
                    message=user_prompt,
                    system_prompt=system_prompt,
                    image=analysis_image,
                    task_complexity=task.complexity
                )
            else:
                # 退回纯文本模式
                observation_text = await self.llm.chat(
                    message=user_prompt,
                    system_prompt=system_prompt,
                    task_complexity=task.complexity
                )

            logger.info(f"[{eid}] 观察完成: {observation_text[:150]}...")

            # 记录步骤到 ReAct 历史 (Datawhale Ch4: Thought-Action-Observation 完整链路)
            last_thought = context.get("last_thought", "")[:300] if context else ""
            for a in actions:
                record = {
                    "step": len(self._step_records) + 1,
                    "thought": last_thought,
                    "action_type": a.get("action_type"),
                    "action_detail": a.get("description"),
                    "coordinates": a.get("coordinates", {}),  # 实际执行的屏幕坐标
                    "observation": observation_text[:500],
                    "success": a.get("success", False),
                }
                # 传递验证状态到反思阶段（修复type操作误报问题）
                if a.get("verification_success"):
                    record["verification_success"] = a.get("verification_success")
                    record["verification_type"] = a.get("verification_type")
                    record["verification_detail"] = a.get("verification_detail")
                self._step_records.append(record)

            if not actions:
                self._step_records.append({
                    "step": len(self._step_records) + 1,
                    "thought": last_thought,
                    "action_type": None,
                    "observation": observation_text[:500],
                    "success": False,
                })

            return observation_text

        except Exception as e:
            logger.error(f"[{eid}] 观察阶段失败: {e}")
            return f"观察失败: {e}"

    # ==================== Reflection: 反思阶段 (增强) ====================

    async def reflect(
        self,
        observation: str,
        task: Task,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        反思阶段 (Reflection 范式) - 增强

        Datawhale Ch4 §4.4 执行-反思-优化循环:
        - 评估维度: 事实性错误、逻辑漏洞、效率问题、遗漏信息
        - 结构化反馈: 指出具体问题和改进建议
        - 优化建议: 如果未完成，提供可操作的下一步建议
        - 终止条件: "无需改进" 或 completed=true

        Agent-S per-step reflection:
        - 循环检测 (相同操作重复)
        - 操作效果验证
        - 任务完成度评估
        """
        context = context or {}
        eid = self._exec_id()

        # 循环检测 (Agent-S per-step reflection)
        recent_actions = self._get_recent_actions(window=5)
        loop_detected = self._detect_loop(recent_actions)

        # O5: 二次验证 - 检查最近的type操作是否真正成功
        _verification_note = ""
        _last_type_action = None
        for record in reversed(self._step_records[-10:]):
            if record.get("action_type") == "type":
                _last_type_action = record
                break

        if _last_type_action:
            # 优先检查：是否有验证成功的标记
            _verification_success = _last_type_action.get("verification_success", False)
            _verification_type = _last_type_action.get("verification_type", "")

            if _verification_success:
                # 已通过页面跳转或文本匹配验证，无需再检查observation文本
                logger.info(f"[{eid}] 反思阶段验证：type操作已通过{_verification_type}验证（{_last_type_action.get('verification_detail', '')}），跳过文本匹配检查")
            else:
                # 未记录验证成功状态，回退到文本匹配检查
                # 优化：提取关键词而非完整action_detail进行匹配
                _action_detail = _last_type_action.get("action_detail", "")
                _observation_lower = observation.lower()

                # 从action_detail中提取关键信息（搜索/输入相关）
                _search_keywords = []
                if "搜索" in _action_detail or "search" in _action_detail.lower():
                    _search_keywords.append("搜索")
                    _search_keywords.append("search")
                if "输入" in _action_detail or "input" in _action_detail.lower() or "type" in _action_detail.lower():
                    _search_keywords.append("输入")
                    _search_keywords.append("input")

                # 检查observation中是否包含搜索/输入相关的成功标志
                _has_success_indicators = any(
                    keyword in _observation_lower
                    for keyword in ["搜索结果", "search result", "歌曲", "列表", "跳转", "播放"]
                )

                # 检查observation中是否提到了输入框或输入相关内容
                _has_input_mention = any(
                    keyword in _observation_lower
                    for keyword in ["输入框", "输入", "搜索框", "文本框", "input", "text", "搜索"]
                )

                if _has_success_indicators:
                    # observation中有成功标志，认为type操作成功
                    logger.info(f"[{eid}] 反思阶段验证：type操作观察结果包含成功标志（{_action_detail}），认为操作成功")
                elif _has_input_mention:
                    # 有输入框提及但无明显成功标志，可能输入失败或需进一步观察
                    logger.info(f"[{eid}] 反思阶段验证：type操作观察到输入框状态，但未确认成功（{_action_detail}）")
                else:
                    # observation中完全没有相关信息，记录为需要关注
                    logger.info(f"[{eid}] 反思阶段验证：type操作观察结果中未找到明确成功标志（{_action_detail}），但基于操作成功标记认为已执行")

        system_prompt = f"""你是一个任务执行评审专家。请根据观察结果评估任务完成情况，并提供结构化的反馈。

当前执行历史 (最近 5 步): {recent_actions}
循环检测: {"⚠️ 检测到重复操作循环！" if loop_detected else "无循环"}

🔍 页面类型识别策略（必须首先判断）：
请根据观察结果中的页面类型，调整下一步策略：

1. **搜索页面** - 策略：关注搜索结果列表，点击目标项
   - 如果搜索结果包含目标，点击搜索结果中的目标项
   - 如果搜索结果为空或不匹配，需要重新搜索或调整搜索词

2. **歌手详情页** - 策略：识别当前是歌手页，需要回到搜索或找到目标歌曲
   - 如果目标是特定歌曲，需要在歌手页的歌曲列表中查找目标歌曲
   - 如果找不到，说明之前搜索的是歌手名而不是歌曲名，需要重新搜索

3. **播放页面** - 策略：检查当前播放歌曲是否为目标歌曲
   - 如果是目标歌曲，任务完成
   - 如果不是，需要回到搜索页面重新搜索

4. **主页/推荐页** - 策略：需要先进入搜索功能
   - 点击搜索框
   - 输入搜索词

评估维度 (Datawhale Ch4 §4.4 Reflection):
1. 事实性错误: 操作是否实际生效？屏幕状态是否与预期一致？
2. 逻辑漏洞: 操作顺序是否合理？是否有遗漏的中间步骤？
3. 效率问题: 是否有更直接的操作路径？是否在做无用的重复操作？
4. 遗漏信息: 是否忽略了任务的某些关键步骤？

重要判断规则:
- "观察结果"描述的是当前屏幕的实际状态，是最可靠的判断依据
- "操作成功"仅表示 pyautogui 调用未报错，绝不等于"任务目标已达成"
- **原始任务目标: "{task.description}"** — 必须严格对照此目标判断完成状态
- 只有当观察结果明确证实任务目标已完全达成，才能说 completed=true
- 例如: 任务是"搜索歌曲来播放"，仅在搜索结果页 ≠ completed，必须确认歌曲正在播放
- 如果只完成了一部分步骤，应指出具体还差哪些步骤
- 如果检测到循环，必须提出完全不同的操作策略
- **输入框清空检测**: 如果操作历史中有 type/set_edit_text 操作，但观察结果显示输入框内容不正确（新旧文本拼接、多余字符等），必须在 feedback 中明确指出"输入前未清空输入框"，并在 next_steps 中建议先清空再输入（click输入框 → ctrl+a全选 → delete删除 → 再type新文本）

⚠️ 页面类型误判检测：
- 如果在歌手详情页但目标是搜索特定歌曲，说明之前搜索的是歌手名而不是歌曲名
- 如果在播放页面但播放的不是目标歌曲，说明点击了错误的歌曲项
- 如果在搜索页面但没有搜索结果或结果不匹配，需要调整搜索词或搜索方式

🔄 **错误恢复机制（重要）**：
当检测到以下情况时，必须在 next_steps 的第一步添加"点击后退按钮返回上一页"：
1. 页面跳转到了非目标页面（如目标是播放歌曲，但跳转到了歌手详情页）
2. 点击操作后页面状态与预期不符（如点击播放按钮后进入了歌手页而不是播放歌曲）
3. 观察结果显示当前页面无法完成目标任务（如在歌手页找不到目标歌曲）

错误恢复操作：
- 第一步：点击浏览器/应用的后退按钮（通常在左上角，箭头图标 < 或 ←）
- 第二步：等待页面加载完成（等待2秒）
- 第三步：在返回的页面中重新执行正确的操作（如点击正确的播放按钮）

请用 JSON 格式回复:
```json
{{
  "completed": false,
  "page_type": "search_result/artist_page/play_page/home/other",
  "progress": "当前进度描述 (百分比或定性说明)",
  "feedback": {{
    "factual_errors": "事实性错误分析 (无则填'无')",
    "logic_gaps": "逻辑漏洞分析 (无则填'无')",
    "efficiency_issues": "效率问题分析 (无则填'无')",
    "missing_info": "遗漏信息分析 (无则填'无')"
  }},
  "next_steps": ["具体可操作的下一步1（考虑页面类型）", "具体可操作的下一步2"],
  "loop_detected": false,
  "summary": "总结"
}}
```"""

        user_prompt = f"""任务目标: {task.description}

已执行操作的详细结果 (Thought-Action-Observation 轨迹):
{self._get_history_text()}

观察结果（当前屏幕实际状态）:
{observation}{_verification_note}

请提供反思评估和改进建议。"""

        try:
            reflection = await self.llm.chat(
                message=user_prompt,
                system_prompt=system_prompt,
                task_complexity=task.complexity
            )

            logger.info(f"[{eid}] 反思完成: {reflection[:150]}...")

            # 记录反思到最后一条步骤记录 (Datawhale Ch4: Memory 模块)
            if self._step_records:
                self._step_records[-1]["reflection"] = reflection[:500]

            return reflection

        except Exception as e:
            logger.error(f"[{eid}] 反思阶段失败: {e}")
            return f"任务失败: {e}"

    # ==================== 操作解析和执行 ====================

    async def _parse_action_plan(
        self,
        thought: str,
        task: Task
    ) -> List[Dict[str, Any]]:
        """解析思考结果，提取操作计划。先尝试直接 JSON 提取，失败再调 LLM。"""
        eid = self._exec_id()

        # 前置过滤: 跳过明显无效的输入 (空响应、LLM 错误文本、垃圾文本)
        if not thought or not thought.strip() or thought.strip() in ("` `", "``"):
            logger.warning(f"[{eid}] _parse_action_plan: 输入为空或无效，跳过解析")
            return []
        if any(thought.startswith(prefix) for prefix in ("思考失败:", "规划失败:")):
            logger.warning(f"[{eid}] _parse_action_plan: 输入为错误消息，跳过解析: {thought[:100]}")
            return []
        # 垃圾文本检测: LLM 有时输出无意义的重复字符 (qwen3-vl 常见)
        stripped = thought.strip()
        if len(stripped) < settings.RAG_MIN_THOUGHT_LENGTH:
            logger.warning(f"[{eid}] _parse_action_plan: 输入过短 ({len(stripped)} chars)，可能为垃圾文本，跳过")
            return []
        if '{' not in stripped and len(re.findall(r'["\']', stripped)) < 2:
            logger.warning(f"[{eid}] _parse_action_plan: 输入不含 JSON 结构，可能为垃圾文本，跳过: {stripped[:100]}")
            return []

        # 优化: 先尝试直接从 think 输出中提取 JSON (省掉 1 次 LLM 调用)
        direct_steps = self._extract_json_steps(thought)
        if direct_steps:
            # 后处理: 从任务描述补全 type 操作缺失的 text 参数
            direct_steps = self._fill_missing_text_from_task(direct_steps, task)
            logger.info(f"[{eid}] _parse_action_plan: 直接提取到 {len(direct_steps)} 个步骤 (跳过 LLM 调用)")
            self._log_parsed_steps(direct_steps)
            return direct_steps

        # 直接提取失败，回退到 LLM 解析
        logger.info(f"[{eid}] _parse_action_plan: 直接提取失败，使用 LLM 解析")

        system_prompt = f"""请从思考结果中提取需要执行的操作步骤，以 JSON 格式输出。

{self._build_system_prompt_suffix()}

格式要求（必须严格遵守）：
```json
{{
  "steps": [
    {{
      "type": "操作类型",
      "description": "操作描述",
      "target": "目标元素描述",
      "x": 100,
      "y": 200,
      "text": "要输入的文本",
      "keys": "快捷键",
      "scroll_y": -3,
      "seconds": 2,
      "clear_current_text": false,
      "app_name": "进程名",
      "search_keyword": "搜索关键词",
      "process_name": "进程名",
      "command": "系统命令",
      "shell": "cmd"
    }}
  ]
}}
```

注意事项:
- type 必须是以下之一: {self._get_action_names()}
- 坐标值基于截图分辨率输出（{self._screenshot_size[0]}x{self._screenshot_size[1]}），系统会自动转换为屏幕坐标
- 只包含该步骤需要的参数
- **每个步骤必须包含该操作类型所需的全部必填参数**:
  - click/double_click 必须有 x,y 坐标; type 必须有 text; open_app 必须有 app_name; keyboard_input 必须有 keys
- 如果思考结果中没有明确的可执行操作，返回空步骤列表

只输出 JSON，不要输出其他内容。"""

        try:
            # 附加 ReAct 历史 (Datawhale Ch4: 将 History 注入提示词)
            history_text = self._get_history_text()
            full_prompt = f"任务目标: {task.description}\n\n请从以下思考结果中提取操作步骤：\n\n{thought}"
            if history_text:
                full_prompt += f"\n\n历史执行记录 (参考):\n{history_text}"

            # LLM 回退解析也需要截图上下文来生成坐标
            latest_screenshot = self._pre_action_screenshot
            if latest_screenshot:
                result = await self.llm.chat(
                    message=full_prompt,
                    system_prompt=system_prompt,
                    image=latest_screenshot,
                    task_complexity=task.complexity
                )
            else:
                result = await self.llm.chat(
                    message=full_prompt,
                    system_prompt=system_prompt,
                    task_complexity=task.complexity
                )

            logger.info(f"[{eid}] _parse_action_plan LLM 原始响应:\n{result}")

            # P2: 垃圾文本检测 — LLM fallback 有时输出 "0.5 0.5..." 等无意义重复数字
            _stripped_result = result.strip() if result else ""
            _is_coord_garbage = bool(re.match(r'^[\d\s.\-,]+$', _stripped_result)) and len(_stripped_result) < 200
            if _is_coord_garbage:
                logger.warning(f"[{eid}] _parse_action_plan: LLM fallback 返回坐标垃圾文本，丢弃: {_stripped_result[:80]}")
                return []

            steps = self._extract_json_steps(result)

            if not steps:
                # P2: 空步骤防护 — 如果 LLM 返回了有效文本但解析不到步骤，
                # 可能是因为 thought 本身包含操作计划但格式不标准，尝试宽松提取
                if len(_stripped_result) > settings.AGENT_MIN_STRIPPED_RESULT_LENGTH and '{' in _stripped_result:
                    logger.warning(f"[{eid}] _parse_action_plan: LLM 返回了含 JSON 的长文本但提取失败，可能是格式异常")
            else:
                steps = self._fill_missing_text_from_task(steps, task)
                self._log_parsed_steps(steps)

            return steps

        except Exception as e:
            logger.error(f"[{eid}] 解析操作计划失败: {e}")
            return []

    def _fill_missing_text_from_task(self, steps: List[Dict[str, Any]], task: Task) -> List[Dict[str, Any]]:
        """从任务描述中提取文本，补全 type/set_edit_text 操作缺失的 text 参数"""
        _text_types = {"type", "set_edit_text"}
        _text_needed = [i for i, s in enumerate(steps) if isinstance(s, dict) and s.get("type") in _text_types and not s.get("text")]
        if not _text_needed:
            return steps
        task_desc = str(task.description or "")
        task_title = str(task.title or "")
        _task_source = f"{task_title} {task_desc}".strip()
        _task_text = None
        # 优先1: 书名号 《发如雪》 或 引号 "发如雪"
        _qm = re.search(r"[\"'\u300c\u300e《](.+?)[\"'\u300d\u300f》]", _task_source)
        if _qm:
            _task_text = _qm.group(1).strip()
        # 优先2: 搜索/输入 后面的关键词（如 "搜索发如雪" → "发如雪"）
        if not _task_text:
            _sm = re.search(r"(?:搜索|输入|查找|查询)\s*([^，,。；来并]+?)(?:歌曲|音乐|内容|文本|文件|网页|应用|软件|程序|$)", _task_source)
            if _sm:
                _candidate = _sm.group(1).strip()
                _placeholder_words = {"歌曲名称", "歌名", "关键词", "搜索内容", "文本内容"}
                if _candidate.lower() not in _placeholder_words and len(_candidate) >= 2:
                    _task_text = _candidate
        # 优先3: 排除动词后的名词短语
        if not _task_text:
            _clean = re.sub(r"(?:打开|启动|运行|搜索|输入|点击|播放|下载|上传|设置|切换到|找到|查看|检查|来播放|歌曲来播放|并播放)", "", _task_source)
            _clean = re.sub(r"(?:应用|软件|程序|窗口|按钮|图标|歌曲)", "", _clean)
            _clean = re.sub(r"[，,。；、\s]+", " ", _clean).strip()
            if _clean and len(_clean) >= 2 and len(_clean) <= 20:
                _task_text = _clean
        if _task_text:
            for idx in _text_needed:
                steps[idx]["text"] = _task_text
                logger.info(f"[UFOAgent] 从任务描述补全 text='{_task_text}' (步骤 {idx+1} type={steps[idx].get('type')})")
        return steps

    def _log_parsed_steps(self, steps: List[Dict[str, Any]]):
        """日志记录解析到的步骤 (坐标基于截图分辨率, 将在执行时自动缩放)"""
        iw, ih = self._screenshot_size
        sw, sh = self._screen_size
        for idx, step in enumerate(steps):
            stype = step.get("type", "unknown")
            desc = step.get("description", "")
            x_val, y_val = step.get("x"), step.get("y")
            if x_val is not None or y_val is not None:
                logger.info(f"[UFOAgent] 步骤 {idx+1}: type={stype}, 截图坐标=({x_val},{y_val}), 截图={iw}x{ih}, 屏幕={sw}x{sh}")
                if iw > 0 and x_val is not None and (int(x_val) < 0 or int(x_val) > iw):
                    logger.warning(f"[UFOAgent] x={x_val} 超出截图宽度 [0, {iw}], 缩放后可能超出屏幕")
                if ih > 0 and y_val is not None and (int(y_val) < 0 or int(y_val) > ih):
                    logger.warning(f"[UFOAgent] y={y_val} 超出截图高度 [0, {ih}], 缩放后可能超出屏幕")
            else:
                logger.info(f"[UFOAgent] 步骤 {idx+1}: type={stype}, 无坐标参数, 描述='{desc}'")

    def _extract_json_steps(self, text: str) -> List[Dict[str, Any]]:
        """从 LLM 响应文本中提取 JSON 步骤"""
        steps = self._raw_extract_json(text)

        # 过滤掉非 dict 元素 (LLM 有时输出 step1:"描述" 这样的字符串值)
        steps = [s if isinstance(s, dict) else {"description": str(s)} for s in steps if s]

        # 字段名归一化: LLM 有时用 "action" 代替 "type"
        steps = self._normalize_step_fields(steps)

        # 过滤掉类型推断失败的步骤
        steps = [s for s in steps if not (isinstance(s, dict) and s.pop("_skip_invalid_type", False))]

        if not steps:
            logger.warning(f"[UFOAgent] 无法从响应中提取有效 JSON steps: {text[:200]}...")
        return steps

    def _raw_extract_json(self, text: str) -> List[Dict[str, Any]]:
        """从文本中提取 JSON 步骤（原始提取，不做归一化）"""
        # LLM 输出的 steps 数组别名
        _steps_aliases = ("steps", "plan", "actions", "operations", "execution_plan")

        def _extract(data):
            """从解析后的 JSON 数据中提取步骤列表"""
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                # 优先查找 steps/plan 等键
                for alias in _steps_aliases:
                    if alias in data:
                        return data[alias]
                # 备用: next_steps 是 LLM reflection 格式中常见的键（值为字符串列表）
                # 将自然语言描述转换为 dict 步骤，后续由 _normalize_step_fields 推断 type
                if "next_steps" in data:
                    _ns = data["next_steps"]
                    if isinstance(_ns, list):
                        _converted = []
                        for item in _ns:
                            if isinstance(item, str) and item.strip():
                                _converted.append({"description": item.strip()})
                            elif isinstance(item, dict):
                                _converted.append(item)
                        if _converted:
                            logger.info(f"[UFOAgent] 从 next_steps 提取到 {len(_converted)} 个描述步骤，将尝试推断操作类型")
                            return _converted
                # step1/step2/step3... 键模式: LLM 有时输出 {"step1": "...", "step2": "..."}
                step_keys = sorted(
                    [k for k in data.keys() if re.match(r'^step\d+$', k)],
                    key=lambda k: int(re.search(r'(\d+)$', k).group())
                )
                if step_keys:
                    return [data[k] for k in step_keys]
                # 单个 dict 且具有 action 类字段 → 包装为列表
                if any(k in data for k in ("type", "action", "operation", "function")):
                    return [data]
            return None

        # 尝试提取 ```json ... ``` 代码块
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?\s*```', text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1).strip())
                result = _extract(data)
                if result is not None:
                    return result
            except json.JSONDecodeError:
                logger.warning("[UFOAgent] JSON 解析失败（代码块方式），尝试其他方式")

        # 尝试直接解析整个文本为 JSON
        try:
            data = json.loads(text.strip())
            result = _extract(data)
            if result is not None:
                return result
        except json.JSONDecodeError:
            pass

        # 尝试找到第一个 { 和最后一个 } 之间的内容
        brace_start = text.find('{')
        brace_end = text.rfind('}')
        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            try:
                data = json.loads(text[brace_start:brace_end + 1])
                result = _extract(data)
                if result is not None:
                    return result
            except json.JSONDecodeError:
                pass

        return []

    @staticmethod
    def _normalize_step_fields(steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """归一化步骤字段名，兼容 LLM 输出的字段名变体"""
        # LLM 常见的字段名映射: action/operation → type
        action_aliases = {"action", "operation", "function", "command"}
        # 有效操作类型集合
        _valid_types = {a["name"] for a in UFO_AVAILABLE_ACTIONS}
        # type 值中的通用占位符 (LLM 经常输出的非操作类型)
        _generic_type_values = {"action", "step", "task", "操作", "execute", "do"}

        # description 关键词 → 操作类型 的推断映射
        _desc_keywords_to_type = [
            (["打开", "启动", "运行", "open", "launch", "start", "run app", "focus", "open_or_focus", "打开应用", "启动应用"], "open_app"),
            (["点击", "click", "press", "tap", "select", "选择"], "click"),
            (["双击", "double", "dblclick"], "double_click"),
            (["输入", "打字", "type text", "type in", "输入文本", "填写", "fill", "搜索", "search", "输入搜索"], "type"),
            (["编辑", "edit", "set_edit", "set text", "写入"], "set_edit_text"),
            (["键盘", "keyboard", "快捷键", "hotkey", "组合键", "ctrl+", "alt+", "shift+"], "keyboard_input"),
            (["按键", "keypress", "press key", "按"], "keypress"),
            (["滚动", "scroll", "向下", "向上", "翻页"], "scroll"),
            (["移动", "move", "hover"], "move"),
            (["拖拽", "drag", "拖动"], "drag"),
            (["等待", "wait", "sleep", "延迟"], "wait"),
            (["命令", "command", "cmd", "powershell", "shell", "terminal", "执行命令"], "run_command"),
            (["检查进程", "check process", "进程", "process"], "check_process"),
        ]
        # LLM 常见伪类型名 → 正确类型的直接映射 (type 值纠正)
        _pseudo_type_map = {
            "open_or_focus_app": "open_app",
            "open_app_and_focus": "open_app",
            "focus_app": "open_app",
            "launch_app": "open_app",
            "start_app": "open_app",
            "search": "type",
            "search_song": "type",
            "search_music": "type",
            "play_song": "click",
            "play_music": "click",
            "play": "click",
            "navigate": "click",
            "find": "scroll",
            "switch_tab": "click",
            "switch_window": "click",
            "screenshot": "wait",
            "capture": "wait",
            "minimize": "click",
            "maximize": "click",
            "close": "click",
            "back": "click",
            "go_back": "click",
            "confirm": "click",
            "submit": "click",
            "cancel": "click",
            "login": "click",
            "logout": "click",
            "save": "click",
            "download": "click",
            "upload": "click",
            "next": "click",
            "previous": "click",
            "pause": "click",
            "resume": "click",
            "stop": "click",
            "volume": "click",
            "mute": "click",
            "fullscreen": "click",
            "enter": "keypress",
            "escape": "keypress",
            "tab": "keypress",
            "return": "keypress",
        }

        def _infer_type_from_description(desc: str) -> Optional[str]:
            """根据 description 文本推断操作类型"""
            if not desc:
                return None
            desc_lower = desc.lower()
            for keywords, action_type in _desc_keywords_to_type:
                for kw in keywords:
                    if kw in desc_lower:
                        return action_type
            return None

        for idx, step in enumerate(steps):
            # 字符串步骤转换: LLM 有时返回纯文本列表 ["打开QQ音乐", "输入发如雪", ...]
            if isinstance(step, str):
                step_text = step.strip()
                if not step_text:
                    continue
                inferred = _infer_type_from_description(step_text)
                steps[idx] = {"description": step_text, "type": inferred or "unknown"}
                if inferred:
                    logger.info(f"[UFOAgent] 字符串步骤 '{step_text}' 推断为 '{inferred}'")
                else:
                    logger.warning(f"[UFOAgent] 字符串步骤 '{step_text}' 无法推断操作类型，跳过")
                    steps[idx]["_skip_invalid_type"] = True
                step = steps[idx]
                continue
            if not isinstance(step, dict):
                continue
            # type 字段名归一化: alias → type
            if "type" not in step:
                for alias in action_aliases:
                    if alias in step:
                        alias_val = str(step[alias]).strip()
                        step["type"] = alias_val
                        # alias 值本身可能是描述文本（如 "点击搜索框"），需校验
                        if alias_val.lower() not in _valid_types:
                            step["description"] = alias_val
                        break

            # type 值验证与修正: 通用占位符 → alias 字段值 → description 推断 → 模糊匹配
            raw_type = str(step.get("type", "")).strip().lower()
            if raw_type in _generic_type_values:
                # 优先: 检查 alias 字段 (action/operation/...) 的值是否是有效操作类型
                # LLM 经常输出 {"type": "action", "action": "open_app", ...}
                alias_value_found = False
                for alias in action_aliases:
                    alias_val = str(step.get(alias, "")).strip().lower()
                    if alias_val and alias_val in _valid_types:
                        logger.info(f"[UFOAgent] type 值 '{raw_type}' 为通用占位符，从 '{alias}' 字段值 '{alias_val}' 获取真实类型")
                        step["type"] = alias_val
                        alias_value_found = True
                        break
                if not alias_value_found:
                    # 回退: 从 description 推断
                    desc = str(step.get("description", ""))
                    inferred = _infer_type_from_description(desc)
                    if inferred:
                        logger.info(f"[UFOAgent] type 值 '{raw_type}' 为通用占位符，根据 description '{desc}' 推断为 '{inferred}'")
                        step["type"] = inferred
                    else:
                        logger.warning(f"[UFOAgent] type 值 '{raw_type}' 为通用占位符且无法推断，description='{desc}'，跳过此步骤")
                        step["_skip_invalid_type"] = True
            elif raw_type and raw_type not in _valid_types:
                # type 值不是通用词但也不在有效列表中，先检查 alias 字段值
                alias_value_found = False
                for alias in action_aliases:
                    alias_val = str(step.get(alias, "")).strip().lower()
                    if alias_val and alias_val in _valid_types:
                        logger.info(f"[UFOAgent] type 值 '{raw_type}' 无效，从 '{alias}' 字段值 '{alias_val}' 获取真实类型")
                        step["type"] = alias_val
                        alias_value_found = True
                        break
                if not alias_value_found:
                    # 回退1: 伪类型名映射 (search_song → type, play_song → click 等)
                    matched = False
                    if raw_type in _pseudo_type_map:
                        _corrected = _pseudo_type_map[raw_type]
                        logger.info(f"[UFOAgent] type 值 '{raw_type}' 是伪类型，映射为 '{_corrected}'")
                        step["type"] = _corrected
                        matched = True
                    # 回退2: 模糊匹配 (英文类型名子串)
                    if not matched:
                        for vt in _valid_types:
                            if vt in raw_type or raw_type in vt:
                                logger.info(f"[UFOAgent] type 值 '{raw_type}' 模糊匹配到有效类型 '{vt}'")
                                step["type"] = vt
                                matched = True
                                break
                    # 回退3: 从 description 推断 (中文/英文描述文本 → 操作类型)
                    if not matched:
                        desc = str(step.get("description", "")).strip()
                        if desc:
                            inferred = _infer_type_from_description(desc)
                            if inferred:
                                logger.info(f"[UFOAgent] type 值 '{raw_type}' 无法匹配，根据 description '{desc}' 推断为 '{inferred}'")
                                step["type"] = inferred
                                matched = True
                    if not matched:
                        logger.warning(f"[UFOAgent] type 值 '{raw_type}' 无效且无法推断，跳过此步骤")
                        step["_skip_invalid_type"] = True

            # 坐标格式归一化: "coordinate"/"coordinates"/"pos" [x, y] → "x", "y"
            coord_aliases = {"coordinate", "coordinates", "pos", "location"}
            if "x" not in step or "y" not in step:
                for alias in coord_aliases:
                    if alias in step:
                        val = step[alias]
                        if isinstance(val, (list, tuple)) and len(val) >= 2:
                            if "x" not in step:
                                step["x"] = int(val[0])
                            if "y" not in step:
                                step["y"] = int(val[1])
                        elif isinstance(val, dict):
                            if "x" not in step and "x" in val:
                                step["x"] = val["x"]
                            if "y" not in step and "y" in val:
                                step["y"] = val["y"]
                        break

        # 坐标缺失标记: click/double_click/scroll/move/drag 缺少必要坐标时标记
        # 标记后不在此处跳过，由执行循环通过截图分析补充坐标
        _coord_required_types = {"click", "double_click", "scroll", "move", "drag"}
        for step in steps:
            if not isinstance(step, dict):
                continue
            stype = str(step.get("type", "")).lower()
            if stype not in _coord_required_types:
                continue
            _missing = False
            if stype in {"click", "double_click", "move"}:
                _missing = step.get("x") is None or step.get("y") is None
            elif stype == "scroll":
                _missing = step.get("scroll_y") is None and step.get("scroll_x") is None
            elif stype == "drag":
                _missing = (step.get("start_x") is None or step.get("start_y") is None
                            or step.get("end_x") is None or step.get("end_y") is None)
            if _missing:
                desc = step.get("description", step.get("target", ""))
                logger.info(f"[UFOAgent] 步骤 type={stype} 缺少必要坐标参数，标记待截图分析补充，desc='{desc}'")
                step["_needs_coord_analysis"] = True

        # 文本提取: type/set_edit_text 缺少 text 参数时，从 description 中提取
        _text_types = {"type", "set_edit_text"}
        for step in steps:
            if not isinstance(step, dict):
                continue
            if step.get("type") in _text_types and not step.get("text"):
                desc = str(step.get("description", ""))
                if desc:
                    # 占位词黑名单: 这些不是真实文本内容，而是描述中的占位符
                    _placeholder_words = {
                        "歌曲名称", "歌曲名", "歌名", "音乐名称",
                        "搜索内容", "搜索词", "搜索关键词", "关键词",
                        "文本内容", "文本", "内容", "输入内容",
                        "文件名", "文件", "路径", "目录",
                        "用户名", "密码", "账号",
                        "目标", "参数", "值",
                    }
                    _text_pats = [
                        r"输入[\"'\u300c\u300e](.+?)[\"'\u300d\u300f]",
                        r"[\"'\u300c\u300e](.+?)[\"'\u300d\u300f]",
                        r"输入\s*([^\s,，。；并\"'\u300c\u300d\u300e\u300f]+?)\s*(?:并|，|。|；|$)",
                    ]
                    for _tp in _text_pats:
                        _tm = re.search(_tp, desc)
                        if _tm:
                            _extracted = _tm.group(1).strip()
                            if _extracted and _extracted.lower() not in _placeholder_words:
                                step["text"] = _extracted
                                logger.info(f"[UFOAgent] 从 description 中提取 text='{_extracted}'")
                                break
                            elif _extracted:
                                logger.info(f"[UFOAgent] 提取到占位词 '{_extracted}'，跳过（等待 LLM 补全参数）")

        # open_app 参数补全: 从 description 提取 app_name 和 search_keyword
        # 常见中文应用名 → 进程名映射
        _app_name_map = {
            "qq音乐": "qqmusic", "qqmusic": "qqmusic",
            "微信": "wechat", "wechat": "wechat",
            "qq": "qq", "腾讯qq": "qq",
            "浏览器": "chrome", "chrome": "chrome",
            "谷歌浏览器": "chrome", "google chrome": "chrome",
            "edge": "msedge", "微软edge": "msedge",
            "记事本": "notepad", "notepad": "notepad",
            "计算器": "calc", "calculator": "calc",
            "文件管理器": "explorer", "资源管理器": "explorer", "explorer": "explorer",
            "设置": "settings", "settings": "settings",
            "网易云音乐": "cloudmusic", "neteasecloudmusic": "cloudmusic",
            "酷狗音乐": "kugou", "kugou": "kugou",
            "酷我音乐": "kuwo", "kuwo": "kuwo",
            "spotify": "spotify",
            "potplayer": "potplayer", "pot": "potplayer",
            "vscode": "code", "visual studio code": "code",
            "钉钉": "dingtalk", "dingtalk": "dingtalk",
            "飞书": "feishu", "lark": "feishu",
            "企业微信": "wxwork", "wxwork": "wxwork",
            "支付宝": "alipay", "alipay": "alipay",
            "抖音": "douyin", "douyin": "douyin",
            "bilibili": "bilibili", "哔哩哔哩": "bilibili", "b站": "bilibili",
            "百度网盘": "baidunetdisk", "baidunetdisk": "baidunetdisk",
            "wps": "wps", "wps office": "wps",
            "word": "winword", "excel": "excel", "powerpoint": "powerpnt",
            "steam": "steam", "epic": "epicgames",
            "telegram": "telegram",
        }
        for step in steps:
            if not isinstance(step, dict) or step.get("type") != "open_app":
                continue
            # 即使已有 app_name，也可能是中文名（如"qq音乐"）需要映射为进程名
            desc = str(step.get("description", "")).strip()
            # action 字段也常包含中文应用名
            action_val = str(step.get("action", "")).strip()
            current_app_name = str(step.get("app_name", "")).strip()
            # 合并 description + action + 当前 app_name 作为匹配来源
            _source = f"{desc} {action_val} {current_app_name}".strip()
            if not _source:
                continue
            _matched_app = None
            _matched_keyword = None
            # 先尝试精确匹配已知应用名
            for cn_name, process_name in _app_name_map.items():
                if cn_name in _source.lower() or cn_name in _source:
                    _matched_app = process_name
                    _matched_keyword = cn_name if any('\u4e00' <= c <= '\u9fff' for c in cn_name) else None
                    break
            if _matched_app:
                step["app_name"] = _matched_app
                # search_keyword 应该是应用中文名，用于系统搜索启动应用
                # 如果当前的 search_keyword 不在 _app_name_map 的值中（说明是 LLM 填错的），用映射值覆盖
                if _matched_keyword:
                    step["search_keyword"] = _matched_keyword
                logger.info(f"[UFOAgent] open_app 映射 app_name: '{current_app_name or desc[:20]}' → '{_matched_app}', search_keyword='{_matched_keyword}'")
            else:
                # 回退: 尝试通用正则提取应用名
                _am = re.search(r"(?:打开|启动|运行|open|launch|start)\s*(.+?)(?:应用|软件|程序|窗口|app|$|，|。|,)", _source, re.IGNORECASE)
                if _am:
                    _raw_app = _am.group(1).strip()
                    if _raw_app and len(_raw_app) <= 20:
                        step["app_name"] = _raw_app
                        logger.info(f"[UFOAgent] open_app 通用正则提取 app_name='{_raw_app}'")

        # 打开应用检测: click 步骤描述"打开/启动应用"时转换为 open_app
        _open_app_pats = [
            r"(?:点击|选择).*(?:图标|任务栏).*(?:打开|启动|运行)",
            r"(?:打开|启动|运行).*(?:图标|任务栏)",
        ]
        for step in steps:
            if not isinstance(step, dict) or step.get("type") != "click":
                continue
            desc = str(step.get("description", ""))
            if not desc:
                continue
            for _op in _open_app_pats:
                if re.search(_op, desc, re.IGNORECASE):
                    _am = re.search(r"(?:的|打开|启动|运行)\s*(.+?)(?:图标|应用|窗口|软件|程序)", desc)
                    if not _am:
                        _am = re.search(r"点击.*?(?:的)?\s*(.+?)(?:图标|应用|窗口|软件|程序)", desc)
                    if _am:
                        _app = _am.group(1).strip()
                        step["type"] = "open_app"
                        step["app_name"] = _app
                        step.pop("x", None)
                        step.pop("y", None)
                        logger.info(f"[UFOAgent] 检测到打开应用意图，click → open_app, app_name='{_app}'")
                    break

        return steps

    async def _execute_action(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行单个操作（通过 pyautogui 实现 UFO Action）"""
        action_type = action.get("type", "unknown").strip().lower()
        description = action.get("description", "")

        result = {
            "action_type": action_type,
            "description": description,
            "success": False,
            "error": None,
            "coordinates": {},  # 实际执行的屏幕坐标 (问题5: 失败坐标负反馈)
        }

        sw, sh = self._screen_size
        coord_keys = ["x", "y", "start_x", "start_y", "end_x", "end_y", "scroll_x", "scroll_y"]
        coords = {k: action.get(k) for k in coord_keys if action.get(k) is not None}

        if coords:
            logger.info(f"[UFOAgent] 操作 '{action_type}' 坐标参数: {coords} | 屏幕分辨率: {sw}x{sh}")
            for ck in ["x", "y", "start_x", "start_y", "end_x", "end_y"]:
                val = action.get(ck)
                if val is not None:
                    int_val = int(val)
                    if sw > 0 and (int_val < 0 or int_val > sw) and "x" in ck:
                        logger.warning(f"[UFOAgent] 坐标 {ck}={int_val} 超出屏幕宽度 [0, {sw}]")
                    if sh > 0 and (int_val < 0 or int_val > sh) and "y" in ck:
                        logger.warning(f"[UFOAgent] 坐标 {ck}={int_val} 超出屏幕高度 [0, {sh}]")

        # Agent-S resize_coordinates: 截图坐标 → 屏幕坐标
        scale = self._screenshot_scale

        # 需要坐标的操作: 检查坐标是否提供且合法
        _coord_required_actions = {"click", "double_click", "scroll", "move", "drag"}
        if action_type in _coord_required_actions:
            has_x = action.get("x") is not None and int(action.get("x", 0)) > 0
            has_y = action.get("y") is not None and int(action.get("y", 0)) > 0
            if not (has_x and has_y):
                result["error"] = f"操作 '{action_type}' 缺少有效的坐标参数 (x={action.get('x')}, y={action.get('y')})，已跳过"
                logger.warning(f"[UFOAgent] {result['error']}")
                return result

        # 需要文本的操作: 检查 text 是否提供
        if action_type in ("type", "set_edit_text"):
            text_val = str(action.get("text", "")).strip()
            if not text_val:
                result["error"] = f"操作 '{action_type}' 缺少有效的 text 参数，已跳过"
                logger.warning(f"[UFOAgent] {result['error']}")
                return result

        try:
            if action_type == "click":
                # 点击前截图记录页面 hash，供导航变化检测使用
                _pre_click_img, _ = self._capture_screenshot(label=f"pre_{action_type}")
                if _pre_click_img:
                    result["screen_hash"] = self._compute_image_hash(_pre_click_img)
                x = int(action.get("x", 0))
                y = int(action.get("y", 0))
                if scale != 1.0:
                    x, y = int(x / scale), int(y / scale)
                    logger.info(f"[UFOAgent] 坐标缩放: 截图({action.get('x')},{action.get('y')}) → 屏幕({x},{y}), scale={scale:.4f}")
                button = action.get("button", "left")
                pyautogui.click(x=x, y=y, button=button)
                result["success"] = True
                result["coordinates"] = {"x": x, "y": y, "screenshot_x": action.get("x"), "screenshot_y": action.get("y")}

            elif action_type == "double_click":
                _pre_dbl_img, _ = self._capture_screenshot(label=f"pre_{action_type}")
                if _pre_dbl_img:
                    result["screen_hash"] = self._compute_image_hash(_pre_dbl_img)
                x = int(action.get("x", 0))
                y = int(action.get("y", 0))
                if scale != 1.0:
                    x, y = int(x / scale), int(y / scale)
                    logger.info(f"[UFOAgent] 坐标缩放: 截图({action.get('x')},{action.get('y')}) → 屏幕({x},{y}), scale={scale:.4f}")
                pyautogui.doubleClick(x=x, y=y)
                result["success"] = True
                result["coordinates"] = {"x": x, "y": y, "screenshot_x": action.get("x"), "screenshot_y": action.get("y")}

            elif action_type == "type":
                text = str(action.get("text", ""))
                interval = float(action.get("interval", 0.02))
                # P1: 输入前先全选清空，防止新旧文本拼接
                # 使用 Ctrl+A 全选 + Delete 删除，确保输入框干净
                pyautogui.hotkey('ctrl', 'a')
                await asyncio.sleep(0.15)
                pyautogui.press('delete')
                await asyncio.sleep(0.15)
                await self._type_text(text, interval)
                result["success"] = True

            elif action_type == "set_edit_text":
                text = str(action.get("text", ""))
                clear = action.get("clear_current_text", False)
                if clear:
                    pyautogui.hotkey('ctrl', 'a')
                    await asyncio.sleep(0.2)
                await self._type_text(text, 0.02)
                result["success"] = True

            elif action_type == "keyboard_input":
                keys = str(action.get("keys", ""))
                parts = re.split(r'[+\-]', keys)
                pyautogui.hotkey(*[p.strip() for p in parts if p.strip()])
                result["success"] = True

            elif action_type == "keypress":
                keys = action.get("keys", "")
                if isinstance(keys, list):
                    pyautogui.hotkey(*keys)
                else:
                    pyautogui.press(keys)
                result["success"] = True

            elif action_type == "scroll":
                x = int(action.get("x", 0))
                y = int(action.get("y", 0))
                scroll_y = int(action.get("scroll_y", -3))
                if scale != 1.0:
                    x, y = int(x / scale), int(y / scale)
                pyautogui.scroll(scroll_y, x=x, y=y)
                result["success"] = True
                result["coordinates"] = {"x": x, "y": y}

            elif action_type == "move":
                x = int(action.get("x", 0))
                y = int(action.get("y", 0))
                if scale != 1.0:
                    x, y = int(x / scale), int(y / scale)
                pyautogui.moveTo(x=x, y=y)
                result["success"] = True
                result["coordinates"] = {"x": x, "y": y}

            elif action_type == "drag":
                start_x = int(action.get("start_x", 0))
                start_y = int(action.get("start_y", 0))
                end_x = int(action.get("end_x", 0))
                end_y = int(action.get("end_y", 0))
                duration = float(action.get("duration", 0.5))
                if scale != 1.0:
                    start_x, start_y = int(start_x / scale), int(start_y / scale)
                    end_x, end_y = int(end_x / scale), int(end_y / scale)
                    logger.debug(f"[UFOAgent] 拖拽坐标缩放: scale={scale:.4f}")
                pyautogui.moveTo(start_x, start_y)
                pyautogui.dragTo(end_x, end_y, duration=duration)
                result["success"] = True
                result["coordinates"] = {"start_x": start_x, "start_y": start_y, "end_x": end_x, "end_y": end_y}

            elif action_type == "wait":
                seconds = float(action.get("seconds", 2))
                await asyncio.sleep(seconds)
                result["success"] = True

            elif action_type == "run_command":
                command = str(action.get("command", ""))
                shell = str(action.get("shell", "cmd"))
                if not command:
                    result["error"] = "run_command 缺少 command 参数"
                else:
                    cmd_result = self._run_system_command(command, shell=shell)
                    result["success"] = cmd_result["success"]
                    result["command_output"] = {
                        "stdout": cmd_result["stdout"],
                        "stderr": cmd_result["stderr"],
                        "returncode": cmd_result["returncode"]
                    }
                    if not cmd_result["success"]:
                        result["error"] = f"命令执行失败: {cmd_result['stderr'][:200]}"

            elif action_type == "check_process":
                process_name = str(action.get("process_name", ""))
                if not process_name:
                    result["error"] = "check_process 缺少 process_name 参数"
                else:
                    proc_result = self._check_process_running(process_name)
                    result["success"] = True
                    result["process_info"] = proc_result

            elif action_type == "open_app":
                app_name = str(action.get("app_name", ""))
                search_keyword = action.get("search_keyword")
                if not app_name:
                    result["error"] = "open_app 缺少 app_name 参数"
                else:
                    app_result = self._open_or_focus_app(app_name, search_keyword)
                    result["success"] = app_result["success"]
                    result["app_action"] = app_result["action"]
                    result["detail"] = app_result["detail"]
                    if not app_result["success"]:
                        result["error"] = app_result["detail"]
                    # 打开应用后等待窗口出现并验证前台窗口属于目标进程
                    if app_result["success"]:
                        await asyncio.sleep(2)
                        # 验证: 检查前台窗口进程是否匹配目标应用
                        _fg_proc = self._get_foreground_process_name()
                        _target_proc = app_name.lower()
                        if _fg_proc and _target_proc:
                            if _target_proc in _fg_proc or _fg_proc in _target_proc:
                                logger.info(f"[UFOAgent] open_app 窗口验证通过: 前台进程 '{_fg_proc}' 匹配目标 '{_target_proc}'")
                            else:
                                logger.warning(f"[UFOAgent] open_app 窗口验证失败: 前台进程 '{_fg_proc}' 不匹配目标 '{_target_proc}'，尝试进程名回退等待")
                                # 用进程名再等待 N 秒
                                _wait_ok = await self._wait_for_target_window(process_name=_target_proc, timeout=settings.AGENT_PLAN_RETRY_OPEN_APP_TIMEOUT)
                                if not _wait_ok:
                                    logger.warning(f"[UFOAgent] open_app 进程名回退等待也超时，标记为可能未成功")
                                    result["detail"] += " (警告: 窗口验证未确认目标进程在前台)"

            else:
                result["error"] = f"不支持的操作类型: {action_type}"

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"[UFOAgent] 执行操作 {action_type} 失败: {e}")

        return result

    @staticmethod
    def _split_special_keys(text: str) -> Tuple[str, List[str]]:
        """将文本中的 {ENTER}, {TAB}, {ESC} 等特殊键名分离出来"""
        special_key_map = {
            'enter': 'enter', 'return': 'enter',
            'tab': 'tab', 'escape': 'escape', 'esc': 'escape',
            'backspace': 'backspace', 'delete': 'delete', 'del': 'delete',
            'home': 'home', 'end': 'end',
            'pageup': 'pageup', 'pagedown': 'pagedown',
            'up': 'up', 'down': 'down', 'left': 'left', 'right': 'right',
            'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4',
            'f5': 'f5', 'f6': 'f6', 'f7': 'f7', 'f8': 'f8',
            'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12',
            'space': 'space',
        }

        pattern = r'\{([^}]+)\}'
        parts = re.split(pattern, text)

        clean_text = ""
        special_keys = []

        for i, part in enumerate(parts):
            if i % 2 == 0:
                clean_text += part
            else:
                key_name = part.strip().lower()
                mapped = special_key_map.get(key_name, key_name)
                if mapped:
                    special_keys.append(mapped)

        return clean_text, special_keys

    async def _type_text(self, text: str, interval: float = 0.02):
        """智能文本输入：ASCII 用 typewrite，非 ASCII 用剪贴板粘贴"""
        if not text:
            return

        clean_text, special_keys = self._split_special_keys(text)

        if clean_text:
            is_ascii = all(ord(c) < 128 for c in clean_text)
            if is_ascii:
                pyautogui.typewrite(clean_text, interval=interval)
            else:
                pyperclip.copy(clean_text)
                await asyncio.sleep(0.1)
                pyautogui.hotkey('ctrl', 'v')
                await asyncio.sleep(0.1)

        for key in special_keys:
            await asyncio.sleep(0.05)
            pyautogui.press(key)

    # ==================== 系统进程检测和应用启动 ====================

    @staticmethod
    def _run_system_command(command: str, shell: str = "cmd", timeout: int = 15) -> Dict[str, Any]:
        """
        执行系统命令并返回结果

        Args:
            command: 要执行的命令
            shell: 使用的 shell ("cmd" 或 "powershell")
            timeout: 超时时间（秒）

        Returns:
            Dict: {"success": bool, "stdout": str, "stderr": str, "returncode": int}
        """
        try:
            if shell == "powershell":
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", command],
                    capture_output=True, text=True, timeout=timeout,
                    encoding="utf-8", errors="replace"
                )
            else:
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True,
                    timeout=timeout, encoding="gbk", errors="replace"
                )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "stdout": "", "stderr": f"命令执行超时 ({timeout}秒)", "returncode": -1}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}

    @staticmethod
    def _check_process_running(process_name: str) -> Dict[str, Any]:
        """
        检查指定进程是否正在运行

        支持模糊匹配进程名（如 "qqmusic" 匹配 "QQMusic.exe"）

        Args:
            process_name: 进程名（支持模糊匹配，不区分大小写）

        Returns:
            Dict: {
                "running": bool,
                "processes": [{"pid": int, "name": str, "cmdline": str}],
                "match_count": int
            }
        """
        try:
            ps_cmd = (
                f"Get-Process | Where-Object {{$_.ProcessName -like '*{process_name}*'}} | "
                "Select-Object Id, ProcessName | ConvertTo-Json -Depth 1"
            )
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True, text=True, timeout=10,
                encoding="utf-8", errors="replace"
            )

            processes = []
            if result.stdout.strip():
                try:
                    data = json.loads(result.stdout.strip())
                    if isinstance(data, dict):
                        data = [data]
                    for p in data:
                        processes.append({
                            "pid": p.get("Id", 0),
                            "name": p.get("ProcessName", ""),
                            "cmdline": p.get("CmdLine", "")
                        })
                except (json.JSONDecodeError, TypeError):
                    # JSON 解析失败，用更简单的命令重试
                    simple_result = subprocess.run(
                        ["powershell", "-NoProfile", "-Command",
                         f"Get-Process | Where-Object {{$_.ProcessName -like '*{process_name}*'}} | "
                         f"Select-Object Id, ProcessName | ConvertTo-Json -Depth 1"],
                        capture_output=True, text=True, timeout=10,
                        encoding="utf-8", errors="replace"
                    )
                    if simple_result.stdout.strip():
                        try:
                            data = json.loads(simple_result.stdout.strip())
                            if isinstance(data, dict):
                                data = [data]
                            for p in data:
                                processes.append({
                                    "pid": p.get("Id", 0),
                                    "name": p.get("ProcessName", ""),
                                    "cmdline": ""
                                })
                        except (json.JSONDecodeError, TypeError):
                            pass

            return {
                "running": len(processes) > 0,
                "processes": processes,
                "match_count": len(processes)
            }

        except Exception as e:
            return {"running": False, "processes": [], "match_count": 0, "error": str(e)}

    @staticmethod
    def _get_taskbar_apps() -> List[str]:
        """
        获取 Windows 任务栏中可见的应用窗口标题列表

        Returns:
            List[str]: 窗口标题列表
        """
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 # 获取有可见窗口的进程（排除桌面和任务栏本身）
                 "(Get-Process | Where-Object {$_.MainWindowTitle -ne '' -and $_.ProcessName -ne 'explorer'} | "
                 "Select-Object -ExpandProperty MainWindowTitle) | ConvertTo-Json -Depth 1"],
                capture_output=True, text=True, timeout=10,
                encoding="utf-8", errors="replace"
            )
            titles = []
            if result.stdout.strip():
                try:
                    data = json.loads(result.stdout.strip())
                    if isinstance(data, list):
                        titles = [t for t in data if t]
                    elif isinstance(data, str):
                        titles = [data]
                except json.JSONDecodeError:
                    pass
            return titles
        except Exception:
            return []

    @staticmethod
    def _get_tray_apps() -> List[str]:
        """
        获取 Windows 系统托盘中的后台应用名称列表

        Returns:
            List[str]: 后台应用名称列表
        """
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 # 查找系统托盘区域的通知图标
                 "$shell = New-Object -ComObject Shell.Application; "
                 "$tray = $shell.NameSpace('shell:Notification'); "
                 "($tray.Items() | Select-Object -ExpandProperty Name) -join ', '"],
                capture_output=True, text=True, timeout=10,
                encoding="utf-8", errors="replace"
            )
            names = []
            if result.stdout.strip():
                names = [n.strip() for n in result.stdout.strip().split(",") if n.strip()]
            return names
        except Exception:
            return []

    def _open_or_focus_app(self, app_name: str, search_keyword: Optional[str] = None) -> Dict[str, Any]:
        """
        打开或聚焦到指定应用程序

        执行流程（按优先级依次检测）:
        1. 任务栏可见窗口: 检查是否有可见窗口 → 激活前置
        2. 系统托盘: 检查底部右侧托盘区域 → 从托盘恢复窗口
        3. 进程检测: 检查进程是否运行 → 尝试唤出或启动新实例
        4. 系统搜索: 搜索快捷方式 → ms-search → 常见安装路径

        Args:
            app_name: 应用程序名称（用于进程匹配）
            search_keyword: 系统搜索关键词（如果与 app_name 不同）

        Returns:
            Dict: {"success": bool, "action": str, "detail": str}
        """
        search = search_keyword or app_name
        app_lower = app_name.lower()
        search_lower = search.lower()

        # ====== 步骤 1: 检查任务栏可见窗口 ======
        logger.info(f"[open_app] 步骤1/4: 检查任务栏可见窗口 (app='{app_name}')")
        window_titles = self._get_taskbar_apps()
        logger.info(f"[open_app] 任务栏可见窗口 ({len(window_titles)}): {window_titles[:10]}")

        matched_title = None
        for title in window_titles:
            if app_lower in title.lower() or search_lower in title.lower():
                matched_title = title
                break

        if matched_title:
            logger.info(f"[open_app] 在任务栏找到匹配窗口: '{matched_title}'，尝试激活前置")
            cmd = (
                f"$w = (Get-Process | Where-Object {{$_.ProcessName -like '*{app_name}*' -and $_.MainWindowTitle -ne ''}} | "
                f"Select-Object -First 1); "
                f"if ($w) {{ (New-Object -ComObject WScript.Shell).AppActivate($w.MainWindowTitle); 'activated' }} "
                f"else {{ 'no_window' }}"
            )
            result = self._run_system_command(cmd, shell="powershell")
            if "activated" in result.get("stdout", ""):
                logger.info(f"[open_app] 步骤1 成功: 已激活前置窗口 '{matched_title}'")
                return {
                    "success": True,
                    "action": "activated_existing_window",
                    "detail": f"应用 '{app_name}' 在任务栏有可见窗口 '{matched_title}'，已激活前置"
                }
            logger.warning(f"[open_app] 步骤1 激活失败，继续下一步...")

        # ====== 步骤 2: 检查系统托盘（底部右侧区域） ======
        logger.info(f"[open_app] 步骤2/4: 检查系统托盘区域 (app='{app_name}')")
        tray_apps = self._get_tray_apps()
        logger.info(f"[open_app] 系统托盘应用 ({len(tray_apps)}): {tray_apps[:10]}")

        matched_tray = None
        for tray_name in tray_apps:
            if app_lower in tray_name.lower() or search_lower in tray_name.lower():
                matched_tray = tray_name
                break

        if matched_tray:
            logger.info(f"[open_app] 在系统托盘找到匹配: '{matched_tray}'，尝试从托盘恢复窗口")
            # 托盘中找到应用 → 通过进程检查并恢复窗口
            process_info = self._check_process_running(app_name)
            if process_info["running"]:
                restore_result = self._try_restore_process_window(app_name)
                if restore_result["success"]:
                    logger.info(f"[open_app] 步骤2 成功: 从托盘恢复窗口 ({restore_result['action']})")
                    restore_result["detail"] = f"应用 '{app_name}' 在系统托盘 '{matched_tray}' 运行，已从后台恢复到前台"
                    return restore_result
            logger.warning(f"[open_app] 步骤2 恢复失败，继续下一步...")
        else:
            logger.info(f"[open_app] 步骤2: 系统托盘中未找到 '{app_name}'")

        # ====== 步骤 3: 检查进程中是否运行 ======
        logger.info(f"[open_app] 步骤3/4: 检查进程列表 (app='{app_name}')")
        process_info = self._check_process_running(app_name)
        logger.info(f"[open_app] 进程检查结果: running={process_info['running']}, count={process_info['match_count']}")
        if process_info['running']:
            for p in process_info.get("processes", []):
                logger.info(f"[open_app]   - PID={p['pid']}, Name={p['name']}")

        if process_info["running"]:
            logger.info(f"[open_app] 进程 '{app_name}' 正在运行，尝试唤出窗口")
            restore_result = self._try_restore_process_window(app_name)
            if restore_result["success"]:
                logger.info(f"[open_app] 步骤3 成功: 从进程唤出窗口 ({restore_result['action']})")
                return restore_result
            logger.warning(f"[open_app] 步骤3 唤出失败，继续下一步...")
        else:
            logger.info(f"[open_app] 步骤3: 进程 '{app_name}' 未运行")

        # ====== 步骤 4: 通过系统搜索启动应用 ======
        logger.info(f"[open_app] 步骤4/4: 系统搜索并启动应用 (keyword='{search}')")
        launch_result = self._try_launch_app(app_name, search)
        if launch_result["success"]:
            logger.info(f"[open_app] 步骤4 成功: {launch_result['detail']}")
            return launch_result

        logger.error(f"[open_app] 所有步骤均失败，无法打开应用 '{app_name}'")
        return {
            "success": False,
            "action": "failed",
            "detail": f"无法启动应用 '{app_name}'，请确认应用名称正确或手动启动"
        }

    def _try_restore_process_window(self, app_name: str) -> Dict[str, Any]:
        """尝试从进程恢复/激活应用窗口（托盘恢复、新实例启动等）"""
        activate_cmd = (
            f"$proc = (Get-Process | Where-Object {{$_.ProcessName -like '*{app_name}*'}} | Select-Object -First 1); "
            "if ($proc) { "
            "  try { "
            "    $hwnd = $proc.MainWindowHandle; "
            "    if ($hwnd -eq 0) { "
            "      Start-Process -FilePath $proc.Path; "
            "      'started_new_instance' "
            "    } else { "
            "      Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32Api { [DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow); public static extern bool SetForegroundWindow(IntPtr hWnd); }'; "
            "      [Win32Api]::ShowWindow($hwnd, 6); Start-Sleep -Milliseconds 400; "
            "      [Win32Api]::ShowWindow($hwnd, 9); Start-Sleep -Milliseconds 300; "
            "      [Win32Api]::SetForegroundWindow($hwnd); "
            "      'restored_and_activated' "
            "    } "
            "  } catch { 'activation_failed:' + $_.Exception.Message } "
            "} else { 'process_not_found' }"
        )
        result = self._run_system_command(activate_cmd, shell="powershell")
        stdout = result.get("stdout", "").strip()
        logger.info(f"[open_app] 恢复窗口结果: {stdout}")

        if "restored_and_activated" in stdout:
            return {
                "success": True,
                "action": "restored_from_tray",
                "detail": f"应用 '{app_name}' 窗口已从后台恢复到前台"
            }
        elif "started_new_instance" in stdout:
            return {
                "success": True,
                "action": "started_new_instance",
                "detail": f"应用 '{app_name}' 进程在运行但无窗口句柄，已启动新实例"
            }

        # 最后手段：Start-Process 重新启动
        start_cmd = f"Start-Process -FilePath (Get-Process -Name '*{app_name}*' | Select-Object -First 1).Path"
        result = self._run_system_command(start_cmd, shell="powershell", timeout=10)
        if result["success"]:
            return {
                "success": True,
                "action": "started_from_existing_process",
                "detail": f"应用 '{app_name}' 进程在运行，已尝试通过 Start-Process 重新启动"
            }

        return {"success": False, "action": "restore_failed", "detail": f"无法恢复应用 '{app_name}' 的窗口"}

    def _try_launch_app(self, app_name: str, search: str) -> Dict[str, Any]:
        """通过快捷方式搜索、ms-search、常见安装路径等方式启动应用"""
        # 方法 A: 搜索开始菜单快捷方式
        logger.info(f"[open_app] 方法A: 搜索开始菜单快捷方式 (keyword='{search}')")
        search_cmd = (
            f"$searchTerm = '{search}'; "
            "$apps = Get-ChildItem 'C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs' -Recurse -Filter '*.lnk' -ErrorAction SilentlyContinue | "
            "Where-Object { $_.Name -like \"*$searchTerm*\" }; "
            "$apps += Get-ChildItem \"$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\" -Recurse -Filter '*.lnk' -ErrorAction SilentlyContinue | "
            "Where-Object { $_.Name -like \"*$searchTerm*\" }; "
            "if ($apps) { $apps[0].FullName } else { 'not_found' }"
        )
        result = self._run_system_command(search_cmd, shell="powershell", timeout=15)
        shortcut_path = result.get("stdout", "").strip()
        logger.info(f"[open_app] 方法A 结果: {shortcut_path}")

        if shortcut_path and shortcut_path != "not_found":
            # 优先用 Invoke-Item 启动 .lnk（更可靠），回退到 Start-Process
            start_cmd = f"Invoke-Item -Path '{shortcut_path}'"
            start_result = self._run_system_command(start_cmd, shell="powershell", timeout=15)
            if not start_result["success"]:
                logger.warning(f"[open_app] 方法A Invoke-Item 失败: {start_result.get('stderr', '')}, 尝试 Start-Process")
                start_cmd = f"Start-Process '{shortcut_path}'"
                start_result = self._run_system_command(start_cmd, shell="powershell", timeout=15)
            if start_result["success"]:
                return {
                    "success": True,
                    "action": "launched_via_shortcut",
                    "detail": f"应用 '{app_name}' 已通过快捷方式启动"
                }
            else:
                logger.warning(f"[open_app] 方法A 快捷方式启动失败: stderr={start_result.get('stderr', '')}")

        # 方法 B: Windows 搜索 (ms-search) — 作为最后手段，打开搜索让用户手动操作
        logger.info(f"[open_app] 方法B: 打开 Windows 搜索 (keyword='{search}')")
        search_cmd2 = f"Start-Process 'ms-search://query={search}'"
        result2 = self._run_system_command(search_cmd2, shell="powershell", timeout=10)
        if result2["success"]:
            return {
                "success": True,
                "action": "opened_search",
                "detail": f"已打开 Windows 搜索（关键词: {search}），将在搜索结果中查找并启动应用 '{app_name}'"
            }

        # 方法 C: 搜索常见安装路径
        logger.info(f"[open_app] 方法C: 搜索常见安装路径 (keyword='{search}')")
        common_paths_cmd = (
            f"$searchTerm = '*{search}*'; "
            "$paths = @('C:\\Program Files', 'C:\\Program Files (x86)'); "
            "$found = $null; "
            "foreach ($p in $paths) { "
            "  $found = Get-ChildItem $p -Recurse -Filter '*.exe' -Depth 2 -ErrorAction SilentlyContinue | "
            "    Where-Object { $_.Name -like $searchTerm } | Select-Object -First 1; "
            "  if ($found) { break } "
            "}; "
            "if ($found) { $found.FullName } else { 'not_found' }"
        )
        result3 = self._run_system_command(common_paths_cmd, shell="powershell", timeout=20)
        exe_path = result3.get("stdout", "").strip()
        logger.info(f"[open_app] 方法C 结果: {exe_path}")

        if exe_path and exe_path != "not_found":
            start_cmd = f"Start-Process '{exe_path}'"
            start_result = self._run_system_command(start_cmd, shell="powershell", timeout=15)
            if start_result["success"]:
                return {
                    "success": True,
                    "action": "launched_via_exe",
                    "detail": f"应用 '{app_name}' 已通过可执行文件 '{exe_path}' 启动"
                }

        return {"success": False, "action": "launch_failed", "detail": f"无法启动应用 '{app_name}'"}


__all__ = ['UFOAgent']
