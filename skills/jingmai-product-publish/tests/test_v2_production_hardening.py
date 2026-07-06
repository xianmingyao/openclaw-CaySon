import json
import sys
from pathlib import Path

import pytest

from jm_ufo_agent.agents.base import AgentContext
from jm_ufo_agent.agents.image_fetch import DownloadedImage, ImageFetchAgent, RetryingImageDownloader
from jm_ufo_agent.agents.jd_crawler import CookieJdTransport, RateLimitedJdTransport, RetryingJdTransport
from jm_ufo_agent.backends.ufo_adapter import JingmaiWindowFacts, Win32ApiAdapter
from jm_ufo_agent.backends.web_surface import OcrBlock, Rect, ScreenshotOcrResult, TesseractOcrProvider
from jm_ufo_agent.cli import command as cli_command
from jm_ufo_agent.cli.interactive import stream_dashboard_from_jsonl
from jm_ufo_agent.core.settings import MySQLSettings
from jm_ufo_agent.core.settings import ReviewScorerSettings
from jm_ufo_agent.io.excel import ExcelProductParser
from jm_ufo_agent.runtime.excel_mysql import MySQLImportPreflightReport, MySQLWriteNotConfirmedError, import_excel_to_mysql_with_readback, preflight_mysql_import_schema
from jm_ufo_agent.runtime.halt_evidence import HaltEvidenceCollector, collect_and_halt
from jm_ufo_agent.runtime.mysql_schema import MySQLSchemaApplyNotConfirmedError, apply_mysql_schema, split_sql_statements
from jm_ufo_agent.runtime.review import ReviewPreflightReport, preflight_minimax_review_scorer
from jm_ufo_agent.workflow.state import GraphState


class HeaderAwareJdTransport:
    def __init__(self):
        self.headers = None

    async def fetch_html(self, url, headers=None):
        self.headers = headers
        return "<html>ok</html>"


class FlakyJdTransport:
    def __init__(self):
        self.calls = 0

    async def fetch_html(self, url, **kwargs):
        self.calls += 1
        if self.calls == 1:
            raise TimeoutError("jd timeout")
        return "<html>ok</html>"


class FlakyImageDownloader:
    def __init__(self):
        self.calls = 0

    async def download(self, url):
        self.calls += 1
        if self.calls == 1:
            raise TimeoutError("image timeout")
        return DownloadedImage(remote_url=url, local_path="tmp/a.jpg", sha256="abc", bytes_size=3)


class AlwaysFailImageDownloader:
    async def download(self, url):
        raise RuntimeError(f"cannot download {url}")


class FakeReviewTransport:
    def __init__(self, payload=None, error=None):
        self.payload = payload or {"data": [{"id": "MiniMax-M3", "type": "model"}]}
        self.error = error

    async def get_json(self, url, headers):
        if self.error is not None:
            raise self.error
        return self.payload

    async def post_json(self, url, headers, payload):
        return {}


class FakeAcquire:
    def __init__(self, connection):
        self.connection = connection

    async def __aenter__(self):
        return self.connection

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakePool:
    def __init__(self, connection):
        self.connection = connection

    def acquire(self):
        return FakeAcquire(self.connection)


class FakeMySQLClient:
    def __init__(self, connection):
        self.connection = connection

    async def connect(self):
        return FakePool(self.connection)


class FakeMySQLConnection:
    def __init__(self):
        self.executed = []
        self.committed = False
        self.rows_by_index = {}

    async def execute(self, sql, params):
        self.executed.append((sql, params))
        product_id, row_index, title, raw_json, enriched_json = params
        self.rows_by_index[row_index] = (product_id, row_index, title, raw_json, enriched_json)

    async def fetchone(self, sql, params):
        return self.rows_by_index.get(params[0])

    async def commit(self):
        self.committed = True


class FakePreflightConnection:
    async def fetchone(self, sql, params):
        if sql.startswith("SHOW TABLES"):
            return ("jm_products",)
        if sql.startswith("SELECT COUNT"):
            return (3,)
        return None


class FakeSchemaConnection:
    def __init__(self):
        self.executed = []
        self.committed = False

    async def execute(self, sql, params):
        self.executed.append((sql, params))

    async def commit(self):
        self.committed = True


class FakeWindowBackend:
    async def screenshot(self, output_path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"fake")
        return output_path

    async def inspect_jingmai(self):
        return JingmaiWindowFacts(
            found=True,
            main_title="京麦 - 新增商品",
            main_class_name="Qt51511QWindowIcon",
            qt_child_count=3,
            webview_pane_count=1,
        )


class FakeOcrService:
    async def capture_and_ocr(self):
        return ScreenshotOcrResult(
            screenshot_path=Path("screen.png"),
            page_signature="sig-1",
            blocks=[OcrBlock("保存草稿失败", Rect(1, 2, 3, 4), 0.98)],
        )


async def test_jd_transport_cookie_retry_and_rate_limit_are_explicit_boundaries():
    # Cookie 包装层只负责传递请求头，不主动访问网络。
    # 重试层记录每次尝试，方便批量抓取统计成功率和失败原因。
    # 限速层在 min_interval=0 时不等待，测试只验证组合边界。
    header_transport = HeaderAwareJdTransport()
    html = await CookieJdTransport(header_transport, cookie="pt_key=1").fetch_html("https://item.jd.com/1.html")
    flaky = FlakyJdTransport()
    retrying = RetryingJdTransport(flaky, max_attempts=2, delay_sec=0)
    limited = RateLimitedJdTransport(retrying, min_interval_sec=0)
    retried_html = await limited.fetch_html("https://item.jd.com/2.html")

    assert html == "<html>ok</html>"
    assert header_transport.headers["Cookie"] == "pt_key=1"
    assert header_transport.headers["User-Agent"].startswith("Mozilla")
    assert retried_html == "<html>ok</html>"
    assert flaky.calls == 2
    assert retrying.attempts == [
        {"attempt": 1, "ok": False, "error": "jd timeout", "error_type": "TimeoutError"},
        {"attempt": 2, "ok": True},
    ]


async def test_image_downloader_retries_and_agent_preserves_failed_asset_evidence():
    # 图片下载重试只包住单张图片，避免一张失败污染其它图片证据。
    # Agent 汇总 failed_assets，后续可以写入 halt evidence 或资产审计表。
    # 这里不进行真实下载，确保 CI 和 dry-run 默认安全。
    retrying = RetryingImageDownloader(FlakyImageDownloader(), max_attempts=2, delay_sec=0)
    image = await retrying.download("https://img.example/a.jpg")
    failing_agent = ImageFetchAgent(downloader=AlwaysFailImageDownloader())
    result = await failing_agent.fetch(AgentContext(task_id="t1", product={"image_urls": ["https://img.example/b.jpg"]}))

    assert image.remote_url == "https://img.example/a.jpg"
    assert retrying.attempts_by_url["https://img.example/a.jpg"][0]["error_type"] == "TimeoutError"
    assert result.ok is False
    assert result.data["assets"] == []
    assert result.data["failed_assets"][0]["remote_url"] == "https://img.example/b.jpg"
    assert result.data["failed_assets"][0]["error_type"] == "RuntimeError"


async def test_minimax_preflight_report_handles_available_missing_and_error():
    # preflight helper 只返回结构化报告，不泄露 Authorization header。
    # 模型不存在时是可读阻断，不把它伪装成网络异常。
    # transport 异常会被归类为 unavailable，供 dashboard/readiness 展示。
    settings = ReviewScorerSettings(api_key="token", max_call_attempts=1, backoff_base_sec=0, backoff_max_sec=0)
    available = await preflight_minimax_review_scorer(settings, transport=FakeReviewTransport())
    missing = await preflight_minimax_review_scorer(settings, transport=FakeReviewTransport(payload={"data": [{"id": "other"}]}))
    failed = await preflight_minimax_review_scorer(settings, transport=FakeReviewTransport(error=TimeoutError("down")))

    assert available.to_dict()["ok"] is True
    assert available.message == "model_available: MiniMax-M3"
    assert missing.ok is False
    assert missing.message == "model_not_found: MiniMax-M3"
    assert failed.ok is False
    assert failed.error_type == "TimeoutError"
    assert "token" not in json.dumps(failed.to_dict(), ensure_ascii=False)


def test_cli_minimax_preflight_uses_explicit_command_and_prints_report(monkeypatch, capsys, tmp_path):
    async def fake_preflight(settings):
        return ReviewPreflightReport(
            ok=True,
            provider=settings.provider,
            model=settings.model,
            base_url=settings.base_url,
            message="model_available: MiniMax-M3",
        )

    # CLI 分支通过 monkeypatch 注入 fake，验证命令存在但不触发真实 MiniMax。
    # env-file 指向临时空文件路径，load_settings 会使用安全默认值。
    # 输出保持 JSON，便于生产脚本和人工预检统一消费。
    monkeypatch.setattr(cli_command, "preflight_minimax_review_scorer", fake_preflight)

    code = cli_command.main(["minimax-preflight", "--env-file", str(tmp_path / ".env")])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["ok"] is True
    assert payload["model"] == "MiniMax-M3"


async def test_import_excel_to_mysql_requires_confirmation_and_commits(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    xlsx = tmp_path / "products.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["商品ID", "商品标题"])
    sheet.append(["sku-1", "标题1"])
    workbook.save(xlsx)
    connection = FakeMySQLConnection()

    # 未确认时必须阻断真实 MySQL 写入，防止把解析验收误当成生产导入。
    # 确认后通过 ProductRepository 写入，并在连接支持 commit 时提交事务。
    # fake client 保证测试不连接真实数据库。
    with pytest.raises(MySQLWriteNotConfirmedError):
        await import_excel_to_mysql_with_readback(xlsx, MySQLSettings(), mysql_client=FakeMySQLClient(connection))

    report = await import_excel_to_mysql_with_readback(
        xlsx,
        MySQLSettings(),
        confirmed_write=True,
        mysql_client=FakeMySQLClient(connection),
    )

    assert report.summary.parsed_count == 1
    assert report.summary.written_count == 1
    assert report.readback_count == 1
    assert report.missing_readback_rows == []
    assert report.to_dict()["readback_passed"] is True
    assert connection.committed is True
    assert "INSERT INTO jm_products" in connection.executed[0][0]


def test_excel_parser_detects_hunan_template_header_after_instruction_rows(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    xlsx = tmp_path / "hunan.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["", "产品上架明细表", ""])
    sheet.append(["", "每一项必填！", ""])
    sheet.append(["上架序号", "商品名称（对应京东开票内容）", "品牌"])
    sheet.append([1, "公牛插座", "公牛"])
    workbook.save(xlsx)

    # 真实湖南模板前两行不是表头，解析器必须自动跳过说明行。
    # “上架序号”应作为稳定 product_id，“商品名称（对应京东开票内容）”应映射为 title。
    # row_index 保留 Excel 原始行号，便于后续 row 恢复和人工核对。
    records = ExcelProductParser().parse(xlsx)

    assert len(records) == 1
    assert records[0].product_id == "1"
    assert records[0].title == "公牛插座"
    assert records[0].row_index == 4


async def test_mysql_preflight_checks_products_table_without_writing():
    report = await preflight_mysql_import_schema(
        MySQLSettings(database="jingmai_agent"),
        mysql_client=FakeMySQLClient(FakePreflightConnection()),
    )

    # preflight 只读 schema 和 count，不执行 INSERT。
    # ok=True 表示 jm_products 表存在且可查询。
    # products_count 帮助真实导入前判断是否已有历史数据。
    assert report.ok is True
    assert report.products_table_exists is True
    assert report.products_count == 3
    assert report.database == "jingmai_agent"


def test_cli_mysql_preflight_uses_explicit_command(monkeypatch, capsys, tmp_path):
    async def fake_preflight(settings):
        return MySQLImportPreflightReport(
            ok=True,
            database=settings.database,
            products_table_exists=True,
            products_count=0,
            message="jm_products 可用",
        )

    # CLI 通过 monkeypatch 注入 fake，验证命令存在但不连接真实 MySQL。
    # env-file 指向不存在文件时 load_settings 会使用安全默认值。
    # 输出不包含数据库密码。
    monkeypatch.setattr(cli_command, "preflight_mysql_import_schema", fake_preflight)

    code = cli_command.main(["mysql-preflight", "--env-file", str(tmp_path / ".env")])
    payload = json.loads(capsys.readouterr().out)

    assert code == 0
    assert payload["ok"] is True
    assert payload["products_table_exists"] is True
    assert "password" not in json.dumps(payload, ensure_ascii=False).lower()


async def test_apply_mysql_schema_requires_confirmation_and_executes_statements(tmp_path):
    schema = tmp_path / "schema.sql"
    schema.write_text(
        """
        -- comment
        CREATE TABLE jm_products (id INT);
        CREATE TABLE jm_tasks (id INT);
        """,
        encoding="utf-8",
    )
    connection = FakeSchemaConnection()

    # schema 应用会修改数据库结构，未确认时必须阻断。
    # 确认后顺序执行 SQL，并在支持 commit 时提交。
    # fake connection 确保测试不连接真实 MySQL。
    with pytest.raises(MySQLSchemaApplyNotConfirmedError):
        await apply_mysql_schema(MySQLSettings(), schema, mysql_client=FakeMySQLClient(connection))

    report = await apply_mysql_schema(
        MySQLSettings(),
        schema,
        confirmed_apply=True,
        mysql_client=FakeMySQLClient(connection),
    )

    assert split_sql_statements(schema.read_text(encoding="utf-8")) == [
        "CREATE TABLE jm_products (id INT)",
        "CREATE TABLE jm_tasks (id INT)",
    ]
    assert report.ok is True
    assert report.statement_count == 2
    assert report.applied_count == 2
    assert connection.committed is True


def test_cli_new_production_validation_commands_are_exposed(capsys):
    with pytest.raises(SystemExit) as schema_exit:
        cli_command.main(["mysql-apply-schema", "--help"])
    schema_help = capsys.readouterr().out
    with pytest.raises(SystemExit) as capture_exit:
        cli_command.main(["capture-halt-evidence", "--help"])
    capture_help = capsys.readouterr().out

    # 只验证命令暴露，不触发真实 MySQL 或京麦窗口采集。
    # argparse help 会通过 SystemExit 正常退出，因此 main 在这里返回 0。
    assert schema_exit.value.code == 0
    assert "--confirm-apply-schema" in schema_help
    assert capture_exit.value.code == 0
    assert "--use-tesseract" in capture_help


async def test_stream_dashboard_from_jsonl_tails_new_frames(tmp_path):
    states_jsonl = tmp_path / "states.jsonl"
    states_jsonl.write_text(
        "\n".join(
            [
                json.dumps({"task_id": "t1", "row_index": 5, "current_node": "BOOTSTRAP", "status": "running"}),
                json.dumps({"task_id": "t1", "row_index": 5, "current_node": "SAVE_DRAFT", "status": "saved_draft"}),
            ]
        ),
        encoding="utf-8",
    )
    outputs: list[str] = []

    # max_frames 让实时 tail 在测试中确定退出。
    # printer 注入后不用依赖真实终端，也不会启动 Rich Live 的阻塞 UI。
    # 输出仍包含 dashboard 关键字段，说明状态流被消费。
    count = await stream_dashboard_from_jsonl(states_jsonl, poll_interval_sec=0, max_frames=2, printer=outputs.append)

    assert count == 2
    assert outputs[0] == "frame: 1"
    assert any("SAVE_DRAFT" in item for item in outputs)


async def test_halt_evidence_collector_captures_window_ocr_and_log(tmp_path):
    collector = HaltEvidenceCollector(
        artifact_dir=tmp_path,
        window_backend=FakeWindowBackend(),
        ocr_service=FakeOcrService(),
    )

    # halt 证据采集失败不能影响原始 halt reason；成功时应包含截图、窗口、OCR 和日志。
    # 这里用 fake backend 写一个本地截图文件，验证证据路径真实存在。
    # 日志 JSON 内也要包含 log_path，便于后续落库和人工排查一致。
    evidence = await collector.collect("task-1", 82, "SAVE_DRAFT", "toast missing", {"extra": 1})
    log_payload = json.loads(Path(evidence["log_path"]).read_text(encoding="utf-8"))

    assert evidence["node"] == "SAVE_DRAFT"
    assert evidence["reason"] == "toast missing"
    assert Path(evidence["screenshot_path"]).exists()
    assert evidence["window_summary"]["main_class_name"] == "Qt51511QWindowIcon"
    assert evidence["ocr_summary"]["page_signature"] == "sig-1"
    assert log_payload["log_path"] == evidence["log_path"]


async def test_collect_and_halt_writes_normalized_evidence_without_nesting(tmp_path):
    collector = HaltEvidenceCollector(
        artifact_dir=tmp_path,
        window_backend=FakeWindowBackend(),
        ocr_service=FakeOcrService(),
    )
    state = GraphState(task_id="task-2", row_index=7, product={})
    state.current_node = "VERIFY_FIELD"

    # collect_and_halt 应直接把标准 evidence 写入 GraphState。
    # GraphState 不能再次 normalize，否则 log_path/screenshot_path 会被塞进 details。
    # blockers 仍保留原始 reason，供路由判断。
    evidence = await collect_and_halt(state, "ocr mismatch", collector, {"field": "title"})
    stored = state.evidence["halt_evidence"][0]

    assert state.status.value == "halted"
    assert state.blockers == ["ocr mismatch"]
    assert stored["log_path"] == evidence["log_path"]
    assert stored["screenshot_path"] == evidence["screenshot_path"]
    assert stored["details"]["field"] == "title"
    assert "log_path" not in stored["details"]


def test_win32_screenshot_window_reports_missing_rect_without_side_effect(monkeypatch, tmp_path):
    adapter = Win32ApiAdapter()
    monkeypatch.setattr(sys, "platform", "linux")

    # 非 Windows 环境不会尝试真实截图，也不会创建输出文件。
    # 真实 Windows 下如果矩形不可用，同样会抛出明确错误，供 halt evidence 记录。
    # 这里验证失败是显式的，而不是返回一个假成功路径。
    with pytest.raises(RuntimeError):
        adapter.screenshot_window(1, tmp_path / "screen.png")
    assert not (tmp_path / "screen.png").exists()


def test_tesseract_ocr_provider_converts_data_to_blocks(tmp_path):
    provider = TesseractOcrProvider(screenshot_backend=FakeWindowBackend(), output_path=tmp_path / "screen.png")
    data = {
        "text": ["", "商品标题", "ABC123", "noise"],
        "conf": ["-1", "96", "82.5", "-1"],
        "left": ["0", "10", "20", "30"],
        "top": ["0", "11", "21", "31"],
        "width": ["0", "120", "80", "10"],
        "height": ["0", "24", "20", "8"],
    }

    # 该测试只验证 Tesseract 输出解析，不依赖本机安装 pytesseract。
    # 空文本和负置信度会被过滤，避免把 OCR 噪声送入坐标定位。
    # 置信度会标准化到 0-1，便于后续阈值判断。
    blocks = provider.blocks_from_tesseract_data(data)

    assert [block.text for block in blocks] == ["商品标题", "ABC123"]
    assert blocks[0].rect == Rect(10, 11, 120, 24)
    assert blocks[0].confidence == 0.96
    assert blocks[1].confidence == 0.825
