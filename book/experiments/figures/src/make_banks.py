"""Draw one byte map per mini-DST bank and write the bank field tables into the pages.

Inputs: ``data/banks_layout.yaml`` (offsets, types, names, bank-lab labels) and
``data/bank_meanings.yaml`` (purpose of each bank; meaning and basis of each field).
Outputs: ``sld-bank-<name>.svg`` next to this directory, and, in every page of
``book/experiments/sld/`` that holds the markers
``<!-- generated:bank NAME -->`` … ``<!-- /generated:bank NAME -->``, the field table of
that bank between them.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from svgkit import Figure, color

SRC_DIR = Path(__file__).resolve().parent
FIGURES_DIR = SRC_DIR.parent
PAGES_DIR = FIGURES_DIR.parent / "sld"
LAYOUT_PATH = SRC_DIR / "data" / "banks_layout.yaml"
MEANINGS_PATH = SRC_DIR / "data" / "bank_meanings.yaml"

# ---- Map geometry -------------------------------------------------------------------
BYTE_WIDTH = 20.0  # px per byte
ROW_BYTES = 32  # bytes per row of the map
ROW_HEIGHT = 26.0
LEFT = 54.0  # room for the offset labels
CHAR_WIDTH = 5.6  # px per character of a 9 px label, to decide whether a name fits
NUMBER_NOTE = (
    "A box too narrow for its field name shows the field's row number in the table."
)
NUMBER_NOTE_HEIGHT = 14.0  # extra height for that note below the legend

TYPE_BYTES = {
    "i2": 2,
    "u2": 2,
    "i4": 4,
    "u4": 4,
    "f4": 4,
    "bits16": 2,
    "bits32": 4,
    "date8": 8,
    "ascii8": 8,
}
TYPE_WORDS = {
    "i2": "int16",
    "u2": "uint16",
    "i4": "int32",
    "u4": "uint32",
    "f4": "VAX F float",
    "bits16": "16 bits",
    "bits32": "32 bits",
    "date8": "VAX date",
    "ascii8": "8 characters",
}

# ---- Field status ---------------------------------------------------------------------
# Status -> (legend text, theme token). The bank-lab labels are those defined in
# sld/decoding.md (section "Level 2: meanings"); the others say where the meaning of a
# reader field is documented.
STATUS: dict[str, tuple[str, str]] = {
    "confirmed": ("confirmed", "box-example"),
    "plausible": ("plausible", "box-remark"),
    "unknown": ("unknown", "ink-3"),
    "documented": ("documented meaning", "box-definition"),
    "reader": ("meaning from the reader only", "accent"),
    "none": ("not documented", "ink-3"),
}
DOCUMENTED_BASES = {"template", "memo", "paper"}

MAP_STYLE = """
    .cell { stroke-width: 0.8; }
    .nm { fill: var(--ink, #1d1b17); font-size: 9px; }
    .off { fill: var(--ink-3, #7a756b); font-size: 9px; }
    .blk { fill: var(--ink-2, #4a463f); font-size: 10.5px; font-weight: 600; }
    .lg { fill: var(--ink-2, #4a463f); font-size: 10px; }
    .grid { stroke: var(--rule, #ddd8cc); stroke-width: 0.6; }
"""


def field_size(field: dict[str, Any]) -> int:
    count = field.get("count", 1)
    return TYPE_BYTES[field["type"]] * (count if isinstance(count, int) else 1)


def field_status(field: dict[str, Any], meaning: dict[str, Any] | None) -> str:
    if "label" in field:
        return field["label"]
    basis = (meaning or {}).get("basis", "none")
    if basis in DOCUMENTED_BASES:
        return "documented"
    return "none" if basis == "none" else "reader"


def block_size(block: dict[str, Any]) -> int:
    if isinstance(block["size"], int):
        return block["size"]
    return max((f["offset"] + field_size(f) for f in block["fields"]), default=0)


def map_label(field: dict[str, Any]) -> str:
    """The name a field carries in the byte map, with its count when it is an array."""
    label = field["name"]
    if isinstance(field.get("count"), int) and field["count"] > 1:
        label += f"[{field['count']}]"
    return label


def first_box_width(field: dict[str, Any]) -> float:
    """Width of the first box of a field, the one that carries its label."""
    length = 4 if field.get("optional") else field_size(field)
    return min(length, ROW_BYTES - field["offset"] % ROW_BYTES) * BYTE_WIDTH


def label_fits(field: dict[str, Any]) -> bool:
    return len(map_label(field)) * CHAR_WIDTH + 6 <= first_box_width(field)


def draw_bank(name: str, bank: dict[str, Any], meanings: dict[str, Any]) -> Path:
    blocks = bank["blocks"]
    field_meanings = meanings.get(name, {}).get("fields", {})
    heights = []
    for block in blocks:
        rows = max(1, -(-block_size(block) // ROW_BYTES))
        heights.append(22 + rows * ROW_HEIGHT + 10)
    numbered = not all(label_fits(f) for block in blocks for f in block["fields"])
    width = LEFT + ROW_BYTES * BYTE_WIDTH + 10
    legend_y = sum(heights) + 14
    height = sum(heights) + 34 + (NUMBER_NOTE_HEIGHT if numbered else 0)
    fig = Figure(width, height, f"bk-{name.lower().replace('_', '-')}", style=MAP_STYLE)
    used: set[str] = set()
    y = 4.0
    number = 0
    for block, block_height in zip(blocks, heights):
        size = block_size(block)
        title = block["name"]
        if block.get("repeat"):
            title += f"  (repeated: {block['repeat']})"
        if isinstance(block["size"], int):
            title += f"  \u2014 {size} bytes"
        else:
            title += f"  \u2014 {block['size']}"
        if block.get("id_word"):
            title += "; a 4-byte id precedes each entry"
        fig.text(LEFT, y + 13, title, cls="blk", anchor="start")
        top = y + 20
        rows = max(1, -(-size // ROW_BYTES))
        for r in range(rows):
            fig.text(
                LEFT - 6,
                top + r * ROW_HEIGHT + 16,
                f"+{r * ROW_BYTES}",
                cls="off",
                anchor="end",
            )
            for b in range(0, ROW_BYTES + 1, 4):
                if r * ROW_BYTES + b <= size:
                    x = LEFT + b * BYTE_WIDTH
                    fig.line(
                        x, top + r * ROW_HEIGHT, x, top + r * ROW_HEIGHT + 4, cls="grid"
                    )
        for field in block["fields"]:
            number += 1
            status = field_status(field, field_meanings.get(field["name"]))
            used.add(status)
            _, token = STATUS[status]
            start, length = field["offset"], field_size(field)
            if field.get("optional"):
                length = 4
            label = map_label(field) if label_fits(field) else str(number)
            # A field may wrap over row ends; draw one rectangle per row it touches.
            pos = start
            first = True
            while pos < start + length:
                row, col = divmod(pos, ROW_BYTES)
                span = min(start + length - pos, ROW_BYTES - col)
                x = LEFT + col * BYTE_WIDTH
                yy = top + row * ROW_HEIGHT
                w = span * BYTE_WIDTH
                dash = ' stroke-dasharray="3 2"' if field.get("optional") else ""
                fig.rect(
                    x + 0.5,
                    yy + 0.5,
                    w - 1,
                    ROW_HEIGHT - 3,
                    cls="cell",
                    extra=f' fill="{color(token)}" fill-opacity="0.16" '
                    f'stroke="{color(token)}"{dash}',
                )
                if first:
                    fig.text(x + w / 2, yy + 15.5, label, cls="nm")
                    first = False
                pos += span
        y += block_height
    # Legend.
    x = LEFT
    for status in STATUS:
        if status not in used:
            continue
        text, token = STATUS[status]
        fig.rect(
            x,
            legend_y,
            10,
            10,
            cls="cell",
            extra=f' fill="{color(token)}" fill-opacity="0.3" stroke="{color(token)}"',
        )
        fig.text(x + 14, legend_y + 9, text, cls="lg", anchor="start")
        x += 14 + len(text) * 5.4 + 18
    if numbered:
        fig.text(
            LEFT,
            legend_y + 9 + NUMBER_NOTE_HEIGHT + 2,
            NUMBER_NOTE,
            cls="lg",
            anchor="start",
        )
    path = FIGURES_DIR / f"sld-bank-{name.lower().replace('_', '-')}.svg"
    fig.write(path)
    return path


BASIS_WORDS = {
    "template": "template",
    "memo": "memo",
    "paper": "paper",
    "reader": "reader only",
    "none": "not documented",
    "confirmed": "confirmed",
    "plausible": "plausible",
    "unknown": "unknown",
}


def bits_text(bits: list[Any]) -> str:
    """Format a bit list from the layout ([range, text]) or the meanings ({bit|range, name, meaning})."""
    parts = []
    for b in bits:
        if isinstance(b, dict):
            where = b.get("range", b.get("bit"))
            name = b.get("name", "")
            meaning = b.get("meaning", "")
            label = (
                f"{name}: {meaning}"
                if name and meaning and name not in meaning
                else (meaning or name)
            )
            parts.append(
                f"bit {where}: {label}"
                if "-" not in str(where)
                else f"bits {where}: {label}"
            )
        else:
            parts.append(f"{'bits' if '-' in str(b[0]) else 'bit'} {b[0]}: {b[1]}")
    return "; ".join(parts)


def markdown_table(
    name: str, bank: dict[str, Any], meanings: dict[str, Any]
) -> tuple[str, list[str]]:
    """The field table of one bank, numbered as in its byte map, and its caveat notes.

    Fields that share a caveat get one note naming all of them.
    """
    field_meanings = meanings.get(name, {}).get("fields", {})
    lines = [
        "| # | Offset | Type | Field | Meaning | Basis |",
        "|---|---|---|---|---|---|",
    ]
    doubts: dict[str, list[str]] = {}  # caveat text -> fields, in table order
    number = 0
    multi = len(bank["blocks"]) > 1
    for block in bank["blocks"]:
        for field in block["fields"]:
            number += 1
            info = field_meanings.get(field["name"], {})
            if "label" in field:
                basis = field["label"]
                meaning = info.get("meaning") or field.get("meaning", "")
            else:
                basis = info.get("basis", "none")
                meaning = info.get("meaning", "")
            meaning = (
                (meaning or "not documented")
                .strip()
                .replace("|", "\\|")
                .replace("\n", " ")
            )
            bits = info.get("bits") or (
                None if info.get("meaning") else field.get("bits")
            )
            if bits:
                # A bit tagged with a block belongs to the row of that block only.
                bits = [
                    b
                    for b in bits
                    if not isinstance(b, dict)
                    or b.get("block", block["name"]) == block["name"]
                ]
                text = bits_text(bits).replace("|", "\\|")
                meaning = (
                    f"{meaning.rstrip('.')}; {text}"
                    if meaning != "not documented"
                    else text
                )
            count = field.get("count")
            type_text = TYPE_WORDS[field["type"]]
            if count and count != 1:
                type_text = f"{count} × {type_text}"
            where = (
                f"{block['name']} +{field['offset']}"
                if multi
                else f"+{field['offset']}"
            )
            if field.get("optional"):
                where += " (if stored)"
            lines.append(
                f"| {number} | {where} | {type_text} | `{field['name']}` | {meaning} | "
                f"{BASIS_WORDS.get(basis, basis)} |"
            )
            doubt = " ".join(info.get("doubt", "").split())
            if doubt:
                names = doubts.setdefault(doubt, [])
                if field["name"] not in names:
                    names.append(field["name"])
    notes = [
        f"- {', '.join(f'`{n}`' for n in names)}: {doubt}"
        for doubt, names in doubts.items()
    ]
    return "\n".join(lines), notes


def write_tables(banks: dict[str, Any], meanings: dict[str, Any]) -> None:
    marker = re.compile(
        r"(<!-- generated:bank (\w+) -->\n)(.*?)(<!-- /generated:bank \2 -->)", re.S
    )
    for page in sorted(PAGES_DIR.glob("*.md")):
        text = page.read_text(encoding="utf-8")

        def fill(match: re.Match[str]) -> str:
            name = match.group(2)
            table, notes = markdown_table(name, banks[name], meanings)
            caption = meanings.get(name, {}).get("caption") or f"Fields of {name}."
            body = f"<!-- table:bank-{name} -->\n{table}\n\nTable: {caption}\n\n"
            if notes:
                body += "Caveats:\n\n" + "\n".join(notes) + "\n\n"
            return f"{match.group(1)}{body}{match.group(4)}"

        new = marker.sub(fill, text)
        if new != text:
            page.write_text(new, encoding="utf-8")


# Blocks laid out in the meanings file rather than in the layout snapshot: the logical
# record header (offsets from the start of the physical record) and the table of contents.
MEANING_LAYOUTS = ("RECORD_HEADER", "PHMTOC")
# Banks described by their table alone: a single word needs no byte map.
TABLE_ONLY_BANKS = ("GAP_WORD",)


def layout_from_meanings(info: dict[str, Any]) -> dict[str, Any]:
    fields = [
        {"offset": f["offset"], "type": f["type"], "name": name}
        for name, f in info["fields"].items()
    ]
    size = max(f["offset"] + TYPE_BYTES[f["type"]] for f in fields)
    block_name = info.get("block_name", "entry")
    return {
        "group": "event",
        "blocks": [{"name": block_name, "size": size, "fields": fields}],
    }


def main() -> None:
    banks = yaml.safe_load(LAYOUT_PATH.read_text())["banks"]
    meanings = (
        yaml.safe_load(MEANINGS_PATH.read_text()) if MEANINGS_PATH.exists() else {}
    )
    for name in MEANING_LAYOUTS:
        if name in meanings:
            banks[name] = layout_from_meanings(meanings[name])
    for name, bank in banks.items():
        if name in TABLE_ONLY_BANKS:
            continue
        if bank["blocks"] and any(block["fields"] for block in bank["blocks"]):
            draw_bank(name, bank, meanings)
    if PAGES_DIR.is_dir():
        write_tables(banks, meanings)


if __name__ == "__main__":
    main()
