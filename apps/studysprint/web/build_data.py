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

from study_reader import Section  # noqa: E402
from study_sr import build_cards_from_practice_set, export_ux_state  # noqa: E402
from study_tools import (build_study_plan, fetch_study_evidence,  # noqa: E402
                         format_trust_receipt, render_today_view)


def emit_state(root: Path | None = None) -> dict:
    root = root or APP_ROOT
    syllabus = json.loads((root / "examples" / "syllabus.json")
                          .read_text())
    practice = json.loads((root / "examples" / "practice_set.json")
                          .read_text())
    evidence = fetch_study_evidence(
        {"kind": "syllabus", "ref": "examples/syllabus.json"}, root=root)
    plan = build_study_plan(syllabus)
    cards = build_cards_from_practice_set(practice)
    ux = export_ux_state(cards, {})
    sections = []
    for w in syllabus.get("weeks") or []:
        for topic in w.get("topics") or []:
            text = (f"{topic}. " + " ".join(
                q["q"] + " " + q["a"]
                for q in practice.get("questions") or []))
            sections.append({"title": topic,
                             "chapter": f"Week {w.get('week')}",
                             "text": text,
                             "words": Section(
                                 section_id="tmp", title=topic,
                                 content=text).tokens})
    version_file = WEB_DIR / "VERSION"
    return {
        "plan_start": date.today().isoformat(),
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
