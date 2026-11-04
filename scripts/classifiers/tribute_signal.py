#!/usr/bin/env python3
"""tribute-signal v1 — maintainer-signal classifier for tribute (foreign-repo) PRs.

Owner taxonomy (2026-11-03, FIXED — do not redesign). Per PR:
  maintainer signal (one primary + all detected):
    explicit-rejection (sub: placeholder | quality | etiquette)
    cleanup · positive · neutral · adjustment-needed · adjustment-made
  adjustment flag: {required, what, happened} — what context adjustment
    the comment flow required, and whether it happened.

Craft rules (v1, rules tier — precedent: classify_pr, chat-intent):
- Signals fire ONLY on maintainer-authored content. The corpus carries
  author_role per comment/review; bot and contributor text never creates
  a maintainer signal (contributor text is used only as adjustment-made
  evidence: "done / fixed / updated" replies and new commits).
- Every signal carries evidence (source refs + short quotes). No
  evidence, no signal.
- Confidence: high = explicit lexicon hit in maintainer text (state
  corroboration raises/locks it); medium = single weak marker or
  state-only (e.g. CHANGES_REQUESTED with no body); low = inference
  only. Low-confidence primaries are flagged adjudicate=true — the
  census counts them separately, never silently.
- Primary precedence: explicit-rejection > adjustment-made >
  adjustment-needed > cleanup > positive > neutral. All detected
  signals are still listed in signals[].
- Close state alone is NEVER a rejection: closed_unmerged without
  maintainer rejection text stays neutral (superseded/stale closes
  are common). Rejection requires maintainer words.

Input: one JSON object per PR (JSONL corpus built by the swarm lane):
  {pr_ref, repo, number, title, state: open|merged|closed_unmerged,
   comments: [{id, author, author_role, body, created_at}],
   reviews:  [{id, author, author_role, state, body, created_at}],
   timeline: [{type: committed|closed|merged|reopened, at, actor}]}
  author_role in {maintainer, contributor, other, bot}.

Output: one verdict JSON per PR (see classify()).
Deterministic, stdlib only.
"""
import json
import re
import sys

VERSION = "tribute-signal v1"

# ---------------------------------------------------------------- lexicons
REJECTION = {
    "placeholder": [
        "placeholder", "just a template", "template only", "empty pr",
        "no changes", "doesn't change anything", "does not change anything",
        "dummy pr", "test pr", "no actual change",
    ],
    "quality": [
        "low quality", "low-quality", "ai-generated", "ai generated",
        "ai slop", "chatgpt", "spam", "not a real contribution",
        "doesn't fix", "does not fix", "this is wrong", "wrong approach",
        "breaks the build", "makes things worse",
    ],
    "etiquette": [
        "read the contributing", "contributing guidelines", "code of conduct",
        "open an issue first", "discuss first", "duplicate pr",
        "already exists", "rude", "off-topic", "off topic",
    ],
}
CLEANUP = [
    "remove the", "delete the", "revert", "clean up", "cleanup",
    "leftover", "generated file", "don't commit", "do not commit",
    "unnecessary file", "binary file", "remove this file", "stray file",
]
ADJUSTMENT = [
    "please change", "please add", "please fix", "please update",
    "could you", "can you", "needs", "please address", "failing",
    "ci is", "tests are failing", "rename", "move this to",
    "instead of", "should be", "missing",
]
POSITIVE = [
    "lgtm", "looks good", "thank", "great", "nice work", "nice catch",
    "welcome", "well done", "perfect", "awesome",
]
DONE = ["done", "fixed", "updated", "addressed", "pushed", "applied"]

PRECEDENCE = ["explicit-rejection", "adjustment-made", "adjustment-needed",
              "cleanup", "positive", "neutral"]


def _hits(text, phrases):
    t = " " + re.sub(r"\s+", " ", (text or "").lower()) + " "
    return [p for p in phrases if p in t]


def _quote(text, limit=120):
    t = re.sub(r"\s+", " ", (text or "")).strip()
    return t[:limit]


def classify(pr):
    """Return the verdict dict for one corpus record."""
    found = {}  # signal -> {confidence, subtype, evidence[]}

    def add(signal, conf, ev, subtype=None):
        rank = {"low": 0, "medium": 1, "high": 2}
        cur = found.get(signal)
        if cur is None or rank[conf] > rank[cur["confidence"]]:
            found[signal] = {"confidence": conf, "subtype": subtype,
                             "evidence": list(ev)}
        else:
            cur["evidence"].extend(ev)

    maint_items = []   # (kind, item) maintainer-authored
    for c in pr.get("comments", []):
        if c.get("author_role") == "maintainer":
            maint_items.append(("comment", c))
    for r in pr.get("reviews", []):
        if r.get("author_role") == "maintainer":
            maint_items.append(("review", r))

    adj_first_at = None       # earliest adjustment ask timestamp
    adj_what = None
    for kind, it in maint_items:
        body = it.get("body") or ""
        ref = {"type": kind, "ref": it.get("id"), "quote": _quote(body)}
        # explicit rejection, per subtype
        for sub, phrases in REJECTION.items():
            h = _hits(body, phrases)
            if h:
                conf = "high"
                add("explicit-rejection", conf, [dict(ref, matched=h)],
                    subtype=sub)
        # cleanup
        h = _hits(body, CLEANUP)
        if h:
            add("cleanup", "high" if len(h) > 1 else "medium",
                [dict(ref, matched=h)])
        # adjustment ask: lexicon or CHANGES_REQUESTED
        h = _hits(body, ADJUSTMENT)
        cr = kind == "review" and it.get("state") == "CHANGES_REQUESTED"
        if h or cr:
            conf = "high" if h else "medium"
            add("adjustment-needed", conf,
                [dict(ref, matched=h or ["CHANGES_REQUESTED"])])
            at = it.get("created_at")
            if adj_first_at is None or (at and at < adj_first_at):
                adj_first_at, adj_what = at, _quote(body)
        # positive
        h = _hits(body, POSITIVE)
        appr = kind == "review" and it.get("state") == "APPROVED"
        if h or appr:
            add("positive", "high" if h else "medium",
                [dict(ref, matched=h or ["APPROVED"])])

    # adjustment-made: an ask exists AND later evidence of the fix
    happened = None
    made_ev = []
    if "adjustment-needed" in found:
        happened = False
        for e in pr.get("timeline", []):
            if e.get("type") == "committed" and adj_first_at and \
                    (e.get("at") or "") > adj_first_at:
                made_ev.append({"type": "timeline", "ref": "committed",
                                "quote": e.get("at")})
        for c in pr.get("comments", []):
            if c.get("author_role") == "contributor" and adj_first_at and \
                    (c.get("created_at") or "") > adj_first_at and \
                    _hits(c.get("body"), DONE):
                made_ev.append({"type": "comment", "ref": c.get("id"),
                                "quote": _quote(c.get("body"))})
        if pr.get("state") == "merged":
            made_ev.append({"type": "state", "ref": "merged",
                            "quote": "PR merged after adjustment ask"})
        if made_ev:
            happened = True
            add("adjustment-made", "high" if len(made_ev) > 1 else "medium",
                made_ev)

    if not found:
        add("neutral", "high", [{"type": "state", "ref": pr.get("state"),
                                  "quote": "no maintainer signal detected"}])

    primary = next(s for s in PRECEDENCE if s in found)
    pv = found[primary]
    adjustment = {
        "required": "adjustment-needed" in found,
        "what": adj_what,
        "happened": happened,
    }
    return {
        "pr_ref": pr.get("pr_ref"),
        "primary_signal": primary,
        "rejection_subtype": pv["subtype"] if primary == "explicit-rejection"
        else None,
        "signals": [{"signal": s, "confidence": v["confidence"],
                     "subtype": v["subtype"], "evidence": v["evidence"]}
                    for s, v in sorted(
                        found.items(),
                        key=lambda kv: PRECEDENCE.index(kv[0]))],
        "adjustment": adjustment,
        "confidence_overall": pv["confidence"],
        "adjudicate": pv["confidence"] == "low",
        "classifier": VERSION,
        "rules_fired": sorted(found.keys()),
    }


def main(argv):
    out = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            out.append(classify(json.loads(line)))
    for v in out:
        print(json.dumps(v))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
