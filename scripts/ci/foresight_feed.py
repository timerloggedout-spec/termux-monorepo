#!/usr/bin/env python3
"""foresight_feed.py — repo-side adaptive variant of
workspace/llm_map/foresight_collect.py (Forge ForeSight).

Original: aggregates device-home stores (termux-multi-agent run_history,
cli-synthegration sprints, FORGE_OVERSIGHT.md, BatchResumer module) into
foresight_state.json with readiness/impact scores. Universe-bound and its
parameters are not portable (staged = staging-path heuristic; score =
50 + 10/pass − 15/fail over device run verdicts).

This variant keeps the concept — one aggregated state feed with readiness,
impact and bottleneck views — over repo inputs only, with the scoring
re-derived and disclosed here:

  inputs (all optional; absence is reported, never invented):
    workspace/llm_map/llm_index_compact.jsonl   (archwiz-repo-index output)
    workspace/llm_map/func_index.jsonl          (archwiz-func-index output)
    scripts/ci/dangle_baseline.json             (known dangling refs)
    ops/challenge/desk-feed.json                (dispatch stamps)
    ops/tracking/*.json                         (coordinator-class feeds)

  readiness(file) in [0,100], deterministic:
    50 base
    +10  indexed and last-touched within 30 days of HEAD commit time
    +min(20, 2 * by)     dependent scrutiny signal from the compact index
    −15  file is the source or target of a known dangling reference
    (no run-verdict term: the repo universe has no per-file PASS/FAIL log;
     Actions verdicts are per-workflow, not per-file — inventing a mapping
     would be a false precision. Revisit if a per-file verdict feed lands.)

  impact(file) = direct + transitive dependents, BFS ≤ 3 hops over the
    compact index dep graph (same definition as the original).

  bottlenecks = feed entries (any input feed) whose status reads blocked,
    with the feed's own blocker text when present.

Output: apps/help-wanted-dashboard/data/foresight_state.json.
generated_at = HEAD commit time (deterministic; no wall clock).
Stdlib only.
"""
import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


def head_time(root):
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "log", "-1", "--format=%cI"],
            capture_output=True, text=True, check=True).stdout.strip()
        return datetime.fromisoformat(out.replace("Z", "+00:00"))
    except Exception:
        return None


def load_jsonl(p):
    if not p.exists():
        return []
    out = []
    for line in p.read_text(errors="replace").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def load_json(p):
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(errors="replace"))
    except ValueError:
        return None


def find_blocked(obj, feed_name, out, path=""):
    if isinstance(obj, dict):
        status = str(obj.get("status", "")).lower()
        if status in ("blocked", "blocker"):
            out.append({"feed": feed_name, "path": path,
                        "id": obj.get("id") or obj.get("name") or "",
                        "blocker": obj.get("blocker", "")})
        for k, v in obj.items():
            find_blocked(v, feed_name, out, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_blocked(v, feed_name, out, f"{path}[{i}]")


def build(root):
    notes = []
    compact = load_jsonl(root / "workspace/llm_map/llm_index_compact.jsonl")
    if not compact:
        notes.append("llm_index_compact.jsonl absent/empty — readiness/impact empty")
    funcs = load_jsonl(root / "workspace/llm_map/func_index.jsonl")
    func_files = {f.get("file") for f in funcs}

    dangle_paths = set()
    base = load_json(root / "scripts/ci/dangle_baseline.json")
    if base:
        for f in base.get("findings", []):
            dangle_paths.add(f.get("path", ""))
            dangle_paths.add(f.get("ref", ""))
    else:
        notes.append("dangle_baseline.json absent — no dangle penalty applied")

    now = head_time(root)
    entries = {e["p"]: e for e in compact if e.get("p")}
    graph = {p: e.get("d", []) for p, e in entries.items()}
    reverse = defaultdict(set)
    for src, ds in graph.items():
        for d in ds:
            reverse[d].add(src)

    def impact(p):
        visited, queue, count = set(), [(p, 0)], 0
        while queue:
            cur, depth = queue.pop(0)
            if cur in visited or depth > 3:
                continue
            visited.add(cur)
            if cur != p:
                count += 1
            for nxt in reverse.get(cur, []):
                if nxt not in visited:
                    queue.append((nxt, depth + 1))
        return count

    readiness, impacts = {}, {}
    for p, e in entries.items():
        score = 50
        ts = e.get("ts", "")
        if now and ts:
            try:
                t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if now - t <= timedelta(days=30):
                    score += 10
            except ValueError:
                pass
        score += min(20, 2 * int(e.get("by", 0)))
        if p in dangle_paths:
            score -= 15
        readiness[p] = max(0, min(100, score))
        impacts[p] = impact(p)

    bottlenecks = []
    feeds_read = []
    for feed in (root / "ops/challenge/desk-feed.json",):
        data = load_json(feed)
        if data is not None:
            feeds_read.append(str(feed.relative_to(root)))
            find_blocked(data, feeds_read[-1], bottlenecks)
    track_dir = root / "ops/tracking"
    if track_dir.exists():
        for feed in sorted(track_dir.glob("*.json")):
            data = load_json(feed)
            if data is not None:
                feeds_read.append(str(feed.relative_to(root)))
                find_blocked(data, feeds_read[-1], bottlenecks)

    ripe = sorted((p for p, s in readiness.items() if s >= 80),
                  key=lambda p: -impacts[p])
    return {
        "schema": "foresight-state/v1-repo",
        "generated_at": now.isoformat() if now else "",
        "inputs": {"compact_entries": len(entries),
                   "func_index_files": len(func_files),
                   "feeds_read": feeds_read},
        "readiness_top": sorted(readiness.items(), key=lambda kv: -kv[1])[:25],
        "ripe_files": ripe[:25],
        "impact_top": sorted(impacts.items(), key=lambda kv: -kv[1])[:25],
        "bottlenecks": bottlenecks,
        "notes": notes,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="apps/help-wanted-dashboard/data/foresight_state.json")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    state = build(root)
    if not args.no_write:
        out = root / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
    print(f"foresight: {state['inputs']['compact_entries']} entries, "
          f"{len(state['ripe_files'])} ripe, "
          f"{len(state['bottlenecks'])} bottlenecks, "
          f"{len(state['notes'])} notes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
