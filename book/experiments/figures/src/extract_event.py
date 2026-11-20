"""Pick one hadronic Z decay from the public SLD data release for the event display.

Usage: python extract_event.py MINIDST_FILE

Reads the file with the jazelle reader (read only) and writes ``data/event_display.json``
with the helix parameters and charges of the tracks and the direction and raw energy of the
calorimeter clusters of the first event that passes the selection below. The output holds
no run, event or file identifiers.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import jazelle

OUT_PATH = Path(__file__).resolve().parent / "data" / "event_display.json"

# ---- Selection -------------------------------------------------------------------------
# A clean two-jet event in the barrel, so that the end view shows it well.
MIN_TRACKS, MAX_TRACKS = 16, 24
MIN_VXD_HITS = 2  # tracks drawn: linked to at least two VXD3 hits
MAX_ABS_COS = 0.6  # for every drawn track
MIN_CLUSTER_GEV = 0.15
DECIMALS = 5


def as_dict(obj):
    return obj.to_dict() if hasattr(obj, "to_dict") else obj


def candidate(ev) -> dict | None:
    tracks = [as_dict(t) for t in ev.phchrg]
    good = [
        t
        for t in tracks
        if t["nhitv"] >= MIN_VXD_HITS
        and abs(t["hlxpar"][2] / math.hypot(1, t["hlxpar"][2])) < MAX_ABS_COS
    ]
    if not MIN_TRACKS <= len(good) <= MAX_TRACKS or len(good) < 0.9 * len(tracks):
        return None
    clusters = [as_dict(k) for k in ev.phklus]
    return {
        "tracks": [
            {
                "phi0": round(t["hlxpar"][0], DECIMALS),
                "inv_pt": round(abs(t["hlxpar"][1]), DECIMALS),
                "tan_lambda": round(t["hlxpar"][2], DECIMALS),
                "charge": int(t["charge"]),
            }
            for t in good
        ],
        "clusters": [
            {
                "cos_theta": round(k["cth"], DECIMALS),
                "phi": round(k["phi"], DECIMALS),
                "e_raw": round(k["eraw"], DECIMALS),
            }
            for k in clusters
            if k["eraw"] >= MIN_CLUSTER_GEV
        ],
    }


def main() -> None:
    handle = jazelle.open(sys.argv[1])
    for i in range(handle.getTotalEvents()):
        try:
            event = candidate(handle[i])
        except RuntimeError:
            continue
        if event:
            OUT_PATH.parent.mkdir(exist_ok=True)
            OUT_PATH.write_text(json.dumps(event, indent=1) + "\n")
            print(
                f"wrote {OUT_PATH}: {len(event['tracks'])} tracks, "
                f"{len(event['clusters'])} clusters"
            )
            return
    raise SystemExit("no event passed the selection")


if __name__ == "__main__":
    main()
