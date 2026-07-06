# Jingmai Verified Action Strategy

Date: 2026-06-08

## Decision

Jingmai WebView fields must not be marked as filled after a blind click and keystroke. A
field is marked `FILLED` only after the verified action layer reports success.

## Action Ladder

1. Native control action: locate the field by automation id, focus it, and try UIA/Win32/WinCOM-style value setting.
2. WebView fallback: click the declared coordinate or automation id, paste through clipboard, then read focused text back. If readback fails, save a screenshot.
3. UFO-style low-level action: use the same lower-level action pattern observed in `E:\PY\UFO\ufo` directly in this project: validate the control, set focus, try `set_edit_text`, `set_text`, `type_keys`, and clipboard paste. This does not import or depend on UFO's own control classes.

## Field Config

Form plan fields can include a coordinate fallback for WebView-only controls:

```json
{
  "fields": {
    "title": {
      "automation_id": "title-input",
      "method": "chinese",
      "fallback_coord": {"x": 1000, "y": 438, "width": 500, "height": 32}
    }
  }
}
```

## Verification Rule

The action layer verifies by exact focused-text readback when possible. If readback is
unavailable or mismatched, it records a screenshot under `data/screenshots/verify_*`
and continues to the next action method. The caller receives failure if every method
fails, and the workflow must not set `FieldStatus.FILLED`.
