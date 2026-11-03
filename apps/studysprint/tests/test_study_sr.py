"""Offline tests for the StudySprint SR module (study_sr.py).

Covers every public function: card building from quiz/term data, both
schedulers (receipts name the scheduler), the invalid-scheduler error,
.apkg export, the Obsidian vault surface + sync read-back, and the
ts-fsrs UX state seed.
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from study_sr import (build_cards, build_cards_from_practice_set,  # noqa: E402
                      export_apkg, export_obsidian_vault,
                      export_ux_state, get_scheduler,
                      import_obsidian_states, read_obsidian_card_state,
                      review_card, to_ts_fsrs_state)

NOW = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)

QUIZ = [
    {"q": "What does the cell membrane do?",
     "a": "Controls what enters and leaves the cell."},
    {"question": "Where is DNA stored?", "answer": "The nucleus."},
    {"term": "photosynthesis",
     "definition": "Conversion of light energy into chemical energy."},
    {"prompt": "Explain 'respiration' from memory"},  # no answer: skipped
]


def test_build_cards_from_quiz_and_term_shapes():
    cards = build_cards(QUIZ, source={"kind": "practice_set"})
    assert len(cards) == 3
    assert cards[0].front.startswith("What does the cell membrane")
    assert cards[0].back.startswith("Controls what enters")
    assert cards[2].front == "photosynthesis"
    ids = [c.card_id for c in cards]
    assert len(set(ids)) == 3 and all(len(i) == 16 for i in ids)
    again = build_cards(QUIZ)
    assert [c.card_id for c in again] == ids  # deterministic ids


def test_build_cards_from_practice_set():
    doc = json.loads((ROOT / "examples" / "practice_set.json").read_text())
    cards = build_cards_from_practice_set(doc)
    assert len(cards) == 2
    assert cards[0].source["topic"] == "cell structure"
    assert "cell structure" in cards[0].tags


def test_get_scheduler_names_and_unknown():
    assert get_scheduler("fsrs").name == "fsrs"
    assert get_scheduler("sm2").name == "sm2"
    assert get_scheduler(" SM2 ").name == "sm2"
    try:
        get_scheduler("leitner")
    except ValueError as e:
        assert "unknown scheduler" in str(e)
    else:
        raise AssertionError("unknown scheduler must raise")


def test_sm2_progression_and_receipt():
    card = build_cards(QUIZ)[0]
    state = get_scheduler("sm2").new_state()
    state, r1 = review_card(card, state, 4, scheduler="sm2", now=NOW)
    assert r1["scheduler"] == "sm2"
    assert r1["interval_days"] == 1.0
    assert r1["due"] == "2026-11-03T12:00:00Z"
    state, r2 = review_card(card, state, 4, scheduler="sm2", now=NOW)
    assert r2["interval_days"] == 6.0
    state, r3 = review_card(card, state, 5, scheduler="sm2", now=NOW)
    assert r3["interval_days"] == round(6 * r3["state"]["easiness"])
    assert r3["state"]["repetitions"] == 3


def test_sm2_lapse_resets_and_ef_floor():
    card = build_cards(QUIZ)[0]
    sched = get_scheduler("sm2")
    state = sched.new_state()
    for _ in range(3):
        state, _ = sched.review(card, state, 5, NOW)
    state, receipt = sched.review(card, state, 1, NOW)
    assert receipt["state"]["repetitions"] == 0
    assert receipt["interval_days"] == 1.0
    for _ in range(30):
        state, _ = sched.review(card, state, 0, NOW)
    assert state["easiness"] >= 1.3


def test_sm2_grade_validation():
    card = build_cards(QUIZ)[0]
    try:
        review_card(card, None, 6, scheduler="sm2", now=NOW)
    except ValueError as e:
        assert "0..5" in str(e)
    else:
        raise AssertionError("sm2 grade 6 must raise")


def test_fsrs_review_and_receipt():
    card = build_cards(QUIZ)[0]
    sched = get_scheduler("fsrs")
    state = sched.new_state()
    state, receipt = review_card(card, state, 3, scheduler="fsrs", now=NOW)
    assert receipt["scheduler"] == "fsrs"
    assert receipt["grade"] == 3
    assert receipt["reviewed_at"] == "2026-11-02T12:00:00Z"
    assert receipt["due"] > receipt["reviewed_at"]
    assert receipt["interval_days"] > 0
    # the returned state feeds the next review (round-trip)
    state2, receipt2 = review_card(card, state, 4, scheduler="fsrs",
                                   now=NOW + timedelta(days=1))
    assert receipt2["scheduler"] == "fsrs"
    assert state2["due"] >= state["due"]


def test_fsrs_grade_validation():
    card = build_cards(QUIZ)[0]
    try:
        review_card(card, None, 5, scheduler="fsrs", now=NOW)
    except ValueError as e:
        assert "1..4" in str(e)
    else:
        raise AssertionError("fsrs grade 5 must raise")


def test_default_scheduler_is_fsrs():
    card = build_cards(QUIZ)[0]
    _state, receipt = review_card(card, None, 3, now=NOW)
    assert receipt["scheduler"] == "fsrs"


def test_export_apkg_produces_file(tmp_path):
    cards = build_cards(QUIZ)
    out = tmp_path / "studysprint.apkg"
    receipt = export_apkg(cards, out)
    assert out.exists() and out.stat().st_size > 0
    assert out.read_bytes()[:2] == b"PK"  # apkg is a zip archive
    assert receipt["deck"] == "StudySprint"
    assert receipt["cards"] == 3
    assert len(receipt["sha256"]) == 64


def test_obsidian_vault_round_trip(tmp_path):
    cards = build_cards(QUIZ)
    card = cards[0]
    _st, receipt = review_card(card, None, 4, scheduler="sm2", now=NOW)
    states = {card.card_id: {"due": receipt["due"],
                             "interval_days": receipt["interval_days"]}}
    out = export_obsidian_vault(cards, tmp_path, states=states,
                                scheduler="sm2")
    assert out["notes"] == 3 and out["scheduler"] == "sm2"
    root = tmp_path / "StudySprint SR"
    assert (root / "StudySprint SR Index.md").exists()
    note = root / f"{card.card_id}.md"
    text = note.read_text()
    assert "#flashcards" in text and "\n?\n" in text
    back = read_obsidian_card_state(note)
    assert back["card_id"] == card.card_id
    assert back["scheduler"] == "sm2"
    assert back["due"] == receipt["due"]
    assert back["interval_days"] == receipt["interval_days"]
    imported = import_obsidian_states(tmp_path)
    assert set(imported) == {c.card_id for c in cards}


def test_obsidian_export_rejects_unknown_scheduler(tmp_path):
    try:
        export_obsidian_vault(build_cards(QUIZ), tmp_path,
                              scheduler="leitner")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown scheduler must raise before writing")


def test_ts_fsrs_state_mapping():
    card = build_cards(QUIZ)[0]
    state, _r = review_card(card, None, 3, scheduler="fsrs", now=NOW)
    ux = to_ts_fsrs_state(state, now=NOW)
    assert ux["due"] == state["due"]
    assert ux["stability"] == state["stability"]
    assert ux["difficulty"] == state["difficulty"]
    assert ux["state"] in ("New", "Learning", "Review", "Relearning")
    assert "reps" in ux and "lapses" in ux


def test_export_ux_state_document():
    cards = build_cards(QUIZ)
    states = {}
    for c in cards:
        st, _r = review_card(c, None, 3, scheduler="fsrs", now=NOW)
        states[c.card_id] = st
    doc = export_ux_state(cards, states, now=NOW)
    assert doc["format"] == "ts-fsrs/v1"
    assert doc["scheduler"] == "fsrs"
    assert len(doc["cards"]) == 3
    assert all(set(e) == {"card_id", "front", "back", "ts_fsrs"}
               for e in doc["cards"])
    json.dumps(doc)  # the whole document is JSON-serializable
