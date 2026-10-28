#!/usr/bin/env python3
"""Delphi RFP *segmentation* feed collector (delphi-rfp-segments-feed/v1).

The per-RFP record of truth is the Delphi lane's feed —
`apps/help-wanted-dashboard/data/delphi-rfp-feed.json`
(`delphi-rfp-feed/v1`, collector scripts/delphi/rfp_flood_feed.py,
contract docs/ops/DELPHI-RFP-FEED.md). This collector adds the DoE
lane's segmentation layer over it and nothing else:

  - ops/delphi/rfp-segments.json      (segmentation config)
  - ops/delphi/research-silos.json    (the 12 research silos)
  - the committed delphi-rfp-feed.json (per-RFP entries)

It emits segment rollups: per research silo, the member set
(baseline + .rnd/.selected/.control) with each member's award status
read from the feed of record, the segment's comparison-axes state,
and progress counts. Quota surfaces and meta/process RFPs roll up by
class. Every feed RFP lands in exactly one segment or is emitted in
`unassigned` — never dropped, never force-fit. No scores are
computed here; awards and axes are read, not re-derived.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "delphi-rfp-segments-feed/v1"
VARIANTS = ("rnd", "selected", "control")
AXES = ("produced_output_results_validated", "feature_extractions",
        "consensus_implementation")

HONESTY = [
    "Awards, scores and axes are read from delphi-rfp-feed/v1 (the feed of record) — never re-derived or re-scored here.",
    "Counts derive from that feed at collection time and carry its generated_at as source stamp.",
    "No cross-silo score aggregation: rollups count members and states, they never average scores across segments.",
    "A research axis counts as recorded only when the feed of record no longer reads it pending.",
]


def _read(rel: str):
    return json.loads((ROOT / rel).read_text())


def _member(entry):
    if entry is None:
        return None
    return {"number": entry["number"],
            "surface_id": entry.get("surface_id"),
            "status": entry.get("status"),
            "effective_score": (entry.get("outcome") or {}).get(
                "effective_score")}


def build_feed() -> dict:
    config = _read("ops/delphi/rfp-segments.json")
    silos = _read("ops/delphi/research-silos.json")["silos"]
    source = _read("apps/help-wanted-dashboard/data/delphi-rfp-feed.json")
    entries = source["rfps"]
    by_surface = {e["surface_id"]: e for e in entries if e.get("surface_id")}
    by_number = {e["number"]: e for e in entries}
    assigned: set[int] = set()

    def take(entry):
        if entry is not None:
            assigned.add(entry["number"])
        return _member(entry)

    research_segments = []
    for silo in silos:
        sid = silo["id"]
        baseline = by_surface.get(sid)
        members = {"baseline": take(baseline)}
        for v in VARIANTS:
            members[v] = take(by_surface.get(f"{sid}.{v}"))
        axes_status, axes_recorded = {}, 0
        if baseline and baseline.get("comparison_axes"):
            for axis in AXES:
                raw = baseline["comparison_axes"].get(axis, "pending")
                recorded = not str(raw).startswith("pending")
                axes_status[axis] = "recorded" if recorded else "pending"
                axes_recorded += 1 if recorded else 0
        filed = sum(1 for m in members.values() if m)
        scored = sum(1 for m in members.values()
                     if m and m["status"] not in (None, "unscored"))
        research_segments.append({
            "segment_id": sid,
            "slot": silo["slot"],
            "role": silo.get("role"),
            "members": members,
            "axes_status": axes_status,
            "progress": {"filed": filed, "expected": 4,
                         "gate_scored": scored,
                         "axes_recorded": axes_recorded, "axes_total": 3},
        })

    surfaces_ids = {s["id"] for s in
                    _read("ops/delphi/surfaces.json")["surfaces"]}
    quota_members = []
    for entry in entries:
        if entry["number"] in assigned:
            continue
        if entry.get("surface_id") in surfaces_ids or \
                entry.get("surface_id") == "fly.free_tier":
            quota_members.append(take(entry))
    meta_segments = []
    for slug, number in config["classes"]["meta-process"]["members"].items():
        m = take(by_number.get(number))
        meta_segments.append({"segment_id": slug, "member": m,
                              "status": m["status"] if m else None})
    unassigned = [{"number": e["number"],
                   "surface_id": e.get("surface_id"),
                   "group": e.get("group")}
                  for e in entries if e["number"] not in assigned]

    classes = {name: {"description": c["description"],
                      "criteria": c["criteria"],
                      "questions": c["questions"],
                      "cycle": c["cycle"]}
               for name, c in config["classes"].items()}
    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "generator": "scripts/delphi/rfp_segment_feed.py",
        "sources": {
            "feed_of_record": "apps/help-wanted-dashboard/data/"
                              "delphi-rfp-feed.json",
            "feed_of_record_schema": source.get("schema"),
            "feed_of_record_generated_at": source.get("generated_at"),
            "segments_config": "ops/delphi/rfp-segments.json",
            "research_silos": "ops/delphi/research-silos.json",
        },
        "honesty_rules": HONESTY,
        "totals": {
            "source_rfps": len(entries),
            "research_segments": len(research_segments),
            "research_members": sum(
                s["progress"]["filed"] for s in research_segments),
            "quota_members": len(quota_members),
            "meta_segments": len(meta_segments),
            "unassigned": len(unassigned),
            "source_by_status": source.get("summary", {}).get("by_status"),
        },
        "classes": classes,
        "research_segments": research_segments,
        "quota_segment": {"segment_id": "quota-surfaces",
                          "members": quota_members},
        "meta_segments": meta_segments,
        "unassigned": unassigned,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(
        ROOT / "apps/help-wanted-dashboard/data/"
               "delphi-rfp-segments-feed.json"))
    a = ap.parse_args()
    feed = build_feed()
    Path(a.out).write_text(json.dumps(feed, indent=1) + "\n")
    print(f"wrote {a.out} totals={feed['totals']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
