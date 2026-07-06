"""截图 OCR 服务边界。"""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jm_ufo_agent.backends.web_surface.coordinate_plan import Rect


@dataclass(frozen=True)
class OcrBlock:
    """OCR 文本块。"""

    text: str
    rect: Rect
    confidence: float


@dataclass(frozen=True)
class ScreenshotOcrResult:
    """截图 OCR 结果。"""

    screenshot_path: Path | None = None
    blocks: list[OcrBlock] = field(default_factory=list)
    page_signature: str = ""


class ScreenshotOcrService:
    """截图/OCR 服务接口。"""

    def __init__(self, provider=None):
        """初始化截图 OCR 服务。"""

        # provider 是可注入的真实截图/OCR 实现。
        # 默认 provider 为空时返回 dry-run 结果，不访问屏幕或 OCR 引擎。
        # 这种边界让测试可以注入固定 OCR blocks 验证 WebView 闭环。
        self.provider = provider

    async def capture_and_ocr(self) -> ScreenshotOcrResult:
        """执行截图 OCR。"""

        # provider 存在时调用真实/测试实现。
        # provider 不存在时返回 dry-run signature。
        # page_signature 为空时根据 OCR 文本生成稳定签名。
        if self.provider is None:
            return ScreenshotOcrResult(page_signature="dry-run")
        result = await self.provider.capture_and_ocr()
        if result.page_signature:
            return result
        signature_text = "|".join(block.text for block in result.blocks)
        signature = hashlib.sha256(signature_text.encode("utf-8")).hexdigest()[:16]
        return ScreenshotOcrResult(screenshot_path=result.screenshot_path, blocks=result.blocks, page_signature=signature)


class TesseractOcrProvider:
    """基于窗口截图和 pytesseract 的真实 OCR provider。"""

    def __init__(self, screenshot_backend: Any, output_path: Path, lang: str = "chi_sim+eng"):
        """保存截图 backend、输出路径和 OCR 语言。"""

        # screenshot_backend 只要求实现 screenshot(output_path)，可接 Win32WindowInspectorBackend。
        # output_path 由调用方显式传入，避免默认写到不可控目录。
        # lang 默认中英混合，适合京麦中文字段和英文/数字型号同时识别。
        self.screenshot_backend = screenshot_backend
        self.output_path = output_path
        self.lang = lang

    async def capture_and_ocr(self) -> ScreenshotOcrResult:
        """截图并执行真实 OCR。"""

        # 截图动作委托给 backend，provider 不直接操作窗口。
        # pytesseract 是可选依赖，只有真实 OCR 路径显式调用时才导入。
        # OCR 属于 CPU/外部进程工作，放到线程中执行，避免阻塞事件循环。
        screenshot_path = Path(await self.screenshot_backend.screenshot(self.output_path))
        return await asyncio.to_thread(self._ocr_image, screenshot_path)

    def _ocr_image(self, screenshot_path: Path) -> ScreenshotOcrResult:
        """对本地截图文件执行 OCR。"""

        # Pillow/pytesseract 缺失时抛出明确错误，让 halt evidence 记录依赖缺口。
        # image_to_data 返回结构化框，便于后续坐标定位和局部相似度验证。
        # page_signature 仍由 ScreenshotOcrService 在外层补齐，保持签名规则统一。
        try:
            from PIL import Image
            import pytesseract
        except ImportError as exc:
            raise RuntimeError("缺少 Pillow 或 pytesseract，不能执行真实 OCR") from exc
        image = Image.open(screenshot_path)
        data = pytesseract.image_to_data(image, lang=self.lang, output_type=pytesseract.Output.DICT)
        return ScreenshotOcrResult(screenshot_path=screenshot_path, blocks=self.blocks_from_tesseract_data(data))

    def blocks_from_tesseract_data(self, data: dict[str, list[Any]]) -> list[OcrBlock]:
        """把 pytesseract image_to_data 结果转换成 OcrBlock。"""

        # 跳过空文本和置信度为负的行，减少噪声。
        # 坐标和尺寸直接来自 Tesseract，后续 CoordinatePlanner 可继续使用。
        # 该方法不依赖真实 OCR，可用固定 dict 做单元测试。
        blocks: list[OcrBlock] = []
        texts = data.get("text", [])
        for index, raw_text in enumerate(texts):
            text = str(raw_text).strip()
            confidence = _safe_float(_value_at(data, "conf", index), default=-1.0)
            if not text or confidence < 0:
                continue
            blocks.append(
                OcrBlock(
                    text=text,
                    rect=Rect(
                        x=int(_safe_float(_value_at(data, "left", index), default=0)),
                        y=int(_safe_float(_value_at(data, "top", index), default=0)),
                        width=int(_safe_float(_value_at(data, "width", index), default=0)),
                        height=int(_safe_float(_value_at(data, "height", index), default=0)),
                    ),
                    confidence=confidence / 100.0 if confidence > 1 else confidence,
                )
            )
        return blocks


def _value_at(data: dict[str, list[Any]], key: str, index: int) -> Any:
    """安全读取 Tesseract dict 中的第 index 个值。"""

    # Tesseract 输出字段长度理论上一致，但异常输出或测试数据可能缺列。
    # 缺值时返回空字符串，由调用方按默认值处理。
    # 该 helper 避免每个字段都重复 try/except。
    values = data.get(key, [])
    return values[index] if index < len(values) else ""


def _safe_float(value: Any, default: float) -> float:
    """把 OCR 字段安全转成 float。"""

    # conf/left/top 等字段可能是字符串、小数或空值。
    # 转换失败时使用默认值，避免单个坏字段中断整个 OCR 结果解析。
    # 真实 OCR 依赖失败仍由 _ocr_image 抛错，不在这里吞掉。
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class LocalPaddleOcrProvider:
    """基于 PaddleOCR 的本地截图+OCR Provider。

    PaddleOCR 是可选依赖，未安装时返回 fallback 结果。
    真实环境下截图通过 pyautogui 或 win32api 获取。
    OCR 结果用于页面签名计算和字段验证。
    """

    async def capture_and_ocr(self) -> ScreenshotOcrResult:
        """截图并执行 OCR。"""

        try:
            from paddleocr import PaddleOCR  # type: ignore
        except ImportError:
            return ScreenshotOcrResult(page_signature="paddleocr-not-installed")

        ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
        screenshot_path = await self._capture_window()
        if not screenshot_path:
            return ScreenshotOcrResult(page_signature="capture-failed")

        result = await asyncio.to_thread(ocr.ocr, screenshot_path, cls=True)
        blocks: list[OcrBlock] = []
        if result and result[0]:
            for line in result[0]:
                text = str(line[1][0])
                confidence = float(line[1][1])
                # PaddleOCR 返回 [[x1,y1],[x2,y2],[x3,y3],[x4,y4]] 四角坐标
                points = line[0]
                x = int(min(p[0] for p in points))
                y = int(min(p[1] for p in points))
                x_max = int(max(p[0] for p in points))
                y_max = int(max(p[1] for p in points))
                blocks.append(
                    OcrBlock(
                        text=text,
                        rect=Rect(x=x, y=y, width=x_max - x, height=y_max - y),
                        confidence=confidence,
                    )
                )

        return ScreenshotOcrResult(screenshot_path=Path(screenshot_path), blocks=blocks)

    async def _capture_window(self) -> str:
        """截取指定窗口截图到临时文件。"""
        import tempfile
        import os

        try:
            import pyautogui  # type: ignore
        except ImportError:
            return ""

        screenshot = pyautogui.screenshot()
        tmp_dir = tempfile.mkdtemp(prefix="jm_ocr_")
        path = os.path.join(tmp_dir, "screenshot.png")
        screenshot.save(path)
        return path
