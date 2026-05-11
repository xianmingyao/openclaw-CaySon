import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cli import _enrich_product_from_source


def test_enrich_product_from_source_merges_local_product_preset(monkeypatch):
    class FakeScraper:
        def scrape(self, url: str):
            return {
                "success": True,
                "product_id": "16793098028",
                "title": "source-title",
                "description": "source-description",
                "description_images": ["detail-a.jpg"],
            }

    monkeypatch.setattr("scraper.JDScraper", FakeScraper)

    payload = {
        "title": "公牛（BULL） 插座/B5系列 带儿童保护门/新国标插座/排插 【8位】总控1.6米（新国标防过载）B5440",
        "url": "https://item.jd.com/16793098028.html",
        "model": "无",
        "attributes": {},
    }

    result = _enrich_product_from_source(payload)

    assert result["product_id"] == "16793098028"
    assert result["model"] == "无"
    assert result["attributes"] == {}


def test_enrich_product_from_source_allows_exact_title_preset_without_variant_conflict(monkeypatch):
    class FakeScraper:
        def scrape(self, url: str):
            return {
                "success": True,
                "product_id": "16793098028",
                "title": "source-title",
                "description": "source-description",
                "description_images": ["detail-a.jpg"],
            }

    monkeypatch.setattr("scraper.JDScraper", FakeScraper)

    payload = {
        "title": "公牛（BULL） 插座/B5系列 带儿童保护门/新国标插座/排插 【8位】总控1.6米（新国标防过载）B5440",
        "url": "https://item.jd.com/16793098028.html",
        "unit": "",
    }

    result = _enrich_product_from_source(payload)

    assert result["unit"] == "个"
    assert result["url"] == "https://item.jd.com/16793098028.html"
