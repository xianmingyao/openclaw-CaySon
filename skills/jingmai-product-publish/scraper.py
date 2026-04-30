"""
京麦商品发布自动化 - JD 商品信息采集
从京东商品页采集标题、价格、类目等信息
"""
import re
import json
from typing import Dict, Any, Optional
from urllib.parse import urlparse


class JDScraper:
    """京东商品信息采集器"""

    # 商品信息字段映射
    FIELD_MAP = {
        "name": "title",
        "p-name": "title",
        "jd-price": "price",
        "summary-price": "price",
    }

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def scrape(self, url: str) -> Dict[str, Any]:
        """
        采集商品信息
        url: 京东商品页 URL
        """
        # 从 URL 提取商品 ID
        product_id = self._extract_product_id(url)
        if not product_id:
            return {"success": False, "error": f"无法从 URL 提取商品 ID: {url}"}

        # 方式1: 通过 JD API 获取
        product = self._scrape_via_api(product_id)
        if product:
            return product

        # 方式2: 通过网页解析
        product = self._scrape_via_html(url, product_id)
        if product:
            return product

        # 降级: 只返回 ID
        return {
            "success": True,
            "product_id": product_id,
            "source": "url_only",
            "title": "",
            "price": "",
        }

    def _extract_product_id(self, url: str) -> str:
        """从 URL 提取商品 ID"""
        # 标准格式: https://item.jd.com/12345678.html
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

    def _scrape_via_api(self, product_id: str) -> Optional[Dict[str, Any]]:
        """通过 JD 商品详情 API 获取"""
        try:
            import requests
            # JD 移动端 API
            api_url = f"https://api.m.jd.com/client.action"
            params = {
                "functionId": "wareBusiness",
                "body": json.dumps({"skuId": product_id}),
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
            resp = requests.get(api_url, params=params, headers=headers, timeout=self.timeout)
            if resp.status_code != 200:
                return None

            data = resp.json()
            ware = data.get("wareInfo", {}).get("basicInfo", {})
            if not ware:
                return None

            return {
                "success": True,
                "product_id": product_id,
                "source": "api",
                "title": ware.get("name", ""),
                "price": ware.get("jdPrice", ""),
                "brand": ware.get("brand", ""),
                "category": ware.get("categoryName", ""),
                "images": ware.get("images", []),
                "url": f"https://item.jd.com/{product_id}.html",
            }
        except Exception:
            return None

    def _scrape_via_html(self, url: str, product_id: str) -> Optional[Dict[str, Any]]:
        """通过网页解析获取"""
        try:
            import requests
            from html.parser import HTMLParser

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Cookie": "",
            }
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            if resp.status_code != 200:
                return None

            html = resp.text
            title = self._extract_title(html)
            price = self._extract_price(html)

            if not title:
                return None

            return {
                "success": True,
                "product_id": product_id,
                "source": "html",
                "title": title,
                "price": price,
                "url": url,
            }
        except Exception:
            return None

    def _extract_title(self, html: str) -> str:
        """从 HTML 提取商品标题"""
        # 方式1: <title> 标签
        match = re.search(r"<title>([^<]+?)\s*[-|]", html)
        if match:
            return match.group(1).strip()

        # 方式2: meta og:title
        match = re.search(r'property="og:title"\s+content="([^"]+)"', html)
        if match:
            return match.group(1).strip()

        # 方式3: 商品名 class
        match = re.search(r'class="sku-name"[^>]*>([^<]+)', html)
        if match:
            return match.group(1).strip()

        return ""

    def _extract_price(self, html: str) -> str:
        """从 HTML 提取价格"""
        # JD 价格通常在 JS 变量中
        match = re.search(r'"p":\s*"([\d.]+)"', html)
        if match:
            return match.group(1)

        match = re.search(r'jd-price["\s:>]+￥?([\d.]+)', html)
        if match:
            return match.group(1)

        return ""
