# Theme files

leaf only scans the **top level** of `~/.config/leaf/themes/`, so copy a theme file directly into that directory. Do not copy the `accents/` subdirectory into it.

## Mauve defaults

| File | Theme name | Flavor |
| --- | --- | --- |
| `catppuccin-latte.toml` | `catppuccin-latte` | Latte (light) |
| `catppuccin-frappe.toml` | `catppuccin-frappe` | Frappé (dark) |
| `catppuccin-macchiato.toml` | `catppuccin-macchiato` | Macchiato (dark) |
| `catppuccin-mocha.toml` | `catppuccin-mocha` | Mocha (dark) |

## Accent variants

`accents/` contains the 52 non-Mauve variants:

```text
accents/catppuccin-<flavor>-<accent>.toml
```

For example:

```text
accents/catppuccin-mocha-blue.toml
accents/catppuccin-latte-teal.toml
accents/catppuccin-frappe-lavender.toml
```

The theme name is the file name without `.toml`:

From the repository root:

```bash
cp themes/accents/catppuccin-mocha-blue.toml ~/.config/leaf/themes/
leaf --theme catppuccin-mocha-blue README.md
```

## Regenerating

The source of truth is `../src/palette.json` and `../src/template.toml`.

```bash
python3 scripts/generate.py --all
python3 scripts/generate.py --check
python3 scripts/check.py
```

See the main [README](../README.md) and [accent reference](../docs/ACCENTS.md) for installation and customization instructions.
