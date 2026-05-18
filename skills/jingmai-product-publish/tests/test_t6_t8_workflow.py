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
        self.detail_editor_calls: list[tuple[str, str]] = []
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
        if text in {"确定", self.uploaded_file_name,
                    Path(self.uploaded_file_name).stem if self.uploaded_file_name else ""}:
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
        self.clicked.append(
            (handle, f"region:{text}:{min_x_ratio:.2f}:{max_x_ratio:.2f}:{min_y_ratio:.2f}:{max_y_ratio:.2f}"))
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

    def type_into_detail_editor(self, handle: str, value: str) -> dict[str, object]:
        self.detail_editor_calls.append((handle, value))
        self.detail_content = value
        return {"success": True, "after_contains": True}

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
                {"status": "filled", "class_name": "Image", "text": "",
                 "bounds": {"left": 1, "top": 1, "right": 2, "bottom": 2}},
                {"status": "empty", "class_name": "DataItem", "text": "请上传图片",
                 "bounds": {"left": 3, "top": 1, "right": 4, "bottom": 2}},
            ]
        return [
            {"status": "empty", "class_name": "DataItem", "text": "请上传图片",
             "bounds": {"left": 1, "top": 1, "right": 2, "bottom": 2}},
            {"status": "empty", "class_name": "DataItem", "text": "请上传图片",
             "bounds": {"left": 3, "top": 1, "right": 4, "bottom": 2}},
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
    assert ("2002", "near:本地上传:1") in adapter.clicked


def test_workflow_t6_upload_main_image_accepts_retry_lane_strategy(tmp_path):
    adapter = DummyT6T8Adapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))
    file_path = _create_probe_image(tmp_path, "main-lane.png")

    result = workflow.run_t6_upload_main_image("2002", file_path, upload_strategy="hover_modal")

    assert result.success is True
    assert result.page_state == "main_image_uploaded"


def test_workflow_t6_upload_main_image_supports_product_main_image_text(tmp_path):
    class ProductMainImageAdapter(DummyT6T8Adapter):
        def inspect_image_upload_slots(self, handle: str) -> list[dict[str, object]]:
            if self.uploaded:
                return [
                    {
                        "status": "filled",
                        "class_name": "Image",
                        "text": "",
                        "bounds": {"left": 1000, "top": 666, "right": 1128, "bottom": 786},
                    }
                ]
            return [
                {
                    "status": "empty",
                    "class_name": "DataItem",
                    "text": "请上传主图",
                    "bounds": {"left": 1000, "top": 666, "right": 1128, "bottom": 786},
                }
            ]

    adapter = ProductMainImageAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))
    file_path = _create_probe_image(tmp_path, "product-main.png")

    result = workflow.run_t6_upload_main_image("2002", file_path)

    assert result.success is True
    assert result.page_state == "main_image_uploaded"
    assert adapter.hovered_slots == [0]


def test_workflow_t6_upload_main_image_waits_for_slot_refresh(tmp_path):
    class DelayedSlotAdapter(DummyT6T8Adapter):
        def __init__(self) -> None:
            super().__init__()
            self.after_upload_inspections = 0

        def inspect_image_upload_slots(self, handle: str) -> list[dict[str, object]]:
            if self.uploaded:
                self.after_upload_inspections += 1
                if self.after_upload_inspections < 3:
                    return [
                        {
                            "status": "empty",
                            "class_name": "DataItem",
                            "text": "请上传图片",
                            "bounds": {"left": 1, "top": 1, "right": 2, "bottom": 2},
                        },
                        {
                            "status": "empty",
                            "class_name": "DataItem",
                            "text": "请上传图片",
                            "bounds": {"left": 3, "top": 1, "right": 4, "bottom": 2},
                        },
                    ]
            return super().inspect_image_upload_slots(handle)

    adapter = DelayedSlotAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))
    file_path = _create_probe_image(tmp_path, "main-delayed.png")

    result = workflow.run_t6_upload_main_image("2002", file_path)

    assert result.success is True
    assert result.page_state == "main_image_uploaded"
    assert "槽位轮询次数=3" in (result.message or "")


def test_workflow_t6_upload_retries_picker_confirmation_when_slot_stays_empty(tmp_path, monkeypatch):
    class DelayedPickerConfirmAdapter(DummyT6T8Adapter):
        def __init__(self) -> None:
            super().__init__()
            self.select_calls = 0
            self.uploaded = False

        def upload_file_from_active_dialog(self, file_path: str) -> dict[str, object]:
            self.uploaded_file_name = Path(file_path).name
            return {"success": True, "file_path": file_path}

        def select_uploaded_image_and_confirm(self, handle: str, file_path: str) -> dict[str, object]:
            self.select_calls += 1
            self.clicked.append((handle, f"select:{self.select_calls}:{Path(file_path).name}"))
            if self.select_calls >= 2:
                self.uploaded = True
            return {"success": True}

    monkeypatch.setattr("jingmai_publish.services.jingmai_workflow.time.sleep", lambda _: None)
    adapter = DelayedPickerConfirmAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))
    file_path = _create_probe_image(tmp_path, "delayed-picker.png")

    result = workflow.run_t6_upload_main_image("2002", file_path)

    assert result.success is True
    assert adapter.select_calls == 2
    assert "选择确认重试=success" in (result.message or "")


def test_workflow_t6_upload_retries_until_file_dialog_ready(tmp_path, monkeypatch):
    class SlowDialogAdapter(DummyT6T8Adapter):
        def __init__(self) -> None:
            super().__init__()
            self.dialog_attempts = 0

        def upload_file_from_active_dialog(self, file_path: str) -> dict[str, object]:
            self.dialog_attempts += 1
            if self.dialog_attempts < 3:
                return {"success": False, "error": "active_file_dialog_not_found"}
            return super().upload_file_from_active_dialog(file_path)

    monkeypatch.setattr("jingmai_publish.services.jingmai_workflow.time.sleep", lambda _: None)
    adapter = SlowDialogAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))
    file_path = _create_probe_image(tmp_path, "slow-dialog.png")

    result = workflow.run_t6_upload_main_image("2002", file_path)

    assert result.success is True
    assert adapter.dialog_attempts == 3


def test_workflow_t6_upload_reuses_visible_picker_uploaded_file(tmp_path, monkeypatch):
    class ExistingPickerAdapter(DummyT6T8Adapter):
        def __init__(self) -> None:
            super().__init__()
            self.dialog_attempts = 0
            self.uploaded_file_name = "existing-picker.png"
            self.document_text = (
                "图片空间 本地上传 800*800 existing-picker.png 共 10000 条 "
                "已选0个，可选10个 确定 取消"
            )

        def upload_file_from_active_dialog(self, file_path: str) -> dict[str, object]:
            self.dialog_attempts += 1
            return {"success": False, "error": "active_file_dialog_not_found"}

        def select_uploaded_image_and_confirm(self, handle: str, file_path: str) -> dict[str, object]:
            self.uploaded = True
            self.document_text = "图片空间 已选1个，可选10个 确定"
            return {"success": True, "selected_by": "file_card"}

    monkeypatch.setattr("jingmai_publish.services.jingmai_workflow.time.sleep", lambda _: None)
    adapter = ExistingPickerAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))
    file_path = _create_probe_image(tmp_path, "existing-picker.png")

    result = workflow.run_t6_upload_main_image("2002", file_path)

    assert result.success is True
    assert adapter.dialog_attempts == 0
    assert "选择确认重试=not_required" in (result.message or "")


def test_workflow_t6_upload_transparent_image(tmp_path):
    workflow = JingmaiWorkflowService(WindowManager(DummyT6T8Adapter()))
    file_path = _create_probe_image(tmp_path, "transparent.png")
    result = workflow.run_t6_upload_transparent_image("2002", file_path)
    assert result.step_id == "T6-TRANSPARENT-IMAGE"
    assert result.success is True
    assert result.page_state == "transparent_image_uploaded"


def test_workflow_t6_upload_transparent_image_enters_sku_image_surface(tmp_path):
    class SurfaceRecoveringAdapter(DummyT6T8Adapter):
        def __init__(self) -> None:
            super().__init__()
            self.surface_visible = False

        def click_text(self, handle: str, text: str) -> bool:
            if text == "SKU图片信息":
                self.surface_visible = True
                self.clicked.append((handle, text))
                return True
            return super().click_text(handle, text)

        def inspect_image_upload_slots(self, handle: str) -> list[dict[str, object]]:
            if not self.surface_visible:
                return []
            return super().inspect_image_upload_slots(handle)

    adapter = SurfaceRecoveringAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))
    file_path = _create_probe_image(tmp_path, "transparent-surface.png")

    result = workflow.run_t6_upload_transparent_image("2002", file_path)

    assert result.success is True
    assert result.page_state == "transparent_image_uploaded"
    assert ("2002", "SKU图片信息") in adapter.clicked
    assert adapter.hovered_slots == [1]
    assert ("2002", "local-upload:1") in adapter.clicked


def test_workflow_t6_upload_transparent_image_is_idempotent_when_slot_filled(tmp_path):
    class AlreadyFilledTransparentAdapter(DummyT6T8Adapter):
        def upload_file_from_active_dialog(self, file_path: str) -> dict[str, object]:
            raise AssertionError("already-filled transparent slot should not reopen file dialog")

        def inspect_image_upload_slots(self, handle: str) -> list[dict[str, object]]:
            return [
                {"status": "filled", "class_name": "Image", "text": "",
                 "bounds": {"left": 1027, "top": 716, "right": 1092, "bottom": 781}},
                {"status": "empty", "class_name": "DataItem", "text": "请上传图片",
                 "bounds": {"left": 1187, "top": 716, "right": 1252, "bottom": 785}},
                {"status": "filled", "class_name": "Image", "text": "",
                 "bounds": {"left": 1810, "top": 716, "right": 1875, "bottom": 781}},
            ]

    workflow = JingmaiWorkflowService(WindowManager(AlreadyFilledTransparentAdapter()))
    file_path = _create_probe_image(tmp_path, "transparent-filled.png")

    result = workflow.run_t6_upload_transparent_image("2002", file_path)

    assert result.success is True
    assert result.page_state == "transparent_image_uploaded"
    assert "触发模式=already_filled" in (result.message or "")


def test_workflow_t6_upload_transparent_image_uses_remaining_empty_slot_after_main_filled(tmp_path):
    class MainFilledTransparentEmptyAdapter(DummyT6T8Adapter):
        def __init__(self) -> None:
            super().__init__()
            self.transparent_uploaded = False

        def upload_file_from_active_dialog(self, file_path: str) -> dict[str, object]:
            self.uploaded_file_name = Path(file_path).name
            return {"success": True, "file_path": file_path}

        def select_uploaded_image_and_confirm(self, handle: str, file_path: str) -> dict[str, object]:
            self.transparent_uploaded = True
            return {"success": True}

        def inspect_image_upload_slots(self, handle: str) -> list[dict[str, object]]:
            if self.transparent_uploaded:
                return [
                    {"status": "filled", "class_name": "Image", "text": "",
                     "bounds": {"left": 632, "top": 304, "right": 712, "bottom": 384}},
                    {"status": "filled", "class_name": "Image", "text": "",
                     "bounds": {"left": 722, "top": 304, "right": 812, "bottom": 388}},
                ]
            return [
                {"status": "filled", "class_name": "Image", "text": "",
                 "bounds": {"left": 632, "top": 304, "right": 712, "bottom": 384}},
                {"status": "empty", "class_name": "DataItem", "text": "请上传图片",
                 "bounds": {"left": 722, "top": 304, "right": 812, "bottom": 388}},
            ]

    adapter = MainFilledTransparentEmptyAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))
    file_path = _create_probe_image(tmp_path, "transparent-after-main.png")

    result = workflow.run_t6_upload_transparent_image("2002", file_path)

    assert result.success is True
    assert adapter.hovered_slots == [0]
    assert ("2002", "local-upload:0") in adapter.clicked


def test_resolve_t6_empty_slot_action_index_maps_transparent_to_remaining_empty_slot():
    slots = [
        {"status": "filled", "class_name": "Image", "text": "", "bounds": {"left": 632}},
        {"status": "empty", "class_name": "DataItem", "text": "请上传图片", "bounds": {"left": 722}},
    ]

    assert JingmaiWorkflowService._resolve_t6_empty_slot_action_index(slots, slot_index=1) == 0


def test_workflow_t6_upload_rejects_small_image(tmp_path):
    image_path = tmp_path / "small.png"
    Image.new("RGB", (350, 350), color=(255, 0, 0)).save(image_path)
    workflow = JingmaiWorkflowService(WindowManager(DummyT6T8Adapter()))

    result = workflow.run_t6_upload_main_image("2002", str(image_path))

    assert result.success is False
    assert result.page_state == "image_dimension_invalid"
    assert "尺寸不足" in (result.message or "")


def test_workflow_t6_fill_detail_editor():
    adapter = DummyT6T8Adapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))
    result = workflow.run_t6_fill_detail_editor("2002", detail_content="<p>详情内容</p>")
    assert result.step_id == "T6-DETAIL-EDITOR"
    assert result.success is True
    assert result.page_state == "detail_content_written"
    assert adapter.detail_editor_calls == [("2002", "<p>详情内容</p>")]
    assert ("2002", "代码编辑") in adapter.clicked


def test_workflow_t6_fill_detail_editor_falls_back_to_focused_control():
    class FocusOnlyAdapter(DummyT6T8Adapter):
        def __getattribute__(self, name: str):
            if name == "type_into_detail_editor":
                raise AttributeError(name)
            return super().__getattribute__(name)

    adapter = FocusOnlyAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))

    result = workflow.run_t6_fill_detail_editor("2002", detail_content="<p>兜底详情</p>")

    assert result.success is True
    assert result.page_state == "detail_content_written"


def test_detail_content_visible_accepts_placeholder_replaced_state():
    before = "商品详情 详情预览 暂未编辑商详 请输入正文 0 /100000 请补充商品描述"
    after = "商品详情 详情预览 公牛插座详情 18 /100000"

    assert (
            JingmaiWorkflowService._detail_content_visible(
                "<section><p>公牛插座详情</p></section>",
                before,
                after,
                {"success": True, "after_contains": False},
            )
            is True
    )


def test_workflow_t7_enters_logistics_tab_and_maps_allowed_values():
    class LogisticsAdapter(DummyT6T8Adapter):
        def __init__(self) -> None:
            super().__init__()
            self.selected: list[tuple[str, str]] = []
            self.filled: list[tuple[str, str]] = []

        def probe_select_options_by_label(self, handle: str, label: str) -> dict[str, object]:
            if label == "销售单位":
                return {"success": True, "label": label, "options": [{"text": "包"}]}
            return {"success": True, "label": label, "options": []}

        def select_combobox_by_label(self, handle: str, label: str, value: str) -> bool:
            self.selected.append((label, value))
            self.document_text += f" {value}"
            return True

        def select_combobox_by_automation_id(self, handle: str, automation_id: str, value: str) -> bool:
            return False

        def fill_edit_by_label(self, handle: str, label: str, value: str) -> bool:
            self.filled.append((label, value))
            self.document_text += f" {value}"
            return True

        def fill_edit_by_automation_id(self, handle: str, automation_id: str, value: str) -> bool:
            return False

    adapter = LogisticsAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))

    result = workflow.run_t7_fill_logistics_fields(
        "2002",
        sale_unit="件",
        package_type="普通商品",
        delivery_mark="普通品",
        package_list="插座*1，说明书*1，保修卡*1",
        warranty_period="365",
    )

    assert result.success is True
    assert result.page_state == "logistics_completed"
    assert ("2002", "region:商品售后及其他:0.22:0.86:0.06:0.14") in adapter.clicked
    assert ("销售单位", "包") in adapter.selected
    assert ("质保期", "1年质保") in adapter.selected


def test_t7_field_validation_uses_local_field_slice():
    document_text = (
        "销售单位填写规范 举例单位=个 "
        "销售单位   *  包        包装规格   *    普通商品     最大值9个9 "
        "商品包装   *  普通商品        特殊发货时效标记   *  普通品        是否危险商品 "
        "包装清单 *    插座*1，说明书*1，保修卡*1\n  26 / 800 "
        "商品售后及其他 质保期   * 1年质保             发布商品 保存草稿"
    )

    assert JingmaiWorkflowService._t7_field_value_visible("销售单位", "包", document_text) is True
    assert JingmaiWorkflowService._t7_field_value_visible("销售单位", "个", document_text) is False
    assert JingmaiWorkflowService._t7_field_value_visible("特殊发货时效标记", "普通品", document_text) is True
    assert JingmaiWorkflowService._t7_field_value_visible("包装清单", "插座*1，说明书*1，保修卡*1", document_text) is True


def test_workflow_t5_fill_required_fields_by_publish_form_labels():
    class RequiredFieldsAdapter(DummyT6T8Adapter):
        def __init__(self) -> None:
            super().__init__()
            self.filled: list[tuple[str, str]] = []

        def fill_edit_by_label(self, handle: str, label: str, value: str) -> bool:
            self.filled.append((label, value))
            self.document_text += f" {label} {value}"
            return True

    adapter = RequiredFieldsAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))

    result = workflow.run_t5_fill_required_fields(
        "2002",
        market_price="82.35",
        purchase_price="66.50",
        jd_price="70.00",
        weight="0.85",
        length_mm="250.00",
        width_mm="76.00",
        height_mm="42.00",
    )

    assert result.success is True
    assert result.page_state == "required_fields_completed"
    assert ("市场价(元)", "82.35") in adapter.filled
    assert ("[包装]长(mm)", "250.00") in adapter.filled


def test_t5_field_validation_accepts_decimal_variants_in_field_slice():
    document_text = (
        "市场价(元) * 82.35 价格凭证类型 京东价(元) * 70 采购价(元) * 66.50 毛利 "
        "商品毛重(kg) * 0.85 [包装]长(mm) * 250 [包装]宽(mm) * 76 [包装]高(mm) * 42 商品条形码"
    )

    assert JingmaiWorkflowService._t5_field_value_visible("京东价(元)", "70.00", document_text) is True
    assert JingmaiWorkflowService._t5_field_value_visible("[包装]长(mm)", "250.00", document_text) is True


def test_workflow_t8_probe():
    workflow = JingmaiWorkflowService(WindowManager(DummyT6T8Adapter()))
    result = workflow.run_t8_probe("2002")
    assert result.step_id == "T8-PROBE"
    assert result.success is True
    assert result.page_state == "submit_ready"


def test_workflow_t8_probe_accepts_draft_list_state():
    adapter = DummyT6T8Adapter()
    adapter.document_text = "商品列表 发布商品 草稿箱 商品草稿仅支持保留30天 商品名称 编辑时间 操作"
    workflow = JingmaiWorkflowService(WindowManager(adapter))

    result = workflow.run_t8_probe("2002")

    assert result.success is True
    assert result.page_state == "draft_list"


def test_workflow_t8_save_draft():
    workflow = JingmaiWorkflowService(WindowManager(DummyT6T8Adapter()))
    result = workflow.run_t8_save_draft("2002")
    assert result.step_id == "T8-SAVE-DRAFT"
    assert result.success is True
    assert result.page_state == "draft_saved"


def test_workflow_t8_save_draft_accepts_retry_lane_click_mode():
    workflow = JingmaiWorkflowService(WindowManager(DummyT6T8Adapter()))
    result = workflow.run_t8_save_draft("2002", click_mode="direct")
    assert result.step_id == "T8-SAVE-DRAFT"
    assert result.success is True
    assert result.page_state == "draft_saved"


def test_workflow_t8_save_draft_waits_for_draft_list(monkeypatch):
    class DelayedDraftAdapter(DummyT6T8Adapter):
        def __init__(self) -> None:
            super().__init__()
            self.saving = False
            self.polls = 0

        def click_text(self, handle: str, text: str) -> bool:
            self.clicked.append((handle, text))
            if text == "保存草稿":
                self.saving = True
                return True
            return super().click_text(handle, text)

        def read_document_text(self, handle: str) -> str:
            if not self.saving:
                return self.document_text
            self.polls += 1
            if self.polls < 3:
                return self.document_text + " 正在保存 保存草稿"
            return "商品列表 发布商品 草稿箱 商品草稿仅支持保留30天 商品名称 测试商品标题-自动化验证 编辑时间 操作"

    monkeypatch.setattr("jingmai_publish.services.jingmai_workflow.time.sleep", lambda _: None)
    adapter = DelayedDraftAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))

    result = workflow.run_t8_save_draft("2002")

    assert result.success is True
    assert result.page_state == "draft_saved"
    assert "触发模式=draft_list" in (result.message or "")
    assert "文档轮询次数=3" in (result.message or "")


def test_workflow_t8_save_draft_accepts_blank_publish_form_after_save(monkeypatch):
    class BlankAfterSaveAdapter(DummyT6T8Adapter):
        def __init__(self) -> None:
            super().__init__()
            self.document_text = (
                "商品标题 * 自动化测试商品 10 / 100 市场价(元) * 82.35 "
                "商品详情 <p>详情</p> 发布商品 保存草稿"
            )
            self.saved = False

        def click_text(self, handle: str, text: str) -> bool:
            self.clicked.append((handle, text))
            if text == "保存草稿":
                self.saved = True
                return True
            return super().click_text(handle, text)

        def read_document_text(self, handle: str) -> str:
            if self.saved:
                return (
                    "商品标题 * 0 / 100 市场价(元) * 京东价(元) * 采购价(元) * "
                    "暂未编辑商详 发布商品 保存草稿"
                )
            return self.document_text

    monkeypatch.setattr("jingmai_publish.services.jingmai_workflow.time.sleep", lambda _: None)
    adapter = BlankAfterSaveAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))

    result = workflow.run_t8_save_draft("2002")

    assert result.success is True
    assert result.page_state == "draft_saved"
    assert "触发模式=blank_publish_form" in (result.message or "")


def test_workflow_t8_save_draft_confirms_popup_menu(monkeypatch):
    class PopupMenuDraftAdapter(DummyT6T8Adapter):
        def __init__(self) -> None:
            super().__init__()
            self.menu_open = False
            self.region_clicks: list[tuple[str, float, float, float, float]] = []

        def click_text(self, handle: str, text: str) -> bool:
            self.clicked.append((handle, text))
            if text == "保存草稿":
                self.menu_open = True
                self.document_text += " 保存草稿 保存发品模板"
                return True
            return super().click_text(handle, text)

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
            self.region_clicks.append((text, min_x_ratio, max_x_ratio, min_y_ratio, max_y_ratio))
            if text == "保存草稿" and self.menu_open and min_y_ratio >= 0.85 and max_y_ratio <= 0.96:
                self.document_text += " 保存成功"
                return True
            return False

    monkeypatch.setattr("jingmai_publish.services.jingmai_workflow.time.sleep", lambda _: None)
    adapter = PopupMenuDraftAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))

    result = workflow.run_t8_save_draft("2002")

    assert result.success is True
    assert result.page_state == "draft_saved"
    assert adapter.region_clicks == [("保存草稿", 0.45, 0.62, 0.86, 0.95)]
    assert "菜单确认=success" in (result.message or "")


def test_workflow_t8_save_draft_does_not_accept_loading_only(monkeypatch):
    class LoadingOnlyAdapter(DummyT6T8Adapter):
        def __init__(self) -> None:
            super().__init__()
            self.saving = False

        def click_text(self, handle: str, text: str) -> bool:
            self.clicked.append((handle, text))
            if text == "保存草稿":
                self.saving = True
                return True
            return super().click_text(handle, text)

        def read_document_text(self, handle: str) -> str:
            if self.saving:
                return self.document_text + " 正在保存 保存草稿"
            return self.document_text

    monkeypatch.setattr("jingmai_publish.services.jingmai_workflow.time.sleep", lambda _: None)
    workflow = JingmaiWorkflowService(WindowManager(LoadingOnlyAdapter()))

    result = workflow.run_t8_save_draft("2002")

    assert result.success is False
    assert result.page_state == "draft_save_pending"
    assert "草稿确认=失败" in (result.message or "")


def test_workflow_t8_publish_product_requires_confirmation():
    workflow = JingmaiWorkflowService(WindowManager(DummyT6T8Adapter()))
    result = workflow.run_t8_publish_product("2002")
    assert result.step_id == "T8-PUBLISH-PRODUCT"
    assert result.success is False
    assert result.page_state == "publish_guard_required"
    assert "守卫拦截" in (result.message or "")


def test_workflow_t8_publish_product_with_confirmation():
    workflow = JingmaiWorkflowService(WindowManager(DummyT6T8Adapter()))
    result = workflow.run_t8_publish_product("2002", confirm_publish=True)
    assert result.step_id == "T8-PUBLISH-PRODUCT"
    assert result.success is True
    assert result.page_state == "publish_submitted"
