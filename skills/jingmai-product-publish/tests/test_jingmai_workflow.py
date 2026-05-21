from jingmai_publish.desktop.adapter import WindowInfo
from jingmai_publish.desktop.window_manager import WindowManager
from jingmai_publish.services.jingmai_workflow import JingmaiWorkflowService


class DummyAdapter:
    def __init__(self):
        self.activated = []
        self.clicked = []
        self.filled = []
        self.selected = []
        self.label_filled = []
        self.label_selected = []
        self.probed = []

    def list_windows(self):
        return [
            WindowInfo(handle="1001", title="记事本"),
            WindowInfo(handle="2002", title="京麦工作台"),
        ]

    def activate_window(self, handle: str) -> bool:
        self.activated.append(handle)
        return True

    def click_text(self, handle: str, text: str) -> bool:
        self.clicked.append((handle, text))
        return text == "发布商品"

    def capture_window(self, handle: str) -> str | None:
        return f"logs/screenshots/{handle}.png"

    def read_document_text(self, handle: str) -> str:
        values = (
                [item[2] for item in self.filled]
                + [item[2] for item in self.selected]
                + [item[2] for item in self.label_filled]
                + [item[2] for item in self.label_selected]
        )
        return "商品类目 工业品 > 中低压配电 > 插座 修改 商品信息 商品标题 " + " ".join(values)

    def fill_edit_by_automation_id(self, handle: str, automation_id: str, value: str) -> bool:
        self.filled.append((handle, automation_id, value))
        return True

    def select_combobox_by_automation_id(self, handle: str, automation_id: str, value: str) -> bool:
        self.selected.append((handle, automation_id, value))
        return True

    def fill_edit_by_label(self, handle: str, label: str, value: str) -> bool:
        self.label_filled.append((handle, label, value))
        return True

    def select_combobox_by_label(self, handle: str, label: str, value: str) -> bool:
        self.label_selected.append((handle, label, value))
        return True

    def probe_select_options_by_label(self, handle: str, label: str) -> dict[str, object]:
        self.probed.append((handle, label))
        return {"success": True, "options": []}


def test_window_manager_find_jingmai_window():
    manager = WindowManager(DummyAdapter())
    window = manager.find_jingmai_window()
    assert window is not None
    assert window.handle == "2002"


def test_window_manager_prefers_real_jingmai_signature():
    class SignatureAdapter(DummyAdapter):
        def list_windows(self):
            return [
                WindowInfo(handle="1001", title="京麦帮助", class_name="Chrome_WidgetWin_1", visible=True),
                WindowInfo(handle="3003", title="jd_465d1abd3ee76", class_name="JMMainFrameBase", visible=True),
            ]

    manager = WindowManager(SignatureAdapter())
    window = manager.find_jingmai_window()
    assert window is not None
    assert window.handle == "3003"


def test_workflow_t1_attach_window():
    workflow = JingmaiWorkflowService(WindowManager(DummyAdapter()))
    result = workflow.run_t1_attach_window()
    assert result.step_id == "T1"
    assert result.success is True
    assert result.page_state == "jingmai_home"
    assert result.window_handle == "2002"


def test_workflow_t2_enter_publish_entry():
    workflow = JingmaiWorkflowService(WindowManager(DummyAdapter()))
    result = workflow.run_t2_enter_publish_entry("2002")
    assert result.step_id == "T2"
    assert result.success is True
    assert result.page_state == "publish_entry"


def test_workflow_t3_confirm_category():
    workflow = JingmaiWorkflowService(WindowManager(DummyAdapter()))
    result = workflow.run_t3_confirm_category("2002")
    assert result.step_id == "T3"
    assert result.success is True
    assert result.page_state == "category_confirmed"
    assert "工业品" in result.message


def test_workflow_t3_accepts_manual_category_next_form():
    class ManualCategoryAdapter(DummyAdapter):
        def read_document_text(self, handle: str) -> str:
            return "商品信息 商品标题 型号 采销信息 商品属性 商品图片 市场价 京东价"

    workflow = JingmaiWorkflowService(WindowManager(ManualCategoryAdapter()))
    result = workflow.run_t3_confirm_category("2002")

    assert result.step_id == "T3"
    assert result.success is True
    assert result.page_state == "category_confirmed"
    assert "发布表单已可见" in result.message


def test_workflow_t3_enters_publish_entry_from_draft_list(monkeypatch):
    class DraftListAdapter(DummyAdapter):
        def __init__(self):
            super().__init__()
            self.document_text = "商品草稿仅支持保留30天 草稿箱 商品名称 编辑时间 操作 发布商品"
            self.region_clicks = []

        def read_document_text(self, handle: str) -> str:
            return self.document_text

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
            if text == "发布商品":
                self.document_text = "商品类目 工业品 > 中低压配电 > 插座 修改 商品信息 商品标题 保存草稿"
                return True
            return False

    monkeypatch.setattr("jingmai_publish.services.jingmai_workflow.time.sleep", lambda _: None)
    adapter = DraftListAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))

    result = workflow.run_t3_confirm_category("2002")

    assert result.success is True
    assert result.page_state == "category_confirmed"
    assert adapter.region_clicks == [("发布商品", 0.82, 1.0, 0.04, 0.18)]
    assert "已从草稿箱进入发布入口" in result.message


def test_workflow_t3_advances_category_selection_page(monkeypatch):
    class CategorySelectionAdapter(DummyAdapter):
        def __init__(self):
            super().__init__()
            self.document_text = (
                "类目选择发品 近期使用类目： 工业品 >电料辅件 >电气辅材> 电气配件 "
                "电脑、办公 >电脑组件> 组装电脑 下一步，完善其他商品信息"
            )
            self.region_clicks = []

        def read_document_text(self, handle: str) -> str:
            return self.document_text

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
            return text.startswith("工业品")

        def click_text(self, handle: str, text: str) -> bool:
            self.clicked.append((handle, text))
            if text == "下一步，完善其他商品信息":
                self.document_text = "商品类目 工业品 > 电料辅件 > 电气辅材 > 电气配件 修改 商品信息 商品标题 保存草稿"
                return True
            return False

    monkeypatch.setattr("jingmai_publish.services.jingmai_workflow.time.sleep", lambda _: None)
    adapter = CategorySelectionAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))

    result = workflow.run_t3_confirm_category("2002")

    assert result.success is True
    assert result.page_state == "category_confirmed"
    assert adapter.region_clicks[0][0].startswith("工业品")
    assert ("2002", "下一步，完善其他商品信息") in adapter.clicked
    assert "已推进类目选择页" in result.message


def test_workflow_t3_prefers_recent_category_shortcut(monkeypatch):
    class RecentCategoryAdapter(DummyAdapter):
        def __init__(self):
            super().__init__()
            self.document_text = (
                "类目选择发品 近期使用类目： 工业品 >化学品 >油漆涂料> 防火涂料 "
                "工业品 >电料辅件 >电气辅材> 电气配件 电脑、办公 >电脑组件> 组装电脑 "
                "下一步，完善其他商品信息"
            )
            self.ratio_clicks = []

        def read_document_text(self, handle: str) -> str:
            return self.document_text

        def click_window_ratio(self, handle: str, x_ratio: float, y_ratio: float) -> bool:
            self.ratio_clicks.append((round(x_ratio, 3), y_ratio))
            if y_ratio == 0.94:
                self.document_text = (
                    "商品类目 工业品 > 电料辅件 > 电气辅材 > 电气配件 修改 "
                    "商品信息 商品标题 保存草稿"
                )
            return True

    monkeypatch.setattr("jingmai_publish.services.jingmai_workflow.time.sleep", lambda _: None)
    adapter = RecentCategoryAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))

    result = workflow.run_t3_confirm_category("2002")

    assert result.success is True
    assert result.page_state == "category_confirmed"
    assert adapter.ratio_clicks[0][1] == 0.202
    assert adapter.ratio_clicks[1] == (0.5, 0.94)
    assert "电料辅件" in result.message


def test_workflow_t4_fill_base_info():
    adapter = DummyAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))
    result = workflow.run_t4_fill_base_info(
        "2002",
        title="测试商品标题",
        model="XH-001",
        required_attribute="10A",
        brand="公牛",
    )
    assert result.step_id == "T4"
    assert result.success is True
    assert result.page_state == "base_info_completed"
    assert ("2002", "商品标题", "测试商品标题") in adapter.label_filled
    assert ("2002", "型号", "XH-001") in adapter.label_filled
    assert ("2002", "类型", "10A") in adapter.label_selected
    assert ("2002", "品牌", "公牛") in adapter.label_selected


def test_workflow_t4_fill_base_info_accepts_retry_lane_input_mode():
    adapter = DummyAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))
    result = workflow.run_t4_fill_base_info(
        "2002",
        title="测试商品标题",
        model="XH-001",
        required_attribute="10A",
        brand="公牛",
        input_mode="text_fallback",
    )
    assert result.step_id == "T4"
    assert result.success is True
    assert result.page_state == "base_info_completed"


def test_brand_validation_accepts_selected_value_with_residual_placeholder():
    document_text = (
        "商品标题 * 公牛插座 标题书写规范 品牌 * 公牛 请选择品牌 "
        "短标题 一键生成 型号 * GN-605"
    )

    assert JingmaiWorkflowService._brand_value_selected("公牛", document_text) is True


def test_brand_validation_rejects_title_only_brand_with_placeholder():
    document_text = (
        "商品标题 * 公牛插座 标题书写规范 品牌 * 请选择品牌 "
        "短标题 一键生成 型号 * GN-605"
    )

    assert JingmaiWorkflowService._brand_value_selected("公牛", document_text) is False


def test_workflow_t4_rejects_unmatched_brand_option():
    class BrandOptionAdapter(DummyAdapter):
        def probe_select_options_by_label(self, handle: str, label: str) -> dict[str, object]:
            self.probed.append((handle, label))
            return {
                "success": True,
                "options": [{"text": "志倍（ZHIBEI）-长沙飞戈电子技术有限公司"}],
            }

        def select_combobox_by_label(self, handle: str, label: str, value: str) -> bool:
            if label == "品牌":
                if value == "志倍（ZHIBEI）-长沙飞戈电子技术有限公司":
                    self.label_selected.append((handle, label, value))
                    return True
                return False
            return super().select_combobox_by_label(handle, label, value)

        def select_combobox_by_automation_id(self, handle: str, automation_id: str, value: str) -> bool:
            if automation_id == JingmaiWorkflowService.BRAND_AUTOMATION_ID:
                if value == "志倍（ZHIBEI）-长沙飞戈电子技术有限公司":
                    self.selected.append((handle, automation_id, value))
                    return True
                return False
            return super().select_combobox_by_automation_id(handle, automation_id, value)

    adapter = BrandOptionAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))

    result = workflow.run_t4_fill_base_info(
        "2002",
        title="测试商品标题",
        model="XH-001",
        required_attribute="10A",
        brand="公牛",
    )

    assert result.success is False
    assert result.page_state == "publish_entry"
    assert ("2002", "品牌", "志倍（ZHIBEI）-长沙飞戈电子技术有限公司") not in adapter.label_selected
    assert "品牌值=公牛" in result.message


def test_workflow_t4_fill_additional_required_fields():
    adapter = DummyAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))
    result = workflow.run_t4_fill_additional_required_fields(
        "2002",
        brand="公牛",
        rated_voltage="220V",
        cable_length="1.8m",
        weight="125",
    )
    assert result.step_id == "T4-EXTRA"
    assert result.success is True
    assert any(item[1] == "额定电压" for item in adapter.label_selected)
    assert any(item[1] == "电缆长度" for item in adapter.label_selected)
    assert any(item[1] == "重量" for item in adapter.label_filled)


def test_workflow_t7_fill_logistics_fields():
    adapter = DummyAdapter()
    workflow = JingmaiWorkflowService(WindowManager(adapter))
    result = workflow.run_t7_fill_logistics_fields(
        "2002",
        sale_unit="个",
        package_type="盒装",
        delivery_mark="现货",
        package_list="插座*1",
        warranty_period="12个月",
    )
    assert result.step_id == "T7"
    assert result.success is True
    selected_targets = [item[1] for item in adapter.selected + adapter.label_selected]
    filled_targets = [item[1] for item in adapter.filled + adapter.label_filled]
    assert "销售单位" in selected_targets or workflow.LOGISTICS_AUTOMATION_IDS["sale_unit"] in selected_targets
    assert "商品包装" in selected_targets or workflow.LOGISTICS_AUTOMATION_IDS["package_type"] in selected_targets
    assert "包装清单" in filled_targets or workflow.LOGISTICS_AUTOMATION_IDS["package_list"] in filled_targets
