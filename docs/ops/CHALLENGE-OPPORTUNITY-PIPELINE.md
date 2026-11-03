# Challenge Opportunity Pipeline — flow of record

Owner order 2026-11-03 (via main): diagnose whether field recon
runs on packaged OSINT machinery and whether a custom
challenge-opportunity pipeline exists; fix the gap. This doc is
the flow of record; the executable binding is the custom skill
`challenge_opportunity_pipeline` (fleet skill catalog).

## Diagnosis (2026-11-03, firsthand vs master + both catalogs)

| Piece | Verdict |
|---|---|
| OSINT-DISPATCH-TEMPLATE (PR #4526) | exists-as-template — PR open, not on master; acceptance run consumed (#4527) |
| CHALLENGE-OSINT.md | exists-as-doc — on master, the earlier carrier |
| SWARM-RESEARCH-TEMPLATE (PR #4390) | exists-as-template — PR open |
| TAK lens (#4325, scope seed #4332) | exists-as-doctrine — DOE-FAMILY.md / LENS-FRAME.md / LENS-TEMPLATE-TRIGGER.md |
| Dual-valence (#4320, #4323) | exists-as-doctrine — LENS-FRAME + proposals/DUAL-VALENCE.md |
| Podium pipeline (#4501) | exists-as-script/workflow — podium_crawl/ingest/load.py + podium-crawl.yml + schema + tests |
| Competition import (#4550) | exists-as-record — merged doc, produced by hand |
| Opportunity ledger + MoneyBall book | exists-as-data — json/jsonl + docs; hooks hand-fired |
| scripts/challenge/* + tinyfish_osint | script fragments, unbound |
| SWOT | no artifact on master — lens language + lane practice only |
| Binding skill / end-to-end flow | **ABSENT at diagnosis** — field recon (D0 enumeration, D1 recon) ran as lane-craft: hand-written dispatches following the templates' discipline |

Answers, plainly: (1) No — today's D1 Projects recon was
dispatched by hand, not on OSINT machinery. (2) No — there was
no custom pipeline; there were pieces. This doc + the skill
close both.

## The flow (six stages)

0. **Intake** — OPPORTUNITY-SPEC per event (verbatim
   requirements, both rubric frames labeled, gates, deadlines)
   + opportunity-ledger row (append-only) + priority timebox.
1. **OSINT dispatch** — OSINT-DISPATCH-TEMPLATE across five
   source classes; venue Projects grids by live browser to
   exhaustion (roster stable ×3 scrolls / Load-more exhausted),
   every project clicked into for the full Body; About/Rules by
   direct read; a second automated read never overrides a
   firsthand one without the triple-check.
2. **Rows** — one per project: title · body verbatim ·
   description · tags · models/providers named (exact ids,
   "live" claims quoted) · repo · demo/endpoint · video · team
   · likes/comments · cluster (clusters seeded per event before
   the reads). Linked repos get their own read (code? surfaces?
   tests? depth on the rewarded axis).
3. **TAK tracks** — per material rival: {position · time
   (as_of) · state VERIFIED/CLAIMED/NOT_ESTABLISHED}; updates
   stamped, superseded reads kept.
4. **SWOT dual-valence** — both valences stamped on the same
   track; every cell cites a row or is NOT_ESTABLISHED; exact
   enumeration at small n, never Monte Carlo.
5. **Dataset + ledger hooks** — rows handed to the dataset
   owner (Recruitment) as a new version (pin + sha256); drift
   carried as dual dated reads, never averaged, usability
   downgraded in the open; placements NOT_ESTABLISHED until the
   venue publishes (re-check = capture issue); ledger entry
   appended at event close.
6. **Outcomes** — the spec's Outcomes section filled from the
   stamped rows (#4550 pattern); unreceiptable sections stay
   PENDING with the blocker named.

## Acceptance

The packaged stamping runs over the in-flight D1 Projects
recon's rows (consumed, not re-run) and diffs against the
lane-crafted path: same rows, same stamps, and the hand-steps
the packaging removes enumerated — or the remaining gap list
stated. Result appended here on completion.

### Acceptance result — D1 field run, 2026-11-03

Ran the same evening the skill was packaged. The recon
(dispatched as lane-craft at 11:18 PT, before the skill
existed) returned 55 rows; the packaged Stages 1–3 were then
executed over them literally (record: PR #4581).

- **Same rows ✓** — the pipeline consumed the recon's rows
  unchanged; no re-reads, no row diverged.
- **Same stamps ✓** — cluster tally (education 15 ·
  climate-heat 5 · climate-agri 11 · devops 1 · other 23) and
  TAK tracks (SyllabusSync · Ladder · CloudOps Swarm ·
  StudyBuddy) produced from the rows per Stages 2–3.
- **Hand-steps the packaging removes** (next run): the
  dispatch text (was hand-written from the order — now the
  Stage-1 procedure), row-shaping decisions (now the Stage-2
  schema), cluster assignment (seeded, not improvised), and
  the record's home (now this flow's Stage-5/6 pattern).
- **Gaps exposed, honestly:**
  1. The enumeration crossed two same-author cards on OUR OWN
     entry's row (contested in PR #4581; targeted re-read in
     flight). The triple-check rule caught it — via a human
     noticing. **Fixed in the skill**: Stage 1 now carries an
     own-entry cross-check step (verify our row against the
     submission of record before use).
  2. Sidebar repo/demo URLs are not always extractable from
     page text; ~15 rows carry "link present, URL not
     extracted". A targeted link-extraction second pass is a
     Stage-2 refinement — recorded, not yet built.
  3. At field size 55, full-verbatim bodies for every row are
     not achievable in one pass (page-view truncation); the
     priority row is verbatim, the rest section-complete with
     truncations marked — the schema's stated compromise.
