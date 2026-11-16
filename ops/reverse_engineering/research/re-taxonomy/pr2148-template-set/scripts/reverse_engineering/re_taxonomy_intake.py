#!/usr/bin/env python3
"""Parse a Reverse Engineering taxonomy/toolkit issue form into a record.

Emits ``re-taxonomy-intake/v1``. The node payload carries exactly the fields
``ops/reverse_engineering/taxonomy.py validate()`` consumes (id, name, kind,
parents, tags, toolchain) so a record can be validated mechanically before it
lands in ``ops/reverse_engineering/taxonomy.json`` (re-taxonomy/v1).

Vocabulary (axes, workflow stages, node/tool ids) is read from taxonomy.json
when --taxonomy is given (the workflow passes it from the trusted checkout);
embedded fallbacks mirror re-taxonomy/v1 at build time.

Two forms feed this parser (docs/ops/RE-TAXONOMY-TEMPLATES.md):
  * filing -- register/propose an RE item or toolchain
  * record -- validated placement + evidence (carries Item ID + Validator
    result headings; its presence selects kind=record)

Deterministic, stdlib-only, no network. Secret-looking VALUES are refused.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

SCHEMA = "re-taxonomy-intake/v1"
ROOT_ID = "reverse-engineering"

AXES = {
    "target": ["native", "bytecode", "script", "firmware", "protocol",
               "hardware", "mobile", "web-client", "data-format"],
    "format": ["PE", "ELF", "Mach-O", "DEX", "JAR", "CLR", "raw-image",
               "filesystem-image", "APK", "JS-bundle", "WASM"],
    "architecture": ["x86", "x64", "ARM", "ARM64", "MIPS", "RISC-V", "other"],
    "method": ["static", "dynamic", "hybrid", "comparative", "emulated",
               "automated"],
    "objective": ["understanding", "interoperability", "malware-analysis",
                  "vulnerability-research", "patch-analysis",
                  "cross-validation", "ctf", "incident-support"],
    "tool_role": ["disassembler", "decompiler", "debugger", "instrumentation",
                  "extractor", "emulator", "workspace", "cross-validator",
                  "capture", "deobfuscator", "adapter-factory"],
    "environment": ["linux", "windows", "macos", "android", "ios", "embedded",
                    "ci-remote", "b160v-thin"],
    "evidence": ["observed", "inferred", "reproduced", "contradicted",
                 "unknown"],
}
STAGES = ["acquire", "identify", "extract", "analyze-static",
          "observe-dynamic", "validate", "document"]
NODE_KINDS = ("category", "tool")

_HEADING_RE = re.compile(r"^###\s+(.+?)\s*$", re.M)
_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SUBMITTER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 _-]*\{[^{}]+\}$")
_SECRET_VALUE_RE = re.compile(
    r"(?:sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|"
    r"github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|"
    r"AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")

AXIS_HEADINGS = {
    "target": "Tags - target", "format": "Tags - format",
    "architecture": "Tags - architecture", "method": "Tags - method",
    "objective": "Tags - objective", "tool_role": "Tags - tool role",
    "environment": "Tags - environment",
}


class IntakeError(ValueError):
    pass


def parse_form(body: str) -> dict[str, str]:
    matches = list(_HEADING_RE.finditer(body or ""))
    fields: dict[str, str] = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        value = body[m.end():end].strip()
        fields[m.group(1).strip()] = "" if value == "_No response_" else value
    return fields


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")
    return slug


def _csv(value: str) -> list[str]:
    out: list[str] = []
    for part in re.split(r"[,\n]", value or ""):
        part = part.strip().strip("`")
        if part and part not in out:
            out.append(part)
    return out


def _parse_toolchain(value: str) -> list[dict]:
    """Lines: `stage: tool-a, tool-b -> output text` (output optional)."""
    stages: list[dict] = []
    for line in (value or "").splitlines():
        line = line.strip().lstrip("-").strip()
        if not line:
            continue
        m = re.match(r"^([a-z][a-z0-9-]*)\s*:\s*(.+)$", line)
        if not m:
            raise IntakeError(f"toolchain line not 'stage: tools': {line!r}")
        stage, rest = m.group(1), m.group(2)
        output = ""
        if "->" in rest:
            rest, output = rest.split("->", 1)
            output = output.strip()
        stages.append({"stage": stage, "tools": _csv(rest),
                       "output": output})
    return stages


def load_taxonomy(path: str | None):
    """Return (axes, stages, node_ids, tool_ids) from taxonomy.json or None."""
    if not path:
        return None
    with open(path, encoding="utf-8") as fh:
        tax = json.load(fh)
    nodes = tax.get("nodes") or []
    node_ids = {n["id"] for n in nodes}
    tool_ids = {n["id"] for n in nodes if n.get("kind") == "tool"}
    return (tax.get("axes") or AXES, tax.get("workflow_stages") or STAGES,
            node_ids, tool_ids)


def build_record(fields: dict[str, str], *, issue_number: int = 0,
                 taxonomy=None) -> dict:
    axes, stages_vocab, node_ids, tool_ids = taxonomy or (AXES, STAGES,
                                                          None, None)
    for key, value in fields.items():
        if _SECRET_VALUE_RE.search(value or ""):
            raise IntakeError(
                f"field {key!r} looks like a secret VALUE; names only")

    is_record = bool(fields.get("Validator result") or fields.get("Item ID"))
    name = fields.get("Item name", "").strip()
    if not name:
        raise IntakeError("Item name is required")
    item_id = (fields.get("Item ID") or "").strip() or _slugify(name)
    if not _SLUG_RE.match(item_id):
        raise IntakeError(f"item id {item_id!r} is not a slug")

    kind = (fields.get("Kind") or "").strip().lower()
    if kind not in NODE_KINDS:
        raise IntakeError(f"Kind must be one of {NODE_KINDS}, got {kind!r}")

    parents = _csv(fields.get("Parent node IDs", ""))
    if not parents:
        raise IntakeError("at least one parent node id is required "
                          "(polyhierarchy; must descend from "
                          f"{ROOT_ID})")
    for parent in parents:
        if not _SLUG_RE.match(parent):
            raise IntakeError(f"parent {parent!r} is not a node-id slug")
        if node_ids is not None and parent not in node_ids:
            raise IntakeError(f"parent {parent!r} does not resolve in "
                              "taxonomy.json")

    tags: dict[str, list[str]] = {}
    for axis, heading in AXIS_HEADINGS.items():
        values = _csv(fields.get(heading, ""))
        if not values:
            continue
        vocab = axes.get(axis)
        if vocab is None:
            raise IntakeError(f"unknown axis {axis!r}")
        for v in values:
            if v not in vocab:
                raise IntakeError(
                    f"tag {axis}:{v} not in axis vocabulary {vocab}")
        tags[axis] = values
    if kind == "tool" and not tags.get("tool_role"):
        raise IntakeError("tool nodes REQUIRE tool_role tags")

    toolchain = _parse_toolchain(fields.get("Toolchain stages", ""))
    last_idx = -1
    for entry in toolchain:
        if entry["stage"] not in stages_vocab:
            raise IntakeError(
                f"toolchain stage {entry['stage']!r} not in workflow_stages "
                f"{stages_vocab}")
        idx = stages_vocab.index(entry["stage"])
        if idx < last_idx:
            raise IntakeError("toolchain stages out of workflow order")
        last_idx = idx
        if tool_ids is not None:
            for tool in entry["tools"]:
                if tool not in tool_ids:
                    raise IntakeError(
                        f"toolchain tool {tool!r} does not resolve to a "
                        "tool node in taxonomy.json")

    submitter = fields.get("Submitter Role{Moniker}", "").strip()
    if not submitter or not _SUBMITTER_RE.match(submitter):
        raise IntakeError("Submitter must be in Role{Moniker} form")

    record = {
        "schema": SCHEMA,
        "kind": "record" if is_record else "filing",
        "node": {
            "id": item_id,
            "name": name,
            "kind": kind,
            "parents": parents,
            "tags": tags,
            "description": fields.get("Description", "").strip(),
        },
        "toolchain": toolchain,
        "outputs": _csv(fields.get("Outputs", "")),
        "submitter": submitter,
        "notes": fields.get("Notes", "").strip(),
        "source_issue": issue_number,
    }
    if is_record:
        evidence = fields.get("Evidence level", "").strip()
        if evidence and evidence not in axes.get("evidence", []):
            raise IntakeError(
                f"evidence level {evidence!r} not in evidence vocabulary")
        record["evidence"] = evidence
        record["validator_result"] = fields.get("Validator result",
                                                "").strip()
    else:
        record["evidence_expectation"] = fields.get(
            "Evidence expectation", "").strip()
    return record


def render_comment(record: dict) -> str:
    node = record["node"]
    lines = [
        "<!-- re-taxonomy-intake-record -->",
        f"**[MUSEai]@{{role:{{research-triggers}}}} re-taxonomy intake "
        f"record** — `{record['schema']}` kind={record['kind']} "
        f"node=`{node['id']}` ({node['kind']})",
        "",
        "```json",
        json.dumps(record, indent=2, sort_keys=True),
        "```",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("body_file")
    ap.add_argument("--issue", type=int, default=0)
    ap.add_argument("--taxonomy",
                    help="path to ops/reverse_engineering/taxonomy.json; "
                         "when given, parents/tools/vocab resolve against it")
    ap.add_argument("--markdown", action="store_true",
                    help="emit the issue-comment rendering instead of JSON")
    args = ap.parse_args(argv)
    with open(args.body_file, encoding="utf-8") as fh:
        fields = parse_form(fh.read())
    taxonomy = load_taxonomy(args.taxonomy)
    try:
        record = build_record(fields, issue_number=args.issue,
                              taxonomy=taxonomy)
    except IntakeError as exc:
        print(f"intake error: {exc}", file=sys.stderr)
        return 2
    print(render_comment(record) if args.markdown
          else json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
