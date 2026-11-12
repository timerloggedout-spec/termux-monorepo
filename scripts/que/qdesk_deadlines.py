#!/usr/bin/env python3
"""QDesk deadline desk: requirement-closure tasks + deadline-proximity alarms.

Reads ops/challenge/coordinator.json (BOTH `events` and `candidate_events`; the
2026-11-11 Amazon Research Awards miss happened because candidate entries were
never counted, the countdown block only covered events and refreshed weekly,
and nothing turned an unmet gate into a dated task or an escalation).

For every entry it:
  * finds the governing deadline (deadline / *_due / submission* / close keys),
  * classifies it: done | gap (screened out, FAIL, institution gap, HOLD) | open,
  * turns each unmet requirement (open gates, institution gaps, owner calls)
    into a requirement-closure task with a due date on the QDesk Gantt,
  * crosses alarm tiers T-7d, T-48h, T-12h (and MISSED) for anything not done,
    and emits only tiers not already sent (state carried in the plan file).

Pure stdlib, no network. Outputs:
  --plan PATH     JSON plan (tasks, alarms, gantt rows, alarms_sent, hitl stats)
  --gantt PATH    the fleet's Gantt filing format "phase | start | end | depends-on"
  --alarms PATH   JSON list of NEW alarms for the hark:queue matrix (may be [])

Owner-approval steps (money, legal attestations, binding agreements such as a
fiscal-sponsor contract, credentials) are tagged hitl=true and escalated as a
ready-to-approve packet; everything else is agent-executable (hitl=false).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone

PT = timezone(timedelta(hours=-8))  # fallback zone for bare dates (fleet default America/Los_Angeles, winter)

TIERS = [("T-7d", timedelta(days=7)), ("T-48h", timedelta(hours=48)), ("T-12h", timedelta(hours=12))]
TIER_PRIORITY = {"T-7d": "P1", "T-48h": "P0", "T-12h": "P0", "MISSED": "P0"}

_INSTANT = re.compile(r"(\d{4}-\d{2}-\d{2})(?:[ T](\d{1,2}:\d{2})(?::\d{2})?(?:\s*([AP]M))?)?"
                      r"(?:(Z)|([+-]\d{2}):?(\d{2})\b|[^()\d]*?\(UTC([+-]\d{2}):(\d{2})\))?")
_DEADLINE_KEY = re.compile(r"deadline|_due$|^due|submission|close|final_due|preliminary_due", re.I)
_SKIP_KEY = re.compile(r"_open$|reg_open|build_start|announced|opens|decision|winners|cohort|grant_period|judging|finalists", re.I)

DONE_RE = re.compile(r"^\s*(closed|submitted|published|won|withdrawn|archived)\b|SUBMITTED", re.I)
GAP_RE = re.compile(r"SCREENED OUT|\bFAIL\b|INSTITUTION-GAP|\bHOLD\b|parked|DEFERRED", re.I)
MONEY_LEGAL_RE = re.compile(r"fiscal.?sponsor|501\(c\)\(3\)|\bNGO\b|\bPI\b|Principal Investigator|faculty|legally able|grant funds|"
                            r"contract|agreement|attest|W-9|payee|\bsign\b", re.I)


def parse_instant(raw) -> datetime | None:
    if isinstance(raw, dict):
        raw = raw.get("at")
    if not isinstance(raw, str) or "NOT_ESTABLISHED" in raw:
        return None
    hits = list(_INSTANT.finditer(raw))
    if not hits:
        return None
    m = hits[-1]  # a range "A to B" governs by its end
    day, hm, ampm, z, ih, im, oh, om = m.groups()
    if ih and hm:
        oh, om = ih, im
    if z:
        oh, om = "+00", "00"
    h, mi = (23, 59) if not hm else map(int, hm.split(":"))
    if ampm:
        h = h % 12 + (12 if ampm.upper() == "PM" else 0)
    tz = PT
    if oh:
        sign = -1 if oh.startswith("-") else 1
        tz = timezone(sign * timedelta(hours=abs(int(oh)), minutes=int(om)))
    try:
        return datetime.strptime(day, "%Y-%m-%d").replace(hour=h, minute=mi, tzinfo=tz)
    except ValueError:
        return None


def governing_deadline(entry: dict) -> tuple[str, datetime] | None:
    dates = entry.get("dates") or {}
    if not isinstance(dates, dict):
        return None
    found = []
    for k, v in dates.items():
        if _SKIP_KEY.search(k) or not _DEADLINE_KEY.search(k):
            continue
        dt = parse_instant(v)
        if dt:
            found.append((k, dt))
    return min(found, key=lambda kv: kv[1]) if found else None  # the earliest binding wall


def classify(entry: dict) -> str:
    st = str(entry.get("status") or "")
    if GAP_RE.search(st):
        return "gap"
    if DONE_RE.search(st):
        return "done"
    return "open"


def _open_gates(entry: dict) -> list[dict]:
    g = entry.get("gates")
    out = []
    if isinstance(g, list):
        for x in g:
            if not isinstance(x, dict):
                continue
            state = str(x.get("status") or x.get("state") or "").lower()
            if state in ("", "open", "conditional", "pending", "blocked") or "open" in state:
                out.append({"id": x.get("id") or "gate", "label": str(x.get("label") or x.get("text") or "")[:240],
                            "owner": str(x.get("owner") or "")[:120]})
    elif isinstance(g, str) and g.strip() and not re.search(r"\bCONFIRMED\b|\bMET\b", g):
        out.append({"id": "eligibility", "label": g[:240], "owner": ""})
    return out


def _d(dt: datetime) -> str:
    return dt.astimezone(PT).strftime("%Y-%m-%d")


def closure_tasks(entry: dict, kind: str, deadline: datetime | None, now: datetime) -> list[dict]:
    """Requirement-closure tasks: what must be true to enter, each dated and owned."""
    eid = entry.get("id")
    tasks: list[dict] = []
    text = " ".join(str(entry.get(k) or "") for k in ("status", "gates")) + json.dumps(entry.get("institution_gap") or "")
    institution = kind == "gap" and MONEY_LEGAL_RE.search(text)
    # due anchor: the live deadline if far enough out, else the next cycle (planning horizon from now)
    live = deadline and deadline > now + timedelta(days=3)
    anchor = deadline if live else now + timedelta(days=75)
    span = max(anchor - now, timedelta(days=4))

    def add(slug, title, frac_start, frac_end, hitl, depends=None, packet=None):
        s, e = now + span * frac_start, now + span * frac_end
        tasks.append({"id": f"{eid}:{slug}", "entry": eid, "title": title, "start": _d(s), "due": _d(e),
                      "hitl": hitl, "depends_on": depends or [], "state": "todo",
                      "cycle": "current" if live else "next-cycle", **({"owner_packet": packet} if packet else {})})

    if institution:
        add("sponsor-shortlist", "Fiscal-sponsor shortlist: 5+ 501(c)(3) sponsors offering Model A (employ PI) or "
            "Model C, fees, intake time, AI/OSS fit, grant-receipt terms (sources cited)", 0.0, 0.2, False)
        add("pi-route", "PI route: which sponsor can employ/appoint a permanent researcher PI meeting the clause; "
            "draft the eligibility memo citing the funder's written answer", 0.15, 0.35, False, [f"{eid}:sponsor-shortlist"])
        add("sponsor-application", "Prepare sponsor intake application + project description (draft, not submitted)",
            0.3, 0.5, False, [f"{eid}:pi-route"])
        add("owner-sign-sponsor", "OWNER APPROVAL: choose sponsor and sign the fiscal-sponsorship / PI agreement "
            "(binding legal agreement; fees may apply)", 0.5, 0.6, True, [f"{eid}:sponsor-application"],
            packet="sponsor shortlist + fee table + draft agreement terms + recommendation; approve = sign via sponsor portal")
        add("rescreen", "Re-screen eligibility with the sponsor in place and register for the cycle", 0.6, 0.7, False,
            [f"{eid}:owner-sign-sponsor"])
        add("draft-submit", "Draft, internal Delphi review, and submit the proposal", 0.7, 0.98, False, [f"{eid}:rescreen"])
    if kind == "open" and re.search(r"awaiting|pending (owner|manager)|slate call", str(entry.get("status") or ""), re.I):
        add("decision", "Get the pending go/no-go decision recorded (" + re.sub(r"\s+", " ", str(entry.get("status")))[:120] + ")",
            0.0, 0.15 if live else 0.1, False)
    if kind == "gap" and not institution:
        add("reassess", "Re-assess the hold/screen-out: name the unmet clause, the cheapest closure route, and a go/no-go",
            0.0, 0.25, False)
    for g in _open_gates(entry) if kind != "done" else []:
        hitl = bool(MONEY_LEGAL_RE.search(g["label"])) or "owner" in g["owner"].lower() and "sign" in g["label"].lower()
        if institution and g["id"] == "eligibility":
            continue
        add(f"gate-{re.sub(r'[^A-Za-z0-9]+', '-', str(g['id'])).strip('-').lower()}",
            f"Close gate {g['id']}: {g['label']}", 0.0, 0.5 if live else 0.3, hitl,
            packet="gate evidence + exact action requested" if hitl else None)
    return tasks


def alarms_for(entry: dict, kind: str, deadline: datetime | None, now: datetime, sent: dict, tasks: list[dict]) -> list[dict]:
    if kind == "done" or not deadline:
        return []
    eid = entry.get("id")
    key = f"qdesk-deadline:{eid}:{_d(deadline)}"
    already = set(sent.get(key, []))
    left = deadline - now
    crossed = []
    if left <= timedelta(0):
        if left > -timedelta(days=2):
            crossed = ["MISSED"]
    else:
        crossed = [t for t, w in TIERS if left <= w]
    new = [t for t in crossed if t not in already]
    if not new:
        return []
    tier = new[-1]  # the most urgent newly crossed tier
    open_tasks = [t for t in tasks if t["state"] != "done" and t["cycle"] == "current"]
    hitl = [t for t in open_tasks if t["hitl"]]
    why = ("unmet requirement(s): " + "; ".join(t["title"][:90] for t in open_tasks[:4])) if open_tasks else \
          ("entry status is not submitted: " + str(entry.get("status"))[:160])
    return [{"key": key, "tier": tier, "tiers": new, "entry": eid, "name": str(entry.get("name") or eid)[:90],
             "deadline": deadline.isoformat(), "left_hours": round(left.total_seconds() / 3600, 1), "kind": kind,
             "priority": TIER_PRIORITY[tier], "why": why, "owner_packets": [t["id"] for t in hitl],
             "url": entry.get("official_url") or ""}]


def build(coord: dict, now: datetime, prev: dict | None = None) -> dict:
    sent = dict((prev or {}).get("alarms_sent") or {})
    prev_tasks = {t["id"]: t for t in (prev or {}).get("tasks", [])}
    tasks, alarms, entries = [], [], []
    for group in ("events", "candidate_events"):
        for e in coord.get(group) or []:
            if not isinstance(e, dict) or not e.get("id"):
                continue
            kind = classify(e)
            gd = governing_deadline(e)
            dl = gd[1] if gd else None
            ts = closure_tasks(e, kind, dl, now)
            for t in ts:  # keep agent-recorded progress and first-planned dates across regenerations
                p = prev_tasks.get(t["id"])
                if p:
                    t["state"] = p.get("state", t["state"])
                    t["start"], t["due"] = p.get("start", t["start"]), p.get("due", t["due"])
            tasks += ts
            al = alarms_for(e, kind, dl, now, sent, ts)
            for a in al:
                sent.setdefault(a["key"], [])
                sent[a["key"]] = sorted(set(sent[a["key"]]) | set(a["tiers"]))
            alarms += al
            entries.append({"id": e["id"], "group": group, "kind": kind, "deadline_key": gd[0] if gd else None,
                            "deadline": dl.isoformat() if dl else None,
                            "left_hours": round((dl - now).total_seconds() / 3600, 1) if dl else None,
                            "status": str(e.get("status") or "")[:160]})
    gantt = [{"id": t["id"], "label": t["title"][:80], "start": t["start"], "end": t["due"], "depends_on": t["depends_on"],
              "hitl": t["hitl"], "entry": t["entry"]} for t in tasks]
    for en in entries:
        if en["deadline"] and en["kind"] != "done":
            d = en["deadline"][:10]
            gantt.append({"id": f"{en['id']}:deadline", "label": f"{en['id']} deadline ({en['deadline_key']})",
                          "start": d, "end": d, "depends_on": [], "hitl": False, "entry": en["id"], "milestone": True})
    n_hitl = sum(t["hitl"] for t in tasks)
    return {"schema": "qdesk.plan.v1", "generated_at": now.isoformat(), "source": "ops/challenge/coordinator.json",
            "doc": "docs/ops/QDESK-DEADLINE-ALARMS.md", "entries": entries, "tasks": tasks, "gantt": gantt,
            "alarms": alarms, "alarms_sent": sent,
            "hitl": {"tasks": len(tasks), "owner_steps": n_hitl, "rate": round(n_hitl / len(tasks), 3) if tasks else 0.0}}


def gantt_text(plan: dict) -> str:
    lines = []  # filing format only (gantt_compile.py treats every line as a phase); provenance lives in the plan JSON
    ids = {g["id"] for g in plan["gantt"]}
    for g in plan["gantt"]:
        deps = ",".join(d for d in g["depends_on"] if d in ids)
        lines.append(f"{g['id']} | {g['start']} | {g['end']} | {deps}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--coordinator", default="ops/challenge/coordinator.json")
    ap.add_argument("--prev", help="previous plan JSON (alarm state); missing file = fresh")
    ap.add_argument("--plan")
    ap.add_argument("--gantt")
    ap.add_argument("--alarms")
    ap.add_argument("--now", help="ISO instant (tests)")
    a = ap.parse_args(argv)
    now = datetime.fromisoformat(a.now) if a.now else datetime.now(timezone.utc)
    coord = json.load(open(a.coordinator, encoding="utf-8"))
    prev = None
    if a.prev:
        try:
            prev = json.load(open(a.prev, encoding="utf-8"))
        except (OSError, ValueError):
            prev = None
    plan = build(coord, now, prev)
    if a.plan:
        json.dump(plan, open(a.plan, "w", encoding="utf-8"), indent=1, sort_keys=False)
        open(a.plan, "a").write("\n")
    if a.gantt:
        open(a.gantt, "w", encoding="utf-8").write(gantt_text(plan))
    if a.alarms is not None:
        json.dump(plan["alarms"], open(a.alarms, "w", encoding="utf-8"))
    for al in plan["alarms"]:
        print(f"::warning title=qdesk {al['tier']}::{al['entry']} {al['name']} - {al['left_hours']}h left - {al['why'][:160]}")
    print(f"::notice title=qdesk::entries={len(plan['entries'])} tasks={plan['hitl']['tasks']} "
          f"owner_steps={plan['hitl']['owner_steps']} hitl_rate={plan['hitl']['rate']} new_alarms={len(plan['alarms'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
