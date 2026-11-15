#!/usr/bin/env python3
"""QUE item fields: Mandate ∧ Report (que-superagent P1).

Ports two dsh-superagent domain rules into QUE items
(docs/proposals/active/que-superagent/LESSONS.md):

  Mandate (que-mandate/v1) -- what an accept grants: policy version,
    scope, strength explicit|inferred, matched rules, sender, Source,
    receiving scope, trigger id. Immutable: wider scope => a new item.
  Report (que-report/v1) -- the state an executor reports to its item:
    progress|waiting|ready|blocked|failed|dropped, plus an optional
    structured one-question `attention` (the only thing that counts
    toward the HITL rate).

Both ride QUE comments as HTML-comment machine blocks, so the human
text stays readable and a parser never infers state from prose.

Templates: refTemplates/06_Task_Tracking/que-superagent/.
Stdlib only.
"""
from __future__ import annotations

import hashlib
import json
import re
from types import MappingProxyType

MANDATE_SCHEMA = "que-mandate/v1"
REPORT_SCHEMA = "que-report/v1"
STRENGTHS = ("explicit", "inferred")
REPORT_STATES = ("progress", "waiting", "ready", "blocked", "failed", "dropped")
# Reply stamp state derived from the latest Report.
STAMP_FOR_STATE = {
    "progress": "live", "waiting": "live", "ready": "live",
    "dropped": "live", "blocked": "blocked", "failed": "down",
}
MANDATE_KEYS = ("schema", "policy_version", "scope", "strength",
                "matched_rules", "source", "receiving_scope", "sender",
                "trigger_id")

_BLOCK_RE = re.compile(r"<!--\s*(que-(?:mandate|report)/v1)\s*\n(.*?)\n\s*-->", re.S)


class FieldError(ValueError):
    """A Mandate or Report that breaks its schema."""


def policy_version(schema_name: str, raw: bytes) -> str:
    """Stable policy version: the policy's schema name @ sha256[:8] of its bytes."""
    return f"{schema_name}@{hashlib.sha256(raw).hexdigest()[:8]}"


def strength_for_sender(sender: str) -> str:
    """A bot can only raise an inferred candidate, never an explicit request."""
    s = (sender or "").lower()
    return "inferred" if s.endswith("[bot]") or s.endswith("-bot") else "explicit"


def make_mandate(*, policy_version: str, scope: str, strength: str,
                 matched_rules, source: str, receiving_scope: str,
                 sender: str, trigger_id: str) -> MappingProxyType:
    """Build an immutable Mandate; raises FieldError on a bad field."""
    if strength not in STRENGTHS:
        raise FieldError(f"strength must be one of {STRENGTHS}, got {strength!r}")
    rules = tuple(str(r) for r in (matched_rules or ()))
    if strength == "inferred" and not rules:
        raise FieldError("an inferred Mandate needs at least one matched rule")
    for name, val in (("policy_version", policy_version), ("scope", scope),
                      ("source", source), ("receiving_scope", receiving_scope)):
        if not val or not str(val).strip():
            raise FieldError(f"{name} is required")
    return MappingProxyType({
        "schema": MANDATE_SCHEMA,
        "policy_version": str(policy_version),
        "scope": str(scope),
        "strength": strength,
        "matched_rules": rules,
        "source": str(source),
        "receiving_scope": str(receiving_scope),
        "sender": str(sender or "unrecorded"),
        "trigger_id": str(trigger_id or "unrecorded"),
    })


def make_report(state: str, summary: str, receipt=(), attention=None) -> MappingProxyType:
    """Build a Report; attention is ONE structured question or None."""
    if state not in REPORT_STATES:
        raise FieldError(f"state must be one of {REPORT_STATES}, got {state!r}")
    if not summary or not summary.strip():
        raise FieldError("summary is required")
    if attention is not None:
        if not isinstance(attention, dict) or not str(attention.get("question", "")).strip():
            raise FieldError("attention must be a dict with one non-empty question")
        opts = attention.get("options")
        if opts is not None and (not isinstance(opts, list) or not opts):
            raise FieldError("attention.options must be a non-empty list when given")
        attention = dict(attention)
    return MappingProxyType({
        "schema": REPORT_SCHEMA,
        "state": state,
        "summary": summary.strip(),
        "receipt": tuple(str(r) for r in receipt),
        "attention": attention,
    })


def _plain(obj):
    if isinstance(obj, MappingProxyType):
        obj = dict(obj)
    if isinstance(obj, dict):
        return {k: _plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_plain(v) for v in obj]
    return obj


def render_block(fields) -> str:
    """Render a Mandate or Report as an HTML-comment machine block."""
    data = _plain(fields)
    return f"<!-- {data['schema']}\n{json.dumps(data, indent=2, ensure_ascii=False)}\n-->"


def parse_blocks(text: str) -> list[dict]:
    """Every que-mandate/que-report block in a comment body, in order."""
    out = []
    for schema, body in _BLOCK_RE.findall(text or ""):
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("schema") == schema:
            out.append(data)
    return out


def latest(blocks, schema: str):
    found = [b for b in blocks if b.get("schema") == schema]
    return found[-1] if found else None


def mandate_changed(old: dict, new: dict) -> list[str]:
    """Keys that differ: a non-empty list means a NEW item, never an edit."""
    return [k for k in MANDATE_KEYS if _plain(old.get(k)) != _plain(new.get(k))]


def stamp_state(report) -> str:
    return STAMP_FOR_STATE[report["state"]]


def reply_stamp(item: str, report, receipts=None) -> str:
    """`{live|degraded|down|blocked} {item} · verified receipt {..} · owner action: {..}`"""
    refs = ", ".join(receipts if receipts is not None else report.get("receipt", ())) or "none"
    att = report.get("attention")
    action = att["question"] if att else "none"
    return f"{stamp_state(report)} {item} · verified receipt {refs} · owner action: {action}"


def hitl_rate(reports) -> float:
    """Share of Reports that carry a structured attention question."""
    reports = list(reports)
    if not reports:
        return 0.0
    return sum(1 for r in reports if r.get("attention")) / len(reports)
