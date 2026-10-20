# MSM-006 / MSM-007 implementation record

## Driver proposal: Q

Implement the user's prioritized free-provider research inside the existing model-selection-market package. MSM-006 ingests pinned public source metadata and proposes only research snapshot updates. MSM-007 computes offline advisory posteriors, signed-review summaries, observed transitions and dependency-aware Cadence plans. No production weights, provider eligibility, secrets, account balances, or merge authority are inferred from research or synthetic DSPy examples.

The workflow reuses the existing daily catalog completion event rather than adding another cron. Publication is restricted to one generated JSON path and explicitly requests the existing dual gates. The importer never executes upstream code or contacts imported endpoints. Full design and reproducible commands: [Provider research compounding](../../../ops/PROVIDER-RESEARCH-COMPOUNDING.md). Research sources and licensing: [provider brief](../../../ops/FREE-LLM-PROVIDER-RECON.md).

## Validation and disposition

Local module and workflow contract tests, repo-gate and termux-smoke are required. Live source ingestion is separate evidence from live inference, which is not part of this slice. Independent implementation review is requested before promotion. A green local test does not mean a deployed workflow or merged PR; remote run/commit evidence belongs in the implementation PR.

No proposal-wide acceptance or closure is claimed. Existing routing/promotion policy remains authoritative. Further provider adapters, causal DOE, DSPy optimization, authentic reviewer identity and real-outcome ingestion require separate scoped items and evidence.
