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
    assert any(item[1] == workflow.TITLE_AUTOMATION_ID for item in adapter.filled)
    assert any(item[1] == workflow.MODEL_AUTOMATION_ID for item in adapter.filled)
    assert any(item[1] == workflow.REQUIRED_ATTR_AUTOMATION_ID for item in adapter.filled)
    assert any(item[1] == workflow.BRAND_AUTOMATION_ID for item in adapter.selected)


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
    assert any(item[1] == "销售单位" for item in adapter.label_selected)
    assert any(item[1] == "商品包装" for item in adapter.label_selected)
    assert any(item[1] == "包装清单" for item in adapter.label_filled)
