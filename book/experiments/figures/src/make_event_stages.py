"""Draw an e+e- -> Z -> q qbar event at its stages (sld-event-stages.svg), stylised.

The panels follow the factorised picture used by event generators: hard process, parton
shower, hadronisation, decays, then passage through the detector and reconstruction.
In the SLD Monte Carlo the generator decayed B and D hadrons and pi0, while GEANT decayed
K0S, K+- and Lambda in flight: MCPART sets ORIGIN bit DECAYED ("Decayed by generator") for
the former and DECAYFLT ("Decayed in flight by swimmer") for the latter (MCPART template,
ORIGIN notes, https://web.archive.org/web/20010906181156/http://www-sld.slac.stanford.edu:80/ducs/prod/mc/mcpart.template;
checked on the MCPART banks of a 1996 JETSET 7.4 mini-DST file). Nothing here is to scale; the shapes are seeded so that a rerun writes
the same bytes.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from svgkit import Figure, color, curl_path, num, wave_path

FIGURES_DIR = Path(__file__).resolve().parent.parent
SEED = 7  # fixes the stylised branchings

PANEL_W, PANEL_H, TOP = 122.0, 200.0, 40.0

STYLE = """
    .pt { fill: var(--ink, #1d1b17); font-size: 11.5px; font-weight: 600; }
    .pc { fill: var(--ink-2, #4a463f); font-size: 9.5px; }
    .frame { fill: none; stroke: var(--rule, #ddd8cc); stroke-width: 1; }
    .q { stroke: var(--box-definition, #2f5d7c); stroke-width: 1.6; fill: none; }
    .g { stroke: var(--box-warning, #a3471e); stroke-width: 1.1; fill: none; }
    .h { fill: var(--box-example, #3f6b3f); fill-opacity: 0.55; stroke: none; }
    .str { stroke: var(--box-remark, #7a6a3b); stroke-width: 5; stroke-opacity: 0.35; fill: none; stroke-linecap: round; }
    .trk { stroke: var(--ink-2, #4a463f); stroke-width: 1; fill: none; }
    .neu { stroke: var(--ink-3, #7a756b); stroke-width: 0.9; stroke-dasharray: 3 2; fill: none; }
    .det { fill: none; stroke: var(--rule, #ddd8cc); stroke-width: 6; }
    .clu { fill: var(--box-warning, #a3471e); fill-opacity: 0.45; stroke: none; }
"""


def panel_origin(i: int) -> tuple[float, float]:
    return 8 + i * (PANEL_W + 4), TOP


def panel(
    fig: Figure, i: int, title: str, lines: tuple[str, ...]
) -> tuple[float, float]:
    x, y = panel_origin(i)
    fig.rect(x, y, PANEL_W, PANEL_H, cls="frame", rx=4)
    fig.text(x + PANEL_W / 2, y - 22, f"{i + 1}. {title}", cls="pt")
    for k, line in enumerate(lines):
        fig.text(x + PANEL_W / 2, y + PANEL_H + 16 + k * 12, line, cls="pc")
    return x + PANEL_W / 2, y + PANEL_H / 2


def rays(rng: random.Random, n: int, spread: float, axis: float) -> list[float]:
    return [axis + rng.uniform(-spread, spread) for _ in range(n)]


def main() -> None:
    rng = random.Random(SEED)
    fig = Figure(6 * (PANEL_W + 4) + 12, TOP + PANEL_H + 52, "es", style=STYLE)
    # 1. Hard process.
    cx, cy = panel(fig, 0, "Hard process", ("e⁺ e⁻ → Z → q q̄", "matrix element"))
    fig.line(cx - 52, cy - 40, cx - 18, cy, cls="trk")
    fig.line(cx - 52, cy + 40, cx - 18, cy, cls="trk")
    fig.path(wave_path(cx - 18, cy, cx + 12, cy, 2.5, 8), cls="g")
    fig.line(cx + 12, cy, cx + 52, cy - 52, cls="q")
    fig.line(cx + 12, cy, cx + 52, cy + 52, cls="q")
    fig.text(cx - 3, cy - 10, "Z", cls="pc")
    # 2. Parton shower: each quark radiates gluons that branch again.
    cx, cy = panel(fig, 1, "Parton shower", ("q → qg, g → gg, g → q q̄", "JETSET 7.4"))
    for sign in (-1, 1):
        axis = sign * math.radians(45)
        fig.line(
            cx - 40,
            cy,
            cx - 40 + 92 * math.cos(axis),
            cy - 92 * math.sin(axis) * -1 * -1,
            cls="q",
        )
        for t in (0.35, 0.6):
            bx = cx - 40 + 92 * t * math.cos(axis)
            by = cy + 92 * t * math.sin(axis)
            angle = axis + sign * rng.uniform(0.25, 0.5)
            ex, ey = bx + 44 * math.cos(angle), by + 44 * math.sin(angle)
            fig.path(curl_path(bx, by, ex, ey, 2.2, 4.5), cls="g")
            fig.line(
                ex,
                ey,
                ex + 14 * math.cos(angle - 0.3),
                ey + 14 * math.sin(angle - 0.3),
                cls="g",
            )
    # 3. Hadronisation: a q - g - qbar string system breaks into hadrons along its length.
    cx, cy = panel(
        fig,
        2,
        "Hadronisation",
        ("the colour string breaks", "into hadrons (Lund model)"),
    )
    q_end, kink, qbar_end = (cx - 48, cy + 46), (cx + 4, cy - 58), (cx + 50, cy + 40)
    for (x1, y1), (x2, y2) in ((q_end, kink), (kink, qbar_end)):
        fig.line(x1, y1, x2, y2, cls="str")
        length = math.hypot(x2 - x1, y2 - y1)
        nx, ny = -(y2 - y1) / length, (x2 - x1) / length
        for t in (0.16, 0.38, 0.6, 0.82):
            offset = rng.uniform(-5, 5)
            fig.circle(
                x1 + (x2 - x1) * t + nx * offset,
                y1 + (y2 - y1) * t + ny * offset,
                3.6,
                cls="h",
            )
    for (x, y), name in ((q_end, "q"), (kink, "g"), (qbar_end, "q\u0304")):
        fig.text(x, y + (16 if name != "g" else -8), name, cls="pc")
    # 4. Decays in the generator: a B decays at a displaced vertex, a pi0 -> gamma gamma
    # at its production point.
    cx, cy = panel(
        fig, 3, "Decays", ("B and D decayed by the", "generator; π⁰ → γγ at once")
    )
    ox, oy = cx - 45, cy
    fig.circle(ox, oy, 2.2, cls="h")
    fig.line(ox, oy, ox + 32, oy - 22, cls="q")
    fig.circle(ox + 32, oy - 22, 2.4, cls="h")
    for a in (-1.2, -0.6, -0.1, 0.4):
        fig.line(
            ox + 32,
            oy - 22,
            ox + 32 + 50 * math.cos(a),
            oy - 22 + 50 * math.sin(a),
            cls="trk",
        )
    fig.text(ox + 20, oy - 30, "B", cls="pc")
    for a in (0.25, 0.75):
        fig.line(ox, oy, ox + 76 * math.cos(a), oy + 76 * math.sin(a), cls="neu")
    fig.text(ox + 22, oy + 62, "π⁰ → γγ", cls="pc")
    fig.line(ox, oy, ox - 10, oy + 50, cls="trk")
    # 5. Detector: tracks curve in the field, photons stop in the calorimeter; in the
    # simulation GEANT 3 also decays the long-lived hadrons.
    cx, cy = panel(
        fig,
        4,
        "Detector",
        (
            "tracking, CRID, LAC, WIC;",
            "simulated by GEANT 3,",
            'which decays K⁰<tspan dy="0.3em" font-size="75%">S</tspan>'
            '<tspan dy="-0.3em">, K±, Λ</tspan>',
        ),
    )
    dx, dy = cx - 50, cy + 70
    for radius, token in (
        (40, "box-definition"),
        (80, "box-example"),
        (112, "box-warning"),
    ):
        fig.path(
            f"M{num(dx + radius)} {num(dy)} A{radius} {radius} 0 0 0 {num(dx)} {num(dy - radius)}",
            cls="det",
            extra=f' stroke="{color(token)}" stroke-opacity="0.25"',
        )
    for k, a in enumerate((0.35, 0.65, 0.95, 1.2)):
        curve = 0.25 * (1 if k % 2 else -1)
        ex, ey = dx + 108 * math.cos(a), dy - 108 * math.sin(a)
        mx, my = dx + 55 * math.cos(a + curve), dy - 55 * math.sin(a + curve)
        fig.path(
            f"M{num(dx)} {num(dy)} Q{num(mx)} {num(my)} {num(ex)} {num(ey)}", cls="trk"
        )
        fig.circle(ex, ey, 4.2, cls="clu")
    fig.line(dx, dy, dx + 112 * math.cos(1.45), dy - 112 * math.sin(1.45), cls="neu")
    fig.circle(dx + 112 * math.cos(1.45), dy - 112 * math.sin(1.45), 5, cls="clu")
    # 6. Reconstruction: helices, clusters, particles, the thrust axis.
    cx, cy = panel(
        fig,
        5,
        "Reconstruction",
        ("tracks, clusters, particles;", "thrust axis and jets"),
    )
    fig.line(
        cx - 48, cy + 48, cx + 48, cy - 48, cls="trk", extra=' stroke-dasharray="6 3"'
    )
    for a in rays(rng, 6, 0.45, math.radians(45)) + rays(
        rng, 5, 0.45, math.radians(225)
    ):
        length = rng.uniform(34, 58)
        fig.arrow_line(
            cx,
            cy,
            cx + length * math.cos(a),
            cy - length * math.sin(a),
            cls="trk",
            token="ink-2",
        )
    fig.text(cx + 30, cy - 56, "thrust", cls="pc", anchor="start")
    fig.write(FIGURES_DIR / "sld-event-stages.svg")


if __name__ == "__main__":
    main()
