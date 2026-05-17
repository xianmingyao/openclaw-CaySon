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

    T6_EMPTY_SLOT_TEXTS = {"请上传图片", "请上传主图", "请上传透图"}
    TITLE_AUTOMATION_ID = "jd-id-8403-277"
    BRAND_AUTOMATION_ID = "jd-id-8403-278"
    MODEL_AUTOMATION_ID = "jd-id-8403-279"
    REQUIRED_ATTR_AUTOMATION_ID = "jd-id-8403-284"
    LOGISTICS_AUTOMATION_IDS = {
        "shelf_life_days": "jd-id-8403-286",
        "sale_unit": "jd-id-8403-287",
        "package_spec": "jd-id-8403-288",
        "package_spec_unit": "jd-id-8403-289",
        "package_type": "jd-id-8403-290",
        "delivery_mark": "jd-id-8403-291",
        "package_list": "jd-id-8403-293",
        "warranty_period": "jd-id-8403-294",
    }

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
        adapter = self.window_manager.adapter
        document_text = adapter.read_document_text(window_handle)
        document_text = self._wait_for_t3_known_document(window_handle, document_text)
        entered_from_draft_list = False
        if self._is_draft_list_document(document_text):
            entered_from_draft_list = self._click_publish_entry_from_draft_list(window_handle)
            if entered_from_draft_list:
                for _ in range(10):
                    time.sleep(0.5)
                    document_text = adapter.read_document_text(window_handle)
                    if (
                        self._extract_category_path_from_text(document_text)
                        or self._is_publish_form_document(document_text)
                        or self._is_category_selection_document(document_text)
                    ):
                        break

        advanced_category_page = False
        if self._is_category_selection_document(document_text):
            advanced_category_page = self._advance_category_selection_page(window_handle, document_text)
            if advanced_category_page:
                for _ in range(16):
                    time.sleep(0.5)
                    document_text = adapter.read_document_text(window_handle)
                    if self._extract_category_path_from_text(document_text) or self._is_publish_form_document(document_text):
                        break

        category_path = self._extract_category_path_from_text(document_text)
        form_visible = self._is_publish_form_document(document_text)
        screenshot_path = adapter.capture_window(window_handle)
        success = bool(category_path or form_visible)
        entry_messages = []
        if entered_from_draft_list:
            entry_messages.append("已从草稿箱进入发布入口")
        if advanced_category_page:
            entry_messages.append("已推进类目选择页")
        entry_message = f"；{'；'.join(entry_messages)}" if entry_messages else ""
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
            message=(
                f"已确认商品类目: {category_path}{entry_message}"
                if category_path
                else f"发布表单已可见但未解析类目{entry_message}"
                if form_visible
                else "未识别到商品类目"
            ),
        )

    def run_t4_fill_base_info(
        self,
        window_handle: str,
        *,
        title: str,
        model: str,
        required_attribute: str,
        brand: str | None = None,
        input_mode: str | None = None,
    ) -> WorkflowStepResult:
        adapter = self.window_manager.adapter
        if hasattr(adapter, "prepare_publish_form_view"):
            adapter.prepare_publish_form_view(window_handle, home=True)
        title_filled = adapter.fill_edit_by_label(window_handle, "商品标题", title)
        if not title_filled:
            title_filled = adapter.fill_edit_by_automation_id(window_handle, self.TITLE_AUTOMATION_ID, title)

        model_filled = adapter.fill_edit_by_label(window_handle, "型号", model)
        if not model_filled:
            model_filled = adapter.fill_edit_by_automation_id(window_handle, self.MODEL_AUTOMATION_ID, model)

        brand_filled = True
        selected_brand = brand or ""
        if brand:
            brand_filled, selected_brand = self._fill_t4_brand(window_handle, brand)

        attr_filled, selected_attribute = self._fill_t4_required_attribute(
            window_handle,
            required_attribute,
        )

        document_text = adapter.read_document_text(window_handle)
        title_ok = title in document_text
        model_ok = model in document_text
        attr_ok = selected_attribute in document_text
        brand_ok = True if not brand else self._brand_value_selected(selected_brand, document_text)
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
                f"必填属性值={selected_attribute}",
                f"品牌填充={'成功' if brand_filled else '失败' if brand else '未要求'}",
                f"品牌校验={'成功' if brand_ok else '失败' if brand else '未要求'}",
                f"品牌值={selected_brand}" if brand else "品牌值=未要求",
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

    def _fill_t4_brand(self, window_handle: str, brand: str) -> tuple[bool, str]:
        adapter = self.window_manager.adapter
        candidates = self._t4_brand_candidates(window_handle, brand)
        for value in candidates:
            filled = adapter.select_combobox_by_label(window_handle, "品牌", value)
            if not filled:
                filled = adapter.select_combobox_by_automation_id(window_handle, self.BRAND_AUTOMATION_ID, value)
            if filled:
                return True, value
        return False, brand

    def _t4_brand_candidates(self, window_handle: str, brand: str) -> list[str]:
        candidates = [brand]
        probe = getattr(self.window_manager.adapter, "probe_select_options_by_label", None)
        if not callable(probe):
            return candidates

        try:
            result = probe(window_handle, "品牌")
        except Exception:
            return candidates

        option_texts = [
            str(item.get("text") or "").strip()
            for item in result.get("options", [])
            if isinstance(item, dict) and str(item.get("text") or "").strip()
        ]
        if not option_texts:
            return candidates

        short_brand = brand.split("-", 1)[0].strip()
        matched = [
            option
            for option in option_texts
            if brand in option or (short_brand and short_brand in option)
        ]
        for value in matched:
            if value not in candidates:
                candidates.append(value)
        return candidates

    def _fill_t4_required_attribute(self, window_handle: str, required_attribute: str) -> tuple[bool, str]:
        adapter = self.window_manager.adapter
        candidates = [
            required_attribute,
            "打火线",
            "零火",
            "固定座",
            "台架",
            "无线缆件",
            "理线器/集线器/绕线器",
            "穿线器",
        ]
        seen: set[str] = set()
        for value in candidates:
            if not value or value in seen:
                continue
            seen.add(value)
            filled = adapter.select_combobox_by_label(window_handle, "类型", value)
            if not filled:
                filled = adapter.fill_edit_by_label(window_handle, "类型", value)
            if not filled:
                filled = adapter.fill_edit_by_automation_id(window_handle, self.REQUIRED_ATTR_AUTOMATION_ID, value)
            if not filled:
                continue
            time.sleep(0.3)
            document_text = adapter.read_document_text(window_handle)
            if value in document_text and "无数据" not in document_text and not re.search(r"类型\s*\*\s*请选择", document_text):
                return True, value
        return False, required_attribute

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
        if hasattr(adapter, "prepare_publish_form_view"):
            adapter.prepare_publish_form_view(window_handle)
        self._open_top_publish_tab(window_handle, ["商品售后及其他", "商品物流"])

        selected_sale_unit = self._choose_select_value(
            window_handle,
            "销售单位",
            sale_unit,
            fallbacks=["件", "个", "只", "包", "把", "张", "枚"],
        )
        warranty_options = self._expand_warranty_period_options(warranty_period)
        actions = [
            (
                "保质期（天）",
                self._fill_edit_by_id_or_label(
                    window_handle,
                    self.LOGISTICS_AUTOMATION_IDS["shelf_life_days"],
                    "保质期",
                    warranty_period,
                ),
                [warranty_period],
            ),
            (
                "销售单位",
                self._select_combobox_by_id_or_label(
                    window_handle,
                    self.LOGISTICS_AUTOMATION_IDS["sale_unit"],
                    "销售单位",
                    [selected_sale_unit],
                ),
                [selected_sale_unit],
            ),
            (
                "商品包装",
                self._select_combobox_by_id_or_label(
                    window_handle,
                    self.LOGISTICS_AUTOMATION_IDS["package_type"],
                    "商品包装",
                    [package_type],
                ),
                [package_type],
            ),
            (
                "特殊发货时效标记",
                self._select_combobox_by_id_or_label(
                    window_handle,
                    self.LOGISTICS_AUTOMATION_IDS["delivery_mark"],
                    "特殊发货时效标记",
                    [delivery_mark],
                ),
                [delivery_mark],
            ),
            (
                "包装清单",
                self._fill_edit_by_id_or_label(
                    window_handle,
                    self.LOGISTICS_AUTOMATION_IDS["package_list"],
                    "包装清单",
                    package_list,
                ),
                [package_list],
            ),
            (
                "质保期",
                self._select_combobox_by_id_or_label(
                    window_handle,
                    self.LOGISTICS_AUTOMATION_IDS["warranty_period"],
                    "质保期",
                    warranty_options,
                ),
                warranty_options,
            ),
        ]

        if hasattr(adapter, "prepare_publish_form_view"):
            adapter.prepare_publish_form_view(window_handle)
        document_text = adapter.read_document_text(window_handle)
        validation = {
            name: any(self._t7_field_value_visible(name, value, document_text) for value in values)
            for name, _, values in actions
        }
        success = all(validation.values())
        screenshot_path = adapter.capture_window(window_handle)
        message = "；".join(
            f"{name}填充={'成功' if (fill_ok or validation[name]) else '失败'}，校验={'成功' if validation[name] else '失败'}"
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

    def run_t5_fill_required_fields(
        self,
        window_handle: str,
        *,
        market_price: str | None = None,
        purchase_price: str | None = None,
        jd_price: str | None = None,
        current: str | None = None,
        weight: str | None = None,
        length_mm: str | None = None,
        width_mm: str | None = None,
        height_mm: str | None = None,
        factory_inventory: str | None = None,
    ) -> WorkflowStepResult:
        adapter = self.window_manager.adapter
        if hasattr(adapter, "prepare_publish_form_view"):
            adapter.prepare_publish_form_view(window_handle)

        top_field_specs: list[tuple[str, list[str], str | None]] = [
            ("市场价(元)", ["市场价(元)", "市场价"], market_price),
            ("京东价(元)", ["京东价(元)", "京东价"], jd_price),
            ("采购价(元)", ["采购价(元)", "采购价"], purchase_price),
            ("电流", ["电流"], current),
            ("厂直库存", ["厂直库存"], factory_inventory),
        ]
        logistics_field_specs: list[tuple[str, list[str], str | None]] = [
            ("商品毛重(kg)", ["商品毛重(kg)", "商品毛重", "重量"], weight),
            ("[包装]长(mm)", ["[包装]长(mm)", "包装长", "长度"], length_mm),
            ("[包装]宽(mm)", ["[包装]宽(mm)", "包装宽", "宽度"], width_mm),
            ("[包装]高(mm)", ["[包装]高(mm)", "包装高", "高度"], height_mm),
        ]

        actions: list[tuple[str, bool, str]] = []
        for field_name, labels, value in top_field_specs:
            if value is None or str(value).strip() == "":
                continue
            normalized_value = str(value).strip()
            fill_ok = False
            for label in labels:
                if adapter.fill_edit_by_label(window_handle, label, normalized_value):
                    fill_ok = True
                    break
            actions.append((field_name, fill_ok, normalized_value))

        if any(value is not None and str(value).strip() for _, _, value in logistics_field_specs):
            self._open_top_publish_tab(window_handle, ["商品物流", "商品售后及其他"])
            time.sleep(0.2)
            for field_name, labels, value in logistics_field_specs:
                if value is None or str(value).strip() == "":
                    continue
                normalized_value = str(value).strip()
                fill_ok = False
                for label in labels:
                    if adapter.fill_edit_by_label(window_handle, label, normalized_value):
                        fill_ok = True
                        break
                actions.append((field_name, fill_ok, normalized_value))

        document_text = adapter.read_document_text(window_handle)
        validation = {
            field_name: self._t5_field_value_visible(field_name, value, document_text)
            for field_name, _, value in actions
        }
        success = bool(actions) and all(validation.values())
        screenshot_path = adapter.capture_window(window_handle)
        message = "；".join(
            f"{field_name}填充={'成功' if (fill_ok or validation[field_name]) else '失败'}，校验={'成功' if validation[field_name] else '失败'}"
            for field_name, fill_ok, _ in actions
        ) or "未提供 T5/发布表单必填项"
        return WorkflowStepResult(
            step_id="T5-REQUIRED-FIELDS",
            success=success,
            page_state="required_fields_completed" if success else "publish_entry",
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message=message,
        )

    def _open_top_publish_tab(self, window_handle: str, tab_texts: list[str]) -> bool:
        """点击发布页顶部阶段页签，避开页面正文和左侧报错导航中的同名文本。"""

        adapter = self.window_manager.adapter
        for text in tab_texts:
            try:
                clicked = adapter.click_text_in_region(
                    window_handle,
                    text,
                    min_x_ratio=0.22,
                    max_x_ratio=0.86,
                    min_y_ratio=0.06,
                    max_y_ratio=0.14,
                )
            except Exception:
                clicked = False
            if clicked:
                time.sleep(0.6)
                return True
        return False

    def _choose_select_value(
        self,
        window_handle: str,
        label: str,
        requested_value: str,
        *,
        fallbacks: list[str],
    ) -> str:
        """在京麦下拉项受类目约束时，选择当前页面真实可用的值。"""

        adapter = self.window_manager.adapter
        try:
            probe = adapter.probe_select_options_by_label(window_handle, label)
        except Exception:
            return requested_value

        option_texts = [str(item.get("text") or "").strip() for item in probe.get("options", [])]
        option_texts = [item for item in option_texts if item]
        if requested_value in option_texts:
            return requested_value
        for fallback in fallbacks:
            if fallback in option_texts:
                return fallback
        return requested_value

    @staticmethod
    def _t7_field_value_visible(field_name: str, value: str, document_text: str) -> bool:
        boundaries = {
            "保质期（天）": ["销售单位"],
            "销售单位": ["包装规格"],
            "商品包装": ["特殊发货时效标记"],
            "特殊发货时效标记": ["是否危险商品", "包装清单"],
            "包装清单": ["商品售后及其他", "质保期"],
            "质保期": ["发布商品", "保存草稿"],
        }
        end_markers = boundaries.get(field_name)
        if not end_markers:
            return JingmaiWorkflowService._value_visible_in_document(field_name, value, document_text)

        values = [value]
        if field_name == "包装清单":
            first_chunk = value.split("，", 1)[0].strip()
            if first_chunk and first_chunk not in values:
                values.append(first_chunk)

        start_positions = [match.start() for match in re.finditer(re.escape(field_name), document_text)]
        saw_field_slice = False
        for start in reversed(start_positions):
            after_label = document_text[start + len(field_name) : start + len(field_name) + 20].lstrip()
            if after_label.startswith("填写规范") or after_label.startswith("不可为空"):
                continue
            saw_field_slice = True
            end = len(document_text)
            for marker in end_markers:
                marker_index = document_text.find(marker, start + len(field_name))
                if marker_index != -1:
                    end = min(end, marker_index)
            field_text = document_text[start:end]
            if any(candidate and candidate in field_text for candidate in values):
                return True
        if not saw_field_slice:
            return JingmaiWorkflowService._value_visible_in_document(field_name, value, document_text)
        return False

    @staticmethod
    def _t5_field_value_visible(field_name: str, value: str, document_text: str) -> bool:
        boundaries = {
            "市场价(元)": ["价格凭证类型", "京东价"],
            "京东价(元)": ["采购价", "毛利"],
            "采购价(元)": ["毛利", "销售员ERP"],
            "商品毛重(kg)": ["[包装]长", "[包装]宽", "商品条形码"],
            "[包装]长(mm)": ["[包装]宽"],
            "[包装]宽(mm)": ["[包装]高"],
            "[包装]高(mm)": ["商品条形码", "保质期"],
            "电流": ["厂直库存", "商品图片", "规格描述"],
            "厂直库存": ["采销信息", "商品属性"],
        }
        labels = [field_name]
        label_aliases = {
            "市场价(元)": ["市场价"],
            "京东价(元)": ["京东价"],
            "采购价(元)": ["采购价"],
            "商品毛重(kg)": ["商品毛重", "重量"],
            "[包装]长(mm)": ["[包装]长", "包装长", "长度"],
            "[包装]宽(mm)": ["[包装]宽", "包装宽", "宽度"],
            "[包装]高(mm)": ["[包装]高", "包装高", "高度"],
        }
        labels.extend(label_aliases.get(field_name, []))
        values = JingmaiWorkflowService._document_value_variants(value)

        for label in labels:
            start_positions = [match.start() for match in re.finditer(re.escape(label), document_text)]
            for start in reversed(start_positions):
                after_label = document_text[start + len(label) : start + len(label) + 24].lstrip()
                if after_label.startswith("填写规范") or after_label.startswith("不可为空"):
                    continue
                end = len(document_text)
                for marker in boundaries.get(field_name, []):
                    marker_index = document_text.find(marker, start + len(label))
                    if marker_index != -1:
                        end = min(end, marker_index)
                field_text = document_text[start:end]
                if any(candidate and candidate in field_text for candidate in values):
                    return True
        return any(candidate and candidate in document_text for candidate in values)

    @staticmethod
    def _document_value_variants(value: str) -> list[str]:
        variants = [value.strip()]
        try:
            from decimal import Decimal

            decimal_value = Decimal(value.strip())
            normalized = format(decimal_value.normalize(), "f")
            if "." in normalized:
                normalized = normalized.rstrip("0").rstrip(".")
            for candidate in (normalized, f"{decimal_value:.2f}"):
                if candidate and candidate not in variants:
                    variants.append(candidate)
        except Exception:
            pass
        return variants

    def _fill_edit_by_id_or_label(self, window_handle: str, automation_id: str, label: str, value: str) -> bool:
        adapter = self.window_manager.adapter
        if adapter.fill_edit_by_label(window_handle, label, value):
            return True
        return adapter.fill_edit_by_automation_id(window_handle, automation_id, value)

    def _select_combobox_by_id_or_label(
        self,
        window_handle: str,
        automation_id: str,
        label: str,
        values: list[str],
    ) -> bool:
        adapter = self.window_manager.adapter
        for value in values:
            if adapter.select_combobox_by_label(window_handle, label, value):
                return True
            if adapter.select_combobox_by_automation_id(window_handle, automation_id, value):
                return True
        return False

    @staticmethod
    def _normalize_warranty_period(value: str) -> str:
        """把 CLI 常用天数映射为京麦质保期下拉里的真实枚举文案。"""

        normalized = value.strip()
        mapping = {
            "0": "无质保",
            "30": "1个月质保",
            "90": "3个月质保",
            "180": "6个月质保",
            "365": "1年质保",
            "730": "2年质保",
            "1095": "3年质保",
        }
        return mapping.get(normalized, normalized)

    @classmethod
    def _expand_warranty_period_options(cls, value: str) -> list[str]:
        """生成质保期下拉可尝试值，兼容类目只给少量枚举的情况。"""

        normalized = value.strip()
        candidates = [cls._normalize_warranty_period(normalized), normalized, "3年质保"]
        deduped: list[str] = []
        seen: set[str] = set()
        for candidate in candidates:
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            deduped.append(candidate)
        return deduped

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

    def run_t6_upload_main_image(
        self,
        window_handle: str,
        file_path: str,
        upload_strategy: str | None = None,
    ) -> WorkflowStepResult:
        return self._run_t6_upload_slot(
            window_handle,
            file_path=file_path,
            slot_index=0,
            step_id="T6-MAIN-IMAGE",
            success_state="main_image_uploaded",
            pending_state="main_image_empty_slot_pending",
            replacement_state="main_image_replacement_pending",
            upload_strategy=upload_strategy,
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
        if hasattr(adapter, "close_image_preview_overlay"):
            adapter.close_image_preview_overlay(window_handle)

        document_before = adapter.read_document_text(window_handle)

        nav_ok = self._click_first_available_texts(window_handle, ["商品描述", "商品详情"])
        time.sleep(0.3)
        mode_ok = self._click_first_available_texts(
            window_handle,
            ["代码编辑", "高级编辑", "图文编辑推荐", "编辑商品详情", "点击使用"],
        )
        trigger_ok = nav_ok or mode_ok

        typing_result = {"success": False, "error": "detail_editor_not_activated"}
        if trigger_ok and hasattr(adapter, "type_into_detail_editor"):
            typing_result = adapter.type_into_detail_editor(window_handle, detail_content)
        elif trigger_ok and hasattr(adapter, "type_into_focused_control"):
            typing_result = adapter.type_into_focused_control(window_handle, detail_content, submit=False)

        document_after = adapter.read_document_text(window_handle)
        content_visible = self._detail_content_visible(
            detail_content,
            document_before,
            document_after,
            typing_result,
        )
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
                f"焦点路径={typing_result.get('focus_method') or 'focused_control'}",
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

    @staticmethod
    def _detail_content_visible(
        detail_content: str,
        document_before: str,
        document_after: str,
        typing_result: dict[str, object],
    ) -> bool:
        content_probe = detail_content[: min(len(detail_content), 24)]
        if content_probe and content_probe in document_after:
            return True
        if typing_result.get("after_contains"):
            return True
        if not typing_result.get("success"):
            return False

        placeholders = ["请补充商品描述", "请输入正文", "暂未编辑商详", "0 /100000"]
        placeholders_before = any(value in document_before for value in placeholders)
        placeholders_after = any(value in document_after for value in placeholders)
        if placeholders_before and not placeholders_after:
            return True

        return len(document_after) > len(document_before) and "商品详情" in document_after

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
        draft_list_visible = self._is_draft_list_document(document_text)
        save_visible = "保存草稿" in document_text
        publish_visible = "发布商品" in document_text
        success = draft_list_visible or (save_visible and publish_visible and save_candidate and publish_candidate)
        screenshot_path = adapter.capture_window(window_handle)
        message = "；".join(
            [
                f"保存草稿按钮定位={'成功' if save_candidate else '失败'}",
                f"保存草稿文案={'成功' if save_visible else '失败'}",
                f"发布商品按钮定位={'成功' if publish_candidate else '失败'}",
                f"发布商品文案={'成功' if publish_visible else '失败'}",
                f"草稿列表={'成功' if draft_list_visible else '失败'}",
            ]
        )
        return WorkflowStepResult(
            step_id="T8-PROBE",
            success=success,
            page_state="draft_list" if draft_list_visible else "submit_ready" if success else "publish_entry",
            window_handle=window_handle,
            screenshot_path=screenshot_path,
            message=message,
        )

    def run_t8_save_draft(self, window_handle: str, click_mode: str | None = None) -> WorkflowStepResult:
        adapter = self.window_manager.adapter
        document_before = adapter.read_document_text(window_handle)
        if self._is_draft_list_document(document_before):
            screenshot_path = adapter.capture_window(window_handle)
            return WorkflowStepResult(
                step_id="T8-SAVE-DRAFT",
                success=True,
                page_state="draft_saved",
                window_handle=window_handle,
                screenshot_path=screenshot_path,
                message="草稿列表已可见；触发模式=already_saved",
            )

        save_texts = ["保存草稿"]
        clicked = self._click_first_available_texts(window_handle, save_texts)
        document_after = document_before
        draft_state = "not_clicked"
        poll_count = 0
        menu_confirmed = "not_required"
        if clicked:
            for poll_count in range(1, 17):
                document_after = adapter.read_document_text(window_handle)
                if "保存发品模板" in document_after and menu_confirmed == "not_required":
                    menu_confirmed = "failed"
                    if hasattr(adapter, "click_text_in_region"):
                        menu_clicked = adapter.click_text_in_region(
                            window_handle,
                            "保存草稿",
                            min_x_ratio=0.45,
                            max_x_ratio=0.62,
                            min_y_ratio=0.86,
                            max_y_ratio=0.95,
                        )
                        if menu_clicked:
                            menu_confirmed = "success"
                            time.sleep(0.3)
                            continue
                draft_state = self._classify_draft_save_document(document_after)
                if draft_state in {"draft_list", "success_hint", "failure_hint"}:
                    break
                time.sleep(0.5)
        state_changed = document_before != document_after
        blank_publish_form = self._is_blank_publish_form_after_save(document_before, document_after)
        if blank_publish_form and draft_state not in {"draft_list", "success_hint", "failure_hint"}:
            draft_state = "blank_publish_form"
        draft_confirmed = draft_state in {"draft_list", "success_hint", "blank_publish_form"}
        screenshot_path = adapter.capture_window(window_handle)
        success = bool(clicked and draft_confirmed)
        page_state = "draft_saved" if success else "draft_save_pending"
        message = "；".join(
            [
                f"草稿点击={'成功' if clicked else '失败'}",
                f"页面变化={'成功' if state_changed else '失败'}",
                f"草稿确认={'成功' if draft_confirmed else '失败'}",
                f"菜单确认={menu_confirmed}",
                f"触发模式={draft_state}",
                f"文档轮询次数={poll_count}",
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

    def run_t8_publish_product(self, window_handle: str, confirm_publish: bool = False) -> WorkflowStepResult:
        adapter = self.window_manager.adapter
        if not confirm_publish:
            screenshot_path = adapter.capture_window(window_handle)
            return WorkflowStepResult(
                step_id="T8-PUBLISH-PRODUCT",
                success=False,
                page_state="publish_guard_required",
                window_handle=window_handle,
                screenshot_path=screenshot_path,
                message="正式发布被守卫拦截：必须显式传入 confirm_publish=True 或 CLI 参数 --confirm-publish。",
            )
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
        upload_strategy: str | None = None,
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

        if hasattr(adapter, "close_image_preview_overlay"):
            adapter.close_image_preview_overlay(window_handle)

        before_slots = self._ensure_t6_image_upload_surface(window_handle, slot_index=slot_index)
        before_image_count = sum(
            1 for slot in before_slots if slot.get("status") == "filled" or slot.get("class_name") == "Image"
        )
        before_empty_slot_count = self._count_t6_empty_slots(before_slots)
        empty_slot_action_index = self._resolve_t6_empty_slot_action_index(before_slots, slot_index=slot_index)
        if self._is_t6_target_slot_filled(before_slots, slot_index=slot_index):
            screenshot_path = adapter.capture_window(window_handle)
            message = "；".join(
                [
                    "上传入口=已完成",
                    "触发模式=already_filled",
                    "文件写入=跳过",
                    "槽位变化=无需变化",
                    "图片出现=成功",
                    f"上传前图片数={before_image_count}",
                    f"上传前空槽数={before_empty_slot_count}",
                    f"图片预检={preflight['message']}",
                    f"文件路径={file_path}",
                ]
            )
            return WorkflowStepResult(
                step_id=step_id,
                success=True,
                page_state=success_state,
                window_handle=window_handle,
                screenshot_path=screenshot_path,
                message=message,
            )

        trigger_ok = False
        trigger_mode = upload_strategy or "empty_slot"
        upload_result = {"success": False, "error": "upload_bridge_unavailable"}

        upload_attempts: list[str]
        if upload_strategy == "direct_click":
            upload_attempts = ["empty_slot_modal", "hover_local_upload", "hover_text_local_upload", "text_index_fallback", "text_fallback"]
        elif upload_strategy == "text_fallback":
            upload_attempts = ["hover_text_local_upload", "text_index_fallback", "text_fallback", "empty_slot_modal", "hover_local_upload"]
        else:
            upload_attempts = ["hover_local_upload", "hover_text_local_upload", "empty_slot_modal", "occupied_slot_replace", "text_index_fallback", "text_fallback"]

        for attempt in upload_attempts:
            if upload_result.get("success"):
                break

            if attempt == "hover_local_upload" and empty_slot_action_index is not None and self._open_hover_local_upload(window_handle, empty_slot_action_index):
                trigger_ok = True
                trigger_mode = "hover_local_upload"
                upload_result = self._complete_local_upload(window_handle, file_path, slot_index=empty_slot_action_index)
                continue

            if attempt == "hover_text_local_upload" and empty_slot_action_index is not None and self._open_hover_local_upload_by_text(window_handle, empty_slot_action_index):
                trigger_ok = True
                trigger_mode = "hover_text_local_upload"
                upload_result = self._complete_local_upload(window_handle, file_path, slot_index=empty_slot_action_index)
                if trigger_ok:
                    continue

            if attempt == "empty_slot_modal" and empty_slot_action_index is not None and hasattr(adapter, "click_image_upload_slot"):
                trigger_ok = adapter.click_image_upload_slot(window_handle, empty_slot_action_index)
                if trigger_ok:
                    trigger_mode = "empty_slot_modal"
                    upload_result = self._complete_local_upload(window_handle, file_path, slot_index=empty_slot_action_index)
                    continue

            if attempt == "occupied_slot_replace" and before_image_count > slot_index and hasattr(adapter, "click_existing_image_slot"):
                trigger_ok = adapter.click_existing_image_slot(window_handle, slot_index)
                if trigger_ok:
                    trigger_mode = "occupied_slot_replace"
                    upload_result = self._complete_local_upload(window_handle, file_path, slot_index=slot_index)
                    continue

            if attempt == "text_index_fallback" and hasattr(adapter, "click_text_by_index"):
                for text in self._t6_upload_trigger_texts(slot_index):
                    text_index = empty_slot_action_index if text == "请上传图片" and empty_slot_action_index is not None else 0
                    trigger_ok = adapter.click_text_by_index(window_handle, text, text_index)
                    if trigger_ok:
                        trigger_mode = f"text_index_fallback:{text}"
                        upload_result = self._complete_local_upload(window_handle, file_path, slot_index=empty_slot_action_index or 0)
                        break
                continue

            if attempt == "text_fallback":
                trigger_ok = self._click_first_available_texts(
                    window_handle,
                    ["去设置", *self._t6_upload_trigger_texts(slot_index), "图片设置"],
                )
                if trigger_ok:
                    trigger_mode = "text_fallback"
                    upload_result = self._complete_local_upload(window_handle, file_path, slot_index=empty_slot_action_index or 0)

        slot_probe = self._wait_for_upload_slot_update(
            window_handle,
            before_slots=before_slots,
            before_image_count=before_image_count,
            before_empty_slot_count=before_empty_slot_count,
        )
        after_slots = slot_probe["after_slots"]
        after_image_count = int(slot_probe["after_image_count"])
        after_empty_slot_count = int(slot_probe["after_empty_slot_count"])
        slot_count_changed = bool(slot_probe["slot_count_changed"])
        slot_content_changed = bool(slot_probe["slot_content_changed"])
        slot_has_image = bool(slot_probe["slot_has_image"])
        picker_retry = "not_required"

        if trigger_ok and upload_result.get("success") and not slot_has_image:
            retry_result = self._finalize_picker_selection(window_handle, file_path, dict(upload_result))
            picker_retry = "success" if retry_result.get("picker_selection_confirmed") else "failed"
            if retry_result.get("success"):
                upload_result = retry_result
                slot_probe = self._wait_for_upload_slot_update(
                    window_handle,
                    before_slots=before_slots,
                    before_image_count=before_image_count,
                    before_empty_slot_count=before_empty_slot_count,
                )
                after_slots = slot_probe["after_slots"]
                after_image_count = int(slot_probe["after_image_count"])
                after_empty_slot_count = int(slot_probe["after_empty_slot_count"])
                slot_count_changed = bool(slot_probe["slot_count_changed"])
                slot_content_changed = bool(slot_probe["slot_content_changed"])
                slot_has_image = bool(slot_probe["slot_has_image"])

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
                f"槽位轮询次数={slot_probe['poll_count']}",
                f"选择确认重试={picker_retry}",
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

    def _ensure_t6_image_upload_surface(self, window_handle: str, *, slot_index: int) -> list[dict[str, object]]:
        """确保当前处在 SKU 图片槽位可操作区域。

        真实京麦在主图上传后可能回到 `SKU基本信息` 子页签，只在“图片设置”列显示
        `已设置/去查看/请上传图片`。此时直接找槽位会失败，需要先切回 `SKU图片信息`
        或点击查看入口，再执行悬停上传。
        """

        adapter = self.window_manager.adapter
        if not hasattr(adapter, "inspect_image_upload_slots"):
            return []

        slots = adapter.inspect_image_upload_slots(window_handle)
        if self._has_t6_slot_target(slots, slot_index=slot_index):
            return slots

        for text in ["商品图片", "主图", "SKU图片信息", "去查看", "图片设置"]:
            clicked = False
            if hasattr(adapter, "click_text"):
                clicked = adapter.click_text(window_handle, text)
            if not clicked and hasattr(adapter, "click_text_by_index"):
                clicked = adapter.click_text_by_index(window_handle, text, 0)
            if not clicked:
                continue
            time.sleep(0.5)
            slots = adapter.inspect_image_upload_slots(window_handle)
            if self._has_t6_slot_target(slots, slot_index=slot_index):
                return slots

        return slots

    @staticmethod
    def _has_t6_slot_target(slots: list[dict[str, object]], *, slot_index: int) -> bool:
        if slot_index < 0:
            return False
        empty_slot_count = JingmaiWorkflowService._count_t6_empty_slots(slots)
        image_slot_count = sum(1 for slot in slots if slot.get("status") == "filled" or slot.get("class_name") == "Image")
        return empty_slot_count > slot_index or image_slot_count > slot_index or len(slots) > slot_index

    @classmethod
    def _count_t6_empty_slots(cls, slots: list[dict[str, object]]) -> int:
        return sum(1 for slot in slots if slot.get("status") == "empty" or slot.get("text") in cls.T6_EMPTY_SLOT_TEXTS)

    @classmethod
    def _resolve_t6_empty_slot_action_index(cls, slots: list[dict[str, object]], *, slot_index: int) -> int | None:
        empty_slots = [slot for slot in slots if slot.get("status") == "empty" or slot.get("text") in cls.T6_EMPTY_SLOT_TEXTS]
        if not empty_slots:
            return None
        if slot_index < len(empty_slots):
            return slot_index
        return len(empty_slots) - 1

    @staticmethod
    def _t6_upload_trigger_texts(slot_index: int) -> list[str]:
        if slot_index == 1:
            return ["请上传透图", "请上传图片"]
        return ["请上传主图", "请上传图片"]

    @staticmethod
    def _is_t6_target_slot_filled(slots: list[dict[str, object]], *, slot_index: int) -> bool:
        """判断 T6 目标列是否已经有图。

        京麦 SKU 图片区同一行里，方图列可能包含多个主图槽，透图列在其右侧。
        因此透明图不能简单按整体槽位序号判断，需要按列的横向位置识别。
        """

        for slot in slots:
            if not (slot.get("status") == "filled" or slot.get("class_name") == "Image"):
                continue
            bounds = slot.get("bounds") or {}
            left = int(bounds.get("left", 0))
            if slot_index == 0 and left < 1600:
                return True
            if slot_index == 1 and left >= 1600:
                return True
        return False

    def _wait_for_upload_slot_update(
        self,
        window_handle: str,
        *,
        before_slots: list[dict[str, object]],
        before_image_count: int,
        before_empty_slot_count: int,
        timeout_seconds: float = 6.0,
        poll_interval_seconds: float = 0.5,
    ) -> dict[str, object]:
        """等待京麦把图片选择结果回写到上传槽位。"""

        adapter = self.window_manager.adapter
        deadline = time.monotonic() + timeout_seconds
        poll_count = 0
        last_slots: list[dict[str, object]] = []

        while True:
            poll_count += 1
            if hasattr(adapter, "inspect_image_upload_slots"):
                last_slots = adapter.inspect_image_upload_slots(window_handle)
            after_image_count = sum(
                1 for slot in last_slots if slot.get("status") == "filled" or slot.get("class_name") == "Image"
            )
            after_empty_slot_count = self._count_t6_empty_slots(last_slots)
            slot_count_changed = len(last_slots) != len(before_slots)
            slot_content_changed = before_slots != last_slots
            slot_has_image = after_image_count > before_image_count or (
                after_image_count > 0 and after_empty_slot_count < before_empty_slot_count
            )
            if slot_has_image and (slot_content_changed or slot_count_changed):
                return {
                    "after_slots": last_slots,
                    "after_image_count": after_image_count,
                    "after_empty_slot_count": after_empty_slot_count,
                    "slot_count_changed": slot_count_changed,
                    "slot_content_changed": slot_content_changed,
                    "slot_has_image": slot_has_image,
                    "poll_count": poll_count,
                }
            if time.monotonic() >= deadline:
                return {
                    "after_slots": last_slots,
                    "after_image_count": after_image_count,
                    "after_empty_slot_count": after_empty_slot_count,
                    "slot_count_changed": slot_count_changed,
                    "slot_content_changed": slot_content_changed,
                    "slot_has_image": slot_has_image,
                    "poll_count": poll_count,
                }
            time.sleep(poll_interval_seconds)

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
        if hasattr(adapter, "click_text_near_bounds"):
            if adapter.click_text_near_bounds(window_handle, "本地上传", anchor_bounds=anchor_bounds, max_dx=520, max_dy=220):
                return True
        if hasattr(adapter, "click_local_upload_entry") and adapter.click_local_upload_entry(window_handle, slot_index):
            return True
        return self._click_first_available_texts(window_handle, ["本地上传"])

    def _open_hover_local_upload_by_text(self, window_handle: str, slot_index: int) -> bool:
        adapter = self.window_manager.adapter
        if not hasattr(adapter, "hover_text_by_index"):
            return False
        for text in ["去设置", *self._t6_upload_trigger_texts(slot_index)]:
            if not adapter.hover_text_by_index(window_handle, text, slot_index):
                continue
            time.sleep(0.2)
            if hasattr(adapter, "click_local_upload_entry") and adapter.click_local_upload_entry(window_handle, slot_index):
                return True
            if self._click_first_available_texts(window_handle, ["本地上传"]):
                return True
        return False

    def _complete_local_upload(self, window_handle: str, file_path: str, *, slot_index: int = 0) -> dict[str, object]:
        """完成本地文件上传的完整流程。

        正确顺序（用户反馈验证）：
        1. 在图片管理弹层中点击"本地上传"触发 Windows 文件对话框
        2. 文件对话框出现后，Alt+D 聚焦地址栏 → 输入目录路径 → 回车导航
        3. 在文件名输入框填入文件名 → 点击"打开"
        4. 回到图片管理弹层，选中已上传图片 → 点击"确定"
        """
        adapter = self.window_manager.adapter

        # -- 阶段一：点击"本地上传"触发文件对话框 --
        upload_clicked = False
        if hasattr(adapter, "click_local_upload_entry"):
            upload_clicked = adapter.click_local_upload_entry(window_handle, slot_index)
        if not upload_clicked and hasattr(adapter, "click_text_in_region"):
            upload_clicked = adapter.click_text_in_region(
                window_handle,
                "本地上传",
                min_x_ratio=0.78,
                max_x_ratio=1.0,
                min_y_ratio=0.0,
                max_y_ratio=0.22,
            )
        if not upload_clicked:
            upload_clicked = self._click_first_available_texts(window_handle, ["本地上传"])

        # 若"本地上传"未命中，尝试"上传图片"作为回退
        if not upload_clicked and hasattr(adapter, "click_upload_image_entry"):
            upload_clicked = adapter.click_upload_image_entry(window_handle)
        if not upload_clicked:
            upload_clicked = self._click_first_available_texts(window_handle, ["上传图片"])

        if upload_clicked:
            # 等待文件对话框出现（Windows 资源管理器对话框需要时间渲染）
            time.sleep(0.4)

        # 若图片空间弹层已经包含目标文件，说明之前的上传已完成但尚未选中回填。
        # 此时直接复用现有上传结果，比继续等待系统文件对话框更可靠。
        try:
            picker_text = adapter.read_document_text(window_handle)
        except Exception:
            picker_text = ""
        target_file_name = Path(file_path).name
        target_file_stem = Path(file_path).stem
        if target_file_name in picker_text or target_file_stem in picker_text:
            picker_result = self._finalize_picker_selection(
                window_handle,
                file_path,
                {"success": True, "file_path": file_path, "reused_picker_result": True},
            )
            if picker_result.get("picker_selection_confirmed"):
                return picker_result

        # -- 阶段二：与文件对话框交互（Alt+D 地址栏导航 → 选文件 → 打开）--
        if hasattr(adapter, "upload_file_from_active_dialog"):
            last_result: dict[str, object] = {"success": False, "error": "file_dialog_not_ready"}
            for _ in range(8):
                result = adapter.upload_file_from_active_dialog(file_path)
                if result.get("success"):
                    return self._finalize_picker_selection(window_handle, file_path, result)
                last_result = result
                time.sleep(0.4)
            return last_result

        return {"success": False, "error": "upload_bridge_unavailable"}

    def _finalize_picker_selection(
        self,
        window_handle: str,
        file_path: str,
        upload_result: dict[str, object],
    ) -> dict[str, object]:
        """若当前仍在京麦图片管理弹层中，则选中图片并点击确定。"""

        adapter = self.window_manager.adapter
        picker_visible = False
        for _ in range(12):
            document_text = adapter.read_document_text(window_handle)
            picker_visible = self._document_contains_any(document_text, ["本地上传", "上传图片", "确定", "共10000条"])
            if picker_visible:
                break
            time.sleep(0.3)
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

    @classmethod
    def _classify_draft_save_document(cls, document_text: str) -> str:
        if cls._is_draft_list_document(document_text):
            return "draft_list"
        if cls._document_contains_any(document_text, ["保存成功", "已保存", "草稿保存成功", "保存至草稿箱"]):
            return "success_hint"
        if cls._document_contains_any(document_text, ["保存失败", "提交失败", "系统异常", "网络异常"]):
            return "failure_hint"
        if "保存草稿" in document_text:
            return "editing_or_loading"
        return "unknown"

    @staticmethod
    def _is_draft_list_document(document_text: str) -> bool:
        return "商品草稿仅支持保留30天" in document_text or (
            "草稿箱" in document_text and "商品名称" in document_text and "编辑时间" in document_text
        )

    @classmethod
    def _is_blank_publish_form_after_save(cls, document_before: str, document_after: str) -> bool:
        return not cls._is_blank_publish_form(document_before) and cls._is_blank_publish_form(document_after)

    @staticmethod
    def _is_blank_publish_form(document_text: str) -> bool:
        return (
            "商品标题" in document_text
            and "0 / 100" in document_text
            and "暂未编辑商详" in document_text
            and "保存草稿" in document_text
            and "市场价(元)" in document_text
        )

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
    def _brand_value_selected(value: str, document_text: str) -> bool:
        candidates = [value.strip()]
        short_value = value.split("-", 1)[0].strip()
        if short_value and short_value not in candidates:
            candidates.append(short_value)

        field_match = re.search(r"品牌\s*\*\s*(?P<field>.{0,120}?)(?:短标题|型号|货号|采销信息)", document_text, re.S)
        if field_match:
            field_text = field_match.group("field")
            return any(candidate and candidate in field_text for candidate in candidates)

        if "请先选择商品品牌" in document_text or "请选择品牌" in document_text:
            return False
        return JingmaiWorkflowService._value_visible_in_document("品牌", value, document_text)

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
        return self._extract_category_path_from_text(document_text)

    @staticmethod
    def _extract_category_path_from_text(document_text: str) -> str | None:
        matched = re.search(r"商品类目\s*([^\n]+?)\s*修改", document_text)
        if matched:
            category_path = " ".join(matched.group(1).split())
            return category_path.strip()
        return None

    def _click_publish_entry_from_draft_list(self, window_handle: str) -> bool:
        adapter = self.window_manager.adapter
        if hasattr(adapter, "click_text_in_region"):
            try:
                clicked = adapter.click_text_in_region(
                    window_handle,
                    "发布商品",
                    min_x_ratio=0.82,
                    max_x_ratio=1.0,
                    min_y_ratio=0.04,
                    max_y_ratio=0.18,
                )
            except Exception:
                clicked = False
            if clicked:
                return True
        return adapter.click_text(window_handle, "发布商品")

    def _wait_for_t3_known_document(self, window_handle: str, document_text: str) -> str:
        for _ in range(12):
            if (
                self._extract_category_path_from_text(document_text)
                or self._is_publish_form_document(document_text)
                or self._is_draft_list_document(document_text)
                or self._is_category_selection_document(document_text)
            ):
                return document_text
            time.sleep(0.5)
            document_text = self.window_manager.adapter.read_document_text(window_handle)
        return document_text

    @classmethod
    def _is_category_selection_document(cls, document_text: str) -> bool:
        return "类目选择发品" in document_text and "下一步，完善其他商品信息" in document_text

    def _advance_category_selection_page(self, window_handle: str, document_text: str) -> bool:
        if self._click_recent_category_shortcut(window_handle, document_text):
            time.sleep(0.3)
            return self._click_category_next_button(window_handle) or True

        clicked_category = False
        for category_text in self._category_selection_candidates(document_text):
            if self._click_category_text(window_handle, category_text):
                clicked_category = True
                time.sleep(0.3)
                break

        clicked_next = self._click_category_next_button(window_handle)
        return clicked_category or clicked_next

    def _click_recent_category_shortcut(self, window_handle: str, document_text: str) -> bool:
        target_tokens = ["工业品", "电料辅件", "电气辅材", "电气配件"]
        if not all(token in document_text for token in target_tokens):
            return False
        click_ratio = getattr(self.window_manager.adapter, "click_window_ratio", None)
        if not callable(click_ratio):
            return False

        matched = re.search(r"近期使用类目：\s*(.+?)\s*下一步，完善其他商品信息", document_text, re.S)
        source = matched.group(1) if matched else document_text
        target_index = source.find("电料辅件")
        if target_index < 0:
            target_index = source.find("工业品")
        x_ratio = 0.238 + max(0, target_index + 8) * 0.0051
        x_ratio = max(0.27, min(0.43, x_ratio))
        return click_ratio(window_handle, x_ratio, 0.202)

    def _click_category_next_button(self, window_handle: str) -> bool:
        click_ratio = getattr(self.window_manager.adapter, "click_window_ratio", None)
        if callable(click_ratio) and click_ratio(window_handle, 0.50, 0.94):
            return True
        return self._click_first_available_texts(window_handle, ["下一步，完善其他商品信息", "下一步"])

    @staticmethod
    def _category_selection_candidates(document_text: str) -> list[str]:
        candidates: list[str] = []
        matched = re.search(r"近期使用类目：\s*(.+?)\s*下一步，完善其他商品信息", document_text, re.S)
        source = matched.group(1) if matched else document_text
        for matched_path in re.finditer(r"[\u4e00-\u9fffA-Za-z0-9、，/（）()]+(?:\s*>\s*[\u4e00-\u9fffA-Za-z0-9、，/（）()]+){2,}", source):
            value = " ".join(matched_path.group(0).split())
            if value and value not in candidates:
                candidates.append(value)
        for fallback in ["工业品 >电料辅件 >电气辅材> 电气配件", "工业品", "电脑、办公"]:
            if fallback in source and fallback not in candidates:
                candidates.append(fallback)
        return candidates

    def _click_category_text(self, window_handle: str, text: str) -> bool:
        adapter = self.window_manager.adapter
        if hasattr(adapter, "click_text_in_region"):
            try:
                clicked = adapter.click_text_in_region(
                    window_handle,
                    text,
                    min_x_ratio=0.10,
                    max_x_ratio=0.75,
                    min_y_ratio=0.18,
                    max_y_ratio=0.70,
                )
            except Exception:
                clicked = False
            if clicked:
                return True
        return adapter.click_text(window_handle, text)

    @classmethod
    def _is_publish_form_document(cls, document_text: str) -> bool:
        if cls._is_draft_list_document(document_text):
            return False
        return "商品标题" in document_text and ("保存草稿" in document_text or "商品类目" in document_text)
