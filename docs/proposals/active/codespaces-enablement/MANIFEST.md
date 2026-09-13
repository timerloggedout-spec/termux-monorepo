# Proposal: codespaces-enablement

**id**: codespaces-enablement
**title**: Codespaces prebuilds (cost decision) + org-wide standard-piece gaps found by the gaps-and-opportunities sweep
**author**: gaps-and-opportunities investigation subagent
**status**: posted
**priority**: P2
**related_prs**: [499]
**related_branches**: [gaps-opps/add-devcontainer-codespaces]
**gates_required**: [repo-gate, termux-smoke]

## Summary

This is the first pass of a new standing "gaps and opportunities" investigation function for
the `timerloggedout-spec` org, sibling to the Agentic Ops (PR/security) and Agent Routing
Orchestrator rooms. It covers two things:

1. A concrete decision the owner needs to make (Codespaces prebuilds — costs money).
2. A set of evidence-backed, standard-but-missing pieces found across the three primary repos,
   proposed here rather than silently added.

The base Codespaces enablement (a working `.devcontainer/devcontainer.json` for
`termux-monorepo`) does NOT need this proposal — it is Tier 0 (new file, no cost, no owner
decision) and has already been opened directly as PR #499. Only the pieces below need an
Operator/owner call.

## Decision 1: Codespaces prebuilds — owner decision (cost)

**Evidence**: `termux-monorepo` has no devcontainer config at all today (verified via GitHub
Contents API — no `.devcontainer/` or root `devcontainer.json` in the default branch). PR #499
fixes the base case: Codespaces will boot into a matched Python/Node/Rust environment and run
`setup.sh`. That part is free and already proposed as code.

**What prebuilds would add**: GitHub can pre-build the devcontainer image on a schedule (e.g.
on every push to `master`, or nightly) so a new Codespace starts in seconds instead of running
`postCreateCommand` cold every time. For a monorepo this size (Python + Node + Rust toolchains,
~9k files at repo root alone) a cold `postCreateCommand` run is not instant.

**Cost**: Prebuild builds run on GitHub-hosted compute and are billed like any other Actions
minutes/storage on this plan; recurring prebuilds on a repo this size are a real, ongoing spend,
not a one-time cost. This is why it is **not** bundled into PR #499 — it is squarely an owner
cost/benefit call, not something an agent should decide unilaterally.

**Recommendation**: Land PR #499 first, use Codespaces for a few weeks without prebuilds, then
revisit — turn prebuilds on only if cold-start time actually proves painful in practice. Enabling
prebuilds later is a small settings change plus a `.devcontainer` prebuild workflow; not adding
it now costs nothing.

**Asking**: Operator/owner sign-off on whether to enable prebuilds now, defer, or skip entirely.

## Decision 2 (informational — not owner-gated, logged for traceability): standard-piece gaps

These were found while building the capability checklist (see `docs/gaps-and-opportunities/capability-checklist.md`
in this same branch). Listed here for the record; none of them need an Operator decision by
themselves — they are normal Tier 0-2 governance-doc/config gaps a follow-up PR can close. This
proposal does not resolve them; it surfaces them so they don't get silently invented and don't
get silently skipped either.

- **No `CODEOWNERS` file in any of the three primary repos.** Nobody is automatically requested
  for review on PRs.
- **`termux-mcp` and `android-mcp` have no `SECURITY.md`** (termux-monorepo has one).
- **`termux-mcp` and `android-mcp` have no Dependabot config** (`.github/dependabot.yml`) —
  dependency updates for their `package.json` stacks are fully manual today.
- **`termux-mcp` and `android-mcp` have no branch protection visible/queryable** with this
  token's scope (same "Resource not accessible by integration" as termux-monorepo — this may be
  an App-permission gap rather than an actual absence; needs an Operator with admin scope to
  confirm either way, since branch-protection changes are Tier 4 territory regardless).
  `allow_auto_merge` is `false` on both, vs. `true` on termux-monorepo.
  **Correction if wrong**: if these two repos in fact have protection configured through a path
  the API token can't see, disregard this line — it is reported as "unverifiable", not
  "confirmed absent".
- **No devcontainer/Codespaces config in `termux-mcp` or `android-mcp`.** Both are small
  Next.js/Vercel-style API services (single `package.json`, `api/`, `vercel.json`) — a
  devcontainer here would be a much smaller lift than the monorepo one, worth a quick follow-up
  PR once the monorepo one lands and the pattern is proven.
- **No `.agents/` governance-skill folder in `termux-mcp` or `android-mcp`** — these two repos
  currently have no pointer back to the org's consensus/permissions model at all. Given they're
  much smaller/simpler than the monorepo, a short `AGENTS.md` pointing at the monorepo's
  governance docs (rather than duplicating the whole `.agents/` tree) is probably the right-sized
  fix, not a full copy.

None of the above is invented to pad this report: `termux-monorepo` itself already has strong
coverage (dependabot, SECURITY.md, an extensive `.github/workflows` set, a full `.agents/`
governance tree, a real `docs/proposals/` process) — that is stated plainly in the checklist,
not glossed over.

## Recommendation on room structure

This first pass fit comfortably in one room. Recommending to the owner: keep "gaps and
opportunities" as a single standing room for now (periodic org-wide scans + checklist upkeep +
proposal drafting), rather than spinning up a dedicated room per gap category. Split it out only
if/when a single category (e.g. "Codespaces rollout across all repos", or "CODEOWNERS +
governance-doc rollout to satellite repos") turns into multi-step execution work with its own
back-and-forth — at that point it earns its own room the same way Agentic Ops and Agent Routing
Orchestrator did.

## Review log

- posted by gaps-and-opportunities subagent, 2026-09-12 — initial findings, PR #499 opened
  separately for the no-cost devcontainer base case; this proposal covers the cost-bearing
  prebuild decision plus the informational gap list above.