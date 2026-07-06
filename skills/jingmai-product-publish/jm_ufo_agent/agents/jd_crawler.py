"""京东数据抓取 Agent。"""

from __future__ import annotations

import json
import re
import asyncio
import inspect
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from html import unescape
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from jm_ufo_agent.agents.base import AgentContext, AgentResult
from jm_ufo_agent.agents.worker import WorkerAgent


def _fetch_html_accepts_kwargs(fetch_html: Any, kwargs: dict[str, Any]) -> bool:
    """判断底层 fetch_html 是否能接收指定关键字参数。"""

    # 生产 transport 可能支持 headers/cookie，老测试 fake 可能只支持 url。
    # 这里用签名判断，不靠捕获 TypeError，避免误吞底层真实解析或网络错误。
    # 如果签名不可读，保守认为支持 kwargs，让真实异常向上暴露。
    try:
        signature = inspect.signature(fetch_html)
    except (TypeError, ValueError):
        return bool(kwargs)
    parameters = signature.parameters
    if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in parameters.values()):
        return True
    return any(name in parameters for name in kwargs)


@dataclass(frozen=True)
class JdProductData:
    """京东商品抓取结果。"""

    product_id: str
    title: str = ""
    price: str = ""
    image_urls: list[str] = field(default_factory=list)
    source_url: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为 workflow 可落库的字典。"""

        # AgentResult.data 只接受普通 JSON 结构，不能直接塞 dataclass。
        # image_urls 保持原顺序，主图默认是第一张。
        # raw 保存解析来源，便于后续排查京东页面结构变化。
        return {
            "product_id": self.product_id,
            "title": self.title,
            "price": self.price,
            "image_urls": list(self.image_urls),
            "source_url": self.source_url,
            "raw": self.raw,
        }


class JdPageParser:
    """从京东 HTML 中提取标题、价格和图片链接。"""

    def parse(self, html: str, source_url: str = "") -> JdProductData:
        """解析京东商品页 HTML。"""

        # 京东页面结构会变，优先解析 JSON-LD，其次退回到常见 meta/title。
        # 价格可能由接口异步加载，HTML 中没有价格时返回空字符串而不是伪造。
        # 图片链接统一补全 https:，避免后续下载器拿到协议相对 URL。
        product_id = self._product_id_from_url(source_url) or self._find_first(r"wareId['\"]?\s*[:=]\s*['\"]?(\d+)", html)
        jsonld = self._jsonld_product(html)
        title = str(jsonld.get("name") or self._meta_content(html, "og:title") or self._title_text(html) or "")
        price = str(jsonld.get("price") or self._find_first(r'"p"\s*:\s*"([^"]+)"', html) or "")
        images = self._image_urls(html, jsonld)
        return JdProductData(
            product_id=product_id or "unknown",
            title=unescape(title).strip(),
            price=price.strip(),
            image_urls=images,
            source_url=source_url,
            raw={"jsonld_found": bool(jsonld), "image_count": len(images)},
        )

    def _jsonld_product(self, html: str) -> dict[str, Any]:
        """提取 JSON-LD 商品结构。"""

        # JSON-LD 是最稳定的结构化入口，优先级高于页面散落脚本。
        # 页面可能有多个 script，只取包含 Product 或 offers 的片段。
        # 解析失败直接跳过，不让单个坏 script 阻断抓取。
        pattern = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.I | re.S)
        for match in pattern.finditer(html):
            try:
                payload = json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                continue
            candidates = payload if isinstance(payload, list) else [payload]
            for item in candidates:
                if isinstance(item, dict) and (item.get("@type") == "Product" or "offers" in item):
                    offers = item.get("offers") if isinstance(item.get("offers"), dict) else {}
                    return {
                        "name": item.get("name"),
                        "price": offers.get("price"),
                        "image": item.get("image"),
                    }
        return {}

    def _image_urls(self, html: str, jsonld: dict[str, Any]) -> list[str]:
        """收集商品图片链接。"""

        # JSON-LD image 可能是字符串或数组，先加入候选。
        # 再扫描页面中常见的 img URL，去重后返回。
        # 这里只做解析，不下载图片，下载交给 ImageFetchAgent。
        urls: list[str] = []
        image = jsonld.get("image")
        if isinstance(image, str):
            urls.append(image)
        elif isinstance(image, list):
            urls.extend(str(item) for item in image)
        urls.extend(re.findall(r'(?:"|\')((?:https?:)?//img\d+\.360buyimg\.com/[^"\']+)(?:"|\')', html))
        normalized: list[str] = []
        seen: set[str] = set()
        for url in urls:
            value = "https:" + url if url.startswith("//") else url
            if value not in seen:
                normalized.append(value)
                seen.add(value)
        return normalized

    def _meta_content(self, html: str, property_name: str) -> str:
        """读取指定 meta property 的 content。"""

        # meta 是 JSON-LD 缺失时的标题兜底来源。
        # 正则限定 property，避免拿到其它页面描述。
        # 找不到时返回空字符串，调用方继续走下一个兜底。
        pattern = rf'<meta[^>]+property=["\']{re.escape(property_name)}["\'][^>]+content=["\']([^"\']+)["\']'
        return self._find_first(pattern, html)

    def _title_text(self, html: str) -> str:
        """读取 title 标签文本。"""

        # title 通常带有“京东JD.COM”等后缀，需要轻量清理。
        # 这里只清理常见分隔符，不做业务推断。
        # 返回值仍可能为空，由上层决定是否 halt。
        title = self._find_first(r"<title>(.*?)</title>", html, flags=re.I | re.S)
        return re.split(r"[-_【]", title)[0].strip()

    def _product_id_from_url(self, source_url: str) -> str:
        """从京东 URL 中提取商品 ID。"""

        # 常见 URL 形态是 https://item.jd.com/123.html。
        # 解析失败返回空字符串，不影响 HTML 内部 wareId 兜底。
        # urlparse 只做结构解析，不发起网络请求。
        path = urlparse(source_url).path
        match = re.search(r"/(\d+)\.html", path)
        return match.group(1) if match else ""

    def _find_first(self, pattern: str, text: str, flags: int = 0) -> str:
        """返回第一个正则捕获组。"""

        # 小工具统一处理正则未命中。
        # 调用方无需重复判断 match 是否为空。
        # 返回空字符串比 None 更适合直接写入 JSON 证据。
        match = re.search(pattern, text, flags)
        return match.group(1) if match else ""


class UrlopenJdTransport:
    """基于 urllib 的京东页面读取器。"""

    async def fetch_html(self, url: str) -> str:
        """读取京东商品页 HTML。"""

        # 该方法只有被显式注入 JdCrawlerAgent 时才会访问网络。
        # User-Agent 使用普通浏览器标识，减少被返回空白页的概率。
        # 网络异常不在这里吞掉，让 workflow 能记录真实失败原因。
        request = Request(url, headers={"User-Agent": "Mozilla/5.0 jm-ufo-agent/2.0"})
        with urlopen(request, timeout=15) as response:
            return response.read().decode("utf-8", errors="ignore")


class CookieJdTransport:
    """给京东抓取 transport 注入 Cookie 和 User-Agent。"""

    def __init__(self, inner: Any, cookie: str = "", user_agent: str = "Mozilla/5.0 jm-ufo-agent/2.0"):
        """保存底层 transport 和请求头配置。"""

        # inner 负责真正读取 HTML，可以是真实 UrlopenJdTransport，也可以是测试 fake。
        # cookie 为空时不注入 Cookie，避免把空凭证写进证据。
        # user_agent 作为显式配置保存，方便后续真实抓取降低空白页概率。
        self.inner = inner
        self.cookie = cookie
        self.user_agent = user_agent

    async def fetch_html(self, url: str) -> str:
        """带请求头读取京东 HTML。"""

        # 如果底层 transport 支持 headers 参数，就把 Cookie/User-Agent 传下去。
        # 如果底层只支持 fetch_html(url)，保持兼容，不强迫所有 fake 修改签名。
        # 这样测试和生产可以共用同一层包装器。
        headers = {"User-Agent": self.user_agent}
        if self.cookie:
            headers["Cookie"] = self.cookie
        if _fetch_html_accepts_kwargs(self.inner.fetch_html, {"headers": headers}):
            return await self.inner.fetch_html(url, headers=headers)
        return await self.inner.fetch_html(url)


class RetryingJdTransport:
    """给京东抓取增加重试和失败证据。"""

    def __init__(self, inner: Any, max_attempts: int = 3, delay_sec: float = 0.0):
        """保存底层 transport 和重试策略。"""

        # max_attempts 默认 3 次，对齐网络中断时的小步重试需求。
        # delay_sec 测试里可设为 0，生产可按需要设置为 1-2 秒。
        # attempts 保留最近一次调用的失败证据，供 batch report 或 halt evidence 使用。
        self.inner = inner
        self.max_attempts = max(1, int(max_attempts))
        self.delay_sec = max(0.0, float(delay_sec))
        self.attempts: list[dict[str, Any]] = []

    async def fetch_html(self, url: str, **kwargs: Any) -> str:
        """按重试策略读取京东 HTML。"""

        # 每次调用都重置 attempts，避免不同 URL 的失败证据混在一起。
        # 最后一次失败会继续抛出原异常，让上层把该 row 记为失败。
        # 成功时保留成功 attempt，便于统计真实重试次数。
        self.attempts = []
        last_error: Exception | None = None
        for attempt_index in range(1, self.max_attempts + 1):
            try:
                html = await self._fetch(url, **kwargs)
                self.attempts.append({"attempt": attempt_index, "ok": True})
                return html
            except Exception as exc:
                last_error = exc
                self.attempts.append({"attempt": attempt_index, "ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
                if attempt_index < self.max_attempts and self.delay_sec:
                    await asyncio.sleep(self.delay_sec)
        assert last_error is not None
        raise last_error

    async def _fetch(self, url: str, **kwargs: Any) -> str:
        """兼容不同 transport 签名执行一次读取。"""

        # 部分 wrapper 支持 headers/kwargs，旧 fake 只接受 url。
        # TypeError 只作为签名不兼容兜底，不吞掉网络类异常。
        if kwargs and _fetch_html_accepts_kwargs(self.inner.fetch_html, kwargs):
            return await self.inner.fetch_html(url, **kwargs)
        return await self.inner.fetch_html(url)


class RateLimitedJdTransport:
    """给京东抓取增加最小请求间隔。"""

    def __init__(self, inner: Any, min_interval_sec: float = 0.5):
        """保存底层 transport 和限速参数。"""

        # 京东反爬风险需要限速；默认 0.5 秒约等于最多 2 req/s。
        # lock 保证同一进程内并发请求也会串行通过限速器。
        # 测试可把 min_interval_sec 设为 0，验证逻辑但不等待。
        self.inner = inner
        self.min_interval_sec = max(0.0, float(min_interval_sec))
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def fetch_html(self, url: str, **kwargs: Any) -> str:
        """限速后读取京东 HTML。"""

        # 使用事件循环时间，避免系统时间调整影响限速。
        # 等待只发生在真实调用该 transport 时，构造对象不会访问网络。
        # 读取动作委托给 inner，保持职责单一。
        async with self._lock:
            loop = asyncio.get_running_loop()
            now = loop.time()
            wait_sec = self.min_interval_sec - (now - self._last_call)
            if wait_sec > 0:
                await asyncio.sleep(wait_sec)
            html = await self._fetch(url, **kwargs)
            self._last_call = loop.time()
            return html

    async def _fetch(self, url: str, **kwargs: Any) -> str:
        """兼容不同 transport 签名执行一次读取。"""

        # 和 RetryingJdTransport 保持相同兼容逻辑，方便任意组合包装顺序。
        # 如果 inner 不支持 kwargs，就退回旧签名。
        # 不捕获网络异常，交给重试层或上层处理。
        if kwargs and _fetch_html_accepts_kwargs(self.inner.fetch_html, kwargs):
            return await self.inner.fetch_html(url, **kwargs)
        return await self.inner.fetch_html(url)


class JdCrawlerAgent(WorkerAgent):
    """负责抓取京东商品标题、价格和图片链接。"""

    def __init__(
        self,
        handler: Callable[[AgentContext], Awaitable[dict[str, Any]]] | None = None,
        transport: Any | None = None,
        parser: JdPageParser | None = None,
    ):
        """初始化京东抓取 Agent。"""

        # handler 仍然优先，方便测试或后续浏览器抓取直接注入完整结果。
        # transport 只有显式传入时才会访问网络，默认 dry-run 不碰京东。
        # parser 是纯函数式解析器，可用固定 HTML 单元测试覆盖。
        super().__init__(name="jd_crawler", handler=handler)
        self.transport = transport
        self.parser = parser or JdPageParser()

    async def crawl(self, context: AgentContext) -> AgentResult:
        """抓取或解析京东商品数据。"""

        # 有 handler 时沿用 WorkerAgent 注入逻辑，保持现有测试兼容。
        # 有 jd_html 时直接解析本地 HTML，便于无网络验证 F02。
        # 有 transport 和 jd_url 时才进行真实读取，否则返回 dry-run 占位。
        if self.handler is not None:
            result = await self.run(context)
            return result
        jd_url = str(context.product.get("jd_url") or context.product.get("source_url") or "")
        html = str(context.product.get("jd_html") or "")
        if not html and self.transport is not None and jd_url:
            html = await self.transport.fetch_html(jd_url)
        if html:
            data = self.parser.parse(html, jd_url)
            return AgentResult(ok=True, message="京东商品数据已解析", data=data.to_dict())
        product_id = str(context.product.get("product_id", "unknown"))
        return AgentResult(
            ok=True,
            message="jd_crawler dry-run",
            data={"product_id": product_id, "title": context.product.get("title", ""), "price": "", "image_urls": [], "source_url": jd_url},
        )
