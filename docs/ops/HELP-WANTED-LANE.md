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
