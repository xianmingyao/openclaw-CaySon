"""ActionRegistry: structured ActionStep definitions replacing VALID_STEPS set.

BL-091: 24 ActionStep entries covering all previously hardcoded step dispatch.
"""

from __future__ import annotations

from .types import ActionStep, RetryLane, StepCategory

# ── 24 个 ActionStep 注册表 ──────────────────────────────────────

REGISTRY_ENTRIES: list[ActionStep] = [
    # ── T1: 窗口挂载 ──
    ActionStep(
        step_name="t1",
        method_name="run_t1_attach_window",
        description="绑定京麦发布商品窗口",
        category=StepCategory.ATTACHMENT,
        max_retry_count=2,
    ),
    # ── T2: 进入发布入口 ──
    ActionStep(
        step_name="t2",
        method_name="run_t2_enter_publish_entry",
        description="点击发布商品入口，进入类目确认页",
        preconditions=("t1",),
        category=StepCategory.NAVIGATION,
    ),
    # ── T3: 确认类目 ──
    ActionStep(
        step_name="t3",
        method_name="run_t3_confirm_category",
        description="确认商品类目",
        preconditions=("t1",),
        category=StepCategory.NAVIGATION,
    ),
    # ── T4: 填写基础信息 ──
    ActionStep(
        step_name="t4",
        method_name="run_t4_fill_base_info",
        description="填写标题、型号、必选属性等基础信息",
        required_params=("title", "model", "required_attribute"),
        param_map={"brand": "brand"},
        preconditions=("t1", "t3"),
        category=StepCategory.DATA_ENTRY,
        max_retry_count=2,
        retry_lanes=(
            RetryLane("text_fallback", "run_t4_fill_base_info",
                      "剪贴板文本回退模式", {"input_mode": "text_fallback"}),
        ),
    ),
    # ── T4 额外必填字段 ──
    ActionStep(
        step_name="t4-extra",
        method_name="run_t4_fill_additional_required_fields",
        description="填写品牌、额定电压、电缆长度、重量等额外必填字段",
        preconditions=("t4",),
        category=StepCategory.DATA_ENTRY,
        max_retry_count=2,
    ),
    # ── T4 选项探测 ──
    ActionStep(
        step_name="t4-option-probe",
        method_name="_run_t4_option_probe",
        description="探测品牌、额定电压、电缆长度等下拉选项",
        preconditions=("t1", "t3"),
        category=StepCategory.PROBE,
    ),
    # ── T5 通用探测 ──
    ActionStep(
        step_name="t5-probe",
        method_name="_run_t5_probe",
        description="探测 SKU 表格控件状态",
        preconditions=("t1", "t3"),
        category=StepCategory.PROBE,
    ),
    # ── T5 单元格输入探测 ──
    ActionStep(
        step_name="t5-input-probe",
        method_name="_run_t5_input_probe",
        description="探测单个 SKU 单元格输入行为",
        required_params=("sku_cell_id", "sku_value"),
        preconditions=("t1", "t3"),
        category=StepCategory.PROBE,
    ),
    # ── T5 行输入探测 ──
    ActionStep(
        step_name="t5-row-probe",
        method_name="_run_t5_row_probe",
        description="探测 SKU 首行多字段输入行为",
        preconditions=("t1", "t3"),
        category=StepCategory.PROBE,
    ),
    # ── T5 市场价探测 ──
    ActionStep(
        step_name="t5-market-probe",
        method_name="_run_t5_market_probe",
        description="探测市场价字段候选 automation_id",
        required_params=("market_price",),
        preconditions=("t1", "t3"),
        category=StepCategory.PROBE,
    ),
    # ── T5 首行填写 ──
    ActionStep(
        step_name="t5-first-row",
        method_name="_run_t5_first_row",
        description="填写 SKU 首行（名称、短标题、市场价、采购价、京东价）",
        required_params=("sku_name", "market_price", "purchase_price", "jd_price"),
        preconditions=("t1", "t3"),
        category=StepCategory.DATA_ENTRY,
        max_retry_count=2,
    ),
    # ── T5 必填字段 ──
    ActionStep(
        step_name="t5-required-fields",
        method_name="run_t5_fill_required_fields",
        description="填写 SKU 重量、厂直库存、额定电流等必填字段",
        preconditions=("t1",),
        category=StepCategory.DATA_ENTRY,
        param_map={
            "market_price": "market_price",
            "purchase_price": "purchase_price",
            "jd_price": "jd_price",
            "current": "current",
            "weight": "weight",
            "length_mm": "length_mm",
            "width_mm": "width_mm",
            "height_mm": "height_mm",
            "factory_inventory": "factory_inventory",
        },
    ),
    # ── T5 尺寸探测 ──
    ActionStep(
        step_name="t5-dimension-probe",
        method_name="_run_t5_dimension_probe",
        description="探测重量、长宽高尺寸字段输入行为",
        required_params=("weight", "length_mm", "width_mm", "height_mm"),
        preconditions=("t1", "t3"),
        category=StepCategory.PROBE,
    ),
    # ── T5 重量探测 ──
    ActionStep(
        step_name="t5-weight-probe",
        method_name="_run_t5_weight_probe",
        description="探测重量字段多格式输入行为",
        required_params=("weight",),
        preconditions=("t1", "t3"),
        category=StepCategory.PROBE,
    ),
    # ── T6 图片区探测 ──
    ActionStep(
        step_name="t6-probe",
        method_name="run_t6_probe",
        description="探测图片区域控件状态",
        preconditions=("t1",),
        category=StepCategory.PROBE,
    ),
    # ── T6 上传对话框探测 ──
    ActionStep(
        step_name="t6-dialog-probe",
        method_name="run_t6_upload_dialog_probe",
        description="探测上传对话框行为",
        required_params=("image_path",),
        param_map={"image_path": "file_path"},
        preconditions=("t1",),
        category=StepCategory.PROBE,
    ),
    # ── T6 主图上传 ──
    ActionStep(
        step_name="t6-main-image",
        method_name="run_t6_upload_main_image",
        description="上传商品主图到京麦图片槽位",
        required_params=("image_path",),
        param_map={"image_path": "file_path"},
        preconditions=("t1",),
        category=StepCategory.UPLOAD,
        max_retry_count=2,
        retry_lanes=(
            RetryLane("hover_modal", "run_t6_upload_main_image",
                      "悬停槽位 + 点击浮层本地上传", {"upload_strategy": "hover_modal"}),
            RetryLane("text_fallback", "run_t6_upload_main_image",
                      "文件对话框地址栏输入 + 文件选中", {"upload_strategy": "text_fallback"}),
            RetryLane("direct_click", "run_t6_upload_main_image",
                      "直接点击槽位进入上传流程", {"upload_strategy": "direct_click"}),
        ),
    ),
    # ── T6 透明图上传（含图片路径回退） ──
    ActionStep(
        step_name="t6-transparent-image",
        method_name="_run_t6_transparent_image",
        description="上传透明图到 SKU 图片信息槽位",
        preconditions=("t1",),
        category=StepCategory.UPLOAD,
        max_retry_count=2,
    ),
    # ── T6 详情编辑器写入（含内容解析） ──
    ActionStep(
        step_name="t6-detail-editor",
        method_name="_run_t6_detail_editor",
        description="写入商品图文详情到京麦编辑器",
        preconditions=("t1",),
        category=StepCategory.CONTENT,
        max_retry_count=2,
        retry_lanes=(
            RetryLane("clipboard", "_run_t6_detail_editor",
                      "点击代码编辑区 + 剪贴板粘贴", {"input_mode": "clipboard"}),
            RetryLane("direct_type", "_run_t6_detail_editor",
                      "直接键盘键入内容", {"input_mode": "direct_type"}),
        ),
    ),
    # ── T7 物流售后 ──
    ActionStep(
        step_name="t7",
        method_name="run_t7_fill_logistics_fields",
        description="填写销售单位、包装类型、发货地、包装清单、质保期",
        required_params=("sale_unit", "package_type", "delivery_mark", "package_list", "warranty_period"),
        preconditions=("t1",),
        category=StepCategory.DATA_ENTRY,
    ),
    # ── T8 探测 ──
    ActionStep(
        step_name="t8-probe",
        method_name="run_t8_probe",
        description="探测保存/发布按钮和页面状态",
        preconditions=("t1",),
        category=StepCategory.PROBE,
    ),
    # ── T8 保存草稿 ──
    ActionStep(
        step_name="t8-save-draft",
        method_name="run_t8_save_draft",
        description="保存商品为草稿",
        preconditions=("t1",),
        category=StepCategory.ACTION,
        max_retry_count=2,
        retry_lanes=(
            RetryLane("direct_click", "run_t8_save_draft",
                      "直接点击保存按钮 + 轮询草稿箱", {"click_mode": "direct"}),
        ),
    ),
    # ── T8 正式发布 ──
    ActionStep(
        step_name="t8-publish-product",
        method_name="run_t8_publish_product",
        description="正式发布商品（需用户明确授权）",
        param_map={"confirm_publish": "confirm_publish"},
        preconditions=("t1",),
        category=StepCategory.ACTION,
        max_retry_count=1,
    ),
    # ── 复合步骤 "both" ──
    ActionStep(
        step_name="both",
        method_name="",
        description="复合步骤：T1 + T2 最小验证环",
        category=StepCategory.COMPOSITE,
    ),
]


class ActionRegistry:
    """Registry of ActionStep definitions, indexed by step name.

    Provides the structured step knowledge previously embedded in
    TaskRunner.VALID_STEPS + _execute_step() + _build_plan().
    """

    def __init__(self, entries: list[ActionStep] | None = None) -> None:
        self._entries: dict[str, ActionStep] = {}
        for entry in (entries or REGISTRY_ENTRIES):
            self._entries[entry.step_name] = entry

    def get(self, step_name: str) -> ActionStep:
        """Get an ActionStep by name. Raises ValueError if unknown."""
        if step_name not in self._entries:
            raise ValueError(f"unknown step: {step_name}")
        return self._entries[step_name]

    def list_all(self) -> list[ActionStep]:
        """Return all registered ActionStep entries."""
        return list(self._entries.values())

    def validate_step(self, step_name: str) -> bool:
        """Check if a step name is registered."""
        return step_name in self._entries

    @property
    def step_names(self) -> list[str]:
        """Return all registered step names."""
        return sorted(self._entries.keys())


# ── 单例 ─────────────────────────────────────────────────────────

REGISTRY = ActionRegistry(REGISTRY_ENTRIES)
