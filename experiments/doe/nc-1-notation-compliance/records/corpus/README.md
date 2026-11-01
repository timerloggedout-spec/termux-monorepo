# nc-1 gold corpus v1 — 32 units, labels committed before scoring

`[MUSEai]@{role:{doe-mgr-classifier-tuning}}` · snapshot 2026-10-31 ·
labels = this lane's adjudication vs spec #320 + #1734; disputes =>
doe-expert (verdict owner). Corpus = `units.jsonl` (verbatim texts).

## Composition (balanced 2×2)

| surface | drift | compliant |
|---|---|---|
| chat (doe-expert 44bb4068 outputs) | 9 | 7 |
| github (PR bodies + issue comments) | 8 | 8 |

Chat units transcribed from `chat.read_messages` reads 2026-10-31;
source locator = message seq in the doe-expert chat (in each unit's
`source` field). GH units extracted verbatim via PAT API (PR/comment
ids in `source`).

## Label rule (execution mode, not intent)

- **drift** = explanatory prose execution: natural-language sentences
  carry the content; symbols/ids sparse. Known positives per DESIGN:
  doe-expert's own prose relays 2026-10-31 (OpenRouter/quota
  explainers, seqs 37676–37950).
- **compliant** = caveman-micro execution: symbol-dense, ids +
  outcomes + refs carry the content (known compliant class).
- A unit with report *function* but prose *execution* labels drift.

## Disclosed build-time decisions

- `chat-c07` (seq 37873, live-3 ruling relay): relabeled
  compliant→drift at corpus build, before commit/scoring — report
  function, prose execution. Only relabel in v1.
- Borderline, labels kept: `gh-c08` (structured review contract,
  prose clauses), `chat-c05` (terse prose correction, id-carrying),
  `gh-d08` (prose notice, ref-heavy). These sit near any threshold
  by construction; they test the detector, not the labeler.
- Single-rater labels (this lane). L1 (main/doe-expert) adjudicates
  FULL-arm flags at run time; corpus label disputes land as corpus
  v2 amendments, never silent edits.

## Feature preview (not scoring)

Deterministic tokenizer (`scripts/doe/nc1_features.py`, harness PR):
drift prose_ratio median 0.838 · compliant 0.656 · ranges overlap
(0.636–0.928 vs 0.491–0.804) ⇒ single-threshold separation is weak
by inspection; run-001 scores it formally. τ in TAU-AMENDMENT.md.
