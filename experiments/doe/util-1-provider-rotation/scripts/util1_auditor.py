#!/usr/bin/env python3
"""util-1 auditor: read desk-feed dispatch stamps, emit EXPERIMENT records.
Bench is read from the registry at run time (DOE-FAMILY rule 6: routes
re-verified, never pinned). Unstamped dispatches are flagged, not scored."""
import json, sys, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parents[4]
FEED = ROOT / "apps/help-wanted-dashboard/data/desk-feed.json"
REG = ROOT / "ops/quota/registry.json"
OUT = ROOT / "experiments/doe/util-1-provider-rotation/records"

def bench():
    """Return the provider bench from the live registry without pinning it."""
    try:
        reg = json.loads(REG.read_text())
        if isinstance(reg, list):
            rows = reg
        else:  # quota.registry.v2: services[]; tolerate providers[] too
            rows = reg.get("services") or reg.get("providers") or []
        return sorted({(r.get("provider") or r.get("id") or r.get("name"))
                       for r in rows if isinstance(r, dict)} - {None})
    except Exception:
        return []

def main():
    """Audit desk dispatches and persist evidence-backed experiment records."""
    OUT.mkdir(parents=True, exist_ok=True)
    feed = json.loads(FEED.read_text()) if FEED.exists() else {}
    dispatches = []
    if isinstance(feed, dict):
        # desk-feed/v1.3 shape: stamps live at traversals[].provider_usage[]
        for trav in feed.get("traversals", []) or []:
            if not isinstance(trav, dict):
                continue
            unit = trav.get("entry") or trav.get("id") or trav.get("name")
            for row in trav.get("provider_usage", []) or []:
                if isinstance(row, dict):
                    dispatches.append({**row, "id": row.get("id") or unit})
        # forward-compat: a future top-level dispatches list wins if present
        if isinstance(feed.get("dispatches"), list) and feed["dispatches"]:
            dispatches = feed["dispatches"]
    known = set(bench())
    scored, flagged = [], []
    for d in dispatches:
        if not isinstance(d, dict):
            continue
        stamp = {k: d.get(k) for k in ("provider", "selection_reason", "ts")}
        if not stamp["provider"] or not stamp["ts"]:
            flagged.append({"unit": d.get("id"), "reason": "missing_stamp"})
            continue
        scored.append({
            "schema": "EXPERIMENT", "campaign_id": "util-1-provider-rotation",
            "unit": d.get("id"), "provider": stamp["provider"],
            "in_registry": stamp["provider"] in known if known else None,
            "selection_reason": stamp["selection_reason"],
            "ts": stamp["ts"],
            **{key: d[key] for key in (
                "model_id", "protocol", "workflow_id", "run_id", "run_attempt",
                "temporal_workflow_id", "request_id", "doe_campaign_id",
                "experiment_instance_key",
            ) if d.get(key) is not None},
            "responses": {k: d.get(k) for k in
                          ("first_pass_success", "rework_cycles", "dispatch_to_pr_wall_time", "stalled_action_required")},
            "usage": {k: d.get(k) for k in (
                "input_tokens", "output_tokens", "total_tokens", "quota_tokens",
                "usage_cost", "latency_ms", "time_to_first_token_ms", "tokens_per_second",
            ) if d.get(k) is not None},
            "status": "scored" if d.get("first_pass_success") is not None else "awaiting_outcome"})
    summary = {"campaign_id": "util-1-provider-rotation",
               "audited_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "bench_size": len(known), "scored": len(scored), "flagged": len(flagged)}
    (OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=1) + "\n")
    (OUT / "latest-audit.json").write_text(json.dumps(
        {"summary": summary, "scored": scored, "flagged": flagged}, indent=1) + "\n")
    print(json.dumps(summary))
    return 0

if __name__ == "__main__":
    sys.exit(main())
