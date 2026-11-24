"""Normalize the separate Delphi Oracle general-intake Issue Form.

This module is deterministic, stdlib-only, and read-only. It resolves selections
against the repository's existing research/DoE/proposal registries. It produces
selection records while execution remains false.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA = "delphi.oracle-intake.v1"
SELECTION_MODES = {"DoE Decides", "All", "Specific selection", "Prior default"}
ARMS = ("baseline", "rnd", "selected", "control")
PROJECT_IDS = (
    "aws-free-tier-strands-delphi-oracle",
    "continuous-capability-evolution-lab",
    "delphi-desk-builder-io",
)
DEFAULT_PANEL = ("OPERATOR", "builder", "reviewer", "Scout", "cost_auditor")
REQUEST_CATEGORIES = {
    "Evaluate an existing proposal", "Create a new proposal", "Refine an existing proposal",
    "Conduct research or evidence review", "Compare alternatives",
    "Harmoniously reconcile multiple projects", "Improve or evaluate Delphi methodology",
    "Oracle recommends classification",
}
METHODOLOGIES = {
    "Oracle recommends", "Classical Delphi", "Modified Delphi", "Policy Delphi",
    "Decision Delphi", "Fuzzy Delphi", "RAND/UCLA appropriateness",
    "One-pass rubric — single assessment",
}
ROUND_PROFILES = {
    "Adaptive with declared stopping criteria", "Fixed 2 rounds", "Fixed 3 rounds",
    "Fixed 4–5 rounds", "Custom round count", "Single-pass (one assessment)",
}
MATRIX_STRATEGIES = {
    "Shared matrix across all rounds", "Per-round expansion",
    "Alternating-round expansion", "Evidence-triggered expansion", "Custom schedule",
}
RECONCILIATION_DIMENSIONS = {
    "Objectives and strategic alignment", "Duplicate or overlapping proposals",
    "Requirements and constraints", "Dependencies and integration points",
    "Evidence and research findings", "Conflicting assumptions",
    "Existing decisions and unresolved dissent", "Implementation sequencing",
}
PANEL_OPTIONS = set(DEFAULT_PANEL) | {
    "Human experts", "Project stakeholders",
    "Model participants (eligible, separately attributed)",
}
WEBVIEW_OPTION = "Request optional human WebView oversight"
MODE_HEADINGS = {
    "Request category": "request_category",
    "Target proposal / project references": "target_references",
    "Research selection mode": "research_selection_mode",
    "Research participants": "research_participants",
    "DoE components": "doe_components",
    "Related methodology RFPs": "methodology_rfps",
    "Related research projects": "research_projects",
    "Research arms": "research_arms",
    "Harmonious Reconciliation dimensions": "reconciliation_dimensions",
    "Delphi methodology": "methodology",
    "Round profile": "round_profile",
    "Round maximum / custom count": "round_maximum",
    "Stopping criteria / stability definition": "stopping_criteria",
    "Question Matrix strategy": "matrix_strategy",
    "Per-round Question Matrix schedule": "matrix_schedule",
    "Panel roles and participants": "panel",
    "Human WebView oversight": "webview_oversight",
    "Selection disposition": "selection_disposition",
    "Research question / objectives": "research_question",
    "Evidence references": "evidence_references",
    "Constraints and desired outcome": "constraints",
}


def parse_issue_body(body: str) -> dict[str, str]:
    """Parse known form headings while preserving free-text Markdown and fences."""
    sections: dict[str, list[str]] = {}
    field_order = list(MODE_HEADINGS)
    field_positions = {label: index for index, label in enumerate(field_order)}
    next_field = 0
    current: str | None = None
    fence: str | None = None

    for line in body.splitlines():
        stripped = line.strip()
        fence_match = re.match(r"^(```+|~~~+)", stripped)
        if fence is not None:
            if current is not None:
                sections[current].append(line)
            if fence_match and fence_match.group(1).startswith(fence):
                fence = None
            continue
        if fence_match:
            fence = fence_match.group(1)[:3]
            if current is not None:
                sections[current].append(line)
            continue

        heading = re.match(r"^###s+(.+?)s*$", line)
        if (
            heading
            and heading.group(1) in field_positions
            and field_positions[heading.group(1)] >= next_field
        ):
            current = heading.group(1)
            sections[current] = []
            next_field = field_positions[current] + 1
        elif current is not None:
            sections[current].append(line)

    return {
        MODE_HEADINGS[name]: "
".join(lines).strip()
        for name, lines in sections.items()
    }


def _strip_outer_text_fence(value: str) -> str:
    lines = value.strip().splitlines()
    if (
        len(lines) >= 2
        and re.fullmatch(r"```[A-Za-z0-9_-]*", lines[0].strip())
        and lines[-1].strip() == "```"
    ):
        return "
".join(lines[1:-1]).strip()
    return value.strip()


def _text_field(fields: dict[str, str], name: str, required: bool = False) -> str:
    return _strip_outer_text_fence(_single(fields, name, required=required))


def _checked(value: str) -> list[str]:
    return [
        match.group(1).strip()
        for line in value.splitlines()
        if (match := re.match(r"^\s*-\s+\[[xX]\]\s+(.+?)\s*$", line))
    ]


def _single(fields: dict[str, str], name: str, required: bool = False) -> str:
    value = fields.get(name, "").strip()
    if value.lower() in {"", "_no response_", "no response"}:
        if required:
            raise ValueError(f"required form field is empty: {name}")
        return ""
    return value


def _load_json(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load catalogue {relative}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"catalogue must contain a JSON object: {relative}")
    return value


def _proposal_ids(root: Path) -> set[str]:
    text = (root / "docs/proposals/registry.yaml").read_text(encoding="utf-8")
    return set(re.findall(r"^\s*- id:\s*([a-z0-9][a-z0-9-]+)\s*$", text, re.M))


def load_catalogues(root: Path) -> dict[str, Any]:
    silos_doc = _load_json(root, "ops/delphi/research-silos.json")
    participants_doc = _load_json(root, "ops/delphi/research-participants.json")
    components_doc = _load_json(root, "ops/doe/component-registry.json")
    segments_doc = _load_json(root, "ops/delphi/rfp-segments.json")

    silos = {item["id"]: item for item in silos_doc.get("silos", [])}
    participants = {
        item["silo_id"]: item for item in participants_doc.get("participants", [])
    }
    components = {
        item["id"]: item for item in components_doc.get("components", [])
    }
    meta_members = segments_doc.get("classes", {}).get("meta-process", {}).get("members", {})
    method_rfps = {str(issue): name for name, issue in meta_members.items()}
    proposals = _proposal_ids(root)
    missing_projects = sorted(set(PROJECT_IDS) - proposals)
    if missing_projects:
        raise ValueError("project IDs missing from proposal registry: " + ", ".join(missing_projects))
    missing_silos = sorted(set(silos) - set(participants))
    if missing_silos:
        raise ValueError("research silos missing participant records: " + ", ".join(missing_silos))
    return {
        "silos": silos,
        "participants": participants,
        "components": components,
        "method_rfps": method_rfps,
        "projects": {project_id: project_id for project_id in PROJECT_IDS},
    }


def _checkbox_ids(values: list[str], allowed: set[str], field: str) -> list[str]:
    ids = []
    for label in values:
        identifier = label.split(" — ", 1)[0].strip()
        if identifier not in allowed:
            raise ValueError(f"unknown {field} checkbox value: {label}")
        if identifier not in ids:
            ids.append(identifier)
    return ids


def _record_participants(ids: list[str], catalogues: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for silo_id in ids:
        participant = catalogues["participants"][silo_id]
        silo = catalogues["silos"][silo_id]
        filings = participant.get("filings", {})
        records.append({
            "id": silo_id,
            "slot": silo.get("slot"),
            "role": silo.get("role"),
            "tier": silo.get("tier"),
            "upstream": silo.get("upstream"),
            "baseline_issue": filings.get("baseline"),
            "arm_issues": dict(filings.get("arms", {})),
        })
    return records


def _record_components(ids: list[str], catalogues: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": component_id,
            "title": catalogues["components"][component_id].get("title"),
            "status": catalogues["components"][component_id].get("status"),
            "delphi_rfp": catalogues["components"][component_id].get("delphi_rfp"),
            "factor_candidate": catalogues["components"][component_id].get("doe", {}).get("factor_candidate", False),
        }
        for component_id in ids
    ]


def normalize_intake(issue: dict[str, Any], body: str, root: Path) -> dict[str, Any]:
    fields = parse_issue_body(body)
    catalogues = load_catalogues(root)

    mode_values = _checked(fields.get("research_selection_mode", ""))
    if len(mode_values) > 1:
        raise ValueError("select exactly one Research selection mode checkbox")
    mode = mode_values[0] if mode_values else "Prior default"
    if mode not in SELECTION_MODES:
        raise ValueError(f"unknown research selection mode: {mode}")

    participant_ids = _checkbox_ids(
        _checked(fields.get("research_participants", "")),
        set(catalogues["participants"]), "research participant"
    )
    component_ids = _checkbox_ids(
        _checked(fields.get("doe_components", "")),
        set(catalogues["components"]), "DoE component"
    )
    method_ids = []
    for label in _checked(fields.get("methodology_rfps", "")):
        match = re.match(r"^#(\d+)\s+—\s+(.+)$", label)
        if not match or match.group(1) not in catalogues["method_rfps"]:
            raise ValueError(f"unknown methodology RFP checkbox value: {label}")
        if method_ids and match.group(1) in method_ids:
            continue
        if catalogues["method_rfps"][match.group(1)] != match.group(2).strip():
            raise ValueError(f"methodology RFP label/registry mismatch: {label}")
        method_ids.append(match.group(1))
    project_ids = _checkbox_ids(
        _checked(fields.get("research_projects", "")),
        set(catalogues["projects"]), "research project"
    )
    arm_values = _checked(fields.get("research_arms", ""))
    unknown_arms = sorted(set(arm_values) - set(ARMS))
    if unknown_arms:
        raise ValueError("unknown research arms: " + ", ".join(unknown_arms))

    if mode == "All":
        participant_ids = sorted(catalogues["participants"])
        component_ids = sorted(catalogues["components"])
        method_ids = sorted(catalogues["method_rfps"], key=int)
        project_ids = sorted(catalogues["projects"])
        arms = list(ARMS)
        selection_status = "all_registered_candidates"
        selection_authority = "submitter"
    elif mode == "Prior default":
        participant_ids = sorted(catalogues["participants"])
        component_ids, method_ids = [], []
        arms = ["baseline"]
        selection_status = "prior_default_baseline"
        selection_authority = "submitter"
    elif mode == "DoE Decides":
        if not any((participant_ids, component_ids, method_ids, project_ids)):
            participant_ids = sorted(catalogues["participants"])
            component_ids = sorted(catalogues["components"])
            method_ids = sorted(catalogues["method_rfps"], key=int)
            project_ids = sorted(catalogues["projects"])
        arms = arm_values or list(ARMS)
        selection_status = "pending_doe_decision"
        selection_authority = "DoE"
    else:
        if not any((participant_ids, component_ids, method_ids, project_ids)):
            raise ValueError("Specific selection requires at least one checked research item")
        arms = arm_values or ["baseline"]
        selection_status = "submitter_selected"
        selection_authority = "submitter"

    request_category = _single(fields, "request_category", required=True)
    target_references = _text_field(fields, "target_references")
    target_reference_items = list(dict.fromkeys(
        item.strip()
        for item in re.split(r"[,;\n]+", target_references)
        if item.strip()
    ))
    resolved_reference_count = len(set(project_ids) | set(target_reference_items))
    if request_category in {"Evaluate an existing proposal", "Refine an existing proposal"} and resolved_reference_count < 1:
        raise ValueError("existing-proposal requests require a target proposal or project reference")
    if request_category in {"Compare alternatives", "Harmoniously reconcile multiple projects"} and resolved_reference_count < 2:
        raise ValueError("comparison and reconciliation requests require at least two distinct references")
    methodology = _single(fields, "methodology", required=True)
    round_profile = _single(fields, "round_profile", required=True)
    matrix_strategy = _single(fields, "matrix_strategy", required=True)
    disposition = _single(fields, "selection_disposition", required=True)
    if request_category not in REQUEST_CATEGORIES:
        raise ValueError(f"unknown request category: {request_category}")
    if methodology not in METHODOLOGIES:
        raise ValueError(f"unknown Delphi methodology: {methodology}")
    if round_profile not in ROUND_PROFILES:
        raise ValueError(f"unknown round profile: {round_profile}")
    if matrix_strategy not in MATRIX_STRATEGIES:
        raise ValueError(f"unknown Question Matrix strategy: {matrix_strategy}")
    allowed_dispositions = {"Selection review", "Registry catalogue", "Both", "Deliberation only"}
    if disposition not in allowed_dispositions:
        raise ValueError(f"unknown selection disposition: {disposition}")

    raw_round_maximum = _single(fields, "round_maximum") or "3"
    if not raw_round_maximum.isdigit():
        raise ValueError("round maximum must be an integer")
    round_maximum = int(raw_round_maximum)
    if round_profile != "Single-pass (one assessment)" and not 2 <= round_maximum <= 10:
        raise ValueError("round maximum must be an integer from 2 through 10")
    stopping_criteria = _text_field(fields, "stopping_criteria")
    if round_profile == "Fixed 2 rounds":
        round_maximum = 2
    elif round_profile == "Fixed 3 rounds":
        round_maximum = 3
    elif round_profile == "Fixed 4–5 rounds" and round_maximum not in {4, 5}:
        raise ValueError("Fixed 4–5 rounds requires a round maximum of 4 or 5")
    elif round_profile == "Custom round count" and not _single(fields, "round_maximum"):
        raise ValueError("Custom round count requires a round maximum")
    elif round_profile == "Adaptive with declared stopping criteria" and not stopping_criteria:
        raise ValueError("adaptive rounds require declared stopping criteria")
    one_pass_method = methodology == "One-pass rubric — single assessment"
    if one_pass_method and round_profile != "Single-pass (one assessment)":
        raise ValueError("one-pass rubric requires the Single-pass round profile")
    if round_profile == "Single-pass (one assessment)":
        if methodology not in {"One-pass rubric — single assessment", "Oracle recommends"}:
            raise ValueError("Single-pass profile requires a one-pass or Oracle-recommended method")
        round_maximum = 1

    matrix_schedule = _text_field(fields, "matrix_schedule")
    reconciliation = _checked(fields.get("reconciliation_dimensions", ""))
    unknown_dimensions = sorted(set(reconciliation) - RECONCILIATION_DIMENSIONS)
    if unknown_dimensions:
        raise ValueError("unknown reconciliation dimensions: " + ", ".join(unknown_dimensions))
    if request_category == "Harmoniously reconcile multiple projects" and not reconciliation:
        raise ValueError("Harmonious Reconciliation requires at least one selected dimension")
    panel = _checked(fields.get("panel", "")) or list(DEFAULT_PANEL)
    unknown_panel = sorted(set(panel) - PANEL_OPTIONS)
    if unknown_panel:
        raise ValueError("unknown panel participants: " + ", ".join(unknown_panel))
    webview_values = _checked(fields.get("webview_oversight", ""))
    if set(webview_values) - {WEBVIEW_OPTION}:
        raise ValueError("unknown WebView oversight option")
    webview = bool(webview_values)
    issue_number = issue.get("number")
    if not isinstance(issue_number, int):
        raise ValueError("issue metadata must include an integer issue number")

    selection_review = disposition in {"Selection review", "Both"}
    catalogue_write = disposition in {"Registry catalogue", "Both"}
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "selection_id": f"delphi-intake-{issue_number}",
        "source": {
            "issue_number": issue_number,
            "title": issue.get("title", ""),
            "url": issue.get("html_url", ""),
            "actor": (issue.get("user") or {}).get("login", ""),
            "created_at": issue.get("created_at"),
            "updated_at": issue.get("updated_at"),
        },
        "request": {
            "category": request_category,
            "target_references": target_references,
            "target_reference_items": target_reference_items,
            "research_question": _text_field(fields, "research_question", required=True),
            "evidence_references": _text_field(fields, "evidence_references"),
            "constraints": _text_field(fields, "constraints"),
        },
        "research_selection": {
            "mode": mode,
            "status": selection_status,
            "authority": selection_authority,
            "participants": _record_participants(participant_ids, catalogues),
            "doe_components": _record_components(component_ids, catalogues),
            "methodology_rfps": [
                {"issue_number": int(issue_id), "surface_id": catalogues["method_rfps"][issue_id]}
                for issue_id in method_ids
            ],
            "projects": project_ids,
            "arms": arms,
            "comparison_policy": "within_segment_only; cross_silo_aggregation=false",
        },
        "reconciliation": {
            "dimensions": reconciliation,
            "project_references": project_ids,
            "additional_references": target_reference_items,
            "mode": "harmonious_reconciliation" if request_category == "Harmoniously reconcile multiple projects" else "standard",
        },
        "delphi": {
            "methodology": methodology,
            "round_profile": round_profile,
            "round_maximum": round_maximum,
            "stopping_criteria": stopping_criteria,
            "question_matrix": {
                "strategy": matrix_strategy,
                "per_round_schedule": matrix_schedule,
                "versioning": "version each round; preserve question identity, lineage, evidence, and change rationale",
            },
        },
        "panel": {
            "context": "Termux-monorepo",
            "participants": panel,
            "human_webview_oversight": webview,
        },
        "disposition": {
            "requested": disposition,
            "selection_review": selection_review,
            "catalogue_write": catalogue_write,
        },
        "execution": False,
    }
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
    record["record_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-path", default=os.environ.get("GITHUB_EVENT_PATH"))
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    if not args.event_path:
        parser.error("--event-path or GITHUB_EVENT_PATH is required")
    event = json.loads(Path(args.event_path).read_text(encoding="utf-8"))
    issue = event.get("issue") or {}
    body = issue.get("body") or ""
    root = Path(__file__).resolve().parents[2]
    try:
        record = normalize_intake(issue, body, root)
    except ValueError as exc:
        print(f"Delphi Oracle intake validation failed: {exc}", file=sys.stderr)
        return 2
    Path(args.output).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"normalized {record['selection_id']} ({record['research_selection']['mode']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
