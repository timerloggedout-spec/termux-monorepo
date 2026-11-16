# tribute-signal v1 — maintainer-signal classifier for tribute PRs

Craft: `scripts/classifiers/tribute_signal.py` (rules tier, stdlib,
deterministic) + `scripts/classifiers/test_tribute_signal.py`
(13/13 at v1.1).

## v1.1 amendments (calibration round 1, 2026-11-03)

Calibration set: 12 records (4 rejections of record + 8 live opens,
hand-labeled by the swarm lane). v1 scored primary 10/12; both
misses diagnosed firsthand from the flows and fixed:

- Haven#657 (etiquette miss): etiquette lexicon += engagement
  phrases verbatim from the flow — "not a person", "from the
  automation", "no real contributor", "no engagement",
  "nothing to track".
- Sail-CLI#23 (placeholder false positive + adjustment-made miss):
  (a) KEEP-OPEN DEMOTION — rejection words inside a flow the
  maintainer explicitly keeps open ("keeping this open", "happy to
  review", …) with the PR not closed_unmerged are a process note,
  not a verdict: the signal stays listed at medium with
  adjudicate=true and yields the primary. (b) DONE lexicon +=
  completion claims "actual fix", "now carries", "implemented".
- v1.1 calibration result: primary 12/12 · rejection subtypes 4/4 ·
  adjustment flags all matching. Sail's verdict is adjustment-made
  at medium + adjudicate (contested-flow honesty), vibewatt#100
  adjustment-made at high.
- Corpus defect noted for the census: timeline `committed` events
  arrive with at=null, so the committed-after-ask leg of
  adjustment-made is blind; v1.1 leans on the contributor-reply and
  merge legs until the harvest carries commit timestamps.
- Seed gaps: cleanup and positive have 0 calibration seeds; the
  census run surfaces round-2 candidates for both classes.
Built by the tier1-classifiers steward at the swarm-optimizer's
request (2026-11-03) so the fleet taxonomy stays ONE taxonomy.
Corpus + census run: swarm lane. Taxonomy: the owner's, fixed —
do not redesign here; amendments go through the owner.

## Taxonomy (verbatim)

Per PR — maintainer signal (one primary, all detected listed):
`explicit-rejection` (sub: `placeholder` | `quality` | `etiquette`) ·
`cleanup` · `positive` · `neutral` · `adjustment-needed` ·
`adjustment-made`.

Per-PR adjustment flag: {required, what, happened} — what context
adjustment the comment flow required, and whether it happened.

## Craft rules

- Signals fire ONLY on maintainer-authored content (`author_role =
  maintainer`). Bot/contributor text never creates a maintainer
  signal; contributor text serves only as adjustment-made evidence.
- Every signal carries evidence (source ref + ≤120-char quote).
  No evidence, no signal.
- Close state alone is never a rejection: closed-unmerged without
  maintainer rejection words stays neutral (superseded/stale closes
  are common in foreign repos).
- Primary precedence: explicit-rejection > adjustment-made >
  adjustment-needed > cleanup > positive > neutral.
- adjustment-made requires an adjustment ask first, then later
  evidence: a `committed` timeline event after the ask, a contributor
  done/fixed reply after the ask, or a merge after the ask.

## Confidence handling

- high = explicit lexicon hit in maintainer text.
- medium = single weak marker, or state-only evidence
  (CHANGES_REQUESTED with no body, APPROVED with no body).
- low = inference only → verdict carries `adjudicate: true`; census
  reporting counts low-confidence primaries separately, never
  silently merged into the headline counts.
- The census deliverable reports TRUE counts per confidence tier and
  a Δ table vs the first (sampled) diagnostics.

## Input shape (JSONL, one record per PR — swarm builds the corpus)

```json
{"pr_ref": "owner/repo#123", "repo": "owner/repo", "number": 123,
 "title": "...", "state": "open|merged|closed_unmerged",
 "comments": [{"id": 1, "author": "...",
   "author_role": "maintainer|contributor|other|bot",
   "body": "...", "created_at": "ISO-8601"}],
 "reviews": [{"id": 1, "author": "...", "author_role": "...",
   "state": "APPROVED|CHANGES_REQUESTED|COMMENTED|DISMISSED",
   "body": "...", "created_at": "ISO-8601"}],
 "timeline": [{"type": "committed|closed|merged|reopened",
   "at": "ISO-8601", "actor": "..."}]}
```

`author_role` is the corpus builder's call (association OWNER/MEMBER/
COLLABORATOR → maintainer; the PR author → contributor). Timestamps
must be comparable ISO strings (adjustment-loop detection depends on
ordering).

## Verdict shape (one JSON per PR)

```json
{"pr_ref": "...", "primary_signal": "...",
 "rejection_subtype": "placeholder|quality|etiquette|null",
 "signals": [{"signal": "...", "confidence": "high|medium|low",
   "subtype": null, "evidence": [{"type": "comment|review|state|timeline",
   "ref": 1, "quote": "...", "matched": ["..."]}]}],
 "adjustment": {"required": true, "what": "...", "happened": true},
 "confidence_overall": "high", "adjudicate": false,
 "classifier": "tribute-signal v1", "rules_fired": ["..."]}
```

## Calibration protocol (before the full 132-PR census)

1. Swarm supplies the 13 hand-sampled PRs (incl. the 4 verbatim
   rejections) in the input shape above, WITH their hand labels.
2. Steward runs v1 over the sample; agreement reported per class.
3. Disagreements are adjudicated (owner taxonomy reading governs);
   rule/lexicon amendments land as v1.x changes with tests — the
   taxonomy itself does not change.
4. Only then the full census. The 8 live opens are included in the
   calibration set if not already among the 13 (they are the
   decision-relevant subset).
