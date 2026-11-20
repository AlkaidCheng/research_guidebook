"""Draw the mini-DST format figures.

- sld-jazelle-records.svg: physical records, a logical record and its contents;
- sld-record-composition.svg: the families of a data record and of an MC record;
- sld-relations.svg: how the families point to each other, and a two-pass relation table.
"""

from __future__ import annotations

from pathlib import Path

from minidst_families import FAMILIES, GROUPS
from svgkit import Figure, color

FIGURES_DIR = Path(__file__).resolve().parent.parent

STYLE = """
    .seg { stroke: var(--ink-2, #4a463f); stroke-width: 1; }
    .hdr { fill: var(--paper-3, #e9e5db); stroke: var(--ink-2, #4a463f); stroke-width: 1; }
    .ghost { fill: none; stroke: var(--ink-3, #7a756b); stroke-width: 1; stroke-dasharray: 3 3; }
    .brace { stroke: var(--ink-3, #7a756b); stroke-width: 1; fill: none; }
    .nm { fill: var(--ink, #1d1b17); font-size: 11px; font-weight: 600; }
    .sz { fill: var(--ink-2, #4a463f); font-size: 9.5px; }
    .gh { fill: var(--ink-3, #7a756b); font-size: 9.5px; }
    .tf { stroke-width: 1; }
"""


def tint(token: str, opacity: float = 0.16) -> str:
    """Fill and stroke attributes for a box tinted with a theme colour."""
    return f' fill="{color(token)}" fill-opacity="{opacity}" stroke="{color(token)}"'


def make_records() -> None:
    fig = Figure(760, 352, "jr", style=STYLE)
    # Row 1: the file as physical records.
    y1 = 40
    fig.text(10, y1 - 12, "FILE: PHYSICAL RECORDS", cls="t3 caps", anchor="start")
    x = 10
    widths = [70, 140, 140, 140, 140, 90]  # ends at x = 750
    labels = ["file header", "record", "record", "record", "record", "…"]
    starts = []
    for w, name in zip(widths, labels):
        starts.append(x)
        fig.rect(x, y1, w, 34, cls="seg", extra=' fill="none"')
        if name != "…":
            fig.rect(x, y1, 12, 34, cls="hdr")
        fig.text(x + w / 2 + 6, y1 + 21, name, cls="sz")
        x += w + 4
    fig.text(
        10,
        y1 + 52,
        "Each physical record starts with 8 bytes: prlen, prres, lrlen, lrcnt "
        "(shaded).",
        cls="sz",
        anchor="start",
    )
    # A logical record spanning two physical records; the brace ends with its last segment.
    tail_w = 92
    lx0, lx1 = starts[2] + 12, starts[3] + 12 + tail_w
    fig.rect(
        lx0, y1 + 6, starts[2] + 140 - lx0, 22, cls="tf", extra=tint("accent", 0.22)
    )
    fig.rect(starts[3] + 12, y1 + 6, tail_w, 22, cls="tf", extra=tint("accent", 0.22))
    fig.path(
        f"M{lx0} {y1 + 64} q0 6 6 6 h{(lx1 - lx0) / 2 - 12} q6 0 6 6 q0 -6 6 -6 "
        f"h{(lx1 - lx0) / 2 - 12} q6 0 6 -6",
        cls="brace",
    )
    fig.text(
        (lx0 + lx1) / 2,
        y1 + 92,
        "one logical record, here an event; lrcnt bit 0: continues "
        "in the next record, bit 1: continues the previous one",
        cls="sz",
    )
    # Row 2: the logical record.
    y2 = 170
    fig.text(10, y2 - 12, "LOGICAL RECORD", cls="t3 caps", anchor="start")
    parts = [
        ("record header", "112 B", "hdr"),
        ("IEVENTH", "32 B, at usroff", "hdr"),
        ("PHMTOC", "72 B, at tocoff1", "hdr"),
        ("data buffer", "datsiz B, at datoff", ""),
    ]
    x = 10
    pw = [180, 130, 130, 288]  # ends at x = 750, as the rows above and below
    for (name, size, cls), w in zip(parts, pw):
        extra = "" if cls else tint("accent", 0.12)
        fig.rect(x, y2, w, 40, cls=cls or "seg", extra=extra)
        fig.text(x + w / 2, y2 + 17, name, cls="nm")
        fig.text(x + w / 2, y2 + 32, size, cls="sz")
        x += w + 4
    fig.text(
        10,
        y2 + 56,
        "Header: recno, recordType = EVENT, format = MINIDST, tocsiz, datsiz,",
        cls="sz",
        anchor="start",
    )
    fig.text(
        10,
        y2 + 69,
        "tocoff1, datoff, usrnam = IJEVHD, usroff …",
        cls="sz",
        anchor="start",
    )
    fig.text(
        10,
        y2 + 82,
        "IEVENTH: header pointer, run, event, time, weight, evttype, trigger",
        cls="sz",
        anchor="start",
    )
    fig.text(
        366,
        y2 + 56,
        "PHMTOC: format version and 17 entry counts",
        cls="sz",
        anchor="start",
    )
    # Row 3: the data buffer as families.
    y3 = 290
    fig.text(
        10,
        y3 - 12,
        "DATA BUFFER: FAMILIES BACK TO BACK, NO DELIMITERS",
        cls="t3 caps",
        anchor="start",
    )
    x = 10
    bw = (740 - 4 * (len(FAMILIES) - 1)) / len(FAMILIES)
    for fam in FAMILIES:
        _, token = GROUPS[fam.group]
        fig.rect(x, y3, bw, 30, cls="tf", extra=tint(token, 0.2))
        x += bw + 4
    fig.text(10, y3 + 48, "MCHEAD", cls="sz", anchor="start")
    fig.text(750, y3 + 48, "PHVXOV", cls="sz", anchor="end")
    fig.text(
        380,
        y3 + 48,
        "19 blocks in the fixed order of the next figure; PHMTOC gives the number "
        "of entries of 17 of them",
        cls="sz",
    )
    # From the centre of the data buffer down to its families.
    buffer_x = 10 + sum(pw[:3]) + 3 * 4 + pw[3] / 2
    fig.arrow_line(buffer_x, y2 + 40, buffer_x, y3 - 4, token="ink-3")
    fig.write(FIGURES_DIR / "sld-jazelle-records.svg")


def make_composition() -> None:
    cols, bw, bh, gap = 10, 70.4, 46, 4
    fig = Figure(760, 384, "rc", style=STYLE)
    for panel, (title, is_mc, y0) in enumerate(
        (("DATA RECORD", False, 24), ("MC RECORD", True, 196))
    ):
        fig.text(10, y0 - 8, f"({'ab'[panel]}) {title}", cls="t3 caps", anchor="start")
        for i, fam in enumerate(FAMILIES):
            row, col = divmod(i, cols)
            x, y = 10 + col * (bw + gap), y0 + row * (bh + 26)
            _, token = GROUPS[fam.group]
            absent = fam.mc_only and not is_mc
            if absent:
                fig.rect(x, y, bw, bh, cls="ghost")
                fig.text(x + bw / 2, y + 20, fam.name, cls="gh")
                fig.text(x + bw / 2, y + 34, "absent", cls="gh")
                continue
            fig.rect(x, y, bw, 4, cls="", extra=f' fill="{color(token)}" stroke="none"')
            fig.rect(x, y, bw, bh, cls="tf", extra=tint(token, 0.10))
            name = fam.name if fam.decoded_by_reader else f"{fam.name}*"
            fig.text(x + bw / 2, y + 20, name, cls="nm")
            fig.text(x + bw / 2, y + 34, fam.size, cls="sz")
            fig.text(x + bw / 2, y + bh + 13, fam.count, cls="gh")
    # Legend.
    for i, (key, (label, token)) in enumerate(GROUPS.items()):
        lx, ly = 10 + (i % 4) * 190, 352 + (i // 4) * 16
        fig.rect(lx, ly - 9, 10, 10, cls="tf", extra=tint(token, 0.5))
        fig.text(lx + 14, ly, label, cls="sz", anchor="start")
    fig.text(750, 18, "* not decoded by jazelle 0.4.0", cls="gh", anchor="end")
    fig.write(FIGURES_DIR / "sld-record-composition.svg")


def node(
    fig: Figure, x: float, y: float, name: str, group: str, w: float = 78
) -> tuple[float, float]:
    """An opaque, tinted box for one family, centred on (x, y)."""
    _, token = GROUPS[group]
    fig.rect(x - w / 2, y - 14, w, 28, cls="paper", rx=3)
    fig.rect(x - w / 2, y - 14, w, 28, cls="tf", rx=3, extra=tint(token, 0.16))
    fig.text(x, y + 4, name, cls="nm")
    return x, y


def make_relations() -> None:
    fig = Figure(760, 470, "rl", style=STYLE)
    half = 39  # half the width of a family box
    pos = {
        "MCHEAD": (80, 60, "truth"),
        "MCPART": (80, 170, "truth"),
        "MCBEAM": (80, 300, "truth"),
        "MCPNT": (250, 60, "relations"),
        "PHKMC1": (250, 230, "relations"),
        "PHWMC": (250, 330, "truth"),
        "PHKCHRG": (362, 180, "relations"),
        "PHPOINT": (480, 60, "summary"),
        "PHCHRG": (480, 130, "tracking"),
        "PHKLUS": (480, 230, "calorimetry"),
        "PHWIC": (480, 330, "muon"),
        "PHPSUM": (680, 60, "summary"),
        "PHVXOV": (680, 130, "tracking"),
        "PHKELID": (680, 230, "calorimetry"),
        "PHCRID": (680, 330, "pid"),
    }

    def edge_point(a: str, b: str) -> tuple[float, float]:
        """Where the line from a's centre to b's centre leaves a's box."""
        (x1, y1, _), (x2, y2, _) = pos[a], pos[b]
        dx, dy = x2 - x1, y2 - y1
        tx = half / abs(dx) if dx else float("inf")
        ty = 14 / abs(dy) if dy else float("inf")
        t = min(tx, ty)
        return x1 + dx * t, y1 + dy * t

    def ptr(a: str, b: str, label: str = "", dx: float = 0, dy: float = -5) -> None:
        x1, y1 = edge_point(a, b)
        x2, y2 = edge_point(b, a)
        fig.arrow_line(x1, y1, x2, y2, cls="ln thin", token="ink-2")
        if label:
            fig.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, label, cls="gh")

    def rel(table: str, *ends: str) -> None:
        for end in ends:
            fig.line(
                pos[table][0], pos[table][1], pos[end][0], pos[end][1], cls="ln3 dash"
            )

    rel("MCPNT", "MCPART", "PHPOINT")
    rel("PHKMC1", "MCPART", "PHKLUS")
    rel("PHKCHRG", "PHCHRG", "PHKLUS")
    # PHWMC is one header per PHWIC bank followed by (code, n_hits, MCPART id) pairs,
    # stored in a single pass, so its links are pointers (specs/PHWMC_HEADER.yaml).
    ptr("PHWMC", "PHWIC", "phwic_id")
    ptr("PHWMC", "MCPART", "mcpart_id", dx=-44, dy=0)
    ptr("PHPOINT", "PHPSUM", "mask bit 0")
    ptr("PHPOINT", "PHCHRG", "bit 2", dx=18, dy=-6)
    ptr("PHVXOV", "PHCHRG", "link")
    ptr("PHKELID", "PHCHRG", "header", dx=32, dy=-6)
    ptr("PHCHRG", "MCPART", "imc (MC only)", dx=30, dy=-14)
    # The hits of PHVXOV point to MCPART; the pointer runs above the PHCHRG row, from the
    # top of PHVXOV to the top of MCPART, so that it crosses no family box.
    (vx, vy, _), (mx, my, _) = pos["PHVXOV"], pos["MCPART"]
    lane_y, x_start, x_end = 102, vx - 20, mx - 14
    fig.path(
        f"M{x_start} {vy - 14} V{lane_y + 6} Q{x_start} {lane_y} {x_start - 6} {lane_y} "
        f"H{x_end + 6} Q{x_end} {lane_y} {x_end} {lane_y + 6} V{my - 14}",
        cls="ln thin",
        extra=f' marker-end="{fig.arrow("arrow-ink-2")}"',
    )
    fig.text(580, lane_y - 5, "hit mc_particle (MC only)", cls="gh")
    for name, (x, y, group) in pos.items():
        node(fig, x, y, name, group)
    fig.text(
        480,
        22,
        "PHPOINT also points to PHCRID (bit 1), PHKLUS (3), PHKELID (4), PHWIC (5)",
        cls="gh",
    )
    fig.path(
        "M41 164 C14 160 14 190 41 184",
        cls="ln thin",
        extra=f' marker-end="{fig.arrow("arrow-ink-2")}"',
    )
    fig.text(20, 208, "parent_id", cls="gh", anchor="start")
    # Legend.
    fig.arrow_line(20, 370, 60, 370, cls="ln thin")
    fig.text(
        66,
        374,
        "pointer: the id of another entry, stored in this one",
        cls="sz",
        anchor="start",
    )
    fig.line(400, 370, 440, 370, cls="ln3 dash")
    fig.text(
        446,
        374,
        "relation table: pairs of ids, in two passes",
        cls="sz",
        anchor="start",
    )
    # Inset: a two-pass relation table.
    y0 = 412
    fig.text(
        10,
        y0 - 8,
        "TWO-PASS STORAGE OF A RELATION TABLE WITH n ROWS",
        cls="t3 caps",
        anchor="start",
    )
    x = 10
    for label in ["A id | own id | payload", "\u2026", "A id | own id | payload"]:
        w = 150 if label != "\u2026" else 30
        fig.rect(x, y0, w, 24, cls="tf", extra=tint("box-recipe", 0.14))
        fig.text(x + w / 2, y0 + 16, label, cls="sz mono")
        x += w + 3
    x += 12
    for label in ["B id | own id", "\u2026", "B id | own id"]:
        w = 100 if label != "\u2026" else 30
        fig.rect(x, y0, w, 24, cls="tf", extra=tint("box-recipe", 0.06))
        fig.text(x + w / 2, y0 + 16, label, cls="sz mono")
        x += w + 3
    fig.text(
        10,
        y0 + 42,
        "Pass 1 holds n rows, then pass 2 holds n rows; the rows of the two "
        "passes with the same own id form one relation.",
        cls="gh",
        anchor="start",
    )
    fig.write(FIGURES_DIR / "sld-relations.svg")


def main() -> None:
    make_records()
    make_composition()
    make_relations()


if __name__ == "__main__":
    main()
