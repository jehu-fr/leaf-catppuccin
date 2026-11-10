#!/usr/bin/env python3
"""Generate Catppuccin themes for leaf.

The source of truth is ``src/palette.json`` (the official Catppuccin palette)
and ``src/template.toml`` (a 99-key leaf theme template).  Generated files in
``themes/`` are checked in so users do not need Python to install a theme.

Examples
--------
Generate one theme to stdout::

    python3 scripts/generate.py --flavor mocha --accent blue

Install it directly into leaf's theme directory::

    python3 scripts/generate.py --flavor mocha --accent blue --install

Regenerate every committed theme::

    python3 scripts/generate.py --all

Verify that committed themes match the generator::

    python3 scripts/generate.py --check
"""

from __future__ import annotations

import argparse
import json
import os
import re
import string
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PALETTE_PATH = ROOT / "src" / "palette.json"
TEMPLATE_PATH = ROOT / "src" / "template.toml"
THEMES_DIR = ROOT / "themes"
ACCENTS_DIR = THEMES_DIR / "accents"
VERSION = "1.1.0"

FLAVOR_SLUGS = ["latte", "frappe", "macchiato", "mocha"]
ACCENTS = [
    "rosewater",
    "flamingo",
    "pink",
    "mauve",
    "red",
    "maroon",
    "peach",
    "yellow",
    "green",
    "teal",
    "sky",
    "sapphire",
    "blue",
    "lavender",
]
ACCENT_NAMES = {
    "rosewater": "Rosewater",
    "flamingo": "Flamingo",
    "pink": "Pink",
    "mauve": "Mauve",
    "red": "Red",
    "maroon": "Maroon",
    "peach": "Peach",
    "yellow": "Yellow",
    "green": "Green",
    "teal": "Teal",
    "sky": "Sky",
    "sapphire": "Sapphire",
    "blue": "Blue",
    "lavender": "Lavender",
    "custom": "Custom",
}

# Keys whose values are allowed to differ between accent variants of a flavor.
ACCENT_DRIVEN_KEYS = {
    ("ui", "scrollbar_hover"),
    ("ui", "status_brand_bg"),
    ("ui", "status_brand_fg"),
    ("ui", "status_percent_fg"),
    ("ui", "toc_accent"),
    ("ui", "toc_primary_active"),
    ("markdown", "blockquote_marker"),
    ("markdown", "list_level_1"),
    ("markdown", "table_header"),
    ("markdown", "heading_1"),
    ("markdown", "latex_inline_fg"),
    ("markdown", "latex_inline_bg"),
    ("markdown", "latex_block_fg"),
    ("markdown", "mermaid_keyword"),
    ("markdown", "alert_important"),
    ("diff", "tree_active"),
}


def load_palette() -> dict:
    return json.loads(PALETTE_PATH.read_text(encoding="utf-8"))


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "".join(f"{channel:02x}" for channel in rgb)


def blend(fg: str, bg: str, fg_weight: float) -> str:
    """Blend *fg* over *bg*; *fg_weight* is 0..1."""
    fg_rgb = hex_to_rgb(fg)
    bg_rgb = hex_to_rgb(bg)
    return rgb_to_hex(
        tuple(
            round(f * fg_weight + b * (1.0 - fg_weight))
            for f, b in zip(fg_rgb, bg_rgb)
        )
    )


def relative_luminance(value: str) -> float:
    channels = []
    for channel in hex_to_rgb(value):
        channel /= 255.0
        channels.append(
            channel / 12.92
            if channel <= 0.03928
            else ((channel + 0.055) / 1.055) ** 2.4
        )
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast(a: str, b: str) -> float:
    la = relative_luminance(a)
    lb = relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def readable_on(fg: str, bg: str, target: str, minimum: float = 3.0) -> str:
    """Darken/lighten *fg* toward *target* until it reaches *minimum* contrast."""
    for step in range(0, 101, 5):
        candidate = blend(fg, target, 1.0 - step / 100.0)
        if contrast(candidate, bg) >= minimum:
            return candidate
    return target


def best_on(bg: str, candidates: list[str]) -> str:
    return max(candidates, key=lambda candidate: contrast(candidate, bg))


def theme_filename(flavor: str, accent: str) -> str:
    if accent == "mauve":
        return f"catppuccin-{flavor}.toml"
    return f"catppuccin-{flavor}-{accent}.toml"


def theme_path(flavor: str, accent: str) -> Path:
    if accent == "mauve":
        return THEMES_DIR / theme_filename(flavor, accent)
    return ACCENTS_DIR / theme_filename(flavor, accent)


def build_context(flavor: str, accent: str, accent_hex: str | None = None) -> dict[str, str]:
    palette = load_palette()
    if flavor not in palette["flavors"]:
        raise ValueError(f"Unknown flavor: {flavor}")
    if accent not in ACCENT_NAMES:
        raise ValueError(f"Unknown accent: {accent}")

    flavor_data = palette["flavors"][flavor]
    colors = flavor_data["colors"]
    dark = bool(flavor_data["dark"])

    if accent_hex is None:
        accent_value = colors[accent].lstrip("#")
    else:
        accent_value = accent_hex.lstrip("#")
        if len(accent_value) != 6 or any(
            c not in "0123456789abcdefABCDEF" for c in accent_value
        ):
            raise ValueError(f"Invalid accent hex: {accent_hex}")
        accent_value = accent_value.lower()

    base = colors["base"].lstrip("#")
    mantle = colors["mantle"].lstrip("#")
    crust = colors["crust"].lstrip("#")
    surface0 = colors["surface0"].lstrip("#")
    surface1 = colors["surface1"].lstrip("#")
    surface2 = colors["surface2"].lstrip("#")
    text = colors["text"].lstrip("#")
    green = colors["green"].lstrip("#")
    yellow = colors["yellow"].lstrip("#")
    red = colors["red"].lstrip("#")
    peach = colors["peach"].lstrip("#")
    sapphire = colors["sapphire"].lstrip("#")

    green18 = blend(green, base, 0.18)
    green35 = blend(green, base, 0.35)
    yellow18 = blend(yellow, base, 0.18)
    yellow22 = blend(yellow, base, 0.22)
    yellow35 = blend(yellow, base, 0.35)
    red18 = blend(red, base, 0.18)
    red35 = blend(red, base, 0.35)
    accent18 = blend(accent_value, base, 0.18)

    if dark:
        status_brand_bg = accent_value
        status_brand_fg = best_on(status_brand_bg, [crust, base, text])
        status_reloaded_bg = green
        status_reloaded_fg = best_on(status_reloaded_bg, [crust, base, text])
        status_watch_fg = green
        status_success_fg = green
        status_search_fg = yellow
        status_warning_fg = yellow
        status_error_fg = red
        inline_code_fg = peach
        ordered_list = peach
        hunk_header_fg = peach
        heading_4 = green
        task_checked = green
        alert_tip = green
        alert_warning = yellow
        tree_tag_change = yellow
        link_icon = sapphire
        footnote_ref = sapphire
        meta_note_sigil_fg = sapphire
        link_hover = colors["sky"].lstrip("#")
        link_hover_name = "Sky"
        strong_text = colors["rosewater"].lstrip("#")
        strong_text_name = "Rosewater"
        mark_fg = base
        mark_fg_name = "Base"
        mark_bg = yellow
        mark_bg_name = "Yellow"
        add_fg = green
        del_fg = red
        accent_on_base = accent_value
        accent_on_mantle = accent_value
        accent_on_surface0 = accent_value
        accent_on_latex_bg = accent_value
        status_percent_fg = accent_value
        toc_accent = accent_value
        toc_primary_active = accent_value
        table_header = accent_value
        heading_1 = accent_value
        latex_inline_fg = accent_value
        latex_block_fg = accent_value
        mermaid_keyword = accent_value
        alert_important = accent_value
        tree_active = accent_value
    else:
        # Latte: keep the palette, but nudge low-contrast foregrounds until
        # they are readable on their tinted backgrounds.
        status_brand_bg = accent_value
        status_brand_fg = best_on(status_brand_bg, [base, text, crust])
        status_reloaded_bg = green
        status_reloaded_fg = best_on(status_reloaded_bg, [base, text, crust])
        status_watch_fg = readable_on(green, green18, text, 3.0)
        status_success_fg = readable_on(green, green18, text, 3.0)
        status_search_fg = readable_on(yellow, yellow18, text, 3.0)
        status_warning_fg = readable_on(yellow, mantle, text, 3.0)
        status_error_fg = red
        inline_code_fg = readable_on(peach, surface0, text, 4.5)
        ordered_list = readable_on(peach, base, text, 3.0)
        hunk_header_fg = readable_on(peach, base, text, 3.0)
        heading_4 = readable_on(green, base, text, 3.0)
        task_checked = readable_on(green, base, text, 3.0)
        alert_tip = readable_on(green, base, text, 3.0)
        alert_warning = readable_on(yellow, base, text, 3.0)
        tree_tag_change = readable_on(yellow, base, text, 3.0)
        link_icon = readable_on(sapphire, base, text, 3.0)
        footnote_ref = readable_on(sapphire, base, text, 3.0)
        meta_note_sigil_fg = readable_on(sapphire, surface0, text, 3.0)
        link_hover = colors["blue"].lstrip("#")
        link_hover_name = "Blue"
        strong_text = text
        strong_text_name = "Text"
        mark_fg = text
        mark_fg_name = "Text"
        mark_bg = yellow35
        mark_bg_name = "Yellow 35% over Base"
        add_fg = readable_on(green, green18, text, 4.5)
        del_fg = readable_on(red, red18, text, 4.5)
        accent_on_base = readable_on(accent_value, base, text, 3.0)
        accent_on_mantle = readable_on(accent_value, mantle, text, 3.0)
        accent_on_surface0 = readable_on(accent_value, surface0, text, 3.0)
        accent_on_latex_bg = readable_on(accent_value, accent18, text, 4.5)
        status_percent_fg = accent_on_mantle
        toc_accent = accent_on_mantle
        toc_primary_active = accent_on_surface0
        table_header = accent_on_base
        heading_1 = accent_on_base
        latex_inline_fg = accent_on_latex_bg
        latex_block_fg = accent_on_base
        mermaid_keyword = accent_on_base
        alert_important = accent_on_base
        tree_active = accent_on_base

    context: dict[str, str] = {
        "version": VERSION,
        "flavor_name": flavor_data["name"],
        "flavor_slug": flavor,
        "accent_name": ACCENT_NAMES[accent],
        "accent_slug": accent,
        "accent": accent_value,
        "accent_hex": f"#{accent_value}",
        "base_preset": "ocean" if dark else "arctic",
        "syntax": "base16-ocean.dark" if dark else "base16-ocean.light",
        "base": base,
        "mantle": mantle,
        "crust": crust,
        "surface0": surface0,
        "surface1": surface1,
        "surface2": surface2,
        "overlay0": colors["overlay0"].lstrip("#"),
        "overlay1": colors["overlay1"].lstrip("#"),
        "overlay2": colors["overlay2"].lstrip("#"),
        "subtext0": colors["subtext0"].lstrip("#"),
        "subtext1": colors["subtext1"].lstrip("#"),
        "text": text,
        "rosewater": colors["rosewater"].lstrip("#"),
        "flamingo": colors["flamingo"].lstrip("#"),
        "pink": colors["pink"].lstrip("#"),
        "mauve": colors["mauve"].lstrip("#"),
        "red": colors["red"].lstrip("#"),
        "maroon": colors["maroon"].lstrip("#"),
        "peach": colors["peach"].lstrip("#"),
        "yellow": colors["yellow"].lstrip("#"),
        "green": green,
        "teal": colors["teal"].lstrip("#"),
        "sky": colors["sky"].lstrip("#"),
        "sapphire": sapphire,
        "blue": colors["blue"].lstrip("#"),
        "lavender": colors["lavender"].lstrip("#"),
        "search_highlight_bg": yellow22,
        "search_match_bg": yellow35,
        "green18": green18,
        "green35": green35,
        "yellow18": yellow18,
        "yellow22": yellow22,
        "yellow35": yellow35,
        "red18": red18,
        "red35": red35,
        "accent18": accent18,
        "status_brand_fg": status_brand_fg,
        "status_reloaded_fg": status_reloaded_fg,
        "status_watch_fg": status_watch_fg,
        "status_success_fg": status_success_fg,
        "status_search_fg": status_search_fg,
        "status_warning_fg": status_warning_fg,
        "status_error_fg": status_error_fg,
        "status_percent_fg": status_percent_fg,
        "toc_accent": toc_accent,
        "toc_primary_active": toc_primary_active,
        "table_header": table_header,
        "heading_1": heading_1,
        "heading_4": heading_4,
        "inline_code_fg": inline_code_fg,
        "ordered_list": ordered_list,
        "hunk_header_fg": hunk_header_fg,
        "task_checked": task_checked,
        "alert_tip": alert_tip,
        "alert_warning": alert_warning,
        "tree_tag_change": tree_tag_change,
        "link_icon": link_icon,
        "footnote_ref": footnote_ref,
        "meta_note_sigil_fg": meta_note_sigil_fg,
        "link_hover": link_hover,
        "link_hover_name": link_hover_name,
        "strong_text": strong_text,
        "strong_text_name": strong_text_name,
        "mark_fg": mark_fg,
        "mark_fg_name": mark_fg_name,
        "mark_bg": mark_bg,
        "mark_bg_name": mark_bg_name,
        "add_fg": add_fg,
        "del_fg": del_fg,
        "latex_inline_fg": latex_inline_fg,
        "latex_inline_bg": accent18,
        "latex_block_fg": latex_block_fg,
        "mermaid_keyword": mermaid_keyword,
        "alert_important": alert_important,
        "tree_active": tree_active,
    }
    return context


COMMENT_COLUMN = 40
COMMENT_LINE = re.compile(r'^(?P<body>\s*[A-Za-z0-9_]+ = "[^"]*")\s+(?P<comment>#.*)$')


def align_comments(text: str) -> str:
    """Line up trailing comments at a consistent column."""
    lines = []
    for line in text.splitlines():
        match = COMMENT_LINE.match(line)
        if match:
            body = match.group("body")
            comment = match.group("comment")
            padding = max(1, COMMENT_COLUMN - len(body))
            line = body + " " * padding + comment
        lines.append(line)
    return "\n".join(lines) + "\n"


def render_theme(flavor: str, accent: str, accent_hex: str | None = None) -> str:
    template = string.Template(TEMPLATE_PATH.read_text(encoding="utf-8"))
    return align_comments(template.substitute(build_context(flavor, accent, accent_hex)))


def expected_themes() -> list[tuple[str, str, Path]]:
    themes: list[tuple[str, str, Path]] = []
    for flavor in FLAVOR_SLUGS:
        for accent in ACCENTS:
            themes.append((flavor, accent, theme_path(flavor, accent)))
    return themes


def command_all() -> int:
    for flavor, accent, path in expected_themes():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_theme(flavor, accent), encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


def command_check() -> int:
    failures = 0
    expected_paths = set()
    for flavor, accent, path in expected_themes():
        expected_paths.add(path)
        expected = render_theme(flavor, accent)
        if not path.exists():
            print(f"missing: {path.relative_to(ROOT)}")
            failures += 1
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            print(f"out of date: {path.relative_to(ROOT)}")
            failures += 1

    for directory in (THEMES_DIR, ACCENTS_DIR):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.toml")):
            if path not in expected_paths:
                print(f"unexpected theme: {path.relative_to(ROOT)}")
                failures += 1

    if failures:
        print(f"{failures} theme file(s) need attention")
        return 1
    print(f"all {len(expected_paths)} theme files are up to date")
    return 0


def command_install(flavor: str, accent: str, accent_hex: str | None) -> int:
    content = render_theme(flavor, accent, accent_hex)
    filename = theme_filename(flavor, accent)
    config_home = Path(
        os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
    ).expanduser()
    target_dir = config_home / "leaf" / "themes"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / filename
    target.write_text(content, encoding="utf-8")
    stem = target.stem
    print(f"installed {target}")
    print(f'select it with: theme = "{stem}"')
    return 0


def command_list() -> int:
    palette = load_palette()
    print("flavors:")
    for flavor in FLAVOR_SLUGS:
        data = palette["flavors"][flavor]
        print(f"  {flavor:<10} {data['name']}")
    print("accents:")
    for accent in ACCENTS:
        print(f"  {accent:<10} {ACCENT_NAMES[accent]}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Catppuccin themes for leaf.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--flavor", choices=FLAVOR_SLUGS, help="flavor to generate")
    parser.add_argument(
        "--accent",
        choices=ACCENTS,
        default=None,
        help="accent name (default: mauve)",
    )
    parser.add_argument(
        "--accent-hex",
        metavar="HEX",
        help="custom accent color, e.g. #b4befe (implies --accent custom)",
    )
    parser.add_argument("--output", type=Path, help="write the theme to this path")
    parser.add_argument(
        "--install",
        action="store_true",
        help="install into $XDG_CONFIG_HOME/leaf/themes",
    )
    parser.add_argument("--all", action="store_true", help="regenerate every theme")
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify committed themes match the generator",
    )
    parser.add_argument("--list", action="store_true", help="list flavors and accents")
    parser.add_argument("--version", action="version", version=VERSION)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    if args.list:
        return command_list()
    if args.check:
        return command_check()
    if args.all:
        return command_all()

    if not args.flavor:
        print("error: --flavor is required unless --all, --check, or --list is used", file=sys.stderr)
        return 2

    accent = args.accent or ("custom" if args.accent_hex else "mauve")
    if args.accent_hex and args.accent not in (None, "mauve"):
        print("error: use either --accent or --accent-hex, not both", file=sys.stderr)
        return 2

    if args.install:
        return command_install(args.flavor, accent, args.accent_hex)

    content = render_theme(args.flavor, accent, args.accent_hex)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        sys.stdout.write(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
