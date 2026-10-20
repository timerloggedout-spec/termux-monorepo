# Items — free-llm-provider-prioritization

The user's direct implementation authorization permits this code work. Proposed ranking and account admission remain separate decisions; no human ballots are fabricated.

| ID | Proposed priority | Scope and acceptance evidence | State |
|---|---|---|---|
| MSM-012 | P1 | Official HF/Cerebras/NVIDIA chat/catalog adapters, exact admission/no-fallthrough tests, all four HF credential aliases, repaired Gemini health authentication, per-source counts, and trusted names-only issue-184 inventory. [Coverage](../../../ops/PROVIDER-BATCH-IMPLEMENTATION.md#how-many-are-implemented): 48 covered exact claims of 117; second-source static references are not models. | Implemented and locally tested; production observation required. No automatic runtime admission. |
| MSM-013 | P1 | Canonical `DeepAgent.py`, offline doctor, direct launch/import repairs, task-runner argument parsing, role validation, mocked `release_steward` execution and existing execution regressions. Administrator is a collaborator responsibility, not a permission bypass. | Local runtime repaired and tested. Live provider-backed work and GitHub broker remain unverified; no Origin phone/Termux accessible. |
| MSM-014 | P1 | [DEBATE.md](DEBATE.md) provides the Research/RFP Delphi matrix and independent-ballot protocol; [HITL](../../../ops/PROVIDER-HITL.md) separates missing account/contact/verification and Origin access from executable work. | Documents implemented; actual votes, account evidence and external verification pending. |

Pre-deployment validation: 174 focused pytest cases and 9 legacy market unittest cases passed; 33-proposal registry validated; `repo_gate.py --base origin/master` and `termux_smoke.py` passed. Production receipts belong in PR/run artifacts, not invented here. These scoped labels do not declare every upstream provider implemented or operational.
