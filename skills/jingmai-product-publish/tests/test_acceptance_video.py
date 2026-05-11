import json
import sys
from pathlib import Path

from click.testing import CliRunner
from PIL import Image

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.executor import ExecutorAgent
from cli import cli
from db import DatabaseManager
from infrastructure.video_observer import StepVideoObserver


class _FakeLocator:
    def __init__(self):
        self.counter = 0

    def take_screenshot(self, save_path: str, for_vision: bool = True):
        self.counter += 1
        image = Image.new("RGB", (80, 40), color=(self.counter * 20, 50, 90))
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
        return str(path.resolve())


def test_step_video_observer_generates_contact_sheet(tmp_path: Path):
    from settings import Settings

    settings = Settings(
        VIDEO_OBSERVER_ENABLED=True,
        VIDEO_OBSERVER_FRAME_COUNT=3,
        VIDEO_OBSERVER_INTERVAL_MS=0,
        VIDEO_OBSERVER_DIR=str(tmp_path / "observer"),
    )
    locator = _FakeLocator()
    observer = StepVideoObserver(locator, settings)

    result = observer.capture_burst("task-1", "step-01-find_window", "precheck")

    assert result["enabled"] is True
    assert result["frame_count"] == 3
    assert len(result["frames"]) == 3
    assert Path(result["contact_sheet"]).exists()
    assert result["primary_path"] == result["contact_sheet"]


def test_executor_capture_visual_artifacts_records_video_outputs(tmp_path: Path):
    from settings import Settings

    settings = Settings(
        VIDEO_OBSERVER_ENABLED=True,
        VIDEO_OBSERVER_FRAME_COUNT=2,
        VIDEO_OBSERVER_INTERVAL_MS=0,
        SCREENSHOT_DIR=str(tmp_path / "screens"),
        VIDEO_OBSERVER_DIR=str(tmp_path / "observer"),
    )
    agent = ExecutorAgent(settings=settings)
    agent._task_id = "task-video"
    agent._locator = _FakeLocator()

    artifacts = agent._capture_visual_artifacts(1, "find_window", "precheck")

    assert Path(artifacts["screenshot"]).exists()
    assert Path(artifacts["contact_sheet"]).exists()
    assert len(artifacts["frames"]) == 2
    assert len(artifacts["analysis_paths"]) >= 2
    assert agent._step_artifacts[1]["precheck_video_frame_count"] == 2
    assert len(agent._step_artifacts[1]["precheck_video_frames"]) == 2


def test_acceptance_run_persists_summary_and_db(monkeypatch, tmp_path: Path):
    runner = CliRunner()
    batch_path = tmp_path / "products.json"
    batch_path.write_text(
        json.dumps([{"title": "商品A", "price": 10, "product_id": "JD-100"}], ensure_ascii=False),
        encoding="utf-8",
    )
    acceptance_dir = tmp_path / "acceptance-out"
    test_db = DatabaseManager(sqlite_url="sqlite:///:memory:")
    test_db.create_tables()

    class FakePlanner:
        def run(self, **kwargs):
            return {
                "success": True,
                "task_id": "task-acceptance-1",
                "product_data": kwargs["product_data"],
                "screen_context": {},
                "plan": [{"action": "find_window", "params": {}, "phase": "window_ready"}],
                "total_steps": 1,
                "workflow_policy": kwargs.get("workflow_policy", "doc_strict"),
            }

    class FakeExecutor:
        def run(self, **kwargs):
            return {"success": True, "risk_stats": {}, "vision_fallback_stats": {}, "recovery_error": ""}

    class FakeFactory:
        def create_planner(self):
            return FakePlanner()

        def create_executor(self):
            return FakeExecutor()

    monkeypatch.setattr("agents.factory.AgentFactory", lambda *args, **kwargs: FakeFactory())
    monkeypatch.setattr("cli._build_db", lambda settings: test_db)
    monkeypatch.setattr("cli._persist_product_snapshot", lambda *args, **kwargs: {"product_id": "JD-100"})

    result = runner.invoke(
        cli,
        ["acceptance-run", "--file", str(batch_path), "--plan-out", str(acceptance_dir), "--no-video-observer"],
    )

    assert result.exit_code == 0
    runs = test_db.list_acceptance_runs(limit=5)
    assert len(runs) == 1
    run = runs[0]
    assert run["status"] == "success"
    assert run["success_count"] == 1
    assert run["fail_count"] == 0
    assert Path(run["summary_file"]).exists()
    summary = json.loads(Path(run["summary_file"]).read_text(encoding="utf-8"))
    assert summary["summary"]["success_count"] == 1
    assert summary["video_observer_enabled"] is False
