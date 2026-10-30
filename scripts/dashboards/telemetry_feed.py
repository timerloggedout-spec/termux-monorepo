"""Telemetry-viz feed — Slice 1 (S1-proxy / S2 / S4).

Reads only committed repository records and emits one feed JSON into
apps/help-wanted-dashboard/data/. The telemetry page (Web Design lane)
consumes this feed and nothing else. Facts the records do not hold are
emitted as named gaps, never synthesized: an unobserved value stays
null/absent, never 0. Refresh = re-run this collector and land the
result by PR, exactly like the surface feeds.

Sources (all committed, no network):
- S2 outcome ledger ...... apps/help-wanted-dashboard/data/status.json
- S4 quota readings ...... apps/help-wanted-dashboard/data/quota.json
- S5 quota usage pack .... apps/help-wanted-dashboard/data/quota-usage.json
- S1-proxy executions .... scripts/dashboards/workflow_observations.json
  (checked-in Actions API observations snapshot, stamped read_at) plus
  the status.json lane receipts. The Neon lane_events table itself is
  NOT page-readable (recon gap G3) — this is a proxy, labeled as such.

Design + stream inventory: docs/ops/TELEMETRY-VIZ-RECON.md
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "apps" / "help-wanted-dashboard" / "data"
SCHEMA = "telemetry-viz-feed/v1"

STATUS = "apps/help-wanted-dashboard/data/status.json"
QUOTA = "apps/help-wanted-dashboard/data/quota.json"
QUOTA_USAGE = "apps/help-wanted-dashboard/data/quota-usage.json"
OBSERVATIONS = "scripts/dashboards/workflow_observations.json"

HONESTY = [
    "Show only what the record holds; a value the record does not hold renders as absent, never synthesized.",
    "Absence is never zero: unobserved quota readings stay null and are counted as unobserved, not as 0 used.",
    "Executions are a committed-projection proxy (recon gap G3): the Neon lane_events table is not read by this collector and no live run state is claimed.",
    "Workflow run counts are API observations stamped with their read time, not live claims.",
    "Derived values are labeled derived and computed from the source fields named beside them.",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(rel: str):
    p = ROOT / rel
    if not p.exists():
        return None
    return json.loads(p.read_text())


def collect() -> dict:
    gaps: list[str] = []
    sources: list[dict] = []

    status = _read_json(STATUS)
    quota = _read_json(QUOTA)
    usage = _read_json(QUOTA_USAGE)
    obs = _read_json(OBSERVATIONS)

    for rel, doc, key in ((STATUS, status, "generated_at"),
                          (QUOTA, quota, "generated_at"),
                          (QUOTA_USAGE, usage, "generated_at"),
                          (OBSERVATIONS, obs, "read_at")):
        if doc is None:
            gaps.append(f"source missing at collection time: {rel}")
        else:
            sources.append({"path": rel, "stamped_at": doc.get(key)})

    # ---- S2: outcome ledger (status.json) --------------------------------
    outcomes = None
    if status is not None:
        outcomes = {
            "lane": status.get("lane"),
            "project": status.get("project"),
            "generated_at": status.get("generated_at"),
            "receipts": status.get("receipts"),
            "kinds": status.get("kinds"),
            "outcomes": status.get("outcomes"),
            "outcome_semantics": status.get("outcome_semantics"),
            "tribute_count": status.get("tribute_count"),
            "foreign_open_count": status.get("foreign_open_count"),
            "issues_tracked": len(status.get("issues") or {}),
        }

    # ---- S1-proxy: executions --------------------------------------------
    executions = None
    if obs is not None:
        workflows = obs.get("workflows") or {}
        executions = {
            "kind": "committed_projection_proxy",
            "source_snapshot": OBSERVATIONS,
            "read_at": obs.get("read_at"),
            "workflows_observed": len(workflows),
            "total_runs_observed": sum(int(w.get("total_runs") or 0)
                                       for w in workflows.values()),
            "workflows": {
                name: {"total_runs": w.get("total_runs"),
                       "latest": w.get("latest")}
                for name, w in sorted(workflows.items())
            },
        }
        gaps.append(
            "G1/G3: executions are proxied from the checked-in observations "
            f"snapshot (read_at {obs.get('read_at')}, {len(workflows)} "
            "workflows) plus status.json lane receipts; there is no "
            "consolidated Actions run-corpus feed and the Neon lane_events "
            "table is not page-readable.")
    if status is not None:
        if executions is None:
            executions = {"kind": "committed_projection_proxy", "workflows": {}}
        executions["lane_receipts"] = {
            "lane": status.get("lane"),
            "receipts": status.get("receipts"),
            "kinds": status.get("kinds"),
            "generated_at": status.get("generated_at"),
        }

    # ---- S4/S5: quota ------------------------------------------------------
    quota_block = None
    if quota is not None:
        readings = quota.get("readings") or []
        measured = [
            {"resource_id": r.get("resource_id"), "used": r.get("used"),
             "limit": r.get("limit"), "unit": r.get("unit"),
             "saturation": (round(r["used"] / r["limit"], 6)
                            if r.get("limit") else None),
             "observed_at": r.get("observed_at")}
            for r in readings
            if r.get("used") is not None and r.get("limit") is not None
        ]
        quota_block = {
            "generated_at": quota.get("generated_at"),
            "readings_total": len(readings),
            "by_status": dict(Counter(r.get("status") for r in readings)),
            "by_horizon": dict(Counter(r.get("horizon") for r in readings)),
            "by_evidence_status": dict(Counter(
                r.get("evidence_status") for r in readings)),
            "measured": measured,
            "unmeasured_count": len(readings) - len(measured),
        }
        if not measured:
            gaps.append(
                "quota saturation NOT OBSERVED: 0 of "
                f"{len(readings)} readings carry both used and limit; "
                "saturation renders as absent, never 0.")
    if usage is not None:
        if quota_block is None:
            quota_block = {}
        s1 = usage.get("series1_api_core") or {}
        s3 = usage.get("series3_actions") or {}
        points = s1.get("points") or []
        quota_block["usage_pack"] = {
            "generated_at": usage.get("generated_at"),
            "api_core": {
                "title": s1.get("title"), "limit": s1.get("limit"),
                "unit": s1.get("unit"),
                "replenishment": s1.get("replenishment"),
                "next_reset_observed": s1.get("next_reset_observed"),
                "points": points,
                "latest_point": points[-1] if points else None,
            },
            "actions_corpus": {
                "title": s3.get("title"), "method": s3.get("method"),
                "days": s3.get("days"), "spike": s3.get("spike"),
            },
            "annotations_count": len(usage.get("annotations") or []),
            "stamps_count": len(usage.get("stamps") or []),
            "buckets": usage.get("buckets"),
        }

    # ---- golden top row ----------------------------------------------------
    golden = {
        "receipts_total": (status or {}).get("receipts"),
        "actioned": ((status or {}).get("outcomes") or {}).get("actioned"),
        "skipped": ((status or {}).get("outcomes") or {}).get("skipped"),
        "quota_readings_total": quota_block.get("readings_total") if quota_block else None,
        "quota_measured_count": len(quota_block["measured"]) if quota_block else None,
        "quota_saturation": None,  # derived only when a measured reading exists
        "workflows_observed": executions.get("workflows_observed") if executions else None,
        "workflow_runs_observed": executions.get("total_runs_observed") if executions else None,
    }
    if quota_block and quota_block["measured"]:
        sats = [m["saturation"] for m in quota_block["measured"]
                if m["saturation"] is not None]
        golden["quota_saturation"] = {
            "kind": "derived_max_of_measured_readings",
            "value": max(sats) if sats else None,
        }

    return {
        "schema": SCHEMA,
        "surface": "telemetry",
        "generated_at": _now(),
        "sources": sources,
        "honesty_rules": HONESTY,
        "data": {
            "golden": golden,
            "executions": executions,
            "outcomes": outcomes,
            "quota": quota_block,
        },
        "gaps": gaps,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", default=str(DATA))
    args = ap.parse_args()
    feed = collect()
    out = Path(args.out_dir) / "telemetry-feed.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(feed, indent=1) + "\n")
    print(f"wrote {out} (gaps: {len(feed['gaps'])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
