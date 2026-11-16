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

METHOD_VERSION = "attribution/1.5"
METHOD = "stamp+trailer+git-author evidence chain (ACP)"

STAMP_RE = re.compile(r"\[MUSEai\]@\{role:\{([^}]+)\}\}")
AGENT_TRAILER_RE = re.compile(r"^\*{0,2}Agent(?:-Identity)?:\*{0,2}\s*(.+?)\*{0,2}$", re.M)
SIGNOFF_RE = re.compile(r"^\*{0,2}(?:Signed-off-by|Co-authored-by):\*{0,2}\s*([^<]+?)\s*(?:<([^>]+)>)?\*{0,2}$", re.M)

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
    "hark": ("hark",),
    "runable": ("runable",),
    "cue": ("cue",),
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


_MANIFEST_AUTHOR_RE = re.compile(r"^\+?\s*author:\s*(.+?)\s*$", re.M)
_MANIFEST_FILE_RE = re.compile(r"(MANIFEST\.|\.(md|ya?ml|toml)$)", re.I)


def _manifest_actor(body: str, files):
    """Manifest/frontmatter evidence leg (owner ruling 2026-11-01): a chain
    that fires only on self-applied sign-offs structurally misses
    collaborators working through owner channels; the artifact's own
    declared author (ACP MANIFEST frontmatter `author: ChatGPT` class) is
    first-class evidence. Sources: PR-body YAML frontmatter, and added
    `author:` lines in changed MANIFEST/frontmatter-carrying files."""
    fm = re.match(r"^---\n(.*?)\n---", body or "", re.S)
    if fm:
        m = _MANIFEST_AUTHOR_RE.search(fm.group(1))
        if m:
            a = normalize_actor(m.group(1))
            if a and not _is_owner(m.group(1), ""):
                return a, {"source": "body_frontmatter", "raw": m.group(1).strip()[:80]}
    for f in files or []:
        if not _MANIFEST_FILE_RE.search(f.get("filename") or ""):
            continue
        for line in (f.get("patch") or "").splitlines():
            if not line.startswith("+"):
                continue
            m = _MANIFEST_AUTHOR_RE.match(line)
            if m:
                a = normalize_actor(m.group(1))
                if a and not _is_owner(m.group(1), ""):
                    return a, {"source": "file_frontmatter", "file": f["filename"],
                               "raw": m.group(1).strip()[:80]}
    return None

def _token_history_actor(pr: dict, token_history: dict | None):
    """attribution/1.5 token-history leg (G14): server-side token records
    for the PR — `merged_by` (single-PR record) and Actions run actors
    on the head SHA. Speaks ONLY about app/bot attributions: when one of
    those independent server records names the PR author's own bot
    login, the transport attribution is corroborated by a second,
    independent surface (merge record / run record vs author field).
    Returns (actor_key, detail) or None. Never an authorship leg and
    never a conflict source (same transport class as app_bot)."""
    if not token_history:
        return None
    login = ((pr.get("user") or {}).get("login") or "")
    if not login.endswith("[bot]"):
        return None
    key = login[:-5].lower()
    via = []
    if token_history.get("merged_by") == login:
        via.append("merged_by")
    if login in (token_history.get("run_actors") or []):
        via.append("run_actor")
    if not via:
        return None
    return (key, {"login": login, "via": via})


def extract_actor(pr: dict, commits=None, files=None,
                  token_history: dict | None = None) -> dict:
    """Return {actor, actor_evidence:{method, detail}, corroboration} for
    one PR dict.

    Corroboration (owner ruling 2026-11-01: some signings are FALSE —
    marks != proof): ALL legs are evaluated, not just the winner. The
    chain order still picks the actor, but the record now carries every
    leg's verdict and a state: "corroborated" (>=2 independent legs name
    the winner, no leg names anyone else), "disputed" (another leg names
    a different actor — suspected false signing; flag, never score at
    face value), "single-leg" (uncorroborated), "unattributed".
    """
    text = (pr.get("title") or "") + "\n" + (pr.get("body") or "")
    legs = {}
    stamp = _stamp_actor(text)
    if stamp:
        legs["stamp"] = stamp
    trailer = _trailer_actor(pr.get("body") or "")
    trailer_detail = None
    if trailer:
        legs["trailer"] = trailer
    else:
        for c in commits or []:
            msg = ((c.get("commit") or {}).get("message") or "")
            hit = _trailer_actor(msg)
            if hit:
                legs["trailer"] = (hit[0], {**hit[1], "source": "commit_message"})
                break
    manifest = _manifest_actor(pr.get("body") or "", files)
    if manifest:
        legs["manifest"] = manifest
    git_author = _git_author_actor(commits)
    if git_author:
        legs["git_author"] = git_author
    login = ((pr.get("user") or {}).get("login") or "")
    if login.endswith("[bot]"):
        legs["app_bot"] = (login[:-5].lower(), {"login": login})
    th = _token_history_actor(pr, token_history)
    if th:
        legs["token_history"] = th
    order = ["stamp", "trailer", "manifest", "git_author", "app_bot"]
    winner = next((k for k in order if k in legs), None)
    verdicts = {k: v[0] for k, v in legs.items()}
    if winner is None:
        return {"actor": None, "actor_evidence": {"method": None, "detail": {}},
                "corroboration": {"state": "unattributed", "legs": verdicts,
                                  "agreeing": [], "conflicts": []}}
    actor = legs[winner][0]
    # app_bot is a TRANSPORT/publisher leg (fleet lanes publish through
    # App identities, e.g. termux-fleet-publisher): it corroborates when
    # it matches, but a mismatch against an authorship leg is the normal
    # publish pattern, not a false signing. Conflicts are computed over
    # AUTHORSHIP legs only (stamp/trailer/manifest/git_author).
    author_legs = {k: a for k, a in verdicts.items()
                   if k not in ("app_bot", "token_history")}
    agreeing = [k for k, a in author_legs.items() if a == actor and k != winner]
    if "app_bot" in verdicts and verdicts["app_bot"] == actor and winner != "app_bot":
        agreeing.append("app_bot")
    if ("token_history" in verdicts and verdicts["token_history"] == actor
            and winner != "token_history"):
        agreeing.append("token_history")
    conflicts = sorted({a for k, a in author_legs.items() if a != actor})
    if conflicts:
        state = "disputed"
    elif agreeing:
        state = "corroborated"
    else:
        state = "single-leg"
    return {"actor": actor,
            "actor_evidence": {"method": winner, "detail": legs[winner][1]},
            "corroboration": {"state": state, "legs": verdicts,
                              "agreeing": agreeing, "conflicts": conflicts,
                              "publisher": verdicts.get("app_bot")}}


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
