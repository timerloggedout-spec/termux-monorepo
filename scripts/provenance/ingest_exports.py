#!/usr/bin/env python3
"""Provenance export ingest (#5555) — classify-on-ingest ⊕ Actions join.

DO ingest every export record of the two agent-side classes:
  message  := seat/side-chat transcript turns (Muse side-chat clones, ChatGPT, other surfaces)
  thinking := reasoning artifacts (Jules prompts ∧ plans ∧ agent messages ∧ progress updates)
DO classify AT ingestion: each record carries
  classifications[] := {classifier_id, classifier_version, label, confidence, rule}
  ↳ chat-intent (scripts/classifiers/chat_intent.py) on every text record
  ↳ PR-lane (ml/pipelines/lanes/classify.py) on every record that carries a pull request
DO join each record to Actions run evidence (head_sha ∨ head_branch ∨ PR number) ⇒ comparison verdict:
  consistent        := claim references code ∧ ∃ run evidence
  claim-unevidenced := claim references code ∧ ∄ run evidence
  no-claim          := record references ∅ code artifact
DO keep per-source namespaces distinct (source_ns); credential-shaped strings ⇒ existence ∧ sha256 only.
Source of record for the Jules corpus: VM batch export (417 sessions) ⇒ private store
`jules-harvest/2026-11-17/` (¬ re-harvest ∧ ¬ hand-copy).

Usage:
  python3 scripts/provenance/ingest_exports.py --source-ns jules-harvest/2026-11-17 \
      --input <dir|file.json|file.jsonl> [--runs actions-runs.json] --out records.jsonl
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Iterator

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "classifiers"))

SCHEMA = "provenance-export-record/v1"
INGEST_VERSION = "provenance-ingest v1"
DISCOVERY_SCHEMA = "muse-side-chat-discovery/v1"
DISCOVERY_PATTERNS = (
    ("moniker", re.compile(r"\bmonikers?\\b", re.I)),
    ("collision", re.compile(r"\bcollisions?\\b", re.I)),
    ("marketing", re.compile(r"\bmarketing\\b", re.I)),
    ("naming", re.compile(r"\bnaming\\b", re.I)),
    ("anon", re.compile(r"\banon(?:ymous|ymity)?\\b", re.I)),
    ("4n0nSEC", re.compile(r"(?<![A-Za-z0-9_])4n0nsec(?![A-Za-z0-9_])", re.I)),
    ("4n∅N", re.compile(r"(?<![A-Za-z0-9_])4n∅n(?![A-Za-z0-9_])", re.I)),
    ("4n∅nSEC", re.compile(r"(?<![A-Za-z0-9_])4n∅nsec(?![A-Za-z0-9_])", re.I)),
    ("profiles", re.compile(r"\bprofiles?\\b", re.I)),
)
SECRET_SHAPES = re.compile(
    r"(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_\-]{20,}|AIza[0-9A-Za-z_\-]{30,}|"
    r"xox[abpr]-[A-Za-z0-9\-]{10,}|hf_[A-Za-z0-9]{20,})")
PR_REF = re.compile(r"(?:github\.com/[\w.\-]+/[\w.\-]+/pull/|PR\s*#|pull request #|(?<![\w/])#)(\d{2,6})\b", re.I)
SHA_REF = re.compile(r"\b[0-9a-f]{40}\b")
BRANCH_REF = re.compile(r"\b(?:branch|head)[:= ]+`?([\w./\-]{3,120})`?", re.I)

# Rule-tier confidence per matched rule: rules with an explicit form match carry more weight
# than defaults. Calibration is owed to the labeled-outcome gate (n≥30/class) — ⊬ accuracy claim.
RULE_CONFIDENCE = {"R1": 0.85, "R2": 0.8, "R3": 0.8, "R4": 0.6, "R5": 0.7, "R6": 0.65, "R7": 0.55, "R8": 0.3}


def file_version(path: Path) -> str:
    try:
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    except OSError:
        return "unavailable"


def scrub(text: str) -> tuple[str, list[dict[str, str]]]:
    found = []

    def repl(m: re.Match[str]) -> str:
        digest = hashlib.sha256(m.group(0).encode()).hexdigest()
        found.append({"kind": "credential-shape", "sha256": digest})
        return f"[credential sha256:{digest[:12]}]"

    return SECRET_SHAPES.sub(repl, text or ""), found


def _chat_intent():
    try:
        import chat_intent  # type: ignore
        return chat_intent, file_version(ROOT / "scripts" / "classifiers" / "chat_intent.py")
    except Exception:  # pragma: no cover - classifier absent ⇒ record carries the gap
        return None, None


def _pr_lane():
    try:
        from ml.pipelines.lanes.classify import classify_pr
        return classify_pr, file_version(ROOT / "ml" / "pipelines" / "lanes" / "classify.py")
    except Exception:  # pragma: no cover
        return None, None


CHAT_INTENT, CHAT_INTENT_VERSION = _chat_intent()
CLASSIFY_PR, CLASSIFY_PR_VERSION = _pr_lane()


def classify_record(text: str, pull_request: dict[str, Any] | None) -> list[dict[str, Any]]:
    out = []
    if CHAT_INTENT is not None and text:
        res = CHAT_INTENT.classify(text[:4000])
        rule = str(res.get("rule") or "")
        out.append({"classifier_id": "chat_intent", "classifier_version": f"{CHAT_INTENT.VERSION}@{CHAT_INTENT_VERSION}",
                    "label": res.get("intent"), "confidence": RULE_CONFIDENCE.get(rule.split("-", 1)[0], 0.3),
                    "rule": rule})
    elif text:
        out.append({"classifier_id": "chat_intent", "classifier_version": None, "label": None,
                    "confidence": None, "rule": "classifier-unavailable"})
    if pull_request and CLASSIFY_PR is not None:
        lane = CLASSIFY_PR(pull_request)
        out.append({"classifier_id": "ml.pipelines.lanes.classify", "classifier_version": CLASSIFY_PR_VERSION,
                    "label": getattr(lane, "value", str(lane)), "confidence": 1.0, "rule": "deterministic-rules"})
    return out


def _text(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        for k in ("text", "content", "agentMessage", "userMessage", "description", "title", "message"):
            if isinstance(v.get(k), str):
                return v[k]
        if isinstance(v.get("parts"), list):
            return "\n".join(_text(p) for p in v["parts"])
    if isinstance(v, list):
        return "\n".join(_text(x) for x in v)
    return str(v)


def _pr_from_outputs(session: dict[str, Any]) -> dict[str, Any] | None:
    for o in session.get("outputs") or []:
        pr = (o or {}).get("pullRequest")
        if pr:
            m = PR_REF.search(str(pr.get("url") or ""))
            return {"number": int(m.group(1)) if m else None, "title": pr.get("title"), "url": pr.get("url"),
                    "base": pr.get("base") or "master", "head_branch": pr.get("headRef") or pr.get("head_branch"),
                    "draft": pr.get("draft", False)}
    return None


def explode(obj: Any, origin: str) -> Iterator[dict[str, Any]]:
    """Yield raw units {kind, class, text, ts, session, pull_request, native_id} from one export object."""
    if isinstance(obj, list):
        for x in obj:
            yield from explode(x, origin)
        return
    if not isinstance(obj, dict):
        return
    if "sessions" in obj and isinstance(obj["sessions"], list):
        for s in obj["sessions"]:
            yield from explode(s, origin)
        return
    if "prompt" in obj or "activities" in obj or "plan" in obj:  # Jules-shaped session (thinking class)
        sid = str(obj.get("id") or obj.get("name") or origin)
        pr = _pr_from_outputs(obj)
        ts0 = obj.get("createTime") or obj.get("created_at")
        if obj.get("prompt"):
            yield {"kind": "prompt", "class": "thinking", "text": _text(obj["prompt"]), "ts": ts0,
                   "session": sid, "pull_request": pr, "native_id": f"{sid}#prompt"}
        plan = obj.get("plan")
        if plan:
            steps = plan.get("steps") if isinstance(plan, dict) else plan
            yield {"kind": "plan", "class": "thinking", "text": _text(steps), "ts": ts0, "session": sid,
                   "pull_request": pr, "native_id": f"{sid}#plan"}
        for i, act in enumerate(obj.get("activities") or []):
            kind, body = "activity", act
            for k in ("agentMessaged", "userMessaged", "planGenerated", "progressUpdated", "sessionCompleted"):
                if k in act:
                    kind, body = k, act[k]
            if kind == "planGenerated":
                body = (body or {}).get("plan", {}).get("steps") if isinstance(body, dict) else body
            yield {"kind": kind, "class": "message" if kind == "userMessaged" else "thinking", "text": _text(body),
                   "ts": act.get("createTime") or ts0, "session": sid, "pull_request": pr,
                   "native_id": str(act.get("id") or f"{sid}#a{i}")}
        return
    if "messages" in obj and isinstance(obj["messages"], list):  # chat transcript export (message class)
        cid = str(obj.get("id") or obj.get("conversation_id") or origin)
        for i, m in enumerate(obj["messages"]):
            yield {"kind": f"turn:{(m or {}).get('role') or (m or {}).get('author') or 'unknown'}", "class": "message",
                   "text": _text(m.get("content") if isinstance(m, dict) else m),
                   "ts": (m or {}).get("created_at") or (m or {}).get("ts"), "session": cid, "pull_request": None,
                   "native_id": str((m or {}).get("id") or f"{cid}#m{i}")}
        return
    if "role" in obj and ("content" in obj or "text" in obj):  # one message per line (jsonl)
        yield {"kind": f"turn:{obj['role']}", "class": "message", "text": _text(obj.get("content") or obj.get("text")),
               "ts": obj.get("created_at") or obj.get("ts"), "session": str(obj.get("conversation_id") or origin),
               "pull_request": None, "native_id": str(obj.get("id") or "")}


def iter_inputs(path: Path) -> Iterator[tuple[str, Any]]:
    files: Iterable[Path] = sorted(p for p in path.rglob("*") if p.suffix in (".json", ".jsonl")) if path.is_dir() else [path]
    for f in files:
        rel = str(f.relative_to(path)) if path.is_dir() else f.name
        if f.suffix == ".jsonl":
            for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if line.strip():
                    yield f"{rel}:{n}", json.loads(line)
        else:
            yield rel, json.loads(f.read_text(encoding="utf-8"))


def index_runs(runs: list[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    idx: dict[str, dict[str, list[dict[str, Any]]]] = {"sha": {}, "branch": {}, "pr": {}}
    for r in runs:
        slim = {"id": r.get("id"), "name": r.get("name"), "conclusion": r.get("conclusion"),
                "status": r.get("status"), "event": r.get("event"), "created_at": r.get("created_at"),
                "head_sha": r.get("head_sha"), "url": r.get("html_url")}
        if r.get("head_sha"):
            idx["sha"].setdefault(r["head_sha"], []).append(slim)
        if r.get("head_branch"):
            idx["branch"].setdefault(r["head_branch"], []).append(slim)
        for p in r.get("pull_requests") or []:
            if p.get("number"):
                idx["pr"].setdefault(str(p["number"]), []).append(slim)
    return idx


def join_actions(text: str, pr: dict[str, Any] | None, idx: dict[str, Any]) -> dict[str, Any]:
    prs = sorted({m.group(1) for m in PR_REF.finditer(text or "")} | ({str(pr["number"])} if pr and pr.get("number") else set()))
    shas = sorted(set(SHA_REF.findall(text or "")))
    branches = sorted({m.group(1) for m in BRANCH_REF.finditer(text or "")} |
                      ({pr["head_branch"]} if pr and pr.get("head_branch") else set()))
    runs: dict[Any, dict[str, Any]] = {}
    for key, vals in (("pr", prs), ("sha", shas), ("branch", branches)):
        for v in vals:
            for r in idx.get(key, {}).get(v, []):
                runs[r["id"]] = r
    claimed = bool(prs or shas or branches)
    verdict = "no-claim" if not claimed else ("consistent" if runs else "claim-unevidenced")
    return {"refs": {"prs": prs, "shas": shas, "branches": branches},
            "runs": sorted(runs.values(), key=lambda r: str(r.get("created_at") or ""))[:20],
            "run_count": len(runs), "verdict": verdict}


def muse_discovery_terms(text: str, source_ns: str) -> list[str]:
    """Return versioned, privacy-safe topic labels for Muse side-chat message exports."""
    if not source_ns.startswith("muse-side-chat/"):
        return []
    return [label for label, pattern in DISCOVERY_PATTERNS if pattern.search(text or "")]


def ingest(path: Path, source_ns: str, runs: list[dict[str, Any]] | None = None,
           now: str | None = None) -> list[dict[str, Any]]:
    idx = index_runs(runs or [])
    stamp = now or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    out = []
    for origin, obj in iter_inputs(path):
        for unit in explode(obj, origin):
            text, creds = scrub(unit["text"])
            rid = hashlib.sha256(f"{source_ns}|{origin}|{unit['native_id']}|{unit['kind']}".encode()).hexdigest()[:20]
            out.append({
                "schema": SCHEMA, "ingest_version": INGEST_VERSION, "record_id": rid,
                "source_ns": source_ns, "origin": origin, "export_class": unit["class"], "kind": unit["kind"],
                "session": unit["session"], "native_id": unit["native_id"], "ts": unit["ts"],
                "text_sha256": hashlib.sha256(text.encode()).hexdigest(), "text_chars": len(text),
                "excerpt": text[:280], "credentials": creds,
                "classifications": classify_record(text, unit["pull_request"]),
                "actions": join_actions(text, unit["pull_request"], idx), "ingested_at": stamp,
            })
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Provenance export ingest (#5555)")
    ap.add_argument("--input", required=True)
    ap.add_argument("--source-ns", required=True)
    ap.add_argument("--runs", help="JSON: Actions runs list ∨ {workflow_runs: [...]}")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    runs = []
    if a.runs:
        raw = json.loads(Path(a.runs).read_text(encoding="utf-8"))
        runs = raw.get("workflow_runs", []) if isinstance(raw, dict) else raw
    recs = ingest(Path(a.input), a.source_ns, runs)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    classified = sum(1 for r in recs if any(c.get("label") for c in r["classifications"]))
    print(f"::notice title=provenance-ingest::ns={a.source_ns} records={len(recs)} classified={classified} "
          f"joined={sum(1 for r in recs if r['actions']['run_count'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
