"""Draw the comparison of sin^2 theta_eff^lept determinations (sld-sin2theta.svg).

Values: the six determinations and their average from Phys. Rept. 427 (2006) 257,
Sec. 7.3.4, Fig. 7.6 and Eq. (7.11); the dataset paper's value from Mach. Learn.: Sci.
Technol. 7 (2026) 050602, Table I, which uses the raw A_LR without the pole correction.
"""

from __future__ import annotations

from pathlib import Path

from svgkit import Figure, color

FIGURES_DIR = Path(__file__).resolve().parent.parent

# (label, experiment, value, error, style)
DETERMINATIONS: tuple[tuple[str, str, float, float, str], ...] = (
    ("A_FB^0,l", "LEP", 0.23099, 0.00053, "lep"),
    ("A_l (P_tau)", "LEP", 0.23159, 0.00041, "lep"),
    ("A_l (SLD)", "SLD", 0.23098, 0.00026, "sld"),
    ("A_FB^0,b", "LEP", 0.23221, 0.00029, "lep"),
    ("A_FB^0,c", "LEP", 0.23220, 0.00081, "lep"),
    ("Q_FB^had", "LEP", 0.2324, 0.0012, "lep"),
)
AVERAGE = (0.23153, 0.00016)  # chi2/dof = 11.8/5
RELEASED = (
    'Released data, raw A<tspan dy="0.32em" font-size="72%">LR</tspan>'
    '<tspan dy="-0.32em"> </tspan>',
    "dataset paper",
    0.23144,
    0.00044,
)

X_MIN, X_MAX = 0.2295, 0.2340
LEFT, RIGHT = 300.0, 740.0
ROW = 30.0

STYLE = """
    .lb { fill: var(--ink, #1d1b17); font-size: 12px; }
    .ex { fill: var(--ink-3, #7a756b); font-size: 10.5px; }
    .tk { fill: var(--ink-3, #7a756b); font-size: 10px; }
    .grid { stroke: var(--rule, #ddd8cc); stroke-width: 0.8; }
    .band { fill: var(--box-definition, #2f5d7c); fill-opacity: 0.14; }
    .bline { stroke: var(--box-definition, #2f5d7c); stroke-width: 1; stroke-dasharray: 4 3; }
"""

LABELS = {
    "A_FB^0,l": 'A<tspan dy="0.32em" font-size="72%">FB</tspan><tspan dy="-0.74em" font-size="72%">0,ℓ</tspan><tspan dy="0.42em"> </tspan>',
    "A_l (P_tau)": '\U0001d49c<tspan dy="0.32em" font-size="72%">ℓ</tspan><tspan dy="-0.32em"> (P</tspan><tspan dy="0.32em" font-size="72%">τ</tspan><tspan dy="-0.32em">)</tspan>',
    "A_l (SLD)": '\U0001d49c<tspan dy="0.32em" font-size="72%">ℓ</tspan><tspan dy="-0.32em"> (A</tspan><tspan dy="0.32em" font-size="72%">LR</tspan><tspan dy="-0.32em">, leptons)</tspan>',
    "A_FB^0,b": 'A<tspan dy="0.32em" font-size="72%">FB</tspan><tspan dy="-0.74em" font-size="72%">0,b</tspan><tspan dy="0.42em"> </tspan>',
    "A_FB^0,c": 'A<tspan dy="0.32em" font-size="72%">FB</tspan><tspan dy="-0.74em" font-size="72%">0,c</tspan><tspan dy="0.42em"> </tspan>',
    "Q_FB^had": '⟨Q<tspan dy="0.32em" font-size="72%">FB</tspan><tspan dy="-0.32em">⟩ hadrons</tspan>',
}


def x_of(value: float) -> float:
    return LEFT + (value - X_MIN) / (X_MAX - X_MIN) * (RIGHT - LEFT)


def main() -> None:
    rows = len(DETERMINATIONS) + 2
    top = 20.0
    height = top + rows * ROW + 50
    fig = Figure(760, height, "s2", style=STYLE)
    bottom = top + rows * ROW
    for k in range(10):
        value = 0.2300 + 0.0005 * k
        if value > X_MAX:
            break
        fig.line(x_of(value), top, x_of(value), bottom, cls="grid")
        fig.text(x_of(value), bottom + 16, f"{value:.4f}", cls="tk")
    mean, err = AVERAGE
    fig.rect(
        x_of(mean - err),
        top,
        x_of(mean + err) - x_of(mean - err),
        bottom - top,
        cls="band",
    )
    fig.line(x_of(mean), top, x_of(mean), bottom, cls="bline")
    for i, (key, experiment, value, error, style) in enumerate(DETERMINATIONS):
        y = top + (i + 0.5) * ROW
        token = "accent" if style == "sld" else "ink-2"
        fig.text(LEFT - 110, y + 4, LABELS[key], cls="lb", anchor="end")
        fig.text(LEFT - 12, y + 4, experiment, cls="ex", anchor="end")
        fig.line(
            x_of(value - error),
            y,
            x_of(value + error),
            y,
            extra=f' stroke="{color(token)}" stroke-width="1.6"',
        )
        fig.circle(
            x_of(value), y, 4, cls="", extra=f' fill="{color(token)}" stroke="none"'
        )
    y = top + (len(DETERMINATIONS) + 0.5) * ROW
    fig.text(LEFT - 110, y + 4, "Average of the six", cls="lb", anchor="end")
    fig.text(LEFT - 12, y + 4, "χ²/dof 11.8/5", cls="ex", anchor="end")
    fig.line(
        x_of(mean - err),
        y,
        x_of(mean + err),
        y,
        extra=f' stroke="{color("box-definition")}" stroke-width="1.6"',
    )
    fig.rect(
        x_of(mean) - 4,
        y - 4,
        8,
        8,
        cls="",
        extra=f' fill="{color("box-definition")}" stroke="none"',
    )
    label, experiment, value, error = RELEASED
    y = top + (len(DETERMINATIONS) + 1.5) * ROW
    fig.text(LEFT - 110, y + 4, label, cls="lb", anchor="end")
    fig.text(LEFT - 12, y + 4, experiment, cls="ex", anchor="end")
    fig.line(
        x_of(value - error),
        y,
        x_of(value + error),
        y,
        extra=f' stroke="{color("accent")}" stroke-width="1.6" stroke-dasharray="3 2"',
    )
    fig.circle(
        x_of(value),
        y,
        4,
        cls="",
        extra=f' fill="none" stroke="{color("accent")}" stroke-width="1.5"',
    )
    fig.text(
        RIGHT,
        height - 8,
        'sin<tspan dy="-0.42em" font-size="72%">2</tspan>'
        '<tspan dy="0.42em">θ</tspan><tspan dy="0.32em" font-size="72%">eff</tspan>'
        '<tspan dy="-0.74em" font-size="72%">lept</tspan>',
        cls="tk",
        anchor="end",
    )
    fig.write(FIGURES_DIR / "sld-sin2theta.svg")


if __name__ == "__main__":
    main()
