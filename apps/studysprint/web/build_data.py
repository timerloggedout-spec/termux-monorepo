"""StudySprint webApp surface — state builder (issue #4092).

Runs the REAL core (plan, trust receipt, today view, SR cards with
the ts-fsrs UX-state export, reader sections) over the bundled
example course and emits `data/state.json`, the exact state shapes
the PWA consumes in the browser. No forked logic: if the core
changes, re-run this builder and the surface state follows.

    python3 build_data.py            # writes data/state.json

Surface version line: independent (see WEBAPP.md / VERSION).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

WEB_DIR = Path(__file__).resolve().parent
APP_ROOT = WEB_DIR.parent
sys.path.insert(0, str(APP_ROOT))

from datetime import date  # noqa: E402

from study_geo import surface_calendar_geo  # noqa: E402
from study_reader import Section  # noqa: E402
from study_sr import build_cards_from_practice_set, export_ux_state  # noqa: E402
from study_tools import (build_study_plan, fetch_study_evidence,  # noqa: E402
                         format_trust_receipt, render_today_view)


def emit_state(root: Path | None = None) -> dict:
    root = root or APP_ROOT
    # Reproducible builds (#4438): STUDYSPRINT_BUILD_NOW pins
    # the state's clock (ISO 8601) and is threaded through every
    # stamped generator, so two builds from the same tree are
    # byte-identical; unset, the state honestly says "as of
    # now" as it always has.
    import os
    from datetime import datetime, timezone
    pinned = os.environ.get("STUDYSPRINT_BUILD_NOW", "").strip()
    now = (datetime.fromisoformat(pinned) if pinned
           else datetime.now(timezone.utc))
    syllabus = json.loads((root / "examples" / "syllabus.json")
                          .read_text())
    practice = json.loads((root / "examples" / "practice_set.json")
                          .read_text())
    evidence = fetch_study_evidence(
        {"kind": "syllabus", "ref": "examples/syllabus.json"},
        now=now, root=root)
    plan = build_study_plan(syllabus)
    cards = build_cards_from_practice_set(practice)
    ux = export_ux_state(cards, {}, now=now)
    # Per-topic reading passages (examples/readings.json): authored
    # example content, one passage per syllabus topic, so a section
    # titled for a topic actually teaches that topic (#4230). Real
    # courses get their sections from the ingested course text.
    readings = {}
    readings_file = root / "examples" / "readings.json"
    if readings_file.exists():
        readings = json.loads(readings_file.read_text())
    sections = []
    for w in syllabus.get("weeks") or []:
        for topic in w.get("topics") or []:
            if readings.get(topic):
                text = readings[topic]
            else:
                # No authored reading: an honest stub naming the
                # topic -- never another topic's content (#4230).
                text = (f"Week {w.get('week')} covers {topic}. The "
                        "full reading for this topic arrives with "
                        "the course text at ingest; the plan, checks "
                        "and reviews for it are live now.")
            stem = topic.lower().rstrip("s").split()[-1]
            checks = [q for q in practice.get("questions") or []
                      if stem in (q["q"] + " " + q["a"]).lower()]
            if checks:
                text += "\n\nCheck yourself: " + " ".join(
                    q["q"] + " " + q["a"] for q in checks)
            sections.append({"title": topic,
                             "chapter": f"Week {w.get('week')}",
                             "text": text,
                             "words": Section(
                                 section_id="tmp", title=topic,
                                 content=text).tokens})
    version_file = WEB_DIR / "VERSION"
    # Calendar + geography (parity iteration 1, #4414): the same
    # core assembler the TUI runs live; here it is computed at
    # build time like the rest of the bundle's state (the APK
    # disclosure covers it: state as of the build).
    calendar_geo = None
    calendar_file = root / "examples" / "calendar.json"
    if calendar_file.exists():
        topics = [t for w in syllabus.get("weeks") or []
                  for t in w.get("topics") or []]
        calendar_geo = surface_calendar_geo(
            json.loads(calendar_file.read_text()),
            now, topics=topics)
    return {
        "plan_start": now.date().isoformat(),
        "surface": "studysprint-webapp",
        "surface_version": version_file.read_text().strip()
        if version_file.exists() else "0.1.0",
        "course": syllabus.get("course"),
        "plan": plan,
        "trust_receipt": format_trust_receipt(evidence),
        "today": render_today_view(plan),
        "sr": {"cards": [c.to_dict() for c in cards],
               "ux_state": ux},
        "reader": {"sections": sections},
        "calendar_geo": calendar_geo,
    }


def stamp_service_worker() -> None:
    """Keep the service worker's cache identity on the surface
    version line (#4219): the cache name carries web/VERSION, so
    a new surface release can never be pinned behind the first
    build's cache. Runs wherever the bundle is (re)built."""
    sw_path = WEB_DIR / "sw.js"
    if not sw_path.exists():
        return
    version = (WEB_DIR / "VERSION").read_text().strip()
    text = sw_path.read_text()
    stamped = re.sub(r"studysprint-webapp-v[0-9.]+",
                     f"studysprint-webapp-v{version}", text)
    if stamped != text:
        sw_path.write_text(stamped)


def main() -> None:
    out = WEB_DIR / "data" / "state.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(emit_state(), indent=1, sort_keys=True))
    stamp_service_worker()
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
