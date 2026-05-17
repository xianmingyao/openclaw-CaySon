"""京东商品抓取快照服务。"""

from __future__ import annotations

import json
import re
from decimal import Decimal
from html import escape

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from jingmai_publish.security import validate_http_url


class JDProductFetchService:
    """抓取京东商品页并构建快照。"""

    JD_ITEM_ID_PATTERN = re.compile(r"item\.jd\.com/(\d+)\.html|sku=(\d+)", re.IGNORECASE)
    JD_TITLE_NOISE_PATTERN = re.compile(r"【[^】]*(图片|价格|品牌|评论|行情|报价|评测)[^】]*】|-京东$")
    JD_TITLE_LEADING_SKU_PATTERN = re.compile(r"^【[^】]+】")
    MODEL_PATTERN = re.compile(r"\b([A-Za-z0-9][A-Za-z0-9\-_/.]{1,31})\b")
    GENERIC_TITLES = {
        "京东(JD.COM)-正品低价、品质保障、配送及时、轻松购物！",
        "京东登录注册",
    }
    ALLOWED_JD_HOSTS = ("item.jd.com", "item.m.jd.com")

    def __init__(self, upload_job_repo, snapshot_repo, runtime_log_repo) -> None:
        self.upload_job_repo = upload_job_repo
        self.snapshot_repo = snapshot_repo
        self.runtime_log_repo = runtime_log_repo

    @classmethod
    def extract_jd_item_id(cls, jd_item_url: str) -> str:
        """从京东链接中提取商品 ID。"""

        match = cls.JD_ITEM_ID_PATTERN.search(jd_item_url or "")
        if not match:
            raise ValueError(f"无法从京东链接提取商品ID: {jd_item_url}")
        return match.group(1) or match.group(2)

    def build_snapshot_for_job_item(self, job_item_id: int):
        """为单条商品行生成一份快照。"""

        item = self.upload_job_repo.get_job_item(job_item_id)
        if item is None:
            raise ValueError(f"未找到导入商品行: {job_item_id}")

        jd_item_id = self.extract_jd_item_id(item.jd_item_url)
        live_payload = self.fetch_product_payload(item.jd_item_url, fallback_price=getattr(item, "jd_sale_price", None))
        live_title = live_payload.get("title")
        if self._is_generic_title(live_title):
            live_title = None

        attributes = {
            "length_mm": self._serialize_decimal(getattr(item, "length_mm", None)),
            "width_mm": self._serialize_decimal(getattr(item, "width_mm", None)),
            "height_mm": self._serialize_decimal(getattr(item, "height_mm", None)),
            "weight_kg": self._serialize_decimal(getattr(item, "weight_kg", None)),
            "unit_name": getattr(item, "unit_name", None),
            **live_payload.get("attributes", {}),
        }
        payload = {
            "source": live_payload.get("source", "jd_rendered_page"),
            "jd_item_id": jd_item_id,
            "jd_item_url": item.jd_item_url,
            "title": live_title or getattr(item, "product_name", None),
            "brand": live_payload.get("brand") or getattr(item, "brand", None),
            "model": live_payload.get("model") or getattr(item, "model", None),
            "price": live_payload.get("price") or self._serialize_decimal(getattr(item, "jd_sale_price", None)),
            "attributes": attributes,
            "detail_text": live_payload.get("detail_text") or getattr(item, "product_summary", None),
            "images": live_payload.get("images", []),
            "fetch_notes": live_payload.get("fetch_notes", []),
        }

        snapshot = self.snapshot_repo.create_snapshot(
            job_item_id=item.id,
            jd_item_url=item.jd_item_url,
            jd_item_id=jd_item_id,
            title=payload["title"],
            brand=payload["brand"],
            model=payload["model"],
            price=self._to_decimal_or_none(payload["price"]),
            attributes_json=attributes,
            detail_html=live_payload.get("detail_html"),
            detail_text=payload["detail_text"],
            source_payload_json=json.dumps(payload, ensure_ascii=False),
        )
        self.runtime_log_repo.append_log(
            session_id=f"fetch-{job_item_id}",
            log_type="process",
            job_id=getattr(item, "job_id", None),
            job_item_id=item.id,
            message=f"已为商品行 {job_item_id} 抓取京东商品快照",
        )
        return snapshot

    def fetch_product_payload(self, jd_item_url: str, fallback_price: Decimal | None = None) -> dict[str, object]:
        """抓取并解析京东商品页面。"""

        jd_item_url = validate_http_url(
            jd_item_url,
            allowed_hosts=self.ALLOWED_JD_HOSTS,
            purpose="京东商品抓取",
        )
        html = self._fetch_page_html(jd_item_url)
        payload = self._parse_product_page(jd_item_url, html)
        if payload.get("price") is None and fallback_price is not None:
            payload["price"] = self._serialize_decimal(fallback_price)
            payload.setdefault("fetch_notes", []).append("live_price_unavailable_fallback_to_excel")
        return payload

    def _fetch_page_html(self, jd_item_url: str) -> str:
        try:
            html = self._fetch_via_requests(jd_item_url)
            if self._looks_like_product_page(html):
                return html
        except Exception:
            pass
        return self._fetch_via_playwright(jd_item_url)

    @staticmethod
    def _fetch_via_requests(jd_item_url: str) -> str:
        response = requests.get(
            jd_item_url,
            timeout=20,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        return response.text

    def _fetch_via_playwright(self, jd_item_url: str) -> str:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                for candidate_url in (jd_item_url, self._to_mobile_product_url(jd_item_url)):
                    page.goto(candidate_url, wait_until="networkidle", timeout=60000)
                    html = page.content()
                    if self._looks_like_product_page(html):
                        return html
                return page.content()
            finally:
                browser.close()

    @classmethod
    def _to_mobile_product_url(cls, jd_item_url: str) -> str:
        sku_id = cls.extract_jd_item_id(jd_item_url)
        return f"https://item.m.jd.com/product/{sku_id}.html"

    def _parse_product_page(self, jd_item_url: str, html: str) -> dict[str, object]:
        soup = BeautifulSoup(html, "html.parser")
        title = self._extract_title(soup)
        body_text = soup.get_text("\n", strip=True)
        brand = self._extract_brand(title, body_text)
        model = self._extract_model(title, body_text)
        price = self._extract_price(html, body_text)
        images = self._extract_images(soup)
        detail_text = self._extract_detail_text(body_text)
        detail_html = self._extract_detail_html(soup)
        if detail_html is None:
            detail_html = self._build_detail_html_from_images(images, title, detail_text)
        attributes = self._extract_attributes(body_text)

        fetch_notes: list[str] = []
        if price is None:
            fetch_notes.append("live_price_not_extracted")
        if not images:
            fetch_notes.append("live_images_not_extracted")

        return {
            "source": "jd_rendered_page",
            "url": jd_item_url,
            "title": title,
            "brand": brand,
            "model": model,
            "price": price,
            "images": images,
            "attributes": attributes,
            "detail_text": detail_text,
            "detail_html": detail_html,
            "fetch_notes": fetch_notes,
        }

    @classmethod
    def build_detail_editor_content(cls, payload: dict[str, object]) -> str | None:
        """从京东抓取 payload 构建可写入京麦详情编辑器的图文内容。"""

        detail_html = payload.get("detail_html")
        if isinstance(detail_html, str) and detail_html.strip():
            return detail_html.strip()

        images = payload.get("images")
        title = payload.get("title")
        detail_text = payload.get("detail_text")
        image_urls = [item for item in images if isinstance(item, str)] if isinstance(images, list) else []
        return cls._build_detail_html_from_images(
            image_urls,
            title if isinstance(title, str) else None,
            detail_text if isinstance(detail_text, str) else None,
        )

    def _extract_title(self, soup: BeautifulSoup) -> str | None:
        title_text = soup.title.get_text(" ", strip=True) if soup.title else None
        if not title_text:
            return None
        normalized = self.JD_TITLE_NOISE_PATTERN.sub("", title_text).strip()
        normalized = self.JD_TITLE_LEADING_SKU_PATTERN.sub("", normalized).strip()
        return normalized or title_text.strip()

    def _extract_brand(self, title: str | None, body_text: str) -> str | None:
        if title and "（" in title and "）" in title:
            match = re.search(r"([^\s]+?（[^）]+）)", title)
            if match:
                return match.group(1)
        store_match = re.search(r"([^\n]{2,40})京东自营旗舰店", body_text)
        if store_match:
            return store_match.group(1).strip()
        return None

    def _extract_model(self, title: str | None, body_text: str) -> str | None:
        if title:
            leading = re.search(r"^【([^】]+)】", title)
            if leading and any(char.isdigit() for char in leading.group(1)):
                return leading.group(1)
        search_area = "\n".join(filter(None, [title, body_text[:300]]))
        matches = self.MODEL_PATTERN.findall(search_area)
        candidates = [
            item
            for item in matches
            if any(char.isdigit() for char in item) and any(char.isalpha() for char in item)
        ]
        return candidates[-1] if candidates else None

    @staticmethod
    def _extract_price(html: str, body_text: str) -> str | None:
        patterns = [
            r'"price"\s*:\s*"([0-9]+(?:\.[0-9]+)?)"',
            r"￥\s*([0-9]+(?:\.[0-9]+)?)",
        ]
        for pattern in patterns:
            match = re.search(pattern, html) or re.search(pattern, body_text)
            if match:
                value = match.group(1)
                if value == "0":
                    continue
                return value
        return None

    @staticmethod
    def _extract_images(soup: BeautifulSoup) -> list[str]:
        image_urls: list[str] = []
        for img in soup.find_all("img"):
            for attr_name in ("src", "data-origin", "data-lazy-img", "source-data-lazy-img"):
                value = img.get(attr_name)
                if not value:
                    continue
                normalized = value.strip()
                if normalized.startswith("//"):
                    normalized = f"https:{normalized}"
                if normalized.startswith("http") and "360buyimg" in normalized and normalized not in image_urls:
                    image_urls.append(normalized)
        return image_urls[:20]

    @staticmethod
    def _extract_detail_text(body_text: str) -> str | None:
        lines = [line.strip() for line in body_text.splitlines() if line.strip()]
        if not lines:
            return None
        keep: list[str] = []
        capture = False
        for line in lines:
            if line in {"商品介绍", "包装清单", "商品参数"}:
                capture = True
            if capture:
                keep.append(line)
            if line in {"价格说明", "店铺", "客服", "购物车"} and capture:
                break
        if keep:
            return "\n".join(keep[:80])
        return "\n".join(lines[:80])

    @staticmethod
    def _extract_detail_html(soup: BeautifulSoup) -> str | None:
        for marker in ("#detail", "#detail-desc", ".detail"):
            node = soup.select_one(marker)
            if node:
                return str(node)
        return None

    @staticmethod
    def _build_detail_html_from_images(
        image_urls: list[str],
        title: str | None,
        detail_text: str | None,
    ) -> str | None:
        blocks: list[str] = ['<section class="jd-product-detail">']
        if title:
            blocks.append(f"<h2>{escape(title.strip())}</h2>")
        if detail_text:
            for line in detail_text.splitlines()[:20]:
                normalized = line.strip()
                if normalized:
                    blocks.append(f"<p>{escape(normalized)}</p>")
        for image_url in image_urls[:20]:
            normalized_url = image_url.strip()
            if not normalized_url:
                continue
            blocks.append(f'<p><img src="{escape(normalized_url, quote=True)}" /></p>')
        blocks.append("</section>")
        if len(blocks) <= 2:
            return None
        return "\n".join(blocks)

    @staticmethod
    def _extract_attributes(body_text: str) -> dict[str, str]:
        attributes: dict[str, str] = {}
        category_match = re.search(r"([^\n>]+>\s*[^\n>]+>\s*[^\n>]+)", body_text)
        if category_match:
            attributes["category_path"] = " ".join(category_match.group(1).split())
        store_match = re.search(r"([^\n]{2,40})京东自营旗舰店", body_text)
        if store_match:
            attributes["brand_name"] = store_match.group(1).strip()
        return attributes

    @classmethod
    def _looks_like_product_page(cls, html: str) -> bool:
        text = html or ""
        if any(title in text for title in cls.GENERIC_TITLES):
            return False
        return any(marker in text for marker in ["sku-name", "京 东 价", "商品参数", "京东自营旗舰店", "加入购物车"])

    @classmethod
    def _is_generic_title(cls, title: object) -> bool:
        return isinstance(title, str) and title in cls.GENERIC_TITLES

    @staticmethod
    def _serialize_decimal(value: Decimal | None) -> str | None:
        if value is None:
            return None
        return str(value)

    @staticmethod
    def _to_decimal_or_none(value: str | Decimal | None) -> Decimal | None:
        if value is None:
            return None
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
