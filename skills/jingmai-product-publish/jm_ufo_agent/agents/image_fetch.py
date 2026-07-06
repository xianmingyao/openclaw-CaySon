"""图片下载 Agent。"""

from __future__ import annotations

import asyncio
import hashlib
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from jm_ufo_agent.agents.base import AgentContext, AgentResult
from jm_ufo_agent.agents.worker import WorkerAgent


@dataclass(frozen=True)
class DownloadedImage:
    """已下载图片记录。"""

    remote_url: str
    local_path: str
    sha256: str
    bytes_size: int

    def to_dict(self) -> dict[str, Any]:
        """转换为可序列化字典。"""

        # workflow 和 repository 只处理普通 JSON 结构。
        # sha256 用于后续 VLM cache 和重复下载去重。
        # bytes_size 方便判断下载结果是否异常过小。
        return {
            "remote_url": self.remote_url,
            "local_path": self.local_path,
            "sha256": self.sha256,
            "bytes_size": self.bytes_size,
        }


class UrlopenImageDownloader:
    """基于 urllib 的图片下载器。"""

    def __init__(self, output_dir: Path):
        """保存图片输出目录。"""

        # 构造函数只记录目录，不主动创建网络连接。
        # output_dir 由调用方显式传入，避免默认写到不可控位置。
        # 真实生产运行时该目录应来自 JINGMAI_ARTIFACT_DIR。
        self.output_dir = output_dir

    async def download(self, url: str) -> DownloadedImage:
        """下载单张图片。"""

        # 该方法只有被显式注入 ImageFetchAgent 时才会访问网络。
        # 文件名使用内容 hash，避免不同 URL 同名覆盖。
        # 下载失败不吞异常，让上层记录真实失败原因。
        self.output_dir.mkdir(parents=True, exist_ok=True)
        request = Request(url, headers={"User-Agent": "Mozilla/5.0 jm-ufo-agent/2.0"})
        with urlopen(request, timeout=20) as response:
            content = response.read()
        digest = hashlib.sha256(content).hexdigest()
        suffix = Path(urlparse(url).path).suffix or ".jpg"
        path = self.output_dir / f"{digest[:16]}{suffix}"
        path.write_bytes(content)
        return DownloadedImage(remote_url=url, local_path=str(path), sha256=digest, bytes_size=len(content))


class RetryingImageDownloader:
    """给图片下载器增加重试和失败证据。"""

    def __init__(self, inner: Any, max_attempts: int = 3, delay_sec: float = 0.0):
        """保存底层下载器和重试参数。"""

        # inner 负责真实下载，可以是 UrlopenImageDownloader 或测试 fake。
        # max_attempts 默认 3 次，对齐设计文档中网络中断后的重试要求。
        # attempts_by_url 保留每个 URL 的尝试记录，便于写入 halt evidence。
        self.inner = inner
        self.max_attempts = max(1, int(max_attempts))
        self.delay_sec = max(0.0, float(delay_sec))
        self.attempts_by_url: dict[str, list[dict[str, Any]]] = {}

    async def download(self, url: str) -> DownloadedImage:
        """按重试策略下载单张图片。"""

        # 每个 URL 独立记录 attempts，避免批量下载时互相覆盖。
        # 最后一次失败继续抛出原异常，让 ImageFetchAgent 记录 failed_assets。
        # 成功也记录 attempt，方便统计是否发生过重试。
        attempts: list[dict[str, Any]] = []
        self.attempts_by_url[url] = attempts
        last_error: Exception | None = None
        for attempt_index in range(1, self.max_attempts + 1):
            try:
                image = await self.inner.download(url)
                attempts.append({"attempt": attempt_index, "ok": True})
                return image
            except Exception as exc:
                last_error = exc
                attempts.append({"attempt": attempt_index, "ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
                if attempt_index < self.max_attempts and self.delay_sec:
                    await asyncio.sleep(self.delay_sec)
        assert last_error is not None
        raise last_error


class ImageFetchAgent(WorkerAgent):
    """负责下载商品图片。"""

    def __init__(
        self,
        handler: Callable[[AgentContext], Awaitable[dict[str, Any]]] | None = None,
        downloader: Any | None = None,
    ):
        """初始化图片下载 Agent。"""

        # handler 优先，方便测试直接注入资产列表。
        # downloader 只有显式传入才会写文件和访问网络。
        # 默认 dry-run 返回空 assets，保证 CI 不依赖外部图片。
        super().__init__(name="image_fetch", handler=handler)
        self.downloader = downloader

    async def fetch(self, context: AgentContext) -> AgentResult:
        """下载图片或返回 dry-run 资产结构。"""

        # 优先使用 handler，兼容现有 WorkerAgent 注入模式。
        # image_urls 来自京东抓取结果或产品原始字段。
        # 每张图的下载结果都独立记录，失败时保留 URL 和异常类型。
        if self.handler is not None:
            result = await self.run(context)
            result.data.setdefault("assets", [])
            result.data.setdefault("failed_assets", [])
            return result
        image_urls = list(context.product.get("image_urls") or context.product.get("sub_images") or [])
        main_image = context.product.get("main_image")
        if main_image:
            image_urls.insert(0, str(main_image))
        if self.downloader is None:
            return AgentResult(ok=True, message="image_fetch dry-run", data={"assets": [], "failed_assets": [], "requested_urls": image_urls})
        assets: list[dict[str, Any]] = []
        failed_assets: list[dict[str, Any]] = []
        for url in image_urls:
            try:
                assets.append((await self.downloader.download(url)).to_dict())
            except Exception as exc:
                failed_assets.append({"remote_url": url, "error": str(exc), "error_type": exc.__class__.__name__})
        if failed_assets:
            return AgentResult(
                ok=False,
                message="部分图片下载失败，已保留失败证据",
                data={"assets": assets, "failed_assets": failed_assets, "requested_urls": image_urls},
            )
        return AgentResult(ok=True, message="图片已下载", data={"assets": assets, "failed_assets": [], "requested_urls": image_urls})

