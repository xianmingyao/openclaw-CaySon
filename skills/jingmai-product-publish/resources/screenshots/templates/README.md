# Vision Templates

This folder stores small template images used by the lightweight vision fallback in `actions/`.

Current policy:
- Template only stable controls.
- Keep UIA as the primary path.
- Do not template every dropdown option or every page state.

Current templates:
- `category_next_button.png`
- `market_price_label.png`
- `jd_price_label.png`
- `product_title_label.png`
- `publish_button.png`
- `save_draft_button.png`
- `popup_close_button.png`

Generation:

```powershell
python tools\generate_vision_templates.py
```

Source screenshots come from `..\..\..\jingmai-product-publish-v1\logs\`.

If a template becomes stale:
1. Capture a fresh full-window screenshot at `2560x1392`
2. Update the crop box in `tools/generate_vision_templates.py`
3. Regenerate the template

Do not add data-specific templates such as a single brand option unless there is a proven repeated failure and no reliable UIA path.

Price-field exception:
- `market_price_label.png`
- `jd_price_label.png`
- `product_title_label.png`

These are layout labels, not data-specific values. They exist because the live price labels and page context are visually present but not reliably exposed in the UIA tree.
