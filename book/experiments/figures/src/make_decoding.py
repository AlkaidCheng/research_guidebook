"""Draw the figures of the decoding procedure.

- sld-decoding-workflow.svg: the two levels, structure (deterministic) and meanings (agentic);
- sld-decoding-closure.svg: the record tail as blocks sized by the TOC counts and the PHVXOV hit
  counts;
- sld-decoding-profile.svg: the harness's word profile of the data PHBM block.
"""

from __future__ import annotations

from pathlib import Path

import json

import yaml

from flow import FLOW_STYLE, right_arrow, stage
from svgkit import Figure, color

SRC_DIR = Path(__file__).resolve().parent
FIGURES_DIR = SRC_DIR.parent
PROFILE_PATH = SRC_DIR / "data" / "phbm_profile.json"
LAYOUT_PATH = SRC_DIR / "data" / "banks_layout.yaml"
# Word classes of the profile -> (legend, theme token).
WORD_CLASSES = {
    "float": ("VAX F float", "box-definition"),
    "zero": ("zero", "ink-3"),
    "int": ("small integer", "box-remark"),
    "other": ("other", "accent"),
}


def make_workflow() -> None:
    fig = Figure(760, 476, "dw", style=FLOW_STYLE)
    fig.text(10, 20, "LEVEL 1: STRUCTURE, DETERMINISTIC", cls="lane", anchor="start")
    w, h = 170, 58
    census = stage(
        fig, 10, 32, w, h, "Census", ("every record: header,", "TOC counts, length")
    )
    harness = stage(
        fig,
        205,
        32,
        330,
        h,
        "Harness checks",
        (
            "closure to the buffer end · XBEAM start signature",
            "PHVXOV header consistency · PHBM anchor",
        ),
    )
    layout = stage(
        fig,
        570,
        32,
        w,
        h,
        "Layout fixed",
        ("order and sizes", "of every block"),
        "box-example",
        0.14,
    )
    right_arrow(fig, census, harness)
    right_arrow(fig, harness, layout)
    fig.text(
        10,
        110,
        "LEVEL 2: MEANINGS, ONE AGENTIC LOOP PER BANK GROUP",
        cls="lane",
        anchor="start",
    )
    dossier = stage(
        fig,
        10,
        138,
        w,
        70,
        "Dossier",
        ("templates, memos, papers;", "each claim dated and", "sourced; hints only"),
        "box-remark",
    )
    blind = stage(
        fig,
        205,
        138,
        150,
        70,
        "Round 1, blind",
        ("no dossier, template", "or memo; fields from", "word profiles, sample"),
        "box-recipe",
    )
    refine = stage(
        fig,
        385,
        138,
        150,
        70,
        "Rounds 2 to 4",
        ("expected result first,", "edit the spec only,", "run the harness"),
        "box-recipe",
    )
    labels = stage(
        fig,
        570,
        138,
        w,
        70,
        "Labels per field",
        ("confirmed, plausible", "or unknown"),
        "box-example",
        0.14,
    )
    # The dossier is compiled alongside round 1 and read from round 2 on.
    dossier_x = dossier[0] + dossier[2] / 2
    dossier_bottom = dossier[1] + dossier[3]
    entry_y = refine[1] + 58
    fig.polyline(
        [
            (dossier_x, dossier_bottom + 2),
            (dossier_x, dossier_bottom + 18),
            (refine[0] - 15, dossier_bottom + 18),
            (refine[0] - 15, entry_y),
            (refine[0] - 3, entry_y),
        ],
        cls="ln",
        extra=f' marker-end="{fig.arrow("arrow-ink-2")}"',
    )
    fig.text(232, dossier_bottom + 32, "read from round 2", cls="note")
    right_arrow(fig, blind, refine)
    right_arrow(fig, refine, labels)
    fig.path(
        f"M{385 + 120} 210 q0 22 -45 22 q-45 0 -45 -22",
        cls="ln",
        extra=f' marker-end="{fig.arrow("arrow-ink-2")}"',
    )
    fig.text(460, 248, "until a round converges or two rounds", cls="note")
    fig.text(460, 261, "pass without progress; at most round 4", cls="note")
    # The fixed structure is the input of every round.
    structure_y = 124
    structure_x = layout[0] + 30
    fig.polyline(
        [
            (structure_x, layout[1] + layout[3] + 2),
            (structure_x, structure_y),
            (blind[0] + blind[2] / 2, structure_y),
        ],
        cls="ln",
    )
    for r in (blind, refine):
        fig.arrow_line(r[0] + r[2] / 2, structure_y, r[0] + r[2] / 2, r[1] - 3)
    fig.text(10, 286, "VERIFICATION AND REVIEW", cls="lane", anchor="start")
    vw = 160
    v1 = stage(
        fig,
        10,
        314,
        vw,
        62,
        "Holdout replay",
        ("files no other agent reads",),
        "box-warning",
    )
    v2 = stage(
        fig,
        190,
        314,
        vw,
        62,
        "Physics checks",
        ("against shuffled nulls",),
        "box-warning",
    )
    v3 = stage(
        fig, 370, 314, vw, 62, "Challenger", ("tries other layouts",), "box-warning"
    )
    vote = stage(
        fig,
        555,
        314,
        195,
        62,
        "Verdict rule",
        (
            "two refutations: unknown",
            "two refutations or downgrades:",
            "one level down",
        ),
    )
    fig.line(655, 210, 655, 300, cls="ln")
    fig.line(10 + vw / 2, 300, 655, 300, cls="ln")
    for v in (v1, v2, v3):
        fig.arrow_line(v[0] + vw / 2, 300, v[0] + vw / 2, 311)
    # Every verifier's verdicts go to the rule.
    verdict_y = 390
    vote_entry_x = vote[0] + 45
    for v in (v1, v2, v3):
        fig.line(v[0] + vw / 2, v[1] + v[3] + 2, v[0] + vw / 2, verdict_y, cls="ln")
    fig.line(v1[0] + vw / 2, verdict_y, vote_entry_x, verdict_y, cls="ln")
    fig.arrow_line(vote_entry_x, verdict_y, vote_entry_x, vote[1] + vote[3] + 3)
    synthesis = stage(
        fig,
        205,
        406,
        365,
        58,
        "Synthesis and human review",
        ("then decoders in the reader:", "zero words skipped, leftover words kept raw"),
        "accent",
        0.14,
    )
    vote_exit_x = vote[0] + 145
    fig.polyline(
        [
            (vote_exit_x, vote[1] + vote[3] + 2),
            (vote_exit_x, synthesis[1] + synthesis[3] / 2),
            (synthesis[0] + synthesis[2] + 3, synthesis[1] + synthesis[3] / 2),
        ],
        cls="ln",
        extra=f' marker-end="{fig.arrow("arrow-ink-2")}"',
    )
    fig.write(FIGURES_DIR / "sld-decoding-workflow.svg")


def make_closure() -> None:
    fig = Figure(
        760,
        250,
        "dc",
        style=FLOW_STYLE
        + """
    .blk { fill: var(--ink, #1d1b17); font-size: 10.5px; font-weight: 600; }
""",
    )

    def strip(
        y: float, title: str, blocks: list[tuple[str, str, float, str]]
    ) -> list[float]:
        fig.text(10, y - 8, title, cls="lane", anchor="start")
        x = 10.0
        starts = []
        for name, size, width, token in blocks:
            starts.append(x)
            fig.rect(
                x,
                y,
                width,
                40,
                cls="tf",
                extra=f' fill="{color(token)}" fill-opacity="0.15" stroke="{color(token)}"',
            )
            fig.text(x + width / 2, y + 17, name, cls="blk")
            fig.text(x + width / 2, y + 31, size, cls="sub")
            x += width + 3
        return starts

    strip(
        28,
        "DATA RECORD, AFTER PHKCHRG",
        [
            ("PHBM", "60 B", 90, "ink-3"),
            ("PHEVCL", "72 B", 100, "ink-3"),
            ("reserved", "4 B", 62, "ink-3"),
            ("PHVXOV", "16 + 80 × hits, per bank", 358, "box-definition"),
        ],
    )
    mc = strip(
        118,
        "MC RECORD, AFTER PHKCHRG",
        [
            ("PHKMC1 pass 1", "20 × n", 120, "box-recipe"),
            ("pass 2", "4 × n", 60, "box-recipe"),
            ("PHBM", "60 B", 70, "ink-3"),
            ("PHEVCL", "72 B", 80, "ink-3"),
            ("MCBEAM", "76 B, “XBEAM”", 104, "box-warning"),
            ("reserved", "4 B", 62, "ink-3"),
            ("PHVXOV", "16 + 80 × hits", 140, "box-definition"),
        ],
    )
    fig.arrow_line(mc[0] + 2, 194, mc[0] + 2, 162, token="accent")
    fig.text(
        mc[0] + 8,
        200,
        "jazelle ≤ 0.4.0 reads PHBM here, so its MC PHBM holds PHKMC1 bytes",
        cls="note",
        anchor="start",
    )
    fig.text(
        10,
        236,
        "tail length = 24 n(PHKMC1) + 60 n(PHBM) + 72 n(PHEVCL) + 76 n(MCBEAM) + 4 + "
        "Σ (16 + 80 hits)",
        cls="sub mono",
        anchor="start",
    )
    fig.write(FIGURES_DIR / "sld-decoding-closure.svg")


def make_profile() -> None:
    profile = json.loads(PROFILE_PATH.read_text())["words"]
    fields = yaml.safe_load(LAYOUT_PATH.read_text())["banks"]["PHBM"]["blocks"][0][
        "fields"
    ]
    names = {f["offset"]: f["name"] for f in fields}
    row, bar_w, left = 22.0, 470.0, 150.0
    fig = Figure(760, 40 + row * len(profile) + 30, "dp", style=FLOW_STYLE)
    fig.text(
        left,
        18,
        "SHARE OF RECORDS, PER 4-BYTE WORD OF PHBM",
        cls="lane",
        anchor="start",
    )
    for i, word in enumerate(profile):
        y = 30 + i * row
        fig.text(
            left - 10,
            y + 14,
            f"+{word['offset']}  {names.get(word['offset'], '')}",
            cls="sub mono",
            anchor="end",
        )
        x = left
        for key, (_, token) in WORD_CLASSES.items():
            w = word[key] * bar_w
            if w > 0.2:
                fig.rect(
                    x,
                    y + 3,
                    w,
                    row - 6,
                    cls="tf",
                    extra=f' fill="{color(token)}" fill-opacity="0.45" stroke="none"',
                )
            x += w
    y = 30 + len(profile) * row + 16
    x = left
    for key, (label, token) in WORD_CLASSES.items():
        fig.rect(
            x,
            y - 10,
            12,
            12,
            cls="tf",
            extra=f' fill="{color(token)}" fill-opacity="0.45" stroke="none"',
        )
        fig.text(x + 18, y, label, cls="sub", anchor="start")
        x += 140
    fig.write(FIGURES_DIR / "sld-decoding-profile.svg")


def main() -> None:
    make_workflow()
    make_closure()
    make_profile()


if __name__ == "__main__":
    main()
