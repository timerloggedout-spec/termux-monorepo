#!/usr/bin/env python3
"""Inference availability ledger (QUE/QDesk #5546 ∧ VM cron mesh #5576 pre-scoped budgets).

DO publish per-endpoint {limit, measured, last_ok} from MEASURED fleet evidence only:
  limit     := ops/quota/registry.json (lane=model) {limit, unit, window} — ∅ ⇒ null (¬ imputed)
  measured  := count of inference calls of record in the window, per provider:
               ↳ ops/3l0/intake.jsonl (routed calls)
               ↳ experiments/doe/routed-dispatch/{records,stamps}/*.json (task_class inference-invoke)
               ↳ ops/quota/quota-probe-ledger.jsonl (probe.request_count)
               ↳ --extra JSONL streams (one call per line; {provider, ts}) e.g. VM spend logs
  last_ok   := newest successful call ∨ inference_ok probe per provider
DO compare measured calls/day vs target (default 7,500/day) — measured ≠ quoted; quoted limits stay in `limit`.
DO derive next-cycle allocation from this cycle's measurements (pre-scoped budget per endpoint):
  ↳ endpoints with last_ok ≤ 72h ∧ known daily limit ⇒ budget = min(limit_day, share of target)
  ↳ endpoints with last_ok ≤ 72h ∧ unknown limit ⇒ budget = 2 × measured_24h (probe-up, bounded)
  ↳ endpoints without recent success ⇒ budget = probe-only (1 call/day)
DO append each cycle to ops/inference/availability-ledger.jsonl (append-only) ∧ read the previous
cycle back as `prior` so allocation Δ is explicit.
Credential handling: reads committed evidence only; ¬ secrets.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "inference-availability-ledger/v1"
TARGET_DEFAULT = 7500
RECENT_OK_H = 72
TS_KEYS = ("ts", "observed_at", "created_at", "timestamp", "completed_at", "started_at", "at")
OK_WORDS = {"success", "passed", "ok", "completed", "pass"}
DAILY_UNITS = re.compile(r"requests?/day|per day|daily|RPD", re.I)


def parse_ts(value: Any) -> dt.datetime | None:
    if not isinstance(value, str) or not value:
        return None
    v = value.strip().replace("Z", "+00:00")
    try:
        t = dt.datetime.fromisoformat(v)
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def first_ts(obj: dict[str, Any]) -> dt.datetime | None:
    for k in TS_KEYS:
        t = parse_ts(obj.get(k))
        if t:
            return t
    src = obj.get("source")
    if isinstance(src, dict):
        return first_ts(src)
    return None


def provider_of(obj: dict[str, Any]) -> str | None:
    for k in ("provider", "arm_provider", "vendor"):
        if isinstance(obj.get(k), str) and obj[k]:
            return obj[k].lower()
    ep = obj.get("endpoint")
    if isinstance(ep, str) and "::" in ep:
        return ep.split("::", 1)[0].lower()
    sel = obj.get("selection")
    if isinstance(sel, dict):
        return provider_of(sel)
    return None


def ok_of(obj: dict[str, Any]) -> bool:
    for k in ("outcome", "status", "conclusion", "result"):
        v = obj.get(k)
        if isinstance(v, str) and (v.lower() in OK_WORDS or "result=success" in v.lower()):
            return True
        if isinstance(v, dict) and ok_of(v):
            return True
    return bool(obj.get("inference_ok"))


def _jsonl(path: Path) -> Iterator[dict[str, Any]]:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                yield obj


def call_events(root: Path, extra: list[Path]) -> Iterator[dict[str, Any]]:
    """Yield {provider, ts, ok, calls, source} — one row per measured call batch."""
    for obj in _jsonl(root / "ops/3l0/intake.jsonl"):
        yield {"provider": provider_of(obj), "ts": first_ts(obj), "ok": ok_of(obj), "calls": 1,
               "source": "ops/3l0/intake.jsonl"}
    for sub in ("records", "stamps"):
        d = root / "experiments/doe/routed-dispatch" / sub
        for f in sorted(d.glob("*.json")) if d.is_dir() else []:
            try:
                obj = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if not isinstance(obj, dict):
                continue
            metrics = obj.get("metrics") or {}
            if metrics.get("task_class") not in (None, "inference-invoke"):
                continue
            yield {"provider": provider_of(obj), "ts": first_ts(obj), "ok": ok_of(obj), "calls": 1,
                   "source": f"experiments/doe/routed-dispatch/{sub}"}
    for obj in _jsonl(root / "ops/quota/quota-probe-ledger.jsonl"):
        n = int(((obj.get("probe") or {}).get("request_count")) or 1)
        yield {"provider": provider_of(obj), "ts": first_ts(obj), "ok": ok_of(obj), "calls": n,
               "source": "ops/quota/quota-probe-ledger.jsonl"}
    for p in extra:
        for obj in _jsonl(p):
            yield {"provider": provider_of(obj), "ts": first_ts(obj), "ok": ok_of(obj),
                   "calls": int(obj.get("calls") or 1), "source": str(p)}


def endpoints(root: Path) -> list[dict[str, Any]]:
    reg = json.loads((root / "ops/quota/registry.json").read_text(encoding="utf-8"))
    out = []
    for s in reg.get("services", []):
        if s.get("lane") != "model":
            continue
        out.append({"endpoint": s["id"], "provider": str(s.get("provider") or "").lower(),
                    "limit": s.get("limit"), "unit": s.get("unit"), "window": s.get("window")})
    return out


NON_INFERENCE = {"github-actions"}  # CI runs ∉ inference calls (usage-series parity)
PROVIDER_ALIASES = {"gemini": "google", "gemini-cli": "google", "hf": "huggingface", "nim": "nvidia"}


def build(root: Path, now: dt.datetime, target: int = TARGET_DEFAULT, extra: list[Path] | None = None,
          prior: dict[str, Any] | None = None) -> dict[str, Any]:
    eps = endpoints(root)
    by_provider: dict[str, dict[str, Any]] = {}
    window_start = now - dt.timedelta(hours=24)
    per_day: dict[str, int] = {}
    total_events = 0
    sources: dict[str, int] = {}
    for ev in call_events(root, extra or []):
        prov = PROVIDER_ALIASES.get(ev["provider"] or "", ev["provider"] or "unattributed")
        if prov in NON_INFERENCE:
            continue
        slot = by_provider.setdefault(prov, {"measured_24h": 0, "measured_total": 0, "last_ok": None, "last_seen": None})
        slot["measured_total"] += ev["calls"]
        total_events += ev["calls"]
        sources[ev["source"]] = sources.get(ev["source"], 0) + ev["calls"]
        t = ev["ts"]
        if t:
            per_day[t.date().isoformat()] = per_day.get(t.date().isoformat(), 0) + ev["calls"]
            if window_start <= t <= now:
                slot["measured_24h"] += ev["calls"]
            iso = t.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")
            if not slot["last_seen"] or iso > slot["last_seen"]:
                slot["last_seen"] = iso
            if ev["ok"] and (not slot["last_ok"] or iso > slot["last_ok"]):
                slot["last_ok"] = iso
    rows = []
    seen = set()
    for ep in eps:
        m = by_provider.get(ep["provider"], {})
        seen.add(ep["provider"])
        rows.append({**ep, "measured_24h": m.get("measured_24h", 0), "measured_total": m.get("measured_total", 0),
                     "last_ok": m.get("last_ok"), "last_seen": m.get("last_seen"),
                     "measured_scope": "provider (shared across that provider's endpoints)"})
    for prov, m in sorted(by_provider.items()):
        if prov not in seen:
            rows.append({"endpoint": f"{prov}.unregistered", "provider": prov, "limit": None, "unit": None,
                         "window": None, **m, "measured_scope": "provider (∉ registry lane=model)"})
    measured_day = sum(m["measured_24h"] for m in by_provider.values())
    allocation = allocate(rows, now, target)
    prior_alloc = {a["endpoint"]: a["budget_calls_day"] for a in (prior or {}).get("next_allocation", [])}
    for a in allocation:
        a["delta_vs_prior"] = None if a["endpoint"] not in prior_alloc else a["budget_calls_day"] - prior_alloc[a["endpoint"]]
    best_day = max(per_day.items(), key=lambda kv: kv[1]) if per_day else (None, 0)
    return {
        "schema": SCHEMA, "generated_at": now.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "target_calls_day": target, "measured_calls_24h": measured_day,
        "target_met": measured_day >= target, "gap_calls_day": max(0, target - measured_day),
        "best_measured_day": {"date": best_day[0], "calls": best_day[1]},
        "measured_calls_all_time": total_events, "sources": sources,
        "providers_with_recent_ok": sum(1 for m in by_provider.values() if _recent(m.get("last_ok"), now)),
        "endpoints": rows, "next_allocation": allocation,
        "allocation_budget_total": sum(a["budget_calls_day"] for a in allocation),
        "prior_generated_at": (prior or {}).get("generated_at"),
        "policy": {"measured_not_quoted": True, "limit_null_means_unknown": True, "feeds": ["#5576", "#5546"]},
    }


def _recent(iso: str | None, now: dt.datetime) -> bool:
    t = parse_ts(iso)
    return bool(t and (now - t) <= dt.timedelta(hours=RECENT_OK_H))


def daily_limit(row: dict[str, Any]) -> int | None:
    lim, unit, window = row.get("limit"), str(row.get("unit") or ""), str(row.get("window") or "")
    if isinstance(lim, (int, float)) and lim > 0 and "token" not in unit.lower():
        if DAILY_UNITS.search(unit) or DAILY_UNITS.search(window):
            return int(lim)
    return None


def allocate(rows: list[dict[str, Any]], now: dt.datetime, target: int) -> list[dict[str, Any]]:
    live = [r for r in rows if _recent(r.get("last_ok"), now)]
    known = [r for r in live if daily_limit(r)]
    share = target // max(1, len(live)) if live else 0
    out = []
    for r in rows:
        if r in known:
            budget, basis = min(daily_limit(r) or 0, share), "min(limit_day, target share)"
        elif r in live:
            budget, basis = max(2 * int(r.get("measured_24h") or 0), 1), "2 × measured_24h (limit unknown)"
        else:
            budget, basis = 1, "probe-only (∄ success ≤72h)"
        out.append({"endpoint": r["endpoint"], "provider": r["provider"], "budget_calls_day": budget, "basis": basis})
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Inference availability ledger")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--target", type=int, default=TARGET_DEFAULT)
    ap.add_argument("--extra", action="append", default=[], help="extra JSONL call stream")
    ap.add_argument("--out", default="ops/inference/availability-ledger.json")
    ap.add_argument("--history", default="ops/inference/availability-ledger.jsonl")
    ap.add_argument("--now")
    a = ap.parse_args(argv)
    root = Path(a.root)
    now = parse_ts(a.now) if a.now else dt.datetime.now(dt.timezone.utc)
    out, hist = root / a.out, root / a.history
    prior = json.loads(out.read_text(encoding="utf-8")) if out.is_file() else None
    ledger = build(root, now, a.target, [Path(p) for p in a.extra], prior)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = {k: ledger[k] for k in ("generated_at", "target_calls_day", "measured_calls_24h", "gap_calls_day",
                                      "best_measured_day", "providers_with_recent_ok", "allocation_budget_total")}
    with open(hist, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(summary, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"::notice title=inference-ledger::measured_24h={ledger['measured_calls_24h']} target={a.target} "
          f"gap={ledger['gap_calls_day']} best_day={ledger['best_measured_day']} recent_ok_providers={ledger['providers_with_recent_ok']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
