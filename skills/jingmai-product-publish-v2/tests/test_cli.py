from __future__ import annotations

from unittest.mock import MagicMock

from jingmai_publish import cli


def test_build_parser_contains_new_commands_and_steps():
    parser = cli.build_parser()

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

    publish_args = parser.parse_args(["run-desktop-check", "--step", "t8-publish-product"])
    assert publish_args.step == "t8-publish-product"


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
