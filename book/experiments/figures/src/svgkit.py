"""Shared SVG helpers for the figures of the Experiments part.

The book inlines each local SVG into its page, so a figure takes its colours from the
theme's CSS custom properties and follows the light and dark schemes. Every colour is
written as ``var(--token, fallback)`` with the light-scheme value as fallback, no figure
sets a fixed width or height, and ``text-anchor`` is set through the ``start``, ``mid``
and ``end`` classes, because a class style on an element overrides its presentation
attributes.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from html import escape
from pathlib import Path

# ---- Theme tokens -------------------------------------------------------------------
# Light-scheme values of bookspine 0.3.0, src/bookspine/static/book.css, :root block:
# https://github.com/AlkaidCheng/bookspine/blob/v0.3.0/src/bookspine/static/book.css
TOKENS: dict[str, str] = {
    "paper": "#fbfaf7",
    "paper-2": "#f3f0e9",
    "paper-3": "#e9e5db",
    "ink": "#1d1b17",
    "ink-2": "#4a463f",
    "ink-3": "#7a756b",
    "rule": "#ddd8cc",
    "accent": "#7f2e2a",
    "accent-ink": "#6a2522",
    "accent-soft": "#f4e6e3",
    "box-definition": "#2f5d7c",
    "box-example": "#3f6b3f",
    "box-remark": "#7a6a3b",
    "box-recipe": "#5a4b82",
    "box-warning": "#a3471e",
}

# ---- Figure geometry ----------------------------------------------------------------
DECIMALS = 2  # coordinates are rounded so that a rerun writes identical bytes
FONT_SIZE = 12.0  # px, the default label size; the page sets the font family


def color(token: str) -> str:
    """Return the CSS value of a theme token with its light-scheme fallback."""
    return f"var(--{token}, {TOKENS[token]})"


def num(value: float) -> str:
    """Format a coordinate with a fixed number of decimals and no trailing zeros."""
    text = f"{value:.{DECIMALS}f}".rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def points(coords: Iterable[tuple[float, float]]) -> str:
    """Format ``(x, y)`` pairs for a ``points`` attribute."""
    return " ".join(f"{num(x)},{num(y)}" for x, y in coords)


BASE_STYLE = f"""
    .t {{ fill: {color("ink")}; font-size: {num(FONT_SIZE)}px; }}
    .t2 {{ fill: {color("ink-2")}; font-size: {num(FONT_SIZE - 1)}px; }}
    .t3 {{ fill: {color("ink-3")}; font-size: {num(FONT_SIZE - 2)}px; }}
    .tb {{ font-weight: 600; }}
    .ti {{ font-style: italic; }}
    .ta {{ fill: {color("accent-ink")}; }}
    .caps {{ letter-spacing: 1.4px; }}
    .mono {{ font-family: var(--mono, monospace); }}
    .start {{ text-anchor: start; }}
    .mid {{ text-anchor: middle; }}
    .end {{ text-anchor: end; }}
    .ln {{ stroke: {color("ink-2")}; stroke-width: 1.2; fill: none; }}
    .ln3 {{ stroke: {color("ink-3")}; stroke-width: 1; fill: none; }}
    .thin {{ stroke-width: 0.7; }}
    .dash {{ stroke-dasharray: 4 3; }}
    .box {{ stroke: {color("ink-2")}; stroke-width: 1.2; fill: none; }}
    .paper {{ fill: {color("paper")}; }}
"""


@dataclass
class Figure:
    """An SVG figure under construction.

    Parameters
    ----------
    width, height : float
        The viewBox size in user units.
    prefix : str
        Unique prefix for ids inside this figure. Several figures share one page,
        so a marker or gradient id must not repeat across them.
    style : str
        Extra CSS rules appended to the base style.
    """

    width: float
    height: float
    prefix: str
    style: str = ""
    body: list[str] = field(default_factory=list)
    defs: list[str] = field(default_factory=list)

    def add(self, element: str) -> None:
        self.body.append(element)

    def comment(self, text: str) -> None:
        self.body.append(f"<!-- {escape(text, quote=False)} -->")

    def arrow(
        self, name: str = "arrow", token: str = "ink-2", size: float = 7.0
    ) -> str:
        """Define an arrowhead marker once and return its ``url(#…)`` reference."""
        marker_id = f"{self.prefix}-{name}"
        if not any(f'id="{marker_id}"' in d for d in self.defs):
            self.defs.append(
                f'<marker id="{marker_id}" viewBox="0 0 10 10" refX="9" refY="5" '
                f'markerWidth="{num(size)}" markerHeight="{num(size)}" '
                f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" '
                f'fill="{color(token)}"/></marker>'
            )
        return f"url(#{marker_id})"

    def text(
        self,
        x: float,
        y: float,
        content: str,
        cls: str = "t",
        anchor: str = "mid",
        extra: str = "",
    ) -> None:
        """Add a text element; `content` is escaped unless it holds a tspan."""
        body = content if "<tspan" in content else escape(content, quote=False)
        self.add(
            f'<text class="{cls} {anchor}" x="{num(x)}" y="{num(y)}"{extra}>{body}</text>'
        )

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        cls: str = "ln",
        extra: str = "",
    ) -> None:
        self.add(
            f'<line class="{cls}" x1="{num(x1)}" y1="{num(y1)}" '
            f'x2="{num(x2)}" y2="{num(y2)}"{extra}/>'
        )

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        cls: str = "box",
        rx: float = 0.0,
        extra: str = "",
    ) -> None:
        radius = f' rx="{num(rx)}"' if rx else ""
        self.add(
            f'<rect class="{cls}" x="{num(x)}" y="{num(y)}" width="{num(w)}" '
            f'height="{num(h)}"{radius}{extra}/>'
        )

    def path(self, d: str, cls: str = "ln", extra: str = "") -> None:
        self.add(f'<path class="{cls}" d="{d}"{extra}/>')

    def polygon(
        self, coords: Sequence[tuple[float, float]], cls: str = "box", extra: str = ""
    ) -> None:
        self.add(f'<polygon class="{cls}" points="{points(coords)}"{extra}/>')

    def polyline(
        self, coords: Sequence[tuple[float, float]], cls: str = "ln", extra: str = ""
    ) -> None:
        self.add(f'<polyline class="{cls}" points="{points(coords)}"{extra}/>')

    def circle(
        self, cx: float, cy: float, r: float, cls: str = "ln", extra: str = ""
    ) -> None:
        self.add(
            f'<circle class="{cls}" cx="{num(cx)}" cy="{num(cy)}" r="{num(r)}"{extra}/>'
        )

    def arrow_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        cls: str = "ln",
        token: str = "ink-2",
        both: bool = False,
    ) -> None:
        """A line with an arrowhead at its end (and its start if `both`)."""
        marker = self.arrow(f"arrow-{token}", token)
        start = f' marker-start="{marker}"' if both else ""
        self.line(x1, y1, x2, y2, cls, extra=f' marker-end="{marker}"{start}')

    def to_svg(self) -> str:
        joined_defs = "\n    ".join(self.defs)
        defs = f"  <defs>\n    {joined_defs}\n  </defs>\n" if self.defs else ""
        body = "\n  ".join(self.body)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {num(self.width)} '
            f'{num(self.height)}">\n{defs}  <style>{BASE_STYLE}{self.style}  </style>\n'
            f"  {body}\n</svg>\n"
        )

    def write(self, path: Path) -> None:
        path.write_text(self.to_svg(), encoding="utf-8")


def wave_path(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    amplitude: float = 3.0,
    wavelength: float = 10.0,
) -> str:
    """A sinusoidal path between two points, as drawn for photon and Z lines."""
    length = math.hypot(x2 - x1, y2 - y1)
    n_half = max(2, round(2 * length / wavelength))
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    nx, ny = -uy, ux
    step = length / n_half
    d = [f"M{num(x1)} {num(y1)}"]
    for k in range(n_half):
        sign = 1 if k % 2 == 0 else -1
        cx = x1 + ux * step * (k + 0.5) + nx * amplitude * 2 * sign
        cy = y1 + uy * step * (k + 0.5) + ny * amplitude * 2 * sign
        ex, ey = x1 + ux * step * (k + 1), y1 + uy * step * (k + 1)
        d.append(f"Q{num(cx)} {num(cy)} {num(ex)} {num(ey)}")
    return " ".join(d)


def curl_path(
    x1: float, y1: float, x2: float, y2: float, radius: float = 4.0, pitch: float = 6.0
) -> str:
    """A curly path between two points, as drawn for gluon lines."""
    length = math.hypot(x2 - x1, y2 - y1)
    n_loops = max(2, round(length / pitch))
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    nx, ny = -uy, ux
    step = length / n_loops
    d = [f"M{num(x1)} {num(y1)}"]
    for k in range(n_loops):
        base_x, base_y = x1 + ux * step * k, y1 + uy * step * k
        c1 = (
            base_x + ux * step * 1.4 + nx * radius * 2,
            base_y + uy * step * 1.4 + ny * radius * 2,
        )
        c2 = (
            base_x - ux * step * 0.4 + nx * radius * 2,
            base_y - uy * step * 0.4 + ny * radius * 2,
        )
        end = (base_x + ux * step, base_y + uy * step)
        d.append(
            f"C{num(c1[0])} {num(c1[1])} {num(c2[0])} {num(c2[1])} {num(end[0])} {num(end[1])}"
        )
    return " ".join(d)
