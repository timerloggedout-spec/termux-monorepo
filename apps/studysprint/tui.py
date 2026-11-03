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

TUI_VERSION = "0.1.0"
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
    sections = []
    for w in syllabus.get("weeks") or []:
        for topic in w.get("topics") or []:
            text = (f"{topic}. " + " ".join(
                q["q"] + " " + q["a"] for q in practice.get("questions")
                or []))
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
    from textual.widgets import (Button, Footer, Header, Label,
                                 Select, Static, TabbedContent,
                                 TabPane)

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
            self.checkin_log: dict = {}
            self.card_index = 0
            self.card_state = None
            self.card_flipped = False
            self.scheduler_name = "fsrs"
            self.reader = RSVPReader(self.state["sections"])
            self.reader_state = None
            self.export_dir = Path(export_dir) if export_dir else \
                (self.state["root"] / "exports")
            self._timer = None

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
            if self.scheduler_name == "sm2":
                grade = {1: 1, 2: 3, 3: 4, 4: 5}[grade]
            self.card_state, receipt = review_card(
                card, self.card_state, grade,
                scheduler=self.scheduler_name,
                now=datetime.now(timezone.utc))
            self.query_one("#sr-receipt", Label).update(
                f"Receipt: scheduler={receipt['scheduler']} "
                f"grade={receipt['grade']} "
                f"next due {receipt['due']} "
                f"(in {receipt['interval_days']} day(s))")
            self.card_index += 1
            self.card_state = None
            self._show_card()

        # ------------------------------------------------------ events
        def on_select_changed(self, event) -> None:
            if event.select.id == "sr-scheduler":
                self.scheduler_name = str(event.value)
                self.card_state = None

        def on_button_pressed(self, event) -> None:
            bid = event.button.id or ""
            if bid.startswith("checkin-"):
                status = bid.replace("checkin-", "")
                status = {"done": "done", "partial": "partial",
                          "missed": "missed"}[status]
                self.checkin_log = record_daily_checkin(
                    self.checkin_log, week=1, session_index=0,
                    status=status)
                entries = self.checkin_log.get("entries") or []
                self.query_one("#checkin-status", Label).update(
                    f"Checked in: {status}. "
                    f"{len(entries)} check-in(s) logged.")
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
