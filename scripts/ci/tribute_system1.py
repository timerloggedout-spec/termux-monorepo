#!/usr/bin/env python3
"""Tribute System 1: fast, deterministic routing for maintainer replies.

No LLM calls, no third-party writes. Stdlib only.

Pipeline (docs/ops/TRIBUTE-SYSTEM1.md):
  ingest (GitHub API thread / Gmail notification) -> dedupe by comment id
  -> extract_features -> classify (rules + lexicons, each label has a confidence)
  -> route (action, ladder rung, re-plan, lane_event, audit record, prefilter
     rules, Delphi reweighting signal).

Escalation ladder:
  rung 0  programmatic   deterministic state/assignee/close/diff/timeline checks
  rung 1  system1        token/feature/semantic classifiers (lexicons, regex)
  rung 2  system2_llm    only what System 1 cannot settle (incl. question_to_us)
  rung 3  replan         LLM unsure -> the system re-plans the lane itself
                         (yield / retire / park, tighten prefilters, Delphi
                         reweight, pick next candidate). No HITL, no human queue.

The classifier is advisory to every writer: nothing here posts anywhere.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SELF_LOGIN = os.environ.get("HELP_WANTED_AUTHOR", "timerloggedout-spec")
CONFIDENT = float(os.environ.get("TRIBUTE_S1_CONFIDENT", "0.75"))
SCHEMA = "tribute-system1/v2"

LABELS = (
    "closed_already_assigned", "claimed_by_other", "needs_human_skill",
    "low_effort_placeholder", "changes_requested", "approved", "merged",
    "question_to_us", "hostile_spam_flag", "closed_resolved",
)
# Highest-priority terminal label wins the primary slot.
PRIORITY = (
    "merged", "closed_already_assigned", "needs_human_skill", "claimed_by_other", "closed_resolved",
    "low_effort_placeholder", "hostile_spam_flag", "question_to_us",
    "changes_requested", "approved",
)
ACTIONS = {
    "merged": "record_win",
    "closed_already_assigned": "retire_lane",
    "needs_human_skill": "drop_candidate",
    "claimed_by_other": "yield_lane",
    "low_effort_placeholder": "retire_lane",
    "hostile_spam_flag": "retire_lane_cooldown",
    "question_to_us": "escalate",
    "changes_requested": "revise_patch",
    "approved": "await_merge",
    "closed_resolved": "retire_lane",
}
# Classes after which a public re-engagement comment is never appropriate.
NO_REENGAGE = {"closed_already_assigned", "needs_human_skill", "claimed_by_other",
               "low_effort_placeholder", "hostile_spam_flag", "merged", "closed_resolved"}
# Our own follow-up comments in a row (no external human reply in between) before the gate shuts.
FOLLOWUP_CAP = int(os.environ.get("TRIBUTE_S1_FOLLOWUP_CAP", "2"))

MAINTAINER_ASSOC = {"OWNER", "MEMBER", "COLLABORATOR"}
LANGUAGES = (
    "arabic bengali bulgarian catalan chinese mandarin cantonese croatian czech danish dutch "
    "estonian farsi persian finnish french german greek hebrew hindi hungarian indonesian "
    "italian japanese korean latvian lithuanian malay marathi norwegian polish portuguese "
    "punjabi romanian russian serbian slovak slovenian spanish swahili swedish tagalog tamil "
    "telugu thai turkish ukrainian urdu vietnamese"
).split()
_LANG = "|".join(LANGUAGES)

RX = {
    "already_assigned": re.compile(
        r"\b(already|is|been|was)\s+(been\s+)?assigned\b|\bassigned\s+to\s+(another|someone|a different|other)\b", re.I),
    "check_assignment": re.compile(r"check\s+the\s+issue['’]?s?\s+assignment|assignment\s+status", re.I),
    "placeholder": re.compile(
        r"\bplace\s?holder\b|\bstub\b|\bnot\s+(the\s+|an?\s+)?actual\s+implementation\b|\bno\s+(real\s+)?implementation\b|\bempty\s+pr\b|\bjust\s+a\s+stake\b", re.I),
    "claim": re.compile(
        r"\b(i['’]?d|i\s+would)\s+(like|love|want)\s+to\s+(work|take|pick)\b|\bassign\s+(this|it)\s+to\s+me\b|"
        r"\bi['’]?m\s+(actively\s+)?working\s+on\s+(this|it)\b|\bi\s+(have\s+)?claimed\b|\bplease\s+yield\b|"
        r"^\s*/assign\b|\bcan\s+i\s+(work|take)\b|\bi['’]?ve\s+(completed|pushed|opened)\b|"
        r"\bhas\s+applied\s+to\s+work\s+on\s+this\s+issue\b|\btaking\s+a\s+look\s+at\s+this\s+and\s+working\b|"
        r"\bi\s+confirmed\b.*\bi['’]?ll\s+work\s+on\s+this\b|\bhappy\s+to\s+tackle\s+this\b", re.I | re.M),
    "yield_demand": re.compile(r"\bplease\s+yield\b|\bclaimed\s+it\b.*\bbefore\s+you\b|\balready\s+working\b", re.I),
    "lang_skill": re.compile(
        rf"\b(fluent|native)\s+(?:({_LANG})\s+)?speakers?\b|\b(fluent|native)\s+(in\s+)?({_LANG})\b|\b({_LANG})\s+speakers?\b|\bspeak\s+({_LANG})\b", re.I),
    "human_only": re.compile(
        r"\bnot\s+(be\s+)?assign\w*\s+(it\s+|this\s+)?to\s+(an?\s+)?(automated|bot|ai|agent)\b|\bhuman\s+contributor\b|\bnot\s+a\s+code\s+change\b|\bmarketing\s+copy\b|\bno\s+(bots|ai)\b", re.I),
    "changes": re.compile(
        r"\bplease\s+(change|fix|update|add|remove|rebase|address)\b|\bcould\s+you\s+(please\s+)?(change|update|add|fix|rebase)\b|\bneeds?\s+(some\s+)?(changes|tests|work)\b|\brequest(ed)?\s+changes\b", re.I),
    "approve": re.compile(r"\blgtm\b|\blooks\s+good\b|\bapproved?\b|\bship\s+it\b|\bthanks\s+for\s+the\s+(fix|pr)\b", re.I),
    "merged_txt": re.compile(r"\bmerged\b", re.I),
    "spam": re.compile(
        r"\bspam(my|ming)?\b|\bai[- ]generated\b|\bslop\b|\bstop\s+(spamming|opening|posting)\b|"
        r"\b(repo)?ban(ned)?\s+(this|that|the)?\s*(bot|account|user)\b|\brepoban\b|\bblock(ed)?\s+(this|that|the)\s+(bot|account)\b|"
        r"\breport(ed)?\s+(it\s+|this\s+)?(as\s+)?(spam|abuse)\b|\bseems\s+to\s+be\s+a\s+bot\b|\bis\s+a\s+bot\b|\bthat\s+bot\b|\bdon['’]?t\s+mind\s+it\b", re.I),
    "ban_request": re.compile(r"\b(repo)?ban\b|\bblock\s+(this|that|the)\s+(bot|account)\b", re.I),
    "wave_accepted": re.compile(r"congratulations,?\s+@([\w-]+)!?.{0,40}application\s+was\s+accepted", re.I | re.S),
    "wave_completed": re.compile(r"this\s+issue\s+has\s+been\s+completed\s+by\s+@([\w-]+)", re.I),
    "question": re.compile(r"\?\s*$|\?\s|\b(can|could|would|will)\s+you\b", re.I | re.M),
}
PLACEHOLDER_PATHS = re.compile(r"(^|/)(help-wanted-lane-stake\.md|placeholder[^/]*|stake[^/]*\.md|TODO[^/]*)$", re.I)
PLACEHOLDER_PATCH = re.compile(r"\bTODO\b|\bFIXME\b|\bstake\b|replace\s+this\s+file|not\s+implemented|\bpass\s*$", re.I | re.M)


# ---------------------------------------------------------------- helpers
def _ts(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None


def is_bot(login: str | None, author_type: str | None = None) -> bool:
    return (author_type or "").lower() == "bot" or str(login or "").lower().endswith("[bot]")


def author_role(c: dict, subject: dict) -> str:
    login = c.get("author") or ""
    if login.lower() == SELF_LOGIN.lower():
        return "self"
    if is_bot(login, c.get("author_type")):
        return "bot"
    if login and login == subject.get("repo", "").split("/")[0]:
        return "owner"
    assoc = (c.get("association") or "").upper()
    if assoc == "OWNER":
        return "owner"
    if assoc in MAINTAINER_ASSOC:
        return "maintainer"
    if login and login == subject.get("closed_by"):
        return "maintainer"
    if assoc == "CONTRIBUTOR":
        return "contributor"
    return "other"


def dedupe_comments(comments: Iterable[dict], seen: set | None = None) -> list[dict]:
    """Drop repeats by comment id (and anything already in `seen`)."""
    seen = set() if seen is None else seen
    out = []
    for c in comments:
        cid = str(c.get("id") or hashlib.sha1(json.dumps(c, sort_keys=True).encode()).hexdigest())
        if cid in seen:
            continue
        seen.add(cid)
        out.append(c)
    return out


def placeholder_diff(files: Iterable[dict] | None) -> dict:
    """Detect stake/placeholder PR diffs: tiny, doc-only, TODO/stub content."""
    files = list(files or [])
    if not files:
        return {"is_placeholder": False, "score": 0.0, "reasons": []}
    adds = sum(int(f.get("additions") or 0) for f in files)
    reasons, score = [], 0.0
    if all(PLACEHOLDER_PATHS.search(f.get("filename", "")) for f in files):
        reasons.append("stake_or_placeholder_path"); score += 0.6
    if adds <= 15 and len(files) <= 2:
        reasons.append(f"tiny_diff:{adds}+/{len(files)}f"); score += 0.2
    if all(f.get("filename", "").lower().endswith((".md", ".txt")) for f in files):
        reasons.append("docs_only"); score += 0.1
    if any(PLACEHOLDER_PATCH.search(f.get("patch") or "") for f in files):
        reasons.append("todo_or_stake_text"); score += 0.2
    score = min(score, 1.0)
    return {"is_placeholder": score >= 0.6, "score": round(score, 2), "reasons": reasons}


def skill_requirement(text: str) -> str | None:
    m = RX["lang_skill"].search(text or "")
    if m:
        for lang in LANGUAGES:
            if re.search(rf"\b{lang}\b", m.group(0), re.I):
                return f"language:{lang}"
        for lang in LANGUAGES:  # language may sit just outside the match window
            if re.search(rf"\b(fluent|native|speak)\w*\s+(in\s+)?{lang}\b|\b{lang}\s+speaker", text, re.I):
                return f"language:{lang}"
        return "language:unspecified" if re.search(r"speakers?\b", m.group(0), re.I) else None
    return None


def prior_claims(comments: list[dict], subject: dict) -> list[dict]:
    """Human, non-self claim comments, oldest first."""
    out = []
    for c in comments:
        role = author_role(c, subject)
        if role in ("self", "bot"):
            continue
        if RX["claim"].search(c.get("body") or ""):
            out.append({"author": c.get("author"), "at": c.get("created_at"), "id": c.get("id")})
    return out


def our_marker_ts(comments: list[dict]) -> datetime | None:
    ts = [_ts(c.get("created_at")) for c in comments if author_role(c, {}) == "self"]
    ts = [t for t in ts if t]
    return min(ts) if ts else None



# ---------------------------------------------------------------- semantic layer
# Tiny bag-of-stems cosine against class prototypes: no model download, no LLM.
PROTOTYPES = {
    "closed_already_assigned": ["closing this because the issue is already assigned to another contributor",
                                "this issue was assigned to someone else please check assignment before opening a pr",
                                "reserved for a cohort we are not taking outside pull requests for it"],
    "claimed_by_other": ["i am already working on this issue please yield", "i would like to work on this please assign it to me",
                         "someone else already claimed this and is working on it"],
    "needs_human_skill": ["this needs a fluent native speaker human contributor not an automated agent",
                          "requires design or translation skills a person must do this"],
    "low_effort_placeholder": ["this pr only contains a placeholder stub not the actual implementation",
                               "we do not accept placeholder stake pull requests a pr should contain the actual change"],
    "closed_resolved": ["closing this the bug shipped in the release and the rest is tracked elsewhere",
                        "closed by pr merge into main"],
    "hostile_spam_flag": ["stop opening ai generated spam pull requests", "can you repoban that bot it is spam"],
    "changes_requested": ["please add tests and update the implementation before we can merge",
                          "could you change this and rebase on main"],
    "approved": ["looks good to me approved", "lgtm thanks for the fix"],
    "question_to_us": ["can you explain why you made this change", "did you test this locally how does it work"],
}
DECLINE_CLASSES = ("closed_already_assigned", "claimed_by_other", "needs_human_skill", "low_effort_placeholder",
                   "closed_resolved", "hostile_spam_flag")
SEMANTIC_MIN = float(os.environ.get("TRIBUTE_S1_SEMANTIC_MIN", "0.34"))
_STOP = set("the a an to of and or is it this that for on in be we you i are was with not as at by our your so its if".split())


def _stems(text: str) -> dict:
    out: dict[str, int] = {}
    text = re.sub(r"```.*?```|<!--.*?-->|https?://\S+", " ", (text or "").lower(), flags=re.S).replace("’", "'")
    for w in re.findall(r"[a-z]+", text):
        if w in _STOP or len(w) < 3:
            continue
        w = w[:5]
        out[w] = out.get(w, 0) + 1
    return out


def _cos(a: dict, b: dict) -> float:
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(k, 0) for k, v in a.items())
    na = sum(v * v for v in a.values()) ** 0.5
    nb = sum(v * v for v in b.values()) ** 0.5
    return dot / (na * nb) if na and nb else 0.0


_PROTO = {k: [_stems(t) for t in v] for k, v in PROTOTYPES.items()}


def semantic_scores(text: str) -> dict:
    """Cosine of the text against each class prototype (max over prototypes)."""
    v = _stems(text)
    if len(v) > 120:  # long technical bodies dilute; score the first part only
        v = _stems(" ".join((text or "").split()[:160]))
    return {k: round(max(_cos(v, p) for p in ps), 3) for k, ps in _PROTO.items()}


def semantic_decline(text: str) -> tuple[str, float] | None:
    sc = semantic_scores(text)
    best = max(DECLINE_CLASSES, key=lambda k: sc[k])
    return (best, sc[best]) if sc[best] >= SEMANTIC_MIN else None


# ---------------------------------------------------------------- features
def extract_features(thread: dict) -> dict:
    subject = thread.get("subject") or {}
    comments = dedupe_comments(thread.get("comments") or [])
    linked = thread.get("linked_issue") or {}
    me = (thread.get("self_login") or SELF_LOGIN).lower()
    roles = [author_role(c, subject) for c in comments]
    human_ext = [c for c, r in zip(comments, roles) if r not in ("self", "bot")]
    maint = [c for c, r in zip(comments, roles) if r in ("owner", "maintainer")]
    claim_src = comments + list(linked.get("comments") or [])
    claims = prior_claims(claim_src, subject)
    marker = our_marker_ts(claim_src)
    claims_before_us = [c for c in claims if marker and _ts(c["at"]) and _ts(c["at"]) <= marker]
    assignees = [a for a in (subject.get("assignees") or []) + (linked.get("assignees") or []) if a.lower() != me]
    skill_txt = " ".join([subject.get("body") or ""] + [c.get("body") or "" for c in maint])
    wave_accepted, wave_completed = [], []
    for c in claim_src:
        b = c.get("body") or ""
        for rx, bucket in ((RX["wave_accepted"], wave_accepted), (RX["wave_completed"], wave_completed)):
            m = rx.search(b)
            if m and m.group(1).lower() != me:
                bucket.append(m.group(1))
    closed_at = _ts(subject.get("closed_at"))
    claimed_after_close = bool(closed_at and marker and marker > closed_at)
    # Our consecutive comments at the tail of the thread (follow-up spam guard).
    tail_self = 0
    for c, r in zip(reversed(comments), reversed(roles)):
        if r == "self":
            tail_self += 1
        elif r == "bot":
            continue
        else:
            break
    last_ext = next((c for c, r in zip(reversed(comments), reversed(roles)) if r not in ("self", "bot")), None)
    return {
        "kind": subject.get("kind"),
        "state": subject.get("state"),
        "merged": bool(subject.get("merged")),
        "closed_by_other": subject.get("state") == "closed" and (subject.get("closed_by") or "").lower() not in ("", me),
        "assigned_to_other": assignees,
        "linked_issue": linked.get("url"),
        "n_comments": len(comments),
        "n_external_human": len(human_ext),
        "n_maintainer": len(maint),
        "maintainer_mentions_us": any(f"@{me}" in (c.get("body") or "").lower() for c in maint),
        "anyone_mentions_us": any(f"@{me}" in (c.get("body") or "").lower() for c in human_ext),
        "claims": claims,
        "claims_before_us": claims_before_us,
        "skill": skill_requirement(skill_txt) or (
            "language:unspecified" if {"translation", "i18n"} & {l.lower() for l in subject.get("labels") or []}
            and RX["human_only"].search(skill_txt) else None),
        "placeholder": placeholder_diff(thread.get("files")),
        "reviews": [r.get("state") for r in thread.get("reviews") or []],
        "bots": sorted({c.get("author") for c, r in zip(comments, roles) if r == "bot"}),
        "our_marker_at": marker.isoformat() if marker else None,
        "wave_accepted": wave_accepted,
        "wave_completed": wave_completed,
        "claimed_after_close": claimed_after_close,
        "self_tail_comments": tail_self,
        "last_external_semantic": semantic_decline(last_ext.get("body") or "") if last_ext else None,
    }


# ---------------------------------------------------------------- classify
def _add(scores: dict, label: str, conf: float, why: str) -> None:
    cur = scores.get(label)
    if cur is None or conf > cur["confidence"]:
        scores[label] = {"label": label, "confidence": round(min(conf, 0.99), 2), "evidence": [why] + (cur["evidence"] if cur else [])}
    else:
        cur["evidence"].append(why)


def classify(thread: dict, feats: dict | None = None) -> list[dict]:
    f = feats or extract_features(thread)
    subject = thread.get("subject") or {}
    comments = dedupe_comments(thread.get("comments") or [])
    s: dict[str, dict] = {}

    if f["merged"]:
        _add(s, "merged", 0.98, "state:merged")
    for r in f["reviews"]:
        if r == "CHANGES_REQUESTED":
            _add(s, "changes_requested", 0.9, "review:CHANGES_REQUESTED")
        if r == "APPROVED":
            _add(s, "approved", 0.9, "review:APPROVED")

    for c in comments:
        role = author_role(c, subject)
        if role in ("self", "bot"):
            continue
        body = c.get("body") or ""
        trusted = role in ("owner", "maintainer")
        w = 1.0 if trusted else 0.6
        cid = c.get("id")
        if RX["already_assigned"].search(body):
            base = 0.8 + (0.15 if f["closed_by_other"] else 0) + (0.04 if f["assigned_to_other"] else 0)
            _add(s, "closed_already_assigned" if f["state"] == "closed" else "claimed_by_other", base * w, f"text:already_assigned@{cid}")
        if RX["placeholder"].search(body):
            _add(s, "low_effort_placeholder", (0.8 + 0.15 * f["placeholder"]["is_placeholder"]) * w, f"text:placeholder@{cid}")
        sk = skill_requirement(body)
        if sk or (trusted and RX["human_only"].search(body)):
            conf = 0.7 + (0.15 if sk else 0) + (0.12 if RX["human_only"].search(body) else 0)
            _add(s, "needs_human_skill", conf * w, f"text:skill:{sk or 'human_only'}@{cid}")
        if RX["claim"].search(body) and not trusted:
            # Any human competing claim is enough to yield: we never race a person for an issue.
            conf = 0.76 + (0.12 if RX["yield_demand"].search(body) else 0) + (0.07 if f["claims_before_us"] else 0)
            _add(s, "claimed_by_other", conf, f"text:claim:{c.get('author')}@{cid}")
        if RX["spam"].search(body):
            conf = 0.85 if trusted else (0.8 if RX["ban_request"].search(body) else 0.5)
            _add(s, "hostile_spam_flag", conf, f"text:spam_or_bot:{role}@{cid}")
        if trusted and RX["changes"].search(body) and f["state"] != "closed":
            _add(s, "changes_requested", 0.78, f"text:changes@{cid}")
        if trusted and RX["approve"].search(body) and f["state"] != "closed" and not RX["changes"].search(body):
            _add(s, "approved", 0.7, f"text:approve@{cid}")
        if trusted and RX["merged_txt"].search(body) and f["merged"]:
            _add(s, "merged", 0.98, f"text:merged@{cid}")
        if trusted and f["maintainer_mentions_us"] and RX["question"].search(body) and f["state"] != "closed":
            _add(s, "question_to_us", 0.8, f"text:question@{cid}")
        # Semantic layer: corroborates a token hit, or proposes a sub-threshold label for the LLM rung.
        sc = semantic_scores(body)
        best = max(sc, key=sc.get)
        if sc[best] >= SEMANTIC_MIN:
            if best in s:
                s[best]["confidence"] = round(min(s[best]["confidence"] + 0.03, 0.99), 2)
                s[best]["evidence"].append(f"semantic:{sc[best]}@{cid}")
            elif trusted and best != "question_to_us":
                _add(s, best, min(0.45 + 0.4 * sc[best], 0.7), f"semantic:{best}:{sc[best]}@{cid}")

    # Structural evidence (no text needed)
    owner = (subject.get("repo") or "/").split("/")[0].lower()
    closer_only = (f["assigned_to_other"] and {a.lower() for a in f["assigned_to_other"]}
                   <= {(subject.get("closed_by") or "").lower(), owner})
    if f["closed_by_other"] and not f["merged"] and f["assigned_to_other"] and not closer_only:
        _add(s, "closed_already_assigned", 0.82, f"state:closed+assigned:{','.join(f['assigned_to_other'])}")
    if f["wave_completed"]:
        _add(s, "closed_already_assigned" if f["state"] == "closed" else "claimed_by_other", 0.95,
             f"timeline:completed_by:{f['wave_completed'][0]}")
    if f["wave_accepted"]:
        _add(s, "claimed_by_other", 0.93, f"timeline:accepted:{f['wave_accepted'][0]}")
    if (f["kind"] == "issue" and f["state"] == "closed" and f["closed_by_other"]
            and (not f["assigned_to_other"] or closer_only) and not f["wave_completed"]):
        _add(s, "closed_resolved", 0.95 if f["claimed_after_close"] else 0.85,
             "state:closed_by_maintainer" + ("+timeline:claimed_after_close" if f["claimed_after_close"] else ""))
    if f["placeholder"]["is_placeholder"]:
        _add(s, "low_effort_placeholder", 0.6 + 0.3 * f["placeholder"]["score"], "diff:" + "+".join(f["placeholder"]["reasons"]))
    if f["state"] == "open" and f["assigned_to_other"] and f["kind"] == "issue":
        _add(s, "claimed_by_other", 0.85, f"state:assigned:{','.join(f['assigned_to_other'])}")
    if f["claims_before_us"]:
        _add(s, "claimed_by_other", 0.8, f"timeline:prior_claim:{f['claims_before_us'][0]['author']}")
    if f["skill"] and f["kind"] == "issue":
        _add(s, "needs_human_skill", 0.7, f"body:skill:{f['skill']}")

    order = {l: i for i, l in enumerate(PRIORITY)}
    return sorted(s.values(), key=lambda x: (order[x["label"]], -x["confidence"]))


# ---------------------------------------------------------------- route
def _key(subject: dict) -> str:
    return f"tribute-s1/{subject.get('repo', '?')}/{subject.get('number', '?')}"


def prefilter_rules(labels: dict, feats: dict) -> list[dict]:
    rules = []
    if "closed_already_assigned" in labels or feats["assigned_to_other"]:
        rules.append({"rule": "require_unassigned_issue", "stage": "scout+claim", "effect": "exclude"})
    if "low_effort_placeholder" in labels:
        rules.append({"rule": "block_placeholder_pr", "stage": "contribute", "effect": "no stake-only PRs; real patch or no PR"})
    if "needs_human_skill" in labels:
        rules.append({"rule": "skill_language_filter", "stage": "scout+claim", "effect": "exclude",
                      "skill": feats.get("skill") or "human_only"})
    if "claimed_by_other" in labels:
        rules.append({"rule": "yield_to_prior_claim", "stage": "claim", "effect": "exclude if a human claimed first or is assigned"})
    if "hostile_spam_flag" in labels:
        rules.append({"rule": "repo_cooldown", "stage": "scout", "effect": "skip repo 30d"})
    if "closed_resolved" in labels or feats.get("claimed_after_close"):
        rules.append({"rule": "require_open_issue", "stage": "scout+claim", "effect": "never claim a closed issue"})
    if feats.get("wave_accepted") or feats.get("wave_completed"):
        rules.append({"rule": "skip_bounty_program_issue", "stage": "scout", "effect": "issues run by an application program (e.g. Drips Wave) are assigned by the program"})
    if feats.get("self_tail_comments", 0) >= FOLLOWUP_CAP:
        rules.append({"rule": "followup_cap", "stage": "followup", "effect": f"no more than {FOLLOWUP_CAP} unanswered follow-ups"})
    return rules


def delphi_signal(primary: str | None, subject: dict, placeholder_merge: bool = False) -> dict | None:
    if not primary:
        return None
    if primary == "merged" and placeholder_merge:
        # A maintainer merged a stake/placeholder file: not a contribution, never a +1.
        return {"surface": "tribute-lane", "repo": subject.get("repo"), "outcome": "merged", "weight": 0.0,
                "lesson": "placeholder_merge_not_a_win"}
    weight = {"closed_resolved": -0.2, "merged": 1.0, "approved": 0.5, "changes_requested": 0.1, "question_to_us": 0.0,
              "claimed_by_other": -0.3, "needs_human_skill": -0.4, "closed_already_assigned": -0.6,
              "low_effort_placeholder": -0.8, "hostile_spam_flag": -1.0}[primary]
    return {"surface": "tribute-lane", "repo": subject.get("repo"), "outcome": primary, "weight": weight,
            "lesson": {"merged": "repeat", "approved": "repeat"}.get(primary, "reweight")}


PROGRAMMATIC_PREFIXES = ("state:", "review:", "diff:", "timeline:", "body:")


def replan(feats: dict, labels: list[dict], why: str) -> dict:
    """Rung 3: the system re-plans the lane itself. No human in the loop."""
    by = {l["label"] for l in labels}
    steps: list[str] = []
    if feats["assigned_to_other"] or feats["claims"] or "claimed_by_other" in by:
        steps.append("yield_lane")
    elif feats["state"] == "closed" and not feats["merged"]:
        steps.append("retire_lane")
    elif "hostile_spam_flag" in by:
        steps += ["retire_lane", "repo_cooldown"]
    else:
        steps.append("park_lane")  # stop engaging; only fresh maintainer activity re-opens it
    steps += ["tighten_prefilters", "delphi_reweight", "pick_next_candidate"]
    return {"why": why, "steps": steps}


def route(thread: dict, labels: list[dict] | None = None, feats: dict | None = None,
          system2: dict | None = None) -> dict:
    """Ladder (no HITL): programmatic -> system1 -> system2_llm -> replan.

    `system2` is the optional LLM verdict {"label", "confidence", "unsure",
    "needs_public_reply"}. When the LLM is unsure the system re-plans the lane
    itself. The only Owner stop is a standing rule (posting on a third-party
    repo); it is recorded as owner_required and counted as HITL cost.
    """
    subject = thread.get("subject") or {}
    feats = feats or extract_features(thread)
    labels = labels if labels is not None else classify(thread, feats)
    by = {l["label"]: l for l in labels}
    confident = [l for l in labels if l["confidence"] >= CONFIDENT]
    primary = confident[0]["label"] if confident else None
    plan = None
    owner_required = None

    if confident and all(e.startswith(PROGRAMMATIC_PREFIXES) for e in confident[0]["evidence"][:1]):
        rung, reason = "programmatic", "deterministic_signal"
    elif confident:
        rung, reason = "system1", "confident"
    elif not labels and not feats["n_maintainer"] and not feats.get("anyone_mentions_us"):
        # Programmatic: nobody with access spoke and nobody addressed us -> nothing to route.
        rung, reason = "programmatic", "no_signal_for_us"
    elif feats["n_external_human"]:
        rung, reason = "system2_llm", "low_confidence" if labels else "no_label"
    else:
        rung, reason = "system1", "no_external_activity"
    # A question to us cannot be settled by rules: the LLM decides between a
    # patch revision, a re-plan, or (standing rule) an Owner-approved reply.
    if primary == "question_to_us":
        rung, reason = "system2_llm", "question_to_us"

    if system2 is not None and rung == "system2_llm":
        conf = float(system2.get("confidence") or 0)
        if system2.get("unsure") or conf < CONFIDENT:
            rung, reason = "replan", "system2_unsure"
            plan = replan(feats, labels, reason)
        elif system2.get("needs_public_reply"):
            primary, rung, reason = system2.get("label") or primary, "system2_llm", "system2_confident"
            owner_required = "post_on_third_party_repo"
            plan = {"why": "reply drafted; posting upstream is a standing Owner stop", "steps": ["park_lane", "pick_next_candidate"]}
        else:
            primary, rung, reason = system2.get("label"), "system2_llm", "system2_confident"

    if rung == "replan":
        action = plan["steps"][0]
    elif rung == "system2_llm" and system2 is None:
        action = "llm_review"
    elif reason in ("no_external_activity", "no_signal_for_us"):
        action = "noop"
    else:
        action = ACTIONS.get(primary, "noop")
        if action == "escalate":
            action = "park_lane"
    placeholder_merge = primary == "merged" and "low_effort_placeholder" in by
    if placeholder_merge:
        action = "record_placeholder_merge"
    sem_decline = feats.get("last_external_semantic")
    reengage = (not (set(by) & NO_REENGAGE) and rung in ("programmatic", "system1")
                and primary in (None, "changes_requested", "approved")
                and feats.get("self_tail_comments", 0) < FOLLOWUP_CAP
                and not sem_decline
                and subject.get("state") != "closed"
                and not (reason == "no_signal_for_us" and feats["n_external_human"])
                and feats.get("kind") != "issue")  # we only follow up our own PRs, never issue threads
    out = {
        "schema": SCHEMA,
        "subject": {k: subject.get(k) for k in ("repo", "number", "kind", "url", "state")},
        "labels": labels,
        "primary": primary,
        "action": action,
        "rung": rung,
        "reason": reason,
        "escalate": rung not in ("programmatic", "system1"),
        "llm_call": rung == "system2_llm" or (system2 is not None),
        "owner_required": owner_required,
        "plan": plan,
        "reengage_allowed": reengage,
        "reengage_block": None if reengage else (
            "class" if set(by) & NO_REENGAGE else "followup_cap" if feats.get("self_tail_comments", 0) >= FOLLOWUP_CAP
            else "semantic_decline" if sem_decline else "closed" if subject.get("state") == "closed"
            else "not_addressed_to_us" if reason == "no_signal_for_us"
            else "issue_thread" if feats.get("kind") == "issue" else "rung"),
        "prefilter_rules": prefilter_rules(by, feats),
        "features": feats,
        "delphi_signal": delphi_signal(primary, subject, placeholder_merge),
    }
    out["lane_event"] = {
        "lane": "tribute", "workflow": "tribute-system1", "event_type": f"s1:{action}",
        "repo": subject.get("repo") or "", "subject_url": subject.get("url") or "",
        "payload": {"primary": primary, "rung": rung, "plan": plan, "labels": {l["label"]: l["confidence"] for l in labels}},
    }
    # Audit-only record for hitl_control_plane (never AWAITING_APPROVAL).
    out["audit"] = {"intent": f"tribute:{action}", "target": subject.get("url"), "state": "RECORDED", "audit_only": True}
    return out


def reengage_allowed(thread: dict) -> bool:
    """Gate for help_wanted_followup.decide_action: a timing-based 'reengage'
    must only fire when System 1 sees no decline/claim/close class."""
    return bool(route(thread)["reengage_allowed"])


# ---------------------------------------------------------------- candidate preflight
def preflight_candidate(issue: dict, comments: list[dict] | None = None, self_login: str | None = None) -> dict:
    """Scout/claim gate run BEFORE we comment or open a PR on a foreign issue."""
    me = (self_login or SELF_LOGIN).lower()
    subject = dict(issue, kind="issue")
    comments = dedupe_comments(comments or [])
    reasons = []
    others = [a for a in issue.get("assignees") or [] if str(a).lower() != me]
    if others:
        reasons.append(f"assigned:{','.join(others)}")
    claims = prior_claims(comments, subject)
    if claims:
        reasons.append(f"claimed_by:{claims[0]['author']}")
    text = " ".join([issue.get("body") or ""] + [c.get("body") or "" for c in comments if author_role(c, subject) in ("owner", "maintainer")])
    sk = skill_requirement(text)
    if sk:
        reasons.append(f"needs_human_skill:{sk}")
    elif RX["human_only"].search(text):
        reasons.append("needs_human_skill:human_only")
    for c in comments:
        for key in ("wave_accepted", "wave_completed"):
            m = RX[key].search(c.get("body") or "")
            if m and m.group(1).lower() != me:
                reasons.append(f"{key}:{m.group(1)}")
    if any(RX["spam"].search(c.get("body") or "") and author_role(c, subject) not in ("self", "bot") for c in comments):
        reasons.append("hostile_spam_flag")
    if issue.get("state") == "closed":
        reasons.append("closed")
    return {"eligible": not reasons, "reasons": reasons}


def preflight_pr(files: list[dict]) -> dict:
    p = placeholder_diff(files)
    return {"allowed": not p["is_placeholder"], "placeholder": p}


# ---------------------------------------------------------------- Gmail fallback
_URL = re.compile(r"https://github\.com/([^/\s]+/[^/\s]+)/(issues|pull)/(\d+)(#issuecomment-(\d+))?")
_SUBJ = re.compile(r"\[([^\]]+)\]\s*(.*?)\s*\((?:PR|Issue)\s*#(\d+)\)", re.I)


def parse_github_email(subject: str, body: str, from_header: str = "") -> dict | None:
    """Turn a GitHub notification email into a one-comment thread."""
    m = _URL.search(body or "")
    s = _SUBJ.search(subject or "")
    if not m and not s:
        return None
    repo = m.group(1) if m else s.group(1)
    num = int(m.group(3) if m else s.group(3))
    kind = "pull_request" if (m and m.group(2) == "pull") or "(PR" in (subject or "") else "issue"
    author = re.sub(r"\s*<.*", "", from_header).strip().strip('"') or "unknown"
    text = re.split(r"\n—\s*\nReply to this email directly|\nReply to this email directly", body or "")[0].strip()
    cid = m.group(5) if m and m.group(5) else hashlib.sha1((subject + text).encode()).hexdigest()[:16]
    closed = bool(re.search(r"^Closed #\d+|closed this", body or "", re.I | re.M))
    return {
        "self_login": SELF_LOGIN,
        "subject": {"repo": repo, "number": num, "kind": kind, "url": f"https://github.com/{repo}/{'pull' if kind == 'pull_request' else 'issues'}/{num}",
                    "state": "closed" if closed else "open", "labels": [], "assignees": [],
                    "closed_by": repo.split("/")[0] if closed else None},
        "comments": [{"id": cid, "author": repo.split("/")[0] if author.lower() == repo.split("/")[0].lower() else author,
                      "association": "OWNER" if author.lower() == repo.split("/")[0].lower() else "", "body": text}],
        "source": "gmail",
    }


# ---------------------------------------------------------------- live ingest (read-only)
def _gh(path: str) -> Any:
    import urllib.request
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
    req = urllib.request.Request(path if path.startswith("http") else f"https://api.github.com{path}", headers={
        "Accept": "application/vnd.github+json", "User-Agent": "tribute-system1",
        **({"Authorization": f"Bearer {tok}"} if tok else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or b"null")


def hydrate(repo: str, number: int) -> dict:
    """Read-only fetch of one foreign thread into the fixture shape. GET only."""
    iss = _gh(f"/repos/{repo}/issues/{number}")
    kind = "pull_request" if iss.get("pull_request") else "issue"
    subj = {"repo": repo, "number": number, "kind": kind, "url": iss["html_url"], "title": iss.get("title"),
            "state": iss.get("state"), "state_reason": iss.get("state_reason"), "author": iss["user"]["login"],
            "assignees": [a["login"] for a in iss.get("assignees") or []], "labels": [l["name"] for l in iss.get("labels") or []],
            "body": (iss.get("body") or "")[:1500], "closed_by": (iss.get("closed_by") or {}).get("login"),
            "created_at": iss.get("created_at"), "closed_at": iss.get("closed_at")}
    cm = [{"id": c["id"], "author": c["user"]["login"], "author_type": c["user"]["type"], "association": c["author_association"],
           "created_at": c["created_at"], "body": c["body"]} for c in _gh(f"/repos/{repo}/issues/{number}/comments?per_page=100")]
    thread = {"self_login": SELF_LOGIN, "subject": subj, "comments": cm}
    if kind == "pull_request":
        pr = _gh(f"/repos/{repo}/pulls/{number}")
        subj["merged"] = bool(pr.get("merged"))
        thread["files"] = [{"filename": f["filename"], "status": f["status"], "additions": f["additions"],
                            "deletions": f["deletions"], "patch": (f.get("patch") or "")[:2000]} for f in _gh(f"/repos/{repo}/pulls/{number}/files")]
        thread["reviews"] = [{"state": r["state"], "author": r["user"]["login"]} for r in _gh(f"/repos/{repo}/pulls/{number}/reviews")]
        m = re.search(rf"github\.com/{re.escape(repo)}/issues/(\d+)|(?:fixes|closes|resolves|for)\s+#(\d+)", subj["body"] or "", re.I)
        if m:
            li = hydrate(repo, int(m.group(1) or m.group(2)))
            thread["linked_issue"] = dict(li["subject"], comments=li["comments"])
    return thread


def discover(since: str, self_login: str = SELF_LOGIN, limit: int = 300) -> list[tuple[str, int]]:
    """Foreign PRs we authored (open AND closed) and foreign issues we commented on."""
    import urllib.parse
    out: set[tuple[str, int]] = set()
    for q in (f"author:{self_login} type:pr -user:{self_login} updated:>={since}",
              f"commenter:{self_login} type:issue -user:{self_login} updated:>={since}"):
        for page in range(1, 11):
            res = _gh(f"/search/issues?per_page=100&page={page}&q=" + urllib.parse.quote(q)) or {}
            items = res.get("items", [])
            for it in items:
                out.add((it["repository_url"].split("/repos/")[1], it["number"]))
            if len(items) < 100 or len(out) >= limit:
                break
    return sorted(out)[:limit]


# ---------------------------------------------------------------- CLI
def run(threads: Iterable[dict]) -> list[dict]:
    return [route(t) for t in threads]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("classify", help="classify fixture/thread JSON files")
    c.add_argument("paths", nargs="+")
    s = sub.add_parser("scan", help="read-only live scan of foreign threads (backfill with an old --since)")
    s.add_argument("--since", default="2026-09-01")
    s.add_argument("--limit", type=int, default=300)
    for p in (c, s):
        p.add_argument("--out", default="", help="decisions JSONL")
        p.add_argument("--lane-events", default="", help="lane_event.py --events-file JSONL")
        a = ap.parse_args(argv)
    if a.cmd == "classify":
        threads = [json.loads(Path(p).read_text(encoding="utf-8")) for p in a.paths]
    else:
        threads = []
        for repo, num in discover(a.since, limit=a.limit):
            try:
                threads.append(hydrate(repo, num))
            except Exception as e:  # noqa: BLE001 - never fail the caller
                print(f"::warning::hydrate {repo}#{num}: {type(e).__name__}", file=sys.stderr)
    decisions = run(threads)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def dump(path: str, rows: Iterable[dict]) -> None:
        if path:
            Path(path).write_text("".join(json.dumps(r, sort_keys=True, default=str) + "\n" for r in rows), encoding="utf-8")
    dump(a.out, decisions)
    dump(a.lane_events, [dict(d["lane_event"], occurred_at=now) for d in decisions])
    for d in decisions:
        print(f"{d['subject']['repo']}#{d['subject']['number']}\t{d['primary']}\t{d['action']}\t{d['rung']}\t"
              + ",".join(f"{l['label']}:{l['confidence']}" for l in d["labels"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
