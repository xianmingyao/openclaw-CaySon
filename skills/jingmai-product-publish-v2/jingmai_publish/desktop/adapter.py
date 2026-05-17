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

    def click_text_by_index(self, handle: str, text: str, index: int = 0) -> bool:
        """按出现顺序点击指定文本控件。"""

    def hover_text_by_index(self, handle: str, text: str, index: int = 0) -> bool:
        """按出现顺序悬浮指定文本控件。"""

    def click_text_in_region(
        self,
        handle: str,
        text: str,
        *,
        min_x_ratio: float,
        max_x_ratio: float,
        min_y_ratio: float,
        max_y_ratio: float,
    ) -> bool:
        """在窗口相对区域内点击指定文本控件。"""

    def click_window_ratio(self, handle: str, x_ratio: float, y_ratio: float) -> bool:
        """按窗口相对坐标点击。"""

    def click_text_near_bounds(
        self,
        handle: str,
        text: str,
        *,
        anchor_bounds: dict[str, int],
        max_dx: int = 500,
        max_dy: int = 250,
    ) -> bool:
        """点击指定边界附近的文本控件。"""

    def click_image_upload_slot(self, handle: str, index: int = 0) -> bool:
        """点击 SKU 图片上传槽位。"""

    def hover_image_upload_slot(self, handle: str, index: int = 0) -> bool:
        """悬浮 SKU 图片上传槽位，触发本地上传悬浮入口。"""

    def click_existing_image_slot(self, handle: str, index: int = 0) -> bool:
        """点击已存在图片的 SKU 图片槽位，用于替换已有图片。"""

    def click_local_upload_entry(self, handle: str, index: int = 0) -> bool:
        """命中图片管理区域里的“本地上传”入口。"""

    def click_upload_image_entry(self, handle: str) -> bool:
        """命中图片管理区域里的“上传图片”入口。"""

    def select_uploaded_image_and_confirm(self, handle: str, file_path: str) -> dict[str, object]:
        """在图片管理弹层里选中刚上传的图片并点击确认。"""

    def capture_window(self, handle: str) -> str | None:
        """截图并返回截图路径。"""

    def read_document_text(self, handle: str) -> str:
        """读取窗口内的主文档文本。"""

    def fill_edit_by_automation_id(self, handle: str, automation_id: str, value: str) -> bool:
        """按 automation_id 向输入框写值。"""

    def select_combobox_by_automation_id(self, handle: str, automation_id: str, value: str) -> bool:
        """按 automation_id 选择下拉值。"""

    def fill_edit_by_label(self, handle: str, label: str, value: str) -> bool:
        """按字段标签定位输入框并写值。"""

    def select_combobox_by_label(self, handle: str, label: str, value: str) -> bool:
        """按字段标签定位下拉框并选择值。"""

    def probe_select_options_by_label(self, handle: str, label: str) -> dict[str, object]:
        """按字段标签探测下拉框当前可见选项。"""

    def build_sku_probe(self, handle: str) -> dict[str, object]:
        """构建 SKU 区域探针结果。"""

    def activate_cell_by_automation_id(self, handle: str, automation_id: str) -> dict[str, object]:
        """按 automation_id 激活表格单元格或输入控件。"""

    def type_into_focused_control(self, handle: str, value: str, submit: bool = False) -> dict[str, object]:
        """向当前焦点控件发送键盘输入。"""

    def inspect_controls_by_automation_id(self, handle: str, automation_id: str) -> list[dict[str, object]]:
        """读取指定 automation_id 当前对应控件的文本与边界信息。"""

    def upload_file_from_active_dialog(self, file_path: str) -> dict[str, object]:
        """向当前激活的系统文件对话框写入本地文件路径。"""
