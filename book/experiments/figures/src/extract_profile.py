"""Profile the 4-byte words of the PHBM block in recorded events with the decoding harness.

Usage: python extract_profile.py   (with the reader's ``tools/bank_lab`` directory on PYTHONPATH)

Reads the data records of the harness's working sample (``bank_lab.blocks.load_sample``) and
classes every 4-byte word of their PHBM entries with the harness's VAX decoder
(``bank_lab.vax.decode_f``): zero, a valid VAX F float, a small integer, or something else.
Writes ``data/phbm_profile.json`` with the fractions and the record count only, no identifiers.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from bank_lab import vax
from bank_lab.blocks import entries, load_sample, words

OUT_PATH = Path(__file__).resolve().parent / "data" / "phbm_profile.json"

# ---- Harness selection ------------------------------------------------------------------
SAMPLE = "working"  # bank_lab/profile.py: profiles use the working sample only
BLOCK = "PHBM"
KIND = "data"
SMALL_INT = 1 << 16  # bank_lab/profile.py, column int_small: |word| < 65536


def classify(word: np.ndarray) -> dict[str, float]:
    """Share of entries in which one word is zero, a valid VAX F float, a small integer or other."""
    _, flags = vax.decode_f(word)
    zero = word == 0
    valid = flags == vax.FLAG_VALID
    small = ~zero & ~valid & (np.abs(word.astype(np.int64)) < SMALL_INT)
    other = ~(zero | valid | small)
    return {
        key: round(float(np.mean(mask)), 4)
        for key, mask in (
            ("zero", zero),
            ("float", valid),
            ("int", small),
            ("other", other),
        )
    }


def main() -> None:
    block = entries(load_sample(SAMPLE, families=()), BLOCK, KIND)
    profile = [
        {"offset": offset, **classify(words(block.data, offset))}
        for offset in range(0, block.data.shape[1] - 3, 4)
    ]
    OUT_PATH.write_text(
        json.dumps(
            {
                "block": BLOCK,
                "kind": KIND,
                "sample": SAMPLE,
                "records": len(block.data),
                "words": profile,
            },
            indent=1,
        )
        + "\n"
    )
    print(f"wrote {OUT_PATH} from {len(block.data)} records")


if __name__ == "__main__":
    main()
