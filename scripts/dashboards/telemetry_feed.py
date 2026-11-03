"""Telemetry-viz feed — Slice 1 (S1-proxy / S2 / S4).

Reads only committed repository records and emits one feed JSON into
apps/tribute-dashboard/data/. The telemetry page (Web Design lane)
consumes this feed and nothing else. Facts the records do not hold are
emitted as named gaps, never synthesized: an unobserved value stays
null/absent, never 0. Refresh = re-run this collector and land the
result by PR, exactly like the surface feeds.

Sources (all committed, no network):
- S2 outcome ledger ...... apps/tribute-dashboard/data/status.json
- S4 quota readings ...... apps/tribute-dashboard/data/quota.json
- S5 quota usage pack .... apps/tribute-dashboard/data/quota-usage.json
- S1-proxy executions .... scripts/dashboards/workflow_observations.json
  (checked-in Actions API observations snapshot, stamped read_at) plus
  the status.json lane receipts. The Neon lane_events table itself is
  NOT page-readable (recon gap G3) — this is a proxy, labeled as such.

Design + stream inventory: docs/ops/TELEMETRY-VIZ-RECON.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "apps" / "tribute-dashboard" / "data"
SCHEMA = "telemetry-viz-feed/v1"

STATUS = "apps/tribute-dashboard/data/status.json"
QUOTA = "apps/tribute-dashboard/data/quota.json"
QUOTA_USAGE = "apps/tribute-dashboard/data/quota-usage.json"
OBSERVATIONS = "scripts/dashboards/workflow_observations.json"
ACTIONS_OBS = "scripts/dashboards/actions_observations.json"

HONESTY = [
    "Show only what the record holds; a value the record does not hold renders as absent, never synthesized.",
    "Absence is never zero: unobserved quota readings stay null and are counted as unobserved, not as 0 used.",
    "Executions are a committed-projection proxy (recon gap G3): the Neon lane_events table is not read by this collector and no live run state is claimed.",
    "Workflow run counts are API observations stamped with their read time, not live claims.",
    "Derived values are labeled derived and computed from the source fields named beside them.",
]


def atomic_write(path: Path, content: str) -> None:
    """Atomically replace a generated feed; readers see old or complete new bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(rel: str, gaps=None, sources=None, stamp_key="generated_at", now=None):
    """Read one committed source without turning absence or corruption into zero."""
    gaps = gaps if gaps is not None else []
    sources = sources if sources is not None else []
    now = now or datetime.now(timezone.utc)
    path = ROOT / rel
    meta = {"path": rel, "state": "missing", "stamped_at": None,
            "age_hours": None, "source_sha256": None, "size_bytes": 0}
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        meta["reason"] = "source missing"
        gaps.append(f"source missing at collection time: {rel}")
        sources.append(meta)
        return None
    except OSError as exc:
        meta.update(state="unavailable", reason=f"read failed: {exc}")
        gaps.append(f"source unavailable: {rel}")
        sources.append(meta)
        return None
    meta["size_bytes"] = len(raw)
    meta["source_sha256"] = hashlib.sha256(raw).hexdigest()
    if not raw.strip():
        meta.update(state="invalid", reason="empty source; missing evidence is not zero")
        gaps.append(f"source empty/invalid: {rel}")
        sources.append(meta)
        return None
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        meta.update(state="invalid", reason="source is not valid UTF-8 JSON")
        gaps.append(f"source malformed: {rel}")
        sources.append(meta)
        return None
    if not isinstance(payload, dict):
        meta.update(state="invalid", reason="JSON root must be an object")
        gaps.append(f"source root invalid: {rel}")
        sources.append(meta)
        return None
    stamp = payload.get(stamp_key)
    meta["stamped_at"] = stamp
    if not isinstance(stamp, str) or not stamp.strip():
        meta.update(state="unknown", reason=f"{stamp_key} timestamp missing")
        gaps.append(f"source timestamp unknown: {rel}")
        sources.append(meta)
        return payload
    try:
        parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        meta.update(state="invalid", reason=f"{stamp_key} is not ISO-8601")
        gaps.append(f"source timestamp invalid: {rel}")
        sources.append(meta)
        return payload
    if parsed.tzinfo is None:
        meta.update(state="invalid", reason=f"{stamp_key} lacks timezone")
        gaps.append(f"source timestamp has no timezone: {rel}")
        sources.append(meta)
        return payload
    age = (now - parsed.astimezone(timezone.utc)).total_seconds() / 3600
    meta["age_hours"] = round(age, 3)
    if age < -1:
        meta.update(state="clock_skew", reason="source timestamp is in the future")
        gaps.append(f"source timestamp is in the future: {rel}")
    elif age > 24:
        meta.update(state="stale", reason=f"source is {age:.1f}h old")
        gaps.append(f"source stale (>24h): {rel}")
    else:
        meta["state"] = "fresh"
    sources.append(meta)
    return payload


def collect() -> dict:
    gaps: list[str] = []
    sources: list[dict] = []

    now = datetime.now(timezone.utc)
    status = _read_json(STATUS, gaps, sources, "generated_at", now)
    quota = _read_json(QUOTA, gaps, sources, "generated_at", now)
    usage = _read_json(QUOTA_USAGE, gaps, sources, "generated_at", now)
    obs = _read_json(OBSERVATIONS, gaps, sources, "read_at", now)
    act = _read_json(ACTIONS_OBS, gaps, sources, "read_at", now)
    source_states = [item["state"] for item in sources]
    collection_state = "complete" if source_states and all(s == "fresh" for s in source_states) else "partial"
    freshness = "stale" if "stale" in source_states else ("fresh" if collection_state == "complete" else "unknown")

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
            "G3: executions are proxied from the checked-in observations "
            f"snapshot (read_at {obs.get('read_at')}, {len(workflows)} "
            "workflows) plus status.json lane receipts; the Neon "
            "lane_events table is not page-readable. The consolidated "
            "Actions corpus lives in the actions block (Slice 2, G1 "
            "partial).")
    if status is not None:
        if executions is None:
            executions = {"kind": "committed_projection_proxy", "workflows": {}}
        executions["lane_receipts"] = {
            "lane": status.get("lane"),
            "receipts": status.get("receipts"),
            "kinds": status.get("kinds"),
            "generated_at": status.get("generated_at"),
        }

    # ---- S6: Actions corpus (Slice 2, gap G1 partial) ---------------------
    actions = None
    if act is not None:
        actions = {
            "kind": "api_observations_snapshot",
            "source_snapshot": ACTIONS_OBS,
            "read_at": act.get("read_at"),
            "budget": act.get("budget"),
            "window": act.get("window"),
            "totals": act.get("totals"),
            "workflows": act.get("workflows"),
            "join": {
                "key": "run_id",
                "s1_source": "Neon lane_events (append-only; run_id + "
                             "run_attempt + subject)",
                "status": "join key defined and carried per workflow as "
                          "latest.id; the join itself is unexecuted — "
                          "lane_events is not page-readable and no "
                          "committed lane-events projection exists (G3).",
            },
        }
        gaps.append(
            "G1 partial: the Actions corpus is a budgeted stride-sample "
            f"snapshot (read_at {act.get('read_at')}, "
            f"{(act.get('budget') or {}).get('runs_fetched')} runs sampled, "
            "pages "
            f"{(act.get('budget') or {}).get('pages_sampled')}); it is not "
            "the full run history — that remains the locally reconstructed "
            "daily corpus (quota usage_pack.actions_corpus).")
    else:
        gaps.append(
            "G1: no Actions corpus snapshot at collection time "
            f"({ACTIONS_OBS} missing); actions block absent.")

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
        "actions_runs_sampled": (actions.get("totals") or {}).get("runs") if actions else None,
        "actions_failure_rate": (actions.get("totals") or {}).get("failure_rate") if actions else None,
        "actions_workflows_sampled": (actions.get("totals") or {}).get("workflows") if actions else None,
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
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "state": collection_state,
        "freshness": freshness,
        "source_count": len(sources),
        "expected_source_count": 5,
        "sources": sources,
        "honesty_rules": HONESTY,
        "data": {
            "golden": golden,
            "executions": executions,
            "actions": actions,
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
