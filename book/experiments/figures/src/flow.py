"""Box-and-arrow helpers for the flow diagrams of the SLD chapter."""

from __future__ import annotations

from svgkit import Figure, color

FLOW_STYLE = """
    .st { fill: var(--ink, #1d1b17); font-size: 12px; font-weight: 600; }
    .sub { fill: var(--ink-2, #4a463f); font-size: 10.5px; }
    .note { fill: var(--ink-3, #7a756b); font-size: 10px; }
    .lane { fill: var(--ink-3, #7a756b); font-size: 10.5px; letter-spacing: 1.4px; }
    .tf { stroke-width: 1.1; }
"""


def stage(
    fig: Figure,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    lines: tuple[str, ...] = (),
    token: str = "ink-2",
    opacity: float = 0.1,
    dashed: bool = False,
) -> tuple[float, float, float, float]:
    """A rounded box with a bold title and smaller lines below it; returns its frame."""
    dash = ' stroke-dasharray="4 3"' if dashed else ""
    fig.rect(x, y, w, h, cls="paper", rx=4)
    fig.rect(
        x,
        y,
        w,
        h,
        cls="tf",
        rx=4,
        extra=f' fill="{color(token)}" fill-opacity="{opacity}" stroke="{color(token)}"{dash}',
    )
    top = y + h / 2 - (len(lines) * 13) / 2 + 4
    fig.text(x + w / 2, top, title, cls="st")
    for i, line in enumerate(lines):
        fig.text(x + w / 2, top + 14 + i * 13, line, cls="sub")
    return x, y, w, h


def right_arrow(
    fig: Figure,
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
    token: str = "ink-2",
) -> None:
    """An arrow from the right edge of frame a to the left edge of frame b."""
    ax, ay, aw, ah = a
    bx, by, _, bh = b
    fig.arrow_line(ax + aw + 2, ay + ah / 2, bx - 3, by + bh / 2, token=token)


def down_arrow(
    fig: Figure,
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
    token: str = "ink-2",
) -> None:
    """An arrow from the bottom of frame a to the top of frame b."""
    ax, ay, aw, ah = a
    bx, by, bw, _ = b
    fig.arrow_line(ax + aw / 2, ay + ah + 2, bx + bw / 2, by - 3, token=token)
