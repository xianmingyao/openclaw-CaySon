import json
from pathlib import Path

import pytest

from jm_ufo_agent.agents.base import AgentContext
from jm_ufo_agent.agents.image_fetch import ImageFetchAgent
from jm_ufo_agent.agents.jd_crawler import JdCrawlerAgent, JdPageParser
from jm_ufo_agent.agents.jm_host import JmHostAgent
from jm_ufo_agent.agents.jm_webview import JmWebViewAgent
from jm_ufo_agent.backends.ufo_adapter import JingmaiWindowFacts, StaticWindowInspectorBackend, WindowInfo
from jm_ufo_agent.backends.web_surface import OcrBlock, Rect, ScreenshotOcrResult, ScreenshotOcrService, WebViewFormLoop
from jm_ufo_agent.cli.command import main
from jm_ufo_agent.cli.progress import DashboardState, ProgressDashboard
from jm_ufo_agent.runtime.production import ProductionRunConfig, assert_production_allowed, describe_production_pipeline
from jm_ufo_agent.storage.business_cache import MilvusReflectionStore, RedisBusinessCache


class FakeOcrProvider:
    def __init__(self, snapshots):
        self.snapshots = list(snapshots)

    async def capture_and_ocr(self):
        return self.snapshots.pop(0)


class FakeRedis:
    def __init__(self):
        self.values = {}

    async def set(self, key, value, ex=None):
        self.values[key] = (value, ex)
        return True

    async def get(self, key):
        value = self.values.get(key)
        return None if value is None else value[0]


class FakeMilvusCollection:
    def __init__(self):
        self.rows = []

    async def insert(self, rows):
        self.rows.extend(rows)


def test_jd_page_parser_extracts_title_price_and_images_from_html():
    html = """
    <html><head>
    <script type="application/ld+json">
      {"@type":"Product","name":"Test JD Product","image":["//img10.360buyimg.com/a.jpg"],"offers":{"price":"12.34"}}
    </script>
    </head><body>"//img11.360buyimg.com/b.jpg"</body></html>
    """

    data = JdPageParser().parse(html, "https://item.jd.com/123456.html")

    assert data.product_id == "123456"
    assert data.title == "Test JD Product"
    assert data.price == "12.34"
    assert data.image_urls == ["https://img10.360buyimg.com/a.jpg", "https://img11.360buyimg.com/b.jpg"]


async def test_jd_crawler_agent_parses_injected_html_without_network():
    html = '<script type="application/ld+json">{"@type":"Product","name":"Injected","offers":{"price":"9.99"}}</script>'
    agent = JdCrawlerAgent()

    result = await agent.crawl(AgentContext(task_id="t1", product={"jd_url": "https://item.jd.com/1.html", "jd_html": html}))

    assert result.ok is True
    assert result.data["title"] == "Injected"
    assert result.data["price"] == "9.99"


async def test_image_fetch_agent_default_is_dryrun_and_no_download():
    agent = ImageFetchAgent()
    context = AgentContext(task_id="t1", product={"main_image": "https://example.test/main.jpg", "image_urls": ["https://example.test/a.jpg"]})

    result = await agent.fetch(context)

    assert result.ok is True
    assert result.data["assets"] == []
    assert result.data["requested_urls"] == ["https://example.test/main.jpg", "https://example.test/a.jpg"]


async def test_jingmai_host_detects_qt_window_login_and_add_page():
    facts = JingmaiWindowFacts(
        found=True,
        main_title="Jingmai Add Product",
        main_class_name="Qt51511QWindowIcon",
        qt_child_count=4,
        webview_pane_count=1,
        panes=[WindowInfo(handle=1, title="web", class_name="Chrome_RenderWidgetHostHWND", control_type="Pane")],
    )
    backend = StaticWindowInspectorBackend(facts)
    agent = JmHostAgent(window_backend=backend, expected_window_title="Add Product")

    fact_result = await agent.inspect_window_facts()
    login_result = await agent.check_login()
    open_result = await agent.open_add_product_page()

    assert fact_result.ok is True
    assert fact_result.data["main_class_name"] == "Qt51511QWindowIcon"
    assert fact_result.data["webview_pane_count"] == 1
    assert login_result.ok is True
    assert open_result.ok is True
    assert backend.focused_keywords


async def test_jingmai_host_prompts_human_login_when_window_missing():
    agent = JmHostAgent(window_backend=StaticWindowInspectorBackend())

    result = await agent.check_login()

    assert result.ok is False
    assert result.data["needs_human_login"] is True


async def test_webview_agent_observe_and_fill_loop_uses_ocr_readback():
    before = ScreenshotOcrResult(
        blocks=[OcrBlock("title", Rect(10, 20, 80, 24), 0.91)],
        page_signature="before",
    )
    after = ScreenshotOcrResult(
        screenshot_path=Path("screen.png"),
        blocks=[OcrBlock("title", Rect(10, 20, 80, 24), 0.91), OcrBlock("New Product", Rect(170, 20, 200, 24), 0.93)],
        page_signature="after",
    )
    loop = WebViewFormLoop(ocr=ScreenshotOcrService(FakeOcrProvider([before, after])))
    agent = JmWebViewAgent(form_loop=loop)

    result = await agent.fill_field_with_surface_loop("title", Rect(10, 20, 80, 24), "New Product")

    assert result.ok is True
    assert result.data["page_signature"] == "after"
    assert result.data["observed"] == "New Product"
    assert result.data["local_similarity"] >= 0.50


async def test_business_cache_roundtrips_redis_payloads_and_milvus_reflection():
    redis = FakeRedis()
    cache = RedisBusinessCache(redis, prefix="test")

    await cache.set_ocr_cache("page-1", {"text": "hello"}, ttl_sec=10)
    await cache.set_vlm_cache("asset-1", {"status": "ok"}, ttl_sec=11)
    await cache.set_locator_cache("title", "page-1", {"confidence": 0.9}, ttl_sec=12)

    assert await cache.get_ocr_cache("page-1") == {"text": "hello"}
    assert await cache.get_vlm_cache("asset-1") == {"status": "ok"}
    assert await cache.get_locator_cache("title", "page-1") == {"confidence": 0.9}

    collection = FakeMilvusCollection()
    store = MilvusReflectionStore(collection)
    await store.add_failure_reflection("t1", 82, "ocr mismatch", [0.1, 0.2], {"node": "VERIFY_FIELD"})

    assert collection.rows[0]["task_id"] == "t1"
    assert json.loads(collection.rows[0]["metadata_json"]) == {"node": "VERIFY_FIELD"}


def test_dashboard_and_production_gate_are_safe_by_default():
    dashboard = ProgressDashboard().render_text(
        DashboardState(
            task_id="t1",
            row_index=82,
            current_node="OBSERVE_PAGE",
            status="running",
            completion_score=0.5,
            verified_fields=["title"],
            blockers=[],
        )
    )

    assert "task_id: t1" in dashboard
    assert "current_node: OBSERVE_PAGE" in dashboard
    assert "crawl_jd" in describe_production_pipeline()
    assert_production_allowed(ProductionRunConfig(backend="dry-run"))
    with pytest.raises(PermissionError):
        assert_production_allowed(ProductionRunConfig(backend="ufo-observe"))
    assert_production_allowed(ProductionRunConfig(backend="ufo-observe", confirmed_real_jingmai=True, observe_only=True))
    with pytest.raises(PermissionError):
        assert_production_allowed(ProductionRunConfig(backend="ufo-observe", confirmed_real_jingmai=True, observe_only=False))


def test_cli_dashboard_and_inspect_ufo_entries(capsys, tmp_path):
    state_file = tmp_path / "state.json"
    state_file.write_text(json.dumps({"task_id": "t1", "row_index": 82, "current_node": "BOOTSTRAP", "status": "running"}), encoding="utf-8")

    dashboard_code = main(["dashboard", "--state-json", f"@{state_file}"])
    dashboard_output = capsys.readouterr().out
    inspect_code = main(["inspect-ufo", "--ufo-root", str(tmp_path)])
    inspect_output = capsys.readouterr().out

    assert dashboard_code == 0
    assert "task_id" in dashboard_output
    assert inspect_code == 0
    assert json.loads(inspect_output)["ufo_root_exists"] is True
