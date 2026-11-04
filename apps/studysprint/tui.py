"""StudySprint TUI surface — issue #4095.

A Textual terminal app over the SAME core functions as the CLI
(∅ forked logic: plan, trust receipt, today view, check-ins, RSVP
reader, and SR review all call the core modules directly).

Screens (tabs): Today (plan + check-in) · Plan / Receipt · Reader
(RSVP) · SR Review (flip, grade keys/buttons 1-4 -> scheduler-named
receipts) · Export (.apkg / Obsidian vault).

FEATURES UX rules carried: today first · plain words · evidence
visible (the receipt is one tap away from every screen).

This surface versions INDEPENDENTLY of the foundation road (owner
overrule 2026-11-03): its version is TUI_VERSION below, on its own
SemVer line with its own releases.

Run:  python3 tui.py [--root <studysprint dir>]
Requires: textual (pip install textual) + the core requirements for
SR export paths.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

TUI_VERSION = "0.5.1"
SURFACE = "studysprint-tui"

from study_geo import surface_calendar_geo  # noqa: E402
from study_memory import build_palace  # noqa: E402
from study_reader import RSVPReader, Section  # noqa: E402
from study_sr import (build_cards_from_practice_set, export_apkg,  # noqa: E402
                      export_obsidian_vault, review_card)
from study_tools import (build_study_plan, fetch_study_evidence,  # noqa: E402
                         format_trust_receipt, record_daily_checkin,
                         render_today_view)

APP_ROOT = Path(__file__).resolve().parent


def build_state(root: Path | None = None, stem: str = "",
                syllabus_doc: dict | None = None) -> dict:
    """Assemble one course's surface state from the core.

    Bundled samples load by examples stem ('' = syllabus.json,
    '_stats' = syllabus_stats.json); a user course passes its
    syllabus doc directly (no practice set, no readings, no
    calendar -- each absence is the panes' own honest empty
    state)."""
    root = root or APP_ROOT
    if syllabus_doc is not None:
        syllabus = syllabus_doc
        practice = {"questions": []}
        evidence_receipt = (
            "Local course — created on this surface from its "
            "syllabus document; nothing was fetched.")
    else:
        syllabus = json.loads(
            (root / "examples" / f"syllabus{stem}.json").read_text())
        practice = json.loads(
            (root / "examples" / f"practice_set{stem}.json")
            .read_text())
        evidence_receipt = None
    evidence = None
    if evidence_receipt is None:
        evidence = fetch_study_evidence(
            {"kind": "syllabus", "ref": f"examples/syllabus{stem}.json"},
            root=root)
    plan = build_study_plan(syllabus)
    # Per-topic readings (#4230), shared with the web builder:
    # examples/readings.json carries one authored passage per
    # syllabus topic; a topic without one gets an honest stub,
    # never another topic's content.
    readings = {}
    readings_file = root / "examples" / f"readings{stem}.json"
    if syllabus_doc is None and readings_file.exists():
        readings = json.loads(readings_file.read_text())
    sections = []
    for w in syllabus.get("weeks") or []:
        for topic in w.get("topics") or []:
            if readings.get(topic):
                text = readings[topic]
            else:
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
            sections.append(Section(
                section_id=f"w{w.get('week')}-{abs(hash(topic)) % 9999}",
                title=topic, content=text,
                chapter=f"Week {w.get('week')}"))
    # Calendar + geography (parity iteration 1, #4414): the
    # bundled example calendar drives the core assembler; a root
    # without one gets None and the panes say so honestly.
    calendar_geo = None
    calendar_error = None
    calendar_file = root / "examples" / f"calendar{stem}.json"
    if syllabus_doc is None and calendar_file.exists():
        calendar_doc = json.loads(calendar_file.read_text())
        topics = [t for w in syllabus.get("weeks") or []
                  for t in w.get("topics") or []]
        try:
            calendar_geo = surface_calendar_geo(
                calendar_doc, datetime.now(timezone.utc),
                topics=topics)
        except ValueError as e:
            # The core calendar intake refused this course's
            # calendar: record it, ship the course (the web
            # builder's rule, #4416).
            calendar_error = str(e)
    return {
        "course": syllabus.get("course"),
        "syllabus": syllabus,
        "plan": plan,
        "trust_receipt": evidence_receipt
        if evidence_receipt is not None
        else format_trust_receipt(evidence),
        "today": render_today_view(plan),
        "cards": build_cards_from_practice_set(practice),
        "sections": sections,
        "calendar_geo": calendar_geo,
        "calendar_error": calendar_error,
        "memory": _memory_state(plan, calendar_geo),
        "root": root,
    }


def user_courses_dir() -> Path:
    return Path.home() / ".studysprint" / "courses"


def build_course_set(root: Path | None = None) -> dict:
    """The surface's course set (parity iteration 3, #4416): both
    bundled samples + the student's own courses (syllabus docs
    under ~/.studysprint/courses), intaken through the REAL core
    course-set machinery -- per-course countdowns, merged totals,
    conflict flags, and a per-course .ics export."""
    from study_courses import export_ics, intake_courses
    root = root or APP_ROOT
    bundles = [build_state(root, stem) for stem in ("", "_stats")]
    docs = [b["syllabus"] for b in bundles]
    cdir = user_courses_dir()
    if cdir.exists():
        for f in sorted(cdir.glob("*.json")):
            try:
                doc = json.loads(f.read_text())
            except (ValueError, OSError):
                continue
            if doc.get("course") and doc.get("weeks"):
                bundles.append(build_state(root, syllabus_doc=doc))
                docs.append(doc)
    intake = intake_courses(docs,
                            now=datetime.now(timezone.utc))
    from datetime import date
    ics = {}
    for b in bundles:
        single = {"courses": [c for c in intake["courses"]
                               if c["course"] == b["course"]]}
        ics[b["course"]] = export_ics(single,
                                      date.today().isoformat())
    return {"bundles": bundles, "intake": intake, "ics": ics}


def build_book_bundle(root: Path | None = None) -> dict:
    """The §1b demonstration book (parity iteration 4, #4417),
    run LIVE through the real core pipeline at app start: Darwin,
    On the Origin of Species, 6th edition (Project Gutenberg
    #2009) — Chapter XIV + the book's complete Glossary and
    Index (typographic normalization only; content verbatim).
    Same construction as web/build_data.py's bundle; the parity
    tests pin both surfaces to the same counts and payloads."""
    from study_pipeline import (build_term_bank, emphasize_terms,
                                extract_structure, make_annotation,
                                term_tap_payload, to_reader_sections)
    root = root or APP_ROOT
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
        sections.append({"title": sec.title,
                         "chapter": sec.chapter,
                         "text": sec.content,
                         "segments": emph["segments"],
                         "terms_found": emph["terms_found"]})
    taps = {t["term"].lower(): term_tap_payload(t["term"], bank)
            for t in flat}
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
        "counts": counts, "receipt": bank["receipt"],
        "sections": sections, "taps": taps,
        "annotations": annotations,
        "annotations_note": (
            "Annotations of record over the bundled book, in "
            "the W3C Web Annotation model (the core's "
            "make_annotation). The hypothes.is API leg syncs "
            "these with an account token — not configured on "
            "this surface, so nothing leaves the device."),
    }


def _memory_state(plan: dict, calendar_geo: dict | None) -> dict:
    """Memory-methods state (parity iteration 2, #4415) — mirrors
    web/build_data.py's bundle rule: iteration 1's temple route
    IS the course palace where present; otherwise the core
    builds one over the plan's topics on its default route."""
    temple = (calendar_geo or {}).get("temple_route") or {}
    if temple.get("placements"):
        return {"palace": {
            "placements": temple["placements"],
            "route": [p["locus"] for p in temple["placements"]],
            "claims_ceiling": temple.get("claims_ceiling"),
            "source": "temple-route"}}
    chapters, items = [], {}
    for w in plan.get("weeks") or []:
        title = f"Week {w.get('week')}"
        topics: list = []
        for s in w.get("sessions") or []:
            if s["topic"] not in topics:
                topics.append(s["topic"])
        chapters.append(title)
        items[title] = topics
    return {"palace": {**build_palace(chapters, items),
                       "source": "default-route"}}


def _plan_text(state: dict) -> str:
    plan = state["plan"]
    lines = [f"Course: {plan.get('course')}",
             f"Sessions: {plan.get('total_sessions')}", ""]
    for w in plan.get("weeks") or []:
        lines.append(f"Week {w.get('week')} (due: {w.get('due')})")
        for s in w.get("sessions") or []:
            lines.append(f"  - {s['kind']}: {s['topic']} "
                         f"({s['minutes']} min)")
    return "\n".join(lines)


def _receipt_text(state: dict) -> str:
    return json.dumps(state["trust_receipt"], indent=2, sort_keys=True)


_DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _calendar_text(state: dict) -> str:
    """Calendar pane (iteration 1, #4414): classes, assessment
    briefings with ramps + shift notices, today's frequency
    plan, and the quiet-hours probe — all from the core
    assembler (study_geo.surface_calendar_geo)."""
    cg = state.get("calendar_geo")
    if not cg:
        if state.get("calendar_error"):
            return ("The core calendar intake refused this "
                    f"course's calendar: {state['calendar_error']}. "
                    "The course itself is unaffected.")
        return ("No calendar loaded for this course yet. "
                "Add examples/calendar.json (classes + "
                "assessments) and this pane binds.")
    lines = ["Classes:"]
    for c in cg["classes"]:
        days = "/".join(_DAY_NAMES[d] for d in c.get("days") or [])
        lines.append(f"  {c.get('course')}: {days} "
                     f"{c.get('start')}–{c.get('end')} · "
                     f"{c.get('location')}")
    lines += ["", "Assessments (nearest first):"]
    for b in cg["briefings"]:
        lines.append(
            f"  {b['date']} {b['time']} · {b['kind']} — "
            f"{b['course']} · {b['location']} · "
            f"{b['days_away']}d away · ramp {b['ramp']['tier']} "
            f"×{b['ramp']['multiplier']}")
        if b.get("briefing"):
            lines.append(f"    ⚠ {b['briefing']}")
    lines += ["", "Today's question frequency:"]
    for course, f in sorted(cg["frequency_plan"].items()):
        lines.append(f"  {course}: {f['per_day']}/day "
                     f"(base {f['base_per_day']} × "
                     f"{f['multiplier']}, {f['tier']}"
                     + (f"; driven by {f['driven_by']}"
                        if f.get("driven_by") else "") + ")")
    q = cg.get("quiet_hours")
    lines += ["", "Quiet hours (probed against the class blocks):"]
    if q:
        for n in q["batched"]:
            lines.append(f"  in-class note {n['at'][11:16]} → held "
                         f"by {n['held_by']}, released "
                         f"{n['release_at'][11:16]}")
        for n in q["delivered"]:
            lines.append(f"  outside note {n['at'][11:16]} → "
                         "delivered")
    else:
        lines.append("  no class block in the next 7 days to probe")
    lines += ["", f"Ceiling: {cg['claims_ceiling']}"]
    return "\n".join(lines)


def _routes_text(state: dict) -> str:
    """Routes pane (iteration 1, #4414): locations, per-assessment
    routes from the student's origin, and the temple route (loci
    over the real campus walk) with its audio cues."""
    cg = state.get("calendar_geo")
    if not cg:
        return ("No calendar loaded — routes need the calendar's "
                "locations first (see the Calendar pane).")
    lines = ["Locations:"]
    for r in cg["locations"]:
        lines.append(f"  {r['location']} — "
                     + ", ".join(r.get("used_by") or []))
    lines += ["", f"Routes from {cg.get('origin') or '—'}:"]
    if cg["routes"]:
        for r in cg["routes"]:
            lines.append(
                f"  {r['assessment_kind']} ({r['course']}) → "
                f"{r['destination']}: {r['travel_minutes']} min "
                f"walk + {r['buffer_minutes']} buffer · leave by "
                f"{r['depart_by'][:10]} {r['depart_by'][11:16]} "
                f"({r['source']})")
    else:
        lines.append("  no routes — the calendar carries no "
                     "coordinates, so nothing is drawn or faked")
    temple = cg.get("temple_route")
    lines += ["", "Temple route (loci over your walk):"]
    if temple:
        for p in temple["placements"]:
            lines.append(f"  {p['position']}. {p['locus']} — "
                         f"{p['item']}")
        lines += ["", "Audio cues:"]
        for cue in cg["audio_cues"]:
            lines.append(f"  {cue['seq']}. {cue['cue']}")
    else:
        lines.append("  no waypoints on this calendar")
    return "\n".join(lines)


def _palace_text(state: dict) -> str:
    """Memory palace (iteration 2): the core-built placements —
    walk the route, then score the walk in the pane below."""
    palace = (state.get("memory") or {}).get("palace") or {}
    if not palace.get("placements"):
        return "No memory palace in this bundle yet."
    lines = [f"Your route ({palace.get('source')}): one placed "
             "item per stop."]
    for p in palace["placements"]:
        lines.append(f"  {p['position']}. {p['locus']} — "
                     f"{p['item']} ({p['chapter']})")
    lines += ["", f"Claims ceiling: {palace.get('claims_ceiling')}"]
    return "\n".join(lines)


def _interleaved_text(state: dict) -> str:
    """Interleaved session (iteration 2): the plan's sessions and
    the SR cards mixed by the core's rotation
    (study_memory.interleave_sessions) — no two consecutive
    items from the same topic when avoidable."""
    from study_memory import interleave_sessions
    quiz: dict = {}
    for w in state["plan"].get("weeks") or []:
        for s in w.get("sessions") or []:
            quiz.setdefault(s["topic"], []).append(
                f"{s['kind']}: {s['topic']} ({s['minutes']} min)")
    mixed = interleave_sessions(quiz, state["cards"])
    lines = ["", "Interleaved session — everything, mixed by "
             f"topic ({mixed['item_count']} items, "
             f"{mixed['adjacent_same_topic']} same-topic joins):"]
    for i, item in enumerate(mixed["items"], 1):
        payload = item["payload"]
        label = payload if isinstance(payload, str) else \
            payload.get("front", "card")
        lines.append(f"  {i}. [{item['kind']}] {label} "
                     f"({item['topic']})")
    return "\n".join(lines)


try:
    from textual.app import App, ComposeResult
    from textual.widgets import (Button, Footer, Header, Input,
                                 Label, Select, Static,
                                 TabbedContent, TabPane)

    class StudySprintTUI(App):
        """StudySprint in the terminal — today first, plain words,
        evidence one tap away."""

        TITLE = f"StudySprint TUI {TUI_VERSION}"
        CSS = """
        Screen { padding: 1 2; }
        .big { text-style: bold; }
        Button { min-height: 3; margin: 0 1; }
        """

        def __init__(self, root: Path | None = None,
                     export_dir: Path | None = None, **kwargs):
            super().__init__(**kwargs)
            # Multi-course (iteration 3, #4416): the app holds
            # the whole course set; self.state is the ACTIVE
            # course's bundle, rebound on a switch.
            self.course_set = build_course_set(root)
            self.state = self.course_set["bundles"][0]
            self.card_index = 0
            # #4224: review state is PER CARD (and per scheduler) —
            # a card's own history accumulates; nothing leaks from
            # the previous card's grade, nothing is discarded.
            self.card_states: dict = {}
            self.card_flipped = False
            self.scheduler_name = "fsrs"
            self.reader = RSVPReader(self.state["sections"])
            self.reader_state = None
            self.export_dir = Path(export_dir) if export_dir else \
                (self.state["root"] / "exports")
            self._timer = None
            # #4223: check-ins persist to disk (they used to live
            # only in process memory) and are loaded back at start.
            self._checkin_path = self.export_dir / "checkin-log.json"
            # Check-ins are PER COURSE (iteration 3): the file
            # stores a map course -> the core's check-in log; the
            # pre-0.4.0 flat log is adopted by the first course.
            self._checkin_map_path = \
                self.export_dir / "checkin-logs.json"
            self.checkin_logs: dict = {}
            if self._checkin_map_path.exists():
                try:
                    self.checkin_logs = json.loads(
                        self._checkin_map_path.read_text(
                            encoding="utf-8"))
                except (ValueError, OSError):
                    self.checkin_logs = {}
            elif self._checkin_path.exists():
                try:
                    self.checkin_logs = {
                        self.state["course"]: json.loads(
                            self._checkin_path.read_text(
                                encoding="utf-8"))}
                except (ValueError, OSError):
                    self.checkin_logs = {}
            self.checkin_log: dict = self.checkin_logs.get(
                self.state["course"], {})
            self._ingest_path: str | None = None
            # Iteration 4 (#4417): the §1b book bundle (live core
            # pipeline over the bundled real book) + the opt-in
            # hardening state (persisted; OFF by default — the
            # core's rule).
            self.book = build_book_bundle(root)
            self._hardening_path = \
                self.export_dir / "hardening.json"
            self.hardening_opt_in = False
            if self._hardening_path.exists():
                try:
                    self.hardening_opt_in = bool(json.loads(
                        self._hardening_path.read_text(
                            encoding="utf-8")).get("opt_in"))
                except (ValueError, OSError):
                    self.hardening_opt_in = False

        # ------------------------------------------------------ layout
        def compose(self) -> ComposeResult:
            yield Header()
            with TabbedContent(id="tabs"):
                with TabPane("Today", id="tab-today"):
                    yield Label(self._today_text(), id="today-text",
                                classes="big")
                    yield Label("How did this session go?")
                    yield Button("Done", id="checkin-done",
                                 variant="success")
                    yield Button("Partly done", id="checkin-partial",
                                 variant="warning")
                    yield Button("I missed this", id="checkin-missed",
                                 variant="error")
                    yield Label("", id="checkin-status")
                with TabPane("Courses", id="tab-courses"):
                    yield Static(self._courses_text(),
                                 id="courses-text")
                    yield Select(
                        [(b["course"], b["course"])
                         for b in self.course_set["bundles"]],
                        value=self.state["course"],
                        id="course-select", allow_blank=False)
                    yield Button("Switch course", id="course-switch")
                    yield Button("Export .ics for active course",
                                 id="course-ics")
                    yield Label("New course — name, exam date "
                                "(optional), topics for week 1 "
                                "(comma-separated):", classes="big")
                    yield Input(placeholder="Course name",
                                id="new-course-name")
                    yield Input(placeholder="Exam date YYYY-MM-DD "
                                            "(optional)",
                                id="new-course-exam")
                    yield Input(placeholder="topic, topic, topic",
                                id="new-course-topics")
                    yield Button("Create course",
                                 id="new-course-create")
                    yield Label("", id="courses-status")
                with TabPane("Plan / Receipt", id="tab-plan"):
                    yield Static(_plan_text(self.state)
                                 + _interleaved_text(self.state),
                                 id="plan-text")
                    yield Label("Trust receipt (what was fetched):",
                                classes="big")
                    yield Static(_receipt_text(self.state),
                                 id="receipt-text")
                with TabPane("Reader", id="tab-reader"):
                    yield Label("Reader — one word at a time.",
                                classes="big")
                    yield Label("Press Start, then Step or Play.",
                                id="reader-word")
                    yield Button("Start section", id="reader-start")
                    yield Button("Step", id="reader-step")
                    yield Button("Play / Pause", id="reader-play")
                    yield Button("Rewind 10", id="reader-rewind")
                    yield Label("", id="reader-status")
                with TabPane("Book", id="tab-book"):
                    yield Static(self._book_receipt_text(),
                                 id="book-receipt")
                    yield Static(self._book_text(), id="book-text")
                    yield Select(
                        [(t["term"], t["term"].lower())
                         for t in sorted(
                             self.book["taps"].values(),
                             key=lambda x: x["term"])],
                        id="book-term", allow_blank=False,
                        value=sorted(self.book["taps"])[0]
                        if self.book["taps"] else None)
                    yield Button("Show expansion", id="book-show")
                    yield Static("", id="book-payload")
                    yield Static(self._annotations_text(),
                                 id="book-annotations")
                with TabPane("SR Review", id="tab-sr"):
                    yield Label("Scheduler:", classes="big")
                    yield Select([("FSRS (default)", "fsrs"),
                                  ("SM-2 (baseline)", "sm2"),
                                  ("Leitner boxes", "leitner")],
                                 value="fsrs", id="sr-scheduler",
                                 allow_blank=False)
                    yield Label("", id="sr-front", classes="big")
                    yield Label("", id="sr-back")
                    yield Button("Flip card", id="sr-flip")
                    yield Button("1 Again", id="grade-1")
                    yield Button("2 Hard", id="grade-2")
                    yield Button("3 Good", id="grade-3")
                    yield Button("4 Easy", id="grade-4")
                    yield Button("Knew it — up a box",
                                 id="grade-leitner-1")
                    yield Button("Missed — back to box 1",
                                 id="grade-leitner-0")
                    yield Label("", id="sr-receipt")
                with TabPane("Memory", id="tab-memory"):
                    yield Static(_palace_text(self.state),
                                 id="palace-text")
                    yield Label("Walk it: type the placed items in "
                                "route order, comma-separated, "
                                "from memory.")
                    yield Input(placeholder="item, item, item",
                                id="walk-input")
                    yield Button("Score my walk", id="walk-score")
                    yield Label("", id="walk-result")
                    yield Label("Explain it back (Feynman):",
                                classes="big")
                    yield Select(
                        [(f"{s.chapter} — {s.title}", s.title)
                         for s in self.state["sections"]],
                        value=self.state["sections"][0].title
                        if self.state["sections"] else None,
                        id="feynman-topic", allow_blank=False)
                    yield Input(placeholder="Explain it in your "
                                            "own words…",
                                id="feynman-input")
                    yield Button("Grade my explanation",
                                 id="feynman-grade")
                    yield Label("", id="feynman-result")
                    yield Label("Retrievability reminders:",
                                classes="big")
                    yield Static(self._retrievability_text(),
                                 id="retrievability-text")
                    yield Button("Refresh reminders",
                                 id="retrievability-refresh")
                with TabPane("Calendar", id="tab-calendar"):
                    yield Static(_calendar_text(self.state),
                                 id="calendar-text")
                with TabPane("Routes", id="tab-routes"):
                    yield Static(_routes_text(self.state),
                                 id="routes-text")
                with TabPane("Hardening", id="tab-hardening"):
                    yield Static(self._hardening_intro_text(),
                                 id="hardening-intro")
                    yield Button("Opt in to hardening",
                                 id="hardening-toggle")
                    yield Label("", id="hardening-status")
                    yield Input(value="drill-1",
                                id="hardening-drill-id")
                    yield Select(
                        [("1 — conceptualization", "1"),
                         ("2 — rehearsal", "2"),
                         ("3 — application", "3")],
                        id="hardening-phase", allow_blank=False,
                        value="1")
                    yield Button("Plan drill", id="hardening-plan")
                    yield Static("", id="hardening-plan-out")
                    yield Input(value="0", id="hardening-answered")
                    yield Input(value="0", id="hardening-notyet")
                    yield Button("Record result",
                                 id="hardening-record")
                    yield Label("", id="hardening-result")
                    yield Static(self._hardening_contexts_text(),
                                 id="hardening-contexts")
                    yield Static(self._hardening_script_text(),
                                 id="hardening-script")
                with TabPane("Ingest", id="tab-ingest"):
                    yield Label("Add a syllabus or textbook file — "
                                "one core path, every surface.",
                                classes="big")
                    yield Input(placeholder="Path to a file "
                                            "(.txt, .md, image, .pdf)",
                                id="ingest-path")
                    yield Button("Ingest", id="ingest-go",
                                 variant="primary")
                    yield Label("", id="ingest-result")
                    yield Button("Confirm placement",
                                 id="ingest-confirm")
                    yield Label("", id="ingest-placement")
                with TabPane("Export", id="tab-export"):
                    yield Label("Take your cards with you.",
                                classes="big")
                    yield Button("Export Anki .apkg", id="export-apkg")
                    yield Button("Export Obsidian vault",
                                 id="export-vault")
                    yield Label("", id="export-status")
            yield Footer()

        def on_mount(self) -> None:
            self._show_card()

        # ---------------------------------------------------- courses
        def _courses_text(self) -> str:
            intake = self.course_set["intake"]
            lines = [f"Course set: {intake['course_count']} "
                     f"course(s) · {intake['total_sessions']} "
                     "sessions total"]
            for row in intake["courses"]:
                cd = row["countdown"]
                when = ("exam unset" if cd["urgency"] == "unset"
                        else f"exam {cd['exam_date']} — "
                             f"{cd['days_remaining']}d "
                             f"({cd['urgency']})")
                mark = ("▶ " if row["course"] ==
                        self.state["course"] else "  ")
                lines.append(f"{mark}{row['course']} — "
                             f"{row['plan']['total_sessions']} "
                             f"sessions · {when}")
            for c in intake["conflicts"]:
                lines.append(f"⚠ conflict: {c['type']} — "
                             f"{' + '.join(c['courses'])} "
                             f"(gap {c['gap_days']}d)")
            return "\n".join(lines)

        # ------------------------------------------------- book (§1b)
        def _book_receipt_text(self) -> str:
            c = self.book["counts"]
            return (f"Textbook ingest — the demonstration book\n"
                    f"{self.book['source']}\n"
                    f"Ingest receipt (core term bank): "
                    f"{c['terms']} terms mined · "
                    f"{c['with_definitions']} with definitions · "
                    f"{c['with_index_refs']} with index refs.")

        def _book_text(self) -> str:
            if not self.book["sections"]:
                return "No book sections."
            sec = self.book["sections"][0]
            out, used = [], 0
            for seg in sec["segments"]:
                piece = (f"*{seg['text']}*" if seg.get("term")
                         else seg["text"])
                out.append(piece)
                used += len(piece)
                if used > 4000:
                    break
            return (f"{sec['chapter']} — {sec['title']} "
                    f"(opening; *terms* are tappable in the "
                    f"expansion picker below)\n\n"
                    + "".join(out) + " …")

        def _annotations_text(self) -> str:
            lines = ["Annotations (hypothes.is leg):"]
            for a in self.book["annotations"]:
                sel = a["target"]["selector"]
                lines.append(f"“{sel.get('exact', '')[:90]}…”")
                lines.append(f"  {a['body'][0]['value']}")
                lines.append(f"  Tags: {', '.join(a['tags'])} · "
                             "model: W3C Web Annotation")
            if not self.book["annotations"]:
                lines.append("  No annotations of record.")
            lines.append(self.book["annotations_note"])
            return "\n".join(lines)

        def _book_payload_text(self, term_key: str) -> str:
            tap = self.book["taps"].get(term_key)
            if tap is None:
                return "Pick a term first."
            pages = (", ".join(str(p) for p in tap["index_pages"])
                     if tap["index_pages"] else "—")
            return (f"{tap['term']} — {tap['definition']}\n"
                    f"Index pages: {pages} · Appears in: "
                    f"{', '.join(tap['sections'])} "
                    f"({tap['chapter']})\n"
                    "From the book's own Glossary + Index, mined "
                    "at ingest by the core term bank.")

        # ------------------------------------------- hardening (§1d)
        def _hardening_intro_text(self) -> str:
            from study_hardening import HARDENING_CEILING
            state = "ON" if self.hardening_opt_in else "OFF"
            return (f"Adaptive hardening is OPT-IN ONLY — it is "
                    f"{state} on this device. Claims ceiling: "
                    f"{HARDENING_CEILING}. No-guilt binds: "
                    "pressure never carries penalties; there are "
                    "no score or penalty fields here.")

        def _hardening_contexts_text(self) -> str:
            from study_hardening import varied_context_plan
            plan = varied_context_plan(6)
            lines = ["Varied-context practice (ceiling: "
                     f"{plan['claims_ceiling']}):"]
            for a in plan["assignments"]:
                lines.append(f"  Session {a['session']}: "
                             f"{a['place']} · {a['time_of_day']} "
                             f"· {a['materials']}")
            return "\n".join(lines)

        def _hardening_script_text(self) -> str:
            from study_hardening import reinstatement_script
            script = reinstatement_script(
                "the exam room", self.state["course"])
            lines = ["Mental reinstatement (exam day):"]
            for i, step in enumerate(script["steps"], 1):
                lines.append(f"  {i}. {step}")
            return "\n".join(lines)

        def _save_hardening(self) -> None:
            try:
                self._hardening_path.parent.mkdir(
                    parents=True, exist_ok=True)
                self._hardening_path.write_text(json.dumps(
                    {"opt_in": self.hardening_opt_in}))
            except OSError:
                pass

        def _switch_course(self, name: str) -> None:
            bundle = next(
                (b for b in self.course_set["bundles"]
                 if b["course"] == name), None)
            if bundle is None or name == self.state["course"]:
                return
            self.checkin_logs[self.state["course"]] = \
                self.checkin_log
            self.state = bundle
            self.checkin_log = self.checkin_logs.get(name, {})
            self.card_index = 0
            self.card_states = {}
            self.card_flipped = False
            self.reader = RSVPReader(self.state["sections"])
            self.reader_state = None
            self.query_one("#today-text", Label).update(
                self._today_text())
            self.query_one("#plan-text", Static).update(
                _plan_text(self.state)
                + _interleaved_text(self.state))
            self.query_one("#receipt-text", Static).update(
                _receipt_text(self.state))
            self.query_one("#palace-text", Static).update(
                _palace_text(self.state))
            self.query_one("#calendar-text", Static).update(
                _calendar_text(self.state))
            self.query_one("#routes-text", Static).update(
                _routes_text(self.state))
            self.query_one("#retrievability-text", Static).update(
                self._retrievability_text())
            self.query_one("#courses-text", Static).update(
                self._courses_text())
            feynman = self.query_one("#feynman-topic", Select)
            feynman.set_options(
                [(f"{s.chapter} — {s.title}", s.title)
                 for s in self.state["sections"]])
            self._show_card()

        def _create_course(self) -> None:
            name = self.query_one("#new-course-name", Input) \
                .value.strip()
            exam = self.query_one("#new-course-exam", Input) \
                .value.strip()
            topics = [t.strip() for t in self.query_one(
                "#new-course-topics", Input).value.split(",")
                if t.strip()]
            status = self.query_one("#courses-status", Label)
            if not name or not topics:
                status.update("A course needs a name and at "
                              "least one topic.")
                return
            doc = {"course": name,
                   "weeks": [{"week": 1, "topics": topics}]}
            if exam:
                doc["exam_date"] = exam
            cdir = user_courses_dir()
            cdir.mkdir(parents=True, exist_ok=True)
            slug = "".join(
                c if c.isalnum() else "-"
                for c in name.lower()).strip("-") or "course"
            (cdir / f"{slug}.json").write_text(
                json.dumps(doc, indent=1), encoding="utf-8")
            self.course_set = build_course_set(self.state["root"])
            sel = self.query_one("#course-select", Select)
            sel.set_options(
                [(b["course"], b["course"])
                 for b in self.course_set["bundles"]])
            self.query_one("#courses-text", Static).update(
                self._courses_text())
            status.update(
                f"Course created: {name} — saved to "
                f"{cdir / (slug + '.json')}; switch to it above. "
                "Its check-ins and reviews live under its own "
                "name, never another course's.")

        # ------------------------------------------------------ today
        def _today_text(self) -> str:
            today = self.state["today"]
            sessions = today.get("sessions") or []
            if not sessions:
                return "Nothing scheduled today. Enjoy the quiet."
            first = sessions[0]
            return (f"Today: {len(sessions)} session(s). "
                    f"First up: {first.get('kind', 'study')} — "
                    f"{first.get('topic')} "
                    f"({first.get('minutes', '?')} min)")

        # --------------------------------------------------------- SR
        def _current_card(self):
            cards = self.state["cards"]
            return cards[self.card_index % len(cards)] if cards \
                else None

        def _show_card(self) -> None:
            card = self._current_card()
            if card is None:
                self.query_one("#sr-front", Label).update(
                    "No cards yet.")
                return
            self.card_flipped = False
            self.query_one("#sr-front", Label).update(
                f"Card {self.card_index + 1}: {card.front}")
            self.query_one("#sr-back", Label).update(
                "(flip to see the answer)")

        def _grade(self, grade: int) -> None:
            card = self._current_card()
            if card is None:
                return
            if self.scheduler_name == "leitner":
                self.query_one("#sr-receipt", Label).update(
                    "Leitner grades in boxes: use “Knew it — up "
                    "a box” or “Missed — back to box 1”.")
                return
            if not self.card_flipped:
                # Grading unlocks once the answer is visible
                # (#4234): a grade records recall of an answer
                # the learner has seen.
                self.query_one("#sr-receipt", Label).update(
                    "Flip the card first — grading unlocks once "
                    "you've seen the answer.")
                return
            if self.scheduler_name == "sm2":
                # The map preserves the core's SM-2 pass boundary
                # (quality < 3 resets): Hard (2) does NOT pass.
                # (#4232; the old map put Hard on quality 3.)
                grade = {1: 1, 2: 2, 3: 3, 4: 5}[grade]
            # #4224: this card's OWN stored state goes in; the
            # resulting state is stored back under this card. The
            # previous implementation shared one app-level state
            # across cards and then discarded it.
            key = (card.card_id, self.scheduler_name)
            next_state, receipt = review_card(
                card, self.card_states.get(key), grade,
                scheduler=self.scheduler_name,
                now=datetime.now(timezone.utc))
            self.card_states[key] = next_state
            generation = receipt.get("fsrs_generation")
            gen_text = f" generation={generation}" if generation else ""
            self.query_one("#sr-receipt", Label).update(
                f"Receipt: scheduler={receipt['scheduler']}{gen_text} "
                f"grade={receipt['grade']} "
                f"next due {receipt['due']} "
                f"(in {receipt['interval_days']} day(s))")
            self.card_index += 1
            self._show_card()

        # ------------------------------------------------------ memory
        def _retrievability_text(self) -> str:
            """Retrievability reminders (iteration 2): the core's
            threshold rule over THIS surface's own reviewed FSRS
            states (per-card states carry stability + last_review
            from the real review path)."""
            from study_memory import retrievability_notifications
            entries = []
            fronts = {c.card_id: c.front
                      for c in self.state["cards"]}
            for (card_id, scheduler), st in \
                    self.card_states.items():
                if scheduler != "fsrs" or not isinstance(st, dict):
                    continue
                entries.append({
                    "card_id": card_id, "front": fronts.get(card_id, ""),
                    "state": {"stability": st.get("stability"),
                              "last_review": st.get("last_review")}})
            notes = retrievability_notifications(
                entries, datetime.now(timezone.utc))
            if not notes:
                return ("No card has fallen to the retrievability "
                        "threshold (R ≤ 0.9) yet. Reminders appear "
                        "here as your reviewed cards fade.")
            lines = []
            for n in notes:
                lines.append(f"  • {n['text']} "
                             f"(R = {n['retrievability']})")
            return "\n".join(lines)

        def _grade_leitner(self, knew_it: bool) -> None:
            """Leitner rotation (iteration 2): the core's box
            scheduler (study_memory.leitner_review) — knew it ->
            up a box, missed -> box 1, plain-language receipt."""
            from study_memory import leitner_review
            card = self._current_card()
            if card is None:
                return
            if not self.card_flipped:
                self.query_one("#sr-receipt", Label).update(
                    "Flip the card first — grading unlocks once "
                    "you've seen the answer.")
                return
            key = (card.card_id, "leitner")
            next_state, receipt = leitner_review(
                card, self.card_states.get(key), 1 if knew_it else 0,
                datetime.now(timezone.utc))
            self.card_states[key] = next_state
            self.query_one("#sr-receipt", Label).update(
                f"Receipt: scheduler=leitner "
                f"grade={receipt['grade']} — "
                f"{receipt['plain_language']} "
                f"(box {receipt['box']}, next due "
                f"{receipt['due'][:10]})")
            self.card_index += 1
            self._show_card()

        # ------------------------------------------------------ events
        def on_select_changed(self, event) -> None:
            if event.select.id == "sr-scheduler":
                # per-card states are keyed by scheduler (#4224),
                # so switching schedulers needs no reset at all
                self.scheduler_name = str(event.value)

        # ------------------------------------------------------ ingest
        def _ingest(self, confirmed: bool) -> None:
            """One core path (study_pipeline.ingest_any) — build D
            leg 2. Placement is confirm-gated: Ingest parses and
            reports; only Confirm placement places."""
            from study_pipeline import ingest_any
            path = self.query_one("#ingest-path", Input).value.strip()
            if confirmed and self._ingest_path:
                path = self._ingest_path
            if not path:
                self.query_one("#ingest-result", Label).update(
                    "Enter a file path first.")
                return
            try:
                result = ingest_any(path, confirmed=confirmed)
            except Exception as exc:  # surfaced, never swallowed
                self.query_one("#ingest-result", Label).update(
                    f"Ingest failed: {exc}")
                return
            self._ingest_path = path
            if result["flow"] == "syllabus":
                counts = result["parse"]["counts"]
                self.query_one("#ingest-result", Label).update(
                    f"Syllabus parsed ({result['provenance']['source']}"
                    f"): {counts['classes']} class meeting(s), "
                    f"{counts['assessments']} assessment(s).")
                placed = result["placement"].get("placed")
                self.query_one("#ingest-placement", Label).update(
                    "Placed on the calendar."
                    if placed else
                    "Not placed — review, then Confirm placement.")
            else:
                tb = result["term_bank"]
                self.query_one("#ingest-result", Label).update(
                    f"Textbook ingested: {tb['terms']} term(s) "
                    f"mined · {tb['with_definitions']} with "
                    f"definitions · {tb['with_index_refs']} with "
                    f"index refs · {result['sr_cards']} SR "
                    f"card(s).")

        def on_button_pressed(self, event) -> None:
            bid = event.button.id or ""
            if bid == "book-show":
                sel = self.query_one("#book-term", Select)
                if sel.value and sel.value != Select.BLANK:
                    self.query_one("#book-payload", Static) \
                        .update(self._book_payload_text(
                            str(sel.value)))
                return
            if bid == "hardening-toggle":
                self.hardening_opt_in = not self.hardening_opt_in
                self._save_hardening()
                event.button.label = (
                    "Turn hardening off" if self.hardening_opt_in
                    else "Opt in to hardening")
                self.query_one("#hardening-intro", Static) \
                    .update(self._hardening_intro_text())
                self.query_one("#hardening-status", Label) \
                    .update("Hardening is "
                            + ("ON." if self.hardening_opt_in
                               else "OFF."))
                return
            if bid == "hardening-plan":
                from study_hardening import plan_hardening_drill
                drill_id = self.query_one(
                    "#hardening-drill-id", Input).value.strip() \
                    or "drill-1"
                phase_sel = self.query_one("#hardening-phase",
                                           Select)
                phase = int(phase_sel.value or 1)
                plan = plan_hardening_drill(
                    drill_id, phase, self.hardening_opt_in,
                    datetime.now(timezone.utc))
                if plan["status"] == "refused":
                    text = (f"Refused: {plan['reason']} "
                            f"(ceiling: {plan['claims_ceiling']})")
                else:
                    pressure = plan.get("pressure") or []
                    text = (f"Phase {plan['phase']} — "
                            f"{plan['name']} "
                            f"({'timed' if plan['timed'] else 'untimed'})\n"
                            f"{plan['brief']}\n"
                            + (f"Pressure elements (seeded by "
                               f"the drill id): "
                               f"{' · '.join(pressure)}\n"
                               if pressure else "")
                            + f"{plan['no_guilt']} · ceiling: "
                              f"{plan['claims_ceiling']}")
                self.query_one("#hardening-plan-out", Static) \
                    .update(text)
                return
            if bid == "hardening-record":
                from study_hardening import record_drill_result
                drill_id = self.query_one(
                    "#hardening-drill-id", Input).value.strip() \
                    or "drill-1"
                try:
                    answered = int(self.query_one(
                        "#hardening-answered", Input).value or 0)
                    not_yet = int(self.query_one(
                        "#hardening-notyet", Input).value or 0)
                except ValueError:
                    answered, not_yet = 0, 0
                result = record_drill_result(
                    drill_id, answered, not_yet,
                    self.hardening_opt_in,
                    datetime.now(timezone.utc))
                self.query_one("#hardening-result", Label) \
                    .update(result["close"])
                return
            if bid == "course-switch":
                sel = self.query_one("#course-select", Select)
                if sel.value and sel.value != Select.BLANK:
                    self._switch_course(str(sel.value))
                    self.query_one("#courses-status", Label) \
                        .update(f"Active course: {self.state['course']}")
                return
            if bid == "course-ics":
                name = self.state["course"]
                slug = "".join(
                    c if c.isalnum() else "-"
                    for c in name.lower()).strip("-") or "course"
                self.export_dir.mkdir(parents=True, exist_ok=True)
                path = self.export_dir / f"{slug}.ics"
                path.write_text(self.course_set["ics"][name],
                                encoding="utf-8")
                self.query_one("#courses-status", Label).update(
                    f".ics for {name} written to {path} "
                    "(this course's sessions + milestones only).")
                return
            if bid == "new-course-create":
                self._create_course()
                return
            if bid.startswith("grade-leitner-"):
                self._grade_leitner(bid.endswith("-1"))
                return
            if bid == "walk-score":
                from study_memory import walk_review
                palace = (self.state.get("memory") or {}).get(
                    "palace") or {}
                raw = self.query_one("#walk-input", Input).value
                recalled = [x.strip() for x in raw.split(",")
                            if x.strip()]
                receipt = walk_review(
                    palace, recalled,
                    datetime.now(timezone.utc))
                missed = ", ".join(receipt["missed"]) or "none"
                self.query_one("#walk-result", Label).update(
                    f"Walk receipt: placed {receipt['placed']} · "
                    f"correct in position "
                    f"{receipt['correct_in_position']} · out of "
                    f"order {receipt['recalled_out_of_order']} · "
                    f"ordered recall {receipt['ordered_recall']} · "
                    f"missed: {missed}.")
                return
            if bid == "feynman-grade":
                from study_memory import explain_back
                topic = str(self.query_one(
                    "#feynman-topic", Select).value)
                section = next(
                    (s for s in self.state["sections"]
                     if s.title == topic), None)
                evidence = [section.content] if section else []
                receipt = explain_back(
                    topic,
                    self.query_one("#feynman-input", Input).value,
                    evidence, datetime.now(timezone.utc))
                if receipt["verdict"] == "abstain":
                    text = f"Verdict: abstain — {receipt['reason']}."
                else:
                    missing = ", ".join(
                        receipt["missing_terms"][:12]) or "none"
                    text = (f"Verdict: {receipt['verdict']} · "
                            f"coverage {receipt['coverage']} · "
                            f"missing: {missing} · "
                            f"{receipt['guidance']}. (Key-term "
                            "coverage against the verified text — "
                            "not semantic grading.)")
                self.query_one("#feynman-result", Label).update(text)
                return
            if bid == "retrievability-refresh":
                self.query_one("#retrievability-text",
                               Static).update(
                    self._retrievability_text())
                return
            if bid == "ingest-go":
                self._ingest(confirmed=False)
                return
            if bid == "ingest-confirm":
                self._ingest(confirmed=True)
                return
            if bid.startswith("checkin-"):
                status = bid.replace("checkin-", "")
                status = {"done": "done", "partial": "partial",
                          "missed": "missed"}[status]
                # #4223: record against TODAY's actual identity
                # (the week + day the surface is showing), not a
                # hardcoded week 1 / session 0 — and persist.
                today = self.state["today"]
                sessions = today.get("sessions") or [{}]
                week = sessions[0].get("week", 1)
                day_index = today.get("day_index", 0)
                self.checkin_log = record_daily_checkin(
                    self.checkin_log, week=week,
                    session_index=day_index, status=status)
                self.checkin_logs[self.state["course"]] = \
                    self.checkin_log
                self._checkin_map_path.parent.mkdir(
                    parents=True, exist_ok=True)
                self._checkin_map_path.write_text(
                    json.dumps(self.checkin_logs, indent=1),
                    encoding="utf-8")
                # The pre-0.4.0 flat file keeps carrying the
                # ACTIVE course's log (older builds read it).
                self._checkin_path.write_text(
                    json.dumps(self.checkin_log, indent=1),
                    encoding="utf-8")
                entries = self.checkin_log.get("entries") or []
                self.query_one("#checkin-status", Label).update(
                    f"Checked in: {status} (week {week}, "
                    f"day {day_index + 1}). "
                    f"{len(entries)} check-in(s) logged + saved.")
            elif bid == "sr-flip":
                card = self._current_card()
                if card is not None:
                    self.card_flipped = True
                    self.query_one("#sr-back", Label).update(card.back)
            elif bid.startswith("grade-"):
                self._grade(int(bid.split("-")[1]))
            elif bid == "reader-start":
                sections = self.state["sections"]
                if sections:
                    self.reader_state = self.reader.start_section(
                        sections[0].section_id, pass_number=1)
                    self.query_one("#reader-status", Label).update(
                        f"Reading: {sections[0].title} "
                        f"({len(sections[0].tokens)} words)")
            elif bid == "reader-step":
                self._reader_step()
            elif bid == "reader-play":
                if self.reader_state is None:
                    self.on_button_pressed(type("E", (), {
                        "button": type("B", (), {"id": "reader-start"})
                        ()})())
                if self._timer is None:
                    self._timer = self.set_interval(
                        0.25, self._reader_step)
                else:
                    self._timer.stop()
                    self._timer = None
            elif bid == "reader-rewind":
                if self.reader_state is not None:
                    self.reader.rewind(10)
                    self._reader_step()
            elif bid == "export-apkg":
                out = self.export_dir / "studysprint.apkg"
                receipt = export_apkg(self.state["cards"], out)
                self.query_one("#export-status", Label).update(
                    f"Exported {receipt['cards']} cards to {out} "
                    f"(sha256 {receipt['sha256'][:12]}...)")
            elif bid == "export-vault":
                receipt = export_obsidian_vault(
                    self.state["cards"], self.export_dir / "vault")
                self.query_one("#export-status", Label).update(
                    f"Vault surface written: {receipt['notes']} "
                    f"notes in {receipt['dir']}")

        def _reader_step(self) -> None:
            if self.reader_state is None:
                return
            token = self.reader.next_token()
            if token is None:
                self.query_one("#reader-word", Label).update(
                    "Section done. Nice reading.")
                if self._timer is not None:
                    self._timer.stop()
                    self._timer = None
                return
            word = token.get("word") or token.get("token") or str(token)
            self.query_one("#reader-word", Label).update(str(word))

except ImportError:  # textual not installed: the module still imports
    StudySprintTUI = None  # type: ignore


def main() -> None:
    if StudySprintTUI is None:
        raise SystemExit(
            "the TUI surface needs textual: pip install textual")
    StudySprintTUI().run()


if __name__ == "__main__":
    main()
