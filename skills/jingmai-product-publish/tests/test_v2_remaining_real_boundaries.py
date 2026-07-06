from jm_ufo_agent.agents.base import AgentContext, AgentResult
from jm_ufo_agent.agents.image_fetch import ImageFetchAgent
from jm_ufo_agent.agents.image_transform import ImageTransformAgent
from jm_ufo_agent.agents.jd_crawler import JdCrawlerAgent
from jm_ufo_agent.backends.ufo_adapter import Win32DesktopBackend
from jm_ufo_agent.backends.web_surface.clipboard_fill import SystemClipboardFillService
from jm_ufo_agent.backends.web_surface.coordinate_plan import CoordinatePlan, Rect
from jm_ufo_agent.commands.base import Command
from jm_ufo_agent.runtime.assets import AssetPipelineService
from jm_ufo_agent.runtime.e2e import ProductionE2EOrchestrator
from jm_ufo_agent.runtime.jd_batch import JdBatchCrawlService


class FakeAssetRepo:
    def __init__(self):
        self.records = []

    async def upsert(self, record):
        self.records.append(record)


class FakeVlmRepo:
    def __init__(self):
        self.records = []

    async def add(self, record):
        self.records.append(record)


class FakeDesktopApi:
    def __init__(self):
        self.calls = []

    def click(self, x, y):
        self.calls.append(("click", x, y))

    def paste_text(self, value):
        self.calls.append(("paste_text", value))

    def choose_file(self, path):
        self.calls.append(("choose_file", path))


class FakeClipboardApi:
    def __init__(self):
        self.calls = []

    def click(self, x, y):
        self.calls.append(("click", x, y))

    def set_clipboard_text(self, value):
        self.calls.append(("clipboard", value))

    def hotkey(self, *keys):
        self.calls.append(("hotkey", keys))


async def test_jd_batch_crawl_service_computes_success_rate():
    async def handler(context):
        if context.product["product_id"] == "bad":
            return {"product_id": "bad", "title": "", "price": "", "image_urls": []}
        return {"product_id": context.product["product_id"], "title": "T", "price": "1.00", "image_urls": ["https://img/a.jpg"]}

    service = JdBatchCrawlService(JdCrawlerAgent(handler=handler))
    report = await service.crawl_products("task-1", [{"product_id": "ok"}, {"product_id": "bad"}], required_success_rate=0.95)

    assert report.total == 2
    assert report.success_count == 1
    assert report.success_rate == 0.5
    assert any(item["message"].startswith("success_rate_below") for item in report.failed_rows)


async def test_asset_pipeline_records_downloads_and_vlm_audit():
    async def fetch_handler(context):
        return {"assets": [{"remote_url": "https://img/a.jpg", "local_path": "a.jpg", "sha256": "abc"}]}

    async def transform_handler(context):
        return {"transformed_assets": [{"remote_url": "https://img/a.jpg", "transformed_path": "a-out.jpg"}], "model": "fake-vlm"}

    asset_repo = FakeAssetRepo()
    vlm_repo = FakeVlmRepo()
    service = AssetPipelineService(ImageFetchAgent(handler=fetch_handler), ImageTransformAgent(handler=transform_handler), asset_repo=asset_repo, vlm_repo=vlm_repo)

    report = await service.process_product(AgentContext(task_id="task-1", row_index=82, product={"product_id": "sku-1"}))

    assert report.failed is False
    assert report.downloaded_count == 1
    assert report.transformed_count == 1
    assert len(asset_repo.records) == 2
    assert vlm_repo.records[0].status == "success"


async def test_win32_desktop_backend_blocks_write_until_enabled():
    api = FakeDesktopApi()
    blocked = Win32DesktopBackend(api=api, allow_write=False)
    allowed = Win32DesktopBackend(api=api, allow_write=True)
    command = Command(action="fill", target="title", value="商品", metadata={"point": [10, 20]})

    blocked_result = await blocked.execute(command)
    allowed_result = await allowed.execute(command)

    assert blocked_result.ok is False
    assert blocked_result.data["blocked"] is True
    assert allowed_result.ok is True
    assert ("click", 10, 20) in api.calls
    assert ("paste_text", "商品") in api.calls


async def test_system_clipboard_fill_service_requires_allow_write():
    api = FakeClipboardApi()
    plan = CoordinatePlan(field_name="title", rect=Rect(10, 20, 80, 24), confidence=0.9, source="test")

    blocked = await SystemClipboardFillService(api, allow_write=False).apply_fill(plan, "商品")
    allowed = await SystemClipboardFillService(api, allow_write=True).apply_fill(plan, "商品")

    assert blocked.ok is False
    assert allowed.ok is True
    assert ("clipboard", "商品") in api.calls
    assert ("hotkey", ("ctrl", "v")) in api.calls


async def test_production_e2e_orchestrator_stops_when_not_ready_and_runs_when_ready():
    order = []
    stages = [
        "parse_excel",
        "crawl_jd",
        "download_images",
        "transform_images",
        "check_jingmai_login",
        "open_add_product_page",
        "fill_webview_form",
        "save_draft",
        "verify_draft_readback",
    ]

    async def handler(payload):
        order.append(payload["stage_name"])
        return {"ok": True}

    not_ready = await ProductionE2EOrchestrator({"parse_excel": True}, {}).run({})
    handlers = {stage: (lambda payload, stage=stage: handler({**payload, "stage_name": stage})) for stage in stages}
    ready = await ProductionE2EOrchestrator({stage: True for stage in stages}, handlers).run({})

    assert not_ready.readiness.ready is False
    assert ready.readiness.ready is True
    assert [stage.stage for stage in ready.stages] == stages
    assert order == stages
