"""telemetry_export.py — the telemetry dispatcher for the dispatch pipeline.

Emits, per captured conversation, the repo's record artifacts in their
exact schemas (all verified at termux-monorepo master):

  records.jsonl          provenance-export-record/v1
                         (scripts/provenance/ingest_exports.py: record_id =
                         sha256(source_ns|origin|native_id|kind)[:20],
                         scrub() credential shapes -> existence + sha256,
                         classify_record() chat-intent gap entry when the
                         repo classifier is not importable locally,
                         join_actions() refs/verdict over an empty runs
                         index — publication joins real runs later)
  session-history.jsonl  chat-provenance/v1 turn records
                         (ops/telemetry/session-history.jsonl shape)
  session-pointers.jsonl session-pointer/v1 lines, one per history record,
                         feed{line, line_sha256, path} pointing at the
                         history line as written

Mapping choices (surface-forced, everything else field-for-field):
  actor          user turns -> "owner" (the account holder), assistant
                 turns -> "chatgpt"; actor_evidence.detail.role carries
                 the turn role, method "surface".
  route          "webwrapper" (the sample's route names its own surface
                 route, "api-token" for the Muse API surface).
  turn_anchor    f"{conversation_id}#m{i}" — ChatGPT captures expose no
                 per-message native id; the ingest native_id form is the
                 traceable local equivalent.
  target.kind    "chatgpt-message" (sample: "muse-message");
                 resolution_route names the local session store.
Appends are deduped by record_id / dispatch_id, so pipeline re-fires
(listener sweeps, core save hooks) never duplicate a record.
"""
import hashlib
import json
import os
import re
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
EXPORTS_DIR = os.path.join(BASE, "exports")
RECORDS = os.path.join(EXPORTS_DIR, "records.jsonl")
HISTORY = os.path.join(EXPORTS_DIR, "session-history.jsonl")
POINTERS = os.path.join(EXPORTS_DIR, "session-pointers.jsonl")
HISTORY_FEED_PATH = "exports/session-history.jsonl"
SOURCE_NS_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")
SOURCE_NS = f"chatgpt-webwrapper/{SOURCE_NS_DATE}"
ROUTE = "webwrapper"

SCHEMA_RECORD = "provenance-export-record/v1"
INGEST_VERSION = "provenance-ingest v1"
SCHEMA_HISTORY = "chat-provenance/v1"
SCHEMA_POINTER = "session-pointer/v1"

# Copied verbatim from scripts/provenance/ingest_exports.py (master).
SECRET_SHAPES = re.compile(
    r"(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_\-]{20,}|AIza[0-9A-Za-z_\-]{30,}|"
    r"xox[abpr]-[A-Za-z0-9\-]{10,}|hf_[A-Za-z0-9]{20,})")
PR_REF = re.compile(r"(?:github\.com/[\w.\-]+/[\w.\-]+/pull/|PR\s*#|pull request #|(?<![\w/])#)(\d{2,6})\b", re.I)
SHA_REF = re.compile(r"\b[0-9a-f]{40}\b")
BRANCH_REF = re.compile(r"\b(?:branch|head)[:= ]+`?([\w./\-]{3,120})`?", re.I)


def _stamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def scrub(text):
    """ingest_exports.scrub: credential-shaped strings -> existence + sha256."""
    found = []

    def repl(m):
        digest = hashlib.sha256(m.group(0).encode()).hexdigest()
        found.append({"kind": "credential-shape", "sha256": digest})
        return f"[credential sha256:{digest[:12]}]"

    return SECRET_SHAPES.sub(repl, text or ""), found


def classify_record(text):
    """ingest_exports.classify_record with the repo chat-intent classifier
    not importable from the wrapper dir: the record carries the gap entry,
    exactly as the model's own fallback writes it."""
    if text:
        return [{"classifier_id": "chat_intent", "classifier_version": None, "label": None,
                 "confidence": None, "rule": "classifier-unavailable"}]
    return []


def join_actions(text):
    """ingest_exports.join_actions over an empty runs index (publication
    joins Actions evidence later, in the repo)."""
    prs = sorted({m.group(1) for m in PR_REF.finditer(text or "")})
    shas = sorted(set(SHA_REF.findall(text or "")))
    branches = sorted({m.group(1) for m in BRANCH_REF.finditer(text or "")})
    claimed = bool(prs or shas or branches)
    verdict = "no-claim" if not claimed else "claim-unevidenced"
    return {"refs": {"prs": prs, "shas": shas, "branches": branches},
            "runs": [], "run_count": 0, "verdict": verdict}


def _existing_ids(path, field):
    ids = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        ids.add(json.loads(line).get(field))
                    except Exception:
                        pass
    return ids


def _line_count(path):
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8") as f:
        return sum(1 for _ in f)


def provenance_record(origin, conversation_id, native_id, kind, text, ts, stamp):
    clean, creds = scrub(text)
    rid = hashlib.sha256(f"{SOURCE_NS}|{origin}|{native_id}|{kind}".encode()).hexdigest()[:20]
    rec = {
        "schema": SCHEMA_RECORD, "ingest_version": INGEST_VERSION, "record_id": rid,
        "source_ns": SOURCE_NS, "origin": origin, "export_class": "message", "kind": kind,
        "session": conversation_id, "native_id": native_id, "ts": ts,
        "text_sha256": hashlib.sha256(clean.encode()).hexdigest(), "text_chars": len(clean),
        "excerpt": clean[:280], "credentials": creds,
        "classifications": classify_record(clean),
        "actions": join_actions(clean), "ingested_at": stamp,
    }
    return rec, clean, creds


def history_record(conversation_id, turn_anchor, role, clean, creds, ts, stamp):
    actor = "owner" if role == "user" else "chatgpt"
    dispatch_id = f"sess:{conversation_id}:{turn_anchor}"
    return {
        "actor": actor,
        "actor_evidence": {"detail": {"role": role}, "method": "surface"},
        "actor_registry_keyed": False,
        "chat_id": conversation_id,
        "content": clean,
        "content_chars": len(clean),
        "content_sha256": hashlib.sha256(clean.encode()).hexdigest(),
        "dispatch_id": dispatch_id,
        "generated_at": stamp,
        "origin": "session-history",
        "outcome": {"confirmed": None},
        "redactions": len(creds),
        "role": role,
        "route": ROUTE,
        "schema": SCHEMA_HISTORY,
        "thinking": "WITHHELD_BY_PLATFORM",
        "tool_calls": "NOT_EXPOSED_BY_ROUTE",
        "ts": ts,
        "turn_anchor": turn_anchor,
    }


def dispatch_telemetry(session_id, messages, origin="session_store", turn_ts=None):
    """Dispatcher signature per archwiz/dispatch_pipeline.py:
    (session_id, messages) -> None. Registered in dispatch_pipeline.py.
    turn_ts: optional list of per-turn ISO timestamps (None entries ok)."""
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    stamp = _stamp()
    seen_records = _existing_ids(RECORDS, "record_id")
    seen_history = _existing_ids(HISTORY, "dispatch_id")
    hist_lines = _line_count(HISTORY)
    new_records, new_history, new_pointers = [], [], []
    for i, msg in enumerate(messages):
        role = (msg or {}).get("role") or "unknown"
        text = (msg or {}).get("content") or ""
        ts = None
        if turn_ts and i < len(turn_ts):
            ts = turn_ts[i]
        if ts is None:
            ts = (msg or {}).get("ts")
        native_id = f"{session_id}#m{i}"
        kind = f"turn:{role}"
        rec, clean, creds = provenance_record(origin, session_id, native_id, kind, text, ts, stamp)
        if rec["record_id"] not in seen_records:
            new_records.append(rec)
            seen_records.add(rec["record_id"])
        turn_anchor = native_id
        hist = history_record(session_id, turn_anchor, role, clean, creds, ts, stamp)
        if hist["dispatch_id"] not in seen_history:
            line_no = hist_lines + len(new_history) + 1
            line_text = json.dumps(hist, ensure_ascii=False, sort_keys=True)
            new_history.append(line_text)
            seen_history.add(hist["dispatch_id"])
            new_pointers.append({
                "actor": hist["actor"],
                "content_chars": hist["content_chars"],
                "content_sha256": hist["content_sha256"],
                "dispatch_id": hist["dispatch_id"],
                "feed": {"line": line_no,
                         "line_sha256": hashlib.sha256(line_text.encode()).hexdigest(),
                         "path": HISTORY_FEED_PATH},
                "route": ROUTE,
                "schema": SCHEMA_POINTER,
                "target": {"chat_id": session_id, "kind": "chatgpt-message",
                           "resolution_route": "chatgpt webwrapper session store (chat_id + turn_anchor)",
                           "turn_anchor": turn_anchor},
                "ts": ts,
            })
    if new_records:
        with open(RECORDS, "a", encoding="utf-8") as f:
            for r in new_records:
                f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    if new_history:
        with open(HISTORY, "a", encoding="utf-8") as f:
            for lt in new_history:
                f.write(lt + "\n")
        with open(POINTERS, "a", encoding="utf-8") as f:
            for p in new_pointers:
                f.write(json.dumps(p, ensure_ascii=False, sort_keys=True) + "\n")
    return {"records": len(new_records), "history": len(new_history), "pointers": len(new_pointers)}
