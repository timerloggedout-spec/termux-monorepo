#!/usr/bin/env python3
"""Certifications Phase 1 (Route A): execute one cert work unit in CI.

One unit = one module-block (lesson steps). For each step, one completion
is produced through the fleet invoke harness (scripts/ops/provider_invoke.py,
model auto-resolved from the provider catalog at runtime - no pinning).
Outputs land in --out as one markdown artifact per step plus a stamped
unit-manifest.json {cert, unit, earner, fleet_run, provider, model,
artifacts[sha256]}. Capture happens at execution; session submit/verify
on the platform is the Platforms lane's step, not this runner's.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INVOKE = ROOT / "scripts/ops/provider_invoke.py"
PROMPT_TEMPLATE = (
    "Produce a concise lesson work product for the FreeCodeCamp Relational "
    "Databases v9 lesson \"{title}\": the key concepts in plain terms and "
    "one worked example. Format as markdown with a title line."
)
QUESTIONS_TEMPLATE = (
    "FreeCodeCamp Relational Databases v9 lesson \"{title}\". Answer each "
    "comprehension check below from the lesson content. Begin with a key "
    "block: one line per question, \"KEY Q<n>: <exact option text>\". Then, "
    "for every question: "
    "restate the question verbatim under a heading line \"Q<n>\", then give "
    "the correct option (letter and full text), a one-sentence justification, "
    "and quote the lesson body evidence that supports the answer. After "
    "each answer, emit one line exactly of the form KEY Q<n>: followed by "
    "the correct option text copied verbatim from the options list (no "
    "paraphrase, no letter, no bold or other formatting on the KEY line). If a "
    "question asks which option is NOT mentioned, select the option that is "
    "absent from the lesson body evidence. Questions:\n{questions}{context}"
)


QUIZ_TEMPLATE = (
    "FreeCodeCamp Relational Databases v9 quiz \"{title}\". Answer each "
    "question from the lesson content. For every question emit exactly two "
    "lines: first \"Q<n>:\" plus a one-sentence justification, then "
    "\"KEY Q<n>:\" followed by the correct option text copied verbatim "
    "from the options list (plain text, no bold). Be compact; no restatements. "
    "Questions:\n{questions}{context}"
)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _ordered_subsequence(needle: list[str], haystack: list[str]) -> bool:
    it = iter(haystack)
    return all(any(tok == want for tok in it) for want in needle)


def content_check(text: str, questions: list[str]) -> list[str]:
    """Return the verbatim questions missing (unkeyed/unanswered) in text.

    Matching is token-based (punctuation/markdown-insensitive, ordered
    subsequence of the question sentence's tokens) so a substance-present
    answer keyed Q<n> is not flagged for formatting variance (backticks,
    punctuation, minor inserted words). Platforms' substance audit remains
    the backstop.
    """
    missing = []
    toks = _tokens(text)
    for i, q in enumerate(questions, 1):
        key = f"Q{i}"
        stem_tokens = _tokens(q.split(" Options:")[0])[:12]
        if key not in text or not _ordered_subsequence(stem_tokens, toks):
            missing.append(key)
    return missing
def _norm(text: str) -> str:
    cleaned = re.sub(r"[*_`]+", "", text)
    return " ".join(cleaned.strip().strip("\"'").split()).lower().rstrip(".;")


def parse_options(question: str) -> list[str]:
    if " Options:" not in question:
        return []
    tail = question.split(" Options:", 1)[1]
    return [o.strip() for o in tail.split("; ") if o.strip()]


def keying_check(text: str, questions: list[str]) -> list[str]:
    """Return Q keys whose KEY line is missing or keys a non-option text.

    The prompt mandates one 'KEY Q<n>: <exact option text>' line per
    question; a keyed text outside the manifest option set is rejected
    (002 failure class: misquoted option keyed anyway).
    """
    bad = []
    keyed = {}
    for m in re.finditer(r"KEY\s+Q(\d+)\s*:\s*(.+)", text):
        keyed[int(m.group(1))] = m.group(2).strip()
    fallback = [m.group(1).strip() for m in
                re.finditer(r"Correct Option\s*:\s*(.+)", text)]
    if fallback:
        unkeyed = [i for i in range(1, len(questions) + 1) if i not in keyed]
        for idx, val in zip(unkeyed, fallback):
            keyed[idx] = val
    for i, q in enumerate(questions, 1):
        options = parse_options(q)
        if not options:
            continue
        got = keyed.get(i)
        if got is None or _norm(got) not in {_norm(o) for o in options}:
            bad.append(f"Q{i}")
    return bad


WORKSHOP_TEMPLATE = (
    "Produce the complete work product for the FreeCodeCamp Relational "
    "Databases v9 workshop \"{title}\": every file the workshop builds, "
    "each as a fenced code block headed by its file path, followed by the "
    "commands used to create and verify it and a short verification note. "
    "Format as markdown with a title line."
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="unit manifest JSON path")
    ap.add_argument("--provider", default="cohere")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    unit = json.loads(Path(args.manifest).read_text())
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    artifacts = []
    model_seen = None
    failures = 0
    for step in unit["steps"]:
        prompt_file = out / f".prompt-{step['id']}.md"
        questions = step.get("questions") or []
        if questions:
            qs = "\n".join(f"Q{i}: {q}" for i, q in enumerate(questions, 1))
            ctx = step.get("context") or ""
            ctx_block = f"\nLesson body evidence (verbatim):\n{ctx}" if ctx else ""
            template = QUIZ_TEMPLATE if step.get("kind") == "quiz" else QUESTIONS_TEMPLATE
            prompt_file.write_text(template.format(title=step["title"], questions=qs, context=ctx_block))
        else:
            template = WORKSHOP_TEMPLATE if step.get("kind") == "workshop" else PROMPT_TEMPLATE
            prompt_file.write_text(template.format(title=step["title"]))
        artifact = out / f"{step['id']}.md"
        invoke_cmd = [sys.executable, str(INVOKE), "--provider", args.provider,
                      "--prompt-file", str(prompt_file), "--out", str(artifact)]
        invoke_cmd += ["--max-tokens", "2000" if step.get("kind") == "quiz" else "1500"]
        proc = subprocess.run(invoke_cmd, capture_output=True, text=True, timeout=600)
        verdict = {}
        for line in proc.stdout.splitlines():
            if line.startswith("INVOKE_VERDICT "):
                verdict = json.loads(line.split(" ", 1)[1])
        if verdict.get("model") == "default":
            # Catalog resolution failed transiently (model unresolved ->
            # "default" -> chat 404, no artifact). One re-invoke after a
            # pause; the model is still auto-resolved on the retry.
            import time
            time.sleep(20)
            proc = subprocess.run(
                [sys.executable, str(INVOKE), "--provider", args.provider,
                 "--prompt-file", str(prompt_file), "--out", str(artifact)],
                capture_output=True, text=True, timeout=600)
            verdict = {}
            for line in proc.stdout.splitlines():
                if line.startswith("INVOKE_VERDICT "):
                    verdict = json.loads(line.split(" ", 1)[1])
        ok = proc.returncode == 0 and verdict.get("ok") is True
        missing = []
        if ok and questions:
            text = artifact.read_text(errors="replace") if artifact.exists() else ""
            if step.get("kind") == "quiz":
                missing = [f"Q{i}" for i in range(1, len(questions) + 1)
                           if not re.search(rf"KEY\s+Q{i}\s*:", text)]
            else:
                missing = content_check(text, questions)
            keying_bad = keying_check(text, questions)
            missing = missing + [f"{k}-key" for k in keying_bad]
            if missing:
                ok = False
        if verdict.get("model"):
            model_seen = verdict["model"]
        if not ok:
            failures += 1
        artifacts.append({
            "step": step["id"], "title": step["title"], "ok": ok,
            "content_missing": missing,
            "http": verdict.get("http"),
            "path": artifact.name,
            "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()
            if artifact.exists() else None,
        })
        prompt_file.unlink(missing_ok=True)
    stamp = {
        "cert": unit["cert"], "unit": unit["unit"],
        "earner": "termux-monorepo",
        "fleet_run": run_id, "provider": args.provider,
        "model": model_seen,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifacts": artifacts,
    }
    (out / "unit-manifest.json").write_text(json.dumps(stamp, indent=2) + "\n")
    missing_map = {a["step"]: a["content_missing"] for a in artifacts
                   if a.get("content_missing")}
    print("UNIT_VERDICT " + json.dumps(
        {"unit": unit["unit"], "ok": failures == 0,
         "steps": len(artifacts), "failures": failures, "model": model_seen,
         "missing": missing_map}))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
