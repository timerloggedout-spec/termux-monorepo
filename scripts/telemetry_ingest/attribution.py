#!/usr/bin/env python3
"""Actor attribution for PAT-riding collaborators (ACP rules).

GitHub's actor field names the credential holder (the owner's PAT), NOT
the authoring collaborator. Per the agent-contributor-provenance
proposal (docs/proposals/active/agent-contributor-provenance, #1241):
attribution must cite its evidence method, and missing evidence stays
null — never defaulted to the owner.

Evidence chain, strongest first:
  1. stamp      — [MUSEai]@{role:{X}} coordination stamp in the PR
                  title/body (the fleet's signed attribution mark).
  2. trailer    — `Agent: X` / `Signed-off-by: X <..>` / `Co-authored-by:`
                  trailers in the PR body (AGENT-IDENTITY.md layer).
  3. git_author — the PR commits' git author name/email, when it maps
                  to a known collaborator identity (alias/email-domain)
                  and is not the owner or a bot.
  4. app_bot    — PR opened by a GitHub App / bot login (`*[bot]`): the
                  app IS the actor for app-authored work.
  5. none       — actor = None. The owner's login alone is NOT evidence.

Known-identity mapping is deliberately conservative: an unrecognized
git author name does not become an actor (it may be a human, a tool, or
free text). Registry-keyed canonicalization (Role{Moniker} registry)
layers on top of the raw actor ids produced here.
"""
from __future__ import annotations

import re

METHOD_VERSION = "attribution/1"
METHOD = "stamp+trailer+git-author evidence chain (ACP)"

STAMP_RE = re.compile(r"\[MUSEai\]@\{role:\{([^}]+)\}\}")
AGENT_TRAILER_RE = re.compile(r"^Agent:\s*(.+)$", re.M)
SIGNOFF_RE = re.compile(r"^(?:Signed-off-by|Co-authored-by):\s*([^<]+?)\s*(?:<([^>]+)>)?$", re.M)

OWNER_NAMES = {"timerloggedout-spec", "timerloggedout", "loggedout", "logged out"}
# Registry #3355 distinction: `Grok (OPERATOR)` is the HUMAN OWNER's
# signing row (archW1z); the AI collaborator is plain `Grok <grok@x.ai>`.
OPERATOR_MARK = "(operator)"
OWNER_EMAIL_HINTS = ("timerloggedout",)

# canonical actor id -> alias fragments (name, email local part, domain)
ALIASES = {
    "grok": ("grok", "x.ai"),
    "jules": ("jules", "bolt"),
    "chatgpt": ("chatgpt", "openai"),
    "Muse": ("Muse", "anthropic"),
    "gemini": ("gemini", "google"),
    "deepseek": ("deepseek",),
    "devin": ("devin", "cognition"),
    "manus": ("manus",),
    "copilot": ("copilot",),
    "coderabbit": ("coderabbit",),
    "qodo": ("qodo",),
    "deepagent": ("deepagent",),
}


def _is_owner(name: str, email: str) -> bool:
    n = (name or "").strip().lower()
    e = (email or "").strip().lower()
    return n in OWNER_NAMES or any(h in e for h in OWNER_EMAIL_HINTS)


def normalize_actor(raw: str) -> str | None:
    """Map a raw name/email/stamp-role to a canonical actor id, or None."""
    if not raw:
        return None
    s = raw.strip().lower()
    email = s if "@" in s else ""
    local = email.split("@")[0] if email else ""
    domain = email.split("@")[-1] if email else ""
    for actor, frags in ALIASES.items():
        for f in frags:
            if f == domain or s == f or local == f or s.startswith(f + " ") or s.startswith(f + "-") or s.startswith(f + "@"):
                return actor
    # a stamp role like `grok-recon` / a plain single-token name is an
    # actor label in its own right when it is identifier-shaped
    token = re.split(r"[\s<]", s)[0]
    if re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,40}", token) and token not in OWNER_NAMES:
        base = token.split("-")[0].split(".")[0]
        return base if base in ALIASES else token
    return None


def _stamp_actor(text: str):
    roles = STAMP_RE.findall(text or "")
    norm = [a for a in (normalize_actor(r) for r in roles) if a]
    if not norm:
        return None
    # most frequent wins; ties -> first seen
    best = max(sorted(set(norm), key=norm.index), key=norm.count)
    return best, {"roles": sorted(set(roles)), "stamps": len(roles)}


def _trailer_actor(body: str):
    for m in AGENT_TRAILER_RE.finditer(body or ""):
        a = normalize_actor(m.group(1))
        if a and not _is_owner(m.group(1), ""):
            return a, {"trailer": "Agent:", "raw": m.group(1).strip()[:80]}
    for m in SIGNOFF_RE.finditer(body or ""):
        name, email = m.group(1) or "", m.group(2) or ""
        if OPERATOR_MARK in name.lower() or _is_owner(name, email):
            continue
        a = normalize_actor(email or name)
        if a:
            return a, {"trailer": "signoff", "raw": (name or email).strip()[:80]}
    return None


def _git_author_actor(commits):
    seen = {}
    for c in commits or []:
        au = ((c.get("commit") or {}).get("author") or {})
        name, email = au.get("name") or "", au.get("email") or ""
        if _is_owner(name, email):
            continue
        if "bot" in name.lower() or "github-actions" in name.lower():
            continue
        a = normalize_actor(email or name)
        # git-author evidence counts only for KNOWN identities: an
        # unrecognized name slug is not attribution (ACP conservatism)
        if a and (email and any(f in email.lower() for frags in ALIASES.values() for f in frags) or a in ALIASES):
            seen[a] = seen.get(a, 0) + 1
    if not seen:
        return None
    best = max(seen.items(), key=lambda kv: kv[1])[0]
    return best, {"commits_by_actor": seen}


def extract_actor(pr: dict, commits=None) -> dict:
    """Return {actor, actor_evidence:{method, detail}} for one PR dict."""
    text = (pr.get("title") or "") + "\n" + (pr.get("body") or "")
    hit = _stamp_actor(text)
    if hit:
        return {"actor": hit[0], "actor_evidence": {"method": "stamp", "detail": hit[1]}}
    hit = _trailer_actor(pr.get("body") or "")
    if hit:
        return {"actor": hit[0], "actor_evidence": {"method": "trailer", "detail": hit[1]}}
    for c in commits or []:
        msg = ((c.get("commit") or {}).get("message") or "")
        hit = _trailer_actor(msg)
        if hit:
            return {"actor": hit[0], "actor_evidence": {"method": "trailer",
                            "detail": {**hit[1], "source": "commit_message"}}}
    hit = _git_author_actor(commits)
    if hit:
        return {"actor": hit[0], "actor_evidence": {"method": "git_author", "detail": hit[1]}}
    login = ((pr.get("user") or {}).get("login") or "")
    if login.endswith("[bot]"):
        return {"actor": login[:-5].lower(), "actor_evidence": {"method": "app_bot", "detail": {"login": login}}}
    return {"actor": None, "actor_evidence": {"method": None, "detail": {}}}


# Registry keying: when the Role{Moniker} registry verdict for an actor
# lands, its canonical registered id replaces the raw id here. Grok's
# entry is applied by keying REGISTRY_CANONICAL["grok"] once Registry
# (ac8e5e6b) publishes it; until then the raw evidence id stands and is
# marked registry_keyed=False in the stats output.
REGISTRY_CANONICAL: dict[str, str] = {
    # Registry verdict LANDED PR #3355 (2026-11-01, AGENT-MONIKERS.md):
    # Grok = distinct attributed actor, registered display `Grok`;
    # established identity git `Grok <grok@x.ai>`, pipeline identity
    # `Grok (Administrator)` (ml/pipelines/peers/grok.py).
    "grok": "Grok",
}


def apply_registry(actor: str | None) -> tuple[str | None, bool]:
    if actor is None:
        return None, False
    if actor in REGISTRY_CANONICAL:
        return REGISTRY_CANONICAL[actor], True
    return actor, False
