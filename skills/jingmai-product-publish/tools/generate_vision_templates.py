"""
Generate lightweight vision fallback templates from v1 screenshots.

Only stable, layout-level controls are templated here:
- category next button
- publish button
- save draft button
- popup close button

Option-like dropdown items remain UIA-first because they vary too much by data.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
V1_LOGS = ROOT.parent / "jingmai-product-publish-v1" / "logs"
OUT_DIR = ROOT / "resources" / "screenshots" / "templates"


@dataclass(frozen=True)
class CropSpec:
    source: str
    box: tuple[int, int, int, int]
    target: str
    note: str


CROPS = [
    CropSpec(
        source="after_next_click.png",
        box=(1148, 1274, 1406, 1341),
        target="category_next_button.png",
        note="Category page next button.",
    ),
    CropSpec(
        source="s2_brand_dropdown.png",
        box=(1160, 1334, 1268, 1391),
        target="publish_button.png",
        note="Publish button on product form.",
    ),
    CropSpec(
        source="s2_brand_dropdown.png",
        box=(1274, 1334, 1395, 1391),
        target="save_draft_button.png",
        note="Save draft button on product form.",
    ),
    CropSpec(
        source="close_popup.png",
        box=(2454, 169, 2541, 242),
        target="popup_close_button.png",
        note="Popup close icon in top-right overlay.",
    ),
    CropSpec(
        source="03_market_price.png",
        box=(608, 632, 730, 674),
        target="market_price_label.png",
        note="Market price field label on product form.",
    ),
    CropSpec(
        source="02_jd_price.png",
        box=(1408, 632, 1528, 674),
        target="jd_price_label.png",
        note="JD price field label on product form.",
    ),
    CropSpec(
        source="03_market_price.png",
        box=(614, 389, 726, 427),
        target="product_title_label.png",
        note="Product title field label on product form.",
    ),
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = []

    for spec in CROPS:
        source_path = V1_LOGS / spec.source
        if not source_path.exists():
            print(f"skip missing source: {source_path}")
            continue

        image = Image.open(source_path)
        cropped = image.crop(spec.box)
        out_path = OUT_DIR / spec.target
        cropped.save(out_path)
        generated.append((spec.target, cropped.size, spec.note))

    if not generated:
        print("no templates generated")
        return 1

    print("generated templates:")
    for name, size, note in generated:
        print(f"- {name}: {size[0]}x{size[1]} | {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
