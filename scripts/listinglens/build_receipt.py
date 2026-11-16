#!/usr/bin/env python3
"""Build the ListingLens demo-render receipt (#5137 publish step).

Receipt = {schema, mp4 file name, sha256, duration_s (ffprobe),
capture_run_id, run_url, beat values cited}. The receipt is the
comment posted on the target issue and uploaded beside the MP4.

Usage:
  python3 scripts/listinglens/build_receipt.py \
      --mp4 listinglens-demo.mp4 --probe probe.json \
      --beats beats.json --capture-run-id 123 --run-url URL \
      --out receipt.json
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path


def build_receipt(mp4_path, probe, manifest, capture_run_id, run_url):
    data = Path(mp4_path).read_bytes()
    duration = float(probe["format"]["duration"])
    return {
        "schema": "listinglens.render-receipt/v1",
        "mp4": Path(mp4_path).name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "duration_s": round(duration, 2),
        "capture_run_id": str(capture_run_id),
        "run_url": run_url,
        "values": manifest["values"],
        "beats": len(manifest["beats"]),
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mp4", required=True)
    ap.add_argument("--probe", required=True)
    ap.add_argument("--beats", required=True)
    ap.add_argument("--capture-run-id", required=True)
    ap.add_argument("--run-url", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    receipt = build_receipt(
        a.mp4,
        json.loads(Path(a.probe).read_text()),
        json.loads(Path(a.beats).read_text()),
        a.capture_run_id,
        a.run_url,
    )
    with open(a.out, "w") as fh:
        json.dump(receipt, fh, indent=1)
        fh.write("\n")
    print(json.dumps(receipt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
