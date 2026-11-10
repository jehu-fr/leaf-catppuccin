#!/usr/bin/env python3
"""Validate the generated Catppuccin themes for leaf.

Checks
------
* Every expected theme file exists and no unexpected ``.toml`` files are
  committed under ``themes/``.
* Each theme has the exact leaf schema: 35 UI, 47 Markdown, and 17 Diff keys.
* Every color value is a lowercase ``#rrggbb`` string.
* Flavor presets and syntax themes match the flavor.
* Accent variants only change the documented accent-driven keys.
* Key foreground/background pairs meet readability thresholds.

Run from the repository root::

    python3 scripts/check.py
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate import (  # noqa: E402
    ACCENTS,
    ACCENT_DRIVEN_KEYS,
    ACCENT_NAMES,
    FLAVOR_SLUGS,
    TEMPLATE_PATH,
    THEMES_DIR,
    ACCENTS_DIR,
    blend,
    contrast,
    expected_themes,
    load_palette,
)

HEX_RE = re.compile(r"^#[0-9a-f]{6}$")
SECTION_COUNTS = {"ui": 35, "markdown": 47, "diff": 17}
TOTAL_THEME_KEYS = sum(SECTION_COUNTS.values())
EXPECTED_TOP_LEVEL = {"base", "syntax"}
PRESETS = {
    "latte": ("arctic", "base16-ocean.light"),
    "frappe": ("ocean", "base16-ocean.dark"),
    "macchiato": ("ocean", "base16-ocean.dark"),
    "mocha": ("ocean", "base16-ocean.dark"),
}

# (foreground key, background key, dark minimum, light minimum, label)
CONTRAST_PAIRS = [
    ("markdown.text", "ui.content_bg", 4.5, 4.5, "body text"),
    ("markdown.blockquote_text", "ui.content_bg", 4.3, 4.3, "blockquote"),
    ("markdown.inline_code_fg", "markdown.inline_code_bg", 4.4, 4.5, "inline code"),
    ("markdown.link_text", "ui.content_bg", 4.3, 4.3, "link text"),
    ("markdown.link_hover", "ui.content_bg", 4.3, 4.3, "link hover"),
    ("markdown.strong_text", "ui.content_bg", 4.5, 4.5, "strong text"),
    ("markdown.mark_fg", "markdown.mark_bg", 4.5, 4.5, "mark"),
    ("markdown.latex_inline_fg", "markdown.latex_inline_bg", 3.5, 4.5, "latex inline"),
    ("markdown.table_cell", "ui.content_bg", 4.5, 4.5, "table cell"),
    ("ui.status_filename_fg", "ui.status_filename_bg", 4.5, 4.5, "status filename"),
    ("ui.status_brand_fg", "ui.status_brand_bg", 2.6, 2.6, "status brand"),
    ("ui.status_reloaded_fg", "ui.status_reloaded_bg", 2.9, 2.9, "status reloaded"),
    ("ui.status_watch_fg", "ui.status_watch_bg", 3.0, 3.0, "status watch"),
    ("ui.status_search_fg", "ui.status_search_bg", 3.0, 3.0, "status search"),
    ("ui.status_success_fg", "ui.status_success_bg", 3.0, 3.0, "status success"),
    ("ui.status_warning_fg", "ui.status_bg", 3.0, 3.0, "status warning"),
    ("ui.status_error_fg", "ui.status_error_bg", 3.0, 3.0, "status error"),
    ("ui.status_percent_fg", "ui.status_bg", 3.0, 3.0, "status percent"),
    ("ui.toc_accent", "ui.toc_inactive_bg", 3.0, 3.0, "toc accent"),
    ("ui.toc_primary_active", "ui.toc_active_bg", 3.0, 3.0, "toc primary active"),
    ("ui.toc_primary_inactive", "ui.toc_active_bg", 3.0, 3.0, "toc primary inactive"),
    ("markdown.heading_1", "ui.content_bg", 3.0, 3.0, "h1"),
    ("markdown.heading_2", "ui.content_bg", 3.0, 3.0, "h2"),
    ("markdown.heading_3", "ui.content_bg", 3.0, 3.0, "h3"),
    ("markdown.heading_4", "ui.content_bg", 3.0, 3.0, "h4"),
    ("markdown.ordered_list", "ui.content_bg", 3.0, 3.0, "ordered list"),
    ("markdown.task_checked", "ui.content_bg", 3.0, 3.0, "task checked"),
    ("markdown.alert_tip", "ui.content_bg", 3.0, 3.0, "alert tip"),
    ("markdown.alert_warning", "ui.content_bg", 3.0, 3.0, "alert warning"),
    ("markdown.footnote_ref", "ui.content_bg", 3.0, 3.0, "footnote ref"),
    ("markdown.link_icon", "ui.content_bg", 3.0, 3.0, "link icon"),
    ("markdown.mermaid_keyword", "ui.content_bg", 3.0, 3.0, "mermaid keyword"),
    ("markdown.latex_block_fg", "ui.content_bg", 3.0, 3.0, "latex block"),
    ("diff.add_fg", "diff.add_bg", 4.5, 4.5, "diff add"),
    ("diff.del_fg", "diff.del_bg", 3.5, 4.5, "diff del"),
    ("diff.context_fg", "ui.content_bg", 4.3, 4.3, "diff context"),
    ("diff.hunk_header_fg", "ui.content_bg", 3.0, 3.0, "hunk header"),
    ("diff.filename_fg", "ui.content_bg", 3.0, 3.0, "diff filename"),
    ("diff.tree_tag_change", "ui.content_bg", 3.0, 3.0, "tree tag change"),
    ("diff.meta_note_sigil_fg", "diff.meta_note_bg", 3.0, 3.0, "meta sigil"),
]


def flatten(theme: dict) -> dict[str, str]:
    flat: dict[str, str] = {}
    for section, values in theme.items():
        if isinstance(values, dict):
            for key, value in values.items():
                flat[f"{section}.{key}"] = value
        else:
            flat[section] = values
    return flat


def load_theme(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def main() -> int:
    failures: list[str] = []
    palette = load_palette()
    template = load_theme(TEMPLATE_PATH)

    expected_keys = {
        section: set(values) for section, values in template.items() if isinstance(values, dict)
    }
    for section, count in SECTION_COUNTS.items():
        if len(expected_keys.get(section, set())) != count:
            failures.append(
                f"template: {section} has {len(expected_keys.get(section, set()))} keys, expected {count}"
            )

    expected_paths = {path for _, _, path in expected_themes()}
    for path in sorted(expected_paths):
        if not path.exists():
            failures.append(f"missing theme: {path.relative_to(THEMES_DIR.parent)}")

    for directory in (THEMES_DIR, ACCENTS_DIR):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.toml")):
            if path not in expected_paths:
                failures.append(f"unexpected theme: {path.relative_to(THEMES_DIR.parent)}")

    themes: dict[tuple[str, str], dict[str, str]] = {}
    for flavor in FLAVOR_SLUGS:
        expected_base, expected_syntax = PRESETS[flavor]
        for accent in ACCENTS:
            path = next(p for f, a, p in expected_themes() if f == flavor and a == accent)
            if not path.exists():
                continue
            try:
                theme = load_theme(path)
            except tomllib.TOMLDecodeError as error:
                failures.append(f"{path.name}: invalid TOML: {error}")
                continue

            flat = flatten(theme)
            themes[(flavor, accent)] = flat

            top_level = {key for key in theme if not isinstance(theme[key], dict)}
            if top_level != EXPECTED_TOP_LEVEL:
                failures.append(
                    f"{path.name}: top-level keys {sorted(top_level)} != {sorted(EXPECTED_TOP_LEVEL)}"
                )

            for section, count in SECTION_COUNTS.items():
                actual = theme.get(section)
                if not isinstance(actual, dict):
                    failures.append(f"{path.name}: missing [{section}] section")
                    continue
                if len(actual) != count:
                    failures.append(
                        f"{path.name}: [{section}] has {len(actual)} keys, expected {count}"
                    )
                missing = expected_keys[section] - set(actual)
                extra = set(actual) - expected_keys[section]
                if missing:
                    failures.append(f"{path.name}: [{section}] missing {sorted(missing)}")
                if extra:
                    failures.append(f"{path.name}: [{section}] unexpected {sorted(extra)}")

            if theme.get("base") != expected_base:
                failures.append(
                    f"{path.name}: base {theme.get('base')!r} != {expected_base!r}"
                )
            if theme.get("syntax") != expected_syntax:
                failures.append(
                    f"{path.name}: syntax {theme.get('syntax')!r} != {expected_syntax!r}"
                )

            for key, value in flat.items():
                if key in EXPECTED_TOP_LEVEL:
                    continue
                if not isinstance(value, str) or not HEX_RE.match(value):
                    failures.append(f"{path.name}: {key} = {value!r} is not #rrggbb")

            colors = palette["flavors"][flavor]["colors"]
            accent_hex = colors[accent]
            if flat.get("ui.scrollbar_hover") != accent_hex:
                failures.append(
                    f"{path.name}: scrollbar_hover {flat.get('ui.scrollbar_hover')} != {accent_hex}"
                )
            if flat.get("ui.status_brand_bg") != accent_hex:
                failures.append(
                    f"{path.name}: status_brand_bg {flat.get('ui.status_brand_bg')} != {accent_hex}"
                )
            expected_latex_bg = "#" + blend(
                accent_hex.lstrip("#"), colors["base"].lstrip("#"), 0.18
            )
            if flat.get("markdown.latex_inline_bg") != expected_latex_bg:
                failures.append(
                    f"{path.name}: latex_inline_bg {flat.get('markdown.latex_inline_bg')} "
                    f"!= {expected_latex_bg}"
                )

    # Accent isolation: only the documented keys may differ between variants.
    for flavor in FLAVOR_SLUGS:
        baseline = themes.get((flavor, "mauve"))
        if baseline is None:
            continue
        for accent in ACCENTS:
            current = themes.get((flavor, accent))
            if current is None:
                continue
            for key in baseline:
                if key in {f"{section}.{name}" for section, name in ACCENT_DRIVEN_KEYS}:
                    continue
                if baseline[key] != current[key]:
                    failures.append(
                        f"{flavor}/{accent}: non-accent key {key} differs from Mauve"
                    )

    # Contrast checks.
    for flavor in FLAVOR_SLUGS:
        is_dark = bool(palette["flavors"][flavor]["dark"])
        for accent in ACCENTS:
            flat = themes.get((flavor, accent))
            if flat is None:
                continue
            for fg_key, bg_key, dark_min, light_min, label in CONTRAST_PAIRS:
                minimum = dark_min if is_dark else light_min
                fg = flat.get(fg_key)
                bg = flat.get(bg_key)
                if not fg or not bg:
                    failures.append(f"{flavor}/{accent}: missing contrast pair {label}")
                    continue
                ratio = contrast(fg.lstrip("#"), bg.lstrip("#"))
                if ratio + 1e-9 < minimum:
                    failures.append(
                        f"{flavor}/{accent}: {label} {ratio:.2f} < {minimum} "
                        f"({fg} on {bg})"
                    )

    if failures:
        print(f"{len(failures)} check(s) failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        f"ok: {len(themes)} themes, {TOTAL_THEME_KEYS} keys each, "
        f"{len(ACCENTS)} accents, {len(FLAVOR_SLUGS)} flavors"
    )
    print(f"ok: {len(CONTRAST_PAIRS)} contrast pairs checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
