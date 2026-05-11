import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class _FakeResponse:
    def __init__(self, text="", status_code=200, json_data=None, content=b""):
        self.text = text
        self.status_code = status_code
        self._json_data = json_data
        self.content = content

    def json(self):
        if self._json_data is not None:
            return self._json_data
        raise ValueError("no json payload")


def test_scraper_html_path_collects_detail_assets(monkeypatch, tmp_path):
    import scraper as scraper_module

    html = """
    <html>
    <head>
      <title>Test Socket - JD</title>
      <meta name="description" content="meta detail text">
    </head>
    <body>
      <script>
        imageList: ["jfs/t1/a.jpg","jfs/t1/b.jpg"],
        desc: '//api.m.jd.com/description/channel?functionId=pc_description_channel&skuId=123'
      </script>
    </body>
    </html>
    """
    detail_json = {
        "content": '<div><img src="//img10.360buyimg.com/n1/jfs/t1/detail-a.jpg"/></div>'
    }

    def fake_get(url, **kwargs):
        if "item.jd.com" in url:
            return _FakeResponse(text=html, status_code=200)
        if "pc_description_channel" in url:
            return _FakeResponse(text='{"content":"<div><img src=\\"//img10.360buyimg.com/n1/jfs/t1/detail-a.jpg\\"/></div>"}', status_code=200, json_data=detail_json)
        if "detail-a.jpg" in url:
            return _FakeResponse(status_code=200, content=b"img-a")
        if "a.jpg" in url or "b.jpg" in url:
            return _FakeResponse(status_code=200, content=b"gallery")
        raise AssertionError(url)

    monkeypatch.setitem(sys.modules, "requests", type("Requests", (), {"get": staticmethod(fake_get)}))

    scraper = scraper_module.JDScraper(image_cache_dir=tmp_path)
    monkeypatch.setattr(scraper, "_load_cached_html", lambda product_id: "")
    monkeypatch.setattr(scraper, "_scrape_via_playwright", lambda url, product_id: None)
    monkeypatch.setattr(scraper, "_scrape_via_opencli", lambda url, product_id: None)
    result = scraper.scrape("https://item.jd.com/123.html")

    assert result["success"] is True
    assert result["title"] == "Test Socket"
    assert result["description"] == "meta detail text"
    assert "detail_content" in result
    assert result["description_images"]
    assert Path(result["description_images"][0]).exists()


def test_cli_enrich_product_from_source_merges_scraped_detail(monkeypatch):
    import cli as cli_module

    class FakeScraper:
        def scrape(self, url):
            return {
                "success": True,
                "product_id": "123",
                "price": "70",
                "description": "meta detail",
                "detail_content": "<p>detail</p>",
                "description_images": ["E:/tmp/detail_01.jpg"],
            }

    monkeypatch.setitem(sys.modules, "scraper", type("ScraperModule", (), {"JDScraper": FakeScraper}))

    enriched = cli_module._enrich_product_from_source(
        {
            "title": "test product",
            "url": "https://item.jd.com/123.html",
        }
    )

    assert enriched["product_id"] == "123"
    assert enriched["price"] == "70"
    assert enriched["description"] == "meta detail"
    assert enriched["detail_content"] == "<p>detail</p>"
    assert enriched["description_images"] == ["E:/tmp/detail_01.jpg"]


def test_scraper_falls_back_to_opencli_after_playwright(monkeypatch):
    import scraper as scraper_module

    scraper = scraper_module.JDScraper()
    monkeypatch.setattr(scraper, "_load_cached_html", lambda product_id: "")
    monkeypatch.setattr(scraper, "_scrape_via_playwright", lambda url, product_id: None)
    monkeypatch.setattr(
        scraper,
        "_scrape_via_opencli",
        lambda url, product_id: {
            "success": True,
            "product_id": product_id,
            "source": "opencli",
            "title": "OpenCLI Socket",
            "price": "70",
            "url": url,
        },
    )
    monkeypatch.setattr(scraper, "_scrape_via_api", lambda product_id: (_ for _ in ()).throw(AssertionError("api should not be called")))
    monkeypatch.setattr(scraper, "_scrape_via_html", lambda url, product_id: (_ for _ in ()).throw(AssertionError("html should not be called")))

    result = scraper.scrape("https://item.jd.com/16793098028.html")

    assert result["success"] is True
    assert result["source"] == "opencli"
    assert result["product_id"] == "16793098028"
