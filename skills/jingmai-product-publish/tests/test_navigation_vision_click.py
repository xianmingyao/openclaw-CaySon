import json
import sys
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_vision_click_text_center_rejects_unsafe_corner_point(monkeypatch, tmp_path):
    import actions.navigation as navigation_module

    screenshot = tmp_path / "vision.png"
    Image.new("RGB", (400, 200), color="white").save(screenshot)

    class FakeLLM:
        def invoke_multimodal(self, prompt, image_path):
            return json.dumps(
                {
                    "status": "ok",
                    "target_text": "商品包装",
                    "center_x": 0,
                    "center_y": 0,
                    "bbox": [0, 0, 24, 24],
                    "reason": "",
                }
            )

    class FakeLocator(SimpleNamespace):
        def __init__(self):
            super().__init__(window_rect=(0, 0, 2560, 1392), clicks=[])

        def llm_to_screen(self, x, y, image_path=None):
            return int(x), int(y)

        def click(self, x, y, delay=0.0):
            self.clicks.append((x, y, delay))
            return True

    monkeypatch.setattr(navigation_module, "LLMManager", FakeLLM)
    locator = FakeLocator()

    result = navigation_module.vision_click_text_center(
        target_text="商品包装",
        screenshot_path=str(screenshot),
        locator=locator,
    )

    assert result["success"] is False
    assert result["message"] == "mapped click point is unsafe"
    assert locator.clicks == []


def test_vision_click_text_center_rejects_drifting_samples(monkeypatch, tmp_path):
    import actions.navigation as navigation_module

    screenshot = tmp_path / "vision.png"
    Image.new("RGB", (1000, 600), color="white").save(screenshot)

    responses = iter(
        [
            json.dumps(
                {
                    "status": "ok",
                    "target_text": "商品标题",
                    "center_x": 120,
                    "center_y": 140,
                    "bbox": [80, 110, 160, 170],
                    "reason": "",
                }
            ),
            json.dumps(
                {
                    "status": "ok",
                    "target_text": "商品标题",
                    "center_x": 420,
                    "center_y": 360,
                    "bbox": [390, 330, 450, 390],
                    "reason": "",
                }
            ),
        ]
    )

    class FakeLLM:
        def invoke_multimodal(self, prompt, image_path):
            return next(responses)

    class FakeLocator(SimpleNamespace):
        def __init__(self):
            super().__init__(window_rect=(0, 0, 2560, 1392), clicks=[])

        def llm_to_screen(self, x, y, image_path=None):
            return int(x), int(y)

        def click(self, x, y, delay=0.0):
            self.clicks.append((x, y, delay))
            return True

    monkeypatch.setattr(navigation_module, "LLMManager", FakeLLM)
    locator = FakeLocator()

    result = navigation_module.vision_click_text_center(
        target_text="商品标题",
        screenshot_path=str(screenshot),
        locator=locator,
    )

    assert result["success"] is False
    assert result["message"] == "vision_target_drift"
    assert locator.clicks == []
