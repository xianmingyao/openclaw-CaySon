import time
from typing import Any, Callable, Dict, List


def run_basic_info_section(
    product: Dict[str, Any],
    *,
    locator=None,
    log=None,
    append_results: Callable[[list[Dict[str, Any]], Any, str], None],
    fill_title: Callable[..., Dict[str, Any]],
    fill_procurement_erp: Callable[..., Dict[str, Any] | None],
    fill_model: Callable[..., Dict[str, Any]],
    fill_brand: Callable[..., Dict[str, Any]],
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    title = product.get("title")
    if title not in (None, ""):
        append_results(results, fill_title(str(title), locator=locator, log=log), "basic_info")
        time.sleep(0.3)

    procurement_erp_result = fill_procurement_erp(product, locator=locator, log=log)
    if procurement_erp_result:
        append_results(results, procurement_erp_result, "basic_info")
        time.sleep(0.2)

    model = product.get("model")
    if model not in (None, ""):
        append_results(results, fill_model(str(model), locator=locator, log=log), "basic_info")
        time.sleep(0.3)

    brand = product.get("brand")
    if brand not in (None, ""):
        append_results(results, fill_brand(str(brand), locator=locator, log=log), "basic_info")
        time.sleep(0.3)

    return results
