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

TUI_VERSION = "0.1.2"
SURFACE = "studysprint-tui"

from study_reader import RSVPReader, Section  # noqa: E402
from study_sr import (build_cards_from_practice_set, export_apkg,  # noqa: E402
                      export_obsidian_vault, review_card)
from study_tools import (build_study_plan, fetch_study_evidence,  # noqa: E402
                         format_trust_receipt, record_daily_checkin,
                         render_today_view)

APP_ROOT = Path(__file__).resolve().parent


def build_state(root: Path | None = None) -> dict:
    """Assemble the surface state from the core, over the bundled
    example course (the same data demo.py runs)."""
    root = root or APP_ROOT
    syllabus = json.loads(
        (root / "examples" / "syllabus.json").read_text())
    practice = json.loads(
        (root / "examples" / "practice_set.json").read_text())
    evidence = fetch_study_evidence(
        {"kind": "syllabus", "ref": "examples/syllabus.json"}, root=root)
    plan = build_study_plan(syllabus)
    # Per-topic readings (#4230), shared with the web builder:
    # examples/readings.json carries one authored passage per
    # syllabus topic; a topic without one gets an honest stub,
    # never another topic's content.
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
            sections.append(Section(
                section_id=f"w{w.get('week')}-{abs(hash(topic)) % 9999}",
                title=topic, content=text,
                chapter=f"Week {w.get('week')}"))
    return {
        "syllabus": syllabus,
        "plan": plan,
        "trust_receipt": format_trust_receipt(evidence),
        "today": render_today_view(plan),
        "cards": build_cards_from_practice_set(practice),
        "sections": sections,
        "root": root,
    }


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
            self.state = build_state(root)
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
            self.checkin_log: dict = {}
            if self._checkin_path.exists():
                try:
                    self.checkin_log = json.loads(
                        self._checkin_path.read_text(encoding="utf-8"))
                except (ValueError, OSError):
                    self.checkin_log = {}
            self._ingest_path: str | None = None

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
                with TabPane("Plan / Receipt", id="tab-plan"):
                    yield Static(_plan_text(self.state), id="plan-text")
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
                with TabPane("SR Review", id="tab-sr"):
                    yield Label("Scheduler:", classes="big")
                    yield Select([("FSRS (default)", "fsrs"),
                                  ("SM-2 (baseline)", "sm2")],
                                 value="fsrs", id="sr-scheduler",
                                 allow_blank=False)
                    yield Label("", id="sr-front", classes="big")
                    yield Label("", id="sr-back")
                    yield Button("Flip card", id="sr-flip")
                    yield Button("1 Again", id="grade-1")
                    yield Button("2 Hard", id="grade-2")
                    yield Button("3 Good", id="grade-3")
                    yield Button("4 Easy", id="grade-4")
                    yield Label("", id="sr-receipt")
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
                self.query_one("#ingest-result", Label).update(
                    f"Textbook ingested: "
                    f"{result['term_bank']['terms']} term(s), "
                    f"{result['sr_cards']} SR card(s).")

        def on_button_pressed(self, event) -> None:
            bid = event.button.id or ""
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
                self._checkin_path.parent.mkdir(parents=True,
                                                 exist_ok=True)
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
