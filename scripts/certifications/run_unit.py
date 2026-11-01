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
    "comprehension check below from the lesson content. For every question: "
    "restate the question verbatim under a heading line \"Q<n>\", then give "
    "the correct option (letter and full text), a one-sentence justification, "
    "and quote the lesson body evidence that supports the answer. If a "
    "question asks which option is NOT mentioned, select the option that is "
    "absent from the lesson body evidence. Questions:\n{questions}{context}"
)


def content_check(text: str, questions: list[str]) -> list[str]:
    """Return the verbatim questions missing (unkeyed/unanswered) in text."""
    missing = []
    for i, q in enumerate(questions, 1):
        key = f"Q{i}"
        stem = " ".join(q.split(" Options:")[0].split())[:60]
        if key not in text or stem not in " ".join(text.split()):
            missing.append(key)
    return missing
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
            prompt_file.write_text(QUESTIONS_TEMPLATE.format(title=step["title"], questions=qs, context=ctx_block))
        else:
            template = WORKSHOP_TEMPLATE if step.get("kind") == "workshop" else PROMPT_TEMPLATE
            prompt_file.write_text(template.format(title=step["title"]))
        artifact = out / f"{step['id']}.md"
        proc = subprocess.run(
            [sys.executable, str(INVOKE), "--provider", args.provider,
             "--prompt-file", str(prompt_file), "--out", str(artifact)],
            capture_output=True, text=True, timeout=600)
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
            missing = content_check(text, questions)
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
