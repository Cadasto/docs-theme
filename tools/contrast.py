#!/usr/bin/env python3
"""Assert every text and control pair in `tokens.css` clears WCAG contrast.

Run from the repository root, no arguments, no dependencies:

    python3 tools/contrast.py

The brand blue and green are tuned for the navy surface and fail badly on
white — 2.27:1 and 1.72:1 — which is how a light scheme shipped with
unreadable links. Nothing in a docs site's build can see that: the CSS is
valid, MkDocs is happy, and the default scheme is the dark one, so a reviewer
looking at the page never meets the failure. This script is the check that
does, so keep it passing rather than reasoning about the ratios by hand.

It parses the real declarations, so editing a brand constant, a `color-mix`
percentage, or an `rgba` alpha re-measures everything automatically. It only
understands the value forms `tokens.css` actually uses; anything else raises
rather than being silently skipped.

Thresholds are WCAG 2.1 AA: 4.5:1 for body text (1.4.3) and 3:1 for the
boundary of a control or a meaningful icon (1.4.11).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "tokens.css"

AA_TEXT = 4.5
AA_NON_TEXT = 3.0

Rgb = tuple[int, int, int]


# --- colour maths ---------------------------------------------------------


def _linear(channel: int) -> float:
    c = channel / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb: Rgb) -> float:
    r, g, b = (_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg: Rgb, bg: Rgb) -> float:
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def over(fg: Rgb, bg: Rgb, alpha: float) -> Rgb:
    """Composite a translucent colour onto an opaque one."""
    return tuple(round(alpha * fg[i] + (1 - alpha) * bg[i]) for i in range(3))


def mix(a: Rgb, b: Rgb, a_share: float) -> Rgb:
    """`color-mix(in srgb, a <share>%, b)` — a gamma-space sRGB mix."""
    return tuple(round(a[i] * a_share + b[i] * (1 - a_share)) for i in range(3))


# --- the tiny bit of CSS we need to understand ----------------------------

HEX = re.compile(r"^#([0-9a-fA-F]{6})$")
VAR = re.compile(r"^var\(\s*(--[\w-]+)\s*\)$")
RGBA = re.compile(r"^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,/\s]+([\d.]+))?\s*\)$")
MIX = re.compile(
    r"^color-mix\(\s*in\s+srgb\s*,\s*var\(\s*(--[\w-]+)\s*\)\s+([\d.]+)%\s*,\s*"
    r"var\(\s*(--[\w-]+)\s*\)\s*\)$"
)
BLOCK = re.compile(r"(?P<sel>[^{}]+)\{(?P<body>[^{}]*)\}", re.S)


def strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def declarations(css: str, selector: str) -> dict[str, str]:
    """`css` must already be comment-free — a comment before a block would
    otherwise be read as part of its selector."""
    for m in BLOCK.finditer(css):
        if m.group("sel").strip() != selector:
            continue
        body = m.group("body")
        out = {}
        for line in body.split(";"):
            if ":" in line:
                name, _, value = line.partition(":")
                out[name.strip()] = value.strip()
        return out
    raise SystemExit(f"contrast: no `{selector}` block in tokens.css")


class Palette:
    """Resolves a token name to an opaque colour on a known background."""

    def __init__(self, root: dict[str, str], scheme: dict[str, str], bg_token: str):
        self.defs = {**root, **scheme}
        self.background: Rgb = self.opaque(bg_token, None)

    def resolve(self, token: str) -> tuple[Rgb, float]:
        """Return (rgb, alpha) for a token, following `var()` chains."""
        if token not in self.defs:
            raise SystemExit(f"contrast: token {token} is not defined")
        value = self.defs[token]

        if m := HEX.match(value):
            h = m.group(1)
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)), 1.0
        if m := VAR.match(value):
            return self.resolve(m.group(1))
        if m := RGBA.match(value):
            r, g, b, a = m.groups()
            return (round(float(r)), round(float(g)), round(float(b))), float(a or 1.0)
        if m := MIX.match(value):
            first, share, second = m.group(1), float(m.group(2)) / 100, m.group(3)
            a, a_alpha = self.resolve(first)
            b, b_alpha = self.resolve(second)
            if a_alpha != 1.0 or b_alpha != 1.0:
                raise SystemExit(f"contrast: {token} mixes a translucent colour")
            return mix(a, b, share), 1.0
        raise SystemExit(f"contrast: cannot read {token}: {value!r}")

    def opaque(self, token: str, bg: Rgb | None) -> Rgb:
        rgb, alpha = self.resolve(token)
        if alpha == 1.0:
            return rgb
        if bg is None:
            raise SystemExit(f"contrast: {token} is translucent and has no backdrop")
        return over(rgb, bg, alpha)

    def against(self, fg_token: str, bg_token: str | None = None) -> tuple[Rgb, Rgb]:
        bg = self.background if bg_token is None else self.opaque(bg_token, self.background)
        return self.opaque(fg_token, bg), bg


# Each row is (foreground, background or None for the page, threshold, what it is).
# `None` means the scheme's own `--md-default-bg-color`.
PAIRS = [
    ("--md-typeset-color", None, AA_TEXT, "body text"),
    ("--md-default-fg-color--light", None, AA_TEXT, "muted body copy (taglines, card text)"),
    ("--md-default-fg-color--lighter", None, AA_NON_TEXT, "icons and small controls"),
    ("--cadasto-heading", None, AA_TEXT, "headings"),
    ("--md-typeset-a-color", None, AA_TEXT, "link text"),
    ("--md-accent-fg-color", None, AA_TEXT, "link hover text"),
    ("--md-primary-fg-color", None, AA_TEXT, "button label on the page"),
    ("--cadasto-ink-blue", None, AA_NON_TEXT, "primary button fill vs the page"),
    ("--cadasto-ink-green", None, AA_NON_TEXT, "button hover fill vs the page"),
    ("--cadasto-on-ink", "--cadasto-ink-blue", AA_TEXT, "label on the blue fill"),
    ("--cadasto-on-ink", "--cadasto-ink-green", AA_TEXT, "label on the green fill"),
    ("--cadasto-icon-1", None, AA_NON_TEXT, "first landing icon ink"),
    ("--cadasto-icon-2", None, AA_NON_TEXT, "second landing icon ink"),
    ("--cadasto-icon-3", None, AA_NON_TEXT, "third landing icon ink"),
    ("--cadasto-cta-bg", None, AA_NON_TEXT, "call-to-action fill vs the page"),
    ("--cadasto-cta-fg", "--cadasto-cta-bg", AA_TEXT, "label on the call-to-action fill"),
    ("--cadasto-cta-outline", None, AA_TEXT, "outline call-to-action label and border"),
]

# Both footers are navy in every scheme, so these rules in `material.css` and
# `landing.css` are scheme-independent and are checked once, against the navy.
FOOTER = [
    ("rgba(255, 255, 255, 0.72)", AA_TEXT, "footer text and links"),
    ("var(--cadasto-white)", AA_TEXT, "the bold word in the attribution"),
    ("var(--cadasto-blue)", AA_TEXT, "footer link hover"),
]

SCHEMES = [
    ('[data-md-color-scheme="slate"]', "dark"),
    ('[data-md-color-scheme="default"]', "light"),
]


def main() -> int:
    css = strip_comments(TOKENS.read_text())
    root = declarations(css, ":root")
    failures = []

    for selector, label in SCHEMES:
        palette = Palette(root, declarations(css, selector), "--md-default-bg-color")
        print(f"\n{label} ({selector})")
        for fg_token, bg_token, threshold, role in PAIRS:
            fg, bg = palette.against(fg_token, bg_token)
            ratio = contrast(fg, bg)
            ok = ratio >= threshold
            print(
                f"  {'ok  ' if ok else 'FAIL'} {ratio:5.2f}:1 "
                f"(need {threshold})  {role}"
            )
            if not ok:
                failures.append(
                    f"{label}: {fg_token} on "
                    f"{bg_token or '--md-default-bg-color'} is {ratio:.2f}:1, "
                    f"needs {threshold} — {role}"
                )

    # The footers borrow the navy regardless of scheme.
    navy_palette = Palette(root, {"--bg": "var(--cadasto-navy)"}, "--bg")
    print("\nboth footers (always navy)")
    for value, threshold, role in FOOTER:
        navy_palette.defs["--probe"] = value
        fg, bg = navy_palette.against("--probe")
        ratio = contrast(fg, bg)
        ok = ratio >= threshold
        print(f"  {'ok  ' if ok else 'FAIL'} {ratio:5.2f}:1 (need {threshold})  {role}")
        if not ok:
            failures.append(f"footer: {value} on navy is {ratio:.2f}:1 — {role}")

    if failures:
        print("\ncontrast: WCAG AA failures\n", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("\ncontrast: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
