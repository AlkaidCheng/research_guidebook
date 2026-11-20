"""SLD detector geometry for the figures: one table of volumes, each with its source.

Coordinates are in cm, in the r–z half-plane of one quadrant (z along the beam, r the
distance from it), for the detector as it ran from 1996 to 1998 (VXD3 installed, MASiC
removed). Where a published as-built number exists it is used and cited; the remaining
outlines are read from the to-scale SLD quadrant drawing (SLAC drawing 7282A02, 1993) and
flagged ``approximate``. The source keys match the ``references`` of the chapter's detector
page.
"""

from __future__ import annotations

from dataclasses import dataclass

# ---- Volumes --------------------------------------------------------------------------


@dataclass(frozen=True)
class Volume:
    """One detector volume in the r–z quadrant.

    Parameters
    ----------
    key : str
        Short identifier, also used by the 3D viewer.
    name : str
        Label in the figures.
    group : str
        Subsystem group, which sets the colour.
    outline : tuple of (z, r)
        Closed polygon in cm, z >= 0, r >= 0.
    sides : int or None
        Number of sides of the cross-section in x–y, or None for a circle.
    source : str
        Reference keys of the numbers.
    approximate : bool
        True if any coordinate is read from the drawing.
    """

    key: str
    name: str
    group: str
    outline: tuple[tuple[float, float], ...]
    sides: int | None
    source: str
    approximate: bool


def box(z0: float, z1: float, r0: float, r1: float) -> tuple[tuple[float, float], ...]:
    """The rectangle z0..z1 by r0..r1 as a closed (z, r) polygon."""
    return ((z0, r0), (z1, r0), (z1, r1), (z0, r1))


# Subsystem group -> (legend text, theme token).
GROUPS: dict[str, tuple[str, str]] = {
    "tracking": ("Tracking: VXD3, CDC, endcap DC", "box-definition"),
    "pid": ("Cherenkov ring imaging (CRID)", "box-example"),
    "calorimetry": ("Liquid argon calorimeter (LAC)", "box-warning"),
    "magnet": ("Solenoid coil", "ink-3"),
    "muon": ("Warm iron calorimeter (WIC)", "box-remark"),
    "lum": ("Luminosity monitor", "box-recipe"),
    "beam": ("Beam line", "ink-2"),
}

VOLUMES: tuple[Volume, ...] = (
    Volume(
        "cdc",
        "CDC",
        "tracking",
        box(0, 100, 20, 100),
        None,
        "hildreth1995cdc; drawing7282",
        False,
    ),
    Volume(
        "edc_inner",
        "Endcap DC",
        "tracking",
        box(102.7, 123.9, 20.3, 97.8),
        None,
        "drawing7282; sld1984design",
        True,
    ),
    # Barrel CRID: outline read from the drawing; its outer wall is the LAC inner wall at
    # 177.5 cm (NIM A328, Table III), and the 1984 layout gives 102-175 cm.
    Volume(
        "crid_barrel",
        "CRID",
        "pid",
        (
            (0, 102.8),
            (140.0, 102.8),
            (145.2, 107.9),
            (145.2, 132.3),
            (195.9, 177.5),
            (0, 177.5),
        ),
        None,
        "breidenbach1986overview; axen1993lac; drawing7282",
        True,
    ),
    # Endcap CRID vessels: z 124-196 cm, r 20-146 cm (IEEE TNS 42 (1995) 518); the
    # outline under the barrel CRID's slanted end is read from the drawing and cut at 146 cm.
    Volume(
        "crid_endcap",
        "Endcap CRID",
        "pid",
        (
            (124.0, 20.0),
            (196.0, 20.0),
            (196.0, 146.0),
            (168.0, 146.0),
            (150.0, 130.0),
            (150.0, 98.0),
            (124.0, 98.0),
        ),
        None,
        "abe1995ecrid; drawing7282",
        True,
    ),
    Volume(
        "edc_outer",
        "Endcap DC",
        "tracking",
        box(196.3, 217.5, 22.3, 166.2),
        None,
        "drawing7282; sld1984design",
        True,
    ),
    # LAC vacuum vessels, NIM A328 (1993) 472, Table III, converted from inches:
    # barrel r 69.875 in to 113.187 + 1.375 in, |z| to 134.167 + 2.250 in;
    # endcap r 7.875 in to 66.062 + 1.250 in, z 87.086 in to 139.179 + 2.750 in.
    Volume(
        "lac_barrel",
        "LAC",
        "calorimetry",
        box(0, 346.5, 177.5, 291.0),
        48,
        "axen1993lac",
        False,
    ),
    Volume(
        "lac_endcap",
        "Endcap LAC",
        "calorimetry",
        box(221.2, 360.5, 20.0, 171.0),
        None,
        "axen1993lac",
        False,
    ),
    Volume(
        "coil",
        "Coil",
        "magnet",
        box(0, 328.2, 296.1, 325.9),
        None,
        "breidenbach1986overview; drawing7282",
        True,
    ),
    Volume(
        "wic_barrel",
        "WIC",
        "muon",
        box(0, 341.7, 334.1, 459.8),
        8,
        "benvenuti1989wic; drawing7282",
        True,
    ),
    Volume(
        "wic_endcap",
        "Endcap WIC (door)",
        "muon",
        box(362.1, 490.0, 41.6, 449.8),
        8,
        "benvenuti1989wic; drawing7282",
        True,
    ),
    Volume(
        "lum",
        "LUM",
        "lum",
        box(101.0, 122.4, 3.0, 11.1),
        None,
        "berridge1992lum; drawing7282",
        True,
    ),
    # Beam-line structure in the bore of the endcap door, unnamed in the drawing. It is not
    # the final focus: the last superconducting quadrupole sits about 1.5 m from the IP
    # (SLD primer, Final Focus), and the luminosity monitor is mounted on the triplet
    # (SLAC-R-446, p. 46).
    Volume(
        "door_bore",
        "Beam-line structure in the endcap door",
        "beam",
        box(357.1, 500.0, 33.4, 41.6),
        None,
        "drawing7282",
        True,
    ),
)

# ---- VXD3 -----------------------------------------------------------------------------
# NIM A400 (1997) 287, Table 2: mean layer radii (cm), ladders per layer; ladder length
# 15.9 cm from NIM A447 (2000) 90; beam pipe inner radius 2.32 cm (NIM A400, Table 2).
VXD3_LAYERS: tuple[tuple[float, int], ...] = ((2.80, 12), (3.82, 16), (4.83, 20))
VXD3_HALF_LENGTH = 15.9 / 2
BEAM_PIPE_RADIUS = 2.32

# ---- Overall --------------------------------------------------------------------------
QUADRANT_Z_MAX = 500.0  # cm, the drawing's z axis ends at 5 m
QUADRANT_R_MAX = 460.0  # cm, the outer edge of the barrel WIC in the drawing
SOLENOID_FIELD_T = 0.6  # Hildreth et al., IEEE TNS 42 (1995) 451
