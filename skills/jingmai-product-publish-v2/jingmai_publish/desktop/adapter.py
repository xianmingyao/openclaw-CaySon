"""桌面自动化适配器协议。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class WindowInfo:
    """桌面窗口信息。"""

    handle: str
    title: str
    process_name: str | None = None
    class_name: str | None = None
    visible: bool = True


class DesktopAutomationAdapter(Protocol):
    """桌面自动化适配器协议。

    这里先抽象出窗口发现、激活、点击与截图能力，
    后续可替换为 pywinauto / UIA / Win32 真实实现。
    """

    def list_windows(self) -> list[WindowInfo]:
        """列出当前桌面的可见窗口。"""

    def activate_window(self, handle: str) -> bool:
        """激活目标窗口。"""

    def click_text(self, handle: str, text: str) -> bool:
        """在窗口内点击包含指定文本的控件。"""

    def capture_window(self, handle: str) -> str | None:
        """截图并返回截图路径。"""

    def read_document_text(self, handle: str) -> str:
        """读取窗口内的主文档文本。"""

    def fill_edit_by_automation_id(self, handle: str, automation_id: str, value: str) -> bool:
        """按 automation_id 向输入框写值。"""

    def select_combobox_by_automation_id(self, handle: str, automation_id: str, value: str) -> bool:
        """按 automation_id 选择下拉值。"""

    def build_sku_probe(self, handle: str) -> dict[str, object]:
        """构建 SKU 区域探针结果。"""

    def activate_cell_by_automation_id(self, handle: str, automation_id: str) -> dict[str, object]:
        """按 automation_id 激活表格单元格或输入控件。"""

    def type_into_focused_control(self, handle: str, value: str, submit: bool = False) -> dict[str, object]:
        """向当前焦点控件发送键盘输入。"""
