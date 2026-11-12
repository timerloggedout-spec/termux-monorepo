#!/usr/bin/env python3
"""Tribute audit revisions: the WHOLE corpus as a versioned comparison.

Owner correction 2026-11-12: the primary audit view is not a 7/14/30-day window.
Each audit revision (rev N) is the entire Tribute corpus since genesis
(every foreign PR authored by the lane account + every watched issue thread
from System 1 decisions), with a stable content hash and a diff vs rev N-1:
new items, items whose state/class changed, items that left the corpus, and the
count delta per class. Revisions are append-only: data/tribute-audit/revs/
rev-NNNN.json + index.json. A run whose corpus hash equals the latest rev
writes nothing (idempotent).

The primary SLO (slo_primary) is evaluated on whole-corpus outcome ratios plus
activity-aware recency. Paused intervals count neither as failure-free time
nor as failure; starved periods (no lane attempts) are reported as STARVED,
never as success.

  python3 scripts/ci/tribute_audit_rev.py --outcomes docs/ops/generated/tribute-outcomes.json \
      --decisions /tmp/s1dec --revs-dir data/tribute-audit/revs \
      --merge-into apps/tribute-dashboard/data/status.json
Read-only toward GitHub: this module never calls the network.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA = "tribute-audit-rev/v1"
GENESIS = os.environ.get("TRIBUTE_GENESIS", "2026-09-18T20:30:00Z")  # first lane claim: vedantnimbarte/zero#72
# Lane pause / starvation intervals known to the owner (UTC, inclusive dates).
PAUSED = [("2026-10-22", "2026-10-31", "lane paused by owner")]
PR_CLASSES = ("real_merge", "stake_merge", "self_merge", "closed_unmerged", "open")
HASH_FIELDS = ("url", "kind", "repo", "class", "state", "at", "attribution_class")


def _ts(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _iso(d):
    return d.strftime("%Y-%m-%dT%H:%M:%SZ") if d else None


def _paused(paused=None):
    out = []
    for a, b, *why in (paused if paused is not None else PAUSED):
        s, e = _ts(a + "T00:00:00Z" if len(a) == 10 else a), _ts(b + "T23:59:59Z" if len(b) == 10 else b)
        if s and e:
            out.append((s, e, (why or [""])[0]))
    return out


def in_paused(t, paused):
    return any(s <= t <= e for s, e, _ in paused)


# ---------------------------------------------------------------- corpus
def corpus_items(outcomes: dict, decisions: list[dict] | None = None) -> list[dict]:
    """Every foreign PR (from the outcome census) + every watched issue thread (S1 decisions)."""
    items: dict[str, dict] = {}
    for r in outcomes.get("prs") or []:
        url = r.get("url")
        if not url:
            continue
        att = r.get("attribution") or {}
        items[url] = {"url": url, "kind": "pr", "repo": r.get("repo"), "class": r.get("class"),
                      "state": "merged" if r.get("class") in ("real_merge", "stake_merge", "self_merge")
                      else ("closed" if r.get("class") == "closed_unmerged" else "open"),
                      "at": r.get("at"), "created_at": r.get("created_at"),
                      "attribution_class": att.get("attribution_class")}
    latest: dict[str, dict] = {}
    for d in decisions or []:
        url = ((d.get("subject") or {}).get("url") or "").strip()
        if url:
            latest[url] = d
    for url, d in latest.items():
        if "/pull/" in url:
            if url in items:
                items[url]["s1_action"] = d.get("action")
            continue
        subj = d.get("subject") or {}
        items[url] = {"url": url, "kind": "issue", "repo": subj.get("repo"),
                      "class": f"thread:{d.get('action') or 'watched'}",
                      "state": subj.get("state") or d.get("state"), "at": None,
                      "created_at": subj.get("created_at"), "attribution_class": None,
                      "s1_primary": d.get("primary")}
    return sorted(items.values(), key=lambda x: x["url"])


def content_hash(items: list[dict]) -> str:
    canon = [{k: it.get(k) for k in HASH_FIELDS} for it in sorted(items, key=lambda x: x["url"])]
    return "sha256:" + hashlib.sha256(json.dumps(canon, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def class_counts(items: list[dict]) -> dict:
    c: dict[str, int] = {}
    for it in items:
        c[it["class"]] = c.get(it["class"], 0) + 1
    return dict(sorted(c.items()))


def diff(prev_items: list[dict] | None, items: list[dict]) -> dict:
    prev = {i["url"]: i for i in (prev_items or [])}
    cur = {i["url"]: i for i in items}
    new = sorted(u for u in cur if u not in prev)
    removed = sorted(u for u in prev if u not in cur)
    changed = []
    for u in sorted(set(cur) & set(prev)):
        a, b = prev[u], cur[u]
        if (a.get("class"), a.get("state")) != (b.get("class"), b.get("state")):
            changed.append({"url": u, "from": {"class": a.get("class"), "state": a.get("state")},
                            "to": {"class": b.get("class"), "state": b.get("state")}})
    pc, cc = class_counts(prev_items or []), class_counts(items)
    delta = {k: cc.get(k, 0) - pc.get(k, 0) for k in sorted(set(pc) | set(cc)) if cc.get(k, 0) != pc.get(k, 0)}
    return {"new": new, "changed": changed, "removed": removed, "counts_delta": delta,
            "n_new": len(new), "n_changed": len(changed), "n_removed": len(removed)}


# ---------------------------------------------------------------- primary SLO
def slo_primary(items: list[dict], now: datetime, paused=None, min_rate: float = 0.10, min_decided: int = 10,
                max_attempts_since_real: int = 25, starve_days: int = 7, genesis: str = GENESIS) -> dict:
    """Whole-corpus ratios + activity-aware recency (paused = excluded, starved = STARVED, never success)."""
    paused = _paused(paused)
    prs = [i for i in items if i["kind"] == "pr" and i["class"] != "self_merge"]
    c = {k: sum(1 for i in prs if i["class"] == k) for k in PR_CLASSES}
    lane_real = sum(1 for i in prs if i["class"] == "real_merge" and i.get("attribution_class") == "maintainer_accept_lane")
    decided = c["real_merge"] + c["stake_merge"] + c["closed_unmerged"]
    rate = round(c["real_merge"] / decided, 4) if decided else None
    real_times = sorted(t for t in (_ts(i["at"]) for i in prs if i["class"] == "real_merge") if t)
    last_real = real_times[-1] if real_times else None
    attempts = sorted(t for t in (_ts(i.get("created_at")) for i in prs) if t and not in_paused(t, paused))
    since = last_real or _ts(genesis)
    attempts_since = [t for t in attempts if since and t > since]
    active_days = sorted({t.date().isoformat() for t in attempts_since})
    last_attempt = attempts[-1] if attempts else None
    # starvation: no lane attempt in the last `starve_days` of NON-paused time
    window_start, d, remaining = now, now, starve_days
    while remaining > 0:
        d -= timedelta(days=1)
        if not in_paused(d, paused):
            remaining -= 1
        window_start = d
    starved = not last_attempt or last_attempt < window_start
    starved_since = _iso(last_attempt) if starved else None
    failures, warnings = [], []
    if c["real_merge"] == 0:
        failures.append({"code": "corpus_zero_real_merges", "detail": "0 real foreign merges in the whole corpus since genesis"})
    if decided >= min_decided and (rate or 0) < min_rate:
        failures.append({"code": "corpus_real_rate_below",
                         "detail": f"whole-corpus real merge rate {rate:.1%} < {min_rate:.0%} over {decided} decided PRs"})
    if len(attempts_since) >= max_attempts_since_real:
        failures.append({"code": "attempt_drought",
                         "detail": f"{len(attempts_since)} active lane attempts (paused excluded) since the last real merge "
                                   f">= {max_attempts_since_real}"})
    if starved:
        warnings.append({"code": "lane_starved",
                         "detail": f"no lane attempts in the last {starve_days} non-paused days (last attempt {starved_since}); "
                                   "starved time is neither success nor failure"})
    if c["stake_merge"]:
        warnings.append({"code": "stake_only_merges_weight_0", "detail": f"{c['stake_merge']} stake-only merges (weight 0)"})
    if lane_real < c["real_merge"]:
        warnings.append({"code": "real_merges_not_lane_produced",
                         "detail": f"{c['real_merge'] - lane_real} of {c['real_merge']} real merges were not produced by the lane"})
    status = "FAIL" if failures else ("WARN" if warnings else "OK")
    paused_now = any(s <= now <= e for s, e, _ in paused)
    return {"status": status, "basis": "whole-corpus ratios + activity-aware recency",
            "activity_state": "paused" if paused_now else ("starved" if starved else "active"),
            "failures": failures, "warnings": warnings,
            "corpus": {"decided": decided, "real_merges": c["real_merge"], "real_merges_lane": lane_real,
                       "stake_only_merges": c["stake_merge"], "closed_unmerged": c["closed_unmerged"], "open": c["open"],
                       "real_merge_rate": rate},
            "recency": {"last_real_merge_at": _iso(last_real), "last_attempt_at": _iso(last_attempt),
                        "active_attempts_since_real": len(attempts_since), "active_days_since_real": len(active_days),
                        "paused_intervals": [{"from": _iso(s), "to": _iso(e), "reason": w} for s, e, w in paused]},
            "thresholds": {"min_real_merge_rate": min_rate, "min_decided": min_decided,
                           "max_attempts_since_real": max_attempts_since_real, "starve_days": starve_days}}


# ---------------------------------------------------------------- persistence (append-only)
def load_index(revs_dir: Path) -> dict:
    p = revs_dir / "index.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"schema": SCHEMA + "/index", "genesis": GENESIS, "revs": []}


def make_rev(items: list[dict], now: datetime, revs_dir: Path, slo: dict, census_check: dict | None = None,
             write: bool = True) -> dict:
    idx = load_index(revs_dir)
    h = content_hash(items)
    prev_meta = idx["revs"][-1] if idx["revs"] else None
    if prev_meta and prev_meta["hash"] == h:
        rev = json.loads((revs_dir / prev_meta["file"]).read_text(encoding="utf-8"))
        rev["unchanged_since"] = prev_meta["generated_at"]
        rev["checked_at"] = _iso(now)
        return rev
    prev_items = json.loads((revs_dir / prev_meta["file"]).read_text(encoding="utf-8"))["items"] if prev_meta else []
    n = (prev_meta["rev"] + 1) if prev_meta else 1
    rev = {"schema": SCHEMA, "rev": n, "generated_at": _iso(now), "genesis": idx.get("genesis", GENESIS),
           "hash": h, "prev_rev": prev_meta["rev"] if prev_meta else None, "prev_hash": prev_meta["hash"] if prev_meta else None,
           "corpus_size": len(items), "counts": class_counts(items),
           "counts_by_kind": {k: sum(1 for i in items if i["kind"] == k) for k in ("pr", "issue")},
           "census_check": census_check, "diff": diff(prev_items, items), "slo_primary": slo, "items": items}
    if write:
        revs_dir.mkdir(parents=True, exist_ok=True)
        fname = f"rev-{n:04d}.json"
        if (revs_dir / fname).exists():  # append-only: never overwrite a published revision
            raise SystemExit(f"refusing to overwrite {revs_dir / fname}")
        (revs_dir / fname).write_text(json.dumps(rev, indent=1) + "\n", encoding="utf-8")
        idx["revs"].append({"rev": n, "hash": h, "generated_at": rev["generated_at"], "file": fname,
                            "corpus_size": len(items), "counts": rev["counts"],
                            "n_new": rev["diff"]["n_new"], "n_changed": rev["diff"]["n_changed"]})
        (revs_dir / "index.json").write_text(json.dumps(idx, indent=1) + "\n", encoding="utf-8")
    return rev


def status_block(rev: dict) -> dict:
    d = rev["diff"]
    return {"rev": rev["rev"], "hash": rev["hash"], "prev_rev": rev["prev_rev"], "prev_hash": rev["prev_hash"],
            "generated_at": rev["generated_at"], "checked_at": rev.get("checked_at", rev["generated_at"]),
            "genesis": rev["genesis"], "corpus_size": rev["corpus_size"], "counts": rev["counts"],
            "counts_by_kind": rev["counts_by_kind"], "census_check": rev.get("census_check"),
            "delta": {"n_new": d["n_new"], "n_changed": d["n_changed"], "n_removed": d["n_removed"],
                      "counts_delta": d["counts_delta"], "changed": d["changed"][:25], "new": d["new"][:25]},
            "slo_primary": rev["slo_primary"], "file": f"data/tribute-audit/revs/rev-{rev['rev']:04d}.json"}


def merge_into(status_path: Path, rev: dict) -> None:
    if not status_path.exists():
        return
    doc = json.loads(status_path.read_text(encoding="utf-8"))
    doc["audit_rev"] = status_block(rev)
    doc["audit_semantics"] = ("audit_rev = whole corpus since genesis, versioned (primary view); "
                              "tribute_outcomes.window_days blocks are secondary")
    status_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def markdown(rev: dict) -> str:
    s, d = rev["slo_primary"], rev["diff"]
    lines = [f"## Tribute audit rev {rev['rev']} — whole corpus since {rev['genesis'][:10]}: **{s['status']}** ({s['activity_state']})", "",
             f"hash `{rev['hash'][:19]}` · prev rev {rev['prev_rev']} · corpus {rev['corpus_size']} "
             f"(PRs {rev['counts_by_kind']['pr']}, issue threads {rev['counts_by_kind']['issue']})",
             f"delta vs prev: +{d['n_new']} new · {d['n_changed']} changed · {d['n_removed']} removed · {d['counts_delta']}", "",
             "| class | count |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in rev["counts"].items()]
    lines += [""] + [f"- FAIL `{f['code']}`: {f['detail']}" for f in s["failures"]]
    lines += [f"- WARN `{w['code']}`: {w['detail']}" for w in s["warnings"]]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    from scripts.ci.tribute_outcomes import read_jsonl  # noqa: E402 (same package)
    ap = argparse.ArgumentParser(description="Tribute whole-corpus audit revision")
    ap.add_argument("--outcomes", default="docs/ops/generated/tribute-outcomes.json")
    ap.add_argument("--decisions", nargs="*", default=[])
    ap.add_argument("--revs-dir", default="data/tribute-audit/revs")
    ap.add_argument("--latest-out", default="apps/tribute-dashboard/data/tribute-audit-rev.json")
    ap.add_argument("--md", default="docs/ops/generated/tribute-audit-rev.md")
    ap.add_argument("--merge-into", action="append", default=[])
    ap.add_argument("--now", default="")
    ap.add_argument("--summary", default="")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    now = _ts(a.now) or datetime.now(timezone.utc)
    outcomes = json.loads(Path(a.outcomes).read_text(encoding="utf-8"))
    items = corpus_items(outcomes, read_jsonl(a.decisions))
    slo = slo_primary(items, now)
    rev = make_rev(items, now, Path(a.revs_dir), slo, outcomes.get("census_check"), write=not a.dry_run)
    if not a.dry_run:
        if a.latest_out:
            Path(a.latest_out).parent.mkdir(parents=True, exist_ok=True)
            Path(a.latest_out).write_text(json.dumps(status_block(rev), indent=1) + "\n", encoding="utf-8")
        for p in a.merge_into:
            merge_into(Path(p), rev)
    md = markdown(rev)
    if a.md and not a.dry_run:
        Path(a.md).write_text(md, encoding="utf-8")
    if a.summary:
        with open(a.summary, "a", encoding="utf-8") as fh:
            fh.write(md)
    print(md)
    return 0


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    raise SystemExit(main())
