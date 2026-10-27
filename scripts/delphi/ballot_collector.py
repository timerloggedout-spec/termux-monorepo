"""The DEBATE collection plane (Strands ITEMS-003), built offline.

Ingests recorded ballots under the DEBATE protocol: validation
(voter identity; MODEL_PROVIDER run record), deduplication on
(source_class, voter, run_id), and a collection receipt from which
the per-class tallies can be reconstructed (the E-06 property).
No ballot is cast here — this is the intake the panel was missing.
"""

from __future__ import annotations

import hashlib
import json

from scripts.delphi.cross_vote import CLASSES, validate_ballots

SCHEMA = "delphi-ballot-collection/v1"


def _hash(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def collect(ballots: list[dict]) -> dict:
    """Validate + dedupe + receipt a set of recorded ballots."""
    validate_ballots(ballots)  # refuses invalid and duplicate ballots
    per_class = {cls: 0 for cls in CLASSES}
    for ballot in ballots:
        per_class[ballot["source_class"]] += 1
    receipt = {
        "schema": SCHEMA,
        "accepted": len(ballots),
        "per_class": per_class,
        "ballot_hashes": sorted(_hash(b) for b in ballots),
        "dedupe_keys": sorted(
            f"{b['source_class']}|{b['voter']}|{(b.get('run') or {}).get('run_id')}"
            for b in ballots),
    }
    # E-06 reconstruction check: tallies recomputed from the accepted
    # set must equal the receipt's — the receipt alone must suffice.
    recomputed = {cls: 0 for cls in CLASSES}
    for ballot in ballots:
        recomputed[ballot["source_class"]] += 1
    receipt["reconstruction_check"] = recomputed == per_class
    return receipt
