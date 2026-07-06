"""原生对话框 Agent。"""

from __future__ import annotations

from pathlib import Path

from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.agents.desktop import DesktopAgent


class NativeDialogAgent(DesktopAgent):
    """负责 Windows 原生文件选择窗口。"""

    def __init__(self, *args, **kwargs):
        """初始化原生对话框 Agent。"""

        # 固定名称用于区分 WebView 表单动作。
        # 真实文件选择 backend 后续注入。
        # 默认仍为 dry-run 记录模式。
        kwargs.setdefault("name", "native_dialog")
        super().__init__(*args, **kwargs)

    async def choose_file(self, path: str | Path) -> AgentResult:
        """选择一个本地文件。"""

        # 文件选择属于原生窗口能力，不走 WebView 坐标策略。
        # 仍然用 fill 建模，确保进入统一安全通道。
        # 这里只记录路径，真实 backend 后续负责输入文件路径。
        return await self.fill(target="native_file_dialog", value=str(path), label="选择文件")
