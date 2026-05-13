import time
from typing import Any, Callable, Dict, List


def run_pricing_section(
    product: Dict[str, Any],
    *,
    locator=None,
    log=None,
    append_results: Callable[[list[Dict[str, Any]], Any, str], None],
    fill_pricing: Callable[..., List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    if any(product.get(field) not in (None, "") for field in ("market_price", "purchase_price", "jd_price")):
        append_results(results, fill_pricing(product, locator=locator, log=log), "pricing")
        time.sleep(0.3)
    return results

