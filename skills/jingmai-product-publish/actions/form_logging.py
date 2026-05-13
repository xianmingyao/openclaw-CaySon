import json
from typing import Any


def log_fill_event(log, section: str, event: str, **payload: Any) -> None:
    if not log:
        return
    body = {"section": section, "event": event, **payload}
    try:
        log.debug("[fill_structured] " + json.dumps(body, ensure_ascii=True, sort_keys=True, default=str))
    except Exception:
        pass

