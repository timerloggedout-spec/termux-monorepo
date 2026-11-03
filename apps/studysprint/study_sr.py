"""StudySprint spaced repetition — FEATURES Next #1 (issue #3050).

Cards are built from StudySprint's existing quiz/term data. Scheduling
goes through a small shared interface with two implementations,
selectable by name:

- ``fsrs`` (DEFAULT) — FSRS via the ``py-fsrs`` package; a DSR memory
  model with retention-targeted intervals.
- ``sm2`` — the classic SM-2 algorithm, a legitimate simple/predictable
  baseline (and the comparison baseline in our own evals).

Every review returns a stamped receipt naming the scheduler that
produced it. Exports: Anki ``.apkg`` via ``genanki``; the REQUIRED
Obsidian vault surface (markdown notes with sync state in frontmatter,
readable back through the import sync point); and a ts-fsrs-shaped
state export that seeds the UX layer.

The bridge sync points adapt the fleet's existing adapter,
``bin/obsidian_server.py`` @master (blob d47a329c5ff1): a
token-authenticated HTTP bridge (port 8085, token at
``~/.obsidian_termux_token``, symlink-rejecting token read) into the
device that hosts the vault.

Offline and deterministic given an explicit ``now``. ``py-fsrs`` and
``genanki`` are imported lazily so the module loads in the app's
zero-dependency baseline; the functions that need them raise a clear
error naming the requirement.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

DECK_NAME = "StudySprint"
SCHEDULER_NAMES = ("fsrs", "sm2")


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _card_id(front: str, back: str) -> str:
    return hashlib.sha256(f"{front}\n{back}".encode()).hexdigest()[:16]


# ---------------------------------------------------------------- cards

@dataclass
class SRCard:
    """One spaced-repetition card (front/back) plus provenance."""

    card_id: str
    front: str
    back: str
    tags: list = field(default_factory=list)
    source: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"card_id": self.card_id, "front": self.front,
                "back": self.back, "tags": list(self.tags),
                "source": dict(self.source)}


def _front_back(item: dict):
    """Map a quiz/term item to (front, back) or None when it has no answer."""
    front = item.get("front") or item.get("q") or item.get("question") \
        or item.get("term")
    back = item.get("back") or item.get("a") or item.get("answer") \
        or item.get("definition")
    if front and back:
        return str(front), str(back)
    return None


def build_cards(items, source: dict | None = None) -> list:
    """Build SR cards from quiz/term items.

    Accepts the shapes StudySprint already produces: practice-set items
    ``{"q", "a"}``, ``{"question", "answer"}``, term-bank items
    ``{"term", "definition"}``, and ready-made ``{"front", "back"}``.
    Items without an answer (e.g. open recall prompts) are skipped —
    they have no back to schedule against.
    """
    cards = []
    for item in items or []:
        fb = _front_back(item)
        if fb is None:
            continue
        front, back = fb
        tags = list(item.get("tags") or [])
        if item.get("topic"):
            tags.append(str(item["topic"]))
        cards.append(SRCard(card_id=_card_id(front, back), front=front,
                            back=back, tags=tags,
                            source=dict(source or {})))
    return cards


def build_cards_from_practice_set(practice_set: dict,
                                  source: dict | None = None) -> list:
    """Build cards from a practice_set document (``{"topic", "questions"}``)."""
    src = {"kind": "practice_set", "topic": practice_set.get("topic")}
    src.update(source or {})
    items = []
    for q in practice_set.get("questions") or []:
        q = dict(q)
        q.setdefault("topic", practice_set.get("topic"))
        items.append(q)
    return build_cards(items, source=src)


# ------------------------------------------------------------ schedulers

class Scheduler:
    """Shared scheduling interface: review(state, grade, now).

    ``state`` is the scheduler-owned per-card state dict (``new_state``
    for a fresh card). ``review`` returns ``(new_state, receipt)``; the
    receipt always carries ``scheduler`` — the name of the scheduler
    that produced it.
    """

    name = ""

    def new_state(self) -> dict:
        raise NotImplementedError

    def review(self, card: SRCard, state: dict, grade: int,
               now: datetime):
        raise NotImplementedError

    def _receipt(self, card: SRCard, grade: int, now: datetime,
                 due: datetime, interval_days: float, state: dict) -> dict:
        return {
            "scheduler": self.name,
            "card_id": card.card_id,
            "grade": grade,
            "reviewed_at": _iso(now),
            "due": _iso(due),
            "interval_days": interval_days,
            "state": state,
        }


class SM2Scheduler(Scheduler):
    """Classic SM-2 (Wozniak): grades are quality 0..5.

    interval: 1 day, then 6 days, then previous * easiness factor.
    Quality < 3 restarts repetitions (interval back to 1 day); the
    easiness factor is floored at 1.3.
    """

    name = "sm2"

    def new_state(self) -> dict:
        return {"repetitions": 0, "easiness": 2.5, "interval_days": 0}

    def review(self, card: SRCard, state: dict, grade: int,
               now: datetime):
        if not isinstance(grade, int) or not 0 <= grade <= 5:
            raise ValueError(
                f"sm2 grade must be an int in 0..5, got {grade!r}")
        st = dict(state or self.new_state())
        ef = float(st.get("easiness", 2.5))
        ef = max(1.3, ef + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02)))
        if grade < 3:
            reps, interval = 0, 1
        else:
            reps = int(st.get("repetitions", 0)) + 1
            if reps == 1:
                interval = 1
            elif reps == 2:
                interval = 6
            else:
                interval = round(int(st.get("interval_days", 6)) * ef)
        st = {"repetitions": reps, "easiness": round(ef, 4),
              "interval_days": interval}
        due = now + timedelta(days=interval)
        return st, self._receipt(card, grade, now, due, float(interval), st)


class FSRSScheduler(Scheduler):
    """FSRS via py-fsrs (the default). Grades are ratings 1..4
    (1=Again, 2=Hard, 3=Good, 4=Easy). The per-card state is the
    py-fsrs card serialization, so it round-trips through JSON and
    maps directly onto the ts-fsrs shape for the UX layer."""

    name = "fsrs"

    def __init__(self):
        try:
            import fsrs  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "the fsrs scheduler requires the py-fsrs package "
                "(apps/studysprint/requirements.txt)") from e
        self._fsrs = fsrs

    def _scheduler(self):
        fsrs = self._fsrs
        if hasattr(fsrs, "Scheduler"):
            return fsrs.Scheduler()
        return fsrs.FSRS()  # py-fsrs < 4 API

    def new_state(self) -> dict:
        return self._fsrs.Card().to_dict()

    def review(self, card: SRCard, state: dict, grade: int,
               now: datetime):
        if grade not in (1, 2, 3, 4):
            raise ValueError(
                f"fsrs grade must be a rating in 1..4 "
                f"(Again/Hard/Good/Easy), got {grade!r}")
        fsrs = self._fsrs
        fcard = fsrs.Card.from_dict(state) if state else fsrs.Card()
        rating = fsrs.Rating(grade)
        try:
            new_card, _log = self._scheduler().review_card(
                fcard, rating, review_datetime=now)
        except TypeError:
            new_card, _log = self._scheduler().review_card(fcard, rating)
        st = new_card.to_dict()
        due = new_card.due
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        interval = (due - now).total_seconds() / 86400.0
        return st, self._receipt(card, grade, now, due,
                                 round(interval, 4), st)


def get_scheduler(name: str) -> Scheduler:
    """Return the scheduler registered under ``name`` ("fsrs" | "sm2")."""
    key = str(name or "").strip().lower()
    if key == "fsrs":
        return FSRSScheduler()
    if key == "sm2":
        return SM2Scheduler()
    raise ValueError(
        f"unknown scheduler {name!r}; expected one of "
        f"{', '.join(SCHEDULER_NAMES)}")


def review_card(card: SRCard, state: dict | None, grade: int,
                scheduler: str = "fsrs", now: datetime | None = None):
    """Review one card with the named scheduler.

    Returns ``(new_state, receipt)``; the receipt's ``scheduler`` field
    names the scheduler that produced it.
    """
    now = now or datetime.now(timezone.utc)
    sched = get_scheduler(scheduler)
    return sched.review(card, state if state is not None
                        else sched.new_state(), grade, now)


# ------------------------------------------------------------ Anki export

def _stable_id(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16) + 1


def _sanitize_tag(tag: str) -> str:
    """Make a card tag genanki-safe: Anki tags cannot contain spaces
    (genanki raises ValueError) — e.g. the practice-set topic
    "cell structure" becomes "cell_structure". Other whitespace is
    folded the same way; empty results are dropped by the caller."""
    return re.sub(r"\s+", "_", str(tag).strip())


def export_apkg(cards, out_path, deck_name: str = DECK_NAME) -> dict:
    """Export cards to an Anki ``.apkg`` file via genanki.

    Returns a stamped receipt {path, deck, cards, sha256}.
    """
    try:
        import genanki
    except ImportError as e:
        raise ImportError(
            "apkg export requires the genanki package "
            "(apps/studysprint/requirements.txt)") from e
    model = genanki.Model(
        _stable_id(f"studysprint-model-{deck_name}"),
        "StudySprint SR",
        fields=[{"name": "Front"}, {"name": "Back"}],
        templates=[{"name": "Card 1",
                    "qfmt": "{{Front}}", "afmt": "{{Back}}"}],
    )
    deck = genanki.Deck(_stable_id(f"studysprint-deck-{deck_name}"),
                        deck_name)
    for card in cards:
        note = genanki.Note(model=model, fields=[card.front, card.back],
                            tags=[t for t in
                                  (_sanitize_tag(t) for t in card.tags)
                                  if t])
        deck.add_note(note)
    out = Path(out_path)
    if out.parent and not out.parent.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
    genanki.Package(deck).write_to_file(str(out))
    return {"path": str(out), "deck": deck_name, "cards": len(cards),
            "sha256": hashlib.sha256(out.read_bytes()).hexdigest()}


# --------------------------------------------------------- Obsidian vault

_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)


def _note_text(card: SRCard, state: dict | None, scheduler: str) -> str:
    st = state or {}
    fm = {
        "studysprint": "sr-card/v1",
        "card_id": card.card_id,
        "scheduler": scheduler,
        "due": st.get("due", ""),
        "interval_days": st.get("interval_days", ""),
        "tags": card.tags,
    }
    lines = ["---"]
    for k, v in fm.items():
        lines.append(f"{k}: {json.dumps(v) if isinstance(v, list) else v}")
    lines.append("---")
    lines.append("")
    lines.append("#flashcards")
    lines.append("")
    lines.append(card.front)
    lines.append("?")
    lines.append(card.back)
    lines.append("")
    return "\n".join(lines)


def export_obsidian_vault(cards, vault_dir, states: dict | None = None,
                          scheduler: str = "fsrs") -> dict:
    """Write the vault surface: one markdown note per card under
    ``<vault_dir>/StudySprint SR/`` in obsidian-spaced-repetition
    format (``#flashcards`` tag; front ``?`` back), with the card's
    sync state in frontmatter, plus an index note. ``states`` maps
    card_id -> scheduler state dict (its ``due``/``interval_days``
    are carried into frontmatter when present).

    Returns a receipt {vault, dir, notes, scheduler}.
    """
    get_scheduler(scheduler)  # validate the name before writing anything
    root = Path(vault_dir) / "StudySprint SR"
    root.mkdir(parents=True, exist_ok=True)
    states = states or {}
    written = []
    for card in cards:
        p = root / f"{card.card_id}.md"
        p.write_text(_note_text(card, states.get(card.card_id), scheduler))
        written.append(p.name)
    index = ["# StudySprint SR", "",
             f"Scheduler of record: `{scheduler}` · cards: {len(cards)}",
             ""]
    for card in cards:
        index.append(f"- [[{card.card_id}]] — {card.front[:80]}")
    (root / "StudySprint SR Index.md").write_text("\n".join(index) + "\n")
    return {"vault": str(vault_dir), "dir": str(root),
            "notes": len(written), "scheduler": scheduler}


def _state_from_text(text: str, origin: str = "note") -> dict:
    m = _FRONTMATTER.match(text or "")
    if not m:
        raise ValueError(f"no frontmatter in {origin}")
    out = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip()
    interval = out.get("interval_days", "")
    return {
        "card_id": out.get("card_id", ""),
        "scheduler": out.get("scheduler", ""),
        "due": out.get("due", ""),
        "interval_days": float(interval) if interval else None,
    }


def read_obsidian_card_state(note_path) -> dict:
    """Parse one vault note's frontmatter back into a sync state
    {card_id, scheduler, due, interval_days} — the vault -> core
    sync point."""
    return _state_from_text(Path(note_path).read_text(),
                            origin=str(note_path))


def import_obsidian_states(vault_dir) -> dict:
    """Read every card note under the vault surface back into
    {card_id: sync state}."""
    root = Path(vault_dir) / "StudySprint SR"
    states = {}
    if not root.exists():
        return states
    for p in sorted(root.glob("*.md")):
        if p.name == "StudySprint SR Index.md":
            continue
        st = read_obsidian_card_state(p)
        if st["card_id"]:
            states[st["card_id"]] = st
    return states



# ------------------------------------------- Obsidian bridge (seeded from
# bin/obsidian_server.py @master, blob d47a329c5ff1 — adapt-across: the
# SR surface speaks the fleet adapter's existing protocol instead of
# inventing a new one)

BRIDGE_URL = "http://127.0.0.1:8085"
BRIDGE_TOKEN_FILE = "~/.obsidian_termux_token"
VAULT_SUBDIR = "StudySprint SR"


def load_bridge_token(token_file: str = BRIDGE_TOKEN_FILE):
    """Read the bridge token exactly as the adapter does: the file
    must exist and must NOT be a symlink (a symlink could redirect
    the read to another file). Returns None when unavailable."""
    p = Path(token_file).expanduser()
    if p.exists() and not p.is_symlink():
        return p.read_text(encoding="utf-8").strip()
    return None


class ObsidianBridge:
    """Client for the fleet Obsidian bridge (bin/obsidian_server.py).

    The bridge is an authenticated command channel into the device
    hosting the vault: POST {cmd, cwd} with a Bearer token; the
    adapter runs the command under $HOME and returns {output, cwd}.
    ``opener`` is injectable for tests: opener(url, data, headers)
    -> (status, body_text).
    """

    def __init__(self, url: str = BRIDGE_URL, token: str | None = None,
                 token_file: str = BRIDGE_TOKEN_FILE, opener=None):
        self.url = url
        self.token = token if token is not None else load_bridge_token(token_file)
        self._opener = opener or self._urllib_opener

    @staticmethod
    def _urllib_opener(url, data, headers):
        import urllib.error
        import urllib.request
        req = urllib.request.Request(url, data=data, headers=headers,
                                     method="POST")
        try:
            with urllib.request.urlopen(req, timeout=35) as resp:
                return resp.status, resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode("utf-8", "replace")

    def run(self, cmd: str, cwd: str = "") -> dict:
        if not self.token:
            raise RuntimeError(
                "no Obsidian bridge token (expected "
                f"{BRIDGE_TOKEN_FILE}, symlink-rejected — see "
                "bin/obsidian_server.py)")
        payload = json.dumps({"cmd": cmd, "cwd": cwd}).encode()
        status, body = self._opener(
            self.url, payload,
            {"Authorization": f"Bearer {self.token}",
             "Content-Type": "application/json"})
        if status != 200:
            raise RuntimeError(
                f"Obsidian bridge HTTP {status}: {body[:160]}")
        return json.loads(body)


def push_cards_to_vault(bridge: ObsidianBridge, vault: str, cards,
                        states: dict | None = None,
                        scheduler: str = "fsrs") -> dict:
    """Sync point (core -> vault): write every card note into the
    device vault through the bridge. Note bytes travel base64-encoded
    so no shell quoting can corrupt them. Returns a receipt."""
    get_scheduler(scheduler)  # validate before spending bridge calls
    states = states or {}
    bridge.run(f"mkdir -p '{VAULT_SUBDIR}'", cwd=vault)
    for card in cards:
        text = _note_text(card, states.get(card.card_id), scheduler)
        b64 = base64.b64encode(text.encode()).decode()
        bridge.run(
            f"printf '%s' '{b64}' | base64 -d > "
            f"'{VAULT_SUBDIR}/{card.card_id}.md'", cwd=vault)
    index_lines = ["# StudySprint SR", "",
                   f"Scheduler of record: `{scheduler}` - cards: {len(cards)}",
                   ""]
    index_lines += [f"- [[{c.card_id}]] - {c.front[:80]}" for c in cards]
    index = chr(10).join(index_lines) + chr(10)
    b64 = base64.b64encode(index.encode()).decode()
    bridge.run(
        f"printf '%s' '{b64}' | base64 -d > "
        f"'{VAULT_SUBDIR}/StudySprint SR Index.md'", cwd=vault)
    return {"vault": vault, "dir": VAULT_SUBDIR, "notes": len(cards),
            "scheduler": scheduler, "via": "obsidian-bridge"}


def pull_states_from_vault(bridge: ObsidianBridge, vault: str) -> dict:
    """Sync point (vault -> core): list the vault surface through the
    bridge and read every card note's frontmatter back into
    {card_id: sync state}."""
    listing = bridge.run(f"ls -1 '{VAULT_SUBDIR}'", cwd=vault)
    states = {}
    for name in (listing.get("output") or "").splitlines():
        name = name.strip()
        if not name.endswith(".md") or name == "StudySprint SR Index.md":
            continue
        got = bridge.run(f"cat '{VAULT_SUBDIR}/{name}'", cwd=vault)
        st = _state_from_text(got.get("output") or "", origin=name)
        if st["card_id"]:
            states[st["card_id"]] = st
    return states


# ------------------------------------------------------------ ts-fsrs seed

_TS_FSRS_STATES = {1: "Learning", 2: "Review", 3: "Relearning"}


def to_ts_fsrs_state(fsrs_state: dict, now: datetime | None = None) -> dict:
    """Map a py-fsrs card state dict onto the ts-fsrs ``Card`` shape
    the UX layer seeds from: {due, stability, difficulty, elapsed_days,
    scheduled_days, reps, lapses, state}. py-fsrs does not track reps /
    lapses / elapsed counters (ts-fsrs does); those map from the state
    when present and default to 0, and a never-reviewed card maps to
    ts-fsrs ``New``."""
    due = fsrs_state.get("due", "")
    last_review = fsrs_state.get("last_review")
    scheduled = fsrs_state.get("scheduled_days")
    if scheduled is None and due and last_review:
        scheduled = (datetime.fromisoformat(str(due).replace("Z", "+00:00"))
                     - datetime.fromisoformat(
                         str(last_review).replace("Z", "+00:00"))
                     ).total_seconds() / 86400.0
    state_name = "New" if not last_review else _TS_FSRS_STATES.get(
        fsrs_state.get("state"), "Review")
    return {
        "due": due,
        "stability": fsrs_state.get("stability"),
        "difficulty": fsrs_state.get("difficulty"),
        "elapsed_days": fsrs_state.get("elapsed_days", 0),
        "scheduled_days": scheduled if scheduled is not None else 0,
        "reps": fsrs_state.get("reps", 0),
        "lapses": fsrs_state.get("lapses", 0),
        "state": state_name,
        "last_review": last_review,
    }


def export_ux_state(cards, states: dict, now: datetime | None = None) -> dict:
    """Assemble the ts-fsrs seed document for the UX layer:
    {"format": "ts-fsrs/v1", "scheduler": "fsrs", "cards": [...]} —
    JSON-serializable throughout."""
    now = now or datetime.now(timezone.utc)
    return {
        "format": "ts-fsrs/v1",
        "scheduler": "fsrs",
        "generated_at": _iso(now),
        "cards": [
            {"card_id": c.card_id, "front": c.front, "back": c.back,
             "ts_fsrs": to_ts_fsrs_state(states.get(c.card_id) or {},
                                         now=now)}
            for c in cards
        ],
    }
