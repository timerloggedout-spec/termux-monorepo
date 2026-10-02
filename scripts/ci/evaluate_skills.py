#!/usr/bin/env python3
"""Deterministic structural evaluator for repository SKILL.md and .skill packages."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

VERSION = "1.1"
SECRET_PATTERNS = [
    re.compile(r"(?:sk-[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9_]{20,})"),
    re.compile(r"(?i)(?:api[_-]?key|token|password|secret)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
]


def parse_frontmatter(text: str):
    if not text.startswith("---\n"):
        return None, "missing YAML frontmatter opener"
    end = text.find("\n---", 4)
    if end < 0:
        return None, "missing YAML frontmatter terminator"
    data = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            return None, f"invalid frontmatter line: {line!r}"
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data, None


def dim(ok: bool) -> int:
    return 5 if ok else 1


def failure(identity, source_kind, checks, code):
    return {
        "path": identity,
        "source_kind": source_kind,
        "validator_version": VERSION,
        "input_sha256": None,
        "valid": False,
        "score": 0,
        "dimensions": {},
        "checks": checks,
        "hard_failures": [code],
    }


def evaluate_text(text: str, identity: str, source_kind: str, packaging_ok: bool = True):
    fm, fm_error = parse_frontmatter(text)
    if fm_error:
        return failure(identity, source_kind, {"frontmatter": fm_error}, "frontmatter")

    identity_ok = bool(fm.get("name", "").strip() and fm.get("description", "").strip())
    body = text.split("---", 2)[-1].strip()
    procedure_ok = bool(re.search(r"^#{1,3} .*?(?:workflow|procedure|steps|operating|process)", text, re.I | re.M))
    safety_ok = bool(re.search(r"safe|safety|secret|credential|permission|do not|never", text, re.I))
    evidence_ok = bool(re.search(r"verify|validate|evidence|test|closeout", text, re.I))
    integration_ok = bool(re.search(r"^#{1,3} .*?(?:reference|maintenance|related)|\bReferences\b|\bmaintenance\b|\brelated\b", text, re.I | re.M))
    fences_ok = len(re.findall(r"^```", text, re.MULTILINE)) % 2 == 0
    secrets_ok = not any(p.search(text) for p in SECRET_PATTERNS)

    checks = {
        "frontmatter": "ok",
        "body": "ok" if body else "empty",
        "procedure": "ok" if procedure_ok else "not detected",
        "safety": "ok" if safety_ok else "not detected",
        "verification": "ok" if evidence_ok else "not detected",
        "integration": "ok" if integration_ok else "not detected",
        "fences": "ok" if fences_ok else "unbalanced",
        "secret_scan": "ok" if secrets_ok else "possible secret pattern",
        "packaging": "ok" if packaging_ok else "invalid",
    }
    dimensions = {
        "identity_clarity": dim(identity_ok),
        "procedure_completeness": dim(procedure_ok),
        "safety_boundaries": dim(safety_ok),
        "verification_evidence": dim(evidence_ok),
        "integration_maintenance": dim(integration_ok),
        "packaging_hygiene": dim(packaging_ok and fences_ok and secrets_ok),
    }
    weights = {
        "identity_clarity": 20,
        "procedure_completeness": 20,
        "safety_boundaries": 20,
        "verification_evidence": 20,
        "integration_maintenance": 10,
        "packaging_hygiene": 10,
    }
    score = round(sum(dimensions[k] * weights[k] for k in dimensions) / 5)
    hard_failures = []
    if not identity_ok:
        hard_failures.append("frontmatter_identity")
    if not body:
        hard_failures.append("empty_body")
    if not fences_ok:
        hard_failures.append("unbalanced_fences")
    if not secrets_ok:
        hard_failures.append("secret_pattern")
    if not packaging_ok:
        hard_failures.append("packaging")
    return {
        "path": identity,
        "source_kind": source_kind,
        "validator_version": VERSION,
        "input_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "valid": not hard_failures,
        "score": score,
        "dimensions": dimensions,
        "checks": checks,
        "hard_failures": hard_failures,
    }


def evaluate_package(path: Path):
    try:
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            if any(Path(n).is_absolute() or ".." in Path(n).parts for n in names):
                return failure(str(path), ".skill", {"archive": "unsafe path"}, "archive_path")
            skills = [n for n in names if Path(n).name == "SKILL.md"]
            if len(skills) != 1:
                return failure(
                    str(path),
                    ".skill",
                    {"archive": f"expected exactly one SKILL.md, found {len(skills)}"},
                    "archive_skill_md",
                )
            text = zf.read(skills[0]).decode("utf-8")
            return evaluate_text(text, f"{path}::{skills[0]}", ".skill")
    except (zipfile.BadZipFile, UnicodeDecodeError) as exc:
        return failure(str(path), ".skill", {"archive": f"invalid: {exc}"}, "archive_invalid")


def changed_skill_paths(base_ref: str, head_ref: str, root: Path) -> set[str]:
    """Return changed skill-definition paths for regression gating on a PR."""
    completed = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}..{head_ref}", "--", ".agents", ".github", "docs", "*.skill"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    paths = set()
    for raw in completed.stdout.splitlines():
        path = raw.strip()
        if path.endswith("SKILL.md") or path.endswith(".skill"):
            paths.add(path)
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--baseline-ref", help="Base ref for PR regression gating; inventory remains complete")
    ap.add_argument("--head-ref", default="HEAD", help="Head ref paired with --baseline-ref")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    results = []
    for base in (root / ".agents" / "skills", root / ".github" / "skills", root / "docs" / "ops" / "skills"):
        if base.exists():
            for p in sorted(base.rglob("SKILL.md")):
                results.append(evaluate_text(p.read_text(encoding="utf-8"), p.relative_to(root).as_posix(), "SKILL.md"))
    for p in sorted(root.rglob("*.skill")):
        if ".git" not in p.parts:
            results.append(evaluate_package(p))

    invalid = [r for r in results if not r["valid"]]
    summary = {
        "validator_version": VERSION,
        "skills": len(results),
        "valid": sum(r["valid"] for r in results),
        "invalid": len(invalid),
        "minimum_score": min((r["score"] for r in results), default=100),
    }
    regression_paths: set[str] = set()
    regression_failures = []
    if args.baseline_ref:
        regression_paths = changed_skill_paths(args.baseline_ref, args.head_ref, root)
        regression_failures = [r for r in invalid if r["path"] in regression_paths]
    summary["changed_skill_definitions"] = len(regression_paths)
    summary["regression_failures"] = len(regression_failures)
    summary["baseline_gated"] = bool(args.baseline_ref)

    payload = {"summary": summary, "results": results}
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else (
        f"skills={summary['skills']} valid={summary['valid']} invalid={summary['invalid']} "
        f"minimum_score={summary['minimum_score']} changed={summary['changed_skill_definitions']} "
        f"regressions={summary['regression_failures']}"
    ))
    for r in invalid:
        print(f"FAIL {r['path']}: {r['hard_failures']}", file=sys.stderr)
    if args.baseline_ref:
        return 1 if regression_failures else 0
    return 1 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
