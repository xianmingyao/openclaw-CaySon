"""命令数据对象。"""

from __future__ import annotations

from jm_ufo_agent.commands.base import Command
from jm_ufo_agent.commands.click import ClickCommand
from jm_ufo_agent.commands.fill import FillCommand
from jm_ufo_agent.commands.navigate import NavigateCommand
from jm_ufo_agent.commands.read import ReadCommand
from jm_ufo_agent.commands.upload import UploadCommand

__all__ = ["ClickCommand", "Command", "FillCommand", "NavigateCommand", "ReadCommand", "UploadCommand"]
