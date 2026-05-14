from unittest.mock import MagicMock

from jingmai_publish import cli


def test_build_parser_contains_expected_commands():
    parser = cli.build_parser()
    args = parser.parse_args(["run-import", "--excel", "demo.xlsx"])
    assert args.command == "run-import"
    assert args.excel == "demo.xlsx"
    assert args.mode == "draft"
    desktop_args = parser.parse_args(["run-desktop-check", "--step", "both", "--debug"])
    assert desktop_args.command == "run-desktop-check"
    assert desktop_args.debug is True
    t4_args = parser.parse_args(
        [
            "run-desktop-check",
            "--step",
            "t4",
            "--title",
            "标题",
            "--model",
            "型号",
            "--required-attr",
            "10A",
        ]
    )
    assert t4_args.step == "t4"
    assert t4_args.required_attr == "10A"
    t5_args = parser.parse_args(
        [
            "run-desktop-check",
            "--step",
            "t5-input-probe",
            "--sku-cell-id",
            "jd-id-1-311",
            "--sku-value",
            "12.50",
            "--sku-submit",
        ]
    )
    assert t5_args.step == "t5-input-probe"
    assert t5_args.sku_cell_id == "jd-id-1-311"
    assert t5_args.sku_submit is True


def test_parse_click_aliases():
    mapping = cli._parse_click_aliases(["发布商品=发布,发商品", "确认=下一步"])
    assert mapping["发布商品"] == ["发布", "发商品"]
    assert mapping["确认"] == ["下一步"]


def test_handle_init_db(monkeypatch):
    fake_settings = MagicMock()
    fake_engine = MagicMock()

    monkeypatch.setattr(cli, "load_settings", lambda root: fake_settings)
    monkeypatch.setattr(cli, "create_engine_from_settings", lambda settings: fake_engine)

    called = {}

    def fake_init_database(engine):
        called["engine"] = engine

    monkeypatch.setattr(cli, "init_database", fake_init_database)
    result = cli.handle_init_db(".")
    assert result == 0
    assert called["engine"] is fake_engine


def test_handle_run_import(monkeypatch):
    fake_settings = MagicMock()
    fake_engine = MagicMock()
    fake_session = MagicMock()
    fake_session_factory = MagicMock()
    fake_pipeline = MagicMock()
    fake_pipeline.run_from_local_excel_path.return_value = {"job_id": "job-123"}

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

    result = cli.handle_run_import("demo.xlsx", "draft", "store-a", ".")
    assert result == 0
    fake_pipeline.run_from_local_excel_path.assert_called_once()
