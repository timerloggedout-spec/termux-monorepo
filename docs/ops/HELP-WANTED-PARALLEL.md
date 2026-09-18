# Help-Wanted Parallel Capacity (SSOT)

**Status:** live after #609 + OPERATOR execute success (zero#81).
**Companion:** `HELP-WANTED-LANE.md` · `AGENT-MONIKERS.md` · skill `help-wanted-lane`.

## How often it runs today

| Workflow | Trigger | Cadence |
|----------|---------|--------|
| `help-wanted-scout.yml` | `schedule` + dispatch | **Every 6 hours** (`cron: 27 */6 * * *`) |
| `help-wanted-execute.yml` | **dispatch only** | On demand (no auto-spray) |
| Continuous agent ops | hourly | Unrelated monorepo PR sweep (`17 * * * *`, max 8 PRs/run) |

Scout ranks. Execute does not auto-fire top-N yet — intentional until daily caps + matrix are proven.

## Delivery modes (external)

| Mode | What happens | When to use |
|------|----------------|-------------|
| **upstream-pr** (default) | Claim → fork branch → PR to **author's** repo | Maintainer accepts external PRs |
| **fork-offer** | Claim → commit on **our** fork only → issue comment with **commit URL** (they cherry-pick / open PR themselves) | Upstream blocks external PRs, wants internal PR, or rate-limit / politeness |

Fork-offer is the workaround you named: contribution visible on our fork; upstream gets a clean pointer, zero merge pressure from us.

## Rosters (parallel workers)

Display monikers are **not** live `@` pings (see `AGENT-MONIKERS.md`). Secrets stay in Actions.

| Slot | Display moniker | Identity / token surface | Parallel role |
|------|-----------------|--------------------------|---------------|
| 0 | `archW1z` | OPERATOR / Grok | Orchestration, dispatch, dual-gate |
| 1 | `l337S33k` | Full-scope operator PAT (intended) | High-privilege external write |
| 2 | `opsSweep` | GHA + OPERATOR_GITHUB_TOKEN | Claim + push + PR create |
| 3 | `heyVern` | `@jules` (live) | Implement hard issues after claim |
| 4 | `sparkFlux` | `@gemini-cli` | Optional alternate implementer |
| 5 | `deepCore` | DeepSeek CI | Review external PR diffs |
| 6 | `codeHound` | CodeRabbit | Review |
| 7 | `peerGate` | GHA peer orch | Contract / state only |

**Token pool (Actions secrets, never logged):**

1. `OPERATOR_GITHUB_TOKEN`
2. `OPERATOR_TOKEN`
3. `ARCHWIZ_GITHUB_TOKEN`
4. `GITHUB_TOKEN` (repo-scoped only — **cannot** claim third-party issues)

Parallel external **write** capacity ≈ number of **distinct** fine-grained PATs with `issues:write` + `pull_requests:write` on public repos (or classic scopes). Today effective write pool is **1–3** secrets; treat **safe concurrent external executes as 2–3** until more PATs are added to the roster.

## Parallel limits (defaults)

| Knob | Default | Why |
|------|---------|-----|
| Scout max issues / run | 25 | Search API + ranking cost |
| Concurrent execute jobs | **2** | Secondary rate limits + abuse optics |
| External PRs / day / token | **3** | Politeness + abuse avoidance |
| Concurrent fork-offers | **5** | Comment-only is lighter |
| Matrix max-parallel | 2 | `strategy.max-parallel` when auto-batch lands |

GitHub secondary rate limits (~100 concurrent requests / user, abuse detection on mass issue comments) dominate long before Actions runner count does.

## Parallel app shape (next product surface)

Not the 2017 React help-wanted UI. Our app:

1. **Catalog** — scout artifacts every 6h (JSON + future Vercel graphs).
2. **Roster board** — moniker slots, token health (len-only / last-success), daily budget remaining.
3. **Queue** — ranked issues → assigned moniker → mode `upstream-pr` | `fork-offer`.
4. **Evidence** — claim URL, commit SHA, PR URL, CPPH score → SHE / dashboard.
5. **Identity** — GitHub App installation tokens (ephemeral, repo-scoped) preferred long-term over long-lived PATs; PATs remain bridge until App + fine-grained roster is complete.

### Ephemeral tokens (preferred trajectory)

| Kind | Lifetime | Fit |
|------|----------|-----|
| GitHub App installation access token | ~1h | Per-job mint in Actions; least standing privilege |
| Fine-grained PAT | long | Named roster slots (`l337S33k`, etc.) |
| Classic PAT | long | Legacy; rotate; never commit |
| Codespace / device `gh auth` | session | Human / local implement |

Do **not** put tokens in issues, PR bodies, or moniker docs. See `CREDENTIAL-EXPOSURE.md` + transport ADR.

## Auto-batch (planned)

When scout artifact lands:

1. Read top-N (N ≤ daily budget).
2. Matrix job per issue with `max-parallel: 2`.
3. Each cell: claim → mode decision → patch or fork-offer comment.
4. Write ledger row for dashboard.

Until then: **manual / agent dispatch** of `help-wanted-execute` (proven on zero#72 → PR #81).

## BIUDL

Agent-Identity: Grok (Administrator) · moniker display `archW1z`
