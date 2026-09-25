#!/usr/bin/env python3
"""Comparative decision-engine registry (not LLM provider catalog).

LLM providers live in provider_model_catalog / model_router.
This registry is for System-1 / schema decision engines used as pre-gates,
guardrails, routing, and completion evidence — comparative only, no primary.

RECON 2026-09-23:
  - logicrw/awesome-jev-projects (595 commit-pinned, 17 categories)
  - Reddit top-20 (Canny = evidence-backed done gate)
  - Laya / Kev / hosted Jev / specialists

Latency is low-value MoneyBall; quality dimensions dominate selection.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Engines — comparative registry
# ---------------------------------------------------------------------------

ENGINES: dict[str, dict[str, Any]] = {
    "laya": {
        "id": "laya",
        "family": "laya",
        "kind": "system1_decision",
        "not_an_llm_provider": True,
        "host": "self",
        "license": "Apache-2.0",
        "repo": "https://github.com/NandhaKishorM/laya",
        "demo": "https://huggingface.co/spaces/convaiinnovations/laya-demo",
        "weights": "https://huggingface.co/convaiinnovations/laya",
        "product": "https://laya.convaiinnovations.com",
        "install": "pip install laya",
        "primitives": ["choice", "score", "noul"],
        "checkpoints": ["english", "multilingual", "typed-decisions"],
        "stub": "scripts/laya_decision_stub.py",
        "slot": "refTemplates/16_Org_Phased/laya",
        "phase": "COMPARATIVE",
        "workflows": [
            "pre-LLM triage",
            "guardrails / jailbreak noul",
            "tool/model route choice",
            "help-wanted urgency score",
            "multi-lang routing",
        ],
        "quality": {
            "calibration": "post-temperature ECE claims strong; base zero-shot weak",
            "cardinality": "degrades >20 options",
            "multi_lang": "Router + 100+ languages",
            "self_host": True,
            "locked_suite": "typed-decisions fine-tuned ~0.766 (published vs Jev)",
        },
        "dense_feedback": [
            "checkpoint",
            "confidence",
            "routing.reason",
            "latency_budget_ms",
        ],
    },
    "kev-0.8b": {
        "id": "kev-0.8b",
        "family": "kev",
        "kind": "system1_decision",
        "not_an_llm_provider": True,
        "host": "self",
        "license": "Apache-2.0 (adapter+head; Qwen base)",
        "repo": "https://github.com/jaredpalmer/kev",
        "weights": "https://huggingface.co/jaredpalmer/kev-0.8b",
        "install": "uv sync --extra serve; python -m kev.serve --run jaredpalmer/kev-0.8b",
        "primitives": ["choice", "score", "noul"],
        "system_one_wire": True,
        "phase": "COMPARATIVE",
        "workflows": ["edge / low-memory System One", "local coding-agent gates"],
        "quality": {
            "calibration": "built-in T; weaker OOD than 4B/9B",
            "cardinality": "better than pure encoder on many suites",
            "multi_lang": "English-first",
            "self_host": True,
            "locked_suite": "see kev model cards (dev + locked)",
        },
        "dense_feedback": ["checkpoint", "confidence", "routing.reason"],
    },
    "kev-4b": {
        "id": "kev-4b",
        "family": "kev",
        "kind": "system1_decision",
        "not_an_llm_provider": True,
        "host": "self",
        "license": "Apache-2.0 (adapter+head; Qwen base)",
        "repo": "https://github.com/jaredpalmer/kev",
        "weights": "https://huggingface.co/jaredpalmer/kev-4b",
        "install": "uv sync --extra serve; python -m kev.serve --run jaredpalmer/kev-4b",
        "primitives": ["choice", "score", "noul"],
        "system_one_wire": True,
        "phase": "COMPARATIVE",
        "workflows": [
            "recommended Kev accuracy/byte",
            "local System One drop-in",
            "coding-agent route / guard",
        ],
        "quality": {
            "calibration": "built-in T; strong OOD relative to size",
            "cardinality": "competitive",
            "multi_lang": "English-first",
            "self_host": True,
            "locked_suite": "see kev-4b card (locked test)",
        },
        "dense_feedback": ["checkpoint", "confidence", "routing.reason"],
    },
    "kev-9b": {
        "id": "kev-9b",
        "family": "kev",
        "kind": "system1_decision",
        "not_an_llm_provider": True,
        "host": "self",
        "license": "Apache-2.0 (adapter+head; Qwen base)",
        "repo": "https://github.com/jaredpalmer/kev",
        "weights": "https://huggingface.co/jaredpalmer/kev-9b",
        "install": "uv sync --extra serve; python -m kev.serve --run jaredpalmer/kev-9b",
        "primitives": ["choice", "score", "noul"],
        "system_one_wire": True,
        "phase": "COMPARATIVE",
        "workflows": ["highest-accuracy open Kev", "local peak when GPU allows"],
        "quality": {
            "calibration": "built-in T; best Kev OOD locked ~0.852",
            "cardinality": "competitive",
            "multi_lang": "English-first",
            "self_host": True,
            "locked_suite": "see kev-9b card",
        },
        "dense_feedback": ["checkpoint", "confidence", "routing.reason"],
    },
    "jev": {
        "id": "jev",
        "family": "jev",
        "kind": "system1_decision",
        "not_an_llm_provider": True,
        "host": "hosted",
        "license": "closed API",
        "product": "https://typesafe.ai",
        "docs": "https://docs.typesafe.ai",
        "primitives": ["choice", "score", "noul"],
        "system_one_wire": True,
        "phase": "REFERENCE",
        "workflows": ["peak hosted accuracy", "long-state when budget allows"],
        "quality": {
            "calibration": "published strong; third-party benches mixed",
            "cardinality": "stronger high-option",
            "multi_lang": "limited public matrix",
            "self_host": False,
            "locked_suite": "vendor + independent benches",
        },
        "dense_feedback": ["model", "confidence", "usage"],
        "cost_note": "metered; never default under free-first policy",
        "cost_penalty": 3,
    },
    "canny_pattern": {
        "id": "canny_pattern",
        "family": "policy",
        "kind": "completion_gate",
        "not_an_llm_provider": True,
        "host": "self",
        "license": "MIT (qkal/Canny)",
        "repo": "https://github.com/qkal/Canny",
        "primitives": ["noul"],
        "phase": "PATTERN",
        "workflows": [
            "dual-gate done evidence",
            "adaptive-wait completion",
            "agent 'I am done' claims",
        ],
        "quality": {
            "calibration": "N/A — deterministic facts hard-block; engine only advises",
            "rule": "Facts → code. Judgments → engine. Only facts hard-block.",
            "self_host": True,
        },
        "dense_feedback": ["ledger_entry", "fact_block", "noul_advice", "reason"],
        "note": "Reddit top-20 #19; high monorepo affinity",
    },
}

# Bolt optimization: Precompute engine metadata and scores at module load time
# to eliminate per-call string conversions, lowercasing, and iterations in select().
for _eng in ENGINES.values():
    _q = _eng.get("quality") or {}
    _host = _eng.get("host")
    _eng["_workflows_str"] = " ".join(_eng.get("workflows") or []).lower()
    _eng["_family"] = str(_eng.get("family") or "").lower()
    _eng["_multi_lang_str"] = str(_q.get("multi_lang", "")).lower()
    _eng["_cardinality_degrades"] = "degrades" in str(_q.get("cardinality", ""))
    _eng["_self_host"] = bool(_q.get("self_host", _host == "self"))
    _eng["_cost_penalty"] = int(_eng.get("cost_penalty") or 0)
    _base = 0
    if _eng.get("phase") == "COMPARATIVE":
        _base += 2
    if _eng.get("phase") == "PATTERN":
        _base += 3
    if _host == "self":
        _base += 2
    if _eng.get("system_one_wire"):
        _base += 1
    _eng["_base_score"] = _base


def list_engines() -> list[dict[str, Any]]:
    return list(ENGINES.values())


def get_engine(engine_id: str) -> dict[str, Any] | None:
    return ENGINES.get(engine_id)


def select(
    *,
    free_only: bool = True,
    self_host_required: bool = False,
    lang: str = "en",
    max_options: int | None = None,
    domain: str | None = None,
    family: str | None = None,
    allow_hosted: bool = False,
) -> list[dict[str, Any]]:
    """Criteria-driven comparative selection. Returns ranked candidates with reasons."""
    ranked: list[dict[str, Any]] = []
    domain_lower = domain.lower() if domain else None
    family_lower = family.lower() if family else None
    for eng in ENGINES.values():
        host = eng.get("host")
        if free_only and host == "hosted" and not allow_hosted:
            continue
        if self_host_required and not eng["_self_host"]:
            continue
        if family_lower and eng["_family"] != family_lower:
            continue
        reasons: list[str] = []
        if lang == "multi" and "multi" not in eng["_multi_lang_str"]:
            if eng["id"] != "laya":
                reasons.append("multi_lang_weak")
        if max_options is not None and max_options > 20 and eng["_cardinality_degrades"]:
            reasons.append("high_cardinality_risk")
        if domain_lower and domain_lower not in eng["_workflows_str"] and domain not in eng["id"]:
            reasons.append(f"domain_soft_miss:{domain}")
        score = eng["_base_score"]
        if host == "hosted":
            score -= eng["_cost_penalty"]
            reasons.append("hosted_cost_penalty")
        if "high_cardinality_risk" in reasons:
            score -= 2
        if "multi_lang_weak" in reasons and lang == "multi":
            score -= 1
        ranked.append(
            {
                "engine": eng["id"],
                "family": eng.get("family"),
                "score": score,
                "reasons": reasons or ["criteria_matched"],
                "dense_feedback_keys": eng.get("dense_feedback", []),
            }
        )
    ranked.sort(key=lambda x: (-x["score"], x["engine"]))
    return ranked


def recommend_pair(
    *,
    domain: str | None = None,
    allow_hosted: bool = False,
) -> dict[str, Any]:
    """Pair a System-1 engine with the Canny completion gate (comparative)."""
    system1 = select(
        domain=domain,
        allow_hosted=allow_hosted,
        free_only=not allow_hosted,
    )
    system1 = [r for r in system1 if r["engine"] != "canny_pattern"]
    gate = select(domain="done", self_host_required=True, family="policy")
    return {
        "policy": "comparative_pair_no_primary",
        "system1": system1[:3],
        "completion_gate": gate[:1],
        "invalid_agent_states": ["HOLD", "WAIT", "OBSERVE"],
        "valid_gate_decisions": ["ALLOW", "BLOCK", "NEED_EVIDENCE"],
    }


def matrix_summary() -> dict[str, Any]:
    return {
        "policy": "comparative_only_no_primary",
        "latency_rank": "low_value_moneyball",
        "high_value_dims": [
            "calibration",
            "locked_suite_accuracy",
            "option_cardinality",
            "zero_shot_honesty",
            "multi_lang",
            "fail_open_vs_hard_block",
            "evidence_density",
            "wire_compatibility",
            "self_host",
            "cost_per_decision",
            "domain_specialization",
            "dense_feedback",
            "family",
        ],
        "recon": {
            "awesome_jev_projects": "https://github.com/logicrw/awesome-jev-projects",
            "radar": "https://logicrw.github.io/awesome-jev-projects/en/",
            "catalog_json": "https://logicrw.github.io/awesome-jev-projects/projects.json",
            "reddit_top20_canny": "https://github.com/qkal/Canny",
            "as_of": "2026-09-23",
        },
        "engines": list(ENGINES.keys()),
        "families": sorted({e.get("family") for e in ENGINES.values() if e.get("family")}),
        "invalid_agent_states": ["HOLD", "WAIT", "OBSERVE"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--id", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--matrix", action="store_true")
    parser.add_argument("--select", action="store_true")
    parser.add_argument("--recommend", action="store_true")
    parser.add_argument("--free-only", action="store_true", default=True)
    parser.add_argument("--allow-hosted", action="store_true")
    parser.add_argument("--self-host", action="store_true")
    parser.add_argument("--lang", default="en")
    parser.add_argument("--domain", default=None)
    parser.add_argument("--family", default=None)
    parser.add_argument("--max-options", type=int, default=None)
    args = parser.parse_args()

    if args.matrix:
        data = matrix_summary()
    elif args.recommend:
        data = recommend_pair(domain=args.domain, allow_hosted=args.allow_hosted)
    elif args.select:
        data = select(
            free_only=not args.allow_hosted,
            self_host_required=args.self_host,
            lang=args.lang,
            max_options=args.max_options,
            domain=args.domain,
            family=args.family,
            allow_hosted=args.allow_hosted,
        )
    elif args.list:
        data = list_engines()
    elif args.id:
        data = get_engine(args.id)
        if data is None:
            print(f"unknown engine: {args.id}", file=sys.stderr)
            return 1
    else:
        data = matrix_summary()

    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
