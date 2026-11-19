"""Draw the timeline of the SLC, SLD and the data recovery (sld-timeline.svg).

Dates and polarisations, with their sources on the chapter's opening page: SLC design
report June 1980 (SLAC-R-229); construction October 1983 to mid-1987 and the final run
(Phinney, arXiv:physics/0010008); first Z on 11 April 1989 and the end of data taking on
5 June 1998 (SLD SLC-history page); SLD at the IP and its engineering run in 1991, first
polarised Z on 2 May 1992 (same); VXD2 in January 1992 (NIM A400) and VXD3 for the 1996 run, installed in December 1995
to January 1996 (NIM A400, NIM A447);
polarisations per run from PRL 70, 73, 78 and 84; final A_LR in June 2000 (PRL 84);
Phys. Rept. 427 in May 2006; the recovery dates from PyPI, Zenodo, arXiv and the journal.
"""

from __future__ import annotations

from pathlib import Path

from flow import FLOW_STYLE
from svgkit import Figure, color

FIGURES_DIR = Path(__file__).resolve().parent.parent

STYLE = (
    FLOW_STYLE
    + """
    .axis { stroke: var(--ink-2, #4a463f); stroke-width: 1.2; }
    .tk { fill: var(--ink-3, #7a756b); font-size: 10px; }
    .ev { fill: var(--ink, #1d1b17); font-size: 10.5px; }
    .evs { fill: var(--ink-3, #7a756b); font-size: 9.5px; }
    .stem { stroke: var(--ink-3, #7a756b); stroke-width: 0.8; }
"""
)

# Panel 1: the SLC and SLD, 1979 to 2007.
YEAR0, YEAR1 = 1979.5, 2006.8
X0, X1 = 20.0, 740.0
AXIS1 = 120.0
EVENTS_1: tuple[tuple[float, str, str, int], ...] = (
    (1980.45, "SLC design report", "June 1980", 1),
    (1983.8, "SLC construction", "Oct 1983 to 1987", 2),
    (1989.28, "first Z at the SLC", "Mark II, Apr 1989", 1),
    (1991.5, "SLD at the IP", "engineering run 1991", 2),
    (1992.33, "first polarised Z", "2 May 1992", -1),
    (1996.0, "VXD3 installed", "for the 1996 run", 2),
    (1998.43, "last SLD data", "5 Jun 1998", -1),
    (
        2000.48,
        'final A<tspan dy="0.32em" font-size="72%">LR</tspan><tspan dy="-0.32em">\u00a0paper</tspan>',
        "PRL 84, Jun 2000",
        1,
    ),
    (2006.35, "LEP + SLD combination", "Phys. Rept. 427, 2006", 2),
)
# Physics runs with the luminosity-weighted polarisation (PRL 70, 73, 78, 84).
RUNS: tuple[tuple[float, float, str], ...] = (
    (1992.3, 1992.65, "22%"),
    (1993.2, 1993.65, "63%"),
    (1994.4, 1995.4, "77%"),
    (1996.25, 1996.6, "76%"),
    (1997.2, 1998.45, "73%"),
)
# Panel 2: the recovery, October 2025 to December 2026, in months.
MONTH0, MONTH1 = 2025 + 9.5 / 12, 2026 + 12 / 12
AXIS2 = 330.0
EVENTS_2: tuple[tuple[float, str, str, int], ...] = (
    (2025 + 10.55 / 12, "jazelle 0.1.0", "17 Nov 2025", 1),
    (2026 + 3.97 / 12, "Zenodo v1", "30 Apr 2026", 1),
    (2026 + 4.93 / 12, "dataset paper on arXiv", "29 May 2026", -1),
    (2026 + 6.15 / 12, "Zenodo v2", "5 Jul 2026", 2),
    (2026 + 6.22 / 12, "jazelle 0.4.0, sld-resurrect 0.2.0", "7 Jul 2026", -2),
    (2026 + 8.4 / 12, "Zenodo v3, Parnassus paper", "13 Sep 2026", 1),
    (2026 + 8.97 / 12, "dataset paper published", "MLST 7 050602, 30 Sep 2026", -1),
)


def x_year(year: float) -> float:
    return X0 + (year - YEAR0) / (YEAR1 - YEAR0) * (X1 - X0)


def x_month(t: float) -> float:
    return X0 + (t - MONTH0) / (MONTH1 - MONTH0) * (X1 - X0)


LEVEL_OFFSET = {2: -66.0, 1: -38.0, -1: 44.0, -2: 72.0}  # px from the axis to the title


def event(fig: Figure, x: float, axis: float, title: str, sub: str, level: int) -> None:
    y = axis + LEVEL_OFFSET[level]
    fig.line(x, axis, x, y + 6 if level > 0 else y - 12, cls="stem")
    fig.circle(x, axis, 3.2, cls="", extra=f' fill="{color("ink")}" stroke="none"')
    anchor = "start" if x < X0 + 60 else "end" if x > X1 - 70 else "mid"
    tx = x - 4 if anchor == "start" else x + 4 if anchor == "end" else x
    fig.text(tx, y - 12 if level > 0 else y, title, cls="ev", anchor=anchor)
    fig.text(tx, y if level > 0 else y + 12, sub, cls="evs", anchor=anchor)


def main() -> None:
    fig = Figure(760, 430, "tl", style=STYLE)
    fig.text(X0, 18, "THE SLC AND SLD", cls="lane", anchor="start")
    fig.line(X0, AXIS1, X1, AXIS1, cls="axis")
    for year in range(1980, 2007, 2):
        fig.line(x_year(year), AXIS1, x_year(year), AXIS1 + 4, cls="axis")
        fig.text(x_year(year), AXIS1 + 15, str(year), cls="tk")
    for start, end, pol in RUNS:
        fig.rect(
            x_year(start),
            AXIS1 - 8,
            x_year(end) - x_year(start),
            8,
            cls="",
            extra=f' fill="{color("box-definition")}" fill-opacity="0.55" stroke="none"',
        )
    for start, end, pol in RUNS:
        fig.text((x_year(start) + x_year(end)) / 2, AXIS1 - 12, pol, cls="evs")
    fig.text(
        X1,
        AXIS1 + 32,
        "bars: physics runs, with their electron polarisation",
        cls="evs",
        anchor="end",
    )
    for year, title, sub, level in EVENTS_1:
        event(fig, x_year(year), AXIS1, title, sub, level)
    fig.text(X0, 222, "THE RECOVERY", cls="lane", anchor="start")
    fig.line(X0, AXIS2, X1, AXIS2, cls="axis")
    months = ["Nov", "Jan", "Mar", "May", "Jul", "Sep", "Nov"]
    for i, t in enumerate(
        [
            2025 + 10 / 12,
            2026,
            2026 + 2 / 12,
            2026 + 4 / 12,
            2026 + 6 / 12,
            2026 + 8 / 12,
            2026 + 10 / 12,
        ]
    ):
        fig.line(x_month(t), AXIS2, x_month(t), AXIS2 + 4, cls="axis")
        label = months[i] + (" 2026" if i == 1 else " 2025" if i == 0 else "")
        fig.text(x_month(t), AXIS2 + 15, label, cls="tk")
    for t, title, sub, level in EVENTS_2:
        event(fig, x_month(t), AXIS2, title, sub, level)
    fig.write(FIGURES_DIR / "sld-timeline.svg")


if __name__ == "__main__":
    main()
