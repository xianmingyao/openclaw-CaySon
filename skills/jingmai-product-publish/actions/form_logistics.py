from typing import Any, Callable, Dict, List, Optional


def run_logistics_section(
    product: Dict[str, Any],
    *,
    locator=None,
    log=None,
    active_required_visual_fields=None,
    explicit_fields: Optional[set[str]] = None,
    append_results: Callable[[list[Dict[str, Any]], Any, str], None],
    fill_logistics: Callable[..., Any],
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    append_results(
        results,
        fill_logistics(
            product,
            required_visual_fields=active_required_visual_fields,
            locator=locator,
            log=log,
            explicit_fields=explicit_fields or set(),
        ),
        "logistics",
    )
    return results
