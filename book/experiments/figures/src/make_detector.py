"""Draw the SLD detector views from the geometry table in ``sld_geometry.py``.

- sld-detector-rz.svg: the r–z quadrant, to scale, labelled;
- sld-detector-xy.svg: the barrel seen along the beam, to scale;
- sld-vxd3-xy.svg: the VXD3 ladders and the beam pipe seen along the beam.
"""

from __future__ import annotations

import math
from pathlib import Path

from sld_geometry import (
    BEAM_PIPE_RADIUS,
    GROUPS,
    QUADRANT_R_MAX,
    QUADRANT_Z_MAX,
    VOLUMES,
    VXD3_LAYERS,
)
from svgkit import Figure, color, num

FIGURES_DIR = Path(__file__).resolve().parent.parent

STYLE = """
    .vol { stroke-width: 1; }
    .vl { fill: var(--ink, #1d1b17); font-size: 11.5px; font-weight: 600; }
    .vs { fill: var(--ink-2, #4a463f); font-size: 10px; }
    .ax { stroke: var(--ink-2, #4a463f); stroke-width: 1; fill: none; }
    .tick { fill: var(--ink-3, #7a756b); font-size: 10px; }
    .ray { stroke: var(--ink-3, #7a756b); stroke-width: 0.8; stroke-dasharray: 2 3; fill: none; }
    .lead { stroke: var(--ink-3, #7a756b); stroke-width: 0.7; fill: none; }
"""

# ---- r–z view layout ------------------------------------------------------------------
RZ_SCALE = 1.3  # px per cm
RZ_LEFT, RZ_BOTTOM = 52.0, 640.0  # px position of z = 0, r = 0

# Polar angles marked in the r–z view: (|cos theta|, label). Sources on the detector page:
# CDC with at least four superlayers and VXD3 with three hits, |cos theta| < 0.85
# (NIM A400; NIM A447); barrel LAC |cos theta| < 0.84 (PRD 53 (1996) 1023).
RAYS: tuple[tuple[float, str], ...] = ((0.85, "|cos θ| = 0.85"),)

# Label placements in the r–z view: key -> (lines, z_cm, r_cm, rotate, leader_to).
LABELS: dict[
    str, tuple[tuple[str, ...], float, float, bool, tuple[float, float] | None]
] = {
    "cdc": (("Central drift", "chamber (CDC)"), 50, 62, False, None),
    "edc_inner": (("Endcap DC",), 113, 60, True, None),
    "crid_barrel": (
        ("Cherenkov ring imaging", "detector (CRID)"),
        68,
        142,
        False,
        None,
    ),
    "crid_endcap": (("Endcap", "CRID"), 172, 45, False, None),
    "edc_outer": (("Endcap DC",), 207, 95, True, None),
    "lac_barrel": (("Liquid argon calorimeter (LAC)",), 160, 238, False, None),
    "lac_endcap": (("Endcap", "LAC"), 291, 100, False, None),
    "coil": (("Solenoid coil, 0.6 T",), 160, 313, False, None),
    "wic_barrel": (("Warm iron calorimeter (WIC)",), 160, 400, False, None),
    "wic_endcap": (("Endcap WIC", "(door)"), 426, 250, False, None),
    "lum": (("Luminosity monitor",), 150, -16, False, (112, 7)),
}


def rz(z: float, r: float) -> tuple[float, float]:
    return RZ_LEFT + z * RZ_SCALE, RZ_BOTTOM - r * RZ_SCALE


def tint(token: str, opacity: float) -> str:
    return f' fill="{color(token)}" fill-opacity="{opacity}" stroke="{color(token)}"'


def make_rz() -> None:
    width = RZ_LEFT + QUADRANT_Z_MAX * RZ_SCALE + 20
    fig = Figure(width, RZ_BOTTOM + 48, "drz", style=STYLE)
    for vol in VOLUMES:
        _, token = GROUPS[vol.group]
        fig.polygon(
            [rz(z, r) for z, r in vol.outline], cls="vol", extra=tint(token, 0.18)
        )
    # VXD3, too small at this scale, drawn as a mark at the origin.
    x0, y0 = rz(0, 0)
    fig.rect(
        x0,
        y0 - 5 * RZ_SCALE,
        8 * RZ_SCALE,
        5 * RZ_SCALE,
        cls="vol",
        extra=tint("box-definition", 0.6),
    )
    for cos_theta, text in RAYS:
        theta = math.acos(cos_theta)
        r_end = 96.0
        z_end = r_end / math.tan(theta)
        fig.line(*rz(0, 0), *rz(z_end, r_end), cls="ray")
        fig.text(*rz(48, 22), text, cls="tick", anchor="start")
    for key, (lines, z, r, rotate, leader) in LABELS.items():
        x, y = rz(z, r)
        if leader:
            fig.line(*rz(*leader), x, y - 12, cls="lead")
        for i, line in enumerate(lines):
            yy = y + (i - (len(lines) - 1) / 2) * 13 + 4
            extra = f' transform="rotate(-90 {num(x)} {num(y)})"' if rotate else ""
            fig.text(
                x,
                yy if not rotate else y + 4,
                line,
                cls="vl" if not leader else "vs",
                extra=extra,
            )
    fig.text(x0 + 14, y0 - 10, "VXD3", cls="vs", anchor="start")
    # Axes.
    fig.line(*rz(0, 0), *rz(QUADRANT_Z_MAX, 0), cls="ax")
    fig.line(*rz(0, 0), *rz(0, QUADRANT_R_MAX), cls="ax")
    for m in range(6):
        x, y = rz(m * 100, 0)
        fig.line(x, y, x, y + 4, cls="ax")
        fig.text(x, y + 30, f"{m}", cls="tick")
    for m in range(5):
        x, y = rz(0, m * 100)
        fig.line(x - 4, y, x, y, cls="ax")
        fig.text(x - 8, y + 3.5, f"{m}", cls="tick", anchor="end")
    fig.text(*rz(QUADRANT_Z_MAX / 2, 0), "", cls="tick")
    fig.text(
        RZ_LEFT + QUADRANT_Z_MAX * RZ_SCALE,
        RZ_BOTTOM + 44,
        "z (m), along the beam",
        cls="tick",
        anchor="end",
    )
    fig.text(
        14,
        RZ_BOTTOM - QUADRANT_R_MAX * RZ_SCALE - 6,
        "r (m)",
        cls="tick",
        anchor="start",
    )
    fig.text(*rz(2, -10), "IP", cls="tick", anchor="start")
    fig.write(FIGURES_DIR / "sld-detector-rz.svg")


def regular_polygon(
    cx: float, cy: float, apothem: float, sides: int, phase: float = 0.0
):
    """Vertices of a regular polygon with the given apothem, a flat side facing +x."""
    radius = apothem / math.cos(math.pi / sides)
    return [
        (
            cx + radius * math.cos(phase + math.pi / sides * (2 * k + 1)),
            cy - radius * math.sin(phase + math.pi / sides * (2 * k + 1)),
        )
        for k in range(sides)
    ]


def make_xy() -> None:
    scale = 0.78  # px per cm
    size = 2 * 470 * scale + 30
    cx = cy = size / 2
    fig = Figure(size, size + 16, "dxy", style=STYLE)
    by_key = {v.key: v for v in VOLUMES}

    def radii(key: str) -> tuple[float, float]:
        vol = by_key[key]
        inner = (
            vol.outline[0][1]
            if key in ("lac_barrel", "crid_barrel")
            else min(r for _, r in vol.outline)
        )
        return inner, max(r for _, r in vol.outline)

    def ring(key: str) -> None:
        vol = by_key[key]
        _, token = GROUPS[vol.group]
        r_in, r_out = radii(key)
        if vol.sides:
            outer = regular_polygon(cx, cy, r_out * scale, vol.sides)
            inner = regular_polygon(cx, cy, r_in * scale, vol.sides)
            d = (
                "M"
                + " L".join(f"{num(x)} {num(y)}" for x, y in outer)
                + " Z M"
                + " L".join(f"{num(x)} {num(y)}" for x, y in reversed(inner))
                + " Z"
            )
        else:
            ro, ri = r_out * scale, r_in * scale
            d = (
                f"M{num(cx + ro)} {num(cy)} a{num(ro)} {num(ro)} 0 1 0 {num(-2 * ro)} 0 "
                f"a{num(ro)} {num(ro)} 0 1 0 {num(2 * ro)} 0 Z M{num(cx + ri)} {num(cy)} "
                f"a{num(ri)} {num(ri)} 0 1 1 {num(-2 * ri)} 0 a{num(ri)} {num(ri)} 0 1 1 "
                f"{num(2 * ri)} 0 Z"
            )
        fig.path(d, cls="vol", extra=tint(token, 0.18) + ' fill-rule="evenodd"')

    for key in ("wic_barrel", "coil", "lac_barrel", "crid_barrel", "cdc"):
        ring(key)
    # The 48 LAC barrel modules (NIM A328 (1993) 472), as faint boundaries joining the
    # vertices of the inner and outer 48-gons, so that each module is one facet.
    r_in, r_out = radii("lac_barrel")
    sides = by_key["lac_barrel"].sides
    for (x1, y1), (x2, y2) in zip(
        regular_polygon(cx, cy, r_in * scale, sides),
        regular_polygon(cx, cy, r_out * scale, sides),
    ):
        fig.line(
            x1,
            y1,
            x2,
            y2,
            cls="ray",
            extra=' stroke-dasharray="none" stroke-opacity="0.5"',
        )
    fig.circle(cx, cy, 5 * scale, cls="vol", extra=tint("box-definition", 0.6))
    # Labels inside each ring, below the centre.
    for key, text in (
        ("wic_barrel", "Warm iron calorimeter (WIC)"),
        ("coil", "Solenoid coil"),
        ("lac_barrel", "Liquid argon calorimeter (LAC)"),
        ("crid_barrel", "Cherenkov ring imaging (CRID)"),
        ("cdc", "CDC"),
    ):
        r_in, r_out = radii(key)
        fig.text(
            cx,
            cy + (r_in + r_out) / 2 * scale + 4,
            text,
            cls="vl" if key != "coil" else "vs",
        )
    fig.text(cx + 14, cy - 8, "VXD3", cls="vs", anchor="start")
    fig.text(
        cx,
        size + 10,
        "view along the beam, to scale; the WIC is an octagon and the LAC "
        "has 48 modules",
        cls="tick",
    )
    fig.write(FIGURES_DIR / "sld-detector-xy.svg")


def make_vxd3() -> None:
    scale = 60.0  # px per cm
    size = 2 * 5.6 * scale
    cx = cy = size / 2
    fig = Figure(size + 230, size, "vx3", style=STYLE)
    fig.circle(cx, cy, BEAM_PIPE_RADIUS * scale, cls="vol", extra=tint("ink-2", 0.08))
    ladder_width = (
        1.6  # cm, the CCD width across the ladder (NIM A400: 80 x 16 mm^2 CCDs)
    )
    cant = {12: 10.0, 16: 9.0, 20: 9.0}  # degrees, NIM A400 Table 2
    for i, (radius, n_ladders) in enumerate(VXD3_LAYERS):
        tilt = math.radians(cant[n_ladders])
        for k in range(n_ladders):
            phi = 2 * math.pi * k / n_ladders
            px, py = radius * math.cos(phi), radius * math.sin(phi)
            tx, ty = -math.sin(phi + tilt), math.cos(phi + tilt)
            x1, y1 = (
                cx + (px - tx * ladder_width / 2) * scale,
                cy - (py - ty * ladder_width / 2) * scale,
            )
            x2, y2 = (
                cx + (px + tx * ladder_width / 2) * scale,
                cy - (py + ty * ladder_width / 2) * scale,
            )
            fig.line(
                x1,
                y1,
                x2,
                y2,
                cls="ln",
                extra=f' stroke="{color("box-definition")}" stroke-width="3"',
            )
        label_r = radius + 0.42
        fig.text(
            cx - label_r * scale * math.cos(math.radians(30)),
            cy + label_r * scale * math.sin(math.radians(30)) + 4,
            str(i + 1),
            cls="vl",
        )
    lx = size + 16
    rows = [
        f"{i + 1}: r = {r:.2f} cm, {n} ladders" for i, (r, n) in enumerate(VXD3_LAYERS)
    ]
    rows.append(f"beam pipe: inner r = {BEAM_PIPE_RADIUS:.2f} cm")
    fig.text(lx, 40, "VXD3 LAYERS", cls="tick caps", anchor="start")
    for i, row in enumerate(rows):
        fig.text(lx, 64 + i * 22, row, cls="vs", anchor="start")
    fig.text(
        lx,
        64 + len(rows) * 22 + 10,
        "two 80 \u00d7 16 mm CCDs per ladder;",
        cls="tick",
        anchor="start",
    )
    fig.text(
        lx,
        64 + len(rows) * 22 + 24,
        "ladders canted by 9\u201310\u00b0",
        cls="tick",
        anchor="start",
    )
    fig.write(FIGURES_DIR / "sld-vxd3-xy.svg")


def main() -> None:
    make_rz()
    make_xy()
    make_vxd3()


if __name__ == "__main__":
    main()
