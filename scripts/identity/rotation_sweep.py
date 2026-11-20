#!/usr/bin/env python3
"""Deterministic collaborator-entrypoint rotation sweep and DoE replay.

Classifier families: path, lexical, Markdown link, workflow, semantic context,
and collaborator identity. The sweep is offline and read-only. It emits a
machine-readable report and a DOE/MVT EXPERIMENT record.
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT_SCHEMA = "collaborator-rotation-sweep/v1"
CAMPAIGN = "collaborator-rotation-sweep"
FACTORS = ("path", "lexical", "link", "workflow", "semantic")
HISTORICAL = re.compile(
    r"\b(deprecated|retired|formerly|previously|historical|legacy|superseded|"
    r"migration|renamed|rename|old entrypoint|prior filename)\b", re.I)
ACTIVE = re.compile(
    r"\b(read|load|include|import|source|uses|use|link|alias|entrypoint|"
    r"dispatch|prompt|workflow|route|open)\b", re.I)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
TEXT_SUFFIXES = {".md", ".mdx", ".txt", ".py", ".sh", ".yml", ".yaml",
                 ".json", ".jsonl", ".toml", ".ini", ".cfg", ".js", ".ts", ".xml"}
SKIP_PARTS = {".git", ".venv", "node_modules", "__pycache__", "tmp", "workspace"}
SKIP_FILES = {"scripts/identity/rotation_sweep.py", "tests/test_rotation_sweep.py",
              "docs/ops/COLLABORATOR-ROTATION-MAP.json"}


def load_map(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def entries(rotation_map: dict) -> list[dict]:
    return list(rotation_map["entries"])


def legacy_names(rotation_map: dict) -> set[str]:
    return {Path(item["source"]).name for item in entries(rotation_map)}


def normalize_rel(value: str) -> str:
    return value.replace("\\", "/").lstrip("./")


def list_files(root: Path) -> list[Path]:
    try:
        raw = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                             check=True, capture_output=True).stdout
        rels = [v.decode("utf-8", "surrogateescape") for v in raw.split(b"\0") if v]
        return [root / value for value in rels]
    except (OSError, subprocess.CalledProcessError):
        return sorted(path for path in root.rglob("*") if path.is_file())


def semantic_class(line: str) -> str:
    if HISTORICAL.search(line):
        return "historical"
    if ACTIVE.search(line):
        return "active"
    return "ambiguous"


def classify_line(path: str, line: str, rotation_entries: list[dict]) -> dict:
    names = {Path(item["source"]).name for item in rotation_entries}
    found = [name for name in names if re.search(
        r"(?<![A-Za-z0-9_.-])" + re.escape(name) + r"(?![A-Za-z0-9_.-])",
        line, re.I)]
    path_vote = any(normalize_rel(path) == normalize_rel(item["source"])
                    for item in rotation_entries)
    targets = [m.group(1).split("#", 1)[0].split("?", 1)[0]
               for m in LINK.finditer(line)]
    link_vote = any(Path(target).name in names for target in targets)
    workflow_vote = path.startswith(".github/workflows/") and bool(found)
    context = semantic_class(line) if found else "none"
    return {"path": path_vote, "lexical": bool(found), "link": link_vote,
            "workflow": workflow_vote, "semantic": context == "active",
            "context": context, "tokens": sorted(found)}


def ensemble(votes: dict, enabled: tuple[str, ...]) -> bool:
    if any(votes[key] for key in ("path", "link", "workflow") if key in enabled):
        return True
    if "lexical" in enabled and "semantic" in enabled:
        return bool(votes["lexical"] and votes["semantic"])
    if "lexical" in enabled:
        return bool(votes["lexical"])
    return bool(votes.get("semantic")) if "semantic" in enabled else False


def score_fixtures(rotation_map: dict) -> dict:
    rotation_entries = entries(rotation_map)
    fixtures = [
        {"id": "workflow_prompt", "path": ".github/workflows/review.yml",
         "line": "Read GEMINI.md before dispatch", "expected": True},
        {"id": "markdown_link", "path": "docs/guide.md",
         "line": "[Roster](docs/ops/AGENT-MONIKERS.md)", "expected": True},
        {"id": "identity_import", "path": "docs/profile.md",
         "line": "Load AGENT-IDENTITY.md for collaborator attribution", "expected": True},
        {"id": "legacy_path", "path": "AGENTS.md", "line": "", "expected": True},
        {"id": "historical_reference", "path": "docs/history.md",
         "line": "AGENTS.md was deprecated and formerly served as an alias", "expected": False},
        {"id": "historical_gemini", "path": "docs/history.md",
         "line": "GEMINI.md was renamed during the migration", "expected": False},
        {"id": "tool_only", "path": ".github/workflows/gemini.yml",
         "line": "uses: google-github-actions/run-gemini-cli@v1", "expected": False},
        {"id": "current_profile", "path": "docs/guide.md",
         "line": "[Gemini](GEMINI-MESH.md)", "expected": False},
    ]
    arms = []
    for levels in itertools.product((False, True), repeat=len(FACTORS)):
        enabled = tuple(key for key, on in zip(FACTORS, levels) if on)
        tp = fp = tn = fn = 0
        for fixture in fixtures:
            votes = classify_line(fixture["path"], fixture["line"], rotation_entries)
            predicted = ensemble(votes, enabled)
            if predicted and fixture["expected"]: tp += 1
            elif predicted and not fixture["expected"]: fp += 1
            elif not predicted and fixture["expected"]: fn += 1
            else: tn += 1
        total = tp + fp + tn + fn
        arms.append({
            "arm_id": "rot-" + "".join("1" if x else "0" for x in levels),
            "factors": dict(zip(FACTORS, levels)),
            "enabled_classifiers": list(enabled),
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "accuracy": round((tp + tn) / total, 4),
            "precision": round(tp / (tp + fp), 4) if tp + fp else None,
            "recall": round(tp / (tp + fn), 4) if tp + fn else None,
        })
    return {"design": "full_factorial_2^5", "fixture_count": len(fixtures),
            "fixtures": fixtures, "arms": arms}


def check_identity_registry(path: Path) -> dict:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\|\s*([^|]+)\|\s*\x60([^\x60]+)\x60\s*\|\s*([^|]+)\|", line)
        if match:
            rows.append({"role": match.group(1).strip(),
                         "moniker": match.group(2).strip(),
                         "trigger": match.group(3).strip()})
    counts = Counter(row["moniker"].casefold() for row in rows)
    duplicates = sorted(key for key, count in counts.items() if count > 1)
    trigger_names = set()
    for row in rows:
        trigger_names.update(value.casefold().lstrip("@")
                             for value in re.findall(r"@[A-Za-z0-9_.-]+", row["trigger"]))
    collisions = sorted({row["moniker"] for row in rows
                         if row["moniker"].casefold() in trigger_names})
    return {"rows": len(rows), "duplicate_monikers": duplicates,
            "trigger_collisions": collisions,
            "external_github_username_inventory": "not_established",
            "scope": "internal moniker uniqueness and declared live-trigger aliases only",
            "passed": not duplicates and not collisions}

def scan_repository(root: Path, rotation_map: dict) -> dict:
    rotation_entries = entries(rotation_map)
    findings, path_hits = [], []
    historical_paths = set(rotation_map.get("historical_reference_paths", []))
    for file_path in list_files(root):
        try:
            rel = file_path.relative_to(root).as_posix()
        except ValueError:
            continue
        if any(part in SKIP_PARTS for part in Path(rel).parts) or rel in SKIP_FILES:
            continue
        if any(rel == normalize_rel(item["source"]) for item in rotation_entries):
            path_hits.append(rel)
        if file_path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            if file_path.stat().st_size > 2_000_000:
                continue
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for number, line in enumerate(content.splitlines(), 1):
            votes = classify_line(rel, line, rotation_entries)
            if not votes["tokens"] and not votes["path"]:
                continue
            if rel == "docs/ops/COLLABORATOR-ROTATION-MAP.json":
                continue
            disposition = votes["context"]
            if rel in historical_paths:
                disposition = "historical"
                active = False
            else:
                if votes["path"] or votes["link"] or votes["workflow"]:
                    disposition = "active"
                elif votes["lexical"] and votes["semantic"]:
                    disposition = "active"
                active = ensemble(votes, FACTORS)
            findings.append({
                "path": rel, "line": number, "tokens": votes["tokens"],
                "classifiers": {key: votes[key] for key in FACTORS},
                "context": votes["context"], "disposition": disposition,
                "active": active, "excerpt": line.strip()[:220],
            })
    return {"path_hits": sorted(path_hits), "findings": findings,
            "active_refs": [item for item in findings if item["active"]],
            "historical_refs": [item for item in findings if item["disposition"] == "historical"],
            "ambiguous_refs": [item for item in findings if item["disposition"] == "ambiguous"]}


def validate_mapping(root: Path, rotation_map: dict) -> list[str]:
    errors, seen = [], set()
    for item in entries(rotation_map):
        source = item["source"]
        if source in seen:
            errors.append("duplicate source mapping: " + source)
        seen.add(source)
        target = item.get("target") or item.get("canonical")
        if target and not (root / target).is_file():
            errors.append("missing target for " + source + ": " + target)
        if (root / source).exists():
            errors.append("legacy source path remains: " + source)
    return errors


def run(root: Path, base_sha: str, candidate_sha: str) -> dict:
    rotation_map = load_map(root / "docs/ops/COLLABORATOR-ROTATION-MAP.json")
    sweep = scan_repository(root, rotation_map)
    mapping_errors = validate_mapping(root, rotation_map)
    identity = check_identity_registry(root / "docs/ops/COLLABORATOR-MONIKERS.md")
    doe = score_fixtures(rotation_map)
    unresolved = sweep["ambiguous_refs"]
    passed = (not mapping_errors and identity["passed"]
              and not sweep["active_refs"] and not unresolved)
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    record = {
        "schema_version": "1.0",
        "experiment_id": "collaborator-rotation-" + candidate_sha[:12],
        "observed_at": now, "baseline_sha": base_sha,
        "candidate_sha": candidate_sha, "suite": "doe-family:" + CAMPAIGN,
        "cohort": "repository-entrypoint-reference-sweep",
        "treatment": {"manager_policy_id": "collaborator-rotation-sweep/v1",
                      "provider": None, "model": None,
                      "arm": "full-factorial-2^5-classifier-comparison",
                      "instance": None},
        "status": "passed" if passed else "failed",
        "provenance": "github", "confidence": "high",
        "outcome": "rotation_clear" if passed else "rotation_debt_detected",
        "metrics": {
            "classifier_arms": len(doe["arms"]), "fixture_count": doe["fixture_count"],
            "best_fixture_accuracy": max(arm["accuracy"] for arm in doe["arms"]),
            "sweep_findings": len(sweep["findings"]),
            "active_refs": len(sweep["active_refs"]),
            "historical_refs": len(sweep["historical_refs"]),
            "ambiguous_refs": len(unresolved), "mapping_errors": len(mapping_errors),
            "moniker_collisions": len(identity["trigger_collisions"]) + len(identity["duplicate_monikers"]),
            "external_username_inventory_established": 0,
        },
        "evidence_refs": [
            "https://github.com/timerloggedout-spec/termux-monorepo/blob/" + candidate_sha + "/docs/ops/COLLABORATOR-ROTATION-MAP.json",
            "https://github.com/timerloggedout-spec/termux-monorepo/blob/" + candidate_sha + "/scripts/identity/rotation_sweep.py"
        ],
    }
    return {"schema": REPORT_SCHEMA, "campaign_id": CAMPAIGN,
            "base_sha": base_sha, "candidate_sha": candidate_sha,
            "passed": passed, "mapping_errors": mapping_errors,
            "identity": identity, "sweep": sweep, "doe": doe,
            "experiment_record": record}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--candidate-sha", required=True)
    parser.add_argument("--report", type=Path, default=Path("rotation-sweep-report.json"))
    parser.add_argument("--record", type=Path, default=Path("rotation-sweep-experiment.json"))
    args = parser.parse_args()
    report = run(args.root.resolve(), args.base_sha, args.candidate_sha)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.record.write_text(json.dumps(report["experiment_record"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "passed": report["passed"], "mapping_errors": report["mapping_errors"],
        "active_refs": len(report["sweep"]["active_refs"]),
        "historical_refs": len(report["sweep"]["historical_refs"]),
        "ambiguous_refs": len(report["sweep"]["ambiguous_refs"]),
        "classifier_arms": len(report["doe"]["arms"]), "identity": report["identity"],
    }, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
