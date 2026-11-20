"""Extract the mini-DST bank layouts into ``data/banks_layout.yaml``.

Two sources are combined:

- the reader's C++ read functions (``src/banks/*.cpp`` of jazelle_reader), parsed for the
  regular ``name = buffer.readX(o); o += N;`` and ``readFloats(o, name.data(), K)``
  statements, with a short table below for the packed words the parser cannot read;
- the bank-lab specifications (``tools/bank_lab/specs/*.yaml``), which give offset, type,
  label and meaning for the banks the reader did not decode or named provisionally.

Usage: python extract_banks.py JAZELLE_READER_DIR

The output records the reader commit, so the snapshot can be compared with a later one.
Field meanings for the reader banks are kept separately in ``data/bank_meanings.yaml``.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

DATA_DIR = Path(__file__).resolve().parent / "data"
OUT_PATH = DATA_DIR / "banks_layout.yaml"

# ---- Types ----------------------------------------------------------------------------
# DataBuffer read method -> (type code, bytes), src/DataBuffer.hpp of jazelle_reader.
READ_TYPES: dict[str, tuple[str, int]] = {
    "readInt": ("i4", 4),
    "readFloat": ("f4", 4),
    "readShort": ("i2", 2),
    "readDate": ("date8", 8),
}
TYPE_BYTES: dict[str, int] = {
    "i2": 2,
    "u2": 2,
    "i4": 4,
    "u4": 4,
    "f4": 4,
    "bits16": 2,
    "bits32": 4,
    "date8": 8,
    "ascii8": 8,
    "pid5": 20,
}

# ---- Patterns of the reader's read functions ------------------------------------------
STMT = re.compile(
    r"(?P<name>\w+)\s*=\s*(?:buffer|data)\.(?P<method>read(?:Int|Float|Short))\(\s*"
    r"(?:o|offset(?:\s*\+\s*(?P<off>\d+))?)\s*\)"
)
ARRAY = re.compile(
    r"(?:buffer|data)\.readFloats\(\s*o\s*,\s*(?P<name>\w+)\.data\(\)\s*,\s*(?P<count>\d+)\s*\)"
)
ADVANCE = re.compile(r"\bo\s*\+=\s*(?P<n>\d+)")
RETURN = re.compile(r"return\s+(?P<n>\d+)\s*;")

# Banks whose read function is regular enough to parse, with their group in the chapter.
PARSED_BANKS: dict[str, str] = {
    "MCHEAD": "truth",
    "PHPSUM": "summary",
    "PHCHRG": "tracking",
    "PHKLUS": "calorimetry",
    "PHWIC": "muon",
    "PHKELID": "calorimetry",
    "PHCRID": "pid",
}

# Packed words and layouts the regular parser does not cover. Each entry cites the reader
# source it restates; the extractor checks the total size against the reader.
MANUAL: dict[str, dict[str, Any]] = {
    "MCPART": {
        "group": "truth",
        "source": "src/banks/MCPART.cpp, MCPART::read; ID-word bits from the decode lines",
        "blocks": [
            {
                "name": "entry",
                "size": "36, or 40 when E is stored",
                "fields": [
                    {"offset": 0, "type": "f4", "name": "px"},
                    {"offset": 4, "type": "f4", "name": "py"},
                    {"offset": 8, "type": "f4", "name": "pz"},
                    {
                        "offset": 12,
                        "type": "u4",
                        "name": "id_word",
                        "bits": [
                            ["0-12", "id"],
                            ["13-25", "parent_id"],
                            [
                                "26-28",
                                "charge magnitude index (0, 1/3, 2/3, 1, 2, 3, 4, 5)",
                            ],
                            ["29", "charge negative"],
                            ["30", "E omitted"],
                        ],
                    },
                    {"offset": 16, "type": "i4", "name": "ptype"},
                    {"offset": 20, "type": "i4", "name": "origin"},
                    {"offset": 24, "type": "f4", "name": "xt_x"},
                    {"offset": 28, "type": "f4", "name": "xt_y"},
                    {"offset": 32, "type": "f4", "name": "xt_z"},
                    {"offset": 36, "type": "f4", "name": "e", "optional": True},
                ],
            }
        ],
    },
    "PHPOINT": {
        "group": "summary",
        "source": "src/banks/PHPOINT.cpp, PHPOINT::read",
        "blocks": [
            {
                "name": "entry",
                "size": "4 + 2 per set mask bit, padded to a multiple of 4",
                "fields": [
                    {
                        "offset": 0,
                        "type": "u4",
                        "name": "header",
                        "bits": [["0-15", "id"], ["16-31", "mask"]],
                    },
                    {
                        "offset": 4,
                        "type": "i2",
                        "name": "pointers",
                        "count": "number of set mask bits",
                        "bits": [
                            [
                                "mask bit 0",
                                "PHPSUM (if clear, the PHPSUM id equals id)",
                            ],
                            ["mask bit 1", "PHCRID"],
                            ["mask bit 2", "PHCHRG"],
                            ["mask bit 3", "PHKLUS"],
                            ["mask bit 4", "PHKELID"],
                            ["mask bit 5", "PHWIC"],
                        ],
                    },
                ],
            }
        ],
    },
    "MCPNT": {
        "group": "relations",
        "source": "src/banks/MCPNT.cpp and the second pass in src/JazelleFile.cpp, parseMiniDst",
        "blocks": [
            {
                "name": "pass 1",
                "size": 16,
                "repeat": "n_mcpnt",
                "fields": [
                    {
                        "offset": 0,
                        "type": "u4",
                        "name": "header",
                        "bits": [["0-15", "MCPART id"], ["16-31", "MCPNT id"]],
                    },
                    {"offset": 4, "type": "i4", "name": "reason"},
                    {"offset": 8, "type": "i4", "name": "nhits"},
                    {"offset": 12, "type": "f4", "name": "econtrib"},
                ],
            },
            {
                "name": "pass 2",
                "size": 4,
                "repeat": "n_mcpnt",
                "fields": [
                    {
                        "offset": 0,
                        "type": "u4",
                        "name": "header",
                        "bits": [["0-15", "PHPOINT id"], ["16-31", "MCPNT id"]],
                    },
                ],
            },
        ],
    },
    "CRIDHYP": {
        "group": "pid",
        "source": "src/banks/CRIDHYP.cpp and src/banks/PIDVEC.cpp; one block per radiator in PHCRID",
        "blocks": [
            {
                "name": "full form",
                "size": 36,
                "fields": [
                    {
                        "offset": 0,
                        "type": "f4",
                        "name": "llik",
                        "count": 5,
                        "reader_note": "PIDVEC: log-likelihoods for e, mu, pi, K, p",
                    },
                    {"offset": 20, "type": "i2", "name": "rc"},
                    {"offset": 22, "type": "i2", "name": "nhits"},
                    {"offset": 24, "type": "i4", "name": "besthyp"},
                    {"offset": 28, "type": "i2", "name": "nhexp"},
                    {"offset": 30, "type": "i2", "name": "nhfnd"},
                    {"offset": 32, "type": "i2", "name": "nhbkg"},
                    {"offset": 34, "type": "i2", "name": "mskphot"},
                ],
            },
            {
                "name": "reduced form",
                "size": 4,
                "fields": [
                    {"offset": 0, "type": "i2", "name": "rc"},
                    {"offset": 2, "type": "i2", "name": "nhits"},
                ],
            },
        ],
    },
    "PHKTRK": {
        "group": "calorimetry",
        "source": "src/banks/PHKTRK.cpp (reads 0 bytes; the count is always 0)",
        "blocks": [{"name": "entry", "size": 0, "fields": []}],
    },
    "IEVENTH": {
        "group": "event",
        "source": "src/banks/IEVENTH.cpp, read from the logical record at usroff",
        "blocks": [
            {
                "name": "header",
                "size": 32,
                "fields": [
                    {"offset": 0, "type": "i4", "name": "header"},
                    {"offset": 4, "type": "i4", "name": "run"},
                    {"offset": 8, "type": "i4", "name": "event"},
                    {"offset": 12, "type": "date8", "name": "evttime"},
                    {"offset": 20, "type": "f4", "name": "weight"},
                    {"offset": 24, "type": "i4", "name": "evttype"},
                    {"offset": 28, "type": "i4", "name": "trigger"},
                ],
            }
        ],
    },
}

# Entries preceded by a separate 4-byte id word in the data buffer
# (src/JazelleFile.cpp, parseMiniDst).
SEPARATE_ID = {"PHPSUM", "PHCHRG", "PHKLUS", "PHWIC"}

# Bank-lab specs grouped into banks, in block order.
SPEC_BANKS: dict[str, dict[str, Any]] = {
    "PHBM": {"group": "event", "blocks": [("PHBM", "entry", "n_phbm")]},
    "PHEVCL": {"group": "event", "blocks": [("PHEVCL", "entry", "n_phevcl")]},
    "GAP_WORD": {"group": "event", "blocks": [("GAP_WORD", "word", "1 per record")]},
    "MCBEAM": {"group": "truth", "blocks": [("MCBEAM", "entry", "n_mcbeam")]},
    "PHVXOV": {
        "group": "tracking",
        "blocks": [
            ("PHVXOV_HEADER", "header", "per bank"),
            ("PHVXOV_HIT", "hit", "n_hits per bank"),
        ],
    },
    "PHKMC1": {
        "group": "relations",
        "blocks": [
            ("PHKMC1_PASS1", "pass 1", "n_phkmc1"),
            ("PHKMC1_PASS2", "pass 2", "n_phkmc1"),
        ],
    },
    "PHKCHRG": {
        "group": "relations",
        "blocks": [
            ("PHKCHRG_PASS1", "pass 1", "n_phkchrg"),
            ("PHKCHRG_PASS2", "pass 2", "n_phkchrg"),
        ],
    },
    "PHWMC": {
        "group": "relations",
        "blocks": [
            ("PHWMC_HEADER", "header", "per bank"),
            ("PHWMC_PAIR", "pair", "n_pairs per bank"),
        ],
    },
}

# Raw file-name suffixes (a dot, a digit, a letter and a digit) in the spec prose are dropped.
RAW_FILE_SUFFIX = re.compile(r" \.\d[a-z]\d\b")

# Block sizes of the bank lab, tools/bank_lab/bank_lab/tail.py and blocks.py.
SPEC_BLOCK_SIZES: dict[str, int] = {
    "PHBM": 60,
    "PHEVCL": 72,
    "GAP_WORD": 4,
    "MCBEAM": 76,
    "PHVXOV_HEADER": 16,
    "PHVXOV_HIT": 80,
    "PHKMC1_PASS1": 20,
    "PHKMC1_PASS2": 4,
    "PHKCHRG_PASS1": 16,
    "PHKCHRG_PASS2": 4,
    "PHWMC_HEADER": 20,
    "PHWMC_PAIR": 8,
}


def read_function_body(source: str) -> str:
    """Return the text of the first ``::read`` function in `source`."""
    start = source.index("::read(")
    brace = source.index("{", start)
    depth, i = 0, brace
    while True:
        depth += {"{": 1, "}": -1}.get(source[i], 0)
        if depth == 0:
            return source[brace : i + 1]
        i += 1


def parse_reader_bank(path: Path) -> tuple[list[dict[str, Any]], int | None]:
    """Parse the regular read statements of one bank into (fields, returned size)."""
    body = read_function_body(path.read_text())
    fields: list[dict[str, Any]] = []
    cursor = 0
    returned = None
    for raw in body.splitlines():
        line = raw.split("//", 1)[0]
        comment = raw.split("//", 1)[1].strip() if "//" in raw else ""
        for match in STMT.finditer(line):
            type_code, size = READ_TYPES[match["method"]]
            offset = int(match["off"]) if match["off"] else 0
            explicit = "offset" in match.group(0)
            field = {
                "offset": offset if explicit else cursor,
                "type": type_code,
                "name": match["name"],
            }
            if comment:
                field["reader_note"] = comment
            fields.append(field)
            if explicit:
                cursor = max(cursor, (offset or 0) + size)
        for match in ARRAY.finditer(line):
            field = {
                "offset": cursor,
                "type": "f4",
                "name": match["name"],
                "count": int(match["count"]),
            }
            if comment:
                field["reader_note"] = comment
            fields.append(field)
        for match in ADVANCE.finditer(line):
            cursor += int(match["n"])
        ret = RETURN.search(line)
        if ret:
            returned = int(ret["n"])
    return fields, returned


def field_bytes(field: dict[str, Any]) -> int:
    count = field.get("count", 1)
    return TYPE_BYTES[field["type"]] * (count if isinstance(count, int) else 1)


def reader_banks(reader_dir: Path) -> dict[str, Any]:
    banks: dict[str, Any] = {}
    for name, group in PARSED_BANKS.items():
        path = reader_dir / "src" / "banks" / f"{name}.cpp"
        fields, returned = parse_reader_bank(path)
        if name == "PHKELID":  # the first word is packed: PHCHRG id and own id
            fields[0] = {
                "offset": 0,
                "type": "u4",
                "name": "header",
                "bits": [["0-15", "id"], ["16-31", "PHCHRG id"]],
            }
        if name == "PHCRID":
            fields[0]["bits"] = [
                ["0-15", "id"],
                ["16", "liquid block present"],
                ["17", "gas block present"],
            ]
        covered = sum(field_bytes(f) for f in fields)
        if name == "PHWIC":  # the last two bytes are never read
            covered += 2
        size: Any = returned
        if name == "PHCRID":
            size = "16 + liquid block (36 or 4) + gas block (36 or 4)"
        elif returned is not None and covered != returned:
            raise SystemExit(
                f"{name}: fields cover {covered} B, the reader returns {returned}"
            )
        block = {"name": "entry", "size": size, "fields": fields}
        if name in SEPARATE_ID:
            block["id_word"] = "a 4-byte id precedes each entry"
        banks[name] = {
            "group": group,
            "source": f"src/banks/{name}.cpp",
            "blocks": [block],
        }
    for name, spec in MANUAL.items():
        banks[name] = spec
    return banks


def spec_banks(reader_dir: Path) -> dict[str, Any]:
    spec_dir = reader_dir / "tools" / "bank_lab" / "specs"
    banks: dict[str, Any] = {}
    for name, layout in SPEC_BANKS.items():
        blocks = []
        kinds: list[str] = []
        for spec_name, block_name, repeat in layout["blocks"]:
            spec = yaml.safe_load((spec_dir / f"{spec_name}.yaml").read_text())
            kinds = spec["kinds"]
            fields = [
                {
                    "offset": f["offset"],
                    "type": f["type"],
                    "name": f["name"],
                    "label": f["label"],
                    "meaning": RAW_FILE_SUFFIX.sub("", f["meaning"].strip()),
                }
                for f in spec["fields"]
            ]
            size = SPEC_BLOCK_SIZES[spec_name]
            covered = sum(TYPE_BYTES[f["type"]] for f in fields)
            if covered != size:
                raise SystemExit(f"{spec_name}: fields cover {covered} B of {size}")
            blocks.append(
                {"name": block_name, "size": size, "repeat": repeat, "fields": fields}
            )
        banks[name] = {
            "group": layout["group"],
            "kinds": kinds,
            "source": "tools/bank_lab/specs",
            "blocks": blocks,
        }
    return banks


def reader_commit(reader_dir: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=reader_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def main() -> None:
    reader_dir = Path(sys.argv[1]).expanduser().resolve()
    banks = reader_banks(reader_dir)
    for name, bank in spec_banks(reader_dir).items():
        banks[name] = bank
    snapshot = {
        "provenance": {
            "reader": "github.com/HEP-KE/jazelle_reader",
            "commit": reader_commit(reader_dir),
            "note": "layouts of src/banks/*.cpp and tools/bank_lab/specs/*.yaml",
        },
        "banks": banks,
    }
    DATA_DIR.mkdir(exist_ok=True)
    OUT_PATH.write_text(
        yaml.safe_dump(snapshot, sort_keys=False, allow_unicode=True, width=100)
    )
    print(f"wrote {OUT_PATH} with {len(banks)} banks")


if __name__ == "__main__":
    main()
