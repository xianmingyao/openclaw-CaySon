from pathlib import Path

from jm_ufo_agent.backends.web_surface.clipboard_fill import ClipboardFillService
from jm_ufo_agent.backends.web_surface.coordinate_plan import CoordinatePlanner, Rect
from jm_ufo_agent.backends.web_surface.screenshot_ocr import ScreenshotOcrService
from jm_ufo_agent.backends.web_surface.verifier import SurfaceVerifier
from jm_ufo_agent.commands import ClickCommand, FillCommand, NavigateCommand, ReadCommand, UploadCommand


def test_command_builders_convert_to_generic_command():
    fill = FillCommand("title", "测试商品").to_command()
    click = ClickCommand("draft", label="保存草稿").to_command()
    navigate = NavigateCommand("new_product").to_command()
    upload = UploadCommand("main_image", Path("a.png")).to_command()
    read = ReadCommand("title").to_command()

    assert fill.action == "fill"
    assert fill.target == "title"
    assert click.label == "保存草稿"
    assert navigate.action == "navigate"
    assert upload.value == "a.png"
    assert read.action == "read"


async def test_web_surface_coordinate_and_clipboard_dryrun():
    planner = CoordinatePlanner()
    plan = planner.plan_from_label("title", Rect(10, 20, 80, 24))
    service = ClipboardFillService()

    result = await service.apply_fill(plan, "测试商品")

    assert plan.rect.center() == (290, 32)
    assert plan.is_trusted() is True
    assert result.ok is True


async def test_screenshot_ocr_service_returns_dryrun_signature():
    result = await ScreenshotOcrService().capture_and_ocr()

    assert result.page_signature == "dry-run"
    assert result.blocks == []


def test_surface_verifier_matches_trimmed_text():
    verifier = SurfaceVerifier()

    ok = verifier.verify_text("title", "测试商品", " 测试商品 ")
    bad = verifier.verify_text("title", "测试商品", "其他")

    assert ok.ok is True
    assert bad.ok is False
