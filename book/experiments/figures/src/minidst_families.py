"""The families of an SLD mini-DST record, in stream order, as one table shared by figures.

Order, entry sizes and the TOC counts that drive them follow ``parseMiniDst`` in
``src/JazelleFile.cpp`` of jazelle_reader and, for the tail after PHKCHRG, the bank-lab
walk in ``tools/bank_lab/bank_lab/tail.py``; the tail layout closes every readable record.
"""

from __future__ import annotations

from dataclasses import dataclass

# ---- Groups ---------------------------------------------------------------------------
# Group -> (display name, theme token used for its colour).
GROUPS: dict[str, tuple[str, str]] = {
    "truth": ("Simulation truth", "box-warning"),
    "relations": ("Relation tables", "box-recipe"),
    "summary": ("Particle summary and pointers", "accent"),
    "tracking": ("Tracking", "box-definition"),
    "calorimetry": ("Calorimetry", "box-remark"),
    "pid": ("Cherenkov particle ID", "box-example"),
    "muon": ("Muon system", "ink-2"),
    "event": ("Beam and event", "ink-3"),
}


@dataclass(frozen=True)
class Family:
    """One family of the data buffer.

    Parameters
    ----------
    name : str
        Bank name, or "reserved" for the reserved word before PHVXOV.
    group : str
        Key of `GROUPS`.
    size : str
        Bytes per entry, as a short formula.
    count : str
        Where the number of entries comes from.
    mc_only : bool
        True if data records never hold an entry.
    decoded_by_reader : bool
        True if jazelle 0.4.0 decodes the family.
    """

    name: str
    group: str
    size: str
    count: str
    mc_only: bool = False
    decoded_by_reader: bool = True


FAMILIES: tuple[Family, ...] = (
    Family("MCHEAD", "truth", "20 B", "always one"),
    Family("MCPART", "truth", "36 or 40 B", "n_mcpart", mc_only=True),
    Family("PHPSUM", "summary", "4 + 32 B", "n_phpsum"),
    Family("PHCHRG", "tracking", "4 + 236 B", "n_phchrg"),
    Family("PHKLUS", "calorimetry", "4 + 96 B", "n_phklus"),
    Family("PHWIC", "muon", "4 + 140 B", "n_phwic"),
    Family("PHCRID", "pid", "24, 56 or 88 B", "n_phcrid"),
    Family("PHKTRK", "calorimetry", "0 B", "always 0"),
    Family("PHKELID", "calorimetry", "96 B", "n_phkelid"),
    Family("PHPOINT", "summary", "4 + 4⌈k/2⌉ B", "n_phpoint"),
    # PHWMC is the MC truth of the muon-system tracks, a header plus pairs stored in one
    # pass, not a two-pass relation table (specs/PHWMC_HEADER.yaml).
    Family("PHWMC", "truth", "20 + 8k B", "n_phwmc", mc_only=True),
    Family("MCPNT", "relations", "16 + 4 B", "n_mcpnt", mc_only=True),
    Family("PHKCHRG", "relations", "16 + 4 B", "n_phkchrg"),
    Family(
        "PHKMC1",
        "relations",
        "20 + 4 B",
        "n_phkmc1",
        mc_only=True,
        decoded_by_reader=False,
    ),
    Family("PHBM", "event", "60 B", "n_phbm"),
    Family("PHEVCL", "event", "72 B", "n_phevcl", decoded_by_reader=False),
    Family(
        "MCBEAM", "truth", "76 B", "n_mcbeam", mc_only=True, decoded_by_reader=False
    ),
    Family("reserved", "event", "4 B", "always one", decoded_by_reader=False),
    Family("PHVXOV", "tracking", "16 + 80k B", "n_phvxov", decoded_by_reader=False),
)

# PHMTOC v4.0: a version word then 17 int32 counts, in this order
# (tools/bank_lab/bank_lab/config.py, TOC_COUNT_FIELDS; src/PHMTOC.cpp).
TOC_COUNTS: tuple[str, ...] = (
    "n_mcpart",
    "n_phpsum",
    "n_phchrg",
    "n_phklus",
    "n_phktrk",
    "n_phwic",
    "n_phwmc",
    "n_phcrid",
    "n_phpoint",
    "n_mcpnt",
    "n_phkmc1",
    "n_phkchrg",
    "n_phbm",
    "n_phevcl",
    "n_mcbeam",
    "n_phkelid",
    "n_phvxov",
)
