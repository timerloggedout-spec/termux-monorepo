"""StudySprint memory methods — RFP-D1-5 (issue #4113), all six.

StudySprint schedules and retrieves (FSRS/SM-2, v0.3.0); this module
is the memory-science surface a student actually studies with — how
material gets encoded, paced, and recalled in the moment. Every
method carries its evidence grade and its CLAIMS CEILING in the
receipts and in FEATURES: the ceiling binds what the product may say
the method does.

1. **Method of loci (Temple Memory)** — chapters -> a palace route,
   term-bank items placed at loci, walk-mode review.
   Evidence: Dresler et al. 2017 (Neuron) — naive trainees 26 -> 62
   of 72 words, durable at 4 months; BJOP 2025 meta-analysis
   d = 0.88 for serial recall (GRADE low).
   CEILING: ordered/concrete recall — NOT understanding.
2. **Pomodoro session engine** — 25/5 blocks x4 + long break,
   check-in = block completion, adaptive block length.
   Evidence: fatigue down ~20%, self-rated focus up; no learning
   gain proven. CEILING: pacing/starting — NOT memory.
3. **Retrievability notifications** — fire at the FSRS
   retrievability threshold; the notification carries the cue and a
   one-tap grade, so retrieval happens inside the reminder.
   Phrasing follows implementation intentions ("When X, I will Y").
4. **Feynman explain-back** — the student's explanation graded
   against VERIFIED evidence only; with no verified evidence the
   grader abstains, and thin coverage escalates (the kernel's
   abstain/escalate discipline).
5. **Interleaved quiz/card sessions** — topics and due cards mixed
   round-robin; no two consecutive items from the same topic when
   avoidable.
6. **Leitner boxes** — the plain-language onboarding scheduler:
   five boxes, known -> up a box, missed -> back to box 1, every
   move receipt-stamped with a plain-language explanation.

Offline and deterministic given explicit times.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from study_sr import review_card as sr_review_card

MEMORY_RECEIPT_SCHEMA = "studysprint-memory-receipt/v1"


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _receipt(method: str, now: datetime, **fields) -> dict:
    out = {"schema": MEMORY_RECEIPT_SCHEMA, "method": method,
           "observed_at": _iso(now)}
    out.update(fields)
    return out


# ------------------------------------------------------------- 1. loci

DEFAULT_ROUTE = [
    "front door", "entryway", "coat rack", "living-room couch",
    "coffee table", "bookshelf", "kitchen counter", "stove",
    "dining table", "hallway mirror", "bedroom desk", "window sill",
    "closet door", "bathroom sink", "back porch", "garden gate",
]

LOCI_CLAIMS_CEILING = "ordered/concrete recall, not understanding"
LOCI_EVIDENCE = ("Dresler et al. 2017 (Neuron): 26 -> 62 of 72 words, "
                 "durable 4 months; BJOP 2025 meta-analysis d=0.88 "
                 "serial recall, GRADE low")


def build_palace(chapters, items_by_chapter=None, route=None) -> dict:
    """Build a memory palace: chapters map onto an ordered route of
    loci; each chapter's items (term-bank entries or topics) are
    placed at consecutive loci in order.

    chapters: list of chapter titles or pipeline chapter dicts.
    items_by_chapter: {chapter_title: [item, ...]} — items are dicts
    with a `term`/`topic`/`front` or plain strings."""
    route = list(route or DEFAULT_ROUTE)
    placements, loci_used = [], 0
    items_by_chapter = items_by_chapter or {}
    for ch in chapters or []:
        title = ch["title"] if isinstance(ch, dict) else str(ch)
        items = items_by_chapter.get(title, [])
        for item in items:
            label = item if isinstance(item, str) else (
                item.get("term") or item.get("topic")
                or item.get("front") or "")
            if loci_used >= len(route):
                raise ValueError(
                    f"palace route exhausted ({len(route)} loci); "
                    "pass a longer route")
            placements.append({"position": loci_used + 1,
                               "locus": route[loci_used],
                               "chapter": title, "item": label})
            loci_used += 1
    return {"route": route[:loci_used] or route, "placements": placements,
            "chapters": [c["title"] if isinstance(c, dict) else str(c)
                         for c in chapters or []],
            "claims_ceiling": LOCI_CLAIMS_CEILING,
            "evidence": LOCI_EVIDENCE}


def walk_review(palace: dict, recalled, now: datetime) -> dict:
    """Walk-mode review: the student walks the route and recalls each
    placed item in order. Scores ORDERED recall (the method's claim):
    correct-in-position, recalled-out-of-order, missed."""
    placed = [p["item"] for p in palace.get("placements", [])]
    recalled = list(recalled or [])
    in_position = sum(1 for i, item in enumerate(placed)
                      if i < len(recalled) and recalled[i] == item)
    placed_set = set(placed)
    out_of_order = sum(1 for r in recalled
                       if r in placed_set) - in_position
    missed = [item for item in placed if item not in set(recalled)]
    return _receipt(
        "loci-walk", now, placed=len(placed),
        correct_in_position=in_position,
        recalled_out_of_order=max(0, out_of_order), missed=missed,
        ordered_recall=(round(in_position / len(placed), 3)
                        if placed else None),
        claims_ceiling=LOCI_CLAIMS_CEILING)


# ---------------------------------------------------------- 2. pomodoro

POMODORO_CLAIMS_CEILING = "pacing/starting, not memory"
POMODORO_EVIDENCE = ("fatigue down ~20%, self-rated focus up in the "
                     "cited studies; no learning gain proven")


def plan_pomodoro(focus_minutes: int = 25, short_break: int = 5,
                  long_break: int = 15, cycles: int = 4,
                  total_focus_blocks: int = 4) -> dict:
    """A Pomodoro timeline: focus blocks separated by short breaks,
    a long break after each `cycles` set."""
    blocks, focus_seen = [], 0
    for i in range(total_focus_blocks):
        focus_seen += 1
        blocks.append({"index": len(blocks) + 1, "kind": "focus",
                       "minutes": focus_minutes,
                       "block": focus_seen})
        if i < total_focus_blocks - 1:
            is_long = focus_seen % cycles == 0
            blocks.append({"index": len(blocks) + 1,
                           "kind": "long-break" if is_long
                           else "short-break",
                           "minutes": long_break if is_long
                           else short_break})
    return {"blocks": blocks,
            "focus_blocks": total_focus_blocks,
            "total_minutes": sum(b["minutes"] for b in blocks),
            "focused_minutes": focus_minutes * total_focus_blocks,
            "claims_ceiling": POMODORO_CLAIMS_CEILING,
            "evidence": POMODORO_EVIDENCE}


def pomodoro_checkin(plan: dict, completed_focus_blocks: int,
                     now: datetime) -> dict:
    """Check-in = block completion: done when every focus block
    completed, partial when some did, missed when none did."""
    total = plan.get("focus_blocks", 0)
    done = max(0, min(completed_focus_blocks, total))
    status = "done" if done == total and total > 0 else \
        "partial" if done > 0 else "missed"
    per_block = (plan.get("focused_minutes", 0) // total) if total else 0
    return _receipt("pomodoro-checkin", now, status=status,
                    focus_blocks_done=done, focus_blocks_total=total,
                    minutes_focused=per_block * done,
                    claims_ceiling=POMODORO_CLAIMS_CEILING)


def adapt_block_length(checkins, current_focus: int = 25) -> dict:
    """Adaptive block length (deterministic heuristic): three fully
    done check-ins in a row -> +5 minutes (cap 50); two partial or
    missed in a row -> -5 (floor 10); otherwise hold. Returns the
    suggestion with its reason — pacing advice, not a memory claim."""
    statuses = [c.get("status") for c in checkins or []]
    suggestion, reason = current_focus, "hold: no streak signal"
    if len(statuses) >= 3 and all(s == "done" for s in statuses[-3:]):
        suggestion = min(50, current_focus + 5)
        reason = "three done check-ins in a row: lengthen the block"
    elif len(statuses) >= 2 and all(s in ("partial", "missed")
                                    for s in statuses[-2:]):
        suggestion = max(10, current_focus - 5)
        reason = "two incomplete check-ins in a row: shorten the block"
    return {"current_focus": current_focus, "suggested_focus": suggestion,
            "reason": reason, "claims_ceiling": POMODORO_CLAIMS_CEILING}


# ------------------------------------------- 3. retrievability notifies

def fsrs_retrievability(stability: float, elapsed_days: float) -> float:
    """FSRS forgetting curve: R = (1 + (19/81) * t/S) ** -0.5."""
    if stability is None or stability <= 0:
        return 0.0
    return (1.0 + (19.0 / 81.0) * (elapsed_days / stability)) ** -0.5


def retrievability_notifications(cards_with_states, now: datetime,
                                 threshold: float = 0.9) -> list:
    """Fire at the retrievability threshold: for each FSRS card whose
    retrievability has fallen to/below `threshold`, emit a
    notification carrying the cue + a one-tap grade payload, phrased
    as an implementation intention. cards_with_states: SRCard-like
    dicts {card_id, front, state{stability, last_review}}."""
    out = []
    for entry in cards_with_states or []:
        state = entry.get("state") or {}
        stability = state.get("stability")
        last_review = state.get("last_review")
        if stability is None or not last_review:
            continue  # never reviewed: not a threshold case
        last = datetime.fromisoformat(
            str(last_review).replace("Z", "+00:00"))
        elapsed = max(0.0, (now - last).total_seconds() / 86400.0)
        r = fsrs_retrievability(float(stability), elapsed)
        if r > threshold:
            continue
        front = entry.get("front", "")
        out.append({
            "card_id": entry.get("card_id"),
            "cue": front,
            "retrievability": round(r, 3),
            "threshold": threshold,
            "text": (f"When this reminder fires, I will picture the "
                     f"answer to: {front} — then grade myself "
                     f"honestly."),
            "one_tap_grade": {"card_id": entry.get("card_id"),
                              "scheduler": "fsrs",
                              "grades": [1, 2, 3, 4]},
            "observed_at": _iso(now),
        })
    return out


def apply_notification_grade(card, state, grade: int, now: datetime):
    """The grade tapped inside the reminder IS the review: delegates
    to the SR core (study_sr.review_card) and returns its stamped
    receipt."""
    _state, receipt = sr_review_card(card, state, grade,
                                     scheduler="fsrs", now=now)
    receipt = dict(receipt)
    receipt["via"] = "retrievability-notification"
    return _state, receipt


# ------------------------------------------------- 4. feynman explain-back

_WORD = re.compile(r"[a-z0-9']+")


def _tokens(text: str) -> set:
    stop = {"the", "a", "an", "of", "to", "in", "is", "are", "and",
            "or", "it", "its", "that", "this", "by", "for", "on",
            "as", "be", "with", "from"}
    return {t for t in _WORD.findall(str(text).lower())
            if t not in stop and len(t) > 2}


def explain_back(topic: str, explanation: str, evidence,
                 now: datetime, escalate_below: float = 0.5) -> dict:
    """Grade an explanation against VERIFIED evidence only.

    evidence: term-bank entries / evidence values for the topic
    ({term, definition} dicts or strings). No verified evidence ->
    ABSTAIN (nothing to grade against). Otherwise coverage = the
    share of the evidence's key terms the explanation actually uses;
    below `escalate_below` -> ESCALATE with the missing terms named
    (re-read, then explain again). This is key-term coverage against
    verified text — stated plainly, not semantic grading."""
    texts = []
    for e in evidence or []:
        if isinstance(e, dict):
            texts.append(str(e.get("definition") or e.get("value")
                             or ""))
        else:
            texts.append(str(e))
    texts = [t for t in texts if t.strip()]
    if not texts:
        return _receipt("feynman", now, topic=topic, verdict="abstain",
                        reason="no verified evidence for this topic; "
                               "nothing to grade against",
                        coverage=None, missing_terms=[])
    key_terms = set()
    for t in texts:
        key_terms |= _tokens(t)
    used = _tokens(explanation)
    covered = key_terms & used
    coverage = round(len(covered) / len(key_terms), 3) if key_terms \
        else 0.0
    missing = sorted(key_terms - used)
    if coverage < escalate_below:
        return _receipt("feynman", now, topic=topic,
                        verdict="escalate", coverage=coverage,
                        missing_terms=missing,
                        guidance="re-read the verified source, then "
                                 "explain again covering the missing "
                                 "terms")
    return _receipt("feynman", now, topic=topic, verdict="graded",
                    coverage=coverage, missing_terms=missing,
                    guidance="solid coverage of the verified evidence")


# ------------------------------------------------------- 5. interleaving

def interleave_sessions(quiz_by_topic: dict, cards) -> dict:
    """Build an interleaved session: quiz prompts and SR cards mixed
    round-robin across topics, no two consecutive items from the same
    topic when avoidable. Deterministic (rotation, not shuffle) so
    the session is receipt-reproducible."""
    queues = {}
    for topic, items in (quiz_by_topic or {}).items():
        queues.setdefault(topic, []).extend(
            {"kind": "quiz", "topic": topic, "payload": q}
            for q in items or [])
    for card in cards or []:
        topic = (card.tags[0] if getattr(card, "tags", None)
                 else "sr-cards")
        queues.setdefault(topic, []).extend(
            [{"kind": "card", "topic": topic,
              "payload": card.to_dict()}])
    topics = sorted(queues)
    items, last_topic = [], None
    while any(queues[t] for t in topics):
        order = [t for t in topics if queues[t]]
        order.sort(key=lambda t: (t == last_topic, -len(queues[t])))
        chosen = order[0]
        items.append(queues[chosen].pop(0))
        last_topic = chosen
    adjacent_same = sum(1 for a, b in zip(items, items[1:])
                        if a["topic"] == b["topic"])
    return {"items": items, "item_count": len(items),
            "topics": topics, "adjacent_same_topic": adjacent_same}


# ------------------------------------------------------------ 6. leitner

LEITNER_INTERVALS_DAYS = {1: 1, 2: 2, 3: 4, 4: 7, 5: 14}
LEITNER_BOXES = 5


class LeitnerScheduler:
    """Leitner boxes — the plain-language onboarding scheduler.

    Same interface as the study_sr schedulers. Grade: 1 = knew it
    (up a box), 0 = missed (back to box 1). Every receipt explains
    the move in plain language."""

    name = "leitner"

    def new_state(self) -> dict:
        return {"box": 1}

    def review(self, card, state, grade: int, now: datetime):
        if grade not in (0, 1):
            raise ValueError(
                f"leitner grade must be 0 (missed) or 1 (knew it), "
                f"got {grade!r}")
        box = int((state or self.new_state()).get("box", 1))
        if grade == 1:
            new_box = min(LEITNER_BOXES, box + 1)
            plain = (f"You knew this one — it moves up to box "
                     f"{new_box} and comes back in "
                     f"{LEITNER_INTERVALS_DAYS[new_box]} days.")
            if new_box == LEITNER_BOXES and box == LEITNER_BOXES:
                plain = ("You knew this one in the top box — it "
                         "stays in box 5 and comes back in 14 days.")
        else:
            new_box = 1
            plain = ("Missed — no problem, it goes back to box 1 "
                     "and comes back tomorrow. That's how the boxes "
                     "work.")
        st = {"box": new_box}
        due = now + timedelta(days=LEITNER_INTERVALS_DAYS[new_box])
        receipt = {"scheduler": "leitner",
                   "card_id": getattr(card, "card_id", None),
                   "grade": grade, "reviewed_at": _iso(now),
                   "due": _iso(due),
                   "interval_days": float(LEITNER_INTERVALS_DAYS[new_box]),
                   "state": st, "box": new_box,
                   "plain_language": plain}
        return st, receipt


def leitner_review(card, state, grade: int, now: datetime):
    """Review one card with the Leitner scheduler (module-level
    convenience mirroring study_sr.review_card)."""
    sched = LeitnerScheduler()
    return sched.review(card, state if state is not None
                        else sched.new_state(), grade, now)


__all__ = [
    "build_palace", "walk_review", "DEFAULT_ROUTE",
    "plan_pomodoro", "pomodoro_checkin", "adapt_block_length",
    "fsrs_retrievability", "retrievability_notifications",
    "apply_notification_grade", "explain_back", "interleave_sessions",
    "LeitnerScheduler", "leitner_review", "LEITNER_INTERVALS_DAYS",
    "MEMORY_RECEIPT_SCHEMA",
]
