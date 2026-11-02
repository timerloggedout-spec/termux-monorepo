#!/usr/bin/env python3
"""Nested-family record — provider > model > {roles, tasks run}, with
dispatch connection (owner standard 2026-11-01; spec:
docs/ops/NESTED-FAMILY.md, schema nested-family/v1).

Population = existing dispatch records only, no new instrumentation:
  1. records    experiments/doe/routed-dispatch/records/*.json
                (EXPERIMENT records — scoring-plane record of record)
  2. campaign-records  experiments/doe/*/records/*.json (any other
                campaign; provider-bearing records only — pre-agreed
                with the DoE plane so live-3 resumption nests free)
  3. stamps     experiments/doe/routed-dispatch/stamps/*.json
  4. intake     ops/3l0/intake.jsonl (3l0-intake/v1 fan-out copy)
  5. desk-usage ops/challenge/desk-feed.json traversals[].provider_usage[]
A dispatch counts once, under the highest-priority source carrying it
(dedupe: dispatch_id, else session_id); lower-priority carriers only
fill fields the winner left null (enrichment, never overwrite).
Identity fields are verbatim; NOT_ESTABLISHED stays literal; outcomes
are the sources' own (this substrate never scores). Single-writer:
repo-tracking-collect.yml. Outputs: ops/tracking/nested-family.json +
apps/tribute-dashboard/data/nested-family-feed.json (byte-identical).
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "nested-family/v1"
NOT_ESTABLISHED = "NOT_ESTABLISHED"
_RUN_TAIL = re.compile(r"(\d{6,})$")
_FILL_FIELDS = ("task_class", "role", "moniker", "context", "run_id",
                "workflow", "session_id", "ts")
# instance_key is deliberately NOT a fill field (DoE ruling 2026-11-01):
# enrichment never synthesizes one — a task's instance_key comes only
# from its own winning record, else stays null/NOT_ESTABLISHED.


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


def _base_task() -> dict:
    return {"task_class": None, "role": None, "moniker": None, "context": None,
            "dispatch_id": None, "run_id": None, "workflow": None,
            "session_id": None, "ts": None,
            "outcome": {"status": None, "gate_call": None, "confirmed": None},
            "instance_key": None, "first_pass": None, "origin": None,
            "pr": None, "field_sources": {}, "source": None, "source_ref": None}


def _task_from_stamp(rec: dict, source: str, source_ref: str) -> dict:
    run = rec.get("run") if isinstance(rec.get("run"), dict) else {}
    inst = rec.get("instance") if isinstance(rec.get("instance"), dict) else {}
    t = _base_task()
    t.update({
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
    })
    return t


def _task_from_record(rec: dict, stem: str, source_ref: str):
    """EXPERIMENT record -> (task, provider, model). Identity from
    treatment.instance, falling back to flat treatment fields."""
    tr = rec.get("treatment") if isinstance(rec.get("treatment"), dict) else {}
    inst = tr.get("instance") if isinstance(tr.get("instance"), dict) else {}
    metrics = rec.get("metrics") if isinstance(rec.get("metrics"), dict) else {}
    provider = inst.get("provider") or tr.get("provider")
    model = inst.get("model") or tr.get("model")
    tail = _RUN_TAIL.search(stem or "")
    t = _base_task()
    t.update({
        "task_class": metrics.get("task_class"),
        "role": inst.get("role"),
        "moniker": inst.get("moniker"),
        "context": inst.get("context"),
        "dispatch_id": stem,
        "run_id": int(tail.group(1)) if tail else None,
        "session_id": rec.get("session_id"),
        "ts": rec.get("observed_at"),
        "outcome": {"status": rec.get("status"), "gate_call": None, "confirmed": None},
        "instance_key": inst.get("instance_key"),
        "first_pass": metrics.get("first_pass_success"),
        "origin": rec.get("origin"),
        "pr": metrics.get("pr"),
        "source": "records",
        "source_ref": source_ref,
    })
    return t, provider, model


def _task_from_campaign(rec: dict, stem: str, source_ref: str, campaign: str):
    """Campaign EXPERIMENT/arm record -> (task, provider, model).
    EXPERIMENT shape first (treatment.instance / flat treatment);
    arm records (apk-1 shape) fall back to top-level provider/pr/route."""
    t, provider, model = _task_from_record(rec, stem, source_ref)
    if not provider:
        provider = rec.get("provider")
    if not model:
        model = rec.get("model")
    if t["pr"] is None and isinstance(rec.get("pr"), int):
        t["pr"] = rec.get("pr")
    if t["context"] is None:
        t["context"] = rec.get("route") or campaign
    if t["ts"] is None:
        t["ts"] = rec.get("recorded_at")
    if t["task_class"] is None:
        t["task_class"] = rec.get("task_class")
    t["source"] = "campaign-records"
    return t, provider, model


def _task_from_desk(row: dict, entry: str) -> dict:
    t = _base_task()
    t.update({
        "task_class": "desk-traversal",
        "role": row.get("role"),
        "moniker": row.get("moniker"),
        "context": row.get("context") or f"desk traversal {entry}",
        "session_id": row.get("session_id"),
        "outcome": _outcome(row.get("state")),
        "instance_key": row.get("instance_key"),
        "source": "desk-usage",
        "source_ref": f"ops/challenge/desk-feed.json#traversals[{entry}].provider_usage",
    })
    return t


def _enrich(task: dict, donor: dict) -> None:
    """Fill fields the task left null from a lower-priority carrier of
    the same dispatch. Never overwrites; every fill is provenance-tagged
    in task['field_sources'] (DoE ruling 2026-11-01)."""
    for f in _FILL_FIELDS:
        if task.get(f) is None and donor.get(f) is not None:
            task[f] = donor[f]
            task["field_sources"][f] = donor["source"]
    for f in ("gate_call", "confirmed"):
        if task["outcome"].get(f) is None and donor["outcome"].get(f) is not None:
            task["outcome"][f] = donor["outcome"][f]
            task["field_sources"][f"outcome.{f}"] = donor["source"]


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

    # --- load the stamp-shaped carriers first (enrichment donors) ---
    sdir = base / "experiments" / "doe" / "routed-dispatch" / "stamps"
    sfiles = sorted(sdir.glob("*.json")) if sdir.exists() else []
    stamp_by_id: dict[str, dict] = {}
    for p in sfiles:
        rec = _read_json(p)
        if isinstance(rec, dict) and rec.get("dispatch_id"):
            t = _task_from_stamp(rec, "stamps",
                                 f"experiments/doe/routed-dispatch/stamps/{p.name}")
            t["_g_provider"] = rec.get("provider")
            t["_g_model"] = rec.get("model") or NOT_ESTABLISHED
            stamp_by_id[rec["dispatch_id"]] = t

    ipath = base / "ops" / "3l0" / "intake.jsonl"
    irows = []
    if ipath.exists():
        for line in ipath.read_text().splitlines():
            if line.strip():
                try:
                    irows.append(json.loads(line))
                except Exception:
                    continue
    intake_by_id: dict[str, dict] = {}
    for rec in irows:
        if isinstance(rec, dict) and rec.get("dispatch_id"):
            intake_by_id[rec["dispatch_id"]] = _task_from_stamp(
                rec, "intake", f"ops/3l0/intake.jsonl#{rec.get('dispatch_id')}")

    # 1. EXPERIMENT records (scoring-plane record of record)
    rdir = base / "experiments" / "doe" / "routed-dispatch" / "records"
    rfiles = sorted(rdir.glob("*.json")) if rdir.exists() else []
    used = 0
    for p in rfiles:
        rec = _read_json(p)
        if not isinstance(rec, dict):
            continue
        task, provider, model = _task_from_record(
            rec, p.stem, f"experiments/doe/routed-dispatch/records/{p.name}")
        if not provider:
            continue
        donor = stamp_by_id.get(p.stem) or intake_by_id.get(p.stem)
        if donor is not None:
            _enrich(task, donor)
        donor2 = intake_by_id.get(p.stem)
        if donor2 is not None and donor2 is not donor:
            _enrich(task, donor2)
        if admit(task, provider, model or NOT_ESTABLISHED):
            used += 1
    meta.append({"id": "records", "path": "experiments/doe/routed-dispatch/records/*.json",
                 "records_read": len(rfiles), "records_used": used})
    if not rfiles:
        gaps.append("records source empty: experiments/doe/routed-dispatch/records has no files")

    # 2. campaign records (any other experiments/doe/*/records dir):
    # provider-bearing per-dispatch records only; summary/audit
    # aggregates are not dispatches and are skipped by name.
    cdirs = []
    doe_dir = base / "experiments" / "doe"
    if doe_dir.exists():
        cdirs = sorted(p for p in doe_dir.glob("*/records")
                       if p.parent.name != "routed-dispatch")
    cread = cused = 0
    for rdir in cdirs:
        for p in sorted(rdir.glob("*.json")):
            cread += 1
            if p.name == "SUMMARY.json" or p.name.endswith("-audit.json"):
                continue
            rec = _read_json(p)
            if not isinstance(rec, dict):
                continue
            ref = f"experiments/doe/{rdir.parent.name}/records/{p.name}"
            task, provider, model = _task_from_campaign(rec, p.stem, ref, rdir.parent.name)
            if not provider:
                continue
            donor = stamp_by_id.get(p.stem) or intake_by_id.get(p.stem)
            if donor is not None:
                _enrich(task, donor)
            if admit(task, provider, model or NOT_ESTABLISHED):
                cused += 1
    meta.append({"id": "campaign-records", "path": "experiments/doe/*/records/*.json",
                 "records_read": cread, "records_used": cused})

    # 3. canonical stamps (dispatches with no EXPERIMENT record)
    used = 0
    for did, task in stamp_by_id.items():
        if task.get("_g_provider") and admit(task, task["_g_provider"], task["_g_model"]):
            used += 1
    meta.append({"id": "stamps", "path": "experiments/doe/routed-dispatch/stamps/*.json",
                 "records_read": len(sfiles), "records_used": used})
    if not sfiles:
        gaps.append("stamps source empty: experiments/doe/routed-dispatch/stamps has no files")

    # 4. 3l0 intake fan-out (dispatches neither record nor stamp carries)
    used = 0
    for rec in irows:
        if not isinstance(rec, dict) or not rec.get("provider"):
            continue
        if admit(_task_from_stamp(rec, "intake", f"ops/3l0/intake.jsonl#{rec.get('dispatch_id')}"),
                 rec.get("provider"), rec.get("model") or NOT_ESTABLISHED):
            used += 1
    meta.append({"id": "intake", "path": "ops/3l0/intake.jsonl",
                 "records_read": len(irows), "records_used": used})

    # 5. desk provider_usage carrier
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


def _registry_providers(base: Path):
    """ALL-providers denominator (owner amendment 2026-11-01): distinct
    provider names, verbatim, from ops/quota/registry.json model lane.
    Returns (names, n_records, path) or (None, 0, path) when unreadable —
    the records/distinct pair is the census vintage fingerprint."""
    path = base / "ops" / "quota" / "registry.json"
    reg = _read_json(path)
    if not isinstance(reg, dict):
        return None, 0, "ops/quota/registry.json"
    lane = [s for s in reg.get("services", [])
            if isinstance(s, dict) and s.get("lane") == "model" and s.get("provider")]
    names = sorted({s.get("provider") for s in lane}, key=lambda s: str(s).casefold())
    return names, len(lane), "ops/quota/registry.json"


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
                          "model_count": len(models), "task_count": p_tasks,
                          "zero_dispatch": False})
        n_tasks += p_tasks

    # ALL-providers denominator: registry model-lane providers with no
    # dispatch family appear as zero-dispatch gap rows (verbatim names;
    # join = casefold-exact, no aliases — declared in spec).
    reg_names, reg_records, reg_path = _registry_providers(base)
    coverage = None
    if reg_names is None:
        gaps.append(f"registry denominator unavailable: {reg_path} unreadable — zero-dispatch rows omitted")
    else:
        fam_fold = {str(p).casefold(): p for p in fam}
        zero = [n for n in reg_names if str(n).casefold() not in fam_fold]
        for n in zero:
            providers.append({"provider": n, "models": [], "model_count": 0,
                              "task_count": 0, "zero_dispatch": True})
        reg_fold = {str(n).casefold() for n in reg_names}
        unregistered = sorted((p for p in fam if str(p).casefold() not in reg_fold),
                              key=lambda s: str(s))
        coverage = {
            "denominator": f"{reg_path} · lane=model · distinct provider",
            "registry_records": reg_records,
            "registry_providers": len(reg_names),
            "with_dispatches": len(reg_names) - len(zero),
            "zero_dispatch": zero,
            "unregistered_dispatch_providers": unregistered,
        }
        if unregistered:
            gaps.append("dispatch providers with no registry model-lane match "
                        f"(casefold-exact join, no aliases): {', '.join(map(str, unregistered))}")

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
        "coverage": coverage,
        "summary": {
            "providers": len({p['provider'] for p in providers if not p.get('zero_dispatch')}),
            "models": n_models,
            "roles": len({r for r in roles_all if r}), "tasks": n_tasks,
            "dispatches": len({t.get("dispatch_id") for t in tasks if t.get("dispatch_id")}),
            "registry_providers": coverage["registry_providers"] if coverage else None,
            "zero_dispatch_providers": len(coverage["zero_dispatch"]) if coverage else None,
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
    dash = ROOT / "apps" / "tribute-dashboard" / "data"
    dash.mkdir(parents=True, exist_ok=True)
    (dash / "nested-family-feed.json").write_text(out)
    print(f"nested-family: providers={feed['summary']['providers']} models={feed['summary']['models']} "
          f"tasks={feed['summary']['tasks']} gaps={len(feed['gaps'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
