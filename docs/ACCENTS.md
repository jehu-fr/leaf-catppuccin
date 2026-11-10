# Accent reference

Every Catppuccin flavor in this repository supports all 14 Catppuccin accents:

`rosewater`, `flamingo`, `pink`, `mauve`, `red`, `maroon`, `peach`, `yellow`, `green`, `teal`, `sky`, `sapphire`, `blue`, `lavender`.

Mauve is the default. The four unsuffixed files in `themes/` are the Mauve themes; every other accent is a separate file in `themes/accents/`.

```text
themes/catppuccin-latte.toml                  Latte + Mauve
themes/catppuccin-frappe.toml                 Frappé + Mauve
themes/catppuccin-macchiato.toml              Macchiato + Mauve
themes/catppuccin-mocha.toml                  Mocha + Mauve

themes/accents/catppuccin-latte-rosewater.toml
themes/accents/catppuccin-latte-flamingo.toml
...
themes/accents/catppuccin-mocha-lavender.toml
```

## Install an accent

leaf only scans the top level of `~/.config/leaf/themes/`. Copy the file directly into that directory; do not copy the `themes/accents/` folder itself.

```bash
mkdir -p ~/.config/leaf/themes
curl -fsSL https://raw.githubusercontent.com/jehu-fr/leaf-catppuccin/main/themes/accents/catppuccin-mocha-blue.toml \
  -o ~/.config/leaf/themes/catppuccin-mocha-blue.toml
```

```toml
# ~/.config/leaf/config.toml
theme = "catppuccin-mocha-blue"
```

Or select it for one file:

```bash
leaf --theme catppuccin-mocha-blue README.md
```

Or point leaf at the file directly:

```bash
leaf --theme ~/.config/leaf/themes/catppuccin-mocha-blue.toml README.md
```

The same pattern works for every flavor and accent:

```text
catppuccin-latte-<accent>
catppuccin-frappe-<accent>
catppuccin-macchiato-<accent>
catppuccin-mocha-<accent>
```

For Mauve, use the unsuffixed name:

```text
catppuccin-latte
catppuccin-frappe
catppuccin-macchiato
catppuccin-mocha
```

## Accent matrix

Each cell links to the theme file and shows the raw Catppuccin accent hex. Latte adjusts a few foreground roles for contrast; open the linked file to see the exact values.

| Accent | Latte | Frappé | Macchiato | Mocha |
| --- | --- | --- | --- | --- |
| Rosewater | [`#dc8a78`](../themes/accents/catppuccin-latte-rosewater.toml) | [`#f2d5cf`](../themes/accents/catppuccin-frappe-rosewater.toml) | [`#f4dbd6`](../themes/accents/catppuccin-macchiato-rosewater.toml) | [`#f5e0dc`](../themes/accents/catppuccin-mocha-rosewater.toml) |
| Flamingo | [`#dd7878`](../themes/accents/catppuccin-latte-flamingo.toml) | [`#eebebe`](../themes/accents/catppuccin-frappe-flamingo.toml) | [`#f0c6c6`](../themes/accents/catppuccin-macchiato-flamingo.toml) | [`#f2cdcd`](../themes/accents/catppuccin-mocha-flamingo.toml) |
| Pink | [`#ea76cb`](../themes/accents/catppuccin-latte-pink.toml) | [`#f4b8e4`](../themes/accents/catppuccin-frappe-pink.toml) | [`#f5bde6`](../themes/accents/catppuccin-macchiato-pink.toml) | [`#f5c2e7`](../themes/accents/catppuccin-mocha-pink.toml) |
| Mauve | [`#8839ef`](../themes/catppuccin-latte.toml) | [`#ca9ee6`](../themes/catppuccin-frappe.toml) | [`#c6a0f6`](../themes/catppuccin-macchiato.toml) | [`#cba6f7`](../themes/catppuccin-mocha.toml) |
| Red | [`#d20f39`](../themes/accents/catppuccin-latte-red.toml) | [`#e78284`](../themes/accents/catppuccin-frappe-red.toml) | [`#ed8796`](../themes/accents/catppuccin-macchiato-red.toml) | [`#f38ba8`](../themes/accents/catppuccin-mocha-red.toml) |
| Maroon | [`#e64553`](../themes/accents/catppuccin-latte-maroon.toml) | [`#ea999c`](../themes/accents/catppuccin-frappe-maroon.toml) | [`#ee99a0`](../themes/accents/catppuccin-macchiato-maroon.toml) | [`#eba0ac`](../themes/accents/catppuccin-mocha-maroon.toml) |
| Peach | [`#fe640b`](../themes/accents/catppuccin-latte-peach.toml) | [`#ef9f76`](../themes/accents/catppuccin-frappe-peach.toml) | [`#f5a97f`](../themes/accents/catppuccin-macchiato-peach.toml) | [`#fab387`](../themes/accents/catppuccin-mocha-peach.toml) |
| Yellow | [`#df8e1d`](../themes/accents/catppuccin-latte-yellow.toml) | [`#e5c890`](../themes/accents/catppuccin-frappe-yellow.toml) | [`#eed49f`](../themes/accents/catppuccin-macchiato-yellow.toml) | [`#f9e2af`](../themes/accents/catppuccin-mocha-yellow.toml) |
| Green | [`#40a02b`](../themes/accents/catppuccin-latte-green.toml) | [`#a6d189`](../themes/accents/catppuccin-frappe-green.toml) | [`#a6da95`](../themes/accents/catppuccin-macchiato-green.toml) | [`#a6e3a1`](../themes/accents/catppuccin-mocha-green.toml) |
| Teal | [`#179299`](../themes/accents/catppuccin-latte-teal.toml) | [`#81c8be`](../themes/accents/catppuccin-frappe-teal.toml) | [`#8bd5ca`](../themes/accents/catppuccin-macchiato-teal.toml) | [`#94e2d5`](../themes/accents/catppuccin-mocha-teal.toml) |
| Sky | [`#04a5e5`](../themes/accents/catppuccin-latte-sky.toml) | [`#99d1db`](../themes/accents/catppuccin-frappe-sky.toml) | [`#91d7e3`](../themes/accents/catppuccin-macchiato-sky.toml) | [`#89dceb`](../themes/accents/catppuccin-mocha-sky.toml) |
| Sapphire | [`#209fb5`](../themes/accents/catppuccin-latte-sapphire.toml) | [`#85c1dc`](../themes/accents/catppuccin-frappe-sapphire.toml) | [`#7dc4e4`](../themes/accents/catppuccin-macchiato-sapphire.toml) | [`#74c7ec`](../themes/accents/catppuccin-mocha-sapphire.toml) |
| Blue | [`#1e66f5`](../themes/accents/catppuccin-latte-blue.toml) | [`#8caaee`](../themes/accents/catppuccin-frappe-blue.toml) | [`#8aadf4`](../themes/accents/catppuccin-macchiato-blue.toml) | [`#89b4fa`](../themes/accents/catppuccin-mocha-blue.toml) |
| Lavender | [`#7287fd`](../themes/accents/catppuccin-latte-lavender.toml) | [`#babbf1`](../themes/accents/catppuccin-frappe-lavender.toml) | [`#b7bdf8`](../themes/accents/catppuccin-macchiato-lavender.toml) | [`#b4befe`](../themes/accents/catppuccin-mocha-lavender.toml) |

## What the accent controls

Only the following keys change between accent variants of the same flavor:

| Section | Keys |
| --- | --- |
| `[ui]` | `scrollbar_hover`, `status_brand_bg`, `status_brand_fg`, `status_percent_fg`, `toc_accent`, `toc_primary_active` |
| `[markdown]` | `blockquote_marker`, `list_level_1`, `table_header`, `heading_1`, `latex_inline_fg`, `latex_inline_bg`, `latex_block_fg`, `mermaid_keyword`, `alert_important` |
| `[diff]` | `tree_active` |

`status_brand_fg` is derived: it is the highest-contrast choice among Crust, Base, and Text for the accent background. `latex_inline_bg` is the accent blended 18% over Base.

Everything else keeps its semantic color. For example, links stay Blue, success stays Green, warnings stay Yellow, errors stay Red, and inline code stays Peach regardless of the accent.

## Generate an accent

The generator uses only the Python standard library.

```bash
# List flavors and accents
python3 scripts/generate.py --list

# Print a theme to stdout
python3 scripts/generate.py --flavor mocha --accent blue

# Write to a specific path
python3 scripts/generate.py --flavor mocha --accent blue \
  --output ~/.config/leaf/themes/catppuccin-mocha-blue.toml

# Install into $XDG_CONFIG_HOME/leaf/themes (or ~/.config/leaf/themes)
python3 scripts/generate.py --flavor mocha --accent blue --install

# Regenerate every committed theme
python3 scripts/generate.py --all

# Check that committed themes match the generator
python3 scripts/generate.py --check
```

### Custom hex accents

Use `--accent-hex` for any `#rrggbb` value. The generated file is named `catppuccin-<flavor>-custom.toml` when installed:

```bash
python3 scripts/generate.py --flavor mocha --accent-hex "#ff79c6" --install
```

```toml
theme = "catppuccin-mocha-custom"
```

You can also write it anywhere:

```bash
python3 scripts/generate.py --flavor mocha --accent-hex "#ff79c6" \
  --output ~/.config/leaf/themes/catppuccin-mocha-pinkish.toml
```

### Safe testing

`--install` respects `XDG_CONFIG_HOME`, so you can try a theme without touching your live configuration:

```bash
XDG_CONFIG_HOME=/tmp/leaf-test \
  python3 scripts/generate.py --flavor latte --accent teal --install

XDG_CONFIG_HOME=/tmp/leaf-test leaf --theme catppuccin-latte-teal README.md
```

### Manual editing

Every generated theme is a normal leaf TOML file. Copy it, change any value, and keep the key names unchanged. leaf silently ignores unknown keys, so use leaf's [`gruvbox.toml`](https://github.com/RivoLink/leaf/blob/main/gruvbox.toml) as the complete key reference.

If you edit the source template instead, regenerate all themes and run the checks:

```bash
python3 scripts/generate.py --all
python3 scripts/check.py
```

## Latte contrast notes

Latte is a light palette, so the raw Catppuccin colors do not always meet comfortable contrast on light backgrounds. The Latte themes keep the palette but adjust only the affected roles:

- `strong_text` uses Text instead of Rosewater.
- `inline_code_fg` uses a darker Peach blend on Surface 0.
- `link_hover` uses Blue instead of Sky.
- Status success/watch/search/warning foregrounds use darker Green/Yellow blends where needed.
- `mark_fg` uses Text and `mark_bg` uses Yellow 35% over Base.
- Diff add/delete foregrounds use darker Green/Red blends on their tinted backgrounds.
- Accent foreground roles are darkened only enough to reach about 3:1 on their background; decorative accent backgrounds keep the raw accent.

The dark flavors use the raw Catppuccin foreground colors.

## Validation

```bash
python3 scripts/generate.py --check
python3 scripts/check.py
```

`scripts/check.py` verifies the 99-key schema (35 UI, 47 Markdown, 17 Diff), valid `#rrggbb` values, flavor presets, accent isolation, and a set of foreground/background contrast pairs across all 56 themes.

## Notes

- Custom themes do not appear in leaf's `Shift+T` picker. Select them with the config file, `--theme`, `LEAF_THEME`, or a direct path.
- leaf only scans the top level of the theme directory. Copy accent files directly into `~/.config/leaf/themes/`.
- The four unsuffixed themes are the backward-compatible Mauve defaults. `catppuccin-frappe` remains color-identical to the 1.0.0 release.
