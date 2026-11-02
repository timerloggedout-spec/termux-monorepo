#!/usr/bin/env python3
"""Nested-family record — provider > model > {roles, tasks run}, with
dispatch connection (owner standard 2026-11-01; spec:
docs/ops/NESTED-FAMILY.md, schema nested-family/v1).

Population = existing dispatch records only, no new instrumentation:
  1. stamps     experiments/doe/routed-dispatch/stamps/*.json (canonical)
  2. intake     ops/3l0/intake.jsonl (3l0-intake/v1 fan-out copy)
  3. desk-usage ops/challenge/desk-feed.json traversals[].provider_usage[]
A dispatch counts once, under the highest-priority source carrying it
(dedupe: dispatch_id, else session_id). Identity fields are verbatim;
NOT_ESTABLISHED stays literal; outcomes are the stamps' own (this
substrate never scores). Single-writer: repo-tracking-collect.yml.
Outputs: ops/tracking/nested-family.json +
apps/help-wanted-dashboard/data/nested-family-feed.json (byte-identical).
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "nested-family/v1"
NOT_ESTABLISHED = "NOT_ESTABLISHED"


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _outcome(raw) -> dict:
    if isinstance(raw, dict):
        return {"status": raw.get("status"), "gate_call": raw.get("gate_call"),
                "confirmed": raw.get("confirmed")}
    if isinstance(raw, str):
        return {"status": raw, "gate_call": None, "confirmed": None}
    return {"status": None, "gate_call": None, "confirmed": None}


def _task_from_stamp(rec: dict, source: str, source_ref: str) -> dict:
    run = rec.get("run") if isinstance(rec.get("run"), dict) else {}
    inst = rec.get("instance") if isinstance(rec.get("instance"), dict) else {}
    return {
        "task_class": rec.get("task_class") or rec.get("suite"),
        "role": rec.get("role"),
        "moniker": rec.get("moniker"),
        "context": rec.get("context"),
        "dispatch_id": rec.get("dispatch_id"),
        "run_id": run.get("run_id"),
        "workflow": run.get("workflow"),
        "session_id": run.get("session_id"),
        "ts": rec.get("ts"),
        "outcome": _outcome(rec.get("outcome")),
        "instance_key": inst.get("instance_key"),
        "source": source,
        "source_ref": source_ref,
    }


def _task_from_desk(row: dict, entry: str) -> dict:
    return {
        "task_class": "desk-traversal",
        "role": row.get("role"),
        "moniker": row.get("moniker"),
        "context": row.get("context") or f"desk traversal {entry}",
        "dispatch_id": None,
        "run_id": None,
        "workflow": None,
        "session_id": row.get("session_id"),
        "ts": None,
        "outcome": _outcome(row.get("state")),
        "instance_key": row.get("instance_key"),
        "source": "desk-usage",
        "source_ref": f"ops/challenge/desk-feed.json#traversals[{entry}].provider_usage",
    }


def collect_tasks(base: Path):
    """Returns (tasks, sources_meta, gaps). Each task gains _provider/_model
    (verbatim grouping keys) consumed by build() and stripped on emit."""
    tasks: list[dict] = []
    seen: set[str] = set()
    meta: list[dict] = []
    gaps: list[str] = []

    def admit(task, provider, model) -> bool:
        key = task.get("dispatch_id") or (f"session:{task['session_id']}" if task.get("session_id") else None)
        if key is None or key in seen:
            return False
        seen.add(key)
        task["_provider"] = provider
        task["_model"] = model
        tasks.append(task)
        return True

    # 1. canonical stamps
    sdir = base / "experiments" / "doe" / "routed-dispatch" / "stamps"
    files = sorted(sdir.glob("*.json")) if sdir.exists() else []
    used = 0
    for p in files:
        rec = _read_json(p)
        if not isinstance(rec, dict) or not rec.get("provider"):
            continue
        if admit(_task_from_stamp(rec, "stamps", f"experiments/doe/routed-dispatch/stamps/{p.name}"),
                 rec.get("provider"), rec.get("model") or NOT_ESTABLISHED):
            used += 1
    meta.append({"id": "stamps", "path": "experiments/doe/routed-dispatch/stamps/*.json",
                 "records_read": len(files), "records_used": used})
    if not files:
        gaps.append("stamps source empty: experiments/doe/routed-dispatch/stamps has no files")

    # 2. 3l0 intake fan-out
    ipath = base / "ops" / "3l0" / "intake.jsonl"
    rows = []
    if ipath.exists():
        for line in ipath.read_text().splitlines():
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except Exception:
                    continue
    used = 0
    for rec in rows:
        if not isinstance(rec, dict) or not rec.get("provider"):
            continue
        if admit(_task_from_stamp(rec, "intake", f"ops/3l0/intake.jsonl#{rec.get('dispatch_id')}"),
                 rec.get("provider"), rec.get("model") or NOT_ESTABLISHED):
            used += 1
    meta.append({"id": "intake", "path": "ops/3l0/intake.jsonl",
                 "records_read": len(rows), "records_used": used})

    # 3. desk provider_usage carrier
    desk = _read_json(base / "ops" / "challenge" / "desk-feed.json") or {}
    read = used = 0
    for tr in desk.get("traversals", []):
        for row in tr.get("provider_usage", []) or []:
            read += 1
            if not row.get("provider"):
                continue
            if admit(_task_from_desk(row, tr.get("entry", "?")),
                     row.get("provider"), row.get("model") or NOT_ESTABLISHED):
                used += 1
    meta.append({"id": "desk-usage", "path": "ops/challenge/desk-feed.json#traversals[].provider_usage",
                 "records_read": read, "records_used": used})
    return tasks, meta, gaps


def build(base=None, now=None) -> dict:
    base = base or ROOT
    now = now or datetime.now(timezone.utc)
    tasks, meta, gaps = collect_tasks(base)

    fam: dict[str, dict[str, list]] = {}
    for t in tasks:
        fam.setdefault(t["_provider"], {}).setdefault(t["_model"], []).append(t)

    providers = []
    n_models = n_tasks = 0
    roles_all: set[str] = set()
    by_outcome: dict[str, int] = {}
    by_source: dict[str, int] = {}
    for pname in sorted(fam, key=lambda s: str(s)):
        models = []
        p_tasks = 0
        for mname in sorted(fam[pname], key=lambda s: str(s)):
            mts = sorted(fam[pname][mname], key=lambda t: (str(t.get("ts") or ""), str(t.get("dispatch_id") or "")))
            clean = []
            for t in mts:
                by_source[t["source"]] = by_source.get(t["source"], 0) + 1
                st = (t["outcome"] or {}).get("status")
                if st:
                    # desk-carrier states can be full prose verdicts; the
                    # summary buckets those, tasks keep them verbatim.
                    key = st if len(str(st)) <= 40 else "(prose state — verbatim in tasks)"
                    by_outcome[key] = by_outcome.get(key, 0) + 1
                roles_all.add(t.get("role"))
                clean.append({k: v for k, v in t.items() if not k.startswith("_")})
            models.append({
                "model": mname,
                "roles": sorted({t.get("role") for t in mts if t.get("role")}),
                "monikers": sorted({t.get("moniker") for t in mts if t.get("moniker")}),
                "contexts": sorted({t.get("context") for t in mts if t.get("context")}),
                "task_count": len(clean),
                "tasks": clean,
            })
            p_tasks += len(clean)
            n_models += 1
        providers.append({"provider": pname, "models": models,
                          "model_count": len(models), "task_count": p_tasks})
        n_tasks += p_tasks

    desk_used = next((m["records_used"] for m in meta if m["id"] == "desk-usage"), 0)
    if desk_used:
        gaps.append(f"desk-usage rows carry no run_id/dispatch_id ({desk_used} tasks): "
                    "dispatch connection for those is session_id + source_ref only (carrier shape)")
    return {
        "schema": SCHEMA,
        "generated_at": _iso(now),
        "generated_by": "scripts/tracking/nested_family.py via repo-tracking-collect.yml (single-writer)",
        "spec": {
            "doc": "docs/ops/NESTED-FAMILY.md",
            "grouping": "provider > model (verbatim, NOT_ESTABLISHED literal) > tasks; roles = distinct roles across the model's tasks",
            "task_link": "dispatch_id + run_id + source_ref (repo path of the dispatch record) = the run-id join",
        },
        "sources": meta,
        "summary": {
            "providers": len(providers), "models": n_models,
            "roles": len({r for r in roles_all if r}), "tasks": n_tasks,
            "dispatches": len({t.get("dispatch_id") for t in tasks if t.get("dispatch_id")}),
            "by_outcome": by_outcome, "by_source": by_source,
        },
        "providers": providers,
        "gaps": gaps,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="build in memory only, print summary")
    ns = ap.parse_args()
    feed = build()
    if ns.check:
        print(json.dumps(feed["summary"], indent=1))
        print("gaps:", len(feed["gaps"]))
        return 0
    out = json.dumps(feed, indent=1, sort_keys=False) + "\n"
    (ROOT / "ops" / "tracking").mkdir(parents=True, exist_ok=True)
    (ROOT / "ops" / "tracking" / "nested-family.json").write_text(out)
    dash = ROOT / "apps" / "help-wanted-dashboard" / "data"
    dash.mkdir(parents=True, exist_ok=True)
    (dash / "nested-family-feed.json").write_text(out)
    print(f"nested-family: providers={feed['summary']['providers']} models={feed['summary']['models']} "
          f"tasks={feed['summary']['tasks']} gaps={len(feed['gaps'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
