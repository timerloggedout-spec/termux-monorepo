#!/usr/bin/env python3
"""Dispatch stamp fan-out — the Swarm routing layer's emission point.

Owner routing update (2026-11-01): every routed+assigned dispatch emits
its full stamp {task class, arm/provider, model, run id, outcome,
quota/cost class} to EACH scoring plane's intake (HindSight/Provenance
substrate), not just the desk-feed. One canonical stamp in, four plane
intakes out:

  1. 3L0        ops/3l0/intake.jsonl                       (3l0-intake/v1, append-only)
  2. DoE        ops/challenge/desk-feed.json               (traversals[].provider_usage[] carrier)
  3. DoE/MVT/ATES experiments/doe/routed-dispatch/records/ (EXPERIMENT schema 1.0 record per dispatch)
  4. MoneyBall  ops/moneyball/routed-dispatch/<record>.json (moneyball-plane/v2 score record per
                                                            dispatch, schema docs/schemas/moneyball-score.schema.json;
                                                            deterministic rubric below, weights fixed at the
                                                            swarm-routing/v2 intake; winprob/method work
                                                            stays parked — population only)

Honesty discipline (binding, per the planes' intake specs): a field the
dispatch does not establish is emitted as null / NOT_ESTABLISHED, never
invented. Usage value is null unless measured/estimated. Emission is
idempotent per dispatch_id.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

NE = "NOT_ESTABLISHED"
CAMPAIGN = "routed-dispatch"
COHORT = "routed-dispatch-2026-11"
MANAGER_POLICY = "swarm-routing/v2 (owner routing update 2026-11-01)"


def _instance_key(root: Path, instance: dict) -> str | None:
    """instance_key per scripts/doe/instance_key.py, when the tuple is complete."""
    try:
        sys.path.insert(0, str(root))
        from scripts.doe.instance_key import instance_key as _ik  # type: ignore
        return _ik(
            provider=instance["provider"],
            model=instance["model"],
            system_prompt_sha256=instance["system_prompt"]["sha256"],
            tools_sha256_=instance["tools"]["sha256"],
            role=instance["role"],
            moniker=instance["moniker"],
            context=instance["context"],
        )
    except Exception:
        return None


def _status_map(status: str) -> str:
    return {"completed": "passed", "failed": "failed"}.get(status, "observed")


def emit(stamp: dict, root: Path, head_sha: str | None = None) -> dict:
    dispatch_id = stamp["dispatch_id"]
    ts = stamp["ts"]
    run = stamp.get("run") or {}
    outcome = stamp.get("outcome") or {}
    quota = stamp.get("quota") or {}
    usage = stamp.get("usage") or {"status": "not_established", "value": None, "unit": None, "source": None}
    if usage.get("status") not in ("measured", "estimated"):
        usage = {**usage, "value": None}
    provider = stamp.get("provider")
    model = stamp.get("model")
    instance = stamp.get("instance")
    run_url = None
    if run.get("run_id"):
        run_url = f"https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/{run['run_id']}"

    # Idempotency: a dispatch_id already in the 3L0 intake is fully emitted.
    intake_path = root / "ops/3l0/intake.jsonl"
    if intake_path.exists():
        for line in intake_path.read_text().splitlines():
            if line.strip() and json.loads(line).get("dispatch_id") == dispatch_id:
                return {"dispatch_id": dispatch_id, "emitted": False, "reason": "already emitted"}

    # ---- 1. 3L0 intake (3l0-intake/v1) ----
    if instance:
        inst_out = {
            "system_prompt": {"ref": instance["system_prompt"]["ref"], "sha256": instance["system_prompt"]["sha256"]},
            "tools": {"ref": instance["tools"]["ref"], "sha256": instance["tools"]["sha256"]},
            "instance_key": _instance_key(root, instance) or NE,
        }
    else:
        inst_out = {"system_prompt": {"ref": NE, "sha256": NE}, "tools": {"ref": NE, "sha256": NE}, "instance_key": NE}
    rec_3l0 = {
        "schema": "3l0-intake/v1",
        "dispatch_id": dispatch_id,
        "ts": ts,
        "provider": provider or NE,
        "model": model or NE,
        "endpoint": stamp.get("endpoint") or (f"{provider}::{model}" if provider and model else NE),
        "moniker": stamp.get("moniker") or NE,
        "role": stamp.get("role") or NE,
        "context": stamp.get("context") or stamp.get("task_class") or NE,
        "instance": inst_out,
        "run": {"session_id": run.get("session_id"), "workflow": run.get("workflow"), "run_id": run.get("run_id")},
        "outcome": {
            "status": outcome.get("status") or NE,
            "gate_call": outcome.get("gate_call"),
            "confirmed": outcome.get("confirmed"),
            "artifact": outcome.get("artifact"),
        },
        "usage": {"tokens_in": usage.get("tokens_in"), "tokens_out": usage.get("tokens_out"),
                  "latency_ms": usage.get("latency_ms"), "retries": usage.get("retries")},
        "quota": {"pool": quota.get("pool"), "slice": quota.get("slice"), "cost_class": quota.get("cost_class")},
        "origin": stamp.get("origin", "live"),
    }
    intake_path.parent.mkdir(parents=True, exist_ok=True)
    with intake_path.open("a") as fh:
        fh.write(json.dumps(rec_3l0, sort_keys=True) + "\n")

    # ---- 2. MoneyBall scoring-feed record (moneyball-plane/v2) ----
    # Rubric (declared, deterministic; weights fixed at intake per the
    # plane's weight law — fixed_at names this routing update):
    #   relevance              task-class table (declared below)
    #   evidence_maturity      outcome evidence: completed+artifact+run -> 9 evidenced;
    #                          completed -> 6 limited; failed -> 3 limited; else 2 unverified
    #   survivability          arm state: live -> 8, degraded -> 4, down -> 1, unknown -> 5 unverified
    #   adoption_cost_inverse  cost class: free-tier 10, free-credit 8, metered 4, funded-out 1, card-gated 0
    #   composability          task-class table (declared below)
    # Quantities stay null = unidentified (schema-visible), never invented.
    MB_WEIGHTS = {"relevance": 0.30, "evidence_maturity": 0.25, "survivability": 0.20,
                  "adoption_cost_inverse": 0.15, "composability": 0.10}
    relevance_tbl = {"entry-build": 9, "certifications-unit": 7, "review": 7,
                     "inference-probe": 6, "docs": 5}
    composability_tbl = {"certifications-unit": 9, "entry-build": 8, "inference-probe": 7, "review": 6}
    cost_tbl = {"free-tier": 10, "free-credit": 8, "metered": 4, "funded-out": 1, "card-gated": 0}
    arm_state = stamp.get("arm_state") or "unknown"
    surv_tbl = {"live": (8, "evidenced"), "degraded": (4, "limited"), "down": (1, "limited"),
                "unknown": (5, "unverified")}
    status = outcome.get("status")
    if status == "completed" and outcome.get("artifact") and run.get("run_id"):
        em = (9, "evidenced")
    elif status == "completed":
        em = (6, "limited")
    elif status == "failed":
        em = (3, "limited")
    else:
        em = (2, "unverified")
    ev_refs = [r for r in (run_url, outcome.get("artifact")) if r]
    tc = stamp.get("task_class") or ""
    axes = [
        {"axis": "relevance", "value": relevance_tbl.get(tc, 5), "evidence_refs": ev_refs or [NE],
         "evidence_strength": "limited"},
        {"axis": "evidence_maturity", "value": em[0], "evidence_refs": ev_refs or [NE],
         "evidence_strength": em[1]},
        {"axis": "survivability", "value": surv_tbl.get(arm_state, surv_tbl["unknown"])[0],
         "evidence_refs": ev_refs or [NE], "evidence_strength": surv_tbl.get(arm_state, surv_tbl["unknown"])[1]},
        {"axis": "adoption_cost_inverse", "value": cost_tbl.get(quota.get("cost_class"), 5),
         "evidence_refs": ev_refs or [NE],
         "evidence_strength": "evidenced" if quota.get("cost_class") in cost_tbl else "unverified"},
        {"axis": "composability", "value": composability_tbl.get(tc, 5), "evidence_refs": ev_refs or [NE],
         "evidence_strength": "limited"},
    ]
    composite = round(sum(MB_WEIGHTS[a["axis"]] * a["value"] for a in axes), 4)
    rec_mb = {
        "schema": "moneyball-plane/v2",
        "record_id": f"mb-{dispatch_id}",
        "pass_id": "swarm-routing/v2",
        "opportunity": {"entity_id": f"{provider or NE}::{model or NE}", "action": "route-dispatch",
                        "context": f"{tc}: {stamp.get('context') or ''}".strip(),
                        "decision_time": ts},
        "baseline_id": "desk-feed-only-routing/v1",
        "weights": {"axes": MB_WEIGHTS, "fixed_at": "swarm-routing/v2 intake 2026-11-01 (owner routing update)"},
        "axes": axes,
        "composite": composite,
        "quantities": {"capability": None, "forecast": None, "incremental_effect": None,
                       "value": None, "surplus": None, "portfolio_marginal_contribution": None},
        "ballot": {"relation": "beside_never_merged", "aggregate": None},
        "point_in_time": {"event_time": ts, "published_at": ts, "ingested_at": ts},
        "rubric": "scripts/dispatch/stamp_fanout.py (declared tables; quantities null = unidentified)",
    }
    mb_dir = root / "ops/moneyball/routed-dispatch"
    mb_dir.mkdir(parents=True, exist_ok=True)
    safe_mb = "".join(c if c.isalnum() or c in "-_" else "-" for c in dispatch_id)
    (mb_dir / f"{safe_mb}.json").write_text(json.dumps(rec_mb, indent=2, sort_keys=True) + "\n")

    # ---- 3. EXPERIMENT record (DoE scored records + MVT/ATES intake) ----
    baseline = stamp.get("baseline_sha") or head_sha
    candidate = stamp.get("candidate_sha") or head_sha
    if not (baseline and candidate):
        raise SystemExit("baseline/candidate SHA unavailable: pass --head-sha or include SHAs in the stamp")
    exp_instance = None
    if instance:
        exp_instance = {
            "provider": instance["provider"],
            "model": instance["model"],
            "system_prompt": {"ref": instance["system_prompt"]["ref"], "sha256": instance["system_prompt"]["sha256"]},
            "tools": {"ref": instance["tools"]["ref"], "sha256": instance["tools"]["sha256"]},
            "role": instance["role"],
            "moniker": instance["moniker"],
            "context": instance["context"],
            "instance_key": _instance_key(root, instance),
        }
    rec_exp = {
        "schema_version": "1.0",
        "experiment_id": CAMPAIGN,
        "observed_at": ts,
        "baseline_sha": baseline,
        "candidate_sha": candidate,
        "suite": stamp.get("suite") or "routed-dispatch/v1",
        "cohort": COHORT,
        "treatment": {
            "manager_policy_id": MANAGER_POLICY,
            "provider": provider,
            "model": model,
            "arm": provider,
            "instance": exp_instance,
        },
        "status": _status_map(outcome.get("status", "")),
        "outcome": outcome.get("summary"),
        "provenance": "github",
        "confidence": "high",
        "evidence_refs": [run_url] if run_url else [],
        "session_id": run.get("session_id"),
        "window": None,
        "usage": {"status": usage.get("status", "not_established"), "value": usage.get("value"),
                  "unit": usage.get("unit"), "source": usage.get("source")},
        "metrics": {
            "task_class": stamp.get("task_class"),
            "quota_cost_class": quota.get("cost_class"),
            "dispatch_status": outcome.get("status"),
            "set_index": stamp.get("set_index"),
            "cumulative_n": stamp.get("cumulative_n"),
            "selection_reason": stamp.get("selection_reason"),
            "ates_outcome": None,
        },
    }
    rec_exp["origin"] = stamp.get("origin", "live")
    rec_dir = root / f"experiments/doe/{CAMPAIGN}/records"
    rec_dir.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in dispatch_id)
    (rec_dir / f"{safe}.json").write_text(json.dumps(rec_exp, indent=2, sort_keys=True) + "\n")
    # Backfill doctrine: the canonical stamp itself is retained beside the
    # record, so any future scoring/emitter version can re-derive every
    # plane's records from the full history (stable stamps, nothing dropped).
    stamp_dir = root / f"experiments/doe/{CAMPAIGN}/stamps"
    stamp_dir.mkdir(parents=True, exist_ok=True)
    (stamp_dir / f"{safe}.json").write_text(json.dumps(stamp, indent=2, sort_keys=True) + "\n")

    # ---- 4. DoE live carrier: desk-feed traversal provider_usage ----
    feed_path = root / "ops/challenge/desk-feed.json"
    feed = json.loads(feed_path.read_text())
    trav = next((t for t in feed.get("traversals", []) if t.get("entry") == CAMPAIGN), None)
    if trav is None:
        trav = {"entry": CAMPAIGN, "project": "Routed dispatch stamp carrier (DoE intake, docs/ops/DOE-SCORING-INTAKE.md)",
                "status": "live", "provider_usage": []}
        feed.setdefault("traversals", []).append(trav)
    trav.setdefault("provider_usage", []).append({
        "provider": provider or NE,
        "via": run.get("workflow") or NE,
        "session_id": run.get("session_id"),
        "state": "landed" if outcome.get("status") == "completed" else (outcome.get("status") or NE),
        "usage": {"value": usage.get("value"), "unit": usage.get("unit"), "source": usage.get("source"),
                  "window": None, "match": None,
                  "note": f"dispatch {dispatch_id}: routed stamp fan-out (swarm-routing/v2); consumption per usage.status.",
                  "status": usage.get("status", "not_established")},
        "model": model or NE,
        "phrases": NE,
    })
    feed_path.write_text(json.dumps(feed, indent=2) + "\n")

    return {"dispatch_id": dispatch_id, "emitted": True,
            "targets": ["ops/3l0/intake.jsonl", "ops/moneyball/routed-dispatch/<record>.json",
                        f"experiments/doe/{CAMPAIGN}/records/{safe}.json", "ops/challenge/desk-feed.json"]}


def emit_outcome_fill(stamp: dict, root: Path) -> dict:
    """Second phase (DoE intake spec): the outcome fill at PR/merge close.

    Updates the dispatch's EXPERIMENT record metrics + desk-feed carrier
    state. Never appends duplicate 3L0/MoneyBall records — those intakes
    are append-only per completed dispatch.
    """
    dispatch_id = stamp["dispatch_id"]
    fill = stamp.get("outcome_fill") or {}
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in dispatch_id)
    rec_path = root / f"experiments/doe/{CAMPAIGN}/records/{safe}.json"
    if not rec_path.exists():
        raise SystemExit(f"outcome fill for unemitted dispatch {dispatch_id}: no record at {rec_path}")
    rec = json.loads(rec_path.read_text())
    metrics = rec.setdefault("metrics", {})
    for key in ("first_pass_success", "rework_cycles", "dispatch_to_pr_wall_time",
                "stalled_action_required", "pr"):
        if key in fill:
            metrics[key] = fill[key]
    if fill.get("pr"):
        rec.setdefault("evidence_refs", []).append(f"https://github.com/timerloggedout-spec/termux-monorepo/pull/{fill['pr']}")
    rec_path.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    return {"dispatch_id": dispatch_id, "emitted": True, "phase": "outcome_fill",
            "targets": [f"experiments/doe/{CAMPAIGN}/records/{safe}.json"]}


def emit_score_fill(stamp: dict, root: Path) -> dict:
    """Third phase (MVT/ATES intake): ATES scoring keys at merge close.

    Deterministic keys derive from the dispatch's required-gate record;
    the judge keys come from an evaluator dispatch (instance != builder)
    over committed evidence only. Keys land in the record's metrics with
    the evaluator's provenance; nothing here is synthesized — a missing
    input raises instead of defaulting.
    """
    dispatch_id = stamp["dispatch_id"]
    score = stamp["score"]
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in dispatch_id)
    rec_path = root / f"experiments/doe/{CAMPAIGN}/records/{safe}.json"
    if not rec_path.exists():
        raise SystemExit(f"score fill for unemitted dispatch {dispatch_id}")
    rec = json.loads(rec_path.read_text())
    det = float(score["deterministic_score"])
    judge = float(score["judge_score"])
    weight = float(score.get("judge_weight", 0.3))
    if weight > 0.3:
        raise SystemExit("judge_weight exceeds the 0.3 cap (MVT/ATES intake)")
    penalty = float(score.get("wrong_commit_penalty", 0.0))
    metrics = rec.setdefault("metrics", {})
    metrics.update({
        "ates_outcome": score["ates_outcome"],
        "deterministic_score": det,
        "judge_score": judge,
        "judge_weight": weight,
        "net_score": round((1 - weight) * det + weight * judge - penalty, 4),
        "wrong_commit_penalty": penalty,
        "trace_id": score["trace_id"],
        "task_fingerprint": score["task_fingerprint"],
        "environment_fingerprint": score["environment_fingerprint"],
        "repetition": score.get("repetition", 1),
        "judge_provider": score["judge_provider"],
        "judge_model": score["judge_model"],
        "judge_dispatch_id": score["judge_dispatch_id"],
    })
    rec_path.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    return {"dispatch_id": dispatch_id, "emitted": True, "phase": "score_fill",
            "targets": [f"experiments/doe/{CAMPAIGN}/records/{safe}.json"]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stamp", required=True, help="Path to the canonical stamp JSON, or - for stdin")
    ap.add_argument("--root", default=".", help="Repo root (default: cwd)")
    ap.add_argument("--head-sha", default=None, help="Fallback baseline/candidate SHA (e.g. github.sha)")
    ap.add_argument("--phase", choices=["dispatch", "outcome", "score"], default="dispatch",
                    help="dispatch = full fan-out at completion; outcome = DoE outcome fill at PR close; score = MVT/ATES scoring keys at merge")
    args = ap.parse_args()
    raw = sys.stdin.read() if args.stamp == "-" else Path(args.stamp).read_text()
    parsed = json.loads(raw)
    if args.phase == "outcome":
        result = emit_outcome_fill(parsed, Path(args.root))
    elif args.phase == "score":
        result = emit_score_fill(parsed, Path(args.root))
    else:
        result = emit(parsed, Path(args.root), head_sha=args.head_sha)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
