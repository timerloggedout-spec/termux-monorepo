#!/usr/bin/env python3
"""live-3-phrases-deepseek dispatcher automation (rule 5, WO-A).

Route of record (doe-expert ruling (a), 2026-10-31): PRIMARY
OpenRouter deepseek/deepseek-r1:free is DEAD (model delisted +
account paid-incapable); the ALT deepseek-ci comment surface is
authorized. plan/record are route-agnostic; the workflow's send
leg posts the composed prompt as the dispatch comment. The route
model string comes from DESIGN automation.model when set.

Replaces manual per-job dispatch with repo automation:

  plan   — screen the target PR against the A3 / cb-1 exclusions
           (in code), enforce the daily OpenRouter free-tier budget,
           assign the Stage-1 cell by the campaign rule
           sha256(f"{pr}:{salt}") mod len(active_cells), compose the
           prompt through scripts/doe/phrase_layer.py, stamp the
           configured instance, and write the dispatch job file
           (schema doe-phrase-dispatch/v1 — the same shape the
           existing doe-phrase-dispatch workflow sends).
  record — fold a dispatch result (from scripts/doe/phrase_dispatch
           .py) into an EXPERIMENT-conforming campaign record +
           regenerate the campaign SUMMARY.json; consumes one budget
           unit (a sent call costs quota whatever its outcome).

Active cells are the ESTABLISHED Stage-1 set only: fixed-anchor
selection, placement {prefix, suffix, both} x form {verbatim,
vowels}, plus the unphrased control. leet-full cells are BLOCKED
(Linguist C2-v) and can never be produced here — asserted in code.

Exits: 0 ok · 4 target excluded (A3/cb-1) · 5 daily budget exhausted.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import instance_key as ik  # noqa: E402
import phrase_layer  # noqa: E402

CAMPAIGN = "live-3-phrases-deepseek"
MODEL = "deepseek/deepseek-r1:free"
SALT = "live-3-phrases-deepseek"
ACTIVE_CELLS = ["control", "prefix-verbatim", "prefix-vowels",
                "suffix-verbatim", "suffix-vowels",
                "both-verbatim", "both-vowels"]
CELL_CFG = {
    "control": None,
    "prefix-verbatim": {"placement": "prefix", "form": "verbatim"},
    "prefix-vowels": {"placement": "prefix", "form": "vowels"},
    "suffix-verbatim": {"placement": "suffix", "form": "verbatim"},
    "suffix-vowels": {"placement": "suffix", "form": "vowels"},
    "both-verbatim": {"placement": "prefix+suffix",
                      "form": "verbatim"},
    "both-vowels": {"placement": "prefix+suffix", "form": "vowels"},
}
DEFAULT_DAILY_CAP = 8  # Pool-1 free tier = 50 calls/day account-wide


def excluded_prs(live1_records: Path, cb1_records: Path,
                 design: dict) -> set[int]:
    """A3 + cb-1 exclusion set, derived in code from the sibling
    campaigns' records plus any DESIGN-declared extras."""
    out: set[int] = set()
    for d in (live1_records, cb1_records):
        if d and d.exists():
            for p in d.glob("*.json"):
                try:
                    rec = json.loads(p.read_text())
                except Exception:
                    continue
                m = rec.get("metrics") or {}
                for key in ("pr", "target_pr"):
                    if isinstance(m.get(key), int):
                        out.add(m[key])
    auto = design.get("automation") or {}
    out |= {int(x) for x in auto.get("extra_excluded_prs", [])}
    return out


def assign_cell(pr: int) -> tuple[int, str]:
    idx = int(hashlib.sha256(f"{pr}:{SALT}".encode()).hexdigest(),
              16) % len(ACTIVE_CELLS)
    return idx, ACTIVE_CELLS[idx]


def compose(task_text: str, cell: str, phrases_data: dict,
            model: str = MODEL):
    cfg = CELL_CFG[cell]
    if cfg is None:
        return task_text, None, {"placement": None, "form": None,
                                 "transform": None}
    transform = {"casing": "as-written",
                 "sub_scope": "vowels" if cfg["form"] == "vowels"
                 else "none",
                 "sub_depth": 0}
    composed, stamp = phrase_layer.apply_phrases(
        task_text, phrases_data, model, selection="first",
        placement=cfg["placement"], form="verbatim",
        transform_cfg=transform)
    if stamp is None:
        raise RuntimeError(f"no phrase set established for {model}")
    return composed, stamp, {"placement": cfg["placement"],
                             "form": cfg["form"],
                             "transform": transform}


def load_state(path: Path, today: str) -> dict:
    if path.exists():
        st = json.loads(path.read_text())
        if st.get("date") != today:
            st = {"date": today, "calls": 0,
                  "next_no": st.get("next_no", 1)}
        return st
    return {"date": today, "calls": 0, "next_no": 1}


def cmd_plan(args) -> int:
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    design = json.loads(Path(args.design).read_text())
    cap = int((design.get("automation") or {}).get(
        "daily_call_cap", DEFAULT_DAILY_CAP))
    excluded = excluded_prs(Path(args.live1_records),
                            Path(args.cb1_records), design)
    if args.pr in excluded:
        print(f"EXCLUDED: PR {args.pr} is live-1-designed or cb-1 "
              f"(A3/cb-1 exclusion)")
        return 4
    state_path = Path(args.state)
    state = load_state(state_path, today)
    if state["calls"] >= cap:
        print(f"BUDGET: {state['calls']}/{cap} free calls used today "
              f"({today}); refusing plan")
        return 5
    model = (design.get("automation") or {}).get("model", MODEL)
    phrases = phrase_layer.load_sets(args.phrases)
    task_text = Path(args.task_file).read_text()
    idx, cell = assign_cell(args.pr)
    composed, stamp, cfg = compose(task_text, cell, phrases, model)
    prompt_sha = ik.sha256_text(composed)
    key = ik.instance_key(
        provider="openrouter", model=model,
        system_prompt_sha256=prompt_sha,
        tools_sha256_=ik.tools_sha256([]),
        role="reviewer", moniker="doe-mgr-phrases-jit",
        context=f"{CAMPAIGN}/{cell}")
    no = state["next_no"]
    job = {
        "schema": "doe-phrase-dispatch/v1",
        "campaign_id": CAMPAIGN,
        "dispatch_no": no,
        "route": "openrouter",
        "model": model,
        "role": "reviewer",
        "task": {"type": "pr_review", "pr": args.pr,
                 "pr_head": args.pr_head,
                 "screening": {
                     "live1_designed": False, "cb1": False,
                     "basis": "dispatcher code screen vs live-1 + "
                              "cb-1 campaign records + DESIGN "
                              "automation.extra_excluded_prs "
                              "(WO-A automation)"}},
        "assignment": {"rule": "sha256(f'{pr}:{salt}') mod "
                               "len(active_cells)",
                       "salt": SALT, "active_cells": ACTIVE_CELLS,
                       "index": idx, "cell": cell, "stage": 1,
                       "selection": "fixed-anchor"},
        "cell_cfg": cfg,
        "phrases_stamp": stamp,
        "prompt_sha256": prompt_sha,
        "instance_key": key,
        "prompt": composed,
    }
    job_path = Path(args.dispatch_dir) / \
        f"job-{no:04d}-pr{args.pr}.json"
    job_path.parent.mkdir(parents=True, exist_ok=True)
    job_path.write_text(json.dumps(job, indent=1))
    state["next_no"] = no + 1
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=1))
    print(f"planned dispatch {no}: PR {args.pr} cell={cell} "
          f"job={job_path}")
    return 0


def cmd_record(args) -> int:
    job = json.loads(Path(args.job).read_text())
    result = json.loads(Path(args.result).read_text())
    ok = result.get("status") == "ok"
    cell = (job.get("assignment") or {}).get("cell")
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    state_path = Path(args.state)
    state = load_state(state_path, today)
    state["calls"] += 1
    state_path.write_text(json.dumps(state, indent=1))
    record = {
        "schema_version": "1.0",
        "experiment_id": f"live3-dispatch-{job['dispatch_no']}",
        "suite": f"doe-family:{CAMPAIGN}",
        "observed_at": result.get("finished_at")
        or dt.datetime.now(dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "baseline_sha": (job.get("task") or {}).get("pr_head")
        or args.base_sha,
        "candidate_sha": (job.get("task") or {}).get("pr_head")
        or args.base_sha,
        "treatment": {
            "manager_policy_id":
                "doe-mgr-phrases-jit/live-3-dispatcher/v1",
            "provider": "openrouter",
            "model": job.get("model", MODEL),
            "arm": cell,
            "instance": {
                "provider": "openrouter",
                "model": job.get("model", MODEL),
                "system_prompt": {
                    "ref": f"experiments/doe/{CAMPAIGN}/dispatch/"
                           f"job-{job['dispatch_no']:04d}-pr"
                           f"{(job.get('task') or {}).get('pr')}.json",
                    "sha256": job.get("prompt_sha256")},
                "tools": {"ref": "tools:openrouter:chat-completions",
                          "sha256": ik.tools_sha256([])},
                "role": "reviewer",
                "moniker": "doe-mgr-phrases-jit",
                "context": f"{CAMPAIGN}/{cell}",
                "instance_key": job.get("instance_key")}},
        "provenance": "github",
        "confidence": "high",
        "status": "passed" if ok else "failed",
        "outcome": "dispatched_ok" if ok else
        f"dispatch_error: {str(result.get('error'))[:120]}",
        "metrics": {
            "pr": (job.get("task") or {}).get("pr"),
            "dispatch_no": job["dispatch_no"],
            "cell": cell,
            "instance_key": job.get("instance_key"),
            "prompt_sha256_12": (job.get("prompt_sha256")
                                 or "")[:12] or None,
            "response_sha256_12": (result.get("response_sha256")
                                   or "")[:12] or None,
            "response_chars": result.get("response_chars"),
            "route_surface": result.get("via") or "openrouter",
            "findings_actioned": None,
        },
        "evidence_refs": [
            f"experiments/doe/{CAMPAIGN}/dispatch/"
            f"job-{job['dispatch_no']:04d}-pr"
            f"{(job.get('task') or {}).get('pr')}.json",
            "workflow artifact doe-phrase-result (dispatch result)"],
    }
    # EXPERIMENT schema rev 1.1 slots (PR #2895, first consumer):
    # usage is carried only with its measurement status; window and
    # session_id appear only when both endpoints are known.
    usage = result.get("usage") or {}
    total = usage.get("total_tokens")
    if isinstance(total, (int, float)) and not isinstance(total,
                                                          bool):
        record["usage"] = {"value": total, "unit": "tokens",
                            "source": "openrouter/usage",
                            "match": "exact", "status": "measured"}
    elif ok:
        record["usage"] = {"value": None, "unit": None,
                            "source": result.get("via")
                            or "openrouter",
                            "match": None,
                            "status": "activity_only"}
    else:
        record["usage"] = {"value": None, "unit": None,
                            "source": None, "match": None,
                            "status": "not_established"}
    if job.get("stamped_at") and result.get("finished_at"):
        record["window"] = {"start": job["stamped_at"],
                            "end": result["finished_at"]}
    if result.get("session_id"):
        record["session_id"] = result["session_id"]
    records = Path(args.records_dir)
    records.mkdir(parents=True, exist_ok=True)
    (records / f"dispatch-{job['dispatch_no']:04d}.json").write_text(
        json.dumps(record, indent=1))
    summary = {"campaign_id": CAMPAIGN,
               "generated_from": "records/ (live3_dispatcher record)",
               "runs": 0, "cells": {}, "statuses": {}}
    for p in sorted(records.glob("*.json")):
        r = json.loads(p.read_text())
        if r.get("schema_version") != "1.0" or not str(
                r.get("experiment_id", "")).startswith(
                "live3-dispatch-"):
            continue  # foreign record shapes are not ours to count
        summary["runs"] += 1
        c = (r.get("metrics") or {}).get("cell")
        summary["cells"][c] = summary["cells"].get(c, 0) + 1
        s = r.get("status")
        summary["statuses"][s] = summary["statuses"].get(s, 0) + 1
    Path(args.summary).write_text(json.dumps(summary, indent=1))
    print(f"recorded dispatch {job['dispatch_no']}: "
          f"status={record['status']} budget {state['calls']} used "
          f"today")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--pr", type=int, required=True)
    p.add_argument("--pr-head")
    p.add_argument("--task-file", required=True)
    p.add_argument("--design", required=True)
    p.add_argument("--phrases", required=True)
    p.add_argument("--live1-records", required=True)
    p.add_argument("--cb1-records", required=True)
    p.add_argument("--dispatch-dir", required=True)
    p.add_argument("--state", required=True)
    p.set_defaults(fn=cmd_plan)
    r = sub.add_parser("record")
    r.add_argument("--job", required=True)
    r.add_argument("--result", required=True)
    r.add_argument("--records-dir", required=True)
    r.add_argument("--summary", required=True)
    r.add_argument("--state", required=True)
    r.add_argument("--base-sha", required=True)
    r.set_defaults(fn=cmd_record)
    args = ap.parse_args()
    assert all("leet" not in c for c in ACTIVE_CELLS), \
        "leet-full must never be an active cell"
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
