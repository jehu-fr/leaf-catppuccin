#!/usr/bin/env python3
"""Regenerate the README preview screenshots.

The preview pipeline is intentionally separate from the theme generator:

1. Run leaf on ``demo/demo.md`` in a pseudo-terminal, using a temporary
   ``XDG_CONFIG_HOME`` so the live leaf configuration is untouched.
2. Replay the PTY output through ``pyte`` to get the final terminal screen.
3. Flatten that screen back to ANSI with full-width background runs.
4. Render the ANSI with ``freeze``.  Unlike termshot, freeze paints ANSI
   background rectangles for the full line pitch, so the theme background is
   continuous instead of leaving a dark strip between terminal rows.
5. Flatten the transparent PNG onto the Catppuccin Crust background and
   resize it to 1600px WebP.

Requirements (not needed to install or use a theme)::

    python3 -m pip install -r scripts/requirements-preview.txt
    GOBIN=~/.local/bin go install github.com/charmbracelet/freeze@latest

``npx`` is used for the final WebP conversion (``npx --yes sharp-cli``).
Set ``FREEZE_BIN`` or ``NPX_BIN`` if the binaries are not on ``PATH``.

Run from the repository root::

    python3 scripts/preview.py
    python3 scripts/preview.py --flavor mocha
"""

from __future__ import annotations

import argparse
import codecs
import fcntl
import os
import pty
import select
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import termios
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
THEMES = ROOT / "themes"
DEMO = ROOT / "demo" / "demo.md"
COLS, ROWS = 120, 40

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate import FLAVOR_SLUGS, load_palette  # noqa: E402

try:
    import pyte
except ImportError as error:  # pragma: no cover - depends on the environment
    raise SystemExit(
        "pyte is required for preview generation; install it with "
        "'python3 -m pip install -r scripts/requirements-preview.txt'"
    ) from error

FREEZE_BIN = os.environ.get("FREEZE_BIN", "freeze")
NPX_BIN = os.environ.get("NPX_BIN", "npx")

FLAVOR_NOTES = {
    "latte": "is a light palette designed for bright environments.",
    "frappe": "is a muted dark palette designed for long reading sessions.",
    "macchiato": "is a medium-dark palette with soft contrast.",
    "mocha": "is a dark palette designed for long reading sessions.",
}


def read_until_idle(
    fd: int,
    stream: pyte.Stream,
    decoder: codecs.IncrementalDecoder,
    timeout: float,
    idle: float = 0.35,
) -> bool:
    """Feed PTY output into *stream* until it has been quiet for *idle* seconds."""
    last_data = time.monotonic()
    deadline = last_data + timeout

    while time.monotonic() < deadline:
        readable, _, _ = select.select([fd], [], [], 0.05)
        if not readable:
            if time.monotonic() - last_data >= idle:
                return True
            continue

        try:
            chunk = os.read(fd, 65536)
        except OSError:
            return False
        if not chunk:
            return False

        stream.feed(decoder.decode(chunk))
        last_data = time.monotonic()

    return False


def stop_leaf(pid: int, fd: int) -> None:
    try:
        os.write(fd, b"q")
    except OSError:
        pass

    deadline = time.monotonic() + 2.0
    while time.monotonic() < deadline:
        try:
            waited, _ = os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:
            return
        if waited == pid:
            return
        time.sleep(0.05)

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        os.waitpid(pid, 0)
    except ChildProcessError:
        pass


def build_demo(flavor: str, palette: dict) -> str:
    """Return the demo document with flavor-specific title, colors, and copy."""
    meta = palette["flavors"][flavor]
    colors = meta["colors"]
    text = DEMO.read_text(encoding="utf-8")

    def replace_once(old: str, new: str) -> None:
        nonlocal text
        if text.count(old) != 1:
            raise ValueError(f"demo/demo.md: expected exactly one {old!r}")
        text = text.replace(old, new)

    replace_once("# Catppuccin Mocha", f"# Catppuccin {meta['name']}")
    replace_once(
        "> Catppuccin Mocha is a dark palette designed for long reading sessions.",
        f"> Catppuccin {meta['name']} {FLAVOR_NOTES[flavor]}",
    )
    replace_once('theme = "catppuccin-mocha"', f'theme = "catppuccin-{flavor}"')
    rows = (
        ("Base", "base", "Background"),
        ("Mauve", "mauve", "Accent"),
        ("Blue", "blue", "Links"),
        ("Green", "green", "Success"),
        ("Peach", "peach", "Inline code"),
    )
    old_hex = {
        "base": "1e1e2e",
        "mauve": "cba6f7",
        "blue": "89b4fa",
        "green": "a6e3a1",
        "peach": "fab387",
    }
    for label, key, role in rows:
        replace_once(
            f"| {label} | `#{old_hex[key]}` | {role} |",
            f"| {label} | `{colors[key]}` | {role} |",
        )

    replace_once('let flavor = "mocha";', f'let flavor = "{flavor}";')
    return text


def capture(flavor: str, palette: dict) -> pyte.Screen:
    """Run leaf and return the terminal screen with the TOC visible."""
    theme_source = THEMES / f"catppuccin-{flavor}.toml"
    if not theme_source.exists():
        raise FileNotFoundError(f"missing theme: {theme_source}")

    with tempfile.TemporaryDirectory(prefix=f"leaf-preview-{flavor}-") as tmp:
        xdg = Path(tmp)
        theme_dir = xdg / "leaf" / "themes"
        theme_dir.mkdir(parents=True)
        theme_path = theme_dir / theme_source.name
        shutil.copy2(theme_source, theme_path)
        demo_path = xdg / "demo.md"
        demo_path.write_text(build_demo(flavor, palette), encoding="utf-8")

        env = os.environ.copy()
        env.update(
            {
                "TERM": "xterm-256color",
                "COLORTERM": "truecolor",
                "XDG_CONFIG_HOME": str(xdg),
                "LANG": "C.UTF-8",
                "LC_ALL": "C.UTF-8",
            }
        )

        pid, fd = pty.fork()
        if pid == 0:
            os.execvpe(
                "leaf",
                ["leaf", "--theme", theme_path.stem, str(demo_path)],
                env,
            )

        try:
            fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
            screen = pyte.Screen(COLS, ROWS)
            stream = pyte.Stream(screen)
            decoder = codecs.getincrementaldecoder("utf-8")("replace")

            if not read_until_idle(fd, stream, decoder, timeout=8.0):
                raise RuntimeError(f"leaf did not settle for {flavor}")
            os.write(fd, b"t")
            if not read_until_idle(fd, stream, decoder, timeout=5.0):
                raise RuntimeError(f"leaf did not render the TOC for {flavor}")

            return screen
        finally:
            # Stop leaf without feeding its exit sequences back into pyte.
            stop_leaf(pid, fd)
            try:
                os.close(fd)
            except OSError:
                pass


def color_to_rgb(value: str | None, fallback: str) -> tuple[int, int, int]:
    value = fallback if value in (None, "default") else value
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(channel * 2 for channel in value)
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def sgr(cell: pyte.screens.Char, default_fg: str, default_bg: str) -> str:
    fg, bg = cell.fg, cell.bg
    if cell.reverse:
        fg, bg = bg, fg

    fr, fg_green, fb = color_to_rgb(fg, default_fg)
    br, bg_green, bb = color_to_rgb(bg, default_bg)
    parts = ["0", f"38;2;{fr};{fg_green};{fb}", f"48;2;{br};{bg_green};{bb}"]

    if cell.bold:
        parts.append("1")
    if cell.italics:
        parts.append("3")
    if cell.underscore:
        parts.append("4")
    if cell.strikethrough:
        parts.append("9")

    return "\x1b[" + ";".join(parts) + "m"


def screen_to_ansi(screen: pyte.Screen, default_fg: str, default_bg: str) -> str:
    """Serialize a pyte screen to ANSI with a background for every cell."""
    lines: list[str] = []
    for row in range(screen.lines):
        current_style = None
        parts: list[str] = []
        for column in range(screen.columns):
            cell = screen.buffer[row][column]
            style = sgr(cell, default_fg, default_bg)
            if style != current_style:
                parts.append(style)
                current_style = style
            parts.append(cell.data or " ")
        parts.append("\x1b[0m\n")
        lines.append("".join(parts))
    return "".join(lines)


def render(flavor: str, ansi: str, palette: dict) -> Path:
    colors = palette["flavors"][flavor]["colors"]
    output = ASSETS / f"preview-{flavor}.webp"

    with tempfile.TemporaryDirectory(prefix=f"leaf-render-{flavor}-") as tmp:
        tmp_path = Path(tmp)
        ansi_path = tmp_path / "screen.ansi"
        png_path = tmp_path / "screen.png"
        flat_path = tmp_path / "flat.png"
        ansi_path.write_text(ansi, encoding="utf-8")

        freeze_command = [
            FREEZE_BIN,
            "--language",
            "ansi",
            "--background",
            colors["base"],
            "--window",
            "--border.radius",
            "12",
            "--border.width",
            "1",
            "--border.color",
            colors["surface1"],
            "--shadow.blur",
            "20",
            "--shadow.x",
            "0",
            "--shadow.y",
            "10",
            "--padding",
            "20,40",
            "--margin",
            "20",
            "--font.size",
            "20",
            "--line-height",
            "1.2",
            "--output",
            str(png_path),
        ]
        with ansi_path.open("rb") as input_file:
            subprocess.run(freeze_command, stdin=input_file, check=True)

        subprocess.run(
            [
                NPX_BIN,
                "--yes",
                "sharp-cli",
                "flatten",
                "#11111b",
                "-i",
                str(png_path),
                "-o",
                str(flat_path),
            ],
            check=True,
        )
        subprocess.run(
            [
                NPX_BIN,
                "--yes",
                "sharp-cli",
                "resize",
                "1600",
                "-i",
                str(flat_path),
                "-o",
                str(output),
            ],
            check=True,
        )

    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate the README preview screenshots.")
    parser.add_argument(
        "--flavor",
        choices=FLAVOR_SLUGS,
        action="append",
        help="flavor to render (repeatable; default: all four)",
    )
    args = parser.parse_args()

    flavors = args.flavor or FLAVOR_SLUGS
    palette = load_palette()
    ASSETS.mkdir(exist_ok=True)

    for flavor in flavors:
        print(f"capturing {flavor}...", flush=True)
        screen = capture(flavor, palette)
        colors = palette["flavors"][flavor]["colors"]
        ansi = screen_to_ansi(screen, colors["text"], colors["base"])
        print(f"rendering {flavor}...", flush=True)
        output = render(flavor, ansi, palette)
        print(f"wrote {output.relative_to(ROOT)}", flush=True)

    if "frappe" in flavors:
        shutil.copyfile(ASSETS / "preview-frappe.webp", ASSETS / "preview.webp")
        print("wrote assets/preview.webp", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
