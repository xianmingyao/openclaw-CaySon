"""
视频帧观察器：对单步执行前后做多帧截图，并生成联系图供视觉校验使用。
"""
from __future__ import annotations

import math
import time
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image, ImageDraw


class StepVideoObserver:
    """基于 burst screenshot 的轻量视频观察器。"""

    def __init__(self, locator, settings, logger=None):
        self._locator = locator
        self._settings = settings
        self._logger = logger
        self._base_dir = Path(getattr(settings, "VIDEO_OBSERVER_DIR", ""))

    @property
    def enabled(self) -> bool:
        return bool(getattr(self._settings, "VIDEO_OBSERVER_ENABLED", False))

    def capture_burst(self, task_id: str, step_key: str, stage: str) -> Dict[str, Any]:
        if not self.enabled or self._locator is None:
            return {
                "enabled": False,
                "frame_count": 0,
                "frames": [],
                "contact_sheet": "",
                "primary_path": "",
            }

        frame_count = max(2, int(getattr(self._settings, "VIDEO_OBSERVER_FRAME_COUNT", 4) or 4))
        interval_ms = max(0, int(getattr(self._settings, "VIDEO_OBSERVER_INTERVAL_MS", 350) or 350))
        run_dir = self._base_dir / (task_id or "adhoc") / step_key
        run_dir.mkdir(parents=True, exist_ok=True)

        frames: List[str] = []
        timestamps: List[int] = []
        for index in range(frame_count):
            frame_path = run_dir / f"{stage}_frame_{index + 1}.png"
            try:
                saved_path = self._locator.take_screenshot(str(frame_path), for_vision=True)
            except Exception as exc:
                self._log(f"视频帧截图失败: {exc}")
                break
            if saved_path:
                frames.append(str(Path(saved_path).resolve()))
                timestamps.append(int(time.time() * 1000))
            if index < frame_count - 1 and interval_ms > 0:
                time.sleep(interval_ms / 1000.0)

        contact_sheet = self._build_contact_sheet(run_dir, stage, frames)
        primary_path = contact_sheet or (frames[-1] if frames else "")
        return {
            "enabled": True,
            "frame_count": len(frames),
            "frames": frames,
            "contact_sheet": contact_sheet,
            "primary_path": primary_path,
            "timestamps": timestamps,
            "interval_ms": interval_ms,
        }

    def _build_contact_sheet(self, run_dir: Path, stage: str, frames: List[str]) -> str:
        if not frames:
            return ""

        images: List[Image.Image] = []
        try:
            for frame in frames:
                images.append(Image.open(frame).convert("RGB"))
            width = max(img.width for img in images)
            height = max(img.height for img in images)
            cols = 2 if len(images) > 1 else 1
            rows = int(math.ceil(len(images) / cols))
            canvas = Image.new("RGB", (width * cols, height * rows), color=(18, 22, 29))
            draw = ImageDraw.Draw(canvas)

            for index, image in enumerate(images):
                x = (index % cols) * width
                y = (index // cols) * height
                canvas.paste(image, (x, y))
                draw.rectangle((x, y, x + 120, y + 28), fill=(0, 0, 0))
                draw.text((x + 8, y + 6), f"Frame {index + 1}", fill=(255, 255, 255))

            output_path = run_dir / f"{stage}_contact_sheet.png"
            canvas.save(output_path)
            return str(output_path.resolve())
        except Exception as exc:
            self._log(f"联系图生成失败: {exc}")
            return ""
        finally:
            for image in images:
                try:
                    image.close()
                except Exception:
                    pass

    def _log(self, message: str) -> None:
        if self._logger is not None:
            try:
                self._logger.debug(f"[VideoObserver] {message}")
            except Exception:
                pass
