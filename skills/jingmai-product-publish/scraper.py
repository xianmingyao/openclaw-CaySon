"""
JD product scraper utilities.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
from urllib.parse import urljoin


class JDScraper:
    """Scrape JD product basics plus detail assets from a product URL."""

    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    def __init__(self, timeout: int = 30, image_cache_dir: str | Path = "data/jd_detail_images"):
        self.timeout = timeout
        self.image_cache_dir = Path(image_cache_dir)

    def scrape(self, url: str) -> Dict[str, Any]:
        product_id = self._extract_product_id(url)
        if not product_id:
            return {"success": False, "error": f"unable to extract product id from url: {url}"}

        cached_html = self._load_cached_html(product_id)
        cached = self._build_product_from_html(cached_html, url, product_id, source="cache") if cached_html else None
        if cached:
            return cached

        product = self._scrape_via_playwright(url, product_id)
        if product:
            return product

        product = self._scrape_via_opencli(url, product_id)
        if product:
            return product

        product = self._scrape_via_api(product_id)
        if product:
            product.setdefault("url", f"https://item.jd.com/{product_id}.html")
            return product

        product = self._scrape_via_html(url, product_id)
        if product:
            return product

        return {
            "success": True,
            "product_id": product_id,
            "source": "url_only",
            "title": "",
            "price": "",
            "url": f"https://item.jd.com/{product_id}.html",
        }

    def _extract_product_id(self, url: str) -> str:
        patterns = [
            r"jd\.com/(\d+)\.html",
            r"jd\.com/(\d+)",
            r"sku=(\d+)",
            r"product/(\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return ""

    def _scrape_via_playwright(self, url: str, product_id: str) -> Optional[Dict[str, Any]]:
        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
            from playwright.sync_api import sync_playwright
        except Exception:
            return None

        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page(user_agent=self.USER_AGENT)
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=self.timeout * 1000)
                    page.wait_for_load_state("networkidle", timeout=min(self.timeout * 1000, 15000))
                except PlaywrightTimeoutError:
                    pass
                html = page.content()
                browser.close()
        except Exception:
            return None

        return self._build_product_from_html(html, url, product_id, source="playwright")

    def _scrape_via_api(self, product_id: str) -> Optional[Dict[str, Any]]:
        try:
            import requests

            api_url = "https://api.m.jd.com/client.action"
            params = {
                "functionId": "wareBusiness",
                "body": json.dumps({"skuId": product_id}),
            }
            headers = {"User-Agent": self.USER_AGENT}
            resp = requests.get(api_url, params=params, headers=headers, timeout=self.timeout)
            if resp.status_code != 200:
                return None

            data = resp.json()
            ware = data.get("wareInfo", {}).get("basicInfo", {})
            if not ware:
                return None

            images = [self._normalize_image_url(item) for item in ware.get("images", [])]
            images = [item for item in images if item]

            return {
                "success": True,
                "product_id": product_id,
                "source": "api",
                "title": ware.get("name", ""),
                "price": ware.get("jdPrice", ""),
                "brand": ware.get("brand", ""),
                "category": ware.get("categoryName", ""),
                "images": images,
                "url": f"https://item.jd.com/{product_id}.html",
            }
        except Exception:
            return None

    def _scrape_via_html(self, url: str, product_id: str) -> Optional[Dict[str, Any]]:
        try:
            import requests

            headers = {
                "User-Agent": self.USER_AGENT,
                "Referer": "https://www.jd.com/",
            }
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            if resp.status_code != 200:
                return None

            return self._build_product_from_html(resp.text, url, product_id, source="html")
        except Exception:
            return None

    def _build_product_from_html(self, html: str, url: str, product_id: str, source: str) -> Optional[Dict[str, Any]]:
        if not html or self._looks_like_blocked_page(html):
            return None

        title = self._extract_title(html)
        price = self._extract_price(html)
        meta_description = self._extract_meta_description(html)
        gallery_images = self._extract_gallery_images(html)
        desc_api_url = self._extract_desc_api_url(html, product_id)
        detail_html = self._fetch_detail_html(desc_api_url) if desc_api_url else ""
        detail_images = self._extract_detail_image_urls(detail_html) or gallery_images
        local_detail_images = self.download_images(product_id, detail_images)

        if not title:
            return None

        payload: Dict[str, Any] = {
            "success": True,
            "product_id": product_id,
            "source": source,
            "title": title,
            "price": price,
            "url": url,
            "images": gallery_images,
        }
        if meta_description:
            payload["description"] = meta_description
        if detail_html:
            payload["detail_content"] = detail_html
        if local_detail_images:
            payload["description_images"] = local_detail_images
        return payload

    def _scrape_via_opencli(self, url: str, product_id: str) -> Optional[Dict[str, Any]]:
        session = f"jd-scrape-{product_id}-{uuid.uuid4().hex[:6]}"
        for prefix in self._opencli_command_prefixes():
            try:
                opened = self._run_opencli(prefix, ["browser", "--session", session, "--window", "background", "open", url])
                if opened is None:
                    continue
                self._run_opencli(prefix, ["browser", "--session", session, "wait", "selector", "body", "--timeout", "15000"])
                html = self._run_opencli(prefix, ["browser", "--session", session, "get", "html"])
                if html:
                    product = self._build_product_from_html(html, url, product_id, source="opencli")
                    if product:
                        return product
            except Exception:
                continue
            finally:
                self._run_opencli(prefix, ["browser", "--session", session, "close"], check=False)
        return None

    def _opencli_command_prefixes(self) -> list[list[str]]:
        prefixes: list[list[str]] = []
        opencli_bin = shutil.which("opencli")
        if opencli_bin:
            prefixes.append([opencli_bin])

        tsx_cmd = Path(r"E:\PY\opencli\node_modules\.bin\tsx.cmd")
        tsx_bin = Path(r"E:\PY\opencli\node_modules\.bin\tsx")
        main_ts = Path(r"E:\PY\opencli\src\main.ts")
        if main_ts.exists():
            if tsx_cmd.exists():
                prefixes.append([str(tsx_cmd), str(main_ts)])
            elif tsx_bin.exists():
                prefixes.append([str(tsx_bin), str(main_ts)])
        return prefixes

    def _run_opencli(self, prefix: list[str], args: list[str], check: bool = True) -> Optional[str]:
        try:
            completed = subprocess.run(
                [*prefix, *args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=max(self.timeout, 30),
                check=False,
            )
        except Exception:
            return None

        if check and completed.returncode != 0:
            return None
        return (completed.stdout or "").strip()

    def _load_cached_html(self, product_id: str) -> str:
        candidates = [
            Path("product_data") / f"{product_id}.html",
            Path("product_data") / f"page_source_{product_id}.html",
            Path("product_data") / "page_source.html",
        ]
        for path in candidates:
            if not path.exists():
                continue
            try:
                text = path.read_text(encoding="utf-8-sig", errors="ignore")
            except Exception:
                continue
            if product_id in text or "imageList:" in text:
                return text
        return ""

    def _extract_title(self, html: str) -> str:
        patterns = [
            r"<title>([^<]+?)\s*[-|]",
            r'property="og:title"\s+content="([^"]+)"',
            r'class="sku-name"[^>]*>([^<]+)',
            r"name:\s*'([^']+)'",
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.I | re.S)
            if match:
                return self._clean_html_text(match.group(1))
        return ""

    def _extract_price(self, html: str) -> str:
        patterns = [
            r'"p":\s*"([\d.]+)"',
            r'jd-price["\s:>]+(?:¥|&yen;)?([\d.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.I | re.S)
            if match:
                return match.group(1)
        return ""

    def _extract_meta_description(self, html: str) -> str:
        match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html, re.I)
        if not match:
            return ""
        return self._clean_html_text(match.group(1))

    def _extract_gallery_images(self, html: str) -> list[str]:
        match = re.search(r"imageList:\s*(\[[^\]]+\])", html, re.I | re.S)
        if not match:
            return []
        try:
            raw_items = json.loads(match.group(1))
        except Exception:
            return []
        normalized = [self._normalize_image_url(item) for item in raw_items]
        return [item for item in normalized if item]

    def _extract_desc_api_url(self, html: str, product_id: str) -> str:
        match = re.search(r"desc:\s*'([^']+pc_description_channel[^']*)'", html, re.I)
        if match:
            return self._normalize_api_url(match.group(1))
        return (
            "https://api.m.jd.com/description/channel"
            f"?appid=item-v3&functionId=pc_description_channel&skuId={product_id}&charset=utf-8&cdn=2"
        )

    def _fetch_detail_html(self, api_url: str) -> str:
        try:
            import requests

            headers = {
                "User-Agent": self.USER_AGENT,
                "Referer": "https://item.jd.com/",
            }
            resp = requests.get(api_url, headers=headers, timeout=self.timeout)
            if resp.status_code != 200:
                return ""

            text = resp.text.strip()
            data: Any
            if text.startswith("{"):
                data = resp.json()
            else:
                data = self._parse_jsonp(text)

            detail_html = ""
            if isinstance(data, dict):
                detail_html = (
                    data.get("content")
                    or data.get("detail")
                    or data.get("data", {}).get("content", "")
                    or data.get("data", {}).get("detail", "")
                )
            return str(detail_html or "")
        except Exception:
            return ""

    def _extract_detail_image_urls(self, detail_html: str) -> list[str]:
        if not detail_html:
            return []
        matches = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', detail_html, re.I)
        normalized = [self._normalize_image_url(item) for item in matches]
        return [item for item in normalized if item]

    def download_images(self, product_id: str, image_urls: Iterable[str], limit: int = 12) -> list[str]:
        urls = []
        seen = set()
        for item in image_urls:
            normalized = self._normalize_image_url(item)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            urls.append(normalized)
            if len(urls) >= limit:
                break

        if not urls:
            return []

        try:
            import requests
        except Exception:
            return []

        target_dir = self.image_cache_dir / str(product_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        headers = {"User-Agent": self.USER_AGENT, "Referer": "https://item.jd.com/"}
        downloaded: list[str] = []
        for index, image_url in enumerate(urls, start=1):
            suffix = Path(image_url.split("?", 1)[0]).suffix or ".jpg"
            output_path = target_dir / f"detail_{index:02d}{suffix}"
            if output_path.exists() and output_path.stat().st_size > 0:
                downloaded.append(str(output_path.resolve()))
                continue
            try:
                resp = requests.get(image_url, headers=headers, timeout=self.timeout)
                if resp.status_code != 200 or not resp.content:
                    continue
                output_path.write_bytes(resp.content)
                downloaded.append(str(output_path.resolve()))
            except Exception:
                continue
        return downloaded

    def _normalize_image_url(self, value: Any) -> str:
        text = str(value or "").strip()
        if not text:
            return ""
        if text.startswith("//"):
            return f"https:{text}"
        if text.startswith("/"):
            return urljoin("https://img10.360buyimg.com/", text.lstrip("/"))
        if text.startswith("http://") or text.startswith("https://"):
            return text
        if text.startswith("jfs/") or text.startswith("imgzone/"):
            return f"https://img10.360buyimg.com/n1/{text}"
        return text

    def _normalize_api_url(self, value: str) -> str:
        text = str(value or "").strip()
        if text.startswith("//"):
            return f"https:{text}"
        if text.startswith("/"):
            return urljoin("https://api.m.jd.com", text)
        return text

    def _parse_jsonp(self, text: str) -> Any:
        match = re.search(r"^[^(]+\((.*)\)\s*;?\s*$", text, re.S)
        if not match:
            return {}
        try:
            return json.loads(match.group(1))
        except Exception:
            return {}

    def _clean_html_text(self, value: str) -> str:
        text = re.sub(r"<[^>]+>", " ", str(value or ""))
        text = text.replace("&nbsp;", " ").replace("&yen;", "¥")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _looks_like_blocked_page(self, html: str) -> bool:
        title = self._extract_title(html)
        lowered = str(html or "").lower()
        blocked_titles = {
            "京东(jd.com)",
            "多快好省，购物上京东",
        }
        if title in blocked_titles:
            return True
        return "window.location.href" in lowered and "item.m.jd.com/product" in lowered and "imageList:" not in html
