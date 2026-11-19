"""Draw the processing chains of simulated and recorded events (sld-processing-chains.svg).

Program names follow the SLD documentation cited on the simulation page: MCSLC for the
beam, MCL74 (JETSET 7.4) and KORALZ as generators, GEANT 3 run as the GSIM processor,
RECSLD for reconstruction, the PASS1 filter and the PASS2 first reconstruction for
recorded data, re-reconstruction with frozen code for physics, and the compressed mini-DST
(memo of December 1995). PASS1 dropped about 97% of the triggers in 1993, and PASS2 and the
physics re-reconstructions both start from the events that passed the PASS1 filters
(R. Dubois, "Pass1 & Pass2 Processing of Data", and R. Dubois, "SLD Primer", section
"Versions of Reconstructed Data", both SLD web documentation cited on the page).
"""

from __future__ import annotations

from pathlib import Path

from flow import FLOW_STYLE, down_arrow, right_arrow, stage
from svgkit import Figure

FIGURES_DIR = Path(__file__).resolve().parent.parent


def main() -> None:
    fig = Figure(760, 330, "pc", style=FLOW_STYLE)
    w, h, gap = 112, 64, 18
    fig.text(10, 22, "SIMULATED EVENTS", cls="lane", anchor="start")
    y_mc = 34
    beam = stage(
        fig, 10, y_mc, w, h, "Beam", ("MCSLC:", "energies, IP, helicity"), "box-warning"
    )
    gen = stage(
        fig,
        10 + (w + gap),
        y_mc,
        w,
        h,
        "Generator",
        ("MCL74 (JETSET 7.4),", "KORALZ for τ pairs"),
        "box-warning",
    )
    sim = stage(
        fig,
        10 + 2 * (w + gap),
        y_mc,
        w,
        h,
        "Detector",
        ("GEANT 3 (GSIM):", "hits of every particle"),
        "box-warning",
    )
    ovl = stage(
        fig,
        10 + 3 * (w + gap),
        y_mc,
        w,
        h,
        "Overlay",
        ("+ raw data of a", "random-trigger event"),
        "box-warning",
        dashed=True,
    )
    for a, b in ((beam, gen), (gen, sim), (sim, ovl)):
        right_arrow(fig, a, b)
    fig.text(
        10 + 2 * (w + gap) + w / 2,
        y_mc + h + 16,
        "truth: MCBEAM, MCHEAD, MCPART",
        cls="note",
    )
    fig.text(10, 214, "RECORDED EVENTS", cls="lane", anchor="start")
    y_data = 226
    acq = stage(
        fig,
        10,
        y_data,
        w,
        h,
        "Readout",
        ("detector data", "of a trigger"),
        "box-definition",
    )
    p1 = stage(
        fig,
        10 + (w + gap),
        y_data,
        w,
        h,
        "PASS1",
        ("drops about 97% of", "triggers (1993)"),
        "box-definition",
    )
    p2 = stage(
        fig,
        10 + 2 * (w + gap),
        y_data,
        w,
        h,
        "PASS2",
        ("first reconstruction,", "event-class tags"),
        "box-definition",
    )
    for a, b in ((acq, p1), (p1, p2)):
        right_arrow(fig, a, b)
    x_rec = 10 + 4 * (w + gap) - 6
    rec = stage(
        fig, x_rec, 130, w, h, "Reconstruction", ("RECSLD, frozen", "production code")
    )
    dst = stage(fig, x_rec + w + gap - 4, 130, 90, h, "DST", ("full output",))
    fig.arrow_line(ovl[0] + w + 2, y_mc + h / 2, x_rec + w / 2, 128)
    # The physics reconstruction starts from the PASS1 output, beside PASS2.
    rec_mid = rec[1] + h / 2
    fig.polyline(
        [(p1[0] + w / 2, y_data - 2), (p1[0] + w / 2, rec_mid), (x_rec - 3, rec_mid)],
        extra=f' marker-end="{fig.arrow("arrow-ink-2", "ink-2")}"',
    )
    fig.text(p2[0] + w / 2, y_data + h + 16, "not used for physics", cls="note")
    right_arrow(fig, rec, dst)
    mini = stage(
        fig,
        x_rec + w + gap - 4,
        230,
        90,
        h,
        "Mini-DST",
        ("compressed", "format"),
        "accent",
        0.14,
    )
    down_arrow(fig, dst, mini)
    fig.text(x_rec + w / 2, rec[1] + h + 16, "same code for data and MC", cls="note")
    fig.text(x_rec + w + gap + 41, 310, "the format of this chapter", cls="note")
    fig.write(FIGURES_DIR / "sld-processing-chains.svg")


if __name__ == "__main__":
    main()
