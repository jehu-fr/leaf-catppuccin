#!/usr/bin/env python3
"""Generate the SVG assets used by the README.

Run from the repository root::

    python3 scripts/assets.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate import ACCENTS, ACCENT_NAMES, FLAVOR_SLUGS, contrast, load_palette  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONT = "ui-sans-serif, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
COLOR_ORDER = [
    "rosewater", "flamingo", "pink", "mauve", "red", "maroon", "peach",
    "yellow", "green", "teal", "sky", "sapphire", "blue", "lavender",
    "text", "subtext1", "subtext0", "overlay2", "overlay1", "overlay0",
    "surface2", "surface1", "surface0", "base", "mantle", "crust",
]
COLOR_NAMES = {
    "rosewater": "Rosewater", "flamingo": "Flamingo", "pink": "Pink",
    "mauve": "Mauve", "red": "Red", "maroon": "Maroon", "peach": "Peach",
    "yellow": "Yellow", "green": "Green", "teal": "Teal", "sky": "Sky",
    "sapphire": "Sapphire", "blue": "Blue", "lavender": "Lavender",
    "text": "Text", "subtext1": "Subtext 1", "subtext0": "Subtext 0",
    "overlay2": "Overlay 2", "overlay1": "Overlay 1", "overlay0": "Overlay 0",
    "surface2": "Surface 2", "surface1": "Surface 1", "surface0": "Surface 0",
    "base": "Base", "mantle": "Mantle", "crust": "Crust",
}


def readable_text(background: str, candidates: list[str]) -> str:
    return max(candidates, key=lambda color: contrast(color.lstrip("#"), background.lstrip("#")))


def accent_grid(palette: dict) -> str:
    width, height = 1440, 640
    x0, y0 = 40, 152
    label_width, cell_width, row_height = 104, 92, 104
    swatch_w, swatch_h = 78, 44
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Catppuccin accents for leaf</title>',
        '<desc id="desc">A 4 by 14 grid of Catppuccin accents for Latte, Frappé, Macchiato, and Mocha.</desc>',
        f'<rect width="{width}" height="{height}" fill="#11111b"/>',
        f'<text x="{x0}" y="62" fill="#cdd6f4" font-family="{FONT}" font-size="36" font-weight="700">Catppuccin accents for leaf</text>',
        f'<text x="{x0}" y="94" fill="#cba6f7" font-family="{FONT}" font-size="17" font-weight="600">14 accents × 4 flavors · Mauve is the default</text>',
        f'<text x="{x0}" y="122" fill="#6c7086" font-family="{FONT}" font-size="13">catppuccin-&lt;flavor&gt;.toml uses Mauve · catppuccin-&lt;flavor&gt;-&lt;accent&gt;.toml for the rest</text>',
    ]

    for index, accent in enumerate(ACCENTS):
        cx = x0 + label_width + index * cell_width + swatch_w / 2
        parts.append(
            f'<text x="{cx:.1f}" y="{y0 - 14}" fill="#a6adc8" font-family="{FONT}" '
            f'font-size="11" text-anchor="middle">{ACCENT_NAMES[accent]}</text>'
        )

    for row, flavor in enumerate(FLAVOR_SLUGS):
        data = palette["flavors"][flavor]
        colors = data["colors"]
        y = y0 + row * row_height
        parts.append(
            f'<text x="{x0}" y="{y + 20}" fill="{colors["text"]}" font-family="{FONT}" '
            f'font-size="19" font-weight="700">{data["name"]}</text>'
        )
        parts.append(
            f'<text x="{x0}" y="{y + 39}" fill="{colors["subtext0"]}" font-family="{FONT}" '
            f'font-size="11">{"light" if not data["dark"] else "dark"} · {colors["base"]}</text>'
        )
        for index, accent in enumerate(ACCENTS):
            accent_hex = colors[accent]
            x = x0 + label_width + index * cell_width
            text_color = readable_text(accent_hex, [colors["base"], colors["crust"], colors["text"]])
            parts.append(
                f'<g><title>{escape(data["name"])} {ACCENT_NAMES[accent]} {accent_hex}</title>'
                f'<rect x="{x}" y="{y}" width="{swatch_w}" height="{swatch_h}" rx="9" '
                f'fill="{accent_hex}" stroke="{colors["surface2"]}" stroke-width="1"/>'
                f'<text x="{x + swatch_w / 2:.1f}" y="{y + 27}" fill="{text_color}" '
                f'font-family="{MONO}" font-size="10" text-anchor="middle">{accent_hex}</text></g>'
            )

    parts.append(
        f'<text x="{x0}" y="{height - 26}" fill="#6c7086" font-family="{FONT}" font-size="12">'
        'github.com/jehu-fr/leaf-catppuccin · unofficial Catppuccin port for leaf</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def palette_card(palette: dict) -> str:
    width, height = 1600, 820
    panel_w, panel_h = 740, 316
    panel_x = [40, 820]
    panel_y = [132, 466]
    swatch_w, swatch_h = 90, 44
    cell_w, cell_h = 100, 54
    columns = 7
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Catppuccin palette for leaf</title>',
        '<desc id="desc">All 26 colors in the Latte, Frappé, Macchiato, and Mocha palettes.</desc>',
        f'<rect width="{width}" height="{height}" fill="#11111b"/>',
        f'<text x="40" y="58" fill="#cdd6f4" font-family="{FONT}" font-size="36" font-weight="700">Catppuccin palette for leaf</text>',
        f'<text x="40" y="90" fill="#cba6f7" font-family="{FONT}" font-size="17" font-weight="600">4 flavors × 26 colors · Mauve accent default</text>',
        f'<text x="40" y="116" fill="#6c7086" font-family="{FONT}" font-size="13">catppuccin.com/palette · unofficial port for leaf</text>',
    ]

    for index, flavor in enumerate(FLAVOR_SLUGS):
        data = palette["flavors"][flavor]
        colors = data["colors"]
        px = panel_x[index % 2]
        py = panel_y[index // 2]
        parts.append(
            f'<g><rect x="{px}" y="{py}" width="{panel_w}" height="{panel_h}" rx="14" '
            f'fill="{colors["base"]}" stroke="{colors["surface1"]}" stroke-width="1"/>'
            f'<text x="{px + 22}" y="{py + 38}" fill="{colors["text"]}" font-family="{FONT}" '
            f'font-size="24" font-weight="700">{data["name"]}</text>'
            f'<text x="{px + panel_w - 22}" y="{py + 38}" fill="{colors["mauve"]}" '
            f'font-family="{MONO}" font-size="12" text-anchor="end">Mauve {colors["mauve"]}</text>'
        )
        for color_index, color in enumerate(COLOR_ORDER):
            color_hex = colors[color]
            row, column = divmod(color_index, columns)
            x = px + 22 + column * cell_w
            y = py + 58 + row * cell_h
            text_color = readable_text(color_hex, [colors["base"], colors["crust"], colors["text"]])
            parts.append(
                f'<g><title>{escape(data["name"])} {COLOR_NAMES[color]} {color_hex}</title>'
                f'<rect x="{x}" y="{y}" width="{swatch_w}" height="{swatch_h}" rx="7" '
                f'fill="{color_hex}" stroke="{colors["surface2"]}" stroke-width="1"/>'
                f'<text x="{x + swatch_w / 2:.1f}" y="{y + 18}" fill="{text_color}" '
                f'font-family="{FONT}" font-size="10" font-weight="700" text-anchor="middle">{COLOR_NAMES[color]}</text>'
                f'<text x="{x + swatch_w / 2:.1f}" y="{y + 33}" fill="{text_color}" '
                f'font-family="{MONO}" font-size="8" text-anchor="middle">{color_hex}</text></g>'
            )
        parts.append("</g>")

    parts.append(
        f'<text x="40" y="{height - 26}" fill="#6c7086" font-family="{FONT}" font-size="12">'
        'github.com/jehu-fr/leaf-catppuccin · palette by the Catppuccin contributors (MIT)</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> int:
    palette = load_palette()
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "accents.svg").write_text(accent_grid(palette), encoding="utf-8")
    (ASSETS / "palette.svg").write_text(palette_card(palette), encoding="utf-8")
    print("wrote assets/accents.svg")
    print("wrote assets/palette.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
