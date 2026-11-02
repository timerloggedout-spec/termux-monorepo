"""Wagering-book render feed: join of the challenges book + its calendar anchors.

Source of subjects: ops/agentic-gambling/book/challenges-book.json
(schema agentic-gambling-book/v1, MoneyBall plane). Anchors ride in the
book (calendar_binding -> deadline-reminders/v1, Tracking lane); the
derivations here were confirmed by Tracking 2026-11-02:
  wall = FINAL (stage E) + 30 min on full-scheme items; landing = stage B;
  FCC items are soft (wall = the soft date, end of day); kickoff items
  carry no wall; AMD-17/AMD-18 carry no anchors (NOT_ESTABLISHED).
Knowable normalization: a date-only knowable resolves at end of day PT,
except "by wall" subjects, which resolve at the wall instant; dated
instants keep their instant; rule knowables (NOT_ESTABLISHED / on
receipt / at exam pass) stay undated - no date is invented.
The book's expectation_record is deliberately NOT carried into this
feed: expectations are the coordinator's internal record, never a
render input. Forecast is an OUTPUT class (naming-collapse amendment,
PR #3830): forecasts score at each subject's settlement, at the
issuer's record. There are no forecast rows.
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


def build_feed(book, generated_at, book_ref):
    subjects = []
    family_label = {}
    for s in book["subjects"]:
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
        subjects.append({
            "id": s["id"], "label": s["subject"], "group": s["group"],
            "family": fam, "register_item": register_item,
            "settles_by": s["settle"]["source"],
            "open": "2026-11-02T00:00:00-08:00",
            "landing_at": landing, "wall_at": wall_at, "wall_soft": soft,
            "final_at": final, "cushions": cushions,
            "knowable": _knowable(s["knowable"], s["subject"], wall_at,
                                  wall_date),
            "anchors_note": note})
    return {
        "schema": "moneyball.wagering-book/v1",
        "generated_at": generated_at,
        "book": {"opened": "2026-11-02", "subjects": len(subjects)},
        "horizon": {"start": "2026-11-02T00:00:00-08:00",
                    "end": "2026-12-12T23:59:00-08:00"},
        "family_label": family_label,
        "forecast_layer": book["calendar_binding"]["forecast_rule"],
        "sources": {
            "book": "ops/agentic-gambling/book/challenges-book.json@"
                    + book_ref + " (schema agentic-gambling-book/v1)",
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
            "subjects, which resolve at the wall instant."],
        "subjects": subjects}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", required=True)
    ap.add_argument("--mirror", default=None)
    args = ap.parse_args()
    root = Path(args.root)
    book = json.loads(
        (root / "ops/agentic-gambling/book/challenges-book.json")
        .read_text())
    feed = build_feed(book, datetime.now(timezone.utc)
                      .strftime("%Y-%m-%dT%H:%M:%SZ"), "working-tree")
    text = json.dumps(feed, indent=1) + "\n"
    Path(args.out).write_text(text)
    if args.mirror:
        Path(args.mirror).write_text(text)


if __name__ == "__main__":
    main()
