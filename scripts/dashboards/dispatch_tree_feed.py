#!/usr/bin/env python3
"""Dispatch-tree cadence & admission feed — quota-dispatch-tree.yml.

Makes the dispatch tree's state visible outside per-run job summaries:

- per-lane cadence state for every lane in the tree's dispatch matrix:
  latest run, age, the firing rule that governs it (extracted verbatim
  from the workflow's decide step, never transcribed from prose), and
  whether the lane is past its staleness threshold ("due");
- Node A admission state: repo-wide queued + in-progress runs (`busy`)
  against the guard threshold, with the per-workflow breakdown that
  shows what `busy` actually counts;
- firing history: recent tree runs, the verdict each dispatch leg
  received (its 'Wake lane' step: success = woken, skipped = not), and
  whether the Supabase verdict-persistence step ran.

Reads only repository records plus the checked-in observation snapshot
(scripts/dashboards/dispatch_tree_observation.json, itself a stamped
firsthand API read — see dispatch_tree_observe.py). The collector never
calls the network. Refresh = re-run the observer, re-run this collector,
land by PR, exactly like the Oracle Panel and surface feeds.

Admission samples: the feed carries a `samples` series. Each refresh
appends the snapshot's busy reading (keyed by the snapshot's read_at)
to the series carried in the previous feed. History before the first
collection does not exist and is never backfilled.

Contract: docs/ops/DISPATCH-TREE-FEED.md
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "apps" / "help-wanted-dashboard" / "data"
TREE = ROOT / ".github" / "workflows" / "quota-dispatch-tree.yml"
SNAP = ROOT / "scripts" / "dashboards" / "dispatch_tree_observation.json"
SCHEMA = "dispatch-tree-feed/v1"

HONESTY = [
    "Firing rules are extracted from .github/workflows/quota-dispatch-tree.yml at collection time, never transcribed from prose.",
    "Run ages and busy counts are the observation snapshot's stamped read (read_at), not live claims at page-view time.",
    "The admission sample series starts at the first collection; earlier busy history does not exist and is never backfilled.",
    "A lane is 'due' only against a staleness threshold the workflow itself defines; phase-only lanes carry due=null.",
    "Verdicts are read from dispatch jobs' 'Wake lane' step conclusions (success = woken, skipped = not woken); the decide step's summary table is not exposed by the API and is not reconstructed.",
    "Supabase verdict persistence is reported as observed (repo variables present, persistence step conclusion); anon SELECT on dispatch_verdicts returns no rows under its insert-only RLS, so the table is not a read source for this feed.",
]

# decide-step outputs whose expression embeds a staleness threshold for a
# specific lane-age variable, and the lane-age variable -> workflow files
# whose age the tree actually measures (hw-pair takes the max of two).
STALE_VAR_FILES = {
    "hwRefreshStaleMin": ["help-wanted-status-refresh.yml"],
    "hwPairStaleMin": ["help-wanted-followup.yml", "help-wanted-scout.yml"],
    "hwExecuteStaleMin": ["help-wanted-execute.yml"],
    "hwAssistStaleMin": ["help-wanted-llm-assist.yml"],
    "paStaleMin": ["provider-availability.yml"],
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_ts(s: str | None) -> datetime | None:
    if not s:
        return None
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def parse_tree(text: str) -> dict:
    """Extract guard, decide outputs + rule expressions, and matrix lanes."""
    guard = re.search(r"const paused = busy >= (\d+)", text)
    threshold = int(guard.group(1)) if guard else None

    outputs: dict[str, str] = {}
    for m in re.finditer(r"core\.setOutput\('([a-z0-9_]+)',\s*(.+?)\);\s*$", text, re.M):
        outputs[m.group(1)] = m.group(2).strip()

    # matrix: lane -> the decide output that gates it
    lanes: list[dict] = []
    block = text.split("matrix:", 1)[-1]
    for m in re.finditer(
        r"- lane: (\S+)\s*\n\s+run: \$\{\{ needs\.decide\.outputs\.([a-z0-9_]+) \}\}", block
    ):
        lanes.append({"lane": m.group(1), "output": m.group(2)})

    # Lane-age staleness per output: only variables in STALE_VAR_FILES are
    # lane ages. bridgeStaleMin / probeStaleMin are *manifest* ages — a
    # different signal, recorded separately and never used for lane due.
    stale: dict[str, dict] = {}
    manifest: dict[str, dict] = {}
    for out, expr in outputs.items():
        m = re.search(r"(\w*StaleMin) > (\d+)", expr)
        if m and m.group(1) in STALE_VAR_FILES:
            stale[out] = {
                "variable": m.group(1),
                "threshold_min": int(m.group(2)),
                "measured_workflows": STALE_VAR_FILES[m.group(1)],
            }
        elif m:
            manifest[out] = {"variable": m.group(1), "threshold_min": int(m.group(2))}
        if "paStaleMin > paThresholdMin" in expr:
            stale[out] = {
                "variable": "paStaleMin",
                "threshold_min": None,  # derived per-read in build_feed
                "threshold_rule": "1.5x median gap between the lane's 5 most recent runs, clamped to [120, 720] min; fallback 360 with too little history (derived by the tree itself each run)",
                "measured_workflows": STALE_VAR_FILES["paStaleMin"],
            }
    return {
        "guard_threshold": threshold,
        "outputs": outputs,
        "lanes": lanes,
        "stale": stale,
        "manifest_stale": manifest,
    }


def lane_state(entry: dict, rule: dict, snap_lanes: dict, read_at: datetime) -> dict:
    lane = entry["lane"]
    runs = snap_lanes.get(lane, [])
    latest = runs[0] if runs else None
    age_min = None
    if latest and _parse_ts(latest["created_at"]):
        age_min = round((read_at - _parse_ts(latest["created_at"])).total_seconds() / 60, 1)
    stale = rule["stale"].get(entry["output"])
    due = None
    measured_age = None
    if stale is not None:
        # The tree measures specific workflows' ages (max, for hw-pair);
        # due is judged on that measured age, not this lane's own age.
        ages = []
        for wf in stale["measured_workflows"]:
            m_runs = snap_lanes.get(wf.removesuffix(".yml"), [])
            if m_runs and _parse_ts(m_runs[0]["created_at"]):
                ages.append(
                    round((read_at - _parse_ts(m_runs[0]["created_at"])).total_seconds() / 60, 1)
                )
        if ages:
            measured_age = max(ages)
            if stale["threshold_min"] is not None:
                due = measured_age > stale["threshold_min"]
    return {
        "lane": lane,
        "workflow_file": f"{lane}.yml",
        "output": entry["output"],
        "rule_expression": rule["outputs"].get(entry["output"]),
        "admission_gated": "!paused" in (rule["outputs"].get(entry["output"]) or ""),
        "staleness": stale,
        "manifest_staleness": rule.get("manifest_stale", {}).get(entry["output"]),
        "latest_run": latest,
        "age_min_at_read": age_min,
        "measured_age_min_at_read": measured_age,
        "due_at_read": due,
        "recent_runs": runs,
    }


def build_feed(prev_feed: dict | None = None) -> dict:
    text = TREE.read_text()
    rule = parse_tree(text)
    snap = json.loads(SNAP.read_text())
    read_at = _parse_ts(snap["read_at"])

    # Derive the q6 dynamic threshold exactly as the tree does, from the
    # provider-availability run gaps in the snapshot.
    for out, st in rule["stale"].items():
        if st["variable"] == "paStaleMin" and st["threshold_min"] is None:
            runs = snap.get("lanes", {}).get("provider-availability", [])
            times = [_parse_ts(r["created_at"]) for r in runs if _parse_ts(r["created_at"])]
            gaps = [
                (times[i] - times[i + 1]).total_seconds() / 60
                for i in range(len(times) - 1)
            ]
            if len(gaps) >= 2:
                gaps.sort()
                med = gaps[len(gaps) // 2]
                st["threshold_min"] = int(min(720, max(120, round(1.5 * med))))
            else:
                st["threshold_min"] = 360
            st["threshold_derived_from"] = f"median of {len(gaps)} gaps in snapshot"

    lanes = [lane_state(e, rule, snap.get("lanes", {}), read_at) for e in rule["lanes"]]
    lane_names = {e["lane"] for e in rule["lanes"]}

    busy = snap.get("busy", {})
    by_wf = busy.get("by_workflow", {})
    sample = {
        "read_at": snap["read_at"],
        "queued": busy.get("queued"),
        "in_progress": busy.get("in_progress"),
        "busy": busy.get("total"),
        "guard_threshold": rule["guard_threshold"],
        "guard_would_pause": (busy.get("total") or 0) >= (rule["guard_threshold"] or 0),
    }
    samples = []
    if prev_feed:
        samples = list(prev_feed.get("data", {}).get("admission", {}).get("samples", []))
    if not samples or samples[-1].get("read_at") != sample["read_at"]:
        samples.append(sample)
    samples = samples[-500:]

    tree_runs = []
    for r in snap.get("tree_runs", []):
        jobs = snap.get("tree_jobs", {}).get(str(r["id"]), [])
        woken, not_woken, supabase_step = [], [], None
        for j in jobs:
            if j.get("supabase_step") is not None:
                supabase_step = j["supabase_step"]
            m = re.match(r"dispatch \(([^,]+),", j.get("name") or "")
            if m and j.get("wake") is not None:
                (woken if j["wake"] == "success" else not_woken).append(m.group(1))
        tree_runs.append(
            {
                **r,
                "jobs_observed": len(jobs) > 0,
                "woken_lanes": sorted(woken),
                "not_woken_lanes": sorted(not_woken),
                "supabase_step_conclusion": supabase_step,
            }
        )

    var_names = snap.get("repo_variable_names", [])
    return {
        "schema": SCHEMA,
        "surface": "dispatch-tree",
        "generated_at": _now(),
        "sources": [
            ".github/workflows/quota-dispatch-tree.yml (rules + matrix, parsed at collection time)",
            "scripts/dashboards/dispatch_tree_observation.json (stamped Actions API read)",
            "docs/ops/GAP-LEDGER.md G-02 + PRs #1759/#1815 (recorded fix evidence)",
        ],
        "honesty_rules": HONESTY,
        "data": {
            "admission": {
                "node": "A",
                "guard_threshold": rule["guard_threshold"],
                "guard_expression": "paused = busy >= threshold && !force",
                "comment_says": "when too many lane runs are already live",
                "code_counts": "ALL repo workflow runs with status queued or in_progress (listWorkflowRunsForRepo, no workflow filter) — dominated in practice by PR check fan-outs, not tree lanes",
                "now": sample,
                "by_workflow_at_read": by_wf,
                "samples": samples,
                "samples_note": "Series begins at first collection (see samples[0].read_at). No earlier busy history exists in any record this collector can read; none is backfilled.",
            },
            "lanes": lanes,
            "lane_count": len(lanes),
            "tree_runs": tree_runs,
            "supabase_verdicts": {
                "step": "Persist verdicts to Supabase lane-state (optional)",
                "table": "dispatch_verdicts",
                "repo_variables_present": {
                    "SUPABASE_URL": "SUPABASE_URL" in var_names,
                    "SUPABASE_ANON_KEY": "SUPABASE_ANON_KEY" in var_names,
                },
                "endpoint_reachable": True,
                "anon_select_visible_rows": 0,
                "note": "Checked firsthand at first collection: the REST endpoint answers and anon SELECT returns [] — consistent with the workflow's own comment (anon INSERT only, RLS-gated). The step's per-run conclusion is carried on each tree run above; row contents are not readable with the anon key and are not used as a feed source.",
            },
        },
        "gaps": [
            {
                "id": "busy-history-starts-at-first-collection",
                "detail": "No record holds repo-wide busy counts before the first observation snapshot; the sample series is append-only from that point.",
            },
            {
                "id": "decide-summary-not-api-visible",
                "detail": "The decide step's 'Decision tree verdicts' summary table is not exposed by the Actions API; this feed carries the equivalent evidence from dispatch jobs' Wake lane step conclusions.",
            },
            {
                "id": "supabase-rows-not-readable-anon",
                "detail": "dispatch_verdicts rows cannot be read back with the anon key (insert-only RLS); persistence is evidenced by the step conclusion, not row contents.",
            },
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DATA / "dispatch-tree-feed.json"))
    args = ap.parse_args()
    out = Path(args.out)
    prev = None
    if out.exists():
        try:
            prev = json.loads(out.read_text())
        except Exception:
            prev = None
    feed = build_feed(prev)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(feed, indent=1) + "\n")
    adm = feed["data"]["admission"]["now"]
    due = [l["lane"] for l in feed["data"]["lanes"] if l["due_at_read"]]
    print(
        f"wrote {out}: lanes={feed['data']['lane_count']} busy={adm['busy']} "
        f"guard>={adm['guard_threshold']} due={due}"
    )


if __name__ == "__main__":
    main()
