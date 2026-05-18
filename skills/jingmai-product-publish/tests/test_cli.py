from __future__ import annotations

from unittest.mock import MagicMock

from sqlalchemy.exc import SQLAlchemyError

from jingmai_publish import cli


def test_build_parser_contains_new_commands_and_steps():
    parser = cli.build_parser()

    config_args = parser.parse_args(["check-config", "--verbose", "--log-file", "logs/cli.log"])
    assert config_args.command == "check-config"
    assert config_args.verbose is True
    assert config_args.log_file == "logs/cli.log"

    import_args = parser.parse_args(["run-import", "--excel", "demo.xlsx"])
    assert import_args.command == "run-import"
    assert import_args.mode == "draft"

    path_args = parser.parse_args(["run-local-path-task", "--path-file", "message.txt"])
    assert path_args.command == "run-local-path-task"
    assert path_args.source_channel == "local_path_message"

    feishu_args = parser.parse_args(["run-feishu-path-task", "--payload-file", "event.json"])
    assert feishu_args.command == "run-feishu-path-task"
    assert feishu_args.mode == "draft"

    cleanup_args = parser.parse_args(["cleanup-runtime-logs"])
    assert cleanup_args.command == "cleanup-runtime-logs"

    evidence_args = parser.parse_args(["check-evidence", "--root", "."])
    assert evidence_args.command == "check-evidence"
    assert evidence_args.root == "."

    draft_args = parser.parse_args(
        [
            "run-draft-e2e",
            "--excel",
            "demo.xlsx",
            "--main-image-path",
            "main.png",
            "--transparent-image-path",
            "transparent.png",
            "--required-attr",
            "五孔",
            "--current",
            "10A",
            "--factory-inventory",
            "10",
        ]
    )
    assert draft_args.command == "run-draft-e2e"
    assert draft_args.excel == "demo.xlsx"
    assert draft_args.main_image_path == "main.png"
    assert draft_args.transparent_image_path == "transparent.png"
    assert draft_args.required_attr == "五孔"
    assert draft_args.current == "10A"
    assert draft_args.factory_inventory == "10"

    desktop_args = parser.parse_args(
        [
            "run-desktop-check",
            "--step",
            "t6-transparent-image",
            "--image-path",
            "main.png",
            "--transparent-image-path",
            "transparent.png",
            "--detail-content",
            "<p>demo</p>",
            "--debug",
        ]
    )
    assert desktop_args.command == "run-desktop-check"
    assert desktop_args.step == "t6-transparent-image"
    assert desktop_args.image_path == "main.png"
    assert desktop_args.transparent_image_path == "transparent.png"
    assert desktop_args.detail_content == "<p>demo</p>"
    assert desktop_args.debug is True

    publish_args = parser.parse_args(["run-desktop-check", "--step", "t8-publish-product", "--confirm-publish"])
    assert publish_args.step == "t8-publish-product"
    assert publish_args.confirm_publish is True


def test_parse_click_aliases():
    mapping = cli._parse_click_aliases(["发布商品=发布,发商品", "确认=下一步"])
    assert mapping["发布商品"] == ["发布", "发商品"]
    assert mapping["确认"] == ["下一步"]


def test_handle_init_db(monkeypatch):
    fake_settings = MagicMock()
    fake_engine = MagicMock()
    called = {}

    monkeypatch.setattr(cli, "load_settings", lambda root: fake_settings)
    monkeypatch.setattr(cli, "create_engine_from_settings", lambda settings: fake_engine)
    monkeypatch.setattr(cli, "init_database", lambda engine: called.setdefault("engine", engine))

    assert cli.handle_init_db(".") == 0
    assert called["engine"] is fake_engine


def test_handle_check_config(monkeypatch, capsys):
    fake_settings = MagicMock()
    fake_settings.app_name = "demo"
    fake_settings.app_version = "v1"
    fake_settings.log_dir = "logs"
    fake_settings.memory_dir = "logs/memory"
    fake_settings.screenshot_dir = "resources/screenshots"

    monkeypatch.setattr(cli, "load_settings", lambda root: fake_settings)
    monkeypatch.setattr(cli, "validate_settings", lambda settings: [])

    assert cli.handle_check_config(".") == 0
    output = capsys.readouterr().out
    assert '"success": true' in output


def test_handle_run_import(monkeypatch):
    fake_settings = MagicMock()
    fake_engine = MagicMock()
    fake_session = MagicMock()
    fake_pipeline = MagicMock()
    fake_pipeline.run_from_local_excel_path.return_value = {"job_id": "job-123", "session_id": "sess-1"}

    class DummySessionFactory:
        def __call__(self):
            return self

        def __enter__(self):
            return fake_session

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(cli, "load_settings", lambda root: fake_settings)
    monkeypatch.setattr(cli, "create_engine_from_settings", lambda settings: fake_engine)
    monkeypatch.setattr(cli, "create_session_factory", lambda engine: DummySessionFactory())
    monkeypatch.setattr(cli, "ImportPipelineService", lambda session: fake_pipeline)

    assert cli.handle_run_import("demo.xlsx", "draft", "store-a", ".") == 0
    fake_pipeline.run_from_local_excel_path.assert_called_once()


def test_handle_run_local_path_task(monkeypatch):
    fake_settings = MagicMock()
    fake_engine = MagicMock()
    fake_session = MagicMock()
    fake_service = MagicMock()
    fake_service.run_from_local_message.return_value = {"job_id": "job-456", "session_id": "sess-2"}

    class DummySessionFactory:
        def __call__(self):
            return self

        def __enter__(self):
            return fake_session

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(cli, "load_settings", lambda root: fake_settings)
    monkeypatch.setattr(cli, "create_engine_from_settings", lambda settings: fake_engine)
    monkeypatch.setattr(cli, "create_session_factory", lambda engine: DummySessionFactory())
    monkeypatch.setattr(cli, "LocalPathChannelService", lambda session: fake_service)

    assert cli.handle_run_local_path_task("msg.txt", "publish", "store-b", "openclaw", ".") == 0
    fake_service.run_from_local_message.assert_called_once_with(
        "msg.txt",
        mode="publish",
        store_id="store-b",
        source_channel="openclaw",
    )


def test_handle_run_feishu_path_task(monkeypatch):
    fake_settings = MagicMock()
    fake_engine = MagicMock()
    fake_session = MagicMock()
    fake_service = MagicMock()
    fake_service.run_from_feishu_payload.return_value = {"job_id": "job-789", "session_id": "sess-3"}

    class DummySessionFactory:
        def __call__(self):
            return self

        def __enter__(self):
            return fake_session

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(cli, "load_settings", lambda root: fake_settings)
    monkeypatch.setattr(cli, "create_engine_from_settings", lambda settings: fake_engine)
    monkeypatch.setattr(cli, "create_session_factory", lambda engine: DummySessionFactory())
    monkeypatch.setattr(cli, "FeishuPathChannelService", lambda session: fake_service)

    assert cli.handle_run_feishu_path_task("event.json", "draft", "store-c", ".") == 0
    fake_service.run_from_feishu_payload.assert_called_once_with("event.json", mode="draft", store_id="store-c")


def test_handle_cleanup_runtime_logs(monkeypatch):
    fake_settings = MagicMock()
    fake_settings.screenshot_dir = "logs/screenshots"
    fake_engine = MagicMock()
    fake_session = MagicMock()
    fake_service = MagicMock()
    fake_service.cleanup.return_value = {"deleted_log_count": 2}

    class DummySessionFactory:
        def __call__(self):
            return self

        def __enter__(self):
            return fake_session

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(cli, "load_settings", lambda root: fake_settings)
    monkeypatch.setattr(cli, "create_engine_from_settings", lambda settings: fake_engine)
    monkeypatch.setattr(cli, "create_session_factory", lambda engine: DummySessionFactory())
    monkeypatch.setattr(cli, "RuntimeRetentionService", lambda session, screenshot_dir: fake_service)

    assert cli.handle_cleanup_runtime_logs(".") == 0
    fake_service.cleanup.assert_called_once()


def test_handle_check_evidence(monkeypatch, capsys):
    fake_service = MagicMock()
    fake_service.collect.return_value = {"success": False, "artifact_count": 1, "missing_count": 1}
    monkeypatch.setattr(cli, "ScreenshotEvidenceService", lambda root: fake_service)

    assert cli.handle_check_evidence(".") == 1
    output = capsys.readouterr().out
    assert '"artifact_count": 1' in output
    fake_service.collect.assert_called_once()


def test_handle_run_draft_e2e(monkeypatch):
    fake_settings = MagicMock()
    fake_settings.screenshot_dir = "logs/screenshots"
    fake_engine = MagicMock()
    fake_session = MagicMock()
    fake_orchestrator = MagicMock()
    fake_orchestrator.run.return_value = {"success": True, "mode": "draft"}
    captured = {}

    class DummySessionFactory:
        def __call__(self):
            return self

        def __enter__(self):
            return fake_session

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_orchestrator_factory(session, screenshot_dir, tuning):
        captured["session"] = session
        captured["screenshot_dir"] = screenshot_dir
        captured["tuning"] = tuning
        return fake_orchestrator

    monkeypatch.setattr(cli, "load_settings", lambda root: fake_settings)
    monkeypatch.setattr(cli, "create_engine_from_settings", lambda settings: fake_engine)
    monkeypatch.setattr(cli, "create_session_factory", lambda engine: DummySessionFactory())
    monkeypatch.setattr(cli, "DraftE2EOrchestrator", fake_orchestrator_factory)

    exit_code = cli.handle_run_draft_e2e(
        excel="demo.xlsx",
        item_index=0,
        store_id="store-a",
        required_attr="五孔",
        current="10A",
        factory_inventory="10",
        main_image_path="main.png",
        transparent_image_path="transparent.png",
        detail_content="<p>详情</p>",
        detail_content_file=None,
        rated_voltage="220V",
        cable_length="1.8m",
        sale_unit="件",
        package_type="普通商品",
        delivery_mark="普通品",
        package_list="插座*1",
        warranty_period="365",
        debug=True,
        window_keywords=["jd_"],
        preferred_classes=["Button"],
        click_aliases={"发布商品": ["发布"]},
        root=".",
    )

    assert exit_code == 0
    assert captured["session"] is fake_session
    assert captured["screenshot_dir"] == "logs/screenshots"
    assert captured["tuning"].window_keywords == ["jd_"]
    options = fake_orchestrator.run.call_args.args[0]
    assert options.excel_path == "demo.xlsx"
    assert options.main_image_path == "main.png"
    assert options.transparent_image_path == "transparent.png"
    assert options.debug is True


def test_handle_run_draft_e2e_reports_database_error(monkeypatch, capsys):
    fake_settings = MagicMock()
    fake_settings.screenshot_dir = "logs/screenshots"
    fake_engine = MagicMock()
    fake_session = MagicMock()
    fake_orchestrator = MagicMock()
    fake_orchestrator.run.side_effect = SQLAlchemyError("missing table")

    class DummySessionFactory:
        def __call__(self):
            return self

        def __enter__(self):
            return fake_session

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(cli, "load_settings", lambda root: fake_settings)
    monkeypatch.setattr(cli, "create_engine_from_settings", lambda settings: fake_engine)
    monkeypatch.setattr(cli, "create_session_factory", lambda engine: DummySessionFactory())
    monkeypatch.setattr(cli, "DraftE2EOrchestrator", lambda *args, **kwargs: fake_orchestrator)

    exit_code = cli.handle_run_draft_e2e(
        excel="demo.xlsx",
        item_index=0,
        store_id=None,
        required_attr=None,
        current=None,
        factory_inventory=None,
        main_image_path="main.png",
        transparent_image_path="transparent.png",
        detail_content=None,
        detail_content_file=None,
        rated_voltage=None,
        cable_length=None,
        sale_unit=None,
        package_type="普通商品",
        delivery_mark="普通品",
        package_list=None,
        warranty_period="365",
        debug=False,
        window_keywords=[],
        preferred_classes=[],
        click_aliases={},
        root=".",
    )

    assert exit_code == 1
    output = capsys.readouterr().out
    assert '"code": "database_error"' in output
    assert "init-db" in output


def test_handle_run_desktop_check(monkeypatch):
    fake_settings = MagicMock()
    fake_settings.screenshot_dir = "logs/screenshots"
    fake_service = MagicMock()
    fake_service.run.return_value = {"ok": True}
    captured = {}

    def fake_verification_service(screenshot_dir, tuning):
        captured["screenshot_dir"] = screenshot_dir
        captured["tuning"] = tuning
        return fake_service

    monkeypatch.setattr(cli, "load_settings", lambda root: fake_settings)
    monkeypatch.setattr(cli, "DesktopVerificationService", fake_verification_service)

    assert (
            cli.handle_run_desktop_check(
                "t6-detail-editor",
                ".",
                debug=True,
                window_keywords=["京麦"],
                preferred_classes=["Button"],
                click_aliases={"发布商品": ["发布"]},
                detail_content="<p>详情</p>",
            )
            == 0
    )
    fake_service.run.assert_called_once_with(step="t6-detail-editor", debug=True, detail_content="<p>详情</p>")
    assert captured["screenshot_dir"] == "logs/screenshots"
    assert captured["tuning"].window_keywords == ["京麦"]


def test_cli_module_exposes_main_entrypoint():
    assert cli.main is not None
