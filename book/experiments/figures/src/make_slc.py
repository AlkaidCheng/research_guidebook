"""Draw the SLAC Linear Collider as a schematic, not to scale (sld-slc-layout.svg).

Values on the figure: damping rings at 1.19 GeV and beams of 46.6 GeV at the end of the
linac (Woods, SLAC-PUB-7320; SLD Polarization at SLC page), the 3 km linac and 120 Hz
operation (Phys. Rept. 427, Sec. 1.1.2 and Fig. 1.4), arcs of about 1 km (SLD Physics
Primer, "Other Collider Details"), 45.6 GeV beams at the IP and the Compton polarimeter
about 30 m downstream (Woods, SLAC-PUB-7319; Phys. Rept. 427), the energy spectrometers
about 150 m downstream (Kent et al., SLAC-PUB-4922).
"""

from __future__ import annotations

from pathlib import Path

from flow import FLOW_STYLE
from svgkit import Figure, color

FIGURES_DIR = Path(__file__).resolve().parent.parent

STYLE = (
    FLOW_STYLE
    + """
    .beam { fill: none; stroke-width: 2.4; }
    .em { stroke: var(--box-definition, #2f5d7c); }
    .ep { stroke: var(--box-warning, #a3471e); }
    .linac { fill: var(--ink-3, #7a756b); fill-opacity: 0.18; stroke: var(--ink-2, #4a463f); stroke-width: 1; }
    .ring { fill: none; stroke: var(--ink-2, #4a463f); stroke-width: 1.4; }
    .dev { fill: var(--paper, #fbfaf7); stroke: var(--ink, #1d1b17); stroke-width: 1.2; }
"""
)


def main() -> None:
    fig = Figure(842, 334, "slc", style=STYLE)
    # Linac along the bottom.
    fig.rect(70, 238, 420, 18, cls="linac", rx=3)
    fig.text(280, 251, "linac, 3 km", cls="sub")
    fig.text(
        250,
        322,
        "electrons and positrons accelerated together to 46.6 GeV, 120 pulses per second",
        cls="note",
    )
    # Source and damping rings at the start.
    fig.rect(14, 236, 44, 22, cls="dev", rx=3)
    fig.text(36, 230, "e⁻ source", cls="sub")
    fig.line(58, 247, 70, 247, cls="beam em")
    fig.circle(110, 196, 22, cls="ring")
    fig.circle(170, 196, 22, cls="ring")
    fig.text(110, 200, "e⁻", cls="sub")
    fig.text(170, 200, "e⁺", cls="sub")
    fig.text(140, 162, "damping rings, 1.19 GeV", cls="sub")
    # Each ring is filled from the linac and extracted back into it.
    fig.path("M90 238 C90 214 95 210 100 214", cls="beam em")
    fig.path("M120 216 C125 228 130 234 140 238", cls="beam em")
    fig.path("M180 216 C185 228 190 234 200 238", cls="beam ep")
    # Positron production and return.
    fig.rect(392, 258, 30, 14, cls="dev", rx=2)
    fig.text(428, 268, "e⁺ target", cls="note", anchor="start")
    fig.path(
        "M392 266 C300 312 200 306 175 220",
        cls="beam ep",
        extra=' stroke-dasharray="5 4"',
    )
    fig.text(300, 306, "positrons returned to the start of the linac", cls="note")
    # Arcs from the end of the linac to the IP.
    fig.path("M490 247 C560 247 580 120 640 92", cls="beam em")
    fig.path("M490 247 C560 247 700 250 700 170 C700 125 670 100 640 92", cls="beam ep")
    fig.text(560, 170, "north and south arcs, about 1 km", cls="note", anchor="end")
    # Final focus, IP and SLD.
    fig.rect(620, 74, 40, 36, cls="dev", rx=4)
    fig.text(640, 96, "SLD", cls="st")
    fig.text(600, 104, "interaction point,", cls="sub", anchor="end")
    fig.text(600, 117, "45.6 GeV beams", cls="sub", anchor="end")
    # Extraction lines: electrons continue up and to the right, positrons up and to the left.
    fig.path("M660 82 L742 22", cls="beam em", extra=' stroke-dasharray="2 3"')
    fig.path("M620 82 L548 22", cls="beam ep", extra=' stroke-dasharray="2 3"')
    fig.rect(676, 62, 22, 12, cls="dev", rx=2)
    fig.text(704, 76, "Compton polarimeter, ~30 m", cls="note", anchor="start")
    fig.circle(735, 27, 5, cls="dev")
    fig.circle(555, 27, 5, cls="dev")
    fig.text(568, 31, "energy spectrometers, ~150 m", cls="note", anchor="start")
    # Legend.
    fig.line(20, 20, 46, 20, cls="beam em")
    fig.text(52, 24, "electrons (polarised)", cls="sub", anchor="start")
    fig.line(20, 40, 46, 40, cls="beam ep")
    fig.text(52, 44, "positrons", cls="sub", anchor="start")
    fig.text(20, 80, "not to scale", cls="note", anchor="start")
    _ = color
    fig.write(FIGURES_DIR / "sld-slc-layout.svg")


if __name__ == "__main__":
    main()
