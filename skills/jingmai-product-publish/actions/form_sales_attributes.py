from typing import Any, Callable, Dict, List, Optional


def run_sales_attribute_sections(
    product: Dict[str, Any],
    *,
    locator=None,
    log=None,
    active_required_visual_fields=None,
    explicit_fields: Optional[set[str]] = None,
    append_results: Callable[[list[Dict[str, Any]], Any, str], None],
    fill_supported_attributes: Callable[..., Any],
    fill_sales_attributes: Callable[..., Any],
    fill_sku_images: Callable[..., Any],
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    explicit_fields = explicit_fields or set()

    append_results(results, fill_supported_attributes(product, locator=locator, log=log), "attributes")
    append_results(
        results,
        fill_sales_attributes(
            product,
            required_visual_fields=active_required_visual_fields,
            locator=locator,
            log=log,
            explicit_fields=explicit_fields,
        ),
        "sales_attributes",
    )
    append_results(
        results,
        fill_sku_images(
            product,
            required_visual_fields=active_required_visual_fields,
            locator=locator,
            log=log,
            explicit_fields=explicit_fields,
        ),
        "sku_images",
    )
    return results

