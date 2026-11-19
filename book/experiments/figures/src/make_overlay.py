"""Draw the random-trigger overlay of the SLD Monte Carlo (sld-overlay.svg).

One recorded random-trigger event is merged with several simulated Z decays. The MC
records that use it share its header label, its detector-status words except the CDC veto
bit, and most background clusters that no simulated particle touched; their truth, PHBM
and MCBEAM come from the simulation. The statements are those of the chapter's MC page.
"""

from __future__ import annotations

from pathlib import Path

from flow import FLOW_STYLE, stage
from svgkit import Figure, color

FIGURES_DIR = Path(__file__).resolve().parent.parent

COPIED, SIMULATED = "box-remark", "box-definition"


def chip(fig: Figure, x: float, y: float, w: float, text: str, token: str) -> None:
    fig.rect(
        x,
        y,
        w,
        17,
        cls="tf",
        rx=2,
        extra=f' fill="{color(token)}" fill-opacity="0.16" stroke="{color(token)}"',
    )
    fig.text(x + w / 2, y + 12.5, text, cls="sub")


def main() -> None:
    fig = Figure(760, 330, "ov", style=FLOW_STYLE)
    stage(
        fig,
        10,
        92,
        200,
        120,
        "Random-trigger event",
        (
            "recorded at a random beam",
            "crossing: detector status,",
            "noise and beam background",
            "(run, event)",
        ),
        COPIED,
        0.14,
    )
    cards = 4
    for k in range(cards):
        x, y = 262 + k * 12, 18 + k * 12
        fig.rect(x, y, 448, 230, cls="paper", rx=4)
        fig.rect(
            x,
            y,
            448,
            230,
            cls="tf",
            rx=4,
            extra=f' fill="none" stroke="{color("ink-3")}"',
        )
    x0, y0 = 262 + 3 * 12, 18 + 3 * 12
    fig.text(
        x0 + 224, y0 + 20, "MC record (one of several that share the event)", cls="st"
    )
    rows = (
        ("header label (run, event)", COPIED),
        ("PHEVCL status words, except the CDC veto bit", COPIED),
        ("background clusters, mostly byte for byte", COPIED),
        ("simulated Z decay: MCPART, MCPNT, PHKMC1, PHWMC", SIMULATED),
        ("tracks, clusters and particles built from both", SIMULATED),
        ("PHBM and MCBEAM: beam energy, IP, helicity", SIMULATED),
    )
    for i, (text, token) in enumerate(rows):
        chip(fig, x0 + 16, y0 + 36 + i * 24, 416, text, token)
    fig.arrow_line(212, 152, x0 - 6, 152, token="box-remark")
    fig.text(255, 140, "reused", cls="note")
    gen = stage(
        fig,
        10,
        238,
        200,
        54,
        "Simulated Z decay",
        ("JETSET 7.4, GEANT 3",),
        SIMULATED,
        0.14,
    )
    fig.arrow_line(212, 265, x0 - 6, 230, token="box-definition")
    # Legend.
    for i, (text, token) in enumerate(
        (
            ("copied from the random trigger", COPIED),
            ("simulated, different in every record", SIMULATED),
        )
    ):
        x = 300 + i * 220
        fig.rect(
            x,
            304,
            12,
            12,
            cls="tf",
            extra=f' fill="{color(token)}" fill-opacity="0.3" stroke="{color(token)}"',
        )
        fig.text(x + 18, 314, text, cls="sub", anchor="start")
    _ = gen
    fig.write(FIGURES_DIR / "sld-overlay.svg")


if __name__ == "__main__":
    main()
