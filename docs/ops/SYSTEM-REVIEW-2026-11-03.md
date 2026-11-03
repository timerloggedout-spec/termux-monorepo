# System Review — Main's Concepts (DoE, 2026-11-03)

Owner order 2026-11-03: main's two concepts run through
the fleet's review system — adversarial (goldfish-class)
pass on assumptions + Delphi scoring + feasibility
against ACTUAL data availability. This document is the
review of record; its verdicts land as amendments to the
placed specs (MoneyBall = test plan · validation lane =
design review · scraping lane = pipeline build).

Delphi filings (concepts presented faithfully; voters
blind to this review): RFP-SYSREV-C1 = issue #4495 ·
RFP-SYSREV-C2 = issue #4496. Scores are recorded in the
verdict sections when the ledgers land; a Delphi score
is one input to the verdict, never the verdict (post
EGM instance #2, scores from this gate are read as
shape-class constants unless the P1/P2 substance channel
has landed — see the caveat in each verdict).

Data availability, verified for this review:
- Podium placements: 11 podium projects pattern-tested
  by main's podium leg (2026-11-03) across ~3 editions
  (RAISE · Milan Agent Olympics · Agent Rush context).
  Agent Rush = FIRST edition: no prior podium. The
  pattern read of record: proof-grounded 10/11 ·
  enterprise workflow 10/11 · approval gates weak
  (1 explicit yes; recurring form = human-in-the-loop).
- Judges: Agent Rush judges are NOT publicly named
  (∅ data). A judges POOL is known only for RAISE.
  Pool membership is not panel assignment: no
  judge×placement or judge×comment linkage is of record.
  The participants mirror (MoneyBall v2) carried judges
  = 0 records at build (PR #2200); event_podium /
  judge_events views exist as schema.
- Full entrant lists (the denominator for any placement
  RATE): NOT of record. Gathered data = podiums.
- Comments: judge/community comment corpora per edition
  = NOT of record as a dataset.

## Concept 1 — Podium ML test plan

**VERDICT: ADOPT-WITH-FIXES.** The structure (tidy
receipted dataset, pre-registered tests, kill signals,
exact methods, ML confined to tagging) is sound and
matches fleet doctrine. The test MENU overclaims against
the actual data in five places:

- **C1-D1 (test ③, judge-panel effects — data support
  fails as stated).** The named constraint does this:
  with Agent Rush judges publicly ∅ and only a RAISE
  pool known, test ③ has NO judge-level data for any
  edition except possibly RAISE, and even there only
  pool membership — no linkage from judges to placements
  or comments. A panel-effect estimate needs
  judge×edition×outcome linkage; none exists. FIX:
  test ③ is DESCOPED to a descriptive RAISE-pool census
  (who is in the pool, what public criteria/statements
  exist) and carries NO effect claims until linkage data
  exists; its kill signal becomes a data-existence gate.
  Panel effects across editions = NOT_ESTABLISHED, and
  any spec text assuming repeat-judge linkage is struck.
- **C1-D2 (denominator missing — tests ①②).** Placement
  RATE per category (②) and over-representation (①)
  both need the full entrant population per edition.
  Gathered data = podiums only (numerators). FIX: until
  entrant lists are ingested (Concept 2's first consumer
  job), ① reports podium COMPOSITION shares with exact
  intervals, labeled as composition — never rates; ② is
  queued behind denominator ingestion.
- **C1-D3 (taxonomy circularity — test ①).** The shape
  taxonomy was induced FROM these same podiums (the
  10/11 pattern read), then test ① proposes testing
  those features' over-representation ON those podiums.
  That is testing on the training set. FIX: the current
  11 projects are the taxonomy's TRAINING stratum; test
  ①'s confirmatory run waits for holdout editions
  (Agent Rush results + the next edition) or is labeled
  EXPLORATORY in every output.
- **C1-D4 (multiplicity + power — test ①).** ≥6 shape
  features × n=11 projects: per-feature exact tests have
  ~no power and the family-wise false-positive risk is
  the finding-generator. FIX: ONE pre-registered primary
  hypothesis (the A∧E composite from the pattern read);
  all other features = secondary, reported with their
  multiplicity, no claim language below the significance
  standard (n · stratum · basis cited or HELD/INTAKE).
- **C1-D5 (backtest = one split — test ⑥).** With ~3
  editions, train ≤n → predict n+1 has exactly ONE
  possible holdout: a single hit/miss is an anecdote,
  not a validation. FIX: test ⑥ runs as a RECORDED
  FORECAST (issued before the next edition's results,
  scored when they land) — evidence accrues per edition;
  no backtest-validity claim until ≥2 scored forecasts.
- **C1-D6 (inferred rubric — test ⑤).** "Each edition's
  inferred rubric" is a model fitted on 11 projects, not
  data. FIX: test ⑤ is a SENSITIVITY analysis over
  stated rubric hypotheses (each labeled as a hypothesis
  with its basis), not a measurement over inferred
  rubrics.
- **C1-D7 (tagging reliability unmeasured).** ML
  feature-tagging feeds every test; tagger error is
  unmeasured. FIX: dual-tag a sample on a second surface
  + report agreement; tags below agreement threshold
  enter as CLAIM-grade inputs (rule 9 pattern: single-leg
  tags held out of weight-bearing runs).

Delphi score: **9.12 / 25 - parked, converged r1, veto false, vote
profile {OPERATOR 9 - builder 9 - reviewer 12 - Scout 15
- cost_auditor 3}** - the filer's shape-class constant,
identical across all ten doe-expert filings in this
series (D1-7, D1-8, EGM2 x6, SYSREV x2) regardless of
substance. It carries no discriminating information
between concepts; the verdict rests on the adversarial
pass + data feasibility, exactly as the caveat states.
(The P1/P2 substance channel, once accepted + merged,
is what would make a future score readable as more
than shape.)

## Concept 2 — Crawl/ingest/store pipeline

**VERDICT: ADOPT-WITH-FIXES.** The concept is the most
doctrine-aligned of the pair (receipts, conflicts kept
as conflicts, version pinning) and it is the
precondition for Concept 1's missing denominators. Four
defects, all fixable at spec level:

- **C2-D1 (store of record unnamed — fork risk).** "Neon
  store + repo snapshots" names two stores and no truth
  hierarchy; the wagering-book precedent had to rule this
  explicitly (repo ledger of record, other surfaces
  derived). FIX: per dataset, ONE store is OF RECORD
  (repo-versioned snapshots recommended: immutable,
  diffable, hashable) and the other is a DERIVED
  projection, rebuilt from record, never edited. The
  spec names the of-record store per dataset before
  build.
- **C2-D2 (conflict consumption rule missing).** Keeping
  conflicts as conflicts is correct; without a stated
  consumption rule, every consumer silently picks a side
  (the failure the concept exists to prevent, one layer
  down). FIX: consumers read conflicts as DISPUTED —
  excluded from weight-bearing use (rule 9), resolvable
  only by a recorded resolution act with its own
  receipt; unresolved conflicts surface in consumer
  outputs as gaps, not picks.
- **C2-D3 (change detection identity).** Change
  detection needs a canonical row identity across crawls
  (source-native id or content key — the mirror's
  content-key dedupe is the in-fleet precedent) plus a
  field-level diff policy, or volatile page furniture
  (timestamps, rotating modules) manufactures false
  changes and version spam. FIX: identity rule +
  diff-relevant field set per source, registered with
  the source; everything outside the field set is not a
  change.
- **C2-D4 (crawl posture per source).** Repeat crawls
  multiply rate-limit and terms exposure; sources differ
  (public pages vs login-gated). The fleet's cost
  doctrine (free only; card-gated parked) and the
  scraping lane's own record bind the tool choice, but
  the concept is silent on per-source cadence, backoff,
  and stop-on-block behavior. FIX: a per-source crawl
  charter {cadence · identity/tool · stop conditions}
  registered before a source goes live; a 403/429 stops
  that source's crawl, never retries around it.
- **C2-D5 (collector identity — minor).** Receipts name
  the collector; for receipts to be weightable later the
  collector must be a configured-instance identity
  (instance_key discipline), not a free-text label. FIX:
  collector = instance_key or the lane's registered
  collector id.
- **Strength noted (not a defect):** the version pin
  must include the conflict-state hash (the concept says
  "including its conflict state" — this review makes it
  explicit and testable: same pin ⇒ byte-identical
  inputs, conflict state included, per the filing's own
  done-evidence).

Feasibility: Neon is provisioned (custom.neon live);
repo snapshots are cheap; the scraping consideration
set exists (scraping lane's record) with one open
dependency (Firecrawl rerun / data-ingestion intake
leg 2) — build sequencing, not a blocker.

Delphi score: **9.12 / 25 - parked, converged r1, veto false, vote
profile {OPERATOR 9 - builder 9 - reviewer 12 - Scout 15
- cost_auditor 3}** - the filer's shape-class constant,
identical across all ten doe-expert filings in this
series (D1-7, D1-8, EGM2 x6, SYSREV x2) regardless of
substance. It carries no discriminating information
between concepts; the verdict rests on the adversarial
pass + data feasibility, exactly as the caveat states.
(The P1/P2 substance channel, once accepted + merged,
is what would make a future score readable as more
than shape.)
