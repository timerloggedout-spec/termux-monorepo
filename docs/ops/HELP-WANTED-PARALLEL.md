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

## Delivery hierarchy (external) — DO NOT FLATTEN

| Priority | Mode | What happens |
|----------|------|----------------|
| **PRIMARY** | **upstream-pr** | Claim → branch on fork → **PR into the author's repo** |
| **FALLBACK** | **fork-offer** | Only if upstream PR is blocked / not allowed / failed |
| **PARALLEL NOTICE** | issue comment + commit URL | Optional **alongside** upstream-pr (or alone in fallback): points maintainers at our fork commit so they can pull / open their own PR |

**upstream-pr is the default and the goal.**

`fork-offer` is **not** a co-equal product mode. It is:

1. **Fallback** when we cannot open (or should not open) a PR on the target repo, **or**
2. **Parallel notice** — extra signal on the issue thread linking the commit, while the real delivery remains the upstream PR when possible.

Proven primary path: [vedantnimbarte/zero#81](https://github.com/vedantnimbarte/zero/pull/81).

## Rosters (parallel workers)

Display monikers are **not** live `@` pings (see `AGENT-MONIKERS.md`). Secrets stay in Actions.

| Slot | Display moniker | Identity / token surface | Parallel role |
|------|-----------------|--------------------------|---------------|
| 0 | `archW1z` | OPERATOR / Grok | Orchestration, dispatch, dual-gate |
| 1 | `l337S33k` | Full-scope operator PAT (intended) | High-privilege external write |
| 2 | `opsSweep` | GHA + OPERATOR_GITHUB_TOKEN | Claim + push + **upstream PR** |
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

Parallel external **write** capacity ≈ number of **distinct** fine-grained PATs with `issues:write` + `pull_requests:write` on public repos. Today effective write pool is **1–3** secrets; treat **safe concurrent external executes as 2–3** until more PATs are added to the roster.

## Parallel limits (defaults)

| Knob | Default | Why |
|------|---------|-----|
| Scout max issues / run | 25 | Search API + ranking cost |
| Concurrent execute jobs | **2** | Secondary rate limits + abuse optics |
| External **upstream PRs** / day / token | **3** | Politeness + abuse avoidance |
| Fallback fork-offers (when primary blocked) | as needed | Not a parallel quota target |
| Matrix max-parallel | 2 | When auto-batch lands |

## Parallel app shape (next product surface)

Not the 2017 React help-wanted UI. Our app:

1. **Catalog** — scout artifacts every 6h (JSON + future Vercel graphs).
2. **Roster board** — moniker slots, token health (len-only / last-success), daily budget remaining.
3. **Queue** — ranked issues → assigned moniker → **always try upstream-pr first**.
4. **Evidence** — claim URL, commit SHA, **upstream PR URL**, CPPH score → SHE / dashboard.
5. **Identity** — GitHub App installation tokens (ephemeral) preferred long-term; PATs bridge until then.

### Ephemeral tokens (preferred trajectory)

| Kind | Lifetime | Fit |
|------|----------|-----|
| GitHub App installation access token | ~1h | Per-job mint in Actions |
| Fine-grained PAT | long | Named roster slots |
| Classic PAT | long | Legacy; rotate; never commit |
| Codespace / device `gh auth` | session | Human / local implement |

Do **not** put tokens in issues, PR bodies, or moniker docs.

## Auto-batch (planned)

1. Read top-N from scout (N ≤ daily budget).
2. Matrix `max-parallel: 2`.
3. Each cell: claim → **upstream-pr** → on hard failure only, fallback fork-offer and/or parallel notice comment.
4. Ledger row for dashboard.

Until then: dispatch `help-wanted-execute` (proven primary: zero#72 → PR #81).

## BIUDL

Agent-Identity: Grok (Administrator) · moniker display `archW1z`
