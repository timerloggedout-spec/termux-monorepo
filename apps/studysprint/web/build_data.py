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


def _memory_bundle(plan: dict, sections: list,
                   calendar_geo: dict | None) -> dict:
    """Memory-methods bundle (parity iteration 2, #4415).

    Palace: iteration 1's temple route IS the course's palace —
    core-built placements over the student's real walk — so it
    binds directly; without one, the core builds a palace over
    the plan's topics on its default route. Feynman evidence:
    the reader sections are the verified text an explanation is
    graded against on this surface (the sample's sections are
    the course's own readings)."""
    from study_memory import LOCI_CLAIMS_CEILING, LOCI_EVIDENCE, \
        build_palace
    temple = (calendar_geo or {}).get("temple_route") or {}
    if temple.get("placements"):
        palace = {
            "placements": temple["placements"],
            "route": [p["locus"] for p in temple["placements"]],
            "claims_ceiling": temple.get("claims_ceiling")
            or LOCI_CLAIMS_CEILING,
            "evidence": LOCI_EVIDENCE,
            "source": "temple-route",
        }
    else:
        chapters, items = [], {}
        for w in plan.get("weeks") or []:
            title = f"Week {w.get('week')}"
            topics: list = []
            for s in w.get("sessions") or []:
                if s["topic"] not in topics:
                    topics.append(s["topic"])
            chapters.append(title)
            items[title] = topics
        palace = {**build_palace(chapters, items),
                  "source": "default-route"}
    return {
        "palace": palace,
        "feynman_topics": [
            {"topic": s["title"], "chapter": s["chapter"],
             "evidence": s["text"]} for s in sections],
    }


def _course_bundle(root: Path, stem: str) -> dict:
    """One course's full surface bundle (parity iteration 3,
    #4416: the emit that used to be the whole state, now per
    course). `stem` names the examples file set: '' for the first
    sample (syllabus.json), '_stats' for the second
    (syllabus_stats.json, STAT 210)."""
    syllabus = json.loads((root / "examples" / f"syllabus{stem}.json")
                          .read_text())
    practice = json.loads((root / "examples" / f"practice_set{stem}.json")
                          .read_text())
    evidence = fetch_study_evidence(
        {"kind": "syllabus", "ref": f"examples/syllabus{stem}.json"},
        root=root)
    plan = build_study_plan(syllabus)
    cards = build_cards_from_practice_set(practice)
    ux = export_ux_state(cards, {})
    # Per-topic reading passages: authored example content, one
    # passage per syllabus topic, so a section titled for a topic
    # actually teaches that topic (#4230). Real courses get their
    # sections from the ingested course text.
    readings = {}
    readings_file = root / "examples" / f"readings{stem}.json"
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
            stem_word = topic.lower().rstrip("s").split()[-1]
            checks = [q for q in practice.get("questions") or []
                      if stem_word in (q["q"] + " " + q["a"]).lower()]
            if checks:
                text += "\n\nCheck yourself: " + " ".join(
                    q["q"] + " " + q["a"] for q in checks)
            sections.append({"title": topic,
                             "chapter": f"Week {w.get('week')}",
                             "text": text,
                             "words": Section(
                                 section_id="tmp", title=topic,
                                 content=text).tokens})
    # Calendar + geography (parity iteration 1, #4414): the same
    # core assembler the TUI runs live; here it is computed at
    # build time like the rest of the bundle's state (the APK
    # disclosure covers it: state as of the build).
    from datetime import datetime, timezone
    calendar_geo = None
    calendar_error = None
    calendar_file = root / "examples" / f"calendar{stem}.json"
    if calendar_file.exists():
        topics = [t for w in syllabus.get("weeks") or []
                  for t in w.get("topics") or []]
        try:
            calendar_geo = surface_calendar_geo(
                json.loads(calendar_file.read_text()),
                datetime.now(timezone.utc), topics=topics)
        except ValueError as e:
            # The core calendar intake refuses this course's
            # calendar (e.g. an assessment kind outside its
            # enum): the refusal is recorded on the bundle, the
            # course still ships -- never a silent drop, never a
            # whole-build crash for one course's calendar.
            calendar_error = str(e)
    return {
        "course": syllabus.get("course"),
        "syllabus": syllabus,
        "plan": plan,
        "trust_receipt": format_trust_receipt(evidence),
        "today": render_today_view(plan),
        "sr": {"cards": [c.to_dict() for c in cards],
               "ux_state": ux},
        "reader": {"sections": sections},
        "calendar_geo": calendar_geo,
        "calendar_error": calendar_error,
        "memory": _memory_bundle(plan, sections, calendar_geo),
    }


def _book_bundle(root: Path) -> dict:
    """The §1b demonstration book (parity iteration 4, #4417):
    a REAL book — Darwin, On the Origin of Species, 6th edition
    (Project Gutenberg #2009) — ingested through the real core
    pipeline. The bundle carries Chapter XIV (the chapter whose
    own title names Morphology and Embryology, both indexed
    headwords in the book) + the book's complete Glossary and
    Index, cut from the Gutenberg text with typographic
    normalization only (line-wrap joins; the index's comma
    before page numbers dropped) — content verbatim.

    Emits everything the surface renders: the ingest receipt
    counts (terms mined · with definitions · with index refs),
    the reader sections with core-emphasized term segments, a
    tap payload per term (definition · index pages · sections),
    and W3C annotations over the indexed terms, built by the
    core's make_annotation over the book's own sentences."""
    from study_pipeline import (build_term_bank, emphasize_terms,
                                extract_structure, make_annotation,
                                term_tap_payload, to_reader_sections)
    chapter_text = (root / "examples" / "textbook_chapter.txt") \
        .read_text()
    glossary_text = (root / "examples" / "textbook_glossary.txt") \
        .read_text()
    index_text = (root / "examples" / "textbook_index.txt") \
        .read_text()
    structure = extract_structure(chapter_text)
    bank = build_term_bank(structure, glossary_text, index_text)
    flat = [t for ch in bank.get("chapters") or []
            for t in ch.get("terms") or []]
    counts = {
        "terms": len(flat),
        "with_definitions": sum(1 for t in flat
                                if t.get("definition")),
        "with_index_refs": sum(1 for t in flat
                               if t.get("index_pages")),
    }
    sections = []
    for sec in to_reader_sections(structure):
        emph = emphasize_terms(sec.content, bank)
        sections.append({
            "title": sec.title, "chapter": sec.chapter,
            "text": sec.content, "words": sec.tokens,
            "segments": emph["segments"],
            "terms_found": emph["terms_found"],
        })
    taps = {}
    for t in flat:
        taps[t["term"].lower()] = term_tap_payload(t["term"], bank)
    annotations = []
    for t in flat:
        if not t.get("index_pages"):
            continue
        quote = ""
        for sentence in chapter_text[2500:].replace("\n", " ") \
                .split(". "):
            s = sentence.strip()
            if len(s) > 80 and t["term"].lower() in s.lower():
                quote = s.rstrip(".") + "."
                break
        annotations.append(make_annotation(
            "examples/textbook_chapter.txt", quote,
            body_text=(f"Glossary: {t['definition']} "
                       f"(indexed, pages "
                       f"{', '.join(str(p) for p in t['index_pages'])})"),
            tags=["term-bank", "index"]))
    return {
        "source": ("On the Origin of Species, 6th edition "
                   "(Project Gutenberg #2009) — Chapter XIV + "
                   "the book's own Glossary and Index"),
        "counts": counts,
        "receipt": bank["receipt"],
        "sections": sections,
        "taps": taps,
        "annotations": annotations,
        "annotations_note": (
            "Annotations of record over the bundled book, in "
            "the W3C Web Annotation model (the core's "
            "make_annotation). The hypothes.is API leg syncs "
            "these with an account token — not configured on "
            "this surface, so nothing leaves the device."),
    }


def emit_state(root: Path | None = None) -> dict:
    root = root or APP_ROOT
    version_file = WEB_DIR / "VERSION"
    # Multi-course (parity iteration 3, #4416): the surface's
    # course set = both bundled samples, intaken through the REAL
    # core course-set machinery (intake_courses: per-course plans
    # + countdowns + merged totals + conflict flags) with a
    # per-course .ics export (export_ics over a single-course
    # intake). Top-level fields stay the FIRST course's bundle --
    # the back-compat shape every existing view reads; the
    # switcher rebinds them to the active course in the browser.
    from datetime import datetime, timezone

    from study_courses import export_ics, intake_courses
    stems = ["", "_stats"]
    bundles = [_course_bundle(root, s) for s in stems]
    docs = [b["syllabus"] for b in bundles]
    intake = intake_courses(docs, now=datetime.now(timezone.utc))
    plan_start = date.today().isoformat()
    ics_by_course = {}
    for b in bundles:
        single = {"courses": [c for c in intake["courses"]
                               if c["course"] == b["course"]]}
        ics_by_course[b["course"]] = export_ics(single, plan_start)
    first = bundles[0]
    return {
        "plan_start": plan_start,
        "surface": "studysprint-webapp",
        "surface_version": version_file.read_text().strip()
        if version_file.exists() else "0.1.0",
        **{k: first[k] for k in
           ("course", "plan", "trust_receipt", "today", "sr",
            "reader", "calendar_geo", "memory")},
        "courses": bundles,
        "courses_intake": intake,
        "ics_by_course": ics_by_course,
        "book": _book_bundle(root),
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
