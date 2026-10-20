# Help-Wanted Lane — INTENDED PURPOSE

**Status:** LIVE · **with Tribute** (contributor project)  
**One sentence:** Scan FOSS help-wanted → rank → claim once → open **upstream PR** (tribute to maintainer) → follow feedback → ledger on `/help-wanted/`.

See **`HELP-WANTED-TRIBUTE.md`** for the contributor ledger contract.

## Pipeline (complete)

```text
scout (2h)       CPPH rank
execute (4h)     claim → PRIMARY upstream PR (FALLBACK notice if blocked)
followup (2h)    CHANGES_REQUESTED on foreign PRs only
llm-assist       live catalog (OR|Felo|Omni) patch plans
rerequest        re-request review after revise
status-refresh   evidence + tributes → status.json
dashboard        https://timerloggedout-spec.github.io/help-wanted/
```

| Workflow | Role |
|----------|------|
| `help-wanted-scout` | Rank |
| `help-wanted-execute` | Claim + upstream PR |
| `help-wanted-followup` | Foreign CHANGES_REQUESTED poll |
| `help-wanted-llm-assist` | Live-catalog model plan on foreign PR |
| `help-wanted-rerequest` | Re-request reviews |
| `help-wanted-status-refresh` | Board + tributes + dashboard data |
| `help-wanted-dashboard-deploy` | Pages / CDN |

## Working with others

Claim once · skip closed · PRIMARY upstream · no stake `Fixes #` · foreign-only followup.

## Tokens

`OPERATOR_GITHUB_TOKEN` → `OPERATOR_TOKEN` → `ARCHWIZ_GITHUB_TOKEN` → `GITHUB_TOKEN`  
LLM assist: `OPENROUTER_API_KEY` / `FELO_AI_API` / `OMNI_*` (by name in Actions).

Agent-Identity: Grok (Administrator)

## Help-Given Tribute graduation gate

The lane now distinguishes the stake/claim event from a delivered fix. Use docs/ops/HELP-GIVEN-TRIBUTE.md and scripts/ci/help_wanted_diff_gate.py for the canonical state machine and diff-proof gate.

A stake PR is a legitimate tribute event but never solution credit. A solution requires a non-placeholder repository delta plus explicit Help-Given Tribute / Stage: solution / Diff proof: / Validation: evidence in the PR body.

Destination: fixes discovered by this lane are delivered as upstream Help-Given Tributes to the foreign maintainer's repository; the monorepo records the transaction and evidence.


## Sweep accountability

This lane is governed by `docs/ops/SWEEP-ACCOUNTABILITY.md`. Every historical/future observation or action is recorded as an append-only sweep receipt with version/iteration lineage, findings, actions, effects, provenance, source SHAs, and continuation cursor. Lane receipts remain source evidence; sweep receipts do not replace them.
