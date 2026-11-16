"""Offline tests for StudySprint RSVP multi-pass reader core (study_reader.py)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from study_reader import (  # noqa: E402
    DEFAULT_WPM_PER_PASS, READER_RECEIPT_SCHEMA, RSVPReader, ReaderState,
    Section, calculate_dwell_ms, calculate_orp, format_reader_receipt,
    reader_plain_language_action, tokenize_text,
)


def test_orp_anchor_calculation():
    # length 1: index 0
    assert calculate_orp("a") == 0
    assert calculate_orp("I") == 0
    # length 2-5: index 1
    assert calculate_orp("to") == 1
    assert calculate_orp("the") == 1
    assert calculate_orp("plant") == 1
    # length 6-9: index 2
    assert calculate_orp("photos") == 2
    assert calculate_orp("cellular") == 2
    # length 10-13: index 3
    assert calculate_orp("respiration") == 3
    assert calculate_orp("chloroplasts") == 3
    # length > 13: index 4
    assert calculate_orp("photosynthesis!") == 4  # without punct 14 chars -> index 4
    # with leading/trailing punctuation
    assert calculate_orp('"hello"') == 1


def test_dwell_ms_calculation():
    # Base 300 wpm -> 200 ms
    # Plain word
    dwell_plain = calculate_dwell_ms("cell", 300)
    assert dwell_plain == 200

    # Sentence end punctuation (. ! ?): +100% (2.0x -> 400 ms)
    dwell_end = calculate_dwell_ms("cell.", 300)
    assert dwell_end == 400

    # Clause punctuation (, ; :): +50% (1.5x -> 300 ms)
    dwell_clause = calculate_dwell_ms("cell,", 300)
    assert dwell_clause == 300

    # Long word > 8 chars: +25%
    dwell_long = calculate_dwell_ms("mitochondria", 300)  # 12 chars -> +25% -> 250 ms
    assert dwell_long == 250

    # Very long word > 12 chars: +50%
    dwell_vlong = calculate_dwell_ms("differentiation", 300)  # 15 chars -> +50% -> 300 ms
    assert dwell_vlong == 300

    # Zero or negative WPM fallback
    dwell_fallback = calculate_dwell_ms("test", -10)
    assert dwell_fallback == 200


def test_tokenize_text():
    tokens = tokenize_text("Photosynthesis converts light into chemical energy.")
    assert len(tokens) == 6
    assert tokens[0] == "Photosynthesis"
    assert tokens[-1] == "energy."


def test_reader_section_initialization_and_passes():
    sec = Section(
        section_id="bio101_sec1",
        title="1.1 Overview of Photosynthesis",
        content="Photosynthesis converts light energy into chemical energy in plants and algae.",
    )
    assert len(sec.tokens) == 11

    reader = RSVPReader(sections=[sec])

    # Pass 1: very fast skim (default 500 wpm)
    state1 = reader.start_section("bio101_sec1", pass_number=1)
    assert state1.pass_number == 1
    assert state1.wpm == 500
    assert not state1.is_paused
    assert not state1.is_completed
    assert state1.token_index == 0

    # Read all tokens in pass 1
    tokens_read = []
    while not state1.is_completed:
        frame = reader.next_token()
        if frame:
            tokens_read.append(frame["word"])

    assert len(tokens_read) == 11
    assert state1.is_completed is True
    assert state1.token_index == 11

    # Pass 2: slower focused re-read (default 260 wpm)
    state2 = reader.start_section("bio101_sec1", pass_number=2)
    assert state2.pass_number == 2
    assert state2.wpm == 260
    assert not state2.is_completed

    # Pass 3+: deep pass (default 220 wpm)
    state3 = reader.start_section("bio101_sec1", pass_number=3)
    assert state3.pass_number == 3
    assert state3.wpm == 220

    # Custom WPM configuration
    custom_reader = RSVPReader(
        sections=[sec],
        wpm_per_pass={1: 650, 2: 300, 3: 180},
    )
    s_custom = custom_reader.start_section("bio101_sec1", pass_number=1)
    assert s_custom.wpm == 650


def test_reader_pause_resume_rewind():
    sec = Section(
        section_id="bio101_sec2",
        title="1.2 Light Reactions",
        content="Light reactions produce ATP and NADPH in the thylakoid membranes of chloroplasts.",
    )
    reader = RSVPReader([sec])
    reader.start_section("bio101_sec2", pass_number=1)

    # Read 5 words
    for _ in range(5):
        reader.next_token()

    assert reader.active_state.token_index == 5
    assert not reader.active_state.is_paused

    # Pause
    reader.pause()
    assert reader.active_state.is_paused is True

    # Resume
    reader.resume()
    assert reader.active_state.is_paused is False

    # Rewind 10 words (should clamp to index 0 since index is 5)
    reader.rewind(words=10)
    assert reader.active_state.token_index == 0
    assert reader.active_state.rewind_count == 1

    # Advance 8 words
    for _ in range(8):
        reader.next_token()
    assert reader.active_state.token_index == 8

    # Rewind 3 words -> index 5
    reader.rewind(words=3)
    assert reader.active_state.token_index == 5
    assert reader.active_state.rewind_count == 2


def test_one_tap_flagging_model():
    sec = Section(
        section_id="bio101_sec3",
        title="1.3 Calvin Cycle",
        content="Carbon fixation occurs during the light independent reactions of the Calvin cycle.",
    )
    reader = RSVPReader([sec])
    reader.start_section("bio101_sec3", pass_number=2)

    # Advance to "fixation"
    reader.next_token()  # Carbon
    reader.next_token()  # fixation

    # One-tap flag term
    term_entry = reader.flag_term(
        term="Carbon fixation",
        context="Carbon fixation occurs during the light independent reactions",
    )
    assert term_entry["term"] == "Carbon fixation"
    assert term_entry["normalized_term"] == "carbon fixation"
    assert term_entry["feeds_sr_card"] is True
    assert term_entry["feeds_quiz_focus"] is True
    assert term_entry["section_id"] == "bio101_sec3"
    assert term_entry["token_index"] == 2
    assert len(reader.active_state.flagged_terms) == 1

    # One-tap flag section
    sec_entry = reader.flag_section(note="Need to re-read enzyme regulation")
    assert sec_entry["section_id"] == "bio101_sec3"
    assert sec_entry["note"] == "Need to re-read enzyme regulation"
    assert len(reader.active_state.flagged_sections) == 1


def test_term_lookup_hook_point():
    # Mock term bank lookup interface (protocol/callable hook only, no concrete bank)
    mock_bank = {
        "chloroplast": {
            "term": "Chloroplast",
            "definition": "Organelle where photosynthesis takes place",
            "index_refs": [12, 14, 45],
            "card_ready": True,
        },
        "atp": {
            "term": "ATP",
            "definition": "Adenosine triphosphate, primary energy carrier in cells",
            "index_refs": [8, 19],
            "card_ready": True,
        },
    }

    def sample_term_lookup(term: str) -> dict | None:
        return mock_bank.get(term.lower())

    sec = Section(
        section_id="bio101_sec4",
        title="1.4 Chloroplast Structure",
        content="The chloroplast generates ATP during the light reactions.",
    )
    reader = RSVPReader(sections=[sec], term_lookup_fn=sample_term_lookup)
    reader.start_section("bio101_sec4", pass_number=2)

    frame1 = reader.next_token()  # "The"
    assert not frame1["is_term_emphasized"]
    assert frame1["term_meta"] is None

    frame2 = reader.next_token()  # "chloroplast"
    assert frame2["is_term_emphasized"] is True
    assert frame2["term_meta"]["term"] == "Chloroplast"
    assert "photosynthesis takes place" in frame2["term_meta"]["definition"]

    frame3 = reader.next_token()  # "generates"
    assert not frame3["is_term_emphasized"]

    frame4 = reader.next_token()  # "ATP"
    assert frame4["is_term_emphasized"] is True
    assert frame4["term_meta"]["term"] == "ATP"


def test_format_reader_receipt_and_plain_language():
    sec = Section(
        section_id="bio101_sec5",
        title="1.5 Summary",
        content="Plants absorb light energy and convert it into sugars.",
    )
    reader = RSVPReader([sec])
    reader.start_section("bio101_sec5", pass_number=1)

    # Flag a term and pause
    reader.next_token()
    reader.flag_term("light energy")
    reader.pause()

    receipt = format_reader_receipt(reader)
    assert receipt["schema"] == READER_RECEIPT_SCHEMA
    assert receipt["section_id"] == "bio101_sec5"
    assert receipt["section_title"] == "1.5 Summary"
    assert receipt["pass_number"] == 1
    assert receipt["wpm"] == 500
    assert receipt["is_paused"] is True
    assert receipt["flagged_terms_count"] == 1
    assert "receipt_sha256" in receipt
    assert "Paused your reading" in receipt["plain_language_summary"]

    # Plain language function checks
    p1_start = reader_plain_language_action("start_pass", {"pass_number": 1, "wpm": 500})
    assert "Starting Pass 1 (fast skim at 500 words per minute)" in p1_start

    p2_start = reader_plain_language_action("start_pass", {"pass_number": 2, "wpm": 260})
    assert "Starting Pass 2 (focused re-read at 260 words per minute)" in p2_start

    p1_end = reader_plain_language_action("complete_pass", {"pass_number": 1})
    assert "Pass 1 skim completed" in p1_end

    rewind_msg = reader_plain_language_action("rewind", {"words": 10})
    assert "Rewound 10 words" in rewind_msg

    flag_sec_msg = reader_plain_language_action("flag_section", {"section_id": "sec1"})
    assert "Flagged sec1 for review" in flag_sec_msg

    flag_term_msg = reader_plain_language_action("flag_term", {"term": "ATP"})
    assert "Saved 'ATP' to your term bank" in flag_term_msg
