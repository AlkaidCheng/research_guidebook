"""Feynman-diagram primitives drawn with svgkit: fermions, photons, gluons, vertices.

The conventions are the usual ones: a fermion is a straight line with an arrow along the
flow of particle number (an antifermion's arrow points backwards in time), a photon,
Z or W is a wavy line, a gluon a curly line, and time runs from left to right.
"""

from __future__ import annotations

import math

from svgkit import Figure, curl_path, num, wave_path

# ---- Drawing constants --------------------------------------------------------------
ARROW_HALF_WIDTH = 3.6  # px, half the base of the arrowhead on a fermion line
ARROW_LENGTH = 7.0  # px
VERTEX_RADIUS = 2.6  # px
COMBINING_MACRON = "̄"  # written after a letter, drawn as an overline (antiparticle)


def fermion(
    fig: Figure, x1: float, y1: float, x2: float, y2: float, forward: bool = True
) -> None:
    """A fermion line from (x1, y1) to (x2, y2) with the arrow at its middle.

    Parameters
    ----------
    forward : bool
        True if particle number flows from the first point to the second.
    """
    fig.line(x1, y1, x2, y2, cls="ln fer")
    length = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    if not forward:
        ux, uy = -ux, -uy
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    tip = (mx + ux * ARROW_LENGTH / 2, my + uy * ARROW_LENGTH / 2)
    base_x, base_y = mx - ux * ARROW_LENGTH / 2, my - uy * ARROW_LENGTH / 2
    left = (base_x - uy * ARROW_HALF_WIDTH, base_y + ux * ARROW_HALF_WIDTH)
    right = (base_x + uy * ARROW_HALF_WIDTH, base_y - ux * ARROW_HALF_WIDTH)
    fig.polygon([tip, left, right], cls="head")


def boson(fig: Figure, x1: float, y1: float, x2: float, y2: float) -> None:
    """A photon, Z or W line."""
    fig.path(wave_path(x1, y1, x2, y2), cls="ln bos")


def gluon(fig: Figure, x1: float, y1: float, x2: float, y2: float) -> None:
    """A gluon line."""
    fig.path(curl_path(x1, y1, x2, y2), cls="ln glu")


def meson(fig: Figure, x1: float, y1: float, x2: float, y2: float) -> None:
    """A hadron drawn as a double line."""
    length = math.hypot(x2 - x1, y2 - y1)
    nx, ny = -(y2 - y1) / length * 1.6, (x2 - x1) / length * 1.6
    fig.line(x1 + nx, y1 + ny, x2 + nx, y2 + ny, cls="ln fer")
    fig.line(x1 - nx, y1 - ny, x2 - nx, y2 - ny, cls="ln fer")


def vertex(fig: Figure, x: float, y: float) -> None:
    fig.circle(x, y, VERTEX_RADIUS, cls="vtx")


def label(fig: Figure, x: float, y: float, content: str, anchor: str = "mid") -> None:
    """A particle label; `content` may hold the ``_{…}`` and ``^{…}`` markup."""
    fig.text(x, y, markup(content), cls="t fl", anchor=anchor)


def markup(content: str) -> str:
    """Turn ``a_{b}`` and ``a^{b}`` into tspans shifted down or up by a third of an em."""
    out, i = [], 0
    while i < len(content):
        if content[i + 1 : i + 2] == COMBINING_MACRON:
            out.append(f'<tspan text-decoration="overline">{content[i]}</tspan>')
            i += 2
        elif content[i] in "_^" and content[i + 1 : i + 2] == "{":
            close = content.index("}", i)
            shift = "0.32em" if content[i] == "_" else "-0.42em"
            back = "-0.32em" if content[i] == "_" else "0.42em"
            out.append(
                f'<tspan dy="{shift}" font-size="72%">{content[i + 2 : close]}</tspan>'
                f'<tspan dy="{back}"> </tspan>'
            )
            i = close + 1
        else:
            out.append(content[i].replace("&", "&amp;").replace("<", "&lt;"))
            i += 1
    text = "".join(out)
    return text if "<tspan" in text else f"<tspan>{text}</tspan>"


FEYNMAN_STYLE = """
    .fer { stroke-width: 1.4; }
    .bos { stroke-width: 1.3; }
    .glu { stroke-width: 1.2; }
    .head { fill: var(--ink-2, #4a463f); stroke: none; }
    .vtx { fill: var(--ink, #1d1b17); stroke: none; }
    .fl { font-size: 14px; font-style: italic; }
    .panel { fill: var(--ink-3, #7a756b); font-size: 12px; }
"""


def new_figure(width: float, height: float, prefix: str) -> Figure:
    return Figure(width, height, prefix, style=FEYNMAN_STYLE)


def panel_label(fig: Figure, x: float, y: float, text: str) -> None:
    fig.text(x, y, text, cls="panel", anchor="start")


__all__ = [
    "boson",
    "fermion",
    "gluon",
    "label",
    "meson",
    "new_figure",
    "num",
    "panel_label",
    "vertex",
]
