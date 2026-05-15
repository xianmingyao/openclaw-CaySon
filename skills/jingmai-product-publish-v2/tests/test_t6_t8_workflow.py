from __future__ import annotations

from pathlib import Path

from PIL import Image

from jingmai_publish.desktop.adapter import WindowInfo
from jingmai_publish.desktop.window_manager import WindowManager
from jingmai_publish.services.jingmai_workflow import JingmaiWorkflowService


def _create_probe_image(tmp_path: Path, name: str) -> str:
    image_path = tmp_path / name
    Image.new("RGB", (800, 800), color=(255, 0, 0)).save(image_path)
    return str(image_path)


class DummyT6T8Adapter:
    def __init__(self) -> None:
        self.clicked: list[tuple[str, str]] = []
        self.hovered_slots: list[int] = []
        self.uploaded = False
        self.uploaded_file_name = ""
        self.detail_content = ""
        self.document_text = "图片设置 请上传图片 商品详情 编辑商品详情 保存草稿 发布商品 本地上传 上传图片 确定 共10000条"
        self.tuning = type("Tuning", (), {"window_keywords": ["京麦"]})()

    def list_windows(self):
        return [WindowInfo(handle="2002", title="京麦工作台", class_name="JMMainFrameBase", visible=True)]

    def activate_window(self, handle: str) -> bool:
        return True

    def click_text(self, handle: str, text: str) -> bool:
        self.clicked.append((handle, text))
        if text in {"去设置", "编辑商品详情", "高级编辑", "图文编辑推荐", "点击使用", "保存草稿", "发布商品"}:
            if text == "保存草稿":
                self.document_text += " 保存成功"
            if text == "发布商品":
                self.document_text += " 提交成功 待审核"
            return True
        if text in {"本地上传", "上传图片"}:
            return True
        if text in {"确定", self.uploaded_file_name, Path(self.uploaded_file_name).stem if self.uploaded_file_name else ""}:
            return True
        return False

    def click_text_by_index(self, handle: str, text: str, index: int) -> bool:
        self.clicked.append((handle, f"{text}:{index}"))
        return text == "请上传图片"

    def hover_text_by_index(self, handle: str, text: str, index: int = 0) -> bool:
        self.clicked.append((handle, f"hover:{text}:{index}"))
        return text in {"去设置", "请上传图片"}

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
        self.clicked.append((handle, f"region:{text}:{min_x_ratio:.2f}:{max_x_ratio:.2f}:{min_y_ratio:.2f}:{max_y_ratio:.2f}"))
        return self.click_text(handle, text)

    def click_text_near_bounds(
        self,
        handle: str,
        text: str,
        *,
        anchor_bounds: dict[str, int],
        max_dx: int = 500,
        max_dy: int = 250,
    ) -> bool:
        self.clicked.append((handle, f"near:{text}:{anchor_bounds['left']}"))
        return self.click_text(handle, text)

    def capture_window(self, handle: str) -> str | None:
        return f"logs/screenshots/{handle}.png"

    def read_document_text(self, handle: str) -> str:
        return self.document_text + self.detail_content

    def fill_edit_by_automation_id(self, handle: str, automation_id: str, value: str) -> bool:
        return True

    def select_combobox_by_automation_id(self, handle: str, automation_id: str, value: str) -> bool:
        return True

    def fill_edit_by_label(self, handle: str, label: str, value: str) -> bool:
        return True

    def select_combobox_by_label(self, handle: str, label: str, value: str) -> bool:
        return True

    def probe_select_options_by_label(self, handle: str, label: str) -> dict[str, object]:
        return {"success": True, "label": label, "options": []}

    def build_sku_probe(self, handle: str) -> dict[str, object]:
        return {}

    def activate_cell_by_automation_id(self, handle: str, automation_id: str) -> dict[str, object]:
        return {"success": True}

    def type_into_focused_control(self, handle: str, value: str, submit: bool = False) -> dict[str, object]:
        self.detail_content = value
        return {"success": True}

    def inspect_controls_by_automation_id(self, handle: str, automation_id: str) -> list[dict[str, object]]:
        return []

    def list_candidate_controls(self, handle: str, text: str) -> list[dict[str, object]]:
        if text in {"保存草稿", "发布商品"}:
            return [{"text": text, "class_name": "Button"}]
        return []

    def upload_file_from_active_dialog(self, file_path: str) -> dict[str, object]:
        self.uploaded = True
        self.uploaded_file_name = Path(file_path).name
        return {"success": True, "file_path": file_path}

    def click_image_upload_slot(self, handle: str, index: int = 0) -> bool:
        return True

    def hover_image_upload_slot(self, handle: str, index: int = 0) -> bool:
        self.hovered_slots.append(index)
        return True

    def click_existing_image_slot(self, handle: str, index: int = 0) -> bool:
        return True

    def click_local_upload_entry(self, handle: str, index: int = 0) -> bool:
        self.clicked.append((handle, f"local-upload:{index}"))
        return True

    def click_upload_image_entry(self, handle: str) -> bool:
        self.clicked.append((handle, "upload-image-entry"))
        return True

    def select_uploaded_image_and_confirm(self, handle: str, file_path: str) -> dict[str, object]:
        self.clicked.append((handle, f"select:{Path(file_path).name}"))
        return {"success": True}

    def inspect_image_upload_slots(self, handle: str) -> list[dict[str, object]]:
        if self.uploaded:
            return [
                {"status": "filled", "class_name": "Image", "text": "", "bounds": {"left": 1, "top": 1, "right": 2, "bottom": 2}},
                {"status": "empty", "class_name": "DataItem", "text": "请上传图片", "bounds": {"left": 3, "top": 1, "right": 4, "bottom": 2}},
            ]
        return [
            {"status": "empty", "class_name": "DataItem", "text": "请上传图片", "bounds": {"left": 1, "top": 1, "right": 2, "bottom": 2}},
            {"status": "empty", "class_name": "DataItem", "text": "请上传图片", "bounds": {"left": 3, "top": 1, "right": 4, "bottom": 2}},
        ]


def test_workflow_t6_probe():
    workflow = JingmaiWorkflowService(WindowManager(DummyT6T8Adapter()))
    result = workflow.run_t6_probe("2002")
    assert result.step_id == "T6-PROBE"
    assert result.success is True
    assert result.page_state == "media_ready"


def test_workflow_t6_upload_main_image_prefers_hover_local_upload(tmp_path):
    adapter = DummyT6T8Adapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))
    file_path = _create_probe_image(tmp_path, "main.png")

    result = workflow.run_t6_upload_main_image("2002", file_path)

    assert result.step_id == "T6-MAIN-IMAGE"
    assert result.success is True
    assert result.page_state == "main_image_uploaded"
    assert adapter.hovered_slots == [0]
    assert ("2002", "local-upload:0") in adapter.clicked


def test_workflow_t6_upload_transparent_image(tmp_path):
    workflow = JingmaiWorkflowService(WindowManager(DummyT6T8Adapter()))
    file_path = _create_probe_image(tmp_path, "transparent.png")
    result = workflow.run_t6_upload_transparent_image("2002", file_path)
    assert result.step_id == "T6-TRANSPARENT-IMAGE"
    assert result.success is True
    assert result.page_state == "transparent_image_uploaded"


def test_workflow_t6_upload_rejects_small_image(tmp_path):
    image_path = tmp_path / "small.png"
    Image.new("RGB", (350, 350), color=(255, 0, 0)).save(image_path)
    workflow = JingmaiWorkflowService(WindowManager(DummyT6T8Adapter()))

    result = workflow.run_t6_upload_main_image("2002", str(image_path))

    assert result.success is False
    assert result.page_state == "image_dimension_invalid"
    assert "尺寸不足" in (result.message or "")


def test_workflow_t6_fill_detail_editor():
    workflow = JingmaiWorkflowService(WindowManager(DummyT6T8Adapter()))
    result = workflow.run_t6_fill_detail_editor("2002", detail_content="<p>详情内容</p>")
    assert result.step_id == "T6-DETAIL-EDITOR"
    assert result.success is True
    assert result.page_state == "detail_content_written"


def test_workflow_t8_probe():
    workflow = JingmaiWorkflowService(WindowManager(DummyT6T8Adapter()))
    result = workflow.run_t8_probe("2002")
    assert result.step_id == "T8-PROBE"
    assert result.success is True
    assert result.page_state == "submit_ready"


def test_workflow_t8_save_draft():
    workflow = JingmaiWorkflowService(WindowManager(DummyT6T8Adapter()))
    result = workflow.run_t8_save_draft("2002")
    assert result.step_id == "T8-SAVE-DRAFT"
    assert result.success is True
    assert result.page_state == "draft_saved"


def test_workflow_t8_publish_product():
    workflow = JingmaiWorkflowService(WindowManager(DummyT6T8Adapter()))
    result = workflow.run_t8_publish_product("2002")
    assert result.step_id == "T8-PUBLISH-PRODUCT"
    assert result.success is True
    assert result.page_state == "publish_submitted"
