"""Draw the Feynman diagrams of the SLD chapter.

Writes, next to this directory's parent:
- sld-feynman-z.svg: e+e- -> gamma*/Z -> f fbar, and e+e- -> Z -> q qbar g;
- sld-feynman-bhabha.svg: Bhabha scattering, s- and t-channel photon exchange;
- sld-feynman-compton.svg: Compton scattering of the beam electron on a laser photon;
- sld-feynman-tau.svg: the decay tau- -> nu_tau pi- through a virtual W.
"""

from __future__ import annotations

from pathlib import Path

from feynman import boson, fermion, gluon, label, meson, new_figure, panel_label, vertex

FIGURES_DIR = Path(__file__).resolve().parent.parent
BAR = "̄"  # combining macron, written after the letter it bars
MINUS, PLUS = "⁻", "⁺"  # superscript minus and plus


def s_channel(
    fig, x0: float, y0: float, mid: str, out_top: str, out_bottom: str
) -> None:
    """e- e+ annihilating into `mid`, which decays to `out_top` and `out_bottom`."""
    v1, v2 = (x0 + 70, y0 + 60), (x0 + 150, y0 + 60)
    fermion(fig, x0 + 5, y0 + 10, *v1)
    fermion(fig, x0 + 5, y0 + 110, *v1, forward=False)
    boson(fig, *v1, *v2)
    fermion(fig, *v2, x0 + 215, y0 + 10)
    fermion(fig, *v2, x0 + 215, y0 + 110, forward=False)
    for v in (v1, v2):
        vertex(fig, *v)
    label(fig, x0 + 2, y0 + 8, f"e{MINUS}", anchor="end")
    label(fig, x0 + 2, y0 + 118, f"e{PLUS}", anchor="end")
    label(fig, x0 + 110, y0 + 46, mid)
    label(fig, x0 + 220, y0 + 8, out_top, anchor="start")
    label(fig, x0 + 220, y0 + 118, out_bottom, anchor="start")


def make_z() -> None:
    fig = new_figure(560, 162, "fz")
    panel_label(fig, 4, 14, "(a)")
    s_channel(fig, 30, 30, "γ*, Z", "f", f"f{BAR}")
    panel_label(fig, 284, 14, "(b)")
    x0, y0 = 310, 30
    v1, v2 = (x0 + 70, y0 + 60), (x0 + 150, y0 + 60)
    emit = (x0 + 182, y0 + 36)
    fermion(fig, x0 + 5, y0 + 10, *v1)
    fermion(fig, x0 + 5, y0 + 110, *v1, forward=False)
    boson(fig, *v1, *v2)
    fermion(fig, *v2, *emit)
    fermion(fig, *emit, x0 + 215, y0 + 10)
    fermion(fig, *v2, x0 + 215, y0 + 110, forward=False)
    gluon(fig, *emit, x0 + 222, y0 + 62)
    for v in (v1, v2, emit):
        vertex(fig, *v)
    label(fig, x0 + 2, y0 + 8, f"e{MINUS}", anchor="end")
    label(fig, x0 + 2, y0 + 118, f"e{PLUS}", anchor="end")
    label(fig, x0 + 110, y0 + 46, "Z")
    label(fig, x0 + 220, y0 + 8, "q", anchor="start")
    label(fig, x0 + 228, y0 + 70, "g", anchor="start")
    label(fig, x0 + 220, y0 + 118, f"q{BAR}", anchor="start")
    fig.write(FIGURES_DIR / "sld-feynman-z.svg")


def make_bhabha() -> None:
    fig = new_figure(560, 162, "fb")
    panel_label(fig, 4, 14, "(a)")
    s_channel(fig, 30, 30, "γ*, Z", f"e{MINUS}", f"e{PLUS}")
    panel_label(fig, 284, 14, "(b)")
    x0, y0 = 330, 30
    top, bottom = (x0 + 100, y0 + 25), (x0 + 100, y0 + 95)
    fermion(fig, x0, y0 + 10, *top)
    fermion(fig, *top, x0 + 200, y0 + 10)
    fermion(fig, x0, y0 + 110, *bottom, forward=False)
    fermion(fig, *bottom, x0 + 200, y0 + 110, forward=False)
    boson(fig, *top, *bottom)
    for v in (top, bottom):
        vertex(fig, *v)
    label(fig, x0 - 3, y0 + 8, f"e{MINUS}", anchor="end")
    label(fig, x0 - 3, y0 + 118, f"e{PLUS}", anchor="end")
    label(fig, x0 + 112, y0 + 64, "γ", anchor="start")
    label(fig, x0 + 205, y0 + 8, f"e{MINUS}", anchor="start")
    label(fig, x0 + 205, y0 + 118, f"e{PLUS}", anchor="start")
    fig.write(FIGURES_DIR / "sld-feynman-bhabha.svg")


def make_compton() -> None:
    fig = new_figure(560, 162, "fc")
    panel_label(fig, 4, 14, "(a)")
    x0, y0 = 40, 30
    v1, v2 = (x0 + 70, y0 + 60), (x0 + 150, y0 + 60)
    fermion(fig, x0, y0 + 10, *v1)
    boson(fig, x0, y0 + 110, *v1)
    fermion(fig, *v1, *v2)
    fermion(fig, *v2, x0 + 215, y0 + 10)
    boson(fig, *v2, x0 + 215, y0 + 110)
    for v in (v1, v2):
        vertex(fig, *v)
    label(fig, x0 - 3, y0 + 8, f"e{MINUS}", anchor="end")
    label(fig, x0 - 3, y0 + 118, "γ", anchor="end")
    label(fig, x0 + 220, y0 + 8, f"e{MINUS}", anchor="start")
    label(fig, x0 + 220, y0 + 118, "γ", anchor="start")
    panel_label(fig, 284, 14, "(b)")
    x0 = 330
    top, bottom = (x0 + 100, y0 + 25), (x0 + 100, y0 + 95)
    fermion(fig, x0, y0 + 10, *top)
    fermion(fig, *top, *bottom)
    fermion(fig, *bottom, x0 + 200, y0 + 110)
    boson(fig, x0, y0 + 110, *bottom)
    boson(fig, *top, x0 + 200, y0 + 10)
    for v in (top, bottom):
        vertex(fig, *v)
    label(fig, x0 - 3, y0 + 8, f"e{MINUS}", anchor="end")
    label(fig, x0 - 3, y0 + 118, "γ", anchor="end")
    label(fig, x0 + 205, y0 + 8, "γ", anchor="start")
    label(fig, x0 + 205, y0 + 118, f"e{MINUS}", anchor="start")
    fig.write(FIGURES_DIR / "sld-feynman-compton.svg")


def make_tau() -> None:
    fig = new_figure(300, 162, "ft")
    x0, y0 = 30, 30
    v1, v2 = (x0 + 90, y0 + 60), (x0 + 175, y0 + 95)
    fermion(fig, x0, y0 + 60, *v1)
    fermion(fig, *v1, x0 + 230, y0 + 10)
    boson(fig, *v1, *v2)
    meson(fig, *v2, x0 + 230, y0 + 115)
    for v in (v1, v2):
        vertex(fig, *v)
    label(fig, x0 - 4, y0 + 65, f"τ{MINUS}", anchor="end")
    label(fig, x0 + 235, y0 + 8, "ν_{τ}", anchor="start")
    label(fig, x0 + 120, y0 + 98, f"W{MINUS}*", anchor="end")
    label(fig, x0 + 235, y0 + 122, f"π{MINUS}", anchor="start")
    fig.write(FIGURES_DIR / "sld-feynman-tau.svg")


def main() -> None:
    make_z()
    make_bhabha()
    make_compton()
    make_tau()


if __name__ == "__main__":
    main()
