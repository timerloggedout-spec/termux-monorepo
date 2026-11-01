"""StudySprint RSVP multi-pass reader core (FEATURES §1b/Next).

Section-by-section RSVP reader engine designed for first-gen college students:
- Pass 1: very-fast skim (high WPM, e.g. 500 wpm) to grasp section structure
- Pass 2+: slower, focused re-reads (e.g. 260 wpm) for dense comprehension
- Configurable WPM per pass, pause/resume state, 10-word rewind, ORP anchor
- Punctuation- and word-length-aware dwell timing
- One-tap flagging (flag_section, flag_term) feeding term banks / SR cards
- Term emphasis hook point (lookup interface only; ∅ bank implementation)
- Plain-language receipts and action explanations for reader events
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

READER_RECEIPT_SCHEMA = "studysprint-reader-receipt/v1"

# Default WPM configurations: pass 1 skim vs pass 2+ focused re-reads
DEFAULT_WPM_PER_PASS = {
    1: 500,  # Pass 1: very-fast skim
    2: 260,  # Pass 2: focused re-read
    3: 220,  # Pass 3+: deep/analytical pass
}

# Term lookup hook interface type: takes normalized term, returns metadata or None
# Metadata format: {"term": str, "definition": str, "index_refs": list[int], "card_ready": bool}
TermLookupFn = Callable[[str], dict[str, Any] | None]


def _iso(dt: datetime | None = None) -> str:
    dt = dt or datetime.now(timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def calculate_orp(word: str) -> int:
    """Calculate the Optimal Recognition Point (ORP) fixation anchor index.

    Typically ~1/3 into the word (0-indexed):
    - length 1: index 0
    - length 2-5: index 1
    - length 6-9: index 2
    - length 10-13: index 3
    - length > 13: index 4
    Formula: max(0, min(4, (len(word) - 1) // 3)) if len > 1 else 0.
    """
    cleaned = re.sub(r"^\W+|\W+$", "", word)
    length = len(cleaned) if cleaned else len(word)
    if length <= 1:
        return 0
    if length <= 5:
        return 1
    if length <= 9:
        return 2
    if length <= 13:
        return 3
    return 4


def calculate_dwell_ms(word: str, wpm: int) -> int:
    """Calculate dwell duration in milliseconds with length and punctuation awareness.

    Baseline = 60,000 / wpm per word.
    Punctuation penalties:
    - Sentence end (. ! ?): +100% (2.0x baseline)
    - Clause pause (, ; : - —): +50% (1.5x baseline)
    Length penalties:
    - Words > 8 characters: +25%
    - Words > 12 characters: +50%
    """
    if wpm <= 0:
        wpm = 300
    base_ms = 60000.0 / wpm
    multiplier = 1.0

    # Punctuation check
    if re.search(r"[.!?][\"')\]]?$", word):
        multiplier += 1.0
    elif re.search(r"[,;:\-—][\"')\]]?$", word):
        multiplier += 0.5

    # Length check
    clean_len = len(re.sub(r"^\W+|\W+$", "", word))
    if clean_len > 12:
        multiplier += 0.5
    elif clean_len > 8:
        multiplier += 0.25

    return int(round(base_ms * multiplier))


def tokenize_text(text: str) -> list[str]:
    """Tokenize section text into words preserving attached punctuation."""
    return [w for w in text.split() if w]


@dataclass
class Section:
    """A chapter or document section for reading."""
    section_id: str
    title: str
    content: str
    chapter: str | None = None
    tokens: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.tokens:
            self.tokens = tokenize_text(self.content)


@dataclass
class ReaderState:
    """State tracking for a section RSVP reading session."""
    section_id: str
    pass_number: int = 1
    token_index: int = 0
    is_paused: bool = True
    is_completed: bool = False
    wpm: int = 500
    total_tokens: int = 0
    rewind_count: int = 0
    flagged_terms: list[dict[str, Any]] = field(default_factory=list)
    flagged_sections: list[dict[str, Any]] = field(default_factory=list)
    actions_log: list[dict[str, Any]] = field(default_factory=list)


class RSVPReader:
    """Multi-pass RSVP reading engine for study sections.

    Supports:
    - Pass 1 skim (fast WPM) -> Pass 2+ focused re-reads (slower WPM)
    - Play, pause, resume, 10-word rewind, next_token
    - One-tap flagging of sections and terms
    - Term lookup interface hook point
    - Action journaling for plain-language receipts
    """

    def __init__(
        self,
        sections: list[Section] | None = None,
        wpm_per_pass: dict[int, int] | None = None,
        term_lookup_fn: TermLookupFn | None = None,
    ) -> None:
        self.sections: dict[str, Section] = {s.section_id: s for s in (sections or [])}
        self.wpm_per_pass: dict[int, int] = dict(DEFAULT_WPM_PER_PASS)
        if wpm_per_pass:
            self.wpm_per_pass.update(wpm_per_pass)
        self.term_lookup_fn: TermLookupFn | None = term_lookup_fn
        self.active_state: ReaderState | None = None

    def add_section(self, section: Section) -> None:
        """Register a section to be read."""
        self.sections[section.section_id] = section

    def get_wpm_for_pass(self, pass_number: int) -> int:
        """Resolve WPM for a given pass number."""
        if pass_number in self.wpm_per_pass:
            return self.wpm_per_pass[pass_number]
        # For passes beyond 3, fall back to pass 3 or lowest configured pass
        max_pass = max(self.wpm_per_pass.keys(), default=2)
        if pass_number > max_pass:
            return self.wpm_per_pass[max_pass]
        return self.wpm_per_pass.get(2, 260)

    def start_section(self, section_id: str, pass_number: int = 1) -> ReaderState:
        """Start or restart a section at a specified pass number."""
        if section_id not in self.sections:
            raise KeyError(f"section '{section_id}' not found in reader")

        sec = self.sections[section_id]
        wpm = self.get_wpm_for_pass(pass_number)
        state = ReaderState(
            section_id=section_id,
            pass_number=pass_number,
            token_index=0,
            is_paused=False,
            is_completed=len(sec.tokens) == 0,
            wpm=wpm,
            total_tokens=len(sec.tokens),
        )
        self._log_action(state, "start_pass", {
            "section_id": section_id,
            "pass_number": pass_number,
            "wpm": wpm,
            "total_tokens": len(sec.tokens),
        })
        self.active_state = state
        return state

    def pause(self) -> ReaderState:
        """Pause the current reading session."""
        if not self.active_state:
            raise RuntimeError("no active reading session to pause")
        self.active_state.is_paused = True
        self._log_action(self.active_state, "pause", {
            "token_index": self.active_state.token_index,
        })
        return self.active_state

    def resume(self) -> ReaderState:
        """Resume the paused reading session."""
        if not self.active_state:
            raise RuntimeError("no active reading session to resume")
        if not self.active_state.is_completed:
            self.active_state.is_paused = False
            self._log_action(self.active_state, "resume", {
                "token_index": self.active_state.token_index,
            })
        return self.active_state

    def rewind(self, words: int = 10) -> ReaderState:
        """Rewind reading position by N words (default 10) to replace eye regression."""
        if not self.active_state:
            raise RuntimeError("no active reading session to rewind")
        if words <= 0:
            words = 10
        old_idx = self.active_state.token_index
        new_idx = max(0, old_idx - words)
        self.active_state.token_index = new_idx
        self.active_state.is_completed = False
        self.active_state.rewind_count += 1
        self._log_action(self.active_state, "rewind", {
            "words": words,
            "from_index": old_idx,
            "to_index": new_idx,
        })
        return self.active_state

    def next_token(self) -> dict[str, Any] | None:
        """Advance one token and return rendering frame info.

        Returns dict with word, orp, dwell_ms, term_emphasis, etc.
        Returns None when section completed.
        """
        state = self.active_state
        if not state:
            return None
        sec = self.sections.get(state.section_id)
        if not sec:
            return None
        if state.token_index >= len(sec.tokens):
            state.is_completed = True
            return None

        word = sec.tokens[state.token_index]
        orp = calculate_orp(word)
        dwell_ms = calculate_dwell_ms(word, state.wpm)

        # Term lookup hook
        clean_word = re.sub(r"^\W+|\W+$", "", word).lower()
        term_meta = None
        if self.term_lookup_fn and clean_word:
            term_meta = self.term_lookup_fn(clean_word)

        frame = {
            "word": word,
            "orp_index": orp,
            "dwell_ms": dwell_ms,
            "token_index": state.token_index,
            "total_tokens": state.total_tokens,
            "pass_number": state.pass_number,
            "wpm": state.wpm,
            "is_term_emphasized": term_meta is not None,
            "term_meta": term_meta,
        }

        state.token_index += 1
        if state.token_index >= len(sec.tokens):
            state.is_completed = True
            self._log_action(state, "complete_pass", {
                "section_id": state.section_id,
                "pass_number": state.pass_number,
                "total_tokens": state.total_tokens,
            })

        return frame

    def flag_section(self, note: str | None = None, section_id: str | None = None) -> dict[str, Any]:
        """One-tap flag on a section, sending it to the review/deck queue."""
        target_sec_id = section_id or (self.active_state.section_id if self.active_state else None)
        if not target_sec_id:
            raise ValueError("no section specified or currently active to flag")

        entry = {
            "section_id": target_sec_id,
            "timestamp": _iso(),
            "note": note or "Flagged for focused review",
            "pass_number": self.active_state.pass_number if self.active_state else None,
            "token_index": self.active_state.token_index if self.active_state else None,
        }

        if self.active_state and self.active_state.section_id == target_sec_id:
            self.active_state.flagged_sections.append(entry)
            self._log_action(self.active_state, "flag_section", entry)

        return entry

    def flag_term(
        self,
        term: str,
        section_id: str | None = None,
        context: str | None = None,
    ) -> dict[str, Any]:
        """One-tap flag on a term/concept, feeding the term bank and spaced repetition cards."""
        if not term or not term.strip():
            raise ValueError("term cannot be empty")

        clean_term = term.strip()
        sec_id = section_id or (self.active_state.section_id if self.active_state else None)

        # Query term lookup hook for definition or enrichment if available
        meta = None
        if self.term_lookup_fn:
            meta = self.term_lookup_fn(clean_term.lower())

        entry = {
            "term": clean_term,
            "normalized_term": clean_term.lower(),
            "section_id": sec_id,
            "context": context,
            "timestamp": _iso(),
            "pass_number": self.active_state.pass_number if self.active_state else None,
            "token_index": self.active_state.token_index if self.active_state else None,
            "term_bank_entry": meta,
            "feeds_sr_card": True,
            "feeds_quiz_focus": True,
        }

        if self.active_state:
            self.active_state.flagged_terms.append(entry)
            self._log_action(self.active_state, "flag_term", {
                "term": clean_term,
                "section_id": sec_id,
            })

        return entry

    def _log_action(self, state: ReaderState, action_type: str, details: dict[str, Any]) -> None:
        state.actions_log.append({
            "action": action_type,
            "timestamp": _iso(),
            "details": details,
        })


def reader_plain_language_action(action_type: str, details: dict[str, Any] | None = None) -> str:
    """Format plain-language explanations for reader events for first-gen students."""
    details = details or {}
    if action_type == "start_pass":
        pass_no = details.get("pass_number", 1)
        wpm = details.get("wpm", 500)
        if pass_no == 1:
            return f"Starting Pass 1 (fast skim at {wpm} words per minute) to get the big picture."
        return f"Starting Pass {pass_no} (focused re-read at {wpm} words per minute) for deep understanding."
    if action_type == "pause":
        return "Paused your reading. Pick right back up whenever you're ready."
    if action_type == "resume":
        return "Resumed reading your section."
    if action_type == "rewind":
        words = details.get("words", 10)
        return f"Rewound {words} words so you can re-catch the thought without eye fatigue."
    if action_type == "complete_pass":
        pass_no = details.get("pass_number", 1)
        if pass_no == 1:
            return "Pass 1 skim completed! Ready for a slower, focused re-read on tricky concepts."
        return f"Pass {pass_no} completed! Great job focusing through this section."
    if action_type == "flag_section":
        sec_id = details.get("section_id", "section")
        return f"Flagged {sec_id} for review. This will appear in your review queue."
    if action_type == "flag_term":
        term = details.get("term", "term")
        return f"Saved '{term}' to your term bank and flashcard deck."
    return "Reader updated successfully."


def format_reader_receipt(reader: RSVPReader, state: ReaderState | None = None) -> dict[str, Any]:
    """Generate structured receipt of reader actions and state in plain language."""
    active = state or reader.active_state
    if not active:
        raise ValueError("no state available to format receipt")

    sec = reader.sections.get(active.section_id)
    title = sec.title if sec else active.section_id

    # Compute content hash of the section content
    content_hash = hashlib.sha256(
        (sec.content if sec else active.section_id).encode("utf-8")
    ).hexdigest()[:12]

    # Summary of flagged items
    flagged_terms_count = len(active.flagged_terms)
    flagged_sections_count = len(active.flagged_sections)

    last_action = active.actions_log[-1]["action"] if active.actions_log else "idle"
    last_details = active.actions_log[-1]["details"] if active.actions_log else {}
    explanation = reader_plain_language_action(last_action, last_details)

    receipt = {
        "schema": READER_RECEIPT_SCHEMA,
        "section_id": active.section_id,
        "section_title": title,
        "section_hash_short": content_hash,
        "pass_number": active.pass_number,
        "wpm": active.wpm,
        "token_position": f"{active.token_index}/{active.total_tokens}",
        "is_completed": active.is_completed,
        "is_paused": active.is_paused,
        "rewind_count": active.rewind_count,
        "flagged_terms_count": flagged_terms_count,
        "flagged_sections_count": flagged_sections_count,
        "flagged_terms": active.flagged_terms,
        "flagged_sections": active.flagged_sections,
        "plain_language_summary": explanation,
        "total_actions_logged": len(active.actions_log),
        "generated_at": _iso(),
    }
    receipt["receipt_sha256"] = hashlib.sha256(
        json.dumps(receipt, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return receipt
