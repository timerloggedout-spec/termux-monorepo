#!/usr/bin/env python3
"""Delphi RFP segmentation feed collector (delphi-rfp-feed/v1).

Builds the delphi:rfp progress feed from records of truth — and
nothing else:

  - ops/delphi/rfp-segments.json          (segmentation config)
  - ops/delphi/research-silos.json        (the 12 research silos)
  - ops/delphi/surfaces.json              (the 18 quota surfaces)
  - scripts/delphi/rfp_census_observation.json
        (checked-in GitHub search-API read of the delphi:rfp label,
         stamped with read_at; refresh = re-read the API and replace
         that file in the same PR as the feed refresh — the collector
         never calls the network)

Every open delphi:rfp issue in the census is assigned to exactly one
segment; an issue that matches no segment lands in `unassigned` and
the feed says so — it is never silently dropped or force-fit.

Segmentation (docs/ops/DELPHI-RFP-SEGMENTATION.md): research silos
compare WITHIN their segment only (baseline vs .rnd/.selected/
.control on the three axes); the gate score for research ids is an
admission rubric, uniform by construction, never a comparison
result. Quota surfaces keep the Delphi lane's gate/flywheel
segmentation. Meta/process RFPs are individual segments.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "delphi-rfp-feed/v1"
VARIANTS = ("rnd", "selected", "control")

HONESTY = [
    "Counts are the census snapshot's, stamped with its read_at — not live claims.",
    "A segment's status is computed from the census + recorded outcomes; a stage the record does not hold renders as pending, never synthesized.",
    "The gate score for research.* ids is an admission rubric (synthetic unsourced surfaces, uniform by construction) — never presented as a comparison result.",
    "No cross-silo score aggregation: attribution stays per segment.",
]


def _read(rel: str):
    return json.loads((ROOT / rel).read_text())


def build_feed() -> dict:
    config = _read("ops/delphi/rfp-segments.json")
    silos = _read("ops/delphi/research-silos.json")["silos"]
    surfaces = {s["id"] for s in _read("ops/delphi/surfaces.json")["surfaces"]}
    census = _read("scripts/delphi/rfp_census_observation.json")
    issues = census["issues"]
    by_surface = {i["surface_id"]: i for i in issues if i["surface_id"]}
    by_number = {i["number"]: i for i in issues}
    assigned: set[int] = set()

    def take(issue):
        if issue is None:
            return None
        assigned.add(issue["number"])
        return {"number": issue["number"], "surface_id": issue["surface_id"],
                "title": issue["title"], "url": issue["url"]}

    # --- research silo segments -------------------------------------
    outcomes = {o["scope"]: o for o in census.get("recorded_outcomes", [])}
    baseline_outcome = outcomes.get("research-silo baselines (12)")
    research_segments = []
    for silo in silos:
        sid = silo["id"]
        members = {"baseline": take(by_surface.get(sid))}
        for v in VARIANTS:
            members[v] = take(by_surface.get(f"{sid}.{v}"))
        filed = sum(1 for m in members.values() if m)
        if baseline_outcome and members["baseline"]:
            status = {
                "stage": "gate_scored_axes_pending",
                "gate_award": baseline_outcome["gate_award"],
                "effective_score": baseline_outcome["effective_score"],
                "recheck": baseline_outcome["recheck"],
                "axes_status": baseline_outcome["axes_status"],
            }
        else:
            status = {"stage": "filed", "axes_status": {
                a: "pending" for a in
                config["classes"]["research-silos"]["criteria"]}}
        research_segments.append({
            "segment_id": sid,
            "slot": silo["slot"],
            "role": silo.get("role"),
            "members": members,
            "progress": {"filed": filed, "expected": 4,
                         "axes_recorded": 0,
                         "axes_total": 3},
            "status": status,
        })

    # --- quota surface segment --------------------------------------
    quota_members = []
    for surf_id in sorted(surfaces | {"fly.free_tier"}):
        m = take(by_surface.get(surf_id))
        if m:
            quota_members.append(m)
    quota_segment = {
        "segment_id": "quota-surfaces",
        "members": quota_members,
        "progress": {"filed": len(quota_members),
                     "expected": len(surfaces) + 1},
        "status": {"stage": "gate_flywheel_home_segmentation",
                   "note": "Per-surface gate state lives on the Delphi "
                           "ledgers (#1487 outcomes, #1489 weights); "
                           "this feed does not re-derive it."},
    }

    # --- meta/process segments --------------------------------------
    meta_segments = []
    for slug, number in config["classes"]["meta-process"]["members"].items():
        m = take(by_number.get(number))
        meta_segments.append({
            "segment_id": slug,
            "members": {"self": m},
            "progress": {"filed": 1 if m else 0, "expected": 1},
            "status": {"stage": "filed",
                       "note": "Individual segment; judged on its own "
                               "stated criteria."},
        })

    unassigned = [{"number": i["number"], "surface_id": i["surface_id"],
                   "title": i["title"]}
                  for i in issues if i["number"] not in assigned]

    classes = {}
    for name, cls in config["classes"].items():
        classes[name] = {
            "description": cls["description"],
            "criteria": cls["criteria"],
            "questions": cls["questions"],
            "cycle": cls["cycle"],
        }

    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "generator": "scripts/delphi/rfp_segment_feed.py",
        "sources": {
            "segments_config": "ops/delphi/rfp-segments.json",
            "research_silos": "ops/delphi/research-silos.json",
            "surfaces": "ops/delphi/surfaces.json",
            "census": "scripts/delphi/rfp_census_observation.json",
            "census_read_at": census["read_at"],
        },
        "honesty_rules": HONESTY,
        "totals": {
            "open_delphi_rfp": census["open_total"],
            "census_issues": len(issues),
            "research_segments": len(research_segments),
            "research_members": sum(
                s["progress"]["filed"] for s in research_segments),
            "quota_members": len(quota_members),
            "meta_segments": len(meta_segments),
            "unassigned": len(unassigned),
        },
        "classes": classes,
        "research_segments": research_segments,
        "quota_segment": quota_segment,
        "meta_segments": meta_segments,
        "recorded_outcomes": census.get("recorded_outcomes", []),
        "unassigned": unassigned,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(
        ROOT / "apps/help-wanted-dashboard/data/delphi-rfp-feed.json"))
    a = ap.parse_args()
    feed = build_feed()
    Path(a.out).write_text(json.dumps(feed, indent=1) + "\n")
    print(f"wrote {a.out} ({feed['generated_at']}) "
          f"totals={feed['totals']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
