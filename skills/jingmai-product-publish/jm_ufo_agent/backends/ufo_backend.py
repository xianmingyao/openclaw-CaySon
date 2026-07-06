# jm_ufo_agent/backends/ufo_backend.py
"""UFO v1 DesktopBackend 实现 — 真实 Windows GUI 操作闭环。"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.commands.base import Command


class UfoDesktopBackend:
    """基于 UFO v1 的真实桌面 backend。

    # UFO v1 使用 Windows UIAutomation + 剪贴板实现 GUI 操作。
    # click → 定位元素 → 调用 Invoke 或 Click 模式。
    # fill → 剪贴板写入 → Ctrl+V 粘贴，绕过输入法问题。
    # submit → 点击按钮（草稿/发布），SafetyPolicy 在上层已拦截发布。
    # ufo_root 指向 UFO v1 项目根目录，动态加载 controller/inspector。
    """

    def __init__(self, ufo_root: Path | None = None):
        """初始化 UFO backend。"""
        self.ufo_root = ufo_root or self._detect_ufo_root()
        self._controller: Any = None

    @staticmethod
    def _detect_ufo_root() -> Path:
        """自动检测 UFO v1 安装路径。"""
        import os

        env_path = os.environ.get("UFO_ROOT")
        if env_path:
            return Path(env_path)

        candidates = [
            Path.home() / "ufo",
            Path("C:/ufo"),
            Path("D:/ufo"),
        ]
        for p in candidates:
            if p.exists():
                return p

        return Path("ufo")  # fallback，后续操作会失败并给出明确错误

    def _ensure_loaded(self) -> None:
        """延迟加载 UFO 模块。"""
        if self._controller is not None:
            return

        if not self.ufo_root.exists():
            raise RuntimeError(f"UFO 根目录不存在: {self.ufo_root}")

        import sys

        ufo_str = str(self.ufo_root)
        if ufo_str not in sys.path:
            sys.path.insert(0, ufo_str)

        try:
            from ufo.agents.agent.ufo_controller import UFOController
            self._controller = UFOController
        except ImportError:
            logger.warning("UFO 模块不可用，降级为 StubController — 所有 GUI 操作将失败")
            self._controller = _StubController()

    async def execute(self, command: Command) -> AgentResult:
        """执行已经通过安全校验的命令。"""
        try:
            self._ensure_loaded()
        except RuntimeError as exc:
            return AgentResult(ok=False, message=str(exc), data={"action": command.action})

        action = command.action
        try:
            if action == "click":
                return await self._do_click(command)
            elif action == "fill":
                return await self._do_fill(command)
            elif action == "submit":
                return await self._do_submit(command)
            else:
                return AgentResult(ok=False, message=f"不支持的动作: {action}", data={"action": action})
        except Exception as exc:
            return AgentResult(ok=False, message=str(exc), data={"action": action})

    async def _do_click(self, command: Command) -> AgentResult:
        """执行点击。"""
        await asyncio.to_thread(self._controller.click, command.target)
        return AgentResult(
            ok=True,
            message=f"已点击: {command.target}",
            data={"action": "click", "target": command.target, "label": command.label},
        )

    async def _do_fill(self, command: Command) -> AgentResult:
        """执行填充 — 通过剪贴板粘贴。"""
        value = str(command.value) if command.value is not None else ""
        await asyncio.to_thread(self._controller.set_text, command.target, value)
        return AgentResult(
            ok=True,
            message=f"已填充: {command.target}={value[:20]}",
            data={"action": "fill", "target": command.target, "value_preview": value[:20]},
        )

    async def _do_submit(self, command: Command) -> AgentResult:
        """执行提交（保存草稿等）。"""
        await asyncio.to_thread(self._controller.click, command.target)
        return AgentResult(
            ok=True,
            message=f"已提交: {command.label}",
            data={"action": "submit", "target": command.target, "label": command.label},
        )


class _StubController:
    """UFO 不可用时的桩控制器，所有操作抛出 RuntimeError。"""

    def click(self, target: str) -> None:
        raise RuntimeError("UFO 未安装，无法执行 click")

    def set_text(self, target: str, value: str) -> None:
        raise RuntimeError("UFO 未安装，无法执行 fill")
