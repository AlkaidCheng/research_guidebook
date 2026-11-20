"""Regenerate every figure of the SLD chapter and the bank tables in its pages.

Usage: python make_all.py

Each drawing script runs in its own interpreter, in the order below. The extractors are
not run, and their output is kept in ``data/``: ``extract_banks.py`` reads the reader's
sources and decoding specifications, ``extract_event.py`` a mini-DST file, and
``extract_profile.py`` the working sample of the reader's decoding tools, which needs the
reader's ``tools/bank_lab`` on ``PYTHONPATH``.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
SCRIPTS = (
    "make_feynman.py",
    "make_format.py",
    "make_banks.py",
    "make_detector.py",
    "make_detector_3d.py",
    "make_event_display.py",
    "make_event_stages.py",
    "make_chains.py",
    "make_overlay.py",
    "make_decoding.py",
    "make_measurements.py",
    "make_slc.py",
    "make_timeline.py",
)


def main() -> None:
    for script in SCRIPTS:
        print(f"running {script}")
        subprocess.run([sys.executable, str(SRC_DIR / script)], check=True)


if __name__ == "__main__":
    main()
