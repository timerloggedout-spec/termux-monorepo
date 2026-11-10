#!/usr/bin/env python3
"""Opportunity self-eval cycle — #5096 / #5103.

Repo-internal, deterministic, stdlib only. Per run, for ALL live
opportunities in ops/challenge/coordinator.json:

  ingest -> QUE priority stamp -> prep gate (Stages 0-4 + submission
  census) -> Delphi-rubric selection -> Stages 5-7 -> tier actions

Honesty rails (binding):
- Absent evidence is stamped NOT_ESTABLISHED with the gap named; nothing
  is fabricated.
- The prep gate is fail-closed: incomplete prep yields verdict
  PREP_INCOMPLETE, stages 5-7 recorded blocked_prep_incomplete, and
  tier_actions == []. No exceptions.
- Selection follows the Delphi gate.py pattern: transparent rubric
  arithmetic, no model ballots, no provider calls. A completion leg that
  cannot execute in-cycle is recorded specified_not_run with a reason
  (method_cycle honesty rule).
- Every tier action stamps ts > prep_verified_at; the invariant is
  enforced in code (AssertionError) and pinned by tests.
- The cycle never executes an external submission; it stamps readiness.

Design of record: docs/ops/OPPORTUNITY-CYCLE.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

NOT_ESTABLISHED = "NOT_ESTABLISHED"

# Coordinator date keys that can serve as the next gate, in preference
# order. Anything else parseable in dates{} is a fallback.
GATE_KEYS = [
    "judging_end",
    "winners_at",
    "deadline",
    "final_due",
    "preliminary_due",
    "submission_deadline",
    "reg_close",
    "build_end",
    "proposal_due",
    "initial_proposal_due",
]

CENSUS_CLASSES = {"automatable", "fleet-executable", "owner-hand"}
COMPLETION_LEGS = ["tournament-update", "moneyball-update", "osint-refresh"]

# priority_timebox derivation offsets when no verbatim timebox is carried.
TIMEBOX_OFFSETS = {
    "landing": timedelta(hours=24),
    "cushion": timedelta(hours=72),
    "escalation": timedelta(hours=12),
    "final": timedelta(minutes=30),
}


# ---------------------------------------------------------------- stamps
class StampClock:
    """Monotonic stamp source: every stamp is strictly later than the
    previous one (>= +1s), so intra-cycle ordering (prep before tier) is
    provable from the receipt alone. With a fixed base (tests) the clock
    is purely logical and deterministic."""

    def __init__(self, fixed: datetime | None = None):
        self.fixed = fixed
        self._last: datetime | None = None

    def stamp(self) -> datetime:
        if self.fixed is not None:
            t = self.fixed if self._last is None else self._last + timedelta(seconds=1)
        else:
            now = datetime.now(timezone.utc)
            t = now if self._last is None else max(now, self._last + timedelta(seconds=1))
        self._last = t
        return t


def iso(t: datetime) -> str:
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- io utils
def load_json(path: Path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_sha(obj) -> str:
    return sha256_bytes(json.dumps(obj, sort_keys=True).encode("utf-8"))


_ISO_HEAD = re.compile(r"^(\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?)?)")


def parse_instant(value):
    """Parse an ISO instant out of the coordinator's loose shapes:
    {at: ...} dicts, plain strings, 'YYYY-MM-DD', and strings with a
    trailing annotation ('2026-11-20T23:59:00-12:00 (Anywhere on Earth)').
    Returns an aware datetime or None."""
    if value is None:
        return None
    if isinstance(value, dict):
        return parse_instant(value.get("at"))
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text or text == NOT_ESTABLISHED:
        return None
    m = _ISO_HEAD.match(text)
    if not m:
        return None
    raw = m.group(1).replace(" ", "T")
    rest = text[m.end():].strip()
    tz = "+00:00"
    if rest.startswith("Z"):
        tz = "+00:00"
    elif rest[:1] in "+-" and re.match(r"^[+-]\d{2}:?\d{2}", rest):
        tz = re.match(r"^[+-]\d{2}:?\d{2}", rest).group(0)
        if len(tz) == 5:
            tz = tz[:3] + ":" + tz[3:]
    try:
        dt = datetime.fromisoformat(raw + tz)
    except ValueError:
        return None
    return dt.astimezone(timezone.utc)


# ---------------------------------------------------------------- ingest
def is_live_event(ev: dict) -> bool:
    return str(ev.get("status", "")).strip().lower() != "closed"


def is_live_candidate(cand: dict) -> bool:
    status = str(cand.get("status", "")).strip().lower()
    return not (status.startswith("screened out") or status.startswith("screened-out"))


def find_next_gate(record: dict):
    """(instant, source_key) for the record's next gate, or (None, None)."""
    dates = record.get("dates") or {}
    if isinstance(dates, dict):
        for key in GATE_KEYS:
            if key in dates:
                t = parse_instant(dates[key])
                if t is not None:
                    return t, f"dates.{key}"
        for key in sorted(dates):
            t = parse_instant(dates[key])
            if t is not None:
                return t, f"dates.{key}"
    t = parse_instant(record.get("deadline"))
    if t is not None:
        return t, "deadline"
    return None, None


def resolve_slug(entries_dir: Path, opp_id: str):
    """Coordinator id -> entries/<slug> directory. Exact lowercase match
    first, then the fleet's id-prefixed directory (D1 -> d1-studysprint).
    Returns (slug, dir-or-None)."""
    low = opp_id.lower()
    if entries_dir.is_dir():
        names = sorted(p.name for p in entries_dir.iterdir() if p.is_dir())
        if low in names:
            return low, entries_dir / low
        for name in names:
            if name.startswith(low + "-"):
                return name, entries_dir / name
    return low, None


def deskfeed_timeboxes(desk_feed) -> dict:
    """entry -> priority_timebox, walked out of desk-feed traversals."""
    found = {}

    def walk(obj):
        if isinstance(obj, dict):
            if "entry" in obj and isinstance(obj.get("priority_timebox"), dict):
                found[str(obj["entry"])] = obj["priority_timebox"]
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    if desk_feed is not None:
        walk(desk_feed)
    return found


def normalize_timebox(pt: dict, wall_fallback):
    """Normalize a verbatim desk-feed priority_timebox into
    {wall, landing, cushion, escalation, final}. Returns None when no
    wall resolves."""
    wall = parse_instant(pt.get("wall"))
    if wall is None:
        wall = wall_fallback
    if wall is None:
        return None
    tiers = pt.get("tiers") or []

    def tier_at(*needles):
        for tier in tiers:
            name = str(tier.get("name", "")).upper()
            if any(n in name for n in needles):
                return parse_instant(tier.get("at") or tier.get("from"))
        return None

    landing = parse_instant(pt.get("landing")) or tier_at("LANDING")
    if landing is None:
        landing = wall - TIMEBOX_OFFSETS["landing"]
    cushion = tier_at("CUSHION") or (wall - TIMEBOX_OFFSETS["cushion"])
    escalation = tier_at("ESCALATION") or (wall - TIMEBOX_OFFSETS["escalation"])
    final = tier_at("FINAL") or (wall - TIMEBOX_OFFSETS["final"])
    return {
        "wall": iso(wall),
        "landing": iso(landing),
        "cushion": iso(cushion),
        "escalation": iso(escalation),
        "final": iso(final),
        "source": "ops/challenge/desk-feed.json priority_timebox (verbatim wall/tiers; gaps derived)",
        "verbatim": pt,
    }


def derive_timebox(wall: datetime):
    return {
        "wall": iso(wall),
        "landing": iso(wall - TIMEBOX_OFFSETS["landing"]),
        "cushion": iso(wall - TIMEBOX_OFFSETS["cushion"]),
        "escalation": iso(wall - TIMEBOX_OFFSETS["escalation"]),
        "final": iso(wall - TIMEBOX_OFFSETS["final"]),
        "source": "derived offsets {landing wall-24h, cushion wall-72h, escalation wall-12h, final wall-30m}",
        "verbatim": None,
    }


# ---------------------------------------------------------------- census
def check_census(census_path: Path, wall: datetime | None):
    """Validate one entry's submission-requirements census.
    Returns (verdict_dict, requirements list)."""
    if not census_path.is_file():
        return {"state": "MISSING", "violations": [f"census missing: {census_path.name}"]}, []
    data = load_json(census_path)
    if not isinstance(data, dict) or not isinstance(data.get("requirements"), list):
        return {"state": "FAIL", "violations": ["census has no requirements[] list"]}, []
    violations = []
    for row in data["requirements"]:
        rid = row.get("id", "<unnamed>")
        cls = row.get("class")
        if cls not in CENSUS_CLASSES:
            violations.append(f"{rid}: class {cls!r} not in {sorted(CENSUS_CLASSES)}")
            continue
        if cls == "owner-hand" and row.get("capacity_verified") is not True:
            violations.append(f"{rid}: owner-hand without capacity_verified=true")
        if cls != "automatable":
            ra = row.get("route_around") or {}
            if ra.get("sought") is not True:
                violations.append(f"{rid}: non-automatable without route_around.sought=true")
        landing = parse_instant(row.get("landing_time"))
        if landing is None:
            violations.append(f"{rid}: landing_time missing/unparseable")
        elif wall is None:
            violations.append(f"{rid}: timebox wall NOT_ESTABLISHED — landing_time cannot be checked")
        elif landing > wall:
            violations.append(f"{rid}: landing_time {iso(landing)} after wall {iso(wall)}")
        if row.get("submit_once") is True and row.get("discharged") is True \
                and row.get("first_send_verified") is not True:
            violations.append(f"{rid}: submit-once discharged without first_send_verified=true")
    state = "PASS" if not violations else "FAIL"
    return {"state": state, "violations": violations}, data["requirements"]


# ---------------------------------------------------------------- prep gate
def ledger_rows_for(ledger: dict | None, opp_id: str) -> list:
    if not isinstance(ledger, dict):
        return []
    rows = []
    for entry in ledger.get("entries", []):
        event = str(entry.get("event", ""))
        if event == opp_id or event.startswith(opp_id + " ") or event.startswith(opp_id + " —"):
            rows.append(entry.get("id"))
    return rows


def coordinator_registered(record: dict) -> bool:
    """CHALLENGE-SCHEMA fallback for Stage 0: the coordinator carries the
    entry with dates and prizes populated."""
    dates = record.get("dates")
    prizes = record.get("prizes")
    dates_ok = isinstance(dates, dict) and any(
        parse_instant(v) is not None for v in dates.values())
    prizes_ok = isinstance(prizes, dict) and bool(
        prizes.get("pool") or prizes.get("tiers") or prizes.get("per_project")
        or prizes.get("per_proposal"))
    return bool(dates_ok and prizes_ok)


def verify_prep(root: Path, opp: dict, record: dict, slug: str, slug_dir,
                timebox, ledger, clock: StampClock):
    """Returns (gate_dict, manifest_or_None, census_rows)."""
    evaluated_at = clock.stamp()
    stages = {}
    gaps = []
    manifest = None
    manifest_rel = f"entries/{slug}/prep-manifest.json"
    if slug_dir is None or not (slug_dir / "prep-manifest.json").is_file():
        for s in "01234":
            stages[s] = {"state": NOT_ESTABLISHED,
                         "gap": f"prep-manifest missing at {manifest_rel}"}
        gaps.append(f"prep-manifest missing at {manifest_rel}")
        census_verdict, census_rows = check_census(
            (slug_dir or (root / "entries" / slug)) / "submission-requirements.json",
            parse_instant((timebox or {}).get("wall")))
        gate = {
            "state": "PREP_INCOMPLETE",
            "evaluated_at": iso(evaluated_at),
            "verified_at": None,
            "stages": stages,
            "census": census_verdict,
            "gaps": gaps,
        }
        return gate, None, census_rows

    manifest = load_json(slug_dir / "prep-manifest.json") or {}
    mstages = manifest.get("stages") or {}
    for s in "01234":
        entry = mstages.get(s) or {}
        artifact = entry.get("artifact")
        if not artifact:
            stages[s] = {"state": NOT_ESTABLISHED,
                         "gap": f"manifest stage {s} names no artifact"}
            gaps.append(f"stage {s}: manifest names no artifact")
            continue
        apath = root / artifact
        if not apath.is_file():
            stages[s] = {"state": NOT_ESTABLISHED, "artifact": artifact,
                         "gap": f"manifest artifact missing on disk: {artifact}"}
            gaps.append(f"stage {s}: artifact missing: {artifact}")
            continue
        stages[s] = {
            "state": "RECEIPTED",
            "artifact": artifact,
            "sha256": sha256_file(apath),
            "size": apath.stat().st_size,
            "receipt_ref": entry.get("receipt_ref"),
        }

    # Stage 0 extra rails: ledger row or coordinator registration, and a
    # resolvable priority_timebox.
    if stages["0"]["state"] == "RECEIPTED":
        rows = ledger_rows_for(ledger, opp["id"])
        reg = coordinator_registered(record)
        stages["0"]["ledger_rows"] = rows if rows else NOT_ESTABLISHED
        stages["0"]["coordinator_registered"] = reg
        if not rows and not reg:
            stages["0"] = {"state": NOT_ESTABLISHED,
                            "artifact": stages["0"].get("artifact"),
                            "gap": "no opportunity_ledger row naming the event and "
                                   "coordinator registration (dates+prizes) not established"}
            gaps.append("stage 0: no ledger row and coordinator registration not established")
        if timebox is None:
            stages["0"] = {"state": NOT_ESTABLISHED,
                            "artifact": stages["0"].get("artifact") if isinstance(stages.get("0"), dict) else None,
                            "gap": "priority_timebox not resolvable"}
            gaps.append("stage 0: priority_timebox not resolvable")

    wall = parse_instant((timebox or {}).get("wall"))
    census_verdict, census_rows = check_census(
        slug_dir / "submission-requirements.json", wall)
    if census_verdict["state"] != "PASS":
        gaps.append(f"census {census_verdict['state']}: " + "; ".join(census_verdict["violations"]))

    complete = all(stages[s]["state"] == "RECEIPTED" for s in "01234") \
        and census_verdict["state"] == "PASS"
    gate = {
        "state": "PASS" if complete else "PREP_INCOMPLETE",
        "evaluated_at": iso(evaluated_at),
        "verified_at": iso(clock.stamp()) if complete else None,
        "stages": stages,
        "census": census_verdict,
        "gaps": gaps,
    }
    return gate, manifest, census_rows


# ---------------------------------------------------------------- selection
def _recency_score(days):
    if days is None:
        return 1
    if days <= 7:
        return 5
    if days <= 14:
        return 4
    if days <= 30:
        return 3
    if days <= 60:
        return 2
    return 1


def _proximity_score(days_to_gate):
    if days_to_gate is None:
        return 1
    if days_to_gate <= 3:
        return 5
    if days_to_gate <= 7:
        return 4
    if days_to_gate <= 14:
        return 3
    if days_to_gate <= 30:
        return 2
    return 1


def _completeness_score(frac):
    return 1 + round(4 * frac)


def _days_between(a: datetime, b: datetime) -> float:
    return round((b - a).total_seconds() / 86400.0, 2)


def delphi_selection(ctx, days_to_gate, now: datetime):
    """Rubric-panel selection over the open completion legs.
    ctx: {dataset_date, settlement_date, snapshot_date, stage_ok{2,3,4},
          book_subjects (int), ledger_rows (list), coverage (bool),
          snapshot (bool), stage1_ok (bool)}"""
    legs = {}
    completeness_inputs = {
        "tournament-update": [ctx["stage_ok"].get("2", False),
                              ctx["stage_ok"].get("3", False),
                              ctx["stage_ok"].get("4", False)],
        "moneyball-update": [ctx["book_subjects"] > 0,
                             len(ctx["ledger_rows"]) > 0,
                             ctx["settlement_date"] is not None],
        "osint-refresh": [ctx["coverage"], ctx["snapshot"], ctx["stage1_ok"]],
    }
    recency_dates = {
        "tournament-update": ctx["dataset_date"],
        "moneyball-update": ctx["settlement_date"] or ctx["dataset_date"],
        "osint-refresh": ctx["snapshot_date"],
    }
    for leg in COMPLETION_LEGS:
        inputs = completeness_inputs[leg]
        frac = sum(1 for x in inputs if x) / len(inputs)
        rdate = recency_dates[leg]
        rdays = _days_between(rdate, now) if rdate else None
        legs[leg] = {
            "evidence_recency": _recency_score(rdays),
            "gate_proximity": _proximity_score(days_to_gate),
            "completeness": _completeness_score(frac),
            "completeness_inputs": inputs,
            "execution": "specified_not_run",
            "execution_reason": "cycle stamps selection only; execution rides the "
                                "entry's own lane — no external writes or inference in-cycle",
        }
        legs[leg]["total"] = (legs[leg]["evidence_recency"]
                              + legs[leg]["gate_proximity"]
                              + legs[leg]["completeness"])
    selected = None
    for leg in COMPLETION_LEGS:  # fixed order -> deterministic ties
        if selected is None or legs[leg]["total"] > legs[selected]["total"]:
            selected = leg
    return {
        "method": "rubric-panel (delphi-gate pattern)",
        "candidates": COMPLETION_LEGS,
        "scores": legs,
        "selected": selected,
    }


# ---------------------------------------------------------------- stages 5-7
def stage5_fold(root: Path, opp_id: str, manifest, ledger):
    manifest = manifest or {}
    pin_entry = (manifest.get("stages") or {}).get("2") or {}
    pin = None
    artifact = pin_entry.get("artifact")
    if artifact and (root / artifact).is_file():
        data = load_json(root / artifact) or {}
        pin = {
            "path": artifact,
            "version": data.get("version") or Path(artifact).stem,
            "sha256": sha256_file(root / artifact),
        }
    book = load_json(root / "ops/agentic-gambling/book/challenges-book.json") or {}
    subjects = []
    for subj in book.get("subjects", []):
        if str(subj.get("id", "")).startswith(opp_id + "-"):
            subjects.append({
                "id": subj.get("id"),
                "subject": subj.get("subject"),
                "knowable": subj.get("knowable"),
                "settle": subj.get("settle"),
                "expectation_record": subj.get("expectation_record"),
            })
    settlements = [s for s in book.get("settlements", [])
                   if any(s.get("subject_id") == sub["id"] for sub in subjects)]
    return {
        "state": "RECEIPTED" if pin else NOT_ESTABLISHED,
        "dataset_pin": pin or NOT_ESTABLISHED,
        "book_subjects": subjects,
        "book_settlements": settlements,
        "opportunity_ledger_rows": ledger_rows_for(ledger, opp_id) or NOT_ESTABLISHED,
    }, subjects, settlements


def stage6_mirror(root: Path, slug: str, opp_id: str):
    fdir = root / "experiments/doe/panel-judge-mirror/forecasts"
    matches = []
    if fdir.is_dir():
        for f in fdir.glob("*.json"):
            if slug in f.name or opp_id.lower() in f.name:
                layer = re.search(r"-L(\d+)", f.name)
                matches.append((int(layer.group(1)) if layer else 0, f))
    if not matches:
        return {"state": NOT_ESTABLISHED,
                "gap": f"no panel-judge-mirror forecast names {opp_id}"}
    matches.sort(key=lambda x: (x[0], x[1].name))
    latest = matches[-1][1]
    data = load_json(latest) or {}
    forecast = data.get("forecast") or {}
    return {
        "state": "RECEIPTED",
        "file": f"experiments/doe/panel-judge-mirror/forecasts/{latest.name}",
        "forecast_id": data.get("forecast_id"),
        "filed_at": data.get("filed_at"),
        "stamp": data.get("stamp"),
        "expected_panel_score": forecast.get("expected_panel_score"),
        "outcome_probabilities": forecast.get("outcome_probabilities"),
        "re_run": {"state": "specified_not_run",
                   "reason": "cycle runs no inference; re-runs ride the Panel Judge Mirror lane"},
    }


def stage7_outcomes(subjects, settlements):
    receipts = [{"subject_id": s.get("subject_id"), "outcome": s.get("outcome"),
                 "value": s.get("value"), "settled_at": s.get("settled_at")}
                for s in settlements]
    pending = [sub for sub in subjects
               if "placement" in str(sub.get("id", ""))
               and str(sub.get("knowable", "")).startswith(NOT_ESTABLISHED)]
    if receipts and not pending:
        return {"state": "RECEIPTED", "outcome_receipts": receipts}
    blocker = None
    if pending:
        blocker = (f"placement outcome not yet knowable — book subject "
                   f"{pending[0]['id']} knowable: {pending[0]['knowable']}")
    elif not receipts:
        blocker = "no outcome receipts exist for this entry yet"
    return {"state": "PENDING", "outcome_receipts": receipts, "blocker": blocker}


# ---------------------------------------------------------------- cycle
def run_cycle(root: Path, *, cycles_dir: Path, cycle_ledger: Path, feed_out: Path,
              now: datetime | None = None, run_id: str = "local"):
    root = Path(root)
    clock = StampClock(fixed=now)
    started = clock.stamp()
    now_ref = now or started

    coordinator = load_json(root / "ops/challenge/coordinator.json") or {}
    ledger = load_json(root / "ops/challenge/opportunity_ledger.json")
    desk_feed = load_json(root / "ops/challenge/desk-feed.json")
    timeboxes = deskfeed_timeboxes(desk_feed)
    tiers_doc = load_json(root / "ops/quota/dispatch-tiers.json") or {}
    chain_entries = {str(c.get("entry", "")).lower()
                     for c in tiers_doc.get("chains", [])}
    coverage = load_json(root / "ops/challenge/osint/coverage.json") or {}
    coverage_events = coverage.get("events") or {}
    snapshots = load_json(root / "ops/challenge/osint/snapshots.json") or {}
    snap_by_event = {}
    for snap in snapshots.get("snapshots", []):
        ev = snap.get("event")
        if ev and (ev not in snap_by_event
                   or str(snap.get("fetched_at", "")) > str(snap_by_event[ev].get("fetched_at", ""))):
            snap_by_event[ev] = snap
    podium_files = sorted((root / "ops/challenge-recruitment").glob("podium-dataset--*.json")) \
        if (root / "ops/challenge-recruitment").is_dir() else []
    podium_latest = None
    if podium_files:
        pdata = load_json(podium_files[-1]) or {}
        podium_latest = {
            "path": str(podium_files[-1].relative_to(root)),
            "version": pdata.get("version") or podium_files[-1].stem,
        }
    entries_dir = root / "entries"

    # ---- phase 1: ingest + gates + timeboxes
    opps = []
    for ev in coordinator.get("events", []):
        if is_live_event(ev):
            opps.append(("event", ev))
    for cand in coordinator.get("candidate_events", []):
        if is_live_candidate(cand):
            opps.append(("candidate", cand))

    records = []
    for kind, record in opps:
        opp_id = str(record.get("id"))
        slug, slug_dir = resolve_slug(entries_dir, opp_id)
        gate_at, gate_src = find_next_gate(record)
        pt = timeboxes.get(opp_id)
        if pt is not None:
            timebox = normalize_timebox(pt, gate_at)
        elif gate_at is not None:
            timebox = derive_timebox(gate_at)
        else:
            timebox = None
        snap = snap_by_event.get(opp_id)
        records.append({
            "id": opp_id,
            "kind": kind,
            "record": record,
            "slug": slug,
            "slug_dir": slug_dir,
            "gate_at": gate_at,
            "gate_src": gate_src,
            "timebox": timebox,
            "ingest": {
                "id": opp_id,
                "kind": kind,
                "name": record.get("name"),
                "state": record.get("status"),
                "source": "ops/challenge/coordinator.json",
                "source_sha256": canonical_sha(record),
                "ingested_at": iso(clock.stamp()),
                "slug": slug,
                "osint_snapshot": ({"fetched_at": snap.get("fetched_at"),
                                    "sha256": snap.get("sha256")}
                                   if snap else NOT_ESTABLISHED),
                "podium_dataset": podium_latest or NOT_ESTABLISHED,
            },
        })

    # ---- phase 2: prep gates
    for rec in records:
        gate, manifest, _census = verify_prep(
            root, rec["ingest"], rec["record"], rec["slug"], rec["slug_dir"],
            rec["timebox"], ledger, clock)
        rec["prep_gate"] = gate
        rec["manifest"] = manifest

    # ---- phase 3: QUE priority stamps + feed
    def sort_key(rec):
        return (rec["gate_at"] is None, rec["gate_at"] or datetime.max.replace(tzinfo=timezone.utc), rec["id"])

    records.sort(key=sort_key)
    feed_opps = []
    for rank, rec in enumerate(records, start=1):
        days_to_gate = _days_between(now_ref, rec["gate_at"]) if rec["gate_at"] else None
        gate_term_days = days_to_gate
        if gate_term_days is None:
            gate_term = 0.0
        elif gate_term_days <= 0:
            gate_term = 1.0
        elif gate_term_days <= 3:
            gate_term = 0.9
        elif gate_term_days <= 7:
            gate_term = 0.75
        elif gate_term_days <= 14:
            gate_term = 0.6
        elif gate_term_days <= 30:
            gate_term = 0.45
        elif gate_term_days <= 60:
            gate_term = 0.3
        else:
            gate_term = 0.15
        prep_complete = rec["prep_gate"]["state"] == "PASS"
        prep_term = 0.05 if prep_complete else 0.2
        tier = 2 if rec["slug"] in chain_entries else 3
        basis = [
            f"next_gate {iso(rec['gate_at']) if rec['gate_at'] else NOT_ESTABLISHED} "
            f"via {rec['gate_src'] or 'none'} -> gate_term {gate_term}",
            f"prep {'complete' if prep_complete else 'incomplete'} -> prep_term {prep_term}",
            f"tier {tier} ({'dispatch-tiers chain entry' if tier == 2 else 'default build class'})",
        ]
        rec["priority_stamp"] = {
            "rank": rank,
            "tier": tier,
            "score": round(100 * (gate_term + prep_term), 1),
            "basis": basis,
            "next_gate": iso(rec["gate_at"]) if rec["gate_at"] else NOT_ESTABLISHED,
            "next_gate_source": rec["gate_src"],
            "days_to_gate": days_to_gate,
            "priority_timebox": rec["timebox"] or NOT_ESTABLISHED,
            "stamped_at": iso(clock.stamp()),
        }
        feed_opps.append({
            "id": rec["id"],
            "slug": rec["slug"],
            "rank": rank,
            "tier": tier,
            "score": rec["priority_stamp"]["score"],
            "basis": basis,
            "next_gate": rec["priority_stamp"]["next_gate"],
            "days_to_gate": days_to_gate,
            "priority_timebox": rec["priority_stamp"]["priority_timebox"],
            "prep_state": rec["prep_gate"]["state"],
            "verdict": None,  # filled in phase 4
        })
        rec["feed_row"] = feed_opps[-1]

    # ---- phase 4: selection + stages 5-7 + tier actions (gated-in only)
    for rec in records:
        gate = rec["prep_gate"]
        if gate["state"] != "PASS":
            rec["selection"] = {"state": "blocked_prep_incomplete"}
            rec["stages"] = {s: {"state": "blocked_prep_incomplete"} for s in "567"}
            rec["tier_actions"] = []
            rec["verdict"] = "PREP_INCOMPLETE"
            rec["feed_row"]["verdict"] = "PREP_INCOMPLETE"
            continue
        verified_at = gate["verified_at"]
        stage_ok = {s: gate["stages"][s]["state"] == "RECEIPTED" for s in "01234"}
        dataset_date = None
        if rec["manifest"]:
            ver = None
            pin_path = ((rec["manifest"].get("stages") or {}).get("2") or {}).get("artifact")
            if pin_path:
                pdata = load_json(root / pin_path) or {}
                ver = str(pdata.get("version") or "")
                m = re.match(r"^(\d{4}-\d{2}-\d{2})", ver)
                if m:
                    dataset_date = parse_instant(m.group(1))
        s5, subjects, settlements = stage5_fold(root, rec["id"], rec["manifest"], ledger)
        settle_dates = [parse_instant(s.get("settled_at")) for s in settlements]
        settle_dates = [d for d in settle_dates if d]
        snap = snap_by_event.get(rec["id"])
        snap_date = parse_instant(snap.get("fetched_at")) if snap else None
        ctx = {
            "dataset_date": dataset_date,
            "settlement_date": max(settle_dates) if settle_dates else None,
            "snapshot_date": snap_date,
            "stage_ok": stage_ok,
            "book_subjects": len(subjects),
            "ledger_rows": ledger_rows_for(ledger, rec["id"]),
            "coverage": rec["id"] in coverage_events,
            "snapshot": snap is not None,
            "stage1_ok": stage_ok.get("1", False),
        }
        days_to_gate = rec["priority_stamp"]["days_to_gate"]
        tier_actions = []

        selection = delphi_selection(ctx, days_to_gate, now_ref)
        tier_actions.append({"action": "delphi_selection", "ts": iso(clock.stamp())})
        s6 = stage6_mirror(root, rec["slug"], rec["id"])
        tier_actions.append({"action": "stage5_fold", "ts": iso(clock.stamp())})
        tier_actions.append({"action": "stage6_read", "ts": iso(clock.stamp())})
        s7 = stage7_outcomes(subjects, settlements)
        tier_actions.append({"action": "stage7_stamp", "ts": iso(clock.stamp())})

        for action in tier_actions:  # invariant, enforced
            assert action["ts"] > verified_at, \
                f"tier action {action['action']} ts {action['ts']} <= prep verified_at {verified_at}"
        rec["selection"] = selection
        rec["stages"] = {"5": s5, "6": s6, "7": s7}
        rec["tier_actions"] = tier_actions
        rec["verdict"] = "COMPLETE"
        rec["feed_row"]["verdict"] = "COMPLETE"

    finished = clock.stamp()
    cycle_id = f"cyc-{started.strftime('%Y%m%dT%H%M%SZ')}-{re.sub(r'[^A-Za-z0-9_-]', '-', str(run_id))}"
    receipt = {
        "schema": "opportunity-cycle/v1",
        "cycle_id": cycle_id,
        "run_id": run_id,
        "started_at": iso(started),
        "finished_at": iso(finished),
        "ingest": [rec["ingest"] for rec in records],
        "priority_feed_ref": str(feed_out),
        "opportunities": [{
            "id": rec["id"],
            "slug": rec["slug"],
            "priority_stamp": rec["priority_stamp"],
            "prep_gate": rec["prep_gate"],
            "selection": rec["selection"],
            "stages": rec["stages"],
            "tier_actions": rec["tier_actions"],
            "verdict": rec["verdict"],
        } for rec in records],
        "doe_stamp": {
            "task_class": "opportunities-cycle",
            "arm": "repo-machinery",
            "provider": "github-actions",
            "model": None,
            "run_id": run_id,
            "outcome": "success",
            "cost_class": "actions-free",
        },
    }
    feed = {
        "schema": "que.opportunity-priority/v1",
        "generated_at": iso(finished),
        "run_id": run_id,
        "opportunities": feed_opps,
    }

    cycles_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = cycles_dir / f"{cycle_id}.json"
    with open(receipt_path, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2)
        fh.write("\n")
    feed_out.parent.mkdir(parents=True, exist_ok=True)
    with open(feed_out, "w", encoding="utf-8") as fh:
        json.dump(feed, fh, indent=2)
        fh.write("\n")
    cycle_ledger.parent.mkdir(parents=True, exist_ok=True)
    with open(cycle_ledger, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({
            "cycle_id": cycle_id,
            "run_id": run_id,
            "started_at": iso(started),
            "finished_at": iso(finished),
            "verdicts": {rec["id"]: rec["verdict"] for rec in records},
            "receipt": str(receipt_path),
            "priority_feed": str(feed_out),
        }) + "\n")
    receipt["_paths"] = {"receipt": str(receipt_path), "feed": str(feed_out),
                         "cycle_ledger": str(cycle_ledger)}
    return receipt


def main(argv=None):
    ap = argparse.ArgumentParser(description="Opportunity self-eval cycle (#5096)")
    default_root = Path(__file__).resolve().parents[2]
    ap.add_argument("--root", default=str(default_root))
    ap.add_argument("--cycles-dir", default=None)
    ap.add_argument("--cycle-ledger", default=None)
    ap.add_argument("--feed-out", default=None)
    ap.add_argument("--now", default=None, help="ISO instant override (tests/dry-runs)")
    ap.add_argument("--run-id", default=None)
    args = ap.parse_args(argv)

    root = Path(args.root)
    now = parse_instant(args.now) if args.now else None
    run_id = args.run_id or os.environ.get("GITHUB_RUN_ID") or "local"
    cycles_dir = Path(args.cycles_dir) if args.cycles_dir else root / "ops/opportunities/cycles"
    cycle_ledger = Path(args.cycle_ledger) if args.cycle_ledger else root / "ops/opportunities/cycle-ledger.jsonl"
    feed_out = Path(args.feed_out) if args.feed_out else root / "ops/que/feeds/opportunity-priority.json"
    receipt = run_cycle(root, cycles_dir=cycles_dir, cycle_ledger=cycle_ledger,
                        feed_out=feed_out, now=now, run_id=run_id)
    verdicts = {o["id"]: o["verdict"] for o in receipt["opportunities"]}
    print(json.dumps({"cycle_id": receipt["cycle_id"], "verdicts": verdicts}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
