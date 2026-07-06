"""上传命令。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jm_ufo_agent.commands.base import Command


@dataclass(frozen=True)
class UploadCommand:
    """文件上传命令构造器。"""

    field_name: str
    path: str | Path
    metadata: dict[str, Any] | None = None

    def to_command(self) -> Command:
        """转换为通用 Command。"""

        # 上传命令仍然只是数据，不直接打开文件选择框。
        # path 转字符串，避免 JSON 序列化 Path 对象失败。
        # label 固定为上传文件，方便日志快速识别。
        return Command(action="upload", target=self.field_name, label="上传文件", value=str(self.path), metadata=self.metadata or {})
