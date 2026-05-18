from decimal import Decimal

from jingmai_publish.services.excel_ingest import ExcelIngestService


def test_price_calculation_rules():
    jd_price = Decimal("100.00")
    assert ExcelIngestService.calculate_purchase_price(jd_price) == Decimal("95.00")
    assert ExcelIngestService.calculate_market_price(jd_price) == Decimal("117.65")
