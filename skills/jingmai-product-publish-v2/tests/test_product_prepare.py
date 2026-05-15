import json
from decimal import Decimal

from jingmai_publish.services.jd_fetch import JDProductFetchService
from jingmai_publish.services.product_prepare import ProductDataPrepareService


class DummyItem:
    id = 1
    job_id = "job-demo"
    jd_item_url = "https://item.jd.com/16793098028.html"
    product_name = "测试商品"
    brand = "公牛"
    model = "B5440"
    jd_sale_price = Decimal("70.00")
    purchase_price = Decimal("66.50")
    market_price = Decimal("82.35")
    length_mm = Decimal("250.00")
    width_mm = Decimal("76.00")
    height_mm = Decimal("42.00")
    weight_kg = Decimal("0.85")
    unit_name = "个"
    qualification_pdf_path = "docs/qualification.pdf"
    product_summary = "Excel摘要"
    remark = "需要优先上架"
    item_type = "single"


class DummyUploadRepo:
    def __init__(self, item=None):
        self.item = item or DummyItem()

    def get_job_item(self, job_item_id):
        if job_item_id == self.item.id:
            return self.item
        return None


class DummySnapshot:
    id = 99
    job_item_id = 1
    jd_item_url = DummyItem.jd_item_url
    jd_item_id = "16793098028"
    title = "京东商品标题"
    brand = "公牛"
    model = "B5440"
    price = Decimal("70.00")
    detail_html = "<div>详情HTML</div>"
    detail_text = "京东详情摘要"
    attributes_json = {
        "length_mm": "250.00",
        "width_mm": "76.00",
        "height_mm": "42.00",
        "weight_kg": "0.85",
        "unit_name": "个",
        "category_path": "工业品 > 低压电器 > 插座",
        "brand_name": "公牛",
    }
    source_payload_json = json.dumps(
        {
            "images": [
                "https://img14.360buyimg.com/n1/jfs/t1/sample-1.jpg",
                "https://img14.360buyimg.com/n1/jfs/t1/sample-2.jpg",
            ],
            "model": "B5440",
            "category_path": "工业品 > 低压电器 > 插座",
        },
        ensure_ascii=False,
    )


class DummySnapshotRepo:
    def __init__(self):
        self.created = []
        self.snapshot = DummySnapshot()

    def create_snapshot(self, **kwargs):
        record = type("Snapshot", (), {"id": 99, **kwargs})
        self.created.append(kwargs)
        return record

    def get_latest_by_job_item_id(self, job_item_id):
        if job_item_id == 1:
            return self.snapshot
        return None


class DummyRuntimeLogRepo:
    def __init__(self):
        self.logs = []

    def append_log(self, **kwargs):
        self.logs.append(kwargs)
        return kwargs


class DummyImageRepo:
    def __init__(self, images=None):
        self.images = images or []

    def list_images_by_job_item(self, job_item_id):
        return self.images if job_item_id == 1 else []


class LiveFetchJDProductFetchService(JDProductFetchService):
    def _fetch_page_html(self, jd_item_url: str) -> str:
        return """
        <html>
          <head>
            <title>贝亲（Pigeon）桃叶精华 婴儿液体爽身露 四季通用 200ml IA171【图片 价格 品牌 评论】-京东</title>
          </head>
          <body>
            <div class="summary-price-wrap">
              <span class="p-price"><span>￥</span><span class="price">49.00</span></span>
            </div>
            <div>母婴 &gt; 婴童洗护 &gt; 婴童护肤</div>
            <div>贝亲（Pigeon）京东自营旗舰店</div>
            <div>商品介绍</div>
            <div>适合婴幼儿日常护理</div>
            <div>商品参数</div>
            <img src="https://img14.360buyimg.com/n1/jfs/t1/sample-1.jpg" />
            <img data-origin="https://img14.360buyimg.com/n1/jfs/t1/sample-2.jpg" />
          </body>
        </html>
        """


class FallbackFetchJDProductFetchService(JDProductFetchService):
    def _fetch_page_html(self, jd_item_url: str) -> str:
        return """
        <html>
          <head><title>京东登录注册</title></head>
          <body><div>登录后继续</div></body>
        </html>
        """


def test_extract_jd_item_id():
    assert JDProductFetchService.extract_jd_item_id("https://item.jd.com/16793098028.html") == "16793098028"


def test_build_snapshot_for_job_item():
    upload_repo = DummyUploadRepo()
    snapshot_repo = DummySnapshotRepo()
    log_repo = DummyRuntimeLogRepo()
    service = FallbackFetchJDProductFetchService(upload_repo, snapshot_repo, log_repo)

    snapshot = service.build_snapshot_for_job_item(1)

    assert snapshot.id == 99
    assert snapshot_repo.created[0]["jd_item_id"] == "16793098028"
    assert snapshot_repo.created[0]["title"] == "测试商品"
    assert snapshot_repo.created[0]["attributes_json"]["length_mm"] == "250.00"
    assert log_repo.logs[0]["job_item_id"] == 1


def test_build_snapshot_for_job_item_prefers_live_payload():
    upload_repo = DummyUploadRepo()
    snapshot_repo = DummySnapshotRepo()
    log_repo = DummyRuntimeLogRepo()
    service = LiveFetchJDProductFetchService(upload_repo, snapshot_repo, log_repo)

    service.build_snapshot_for_job_item(1)

    assert snapshot_repo.created[0]["title"] == "贝亲（Pigeon）桃叶精华 婴儿液体爽身露 四季通用 200ml IA171"
    assert snapshot_repo.created[0]["brand"] == "贝亲（Pigeon）"
    assert snapshot_repo.created[0]["model"] == "IA171"
    assert snapshot_repo.created[0]["price"] == Decimal("49.00")
    source_payload = snapshot_repo.created[0]["source_payload_json"]
    assert "sample-1.jpg" in source_payload
    assert "live_price_not_extracted" not in source_payload


def test_prepare_product_data_uses_snapshot_fallback_and_local_images():
    item = DummyItem()
    item.product_summary = None
    item.brand = None
    item.purchase_price = None
    item.market_price = None
    item.unit_name = None
    upload_repo = DummyUploadRepo(item=item)
    snapshot_repo = DummySnapshotRepo()
    log_repo = DummyRuntimeLogRepo()
    image_repo = DummyImageRepo(
        images=[
            type(
                "ImageRecord",
                (),
                {
                    "image_role": "main",
                    "image_source_url": "https://img14.360buyimg.com/n1/jfs/t1/sample-1.jpg",
                    "image_local_path": "logs/images/main.png",
                    "image_format": "png",
                    "image_width": 800,
                    "image_height": 800,
                    "is_valid": 1,
                },
            )()
        ]
    )
    service = ProductDataPrepareService(upload_repo, snapshot_repo, log_repo, image_repo=image_repo)

    prepared = service.prepare_for_job_item(1)

    assert prepared.product_name == "测试商品"
    assert prepared.brand == "公牛"
    assert prepared.model == "B5440"
    assert prepared.jd_sale_price == Decimal("70.00")
    assert prepared.purchase_price == Decimal("66.50")
    assert prepared.market_price == Decimal("82.35")
    assert prepared.unit_name == "个"
    assert prepared.product_summary == "京东详情摘要"
    assert prepared.category_path == "工业品 > 低压电器 > 插座"
    assert prepared.detail_html == "<div>详情HTML</div>"
    assert prepared.qualification_pdf_path == "docs/qualification.pdf"
    assert prepared.remark == "需要优先上架"
    assert prepared.images[0].local_path == "logs/images/main.png"
    assert prepared.images[0].role == "main"
    assert prepared.length_mm == Decimal("250.00")
    assert prepared.weight_kg == Decimal("0.85")
    assert log_repo.logs[0]["job_item_id"] == 1


def test_prepare_product_data_falls_back_to_payload_images_and_price_rules():
    item = DummyItem()
    item.purchase_price = None
    item.market_price = None
    upload_repo = DummyUploadRepo(item=item)
    snapshot_repo = DummySnapshotRepo()
    snapshot_repo.snapshot.price = Decimal("88.00")
    log_repo = DummyRuntimeLogRepo()
    service = ProductDataPrepareService(upload_repo, snapshot_repo, log_repo, image_repo=DummyImageRepo())

    prepared = service.prepare_for_job_item(1)

    assert len(prepared.images) == 2
    assert prepared.images[0].role == "main"
    assert prepared.images[1].role == "detail"
    assert prepared.purchase_price == Decimal("66.50")
    assert prepared.market_price == Decimal("82.35")
