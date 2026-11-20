"""Draw one recorded hadronic Z decay seen along the beam (sld-event-display.svg).

Tracks are helices from their PHCHRG parameters (azimuth phi0 and 1/pT at the point of
closest approach, charge) in the 0.6 T field, drawn from the beam line to the outer wall of
the CDC and faintly on to the LAC. Barrel clusters (|cos theta| below the LAC barrel edge)
are radial bars on the LAC, their length growing with the logarithm of the raw energy.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

from sld_geometry import SOLENOID_FIELD_T, VOLUMES
from svgkit import Figure, color, num, points

SRC_DIR = Path(__file__).resolve().parent
FIGURES_DIR = SRC_DIR.parent
EVENT_PATH = SRC_DIR / "data" / "event_display.json"

SCALE = 1.12  # px per cm
HALF = 305.0  # cm shown on each side of the beam
LIGHT_SPEED_FACTOR = 0.299792458  # pT [GeV] = 0.3 B [T] R [m]
STEP_CM = 1.0
LAC_BARREL_COS = 0.84  # barrel coverage, PRD 53 (1996) 1023
TOWER_HALF_WIDTH = (
    0.033  # rad, half of two barrel towers of 33 mrad (NIM A328 (1993) 472)
)

STYLE = """
    .ring { fill: none; stroke: var(--rule, #ddd8cc); stroke-width: 1; }
    .trk { fill: none; stroke: var(--box-definition, #2f5d7c); stroke-width: 1.3; }
    .trk2 { fill: none; stroke: var(--box-definition, #2f5d7c); stroke-width: 0.8; stroke-opacity: 0.35; }
    .clu { fill: var(--box-warning, #a3471e); fill-opacity: 0.75; stroke: none; }
    .lbl { fill: var(--ink-3, #7a756b); font-size: 10px; }
"""


def radii(key: str) -> tuple[float, float]:
    vol = next(v for v in VOLUMES if v.key == key)
    rs = [r for _, r in vol.outline]
    inner = vol.outline[0][1] if key in ("lac_barrel", "crid_barrel") else min(rs)
    return inner, max(rs)


def helix(
    phi0: float, inv_pt: float, charge: int, r_stop: float
) -> list[tuple[float, float]]:
    """Step along a helix projected on x–y, from the origin out to radius r_stop."""
    radius = 100.0 / (LIGHT_SPEED_FACTOR * SOLENOID_FIELD_T * inv_pt)  # cm
    x = y = turned = 0.0
    phi = phi0
    path = [(x, y)]
    while math.hypot(x, y) < r_stop and turned < math.pi:
        x += STEP_CM * math.cos(phi)
        y += STEP_CM * math.sin(phi)
        phi -= charge * STEP_CM / radius
        turned += STEP_CM / radius
        path.append((x, y))
    return path


def main() -> None:
    event = json.loads(EVENT_PATH.read_text())
    size = 2 * HALF * SCALE
    c = size / 2
    fig = Figure(size, size + 18, "ed", style=STYLE)

    def xy(x: float, y: float) -> tuple[float, float]:
        return c + x * SCALE, c - y * SCALE

    for key in ("cdc", "crid_barrel", "lac_barrel"):
        r_in, r_out = radii(key)
        for r in (r_in, r_out):
            fig.circle(c, c, r * SCALE, cls="ring")
    cdc_out = radii("cdc")[1]
    lac_in = (
        192.0  # cm, inner face of the active LAC barrel (quadrant drawing; data: 192.7)
    )
    for track in event["tracks"]:
        inner = helix(track["phi0"], track["inv_pt"], track["charge"], cdc_out)
        outer = helix(track["phi0"], track["inv_pt"], track["charge"], lac_in)[
            len(inner) - 1 :
        ]
        fig.polyline([xy(*p) for p in inner], cls="trk")
        if len(outer) > 1:
            fig.polyline([xy(*p) for p in outer], cls="trk2")
    for cluster in event["clusters"]:
        if abs(cluster["cos_theta"]) >= LAC_BARREL_COS:
            continue
        length = min(80.0, 22.0 + 22.0 * math.log10(cluster["e_raw"] / 0.1))
        phi = cluster["phi"]
        corners = []
        for r, dphi in (
            (lac_in, -TOWER_HALF_WIDTH),
            (lac_in + length, -TOWER_HALF_WIDTH),
            (lac_in + length, TOWER_HALF_WIDTH),
            (lac_in, TOWER_HALF_WIDTH),
        ):
            corners.append(xy(r * math.cos(phi + dphi), r * math.sin(phi + dphi)))
        fig.polygon(corners, cls="clu")
    labels = (
        ("CDC", radii("cdc")[1] - 8),
        ("CRID", radii("crid_barrel")[1] - 8),
        ("LAC", radii("lac_barrel")[1] - 8),
    )
    for text, r in labels:
        fig.text(
            *xy(-r * math.cos(math.radians(40)), -r * math.sin(math.radians(40))),
            text,
            cls="lbl",
        )
    fig.text(
        c,
        size + 12,
        "tracks: helices from the CDC and VXD3 fit; bars: barrel LAC clusters, "
        "length growing with log E",
        cls="lbl",
    )
    _ = (color, num, points)
    fig.write(FIGURES_DIR / "sld-event-display.svg")


if __name__ == "__main__":
    main()
