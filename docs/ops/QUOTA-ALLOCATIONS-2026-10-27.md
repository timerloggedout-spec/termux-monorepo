# Focused Quota Allocations (2026-10-27, issue #1884)

Implements the owner's allocation model: quota is allocatable to
specific focuses as percentages of named pools, dynamically, reviewed
on cadence. Owner lane: quota readings & convergence.

## Model

- **Pool** = a named quota source: a provider's registry services
  (`ops/quota/registry.json`), a provider free tier, or a credit balance
  (credit records — `aws.account_credits` $200, `azure.account_credit`
  $200, `digitalocean.trial_credit` $200, `netlify.credits`,
  `felo.api_credits`, `partners.credits` — are their own pools; amounts
  are the registry-documented / owner-supplied entitlement figures,
  joined from the registry at feed build, never invented).
- **Focus** = winning (challenge entries), repo-development,
  boinc-donations, research.
- **Allocation** = pool × focus × % + mode, as data:
  `ops/quota/allocations.json` (schema `quota-allocations/v1`) is the
  single source lanes read. Modes: `standing` (a real split),
  `leftover-only` (draws only what higher-priority focuses cannot
  consume before expiry; pct 0), `none`. Per pool, standing allocations
  sum to ≤ 100%; the remainder is **explicit reserve**, computed and
  published in the feed.

Coverage: 50 pools, 88 of 89 registry services pooled;
`openrouter.key` is explicitly excluded (opt-in private observation
record, not a consumable service).

## Owner setting (2026-10-27, until reset)

**Winning ≈ 100%** on the active challenge slate (D1/D3/D2/D4): every
non-excluded pool stands at winning 100 / reserve 0. Repo-development
and research are `leftover-only` everywhere. BOINC composes with its
standing rule: `leftover-only` on GitHub-provider pools only, `none`
elsewhere — stranded leftover, never displacing. One exception pool:
**`github.codespaces` is excluded-interim** (owner, 2026-10-27, after
the setup-error burn) — all allocations 0 / `none`, reserve 100, until
the owner resets it.

Guardrails are config constraints, recorded in the file: card rule,
free-only, no displacement of the top focus, BOINC eligibility,
per-pool ≤ 100%.

## Feed + Gantt

`scripts/quota_allocations.py` (validate | feed | gantt):

- **Feed**: `apps/help-wanted-dashboard/data/quota-allocations-feed.json`
  (schema `quota-allocations-feed/v1`) — per pool: registry entitlement,
  allocations, explicit `reserve_pct`, observed readings per service
  (from the public readings snapshot; readings discipline unchanged),
  the #1880 countdown entries, and the Gantt rows. MoneyBall and the
  quota dashboard consume this file for explained focus scoring.
  **Observed consumption by focus is `null`**: readings observe
  services, not focuses, and no attribution is invented.
- **Gantt**: plan-vs-actual rows per pool × focus (plus reserve) ride in
  the feed's `gantt` block for the existing Gantt adapters
  (`scripts/agentic/gantt_projection.py`; Gantt-as-workflow in the
  Temporal RFP), alongside the #1880 countdowns. Plan window = owner
  setting date → latest countdown close (D4, 2026-12-04). Actual % per
  focus is `null` until a focus-attributed read exists. A mermaid
  rendering is available via `quota_allocations.py gantt`.

## Cadence

Re-splits happen at cadence ticks (dispatch-tree cadence / weekly
sweep). Every change is a PR that (a) edits only
`ops/quota/allocations.json` (+ regenerates the feed), (b) cites #1884
and the reason in each changed allocation row (`date` + `reason` are
required fields, validator-enforced), and (c) keeps
`tests/test_quota_allocations.py` green — it validates the live config
against the live registry on every run, pins the owner setting, the
BOINC eligibility rule and the Codespaces exclusion.
