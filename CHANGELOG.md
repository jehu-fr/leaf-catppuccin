# Changelog

## Unreleased

- Fixed the README previews showing dark horizontal gaps between terminal lines by replacing `termshot` with `freeze`, which paints ANSI backgrounds for the full line pitch.
- Added `scripts/preview.py` and `scripts/requirements-preview.txt` so the previews can be regenerated reproducibly without touching the live leaf configuration.

## 1.1.0 - 2026-11-09

- Added **Latte**, **Macchiato**, and **Mocha** alongside Frappé.
- Added all **14 Catppuccin accents** for every flavor: 56 themes total.
- Kept `catppuccin-frappe` as the backward-compatible Mauve Frappé theme; its colors are identical to 1.0.0.
- Added `scripts/generate.py` with `--flavor`, `--accent`, `--accent-hex`, `--output`, `--install`, `--all`, `--check`, and `--list`.
- Added `scripts/check.py` for schema, hex, flavor-preset, accent-isolation, and contrast validation.
- Added `scripts/assets.py` for the accent grid and combined palette card.
- Added targeted Latte readability fixes for inline code, link hover, status foregrounds, marks, diff foregrounds, and accent roles.
- Added four real leaf previews, a 4×14 accent grid, and a combined 4-flavor palette card.
- Added `docs/ACCENTS.md`, `themes/README.md`, and a GitHub Actions validation workflow.
- Added `src/palette.json` (official Catppuccin palette v1.8.0) and `src/template.toml` as the theme source of truth.

## 1.0.0 - 2026-11-08

- Initial release of the Catppuccin Frappé theme for leaf.
- Mauve accent across UI, Markdown, and diff views.
- Full 99-key theme coverage.
