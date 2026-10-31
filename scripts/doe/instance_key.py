#!/usr/bin/env python3
"""Configured-instance identity for DoE (owner fix, 2026-10-30).

model@version is NOT a sufficient identity: one provider
model@version runs as different configured instances — distinct
system prompts, distinct tools, per role/context. Every DoE record
and every dispatch stamp keys the instance by its configuration:

    {provider, model@version, system_prompt (ref + sha256),
     tools (ref + sha256), role, moniker, context}

Ref scheme (the fleet stamp scheme, named by the DoE lane):
- A ref is a repo-relative path when the artifact lives in the repo
  (e.g. docs/prompts/<name>.md, a tool manifest .json); otherwise a
  scoped id: prompt:<moniker>:<slug> or tools:<moniker>:<slug>.
- Every ref travels with the full SHA-256 of the exact content as
  dispatched: for a prompt, the prompt text; for tools, the manifest
  file bytes when a manifest exists, else the canonical tool set =
  sorted tool names joined by "\\n".
- Compact stamp form: <ref>#<sha256[:12]>.
- instance_key = SHA-256 hex of the canonical JSON of the tuple
  (sorted keys; prompt/tools enter by their sha256). Aggregation and
  quota attribution group by instance_key — never by model alone.
"""
from __future__ import annotations

import hashlib
import json


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def tools_sha256(tool_names: list[str]) -> str:
    """Canonical tool-set hash when no manifest file exists."""
    return sha256_text("\n".join(sorted(tool_names)))


def canonical_instance(*, provider: str, model: str,
                       system_prompt_sha256: str, tools_sha256_: str,
                       role: str, moniker: str, context: str) -> dict:
    return {
        "provider": provider,
        "model": model,
        "system_prompt_sha256": system_prompt_sha256,
        "tools_sha256": tools_sha256_,
        "role": role,
        "moniker": moniker,
        "context": context,
    }


def instance_key(**kwargs) -> str:
    canon = canonical_instance(**kwargs)
    return sha256_text(json.dumps(canon, sort_keys=True,
                                  separators=(",", ":")))


def ref_stamp(ref: str, sha256_hex: str) -> str:
    return f"{ref}#{sha256_hex[:12]}"
