# DeepWiki.com refresh — webWrapper campaign prep

`[MUSEai]@{role:{optimizations-assurance}}` · Owner requirement (2026-11-01, "FIX → AUTOMATE" for the DeepWiki workstream; promotion recorded in `docs/ops/SWARM-OPTIMIZATION-ASSURANCE.md` §18).

## Requirement

DeepWiki.com requires **continuous automated refresh + update**. It has **no documented indexing-write endpoint** (the public MCP at mcp.deepwiki.com is read-only), so the refresh path is **webWrapper UI interaction** — additional to Devin's API automation, which is separately provisioning-gated (`DEVIN_API_KEY` secret + `DEVIN_ORG_ID` / `DEVIN_WIKI_EFFORT` variables; GATES-REGISTER PR #3323).

## Target set

- Primary: `deepwiki.com/timerloggedout-spec/termux-monorepo`.
- Census at first run: every `timerloggedout-spec` repository that has a public DeepWiki page joins the target set; the census result is stamped on the campaign issue.

## Refresh flow (per target, per run)

1. Read the current master tip of the target repo (PAT helper) and the DeepWiki page's visible indexed commit / "last indexed" timestamp.
2. If the page is behind, use the page's refresh/update control to trigger a re-index.
3. Re-read the page until the indexed commit/timestamp advances (bounded wait; a still-behind page at the bound is a stamped datum, not a silent pass).
4. Stamp the campaign issue: `{repo, before: <indexed ref/ts>, after: <indexed ref/ts>, run/session id, builder instance}`.

## Cadence

Continuous = (a) every campaign dispatch, and (b) an episodic staleness check: a target whose indexed commit is >7 days behind its master tip, or behind a major docs change, is queued for the next dispatch. No tight polling (QAC-008 discipline applies).

## Builder wiring (what fires it)

- Dispatch target: the campaign issue **[webWrapper] DeepWiki.com continuous refresh — ww-deepwiki** (session brief embedded in the issue body).
- Builder arm: **Jules session** (campaign pattern: builder ≠ evaluator; evaluator = Gemini, evidence-only, verifying stamps against the live page state).
- Execution is **Jules-gated**: the wave is held at the builder layer until a Jules probe session completes (tally at prep time: created 3 / completed 0 / errored 3). This prep wires everything repo-side so the first recovered arm fires immediately.

## Boundaries

- **Import** of DeepWiki.com material to our surfaces = repo-org tree's design leg (ICM harvest automation, PR #3335; mcp.deepwiki.com read tools). This leg does **not** import; it refreshes the public pages. Coordinate via main if the legs touch.
- Devin **organization** Wiki indexing (v3 API) = the provisioning leg (`docs/agentic/devin-wiki-access-reconciliation.md`); not this campaign.
- No undocumented endpoints, no credential material in issues/comments/files: names and states only.

## Wired vs waiting (prep state, 2026-11-01)

| Piece | State |
|---|---|
| Requirement + promotion record (§18) | ✅ wired |
| This prep (targets, flow, cadence, evidence format) | ✅ wired |
| Campaign issue with embedded session brief | ✅ wired |
| Evaluator pattern (Gemini, evidence-only) | ✅ wired (DoE pattern) |
| Builder execution | ⏳ waits on Jules arm recovery (probe completion) |
| Devin API automation | ⏳ waits on provisioning gate (leg 1) |
