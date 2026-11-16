#!/usr/bin/env python3
"""Self-count layer (owner ruling 2026-11-03: "We count ourselves
for nulls && derive heuristics over time. When they fail by our
#'s."). Tallies the fleet's OWN recorded events from committed
sources - never provider readings, never estimates:

- dispatches per provider: experiments/doe/routed-dispatch
  {records,stamps} (deduped by dispatch_id, same semantics as
  scripts/quota_usage_series.py) + ops/tracking/nested-family.json
  task carriers;
- rate-limit wall events per bucket: ops/quota/rate-limit-events.json;
- Actions volume: the actions-performance-reconstructed corpus
  (latest file = cumulative runs/jobs the fleet itself executed);
- stamped usage rows per provider: ops/challenge/desk-feed.json
  traversals (activity-proxy class, as labeled there).

Output: ops/quota/self-counts.json (quota-self-counts/v1). Every
count is stamped method="self-count" with its sources. The planner
(scripts/quota_allocation_planner.py) consumes this file to compute
matching where provider readings are null; heuristics live in the
planner's labeled matching layer, ABOVE these counts.

Coverage honesty: a surface the tally cannot see is NAMED in
coverage_notes, never silently zero. Known blind spots at first
issue: the PAT helper's spend log is VM-local (not committed), and
provider-side token/$ consumption is visible only where a dispatch
was stamped.

Usage: python3 scripts/quota_self_counts.py [--root .]
stdlib only.
"""
import argparse
import glob as globmod
import json
import re
from datetime import datetime, timezone
from pathlib import Path

OUT_REL = "ops/quota/self-counts.json"


def load(root, rel):
    p = Path(root) / rel
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError):
        return None


def fam_slug(provider):
    tok = re.split(r"[\s(]", str(provider).strip().lower())[0]
    return tok or "unknown"


def tally_dispatches(root):
    """dispatch_id-deduped dispatch counts per provider slug."""
    seen, per = {}, {}
    for sub in ("records", "stamps"):
        for f in sorted(globmod.glob(
                str(Path(root) / "experiments/doe/routed-dispatch"
                    / sub / "*.json"))):
            try:
                rec = json.loads(Path(f).read_text())
            except (OSError, ValueError):
                continue
            prov, ts = rec.get("provider"), rec.get("ts")
            if not prov or str(prov).lower() == "github-actions":
                continue
            key = rec.get("dispatch_id") or (
                str(prov) + "|" + str(rec.get("model")) + "|" + str(ts))
            if key in seen:
                continue
            seen[key] = (prov, ts)
    nested = load(root, "ops/tracking/nested-family.json") or {}
    for prov in nested.get("providers", []):
        for mod in prov.get("models", []):
            for t in mod.get("tasks", []):
                pname, ts = prov.get("provider"), t.get("ts")
                if not pname or str(pname).lower() == "github-actions":
                    continue
                key = t.get("dispatch_id") or (
                    str(pname) + "|" + str(mod.get("model")) + "|"
                    + str(ts))
                if key in seen:
                    continue
                seen[key] = (pname, ts)
    for prov, ts in seen.values():
        slot = per.setdefault(fam_slug(prov),
                              {"provider": prov, "dispatches": 0,
                               "first_at": ts, "last_at": ts})
        slot["dispatches"] += 1
        if ts:
            if not slot["first_at"] or ts < slot["first_at"]:
                slot["first_at"] = ts
            if not slot["last_at"] or ts > slot["last_at"]:
                slot["last_at"] = ts
    return per


def tally_walls(root):
    doc = load(root, "ops/quota/rate-limit-events.json") or {}
    per = {}
    for e in doc.get("events", []):
        slot = per.setdefault(e.get("bucket", "unknown"),
                              {"wall_events": 0, "by_class": {},
                               "last_at": None})
        slot["wall_events"] += 1
        cls = e.get("class") or "unknown"
        slot["by_class"][cls] = slot["by_class"].get(cls, 0) + 1
        if e.get("at") and (not slot["last_at"]
                            or e["at"] > slot["last_at"]):
            slot["last_at"] = e["at"]
    return per


def tally_actions(root):
    files = sorted(globmod.glob(
        str(Path(root) / "docs/ops/generated"
            / "actions-performance-reconstructed-*.json")))
    if not files:
        return None
    latest = json.loads(Path(files[-1]).read_text())
    m = re.search(r"(\d{4}-\d{2}-\d{2})\.json$", files[-1])
    return {"runs_total": latest.get("run_count"),
            "jobs_total": latest.get("total_jobs"),
            "corpus_files": len(files),
            "latest_corpus_date": m.group(1) if m else None,
            "source": "docs/ops/generated/"
                      "actions-performance-reconstructed-*.json"}


def tally_desk_usage(root):
    desk = load(root, "ops/challenge/desk-feed.json") or {}
    per = {}
    for trav in desk.get("traversals", []):
        for row in trav.get("provider_usage", []):
            if not row.get("provider"):
                continue
            slot = per.setdefault(fam_slug(row["provider"]),
                                  {"provider": row["provider"],
                                   "usage_stamps": 0})
            slot["usage_stamps"] += 1
    return per


def build(root):
    dispatches = tally_dispatches(root)
    desk = tally_desk_usage(root)
    for slug, d in desk.items():
        slot = dispatches.setdefault(
            slug, {"provider": d["provider"], "dispatches": 0,
                   "first_at": None, "last_at": None})
        slot["usage_stamps"] = d["usage_stamps"]
    return {
        "schema": "quota-self-counts/v1",
        "generated_by": "scripts/quota_self_counts.py",
        "generated_at": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "method": "self-count: tallies of the fleet's own recorded "
                  "events from committed sources (owner ruling "
                  "2026-11-03). Not provider readings; not "
                  "estimates. Provider readings govern where "
                  "present; these counts govern where readings "
                  "are null.",
        "providers": dispatches,
        "buckets": tally_walls(root),
        "services": {"github.actions": tally_actions(root)},
        "coverage_notes": [
            "PAT helper spend logs (spend.jsonl beside the helper) "
            "are VM-local and not committed - PAT call volume is "
            "NOT tallied here; its wall events are (rate-limit "
            "register). Export of the spend log is the follow-up "
            "that closes this blind spot.",
            "Provider-side token/$ consumption is visible only "
            "where a dispatch was stamped (routed-dispatch + "
            "nested-family carriers); unstamped consumption is "
            "not counted and not estimated.",
            "Dispatch counts are per provider (dispatch records "
            "name provider+model, not registry service id); the "
            "planner rolls them up to pools by provider.",
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    doc = build(a.root)
    out = Path(a.root) / OUT_REL
    out.write_text(json.dumps(doc, indent=1) + "\n")
    print("self-counts:", doc["generated_at"],
          "| providers:", len(doc["providers"]),
          "| dispatches:", sum(p["dispatches"]
                               for p in doc["providers"].values()),
          "| buckets:", len(doc["buckets"]))


if __name__ == "__main__":
    main()
