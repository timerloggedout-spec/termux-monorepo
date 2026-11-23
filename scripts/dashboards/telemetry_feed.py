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
import json
import math
import re
from collections import Counter, deque
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
AGENT_STREAM = "agent_telemetry_stream.json"
PROVIDER_RUNTIME = "apps/tribute-dashboard/data/puter-pool-runtime.json"

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


def _safe_event_text(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.:/@-]{1,256}", value):
        return None
    if value.startswith(("sk-", "ghp_", "github_pat_")):
        return None
    return value


def _recent_puter_requests(limit: int = 20) -> list[dict]:
    path = ROOT / AGENT_STREAM
    if not path.is_file() or path.is_symlink():
        return []
    tail = deque(maxlen=limit)
    try:
        with path.open("rb") as stream:
            size = path.stat().st_size
            if size > 2_000_000:
                stream.seek(size - 2_000_000)
                stream.readline()
            for raw in stream:
                if len(raw) > 64_000:
                    continue
                try:
                    event = json.loads(raw)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                if not isinstance(event, dict) or event.get("event_type") != "provider.inference.completed":
                    continue
                if event.get("entity_id") != "g4f.puter" and event.get("provider_id") != "g4f.puter":
                    continue
                attrs = event.get("attributes") or {}
                if not isinstance(attrs, dict):
                    continue
                latency = attrs.get("latency_ms")
                tokens_in = attrs.get("input_tokens")
                tokens_out = attrs.get("output_tokens")
                tail.append({
                    "occurred_at": event.get("occurred_at") if isinstance(event.get("occurred_at"), str) else None,
                    "request_id": _safe_event_text(attrs.get("request_id")),
                    "exact_model_id": _safe_event_text(attrs.get("exact_model_id")),
                    "outcome": attrs.get("outcome") if attrs.get("outcome") in {"success", "failure"} else "unknown",
                    "latency_ms": latency if isinstance(latency, (int, float)) and not isinstance(latency, bool) and math.isfinite(latency) and latency >= 0 else None,
                    "input_tokens": tokens_in if isinstance(tokens_in, int) and not isinstance(tokens_in, bool) and tokens_in >= 0 else None,
                    "output_tokens": tokens_out if isinstance(tokens_out, int) and not isinstance(tokens_out, bool) and tokens_out >= 0 else None,
                    "task_or_entry_ref": _safe_event_text(attrs.get("task_or_entry_ref")),
                    "doe_run_id": _safe_event_text(attrs.get("doe_run_id")),
                    "workflow_run_id": _safe_event_text(attrs.get("workflow_run_id")),
                    "run_attempt": attrs.get("run_attempt") if isinstance(attrs.get("run_attempt"), int) and not isinstance(attrs.get("run_attempt"), bool) and attrs.get("run_attempt") > 0 else None,
                    "temporal_workflow_id": _safe_event_text(attrs.get("temporal_workflow_id")),
                    "temporal_run_id": _safe_event_text(attrs.get("temporal_run_id")),
                })
    except OSError:
        return []
    return list(reversed(tail))


def collect() -> dict:
    gaps: list[str] = []
    sources: list[dict] = []

    status = _read_json(STATUS)
    quota = _read_json(QUOTA)
    usage = _read_json(QUOTA_USAGE)
    obs = _read_json(OBSERVATIONS)
    act = _read_json(ACTIONS_OBS)
    provider_runtime = _read_json(PROVIDER_RUNTIME)
    recent_puter_requests = _recent_puter_requests()

    for rel, doc, key in ((STATUS, status, "generated_at"),
                          (QUOTA, quota, "generated_at"),
                          (QUOTA_USAGE, usage, "generated_at"),
                          (OBSERVATIONS, obs, "read_at"),
                          (ACTIONS_OBS, act, "read_at"),
                          (PROVIDER_RUNTIME, provider_runtime, "observed_at")):
        if doc is None:
            gaps.append(f"source missing at collection time: {rel}")
        else:
            sources.append({"path": rel, "stamped_at": doc.get(key)})

    agent_path = ROOT / AGENT_STREAM
    if agent_path.is_file():
        sources.append({"path": AGENT_STREAM, "stamped_at": recent_puter_requests[0]["occurred_at"] if recent_puter_requests else None})
    else:
        gaps.append(f"source missing at collection time: {AGENT_STREAM}")
    if not recent_puter_requests:
        gaps.append("Puter Pool per-request inference events not yet observed in agent_telemetry_stream.json.")

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

    # ---- Puter Pool runtime and correlation -------------------------------
    provider_runtime_block = None
    if provider_runtime is not None:
        if provider_runtime.get("schema") == "provider-runtime-observation/v1" and provider_runtime.get("provider_id") == "g4f.puter":
            pool = provider_runtime.get("pool") or {}
            provider_runtime_block = {
                "provider_id": "g4f.puter",
                "provider": "g4f/Puter",
                "source_repository": provider_runtime.get("source_repository"),
                "observed_at": provider_runtime.get("observed_at"),
                "health": pool.get("health"),
                "readiness": pool.get("readiness"),
                "strategy": pool.get("strategy"),
                "model_count": pool.get("model_count"),
                "model_ids": pool.get("model_ids") or [],
                "counters": pool.get("counters") or {},
                "quota": provider_runtime.get("quota") or {"status": "unknown", "used": None, "limit": None, "reset": None},
                "correlation": provider_runtime.get("correlation") or {},
                "recent_requests": recent_puter_requests,
            }
        else:
            gaps.append("Puter Pool runtime snapshot has an unrecognized schema or provider identity; provider runtime block withheld.")
    else:
        gaps.append(f"Puter Pool runtime snapshot not yet observed: {PROVIDER_RUNTIME} is absent.")

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
        "generated_at": _now(),
        "sources": sources,
        "honesty_rules": HONESTY,
        "data": {
            "golden": golden,
            "executions": executions,
            "actions": actions,
            "outcomes": outcomes,
            "quota": quota_block,
            "provider_runtime": provider_runtime_block,
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
