"""Jingmai desktop workflow service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import time

from PIL import Image

from jingmai_publish.desktop.window_manager import WindowManager
from jingmai_publish.repositories.runtime_log import RuntimeLogRepository


@dataclass(slots=True)
class WorkflowStepResult:
    """Structured workflow step result."""

    step_id: str
    success: bool
    page_state: str
    window_handle: str | None = None
    screenshot_path: str | None = None
    message: str | None = None


class JingmaiWorkflowService:
    """Encapsulates Jingmai T1-T8 workflow execution."""

    TITLE_AUTOMATION_ID = "jd-id-8403-277"
    BRAND_AUTOMATION_ID = "jd-id-8403-278"
    MODEL_AUTOMATION_ID = "jd-id-8403-279"
    REQUIRED_ATTR_AUTOMATION_ID = "jd-id-8403-284"

    def __init__(
        self,
        window_manager: WindowManager,
        runtime_log_repo: RuntimeLogRepository | None = None,
    ) -> None:
        self.window_manager = window_manager
        self.runtime_log_repo = runtime_log_repo

    def run_t1_attach_window(self) -> WorkflowStepResult:
        window = self.window_manager.attach_jingmai_window()
        screenshot_path = self.window_manager.adapter.capture_window(window.handle)
        self._append_runtime_log(
            window_handle=window.handle,
            log_type="process",
            message=f"T1 attached window: {window.title}",
            detail_path=screenshot_path,
            step_id="T1",
        )
        return WorkflowStepResult(
            step_id="T1",
            success=True,
            page_state="jingmai_home",
            window_handle=window.handle,
            screenshot_path=screenshot_path,
            message=f"已接管京麦窗口: {window.title}",
        )

    def run_t2_enter_publish_entry(self, window_handle: str) -> WorkflowStepResult:
        clicked = self.window_manager.adapter.click_text(window_handle, "发布商品")
        screenshot_path = self.window_manager.adapter.capture_window(window_handle)
        self._append_runtime_log(
            window_handle=window_handle,
            log_type="process",
            message="T2 attempted to enter publish flow",
            detail_path=screenshot_path,
            step_id="T2",
        )
        return WorkflowStepResult(
            step_id="T2",
            success=clicked,
            page_state="publish_entry" if clicked else "jingmai_home",
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message="已进入发布商品入口" if clicked else "未找到发布商品入口",
        )

    def run_t3_confirm_category(self, window_handle: str) -> WorkflowStepResult:
        category_path = self._extract_category_path(window_handle)
        screenshot_path = self.window_manager.adapter.capture_window(window_handle)
        success = bool(category_path)
        self._append_runtime_log(
            window_handle=window_handle,
            log_type="process",
            message=f"T3 category path: {category_path or 'unresolved'}",
            detail_path=screenshot_path,
            step_id="T3",
        )
        return WorkflowStepResult(
            step_id="T3",
            success=success,
            page_state="category_confirmed" if success else "publish_entry",
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message=f"已确认商品类目: {category_path}" if success else "未识别到商品类目",
        )

    def run_t4_fill_base_info(
        self,
        window_handle: str,
        *,
        title: str,
        model: str,
        required_attribute: str,
        brand: str | None = None,
    ) -> WorkflowStepResult:
        adapter = self.window_manager.adapter
        title_filled = adapter.fill_edit_by_automation_id(window_handle, self.TITLE_AUTOMATION_ID, title)
        model_filled = adapter.fill_edit_by_automation_id(window_handle, self.MODEL_AUTOMATION_ID, model)
        attr_filled = adapter.fill_edit_by_automation_id(window_handle, self.REQUIRED_ATTR_AUTOMATION_ID, required_attribute)

        brand_filled = True
        if brand:
            brand_filled = adapter.select_combobox_by_automation_id(window_handle, self.BRAND_AUTOMATION_ID, brand)

        document_text = adapter.read_document_text(window_handle)
        title_ok = title in document_text
        model_ok = model in document_text
        attr_ok = required_attribute in document_text
        brand_ok = True if not brand else self._value_visible_in_document("品牌", brand, document_text)
        success = title_ok and model_ok and attr_ok and brand_ok
        screenshot_path = adapter.capture_window(window_handle)
        message = "；".join(
            [
                f"标题填充={'成功' if title_filled else '失败'}",
                f"标题校验={'成功' if title_ok else '失败'}",
                f"型号填充={'成功' if model_filled else '失败'}",
                f"型号校验={'成功' if model_ok else '失败'}",
                f"必填属性填充={'成功' if attr_filled else '失败'}",
                f"必填属性校验={'成功' if attr_ok else '失败'}",
                f"品牌填充={'成功' if brand_filled else '失败' if brand else '未要求'}",
                f"品牌校验={'成功' if brand_ok else '失败' if brand else '未要求'}",
            ]
        )
        self._append_runtime_log(
            window_handle=window_handle,
            log_type="process",
            message=f"T4 base info: {message}",
            detail_path=screenshot_path,
            step_id="T4",
        )
        return WorkflowStepResult(
            step_id="T4",
            success=success,
            page_state="base_info_completed" if success else "publish_entry",
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message=message,
        )

    def run_t4_fill_additional_required_fields(
        self,
        window_handle: str,
        *,
        brand: str | None = None,
        rated_voltage: str | None = None,
        cable_length: str | None = None,
        weight: str | None = None,
    ) -> WorkflowStepResult:
        adapter = self.window_manager.adapter
        actions: list[tuple[str, bool, str | None]] = []

        if brand:
            brand_ok = adapter.select_combobox_by_automation_id(window_handle, self.BRAND_AUTOMATION_ID, brand)
            if not brand_ok:
                brand_ok = adapter.select_combobox_by_label(window_handle, "品牌", brand)
            actions.append(("品牌", brand_ok, brand))
        if rated_voltage:
            actions.append(("额定电压", adapter.select_combobox_by_label(window_handle, "额定电压", rated_voltage), rated_voltage))
        if cable_length:
            actions.append(("电缆长度", adapter.select_combobox_by_label(window_handle, "电缆长度", cable_length), cable_length))
        if weight:
            actions.append(("重量", adapter.fill_edit_by_label(window_handle, "重量", weight), weight))

        document_text = adapter.read_document_text(window_handle)
        validation = {
            name: self._value_visible_in_document(name, value, document_text) if value else fill_ok
            for name, fill_ok, value in actions
        }
        success = all(validation.values()) if actions else False
        screenshot_path = adapter.capture_window(window_handle)
        message = "；".join(
            f"{name}填充={'成功' if fill_ok else '失败'}，校验={'成功' if validation[name] else '失败'}"
            for name, fill_ok, _ in actions
        ) or "未提供扩展必填项"
        return WorkflowStepResult(
            step_id="T4-EXTRA",
            success=success,
            page_state="base_info_completed" if success else "publish_entry",
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message=message,
        )

    def run_t7_fill_logistics_fields(
        self,
        window_handle: str,
        *,
        sale_unit: str,
        package_type: str,
        delivery_mark: str,
        package_list: str,
        warranty_period: str,
    ) -> WorkflowStepResult:
        adapter = self.window_manager.adapter
        actions = [
            ("销售单位", adapter.select_combobox_by_label(window_handle, "销售单位", sale_unit), sale_unit),
            ("商品包装", adapter.select_combobox_by_label(window_handle, "商品包装", package_type), package_type),
            ("特殊发货时效标记", adapter.select_combobox_by_label(window_handle, "特殊发货时效标记", delivery_mark), delivery_mark),
            ("包装清单", adapter.fill_edit_by_label(window_handle, "包装清单", package_list), package_list),
            ("质保期", adapter.select_combobox_by_label(window_handle, "质保期", warranty_period), warranty_period),
        ]

        document_text = adapter.read_document_text(window_handle)
        validation = {name: self._value_visible_in_document(name, value, document_text) for name, _, value in actions}
        success = all(validation.values())
        screenshot_path = adapter.capture_window(window_handle)
        message = "；".join(
            f"{name}填充={'成功' if fill_ok else '失败'}，校验={'成功' if validation[name] else '失败'}"
            for name, fill_ok, _ in actions
        )
        return WorkflowStepResult(
            step_id="T7",
            success=success,
            page_state="logistics_completed" if success else "publish_entry",
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message=message,
        )

    def run_t6_probe(self, window_handle: str) -> WorkflowStepResult:
        adapter = self.window_manager.adapter
        image_clicked = self._click_first_available_texts(window_handle, ["去设置", "请上传图片", "图片设置"])
        detail_clicked = self._click_first_available_texts(window_handle, ["编辑商品详情", "图文编辑推荐", "高级编辑"])
        document_text = adapter.read_document_text(window_handle)
        image_visible = self._document_contains_any(document_text, ["图片设置", "请上传图片"])
        detail_visible = self._document_contains_any(document_text, ["商品详情", "编辑商品详情"])
        success = image_clicked and detail_clicked and image_visible and detail_visible
        screenshot_path = adapter.capture_window(window_handle)
        message = "；".join(
            [
                f"图片设置入口={'成功' if image_clicked else '失败'}",
                f"图片设置区域={'成功' if image_visible else '失败'}",
                f"商品详情入口={'成功' if detail_clicked else '失败'}",
                f"商品详情区域={'成功' if detail_visible else '失败'}",
            ]
        )
        return WorkflowStepResult(
            step_id="T6-PROBE",
            success=success,
            page_state="media_ready" if success else "publish_entry",
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message=message,
        )

    def run_t6_upload_dialog_probe(self, window_handle: str, file_path: str) -> WorkflowStepResult:
        adapter = self.window_manager.adapter
        trigger_ok = self._open_hover_local_upload(window_handle, 0)
        upload_result = self._complete_local_upload(window_handle, file_path) if trigger_ok else {"success": False, "error": "entry_not_found"}
        screenshot_path = adapter.capture_window(window_handle)
        success = bool(trigger_ok and upload_result.get("success"))
        message = "；".join(
            [
                f"上传入口={'成功' if trigger_ok else '失败'}",
                f"文件桥接={'成功' if upload_result.get('success') else '失败'}",
                f"文件路径={file_path}",
            ]
        )
        return WorkflowStepResult(
            step_id="T6-DIALOG-PROBE",
            success=success,
            page_state="media_upload_ready" if success else "publish_entry",
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message=message,
        )

    def run_t6_upload_main_image(self, window_handle: str, file_path: str) -> WorkflowStepResult:
        return self._run_t6_upload_slot(
            window_handle,
            file_path=file_path,
            slot_index=0,
            step_id="T6-MAIN-IMAGE",
            success_state="main_image_uploaded",
            pending_state="main_image_empty_slot_pending",
            replacement_state="main_image_replacement_pending",
        )

    def run_t6_upload_transparent_image(self, window_handle: str, file_path: str) -> WorkflowStepResult:
        return self._run_t6_upload_slot(
            window_handle,
            file_path=file_path,
            slot_index=1,
            step_id="T6-TRANSPARENT-IMAGE",
            success_state="transparent_image_uploaded",
            pending_state="transparent_image_empty_slot_pending",
            replacement_state="transparent_image_replacement_pending",
        )

    def run_t6_fill_detail_editor(
        self,
        window_handle: str,
        *,
        detail_content: str,
    ) -> WorkflowStepResult:
        adapter = self.window_manager.adapter
        document_before = adapter.read_document_text(window_handle)
        trigger_ok = self._click_first_available_texts(
            window_handle,
            ["编辑商品详情", "高级编辑", "图文编辑推荐", "点击使用", "代码编辑"],
        )
        typing_result = {"success": False, "error": "detail_editor_not_activated"}
        if trigger_ok and hasattr(adapter, "type_into_focused_control"):
            typing_result = adapter.type_into_focused_control(window_handle, detail_content, submit=False)

        document_after = adapter.read_document_text(window_handle)
        content_visible = detail_content[: min(len(detail_content), 24)] in document_after
        editor_visible = self._document_contains_any(document_after, ["商品详情", "详情预览", "商详"])
        screenshot_path = adapter.capture_window(window_handle)
        if trigger_ok and typing_result.get("success") and content_visible:
            page_state = "detail_content_written"
            success = True
        elif trigger_ok and typing_result.get("success") and editor_visible:
            page_state = "detail_editor_pending_verify"
            success = False
        else:
            page_state = "detail_editor_not_ready"
            success = False

        message = "；".join(
            [
                f"编辑器触发={'成功' if trigger_ok else '失败'}",
                f"内容写入={'成功' if typing_result.get('success') else '失败'}",
                f"内容可见={'成功' if content_visible else '失败'}",
                f"详情区域可见={'成功' if editor_visible else '失败'}",
                f"写入前长度={len(document_before)}",
                f"写入后长度={len(document_after)}",
            ]
        )
        return WorkflowStepResult(
            step_id="T6-DETAIL-EDITOR",
            success=success,
            page_state=page_state,
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message=message,
        )

    def run_t8_probe(self, window_handle: str) -> WorkflowStepResult:
        adapter = self.window_manager.adapter
        save_candidate = False
        publish_candidate = False
        if hasattr(adapter, "list_candidate_controls"):
            try:
                save_candidate = bool(adapter.list_candidate_controls(window_handle, "保存草稿"))
                publish_candidate = bool(adapter.list_candidate_controls(window_handle, "发布商品"))
            except Exception:
                save_candidate = False
                publish_candidate = False
        document_text = adapter.read_document_text(window_handle)
        save_visible = "保存草稿" in document_text
        publish_visible = "发布商品" in document_text
        success = save_visible and publish_visible and save_candidate and publish_candidate
        screenshot_path = adapter.capture_window(window_handle)
        message = "；".join(
            [
                f"保存草稿按钮定位={'成功' if save_candidate else '失败'}",
                f"保存草稿文案={'成功' if save_visible else '失败'}",
                f"发布商品按钮定位={'成功' if publish_candidate else '失败'}",
                f"发布商品文案={'成功' if publish_visible else '失败'}",
            ]
        )
        return WorkflowStepResult(
            step_id="T8-PROBE",
            success=success,
            page_state="submit_ready" if success else "publish_entry",
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message=message,
        )

    def run_t8_save_draft(self, window_handle: str) -> WorkflowStepResult:
        adapter = self.window_manager.adapter
        document_before = adapter.read_document_text(window_handle)
        clicked = self._click_first_available_texts(window_handle, ["保存草稿"])
        document_after = adapter.read_document_text(window_handle)
        state_changed = document_before != document_after
        draft_hint_visible = self._document_contains_any(document_after, ["保存草稿", "草稿", "保存成功", "已保存"])
        screenshot_path = adapter.capture_window(window_handle)
        success = bool(clicked and (state_changed or draft_hint_visible))
        page_state = "draft_saved" if success else "draft_save_pending"
        message = "；".join(
            [
                f"草稿点击={'成功' if clicked else '失败'}",
                f"页面变化={'成功' if state_changed else '失败'}",
                f"草稿提示={'成功' if draft_hint_visible else '失败'}",
            ]
        )
        return WorkflowStepResult(
            step_id="T8-SAVE-DRAFT",
            success=success,
            page_state=page_state,
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message=message,
        )

    def run_t8_publish_product(self, window_handle: str) -> WorkflowStepResult:
        adapter = self.window_manager.adapter
        document_before = adapter.read_document_text(window_handle)
        publish_clicked = self._click_first_available_texts(window_handle, ["发布商品"])
        continue_clicked = False
        if publish_clicked:
            continue_clicked = self._click_first_available_texts(window_handle, ["继续发布", "确认发布", "确定"])
        document_after = adapter.read_document_text(window_handle)
        review_visible = self._document_contains_any(document_after, ["审核", "采销审核", "提交成功", "发布成功", "待审核"])
        state_changed = document_before != document_after
        screenshot_path = adapter.capture_window(window_handle)
        success = bool(publish_clicked and (continue_clicked or review_visible) and (state_changed or review_visible))
        if success:
            page_state = "publish_submitted"
        elif publish_clicked:
            page_state = "publish_confirmation_pending"
        else:
            page_state = "publish_entry"
        message = "；".join(
            [
                f"发布点击={'成功' if publish_clicked else '失败'}",
                f"继续发布={'成功' if continue_clicked else '失败'}",
                f"审核态可见={'成功' if review_visible else '失败'}",
                f"页面变化={'成功' if state_changed else '失败'}",
            ]
        )
        return WorkflowStepResult(
            step_id="T8-PUBLISH-PRODUCT",
            success=success,
            page_state=page_state,
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message=message,
        )

    def _run_t6_upload_slot(
        self,
        window_handle: str,
        *,
        file_path: str,
        slot_index: int,
        step_id: str,
        success_state: str,
        pending_state: str,
        replacement_state: str,
    ) -> WorkflowStepResult:
        adapter = self.window_manager.adapter
        preflight = self._validate_upload_image_file(file_path)
        if not preflight["success"]:
            screenshot_path = adapter.capture_window(window_handle)
            return WorkflowStepResult(
                step_id=step_id,
                success=False,
                page_state="image_dimension_invalid",
                window_handle=window_handle,
                screenshot_path=screenshot_path,
                message=preflight["message"],
            )

        before_slots = adapter.inspect_image_upload_slots(window_handle) if hasattr(adapter, "inspect_image_upload_slots") else []
        before_image_count = sum(
            1 for slot in before_slots if slot.get("status") == "filled" or slot.get("class_name") == "Image"
        )
        before_empty_slot_count = sum(
            1 for slot in before_slots if slot.get("status") == "empty" or slot.get("text") == "请上传图片"
        )

        trigger_ok = False
        trigger_mode = "empty_slot"
        upload_result = {"success": False, "error": "upload_bridge_unavailable"}

        if before_empty_slot_count > slot_index:
            if self._open_hover_local_upload(window_handle, slot_index):
                trigger_ok = True
                trigger_mode = "hover_local_upload"
                upload_result = self._complete_local_upload(window_handle, file_path)

        if not upload_result.get("success"):
            if self._open_hover_local_upload_by_text(window_handle, slot_index):
                trigger_ok = True
                trigger_mode = "hover_text_local_upload"
                upload_result = self._complete_local_upload(window_handle, file_path)

        if (not upload_result.get("success")) and before_empty_slot_count > slot_index and hasattr(adapter, "click_image_upload_slot"):
            trigger_ok = adapter.click_image_upload_slot(window_handle, slot_index)
            if trigger_ok:
                trigger_mode = "empty_slot_modal"
                upload_result = self._complete_local_upload(window_handle, file_path)

        if (not upload_result.get("success")) and before_image_count > slot_index and hasattr(adapter, "click_existing_image_slot"):
            trigger_ok = adapter.click_existing_image_slot(window_handle, slot_index)
            if trigger_ok:
                trigger_mode = "occupied_slot_replace"
                upload_result = self._complete_local_upload(window_handle, file_path)

        if (not upload_result.get("success")) and hasattr(adapter, "click_text_by_index"):
            trigger_ok = adapter.click_text_by_index(window_handle, "请上传图片", slot_index)
            if trigger_ok:
                trigger_mode = "text_index_fallback"
                upload_result = self._complete_local_upload(window_handle, file_path)

        if (not upload_result.get("success")):
            trigger_ok = self._click_first_available_texts(window_handle, ["去设置", "请上传图片", "图片设置"])
            if trigger_ok:
                trigger_mode = "text_fallback"
                upload_result = self._complete_local_upload(window_handle, file_path)

        after_slots = adapter.inspect_image_upload_slots(window_handle) if hasattr(adapter, "inspect_image_upload_slots") else []
        after_image_count = sum(
            1 for slot in after_slots if slot.get("status") == "filled" or slot.get("class_name") == "Image"
        )
        after_empty_slot_count = sum(
            1 for slot in after_slots if slot.get("status") == "empty" or slot.get("text") == "请上传图片"
        )
        slot_count_changed = len(after_slots) != len(before_slots)
        slot_content_changed = before_slots != after_slots
        slot_has_image = after_image_count > before_image_count or (
            after_image_count > 0 and after_empty_slot_count < before_empty_slot_count
        )

        if before_image_count > slot_index and trigger_mode == "occupied_slot_replace" and not slot_content_changed and not slot_count_changed:
            page_state = replacement_state
        elif before_empty_slot_count > slot_index and not slot_content_changed and not slot_count_changed:
            page_state = pending_state
        elif trigger_ok and upload_result.get("success") and slot_has_image:
            page_state = success_state
        else:
            page_state = "publish_entry"

        success = bool(
            trigger_ok
            and upload_result.get("success")
            and slot_has_image
            and (slot_content_changed or slot_count_changed)
        )
        screenshot_path = adapter.capture_window(window_handle)
        message = "；".join(
            [
                f"上传入口={'成功' if trigger_ok else '失败'}",
                f"触发模式={trigger_mode}",
                f"文件写入={'成功' if upload_result.get('success') else '失败'}",
                f"槽位变化={'成功' if (slot_content_changed or slot_count_changed) else '失败'}",
                f"图片出现={'成功' if slot_has_image else '失败'}",
                f"上传前图片数={before_image_count}",
                f"上传后图片数={after_image_count}",
                f"上传前空槽数={before_empty_slot_count}",
                f"上传后空槽数={after_empty_slot_count}",
                f"图片预检={preflight['message']}",
                f"文件路径={file_path}",
            ]
        )
        return WorkflowStepResult(
            step_id=step_id,
            success=success,
            page_state=success_state if success else page_state,
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message=message,
        )

    def _open_hover_local_upload(self, window_handle: str, slot_index: int) -> bool:
        adapter = self.window_manager.adapter
        if not hasattr(adapter, "hover_image_upload_slot"):
            return False
        slots = adapter.inspect_image_upload_slots(window_handle) if hasattr(adapter, "inspect_image_upload_slots") else []
        empty_slots = [slot for slot in slots if slot.get("status") == "empty"]
        if slot_index < 0 or slot_index >= len(empty_slots):
            return False
        if not adapter.hover_image_upload_slot(window_handle, slot_index):
            return False
        time.sleep(0.2)
        anchor_bounds = empty_slots[slot_index]["bounds"]
        if hasattr(adapter, "click_local_upload_entry") and adapter.click_local_upload_entry(window_handle, slot_index):
            return True
        if hasattr(adapter, "click_text_near_bounds"):
            if adapter.click_text_near_bounds(window_handle, "本地上传", anchor_bounds=anchor_bounds, max_dx=520, max_dy=220):
                return True
        return self._click_first_available_texts(window_handle, ["本地上传"])

    def _open_hover_local_upload_by_text(self, window_handle: str, slot_index: int) -> bool:
        adapter = self.window_manager.adapter
        if not hasattr(adapter, "hover_text_by_index"):
            return False
        for text in ["去设置", "请上传图片"]:
            if not adapter.hover_text_by_index(window_handle, text, slot_index):
                continue
            time.sleep(0.2)
            if hasattr(adapter, "click_local_upload_entry") and adapter.click_local_upload_entry(window_handle, slot_index):
                return True
            if self._click_first_available_texts(window_handle, ["本地上传"]):
                return True
        return False

    def _complete_local_upload(self, window_handle: str, file_path: str) -> dict[str, object]:
        adapter = self.window_manager.adapter
        if hasattr(adapter, "upload_file_from_active_dialog"):
            direct_result = adapter.upload_file_from_active_dialog(file_path)
            if direct_result.get("success"):
                return self._finalize_picker_selection(window_handle, file_path, direct_result)

        top_local_clicked = False
        if hasattr(adapter, "click_local_upload_entry"):
            top_local_clicked = adapter.click_local_upload_entry(window_handle, 0)
        if not top_local_clicked and hasattr(adapter, "click_text_in_region"):
            top_local_clicked = adapter.click_text_in_region(
                window_handle,
                "本地上传",
                min_x_ratio=0.78,
                max_x_ratio=1.0,
                min_y_ratio=0.0,
                max_y_ratio=0.22,
            )
        if not top_local_clicked:
            top_local_clicked = self._click_first_available_texts(window_handle, ["本地上传"])
        if top_local_clicked:
            time.sleep(0.2)
        upload_button_clicked = False
        if hasattr(adapter, "click_upload_image_entry"):
            upload_button_clicked = adapter.click_upload_image_entry(window_handle)
        if not upload_button_clicked and hasattr(adapter, "click_text_in_region"):
            upload_button_clicked = adapter.click_text_in_region(
                window_handle,
                "上传图片",
                min_x_ratio=0.78,
                max_x_ratio=1.0,
                min_y_ratio=0.05,
                max_y_ratio=0.40,
            )
        if not upload_button_clicked:
            upload_button_clicked = self._click_first_available_texts(window_handle, ["上传图片"])
        if upload_button_clicked:
            time.sleep(0.3)

        if hasattr(adapter, "upload_file_from_active_dialog"):
            second_result = adapter.upload_file_from_active_dialog(file_path)
            if second_result.get("success"):
                second_result["modal_local_upload"] = bool(top_local_clicked or upload_button_clicked)
                return self._finalize_picker_selection(window_handle, file_path, second_result)
            return second_result
        return {"success": False, "error": "upload_bridge_unavailable"}

    def _finalize_picker_selection(
        self,
        window_handle: str,
        file_path: str,
        upload_result: dict[str, object],
    ) -> dict[str, object]:
        """若当前仍在京麦图片管理弹层中，则选中图片并点击确定。"""

        adapter = self.window_manager.adapter
        document_text = adapter.read_document_text(window_handle)
        picker_visible = self._document_contains_any(document_text, ["本地上传", "上传图片", "确定", "共10000条"])
        if not picker_visible:
            return upload_result

        if hasattr(adapter, "select_uploaded_image_and_confirm"):
            picker_result = adapter.select_uploaded_image_and_confirm(window_handle, file_path)
            if picker_result.get("success"):
                upload_result["picker_selection_confirmed"] = True
                return upload_result
            upload_result["success"] = False
            upload_result["error"] = picker_result.get("error", "picker_selection_failed")
            return upload_result

        file_name = Path(file_path).name
        file_stem = Path(file_path).stem
        selected = False
        for _ in range(10):
            if adapter.click_text(window_handle, file_name):
                selected = True
                break
            if adapter.click_text(window_handle, file_stem):
                selected = True
                break
            time.sleep(0.3)

        if not selected:
            upload_result["success"] = False
            upload_result["error"] = "picker_uploaded_image_not_selectable"
            return upload_result

        confirmed = False
        for _ in range(5):
            if hasattr(adapter, "click_text_in_region"):
                if adapter.click_text_in_region(
                    window_handle,
                    "确定",
                    min_x_ratio=0.88,
                    max_x_ratio=1.0,
                    min_y_ratio=0.88,
                    max_y_ratio=1.0,
                ):
                    confirmed = True
                    break
            if adapter.click_text(window_handle, "确定"):
                confirmed = True
                break
            time.sleep(0.2)

        if not confirmed:
            upload_result["success"] = False
            upload_result["error"] = "picker_confirm_button_not_clicked"
            return upload_result

        upload_result["picker_selection_confirmed"] = True
        return upload_result

    def _append_runtime_log(
        self,
        *,
        window_handle: str,
        log_type: str,
        message: str,
        detail_path: str | None,
        step_id: str,
    ) -> None:
        if self.runtime_log_repo is None:
            return
        self.runtime_log_repo.append_log(
            session_id=f"window-{window_handle}",
            log_type=log_type,
            message=message,
            detail_path=detail_path,
            step_id=step_id,
        )

    def _click_first_available_texts(self, window_handle: str, texts: list[str]) -> bool:
        adapter = self.window_manager.adapter
        for text in texts:
            if adapter.click_text(window_handle, text):
                return True
        return False

    @staticmethod
    def _document_contains_any(document_text: str, values: list[str]) -> bool:
        return any(value and value in document_text for value in values)

    @staticmethod
    def _value_visible_in_document(field_name: str, value: str, document_text: str) -> bool:
        if value in document_text:
            return True
        if field_name == "品牌":
            short_value = value.split("-", 1)[0].strip()
            return bool(short_value and short_value in document_text)
        if field_name == "包装清单":
            first_chunk = value.split("，", 1)[0].strip()
            return bool(first_chunk and first_chunk in document_text)
        return False

    @staticmethod
    def _validate_upload_image_file(file_path: str) -> dict[str, object]:
        resolved_path = Path(file_path)
        if not resolved_path.exists():
            return {"success": False, "message": f"图片不存在: {resolved_path}"}
        try:
            with Image.open(resolved_path) as image:
                width, height = image.size
        except Exception as exc:
            return {"success": False, "message": f"图片无法读取: {exc}"}

        if width < 480 or height < 480:
            return {"success": False, "message": f"图片尺寸不足: {width}x{height}，最小 480x480"}
        if width != height:
            return {"success": False, "message": f"方图要求未满足: {width}x{height}"}
        return {"success": True, "message": f"通过 {width}x{height} 方图预检"}

    def _extract_category_path(self, window_handle: str) -> str | None:
        document_text = self.window_manager.adapter.read_document_text(window_handle)
        matched = re.search(r"商品类目\s*([^\n]+?)\s*修改", document_text)
        if matched:
            category_path = " ".join(matched.group(1).split())
            return category_path.strip()
        return None
