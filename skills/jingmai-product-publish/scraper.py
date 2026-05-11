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

        best_product: Optional[Dict[str, Any]] = None
        diagnostics: Dict[str, Any] = {"product_id": product_id, "strategies": []}
        cached_html = self._load_cached_html(product_id)
        diagnostics["strategies"].append(
            {
                "strategy": "cache_probe",
                "status": "hit" if cached_html else "miss",
                "html_length": len(cached_html or ""),
            }
        )
        cached = self._build_product_from_html(cached_html, url, product_id, source="cache") if cached_html else None
        if cached:
            best_product = self._enrich_product_with_api(cached, product_id)
            diagnostics["strategies"].append(
                {
                    "strategy": "cache",
                    "status": "success",
                    "complete": self._is_product_payload_complete(best_product),
                    "score": self._product_completeness_score(best_product),
                }
            )
            if self._is_product_payload_complete(best_product):
                return self._attach_scrape_diagnostics(best_product, diagnostics)
        elif cached_html:
            diagnostics["strategies"].append({"strategy": "cache", "status": "unusable_html"})

        product = self._scrape_via_playwright(url, product_id)
        if product:
            best_product = self._merge_product_candidates(
                best_product,
                self._enrich_product_with_api(product, product_id),
            )
            diagnostics["strategies"].append(
                {
                    "strategy": "playwright",
                    "status": "success",
                    "complete": self._is_product_payload_complete(best_product),
                    "score": self._product_completeness_score(best_product),
                }
            )
            if self._is_product_payload_complete(best_product):
                return self._attach_scrape_diagnostics(best_product, diagnostics)
        else:
            diagnostics["strategies"].append({"strategy": "playwright", "status": "empty"})

        product = self._scrape_via_opencli(url, product_id)
        if product:
            best_product = self._merge_product_candidates(
                best_product,
                self._enrich_product_with_api(product, product_id),
            )
            diagnostics["strategies"].append(
                {
                    "strategy": "opencli",
                    "status": "success",
                    "complete": self._is_product_payload_complete(best_product),
                    "score": self._product_completeness_score(best_product),
                    "prefixes": [" ".join(prefix) for prefix in self._opencli_command_prefixes()],
                }
            )
            if self._is_product_payload_complete(best_product):
                return self._attach_scrape_diagnostics(best_product, diagnostics)
        else:
            diagnostics["strategies"].append(
                {
                    "strategy": "opencli",
                    "status": "empty",
                    "prefixes": [" ".join(prefix) for prefix in self._opencli_command_prefixes()],
                }
            )

        product = self._scrape_via_api(product_id)
        if product:
            product.setdefault("url", f"https://item.jd.com/{product_id}.html")
            best_product = self._merge_product_candidates(best_product, product)
            diagnostics["strategies"].append(
                {
                    "strategy": "api",
                    "status": "success",
                    "complete": self._is_product_payload_complete(best_product),
                    "score": self._product_completeness_score(best_product),
                }
            )
            if self._is_product_payload_complete(best_product):
                return self._attach_scrape_diagnostics(best_product, diagnostics)
        else:
            diagnostics["strategies"].append({"strategy": "api", "status": "empty"})

        product = self._scrape_via_html(url, product_id)
        if product:
            best_product = self._merge_product_candidates(
                best_product,
                self._enrich_product_with_api(product, product_id),
            )
            diagnostics["strategies"].append(
                {
                    "strategy": "html",
                    "status": "success",
                    "complete": self._is_product_payload_complete(best_product),
                    "score": self._product_completeness_score(best_product),
                    "title": str(product.get("title", "") or "")[:120],
                }
            )
            if self._is_product_payload_complete(best_product):
                return self._attach_scrape_diagnostics(best_product, diagnostics)
        else:
            diagnostics["strategies"].append({"strategy": "html", "status": "empty"})

        if best_product:
            return self._attach_scrape_diagnostics(best_product, diagnostics)

        return self._attach_scrape_diagnostics(
            {
            "success": True,
            "product_id": product_id,
            "source": "url_only",
            "title": "",
            "price": "",
            "url": f"https://item.jd.com/{product_id}.html",
            },
            diagnostics,
        )

    def _enrich_product_with_api(self, product: Dict[str, Any], product_id: str) -> Dict[str, Any]:
        payload = dict(product or {})
        if not product_id:
            return payload
        if str(payload.get("source", "") or "").strip().lower() == "opencli":
            return payload
        needs_api_fill = any(payload.get(field) in (None, "", []) for field in ("category", "brand", "price"))
        if not needs_api_fill:
            return payload
        api_product = self._scrape_via_api(product_id)
        if not api_product:
            return payload
        for field in ("category", "brand", "price", "images", "url"):
            if payload.get(field) in (None, "", []):
                value = api_product.get(field)
                if value not in (None, "", []):
                    payload[field] = value
        payload.setdefault("source_meta", {})
        api_meta = dict(api_product.get("source_meta") or {})
        for key, value in api_meta.items():
            payload["source_meta"].setdefault(key, value)
        return payload

    @staticmethod
    def _is_product_payload_complete(product: Optional[Dict[str, Any]]) -> bool:
        if not isinstance(product, dict):
            return False
        has_title = bool(str(product.get("title", "") or "").strip())
        price_or_brand_count = sum(
            1 for field in ("price", "brand") if product.get(field) not in (None, "", [])
        )
        has_core_merch_fields = price_or_brand_count >= 1
        has_assets = any(product.get(field) not in (None, "", []) for field in ("images", "description_images", "detail_content"))
        return has_title and has_core_merch_fields and has_assets

    @staticmethod
    def _product_completeness_score(product: Optional[Dict[str, Any]]) -> int:
        if not isinstance(product, dict):
            return 0
        score = 0
        for field in ("title", "price", "brand", "category", "description", "detail_content"):
            if product.get(field) not in (None, "", []):
                score += 2
        for field in ("images", "description_images"):
            if product.get(field) not in (None, "", []):
                score += 2
        return score

    def _merge_product_candidates(
        self,
        base: Optional[Dict[str, Any]],
        candidate: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        if not isinstance(candidate, dict):
            return base
        if not isinstance(base, dict):
            return dict(candidate)

        merged = dict(base)
        base_score = self._product_completeness_score(base)
        candidate_score = self._product_completeness_score(candidate)
        preferred = candidate if candidate_score > base_score else base
        merged["source"] = preferred.get("source", merged.get("source", ""))

        for field in (
            "product_id",
            "title",
            "price",
            "brand",
            "category",
            "description",
            "detail_content",
            "images",
            "description_images",
            "url",
        ):
            if merged.get(field) in (None, "", []):
                value = candidate.get(field)
                if value not in (None, "", []):
                    merged[field] = value

        merged_source_meta = dict(merged.get("source_meta") or {})
        candidate_source_meta = dict(candidate.get("source_meta") or {})
        for key, value in candidate_source_meta.items():
            merged_source_meta.setdefault(key, value)
        if merged_source_meta:
            merged["source_meta"] = merged_source_meta
        return merged

    @staticmethod
    def _attach_scrape_diagnostics(product: Dict[str, Any], diagnostics: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(product or {})
        source_meta = dict(payload.get("source_meta") or {})
        source_meta["scrape_diagnostics"] = diagnostics
        payload["source_meta"] = source_meta
        return payload

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
            local_images = self.download_images(product_id, images, prefix="main", subdir="main")

            return {
                "success": True,
                "product_id": product_id,
                "source": "api",
                "title": ware.get("name", ""),
                "price": ware.get("jdPrice", ""),
                "brand": ware.get("brand", ""),
                "category": ware.get("categoryName", ""),
                "images": local_images or images,
                "source_meta": {
                    "image_source_urls": images,
                },
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
        category = self._extract_category(html)
        meta_description = self._extract_meta_description(html)
        gallery_images = self._extract_gallery_images(html)
        local_gallery_images = self.download_images(product_id, gallery_images, prefix="main", subdir="main")
        desc_api_url = self._extract_desc_api_url(html, product_id)
        detail_html = self._fetch_detail_html(desc_api_url) if desc_api_url else ""
        detail_images = self._extract_detail_image_urls(detail_html) or gallery_images
        local_detail_images = self.download_images(product_id, detail_images, prefix="detail", subdir="detail")

        if not title:
            return None

        payload: Dict[str, Any] = {
            "success": True,
            "product_id": product_id,
            "source": source,
            "title": title,
            "price": price,
            "category": category,
            "url": url,
            "images": local_gallery_images or gallery_images,
            "source_meta": {
                "image_source_urls": gallery_images,
                "detail_image_source_urls": detail_images,
            },
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
        contract = self._load_opencli_browser_contract()
        for prefix in self._opencli_command_prefixes():
            try:
                open_args = ["browser", "--session", session]
                if contract.get("supports_window_flag"):
                    open_args.extend(["--window", "background"])
                open_args.extend(["open", url])
                opened = self._run_opencli(prefix, open_args)
                if opened is None:
                    continue
                for wait_args in self._opencli_wait_commands(session):
                    wait_result = self._run_opencli(prefix, wait_args, check=False)
                    if wait_result is not None:
                        break
                html = ""
                for html_args in self._opencli_html_commands(session):
                    output = self._run_opencli(prefix, html_args, check=False)
                    html = self._extract_opencli_html(output)
                    if html:
                        break
                if html:
                    product = self._build_product_from_html(html, url, product_id, source="opencli")
                    if product:
                        return product
                for state_args in self._opencli_state_commands(session):
                    output = self._run_opencli(prefix, state_args, check=False)
                    product = self._extract_opencli_product_from_state(output, url, product_id)
                    if product:
                        return product
                for network_args in self._opencli_network_commands(session):
                    output = self._run_opencli(prefix, network_args, check=False)
                    product = self._extract_opencli_product_from_network(output, url, product_id)
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

    def _load_opencli_browser_contract(self) -> Dict[str, Any]:
        repo_root = Path(r"E:\PY\opencli")
        contract = {
            "supports_window_flag": True,
            "html_commands": [
                ["browser", "--session", "{session}", "get", "html"],
                ["browser", "--session", "{session}", "get", "html", "--selector", "html"],
            ],
            "state_commands": [
                ["browser", "--session", "{session}", "state"],
            ],
            "network_commands": [
                ["browser", "--session", "{session}", "network", "--since", "30s", "--raw"],
                ["browser", "--session", "{session}", "network", "--since", "30s"],
            ],
        }

        manifest_path = repo_root / "cli-manifest.json"
        readme_path = repo_root / "README.md"
        try:
            manifest_text = manifest_path.read_text(encoding="utf-8")
            if '"--window <mode>"' not in manifest_text and '"--window"' not in manifest_text:
                contract["supports_window_flag"] = False
            if '"browser", "get", "html"' not in manifest_text and '"get html"' not in manifest_text:
                contract["html_commands"] = [
                    ["browser", "--session", "{session}", "state"],
                ]
        except Exception:
            pass

        try:
            readme_text = readme_path.read_text(encoding="utf-8")
            if "browser get html" in readme_text and ["browser", "--session", "{session}", "get", "html"] not in contract["html_commands"]:
                contract["html_commands"].insert(0, ["browser", "--session", "{session}", "get", "html"])
            if "get html --as json" in readme_text:
                contract["html_commands"].append(
                    ["browser", "--session", "{session}", "get", "html", "--as", "json", "--depth", "3", "--children-max", "30", "--text-max", "400"]
                )
            if "browser state --source ax" in readme_text:
                contract["state_commands"].append(["browser", "--session", "{session}", "state", "--source", "ax"])
            if "browser network" in readme_text and ["browser", "--session", "{session}", "network", "--since", "30s", "--raw"] not in contract["network_commands"]:
                contract["network_commands"].insert(0, ["browser", "--session", "{session}", "network", "--since", "30s", "--raw"])
            if "--window <foreground|background>" not in readme_text and "--window <foreground\\|background>" not in readme_text:
                contract["supports_window_flag"] = contract["supports_window_flag"] and False
        except Exception:
            pass

        return contract

    def _opencli_wait_commands(self, session: str) -> list[list[str]]:
        return [
            ["browser", "--session", session, "wait", "selector", "body", "--timeout", "15000"],
            ["browser", "--session", session, "wait", "selector", "body"],
        ]

    def _opencli_html_commands(self, session: str) -> list[list[str]]:
        contract = self._load_opencli_browser_contract()
        commands: list[list[str]] = []
        for template in contract.get("html_commands", []):
            commands.append([part.replace("{session}", session) for part in template])
        return commands

    def _opencli_state_commands(self, session: str) -> list[list[str]]:
        contract = self._load_opencli_browser_contract()
        commands: list[list[str]] = []
        for template in contract.get("state_commands", []):
            commands.append([part.replace("{session}", session) for part in template])
        return commands

    def _opencli_network_commands(self, session: str) -> list[list[str]]:
        contract = self._load_opencli_browser_contract()
        commands: list[list[str]] = []
        for template in contract.get("network_commands", []):
            commands.append([part.replace("{session}", session) for part in template])
        return commands

    def _extract_opencli_html(self, output: Optional[str]) -> str:
        text = str(output or "").strip()
        if not text:
            return ""
        if text.startswith("<"):
            return text
        try:
            payload = json.loads(text)
        except Exception:
            return ""
        if isinstance(payload, str):
            return payload if payload.lstrip().startswith("<") else ""
        if isinstance(payload, dict):
            for key in ("html", "content", "outerHTML"):
                value = payload.get(key)
                if isinstance(value, str) and value.lstrip().startswith("<"):
                    return value
        return ""

    def _extract_opencli_product_from_state(self, output: Optional[str], url: str, product_id: str) -> Optional[Dict[str, Any]]:
        payload = self._parse_opencli_json(output)
        if payload is None:
            return None
        html = self._extract_opencli_html(output)
        if html:
            product = self._build_product_from_html(html, url, product_id, source="opencli")
            if product:
                return product

        state_url = self._find_first_string(payload, {"url", "href"})
        state_title = self._find_first_string(payload, {"title", "name"})
        if state_title and "京东" in state_title and "JD.COM" not in state_title:
            return {
                "success": True,
                "product_id": product_id,
                "source": "opencli",
                "title": self._strip_jd_suffix(state_title),
                "url": state_url or url,
                "source_meta": {"opencli_state_used": True},
            }
        return None

    def _extract_opencli_product_from_network(self, output: Optional[str], url: str, product_id: str) -> Optional[Dict[str, Any]]:
        payload = self._parse_opencli_json(output)
        if payload is None:
            return None

        for text in self._iter_payload_strings(payload):
            if not text:
                continue
            html = self._extract_opencli_html(text)
            if html:
                product = self._build_product_from_html(html, url, product_id, source="opencli")
                if product:
                    return product
            extracted = self._extract_product_from_json_text(text, url, product_id)
            if extracted:
                return extracted

        if isinstance(payload, (dict, list)):
            extracted = self._extract_product_from_json_payload(payload, url, product_id)
            if extracted:
                return extracted
        return None

    def _extract_product_from_json_text(self, text: str, url: str, product_id: str) -> Optional[Dict[str, Any]]:
        stripped = str(text or "").strip()
        if not stripped or stripped[0] not in "[{":
            return None
        try:
            payload = json.loads(stripped)
        except Exception:
            return None
        return self._extract_product_from_json_payload(payload, url, product_id)

    def _extract_product_from_json_payload(self, payload: Any, url: str, product_id: str) -> Optional[Dict[str, Any]]:
        title = self._find_first_string(payload, {"skuName", "name", "title", "wareName"})
        brand = self._find_first_string(payload, {"brandName", "brand"})
        category = self._find_first_string(payload, {"category", "categoryName", "catName"})
        price = self._find_first_numeric_string(payload, {"price", "p", "jdPrice"})
        images = self._find_all_image_urls(payload)
        if not any([title, brand, category, price, images]):
            return None
        product: Dict[str, Any] = {
            "success": True,
            "product_id": product_id,
            "source": "opencli",
            "title": self._strip_jd_suffix(title),
            "price": price,
            "brand": brand,
            "category": category,
            "url": url,
        }
        if images:
            product["source_meta"] = {"image_source_urls": images}
        return product

    @staticmethod
    def _parse_opencli_json(output: Optional[str]) -> Any:
        text = str(output or "").strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except Exception:
            return None

    def _iter_payload_strings(self, payload: Any) -> Iterable[str]:
        if isinstance(payload, str):
            yield payload
            return
        if isinstance(payload, dict):
            for value in payload.values():
                yield from self._iter_payload_strings(value)
            return
        if isinstance(payload, list):
            for item in payload:
                yield from self._iter_payload_strings(item)

    def _find_first_string(self, payload: Any, preferred_keys: set[str]) -> str:
        if isinstance(payload, dict):
            for key, value in payload.items():
                if key in preferred_keys and isinstance(value, str) and value.strip():
                    return value.strip()
            for value in payload.values():
                nested = self._find_first_string(value, preferred_keys)
                if nested:
                    return nested
        elif isinstance(payload, list):
            for item in payload:
                nested = self._find_first_string(item, preferred_keys)
                if nested:
                    return nested
        return ""

    def _find_first_numeric_string(self, payload: Any, preferred_keys: set[str]) -> str:
        value = self._find_first_string(payload, preferred_keys)
        if value:
            match = re.search(r"\d+(?:\.\d+)?", value)
            if match:
                return match.group(0)
        if isinstance(payload, dict):
            for key, child in payload.items():
                if key in preferred_keys and isinstance(child, (int, float)):
                    return str(child)
                nested = self._find_first_numeric_string(child, preferred_keys)
                if nested:
                    return nested
        elif isinstance(payload, list):
            for item in payload:
                nested = self._find_first_numeric_string(item, preferred_keys)
                if nested:
                    return nested
        return ""

    def _find_all_image_urls(self, payload: Any) -> list[str]:
        urls: list[str] = []
        for text in self._iter_payload_strings(payload):
            candidate = str(text or "").strip()
            if not candidate:
                continue
            if any(ext in candidate.lower() for ext in (".jpg", ".jpeg", ".png", ".webp")) and ("img" in candidate.lower() or candidate.startswith("//")):
                normalized = self._normalize_image_url(candidate)
                if normalized and normalized not in urls:
                    urls.append(normalized)
        return urls[:20]

    @staticmethod
    def _strip_jd_suffix(text: str) -> str:
        value = str(text or "").strip()
        for suffix in ("- 京东", "_京东", "-JD", "- JD", "【京东】", "京东(JD.COM)"):
            if value.endswith(suffix):
                value = value[: -len(suffix)].strip()
        return value

    def _extract_category(self, html: str) -> str:
        match = re.search(r'catName:\s*\[(.*?)\]', html, re.I | re.S)
        if match:
            raw_values = re.findall(r'"([^"]+)"', match.group(1))
            if raw_values:
                return " > ".join([item.strip() for item in raw_values if item.strip()])

        matches = re.findall(r'<div class="item"><a [^>]+>([^<]+)</a></div>', html, re.I)
        cleaned = [self._clean_html_text(item) for item in matches if self._clean_html_text(item)]
        if cleaned:
            return " > ".join(cleaned[-3:])
        return ""

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

    def download_images(
        self,
        product_id: str,
        image_urls: Iterable[str],
        limit: int = 12,
        prefix: str = "detail",
        subdir: str = "",
    ) -> list[str]:
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
        if subdir:
            target_dir = target_dir / subdir
        target_dir.mkdir(parents=True, exist_ok=True)
        headers = {"User-Agent": self.USER_AGENT, "Referer": "https://item.jd.com/"}
        downloaded: list[str] = []
        for index, image_url in enumerate(urls, start=1):
            suffix = Path(image_url.split("?", 1)[0]).suffix or ".jpg"
            output_path = target_dir / f"{prefix}_{index:02d}{suffix}"
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
