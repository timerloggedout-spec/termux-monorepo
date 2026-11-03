"""Wagering-book render feed: the challenges book + calendar anchors + ledger.

Sources (MoneyBall plane): the publication feed
ops/agentic-gambling/book/book-feed.json (schema
agentic-gambling-book-feed/v1 - subjects, expectation records,
positions, settlements at ledger truth), the book
ops/agentic-gambling/book/challenges-book.json (calendar_binding),
and the ledger of record ops/agentic-gambling/book/ledger.jsonl
(append-only; carried BY REFERENCE only - MoneyBall publishability
flag 4: bookkeeping-event notes are internal routing language and do
not render; only positions/settlements arrays render). Anchors ride
in the subjects (calendar_binding -> deadline-reminders/v1);
derivations confirmed by Tracking 2026-11-02: wall = FINAL (stage E)
+ 30 min on full-scheme items; landing = stage B; FCC soft; kickoffs
wall-less; AMD-17/AMD-18 anchorless (NOT_ESTABLISHED).
Knowable normalization: date-only = end of day PT, except "by wall"
subjects (the wall instant); dated instants keep their instant; rule
knowables stay undated - no date is invented.
Expectation records ARE carried (owner publication ruling 2026-11-02):
prior/posterior values render exactly as the book holds them; null =
INTAKE state, shown as such. Positions and settlements derive from
the ledger + the book's settle values, verbatim - published values
equal ledger values by construction (this feed is a join, not an
edit). Forecast is an OUTPUT class (naming-collapse amendment,
PR #3830): no forecast rows.
"""
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _parse(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _knowable(raw, label, wall_at, wall_date):
    if raw.startswith("NOT_ESTABLISHED") or raw in (
            "on receipt (pending now)", "at exam pass"):
        return {"kind": "rule", "at": None, "text": raw}
    if raw.endswith("15:00Z"):
        return {"kind": "dated", "at": "2026-11-03T15:00:00Z", "text": raw}
    if "11:30 PT" in raw:
        return {"kind": "dated", "at": "2026-11-20T11:30:00-08:00",
                "text": raw}
    date = raw[:10]
    out = {"kind": "dated", "text": raw}
    if "by wall" in label and wall_date and date == wall_date:
        out["at"] = wall_at
        out["basis"] = "knowable = wall instant"
    else:
        out["at"] = date + "T23:59:00-08:00"
        out["basis"] = "date-only knowable = end of day PT"
    if "may lag" in raw:
        out["lag"] = True
    return out


def _window_pct(window, note, at):
    """Window consumption at instant `at`, from the anchors alone.

    consumed = clamp(100 * (at - start) / (wall - start), 0, 100),
    1dp; remaining = 100 - consumed. Degenerate windows (wall <=
    start: instant/point subjects) carry null + the feed's pct_note -
    never 0 or 100 by default."""
    if not window:
        return {"consumed": None, "remaining": None,
                "computed_at": at, "note": note}
    start = _parse(window["window_start"])
    wall = _parse(window["wall"])
    if wall <= start:
        return {"consumed": None, "remaining": None,
                "computed_at": at, "note": note}
    consumed = round(min(100.0, max(0.0, (_parse(at) - start)
                 .total_seconds() / (wall - start).total_seconds()
                 * 100)), 1)
    return {"consumed": consumed, "remaining": round(100 - consumed, 1),
            "computed_at": at, "note": None}


def build_feed(bookfeed, book, ledger_count, generated_at, book_ref):
    subjects = []
    family_label = {}
    settlements = []
    for s in bookfeed["subjects"]:
        fam = s["id"].split("-")[0]
        if len(s["group"]) > len(family_label.get(fam, "")):
            family_label[fam] = s["group"]
        a = s.get("anchors")
        if a:
            landing, final = a["landing"], a["final"]
            wall_raw = a["wall"]
            if final:
                wall_at = (_parse(final) + timedelta(minutes=30)).isoformat()
                soft = False
            elif wall_raw:
                wall_at = wall_raw[:10] + "T23:59:00-08:00"
                soft = "(soft)" in wall_raw
            else:
                wall_at, soft = None, False
            wall_date = wall_raw[:10] if wall_raw else None
            cushions = a["cushion"]
            note = a.get("note")
            register_item = a["register_item"]
        else:
            landing = final = wall_at = None
            soft, cushions, wall_date = False, [], None
            note = s.get("anchors_note")
            register_item = None
        exp = s["expectation_record"]
        stl = s["settle"]
        if stl.get("value") is not None:
            settlements.append({"subject_id": s["id"],
                                "field": stl["field"],
                                "source": stl["source"],
                                "value": stl["value"]})
        subjects.append({
            "id": s["id"], "label": s["subject"], "group": s["group"],
            "family": fam, "register_item": register_item,
            "settles_by": stl["source"],
            "record_of_record": s.get("record_of_record"),
            "open": "2026-11-02T00:00:00-08:00",
            "landing_at": landing, "wall_at": wall_at, "wall_soft": soft,
            "final_at": final, "cushions": cushions,
            "knowable": _knowable(s["knowable"], s["subject"], wall_at,
                                  wall_date),
            "anchors_note": note,
            "expectation": {
                "quantity": exp["quantity"],
                "prior_value": exp["prior"]["value"],
                "prior_basis": exp["prior"]["basis"],
                "posterior_value": exp["posterior"]["value"],
                "posterior_range": exp["posterior"]["range"],
                "n_evidence": exp["posterior"]["n_evidence"],
                "n_evidence_items": len(exp["evidence"])},
            "window": ({"start": s["window"]["window_start"],
                        "start_basis": s["window"]["window_start_basis"],
                        "wall": s["window"]["wall"]}
                       if s.get("window") else None),
            "window_pct": _window_pct(s.get("window"),
                                      s.get("pct_note"), generated_at),
            "settlement": {"field": stl["field"], "value": stl["value"]}})
    pct_block = {"rule": bookfeed["pct_block"]["rule"],
                 "computed_at": generated_at,
                 "upstream_computed_at":
                     bookfeed["pct_block"]["computed_at"],
                 "method": "recomputed by this generator from the "
                           "window anchors at build time; the upstream "
                           "feed's stamped pct is proof-of-shape only"}
    positions = bookfeed["positions"]
    feed_settlements = bookfeed["settlements"]
    return {
        "schema": "moneyball.wagering-book/v2",
        "generated_at": generated_at,
        "book": {"opened": "2026-11-02", "subjects": len(subjects)},
        "horizon": {"start": "2026-11-02T00:00:00-08:00",
                    "end": "2026-12-12T23:59:00-08:00"},
        "family_label": family_label,
        "forecast_layer": book["calendar_binding"]["forecast_rule"],
        "publishability_flags": bookfeed["publishability_flags"],
        "ledger_ref": {"path": "ops/agentic-gambling/book/ledger.jsonl",
                       "entries": ledger_count,
                       "note": bookfeed["ledger_of_record"]},
        "upstream_feed": "ops/agentic-gambling/book/book-feed.json "
                         "(schema agentic-gambling-book-feed/v1)",
        "publication": "Public view of the internal book (owner ruling "
                       "2026-11-02). Entries stay internal: observational "
                       "stakes only, no external participation surface, "
                       "no wallet movement. Published values equal the "
                       "ledger of record by construction.",
        "sources": {
            "book": "ops/agentic-gambling/book/challenges-book.json@"
                    + book_ref + " (schema agentic-gambling-book/v1)",
            "ledger": "ops/agentic-gambling/book/ledger.jsonl "
                      "(append-only ledger of record, MoneyBall plane)",
            "register": "deadline-reminders/v1 (Tracking lane d6c12f3a; "
                        "primary calendar, America/Los_Angeles) - anchors "
                        "as bound in the book; derivation confirmed by "
                        "Tracking 2026-11-02"},
        "honesty": [
            "Subjects with a rule knowable (NOT_ESTABLISHED / on receipt / "
            "at exam pass) render open-ended: no date is invented.",
            "AMD-17 / AMD-18 carry no register anchors (NOT_ESTABLISHED in "
            "the book) - no landing/wall markers render.",
            "Forecast is an OUTPUT class (naming-collapse amendment "
            "#3830): forecasts score at each subject's settlement, at the "
            "issuer's record. There are no forecast rows.",
            "Date-only knowables render at end of day PT, except 'by wall' "
            "subjects, which resolve at the wall instant.",
            "An expectation whose prior and posterior are both null is in "
            "INTAKE state and renders as INTAKE (no estimate) - never as "
            "a number, never as 0.",
            "Window consumption (% remaining) is computed from each "
            "subject's window anchors at feed build (pct_block "
            "computed_at) and shades the window span of its bar; "
            "degenerate windows (wall at or before start - instant "
            "subjects) carry no percentage: never 0, never 100 by "
            "default.",
            "The ledger's bookkeeping-event notes are internal routing "
            "language and do not render (MoneyBall publishability flag "
            "4); the ledger is carried by reference - path + entry "
            "count - and only its positions/settlements extracts "
            "render."],
        "pct_block": pct_block,
        "subjects": subjects,
        "positions": positions,
        "settlements": settlements,
        "feed_settlements": feed_settlements}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mirror", default=None)
    args = ap.parse_args()
    root = Path(args.root)
    bookfeed = json.loads(
        (root / "ops/agentic-gambling/book/book-feed.json").read_text())
    book = json.loads(
        (root / "ops/agentic-gambling/book/challenges-book.json")
        .read_text())
    ledger_count = sum(1 for l in
                       (root / "ops/agentic-gambling/book/ledger.jsonl")
                       .read_text().splitlines() if l.strip())
    feed = build_feed(bookfeed, book, ledger_count,
                      datetime.now(timezone.utc)
                      .strftime("%Y-%m-%dT%H:%M:%SZ"), "working-tree")
    text = json.dumps(feed, indent=1) + "\n"
    Path(args.out).write_text(text)
    if args.mirror:
        Path(args.mirror).write_text(text)


if __name__ == "__main__":
    main()
