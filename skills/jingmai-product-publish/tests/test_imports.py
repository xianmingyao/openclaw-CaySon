"""
京麦商品发布自动化 - 基础导入测试
验证所有模块可以正确加载
"""
import sys
from pathlib import Path

# 确保项目根目录在 path 中
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_settings():
    """测试配置模块"""
    from settings import Settings, get_settings
    s = Settings()
    assert s.WINDOW_WIDTH == 1280
    assert s.MILVUS_HOST == "8.137.122.11"
    assert s.VLLM_BASE_URL == "http://localhost:8001"
    singleton = get_settings()
    assert singleton is not None


def test_models():
    """测试 ORM 模型"""
    from models import Base, Product, PublishTask, TaskStep
    assert Product is not None
    assert PublishTask is not None
    assert TaskStep is not None


def test_infrastructure():
    """测试基础设施模块"""
    from infrastructure import JingmaiLogger, CircuitBreaker
    assert JingmaiLogger is not None
    cb = CircuitBreaker(base_delay=60)
    assert cb.can_execute()


def test_memory_base():
    """测试记忆基类"""
    from memory.base import MemoryItem, MemoryType, MemoryStore
    item = MemoryItem(content="test", importance=0.5)
    assert item.id
    assert item.type == MemoryType.WORKING


def test_memory_working():
    """测试工作记忆"""
    from memory.working import WorkingMemory
    from memory.base import MemoryItem
    wm = WorkingMemory()
    item = MemoryItem(content="测试记忆", importance=0.7)
    item_id = wm.create(item)
    assert item_id

    retrieved = wm.retrieve(item_id)
    assert retrieved is not None
    assert retrieved.content == "测试记忆"

    results = wm.search("测试")
    assert len(results) > 0

    wm.delete(item_id)
    assert wm.retrieve(item_id) is None


def test_action_registry():
    """测试动作注册表"""
    from actions.registry import ActionRegistry

    # 验证内置动作已注册
    actions = ActionRegistry.list_actions()
    assert "find_window" in actions
    assert "fill_text" in actions
    assert "navigate_to" in actions
    assert "publish_product" in actions

    # 验证摘要
    summary = ActionRegistry.summary()
    assert len(summary) > 0


def test_locator_keywords():
    """测试窗口定位关键词"""
    from infrastructure.locator import WINDOW_KEYWORDS, WINDOW_EXCLUDE_KEYWORDS

    assert "jd_" in WINDOW_KEYWORDS
    assert "京麦" in WINDOW_KEYWORDS
    # "jingmai" 不应在关键词中（避免匹配 IDE）
    assert "jingmai" not in WINDOW_KEYWORDS

    assert "code" in WINDOW_EXCLUDE_KEYWORDS
    assert "vscode" in WINDOW_EXCLUDE_KEYWORDS


def test_agent_factory_aliases():
    """测试 Agent 工厂别名匹配"""
    from agents.factory import AgentFactory

    assert AgentFactory._resolve_agent_type("planner") == "planner"
    assert AgentFactory._resolve_agent_type("plan") == "planner"
    assert AgentFactory._resolve_agent_type("规划") == "planner"
    assert AgentFactory._resolve_agent_type("executor") == "executor"
    assert AgentFactory._resolve_agent_type("执行") == "executor"
    assert AgentFactory._resolve_agent_type("thinker") == "thinker"
    assert AgentFactory._resolve_agent_type("思考") == "thinker"
    assert AgentFactory._resolve_agent_type("unknown") == ""


def test_memory_manager():
    """测试三层记忆管理器"""
    from memory.manager import MemoryManager
    from memory.base import MemoryType

    mgr = MemoryManager()

    # 工作记忆写入/读取
    wid = mgr.remember_working("测试工作记忆", importance=0.5)
    item = mgr.get(wid, MemoryType.WORKING)
    assert item is not None
    assert item.content == "测试工作记忆"

    # 短期记忆写入/读取
    sid = mgr.remember_short_term("测试短期记忆", importance=0.6)
    item = mgr.get(sid, MemoryType.SHORT_TERM)
    assert item is not None
    assert item.content == "测试短期记忆"

    # 跨层搜索
    results = mgr.recall("测试", top_k=5, layers=[MemoryType.WORKING, MemoryType.SHORT_TERM])
    assert len(results) >= 2

    # 清理
    mgr.forget(wid, MemoryType.WORKING)
    mgr.forget(sid, MemoryType.SHORT_TERM)


def test_milvus_connection():
    """测试 Milvus 连接（不依赖 embedding）"""
    from memory.long_term import LongTermMemory
    ltm = LongTermMemory()
    connected = ltm._connect()
    # 连接可能因网络失败，只验证代码路径不报错
    assert isinstance(connected, bool)


def test_scraper():
    """测试商品采集器"""
    from scraper import JDScraper

    scraper = JDScraper()
    # 测试 URL 提取
    assert scraper._extract_product_id("https://item.jd.com/12345678.html") == "12345678"
    assert scraper._extract_product_id("https://item.jd.com/87654321") == "87654321"
    assert scraper._extract_product_id("https://example.com") == ""


def test_planner_template_params():
    """测试 Planner 模板参数是否对齐 Action 签名"""
    # 这个测试验证模板计划中的参数名与 Action 函数签名匹配
    # 不实际执行，只检查参数名
    from actions.navigation import select_category
    from actions.window import navigate_to
    from actions.form import fill_text, fill_product_info
    from actions.verification import verify_result
    import inspect

    # select_category 的参数应该包含 search_text
    sig = inspect.signature(select_category)
    assert "search_text" in sig.parameters

    # navigate_to 的参数应该包含 page
    sig = inspect.signature(navigate_to)
    assert "page" in sig.parameters

    # fill_text 的参数应该包含 text
    sig = inspect.signature(fill_text)
    assert "text" in sig.parameters

    # fill_product_info 的参数应该包含 product
    sig = inspect.signature(fill_product_info)
    assert "product" in sig.parameters

    # verify_result 的参数应该包含 check_errors
    sig = inspect.signature(verify_result)
    assert "check_errors" in sig.parameters


def test_publish_pipeline_params():
    """端到端验证 publish 流程参数链：Planner 生成计划 → 参数名匹配 Action 签名"""
    from agents.planner import PlannerAgent
    from actions import ActionRegistry
    import inspect

    agent = PlannerAgent()
    plan = agent._template_plan({
        "title": "测试商品",
        "price": "99.9",
        "category": "手机",
        "product_id": "12345",
    })

    assert len(plan) > 0, "模板计划不能为空"

    # 验证每一步的 action 都已注册
    registered = set(ActionRegistry.list_actions())
    for step in plan:
        action_name = step["action"]
        assert action_name in registered, f"动作未注册: {action_name}"

    # 验证每一步的 params 都与 Action 签名兼容
    for step in plan:
        action_name = step["action"]
        params = step.get("params", {})
        action_info = ActionRegistry._actions.get(action_name)
        if action_info:
            fn = action_info["func"]
            sig = inspect.signature(fn)
            # 跳过 locator 和 log（由 Executor 注入）
            skip_params = {"locator", "log"}
            for key in params:
                assert key in sig.parameters or key in skip_params, \
                    f"参数不匹配: {action_name}.{key} 不在签名 {list(sig.parameters.keys())} 中"

    # 验证关键步骤存在
    action_names = [s["action"] for s in plan]
    assert "find_window" in action_names
    assert "navigate_to" in action_names
    assert "verify_result" in action_names
    assert "publish_product" in action_names


def test_planner_nested_product():
    """测试 Planner 支持嵌套 product 子对象结构"""
    from agents.planner import PlannerAgent
    import json

    # 嵌套结构（与 config/product_template.json 一致）
    nested_data = {
        "product": {
            "title": "嵌套测试商品",
            "price": 199.9,
            "category": "手机通讯",
            "sku": "NESTED001",
        },
        "images": [],
        "publish": {"auto_submit": True},
    }

    # 加载 product_template.json 验证真实模板也能工作
    template_path = Path(__file__).parent.parent / "config" / "product_template.json"
    if template_path.exists():
        template_data = json.loads(template_path.read_text(encoding="utf-8"))
        nested_data = template_data

    agent = PlannerAgent()
    plan = agent._template_plan(nested_data.get("product", nested_data))

    assert len(plan) > 0, "嵌套结构模板计划不能为空"

    # 验证标题被正确传递
    fill_steps = [s for s in plan if s["action"] == "fill_text"]
    assert any("嵌套测试" in s.get("params", {}).get("text", "") or
               "商品标题" in s.get("params", {}).get("text", "")
               for s in fill_steps), "标题应传递到 fill_text 步骤"

    # 验证类目被正确传递
    cat_steps = [s for s in plan if s["action"] == "select_category"]
    assert len(cat_steps) > 0, "应生成类目选择步骤"


def test_db_returns_dicts():
    """测试 DB 查询返回字典而非 ORM 对象"""
    from db import DatabaseManager, _to_dict
    from models import Product

    # 使用 SQLite 内存数据库测试
    db = DatabaseManager(sqlite_url="sqlite:///:memory:")
    db.create_tables()

    # save_product 返回 ORM 对象（用于链式操作）
    p = Product(product_id="test-001", title="测试商品", status="draft")
    saved = db.save_product(p)
    assert saved.product_id == "test-001"

    # get_product 返回字典
    result = db.get_product("test-001")
    assert isinstance(result, dict)
    assert result["product_id"] == "test-001"
    assert result["title"] == "测试商品"

    # list_products 返回字典列表
    items = db.list_products()
    assert len(items) == 1
    assert isinstance(items[0], dict)

    # get_task 对不存在的 task 返回 None
    assert db.get_task("nonexistent") is None


if __name__ == "__main__":
    # 运行所有测试
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for test_fn in tests:
        try:
            test_fn()
            print(f"  PASS: {test_fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {test_fn.__name__}: {e}")
            failed += 1

    print(f"\n结果: {passed} 通过, {failed} 失败")
    sys.exit(1 if failed else 0)
