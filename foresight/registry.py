from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

HORIZONS = {"H0", "H1", "H2", "H3"}
EVIDENCE_STATUSES = {
    "confirmed",
    "research_finding",
    "attributed_claim",
    "early_signal",
    "speculative",
}
DECISIONS = {"watch", "investigate", "prototype", "adopt", "reject", "defer"}

PROCUREMENT_FIELDS = [
    "license", "canonical_source", "maintenance", "portability",
    "offline_capability", "interoperability", "reproducibility",
    "provenance", "dependency_risk", "lock_in_risk", "security_surface",
    "resource_cost", "operational_fit", "horizon", "confidence",
    "decision_status",
]

REQUIRED = [
    "resource_id", "title", "category", "horizon",
    "evidence_status", "summary", "source", "observed_at",
]

DEFAULT_REGISTRY = Path("data/foresight/resource-registry.jsonl")


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def fingerprint(record: dict[str, Any]) -> str:
    payload = dict(record)
    payload.pop("evidence_hash", None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def normalize(record: dict[str, Any]) -> dict[str, Any]:
    out = dict(record)
    out.setdefault("observed_at", now_utc())
    out.setdefault("captured_at", now_utc())
    out.setdefault("source_type", "unknown")
    out.setdefault("source_version", None)
    out.setdefault("source_date", None)
    out.setdefault("evidence", [])
    out.setdefault("unresolved_questions", [])
    out.setdefault("why_it_matters", None)
    out.setdefault("practical_opportunity", None)
    out.setdefault("termux_relevance", None)
    out.setdefault("procurement", {})
    out.setdefault("tags", [])
    out["horizon"] = str(out.get("horizon", "")).upper()
    out["evidence_status"] = str(out.get("evidence_status", "")).lower()
    out["confidence"] = float(out.get("confidence", 0.0))
    out["evidence_hash"] = fingerprint(out)
    return out


def validate(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED:
        if not record.get(key):
            errors.append(f"missing required field: {key}")

    if record.get("horizon") not in HORIZONS:
        errors.append("horizon must be one of H0/H1/H2/H3")
    if record.get("evidence_status") not in EVIDENCE_STATUSES:
        errors.append("invalid evidence_status")

    confidence = record.get("confidence")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        errors.append("confidence must be in [0,1]")

    source = record.get("source")
    if not isinstance(source, dict) or not source.get("url"):
        errors.append("source.url is required")

    procurement = record.get("procurement", {})
    if not isinstance(procurement, dict):
        errors.append("procurement must be an object")
    else:
        unknown = set(procurement) - set(PROCUREMENT_FIELDS)
        if unknown:
            errors.append("unknown procurement fields: " + ", ".join(sorted(unknown)))
        if procurement.get("horizon") and procurement["horizon"] not in HORIZONS:
            errors.append("procurement.horizon must be H0/H1/H2/H3")
        if procurement.get("decision_status") and procurement["decision_status"] not in DECISIONS:
            errors.append("invalid procurement.decision_status")

    return errors


def load(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{lineno}: invalid JSON: {exc}") from exc
    return records


def append(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    record = normalize(record)
    errors = validate(record)
    if errors:
        raise ValueError("; ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(canonical_json(record) + "\n")
    return record


def dedupe(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for raw in records:
        record = normalize(raw)
        latest[record["resource_id"]] = record
    return list(latest.values())


def export_csv(records: Iterable[dict[str, Any]], destination: Path) -> None:
    records = list(records)
    destination.parent.mkdir(parents=True, exist_ok=True)
    columns = REQUIRED + [
        "source_type", "source_version", "source_date",
        "why_it_matters", "practical_opportunity", "termux_relevance",
        "confidence", "evidence_hash",
    ] + PROCUREMENT_FIELDS
    with destination.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            row = dict(record)
            row.update(record.get("procurement", {}))
            writer.writerow(row)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="foresight-registry")
    p.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    sub = p.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.set_defaults(func=lambda a: (a.registry.parent.mkdir(parents=True, exist_ok=True),
                                      a.registry.touch(exist_ok=True), print(a.registry), 0)[-1])

    add = sub.add_parser("add")
    add.add_argument("file", type=Path)
    def add_cmd(a):
        payload = json.loads(a.file.read_text(encoding="utf-8"))
        for record in payload if isinstance(payload, list) else [payload]:
            append(a.registry, record)
        return 0
    add.set_defaults(func=add_cmd)

    validate_cmd = sub.add_parser("validate")
    def validate_cmd_fn(a):
        failures = 0
        records = load(a.registry)
        for i, raw in enumerate(records, 1):
            record = normalize(raw)
            errors = validate(record)
            if raw.get("evidence_hash") != fingerprint(raw):
                errors.append("evidence_hash mismatch")
            if errors:
                failures += 1
                print(f"{a.registry}:{i}: " + "; ".join(errors), file=sys.stderr)
        print(f"validated={len(records)} failures={failures}")
        return int(bool(failures))
    validate_cmd.set_defaults(func=validate_cmd_fn)

    radar = sub.add_parser("radar")
    radar.add_argument("--horizon", action="append", choices=sorted(HORIZONS))
    def radar_cmd(a):
        allowed = set(a.horizon or HORIZONS)
        for r in sorted(dedupe(load(a.registry)), key=lambda x: (x["horizon"], x["title"].lower())):
            if r["horizon"] in allowed:
                print(json.dumps({
                    "resource_id": r["resource_id"],
                    "horizon": r["horizon"],
                    "evidence_status": r["evidence_status"],
                    "confidence": r["confidence"],
                    "title": r["title"],
                    "source": r["source"]["url"],
                    "termux_relevance": r.get("termux_relevance"),
                    "decision_status": r.get("procurement", {}).get("decision_status"),
                }, ensure_ascii=False))
        return 0
    radar.set_defaults(func=radar_cmd)

    export = sub.add_parser("export-csv")
    export.add_argument("output", type=Path)
    export.set_defaults(func=lambda a: (export_csv(dedupe(load(a.registry)), a.output), print(a.output), 0)[-1])

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
