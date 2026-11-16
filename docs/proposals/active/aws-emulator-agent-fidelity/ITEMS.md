# ITEMS — aws-emulator-agent-fidelity

| ID | Item | State | Evidence / exit condition |
|---|---|---|---|
| AEF-001 | Reconcile AWS Emulator research against existing Termux architecture | done | RFP architecture and reuse map cite existing control-plane, evidence, and AWS proposal owners |
| AEF-002 | Publish complete source register and transferability notes | done | SOURCES.md contains all 25 supplied references, classified by role |
| AEF-003 | Define fidelity-first agent-team architecture and priority order | done | RFP.md and AWS-EMULATOR-AGENT-FIDELITY.mmd |
| AEF-004 | Add fail-closed, runtime-disabled integration contract | done | integrations/aws-emulator/contract.json |
| AEF-005 | Add offline contract validator and regression tests | done | scripts/ci/verify_aws_emulator_contract.py; 10 focused unittest cases passed locally |
| AEF-006 | Wire focused validator/tests into canonical repo-gate | posted | Requires owner-path review; do not duplicate an existing AWS/emulator test gate |
| AEF-007 | Verify host compatibility and run a pinned emulator smoke test | blocked | Requires supported Linux x86_64/aarch64 host, sufficient disk, pinned release, and actual runtime receipt |
| AEF-008 | Build AWS SDK integration/fidelity cohort for selected services | posted | Reuse official evaluation suite; define service shortlist from real repo dependencies and fidelity evidence |
| AEF-009 | Compare emulator and LocalStack for the same cohort | posted | Same fixtures, SDK versions, host, timeout, policy, and cost/maintenance rubric |
| AEF-010 | Add model-driven gap discovery and one-issue fix loop | posted | Reuse QUE/QDesk and issue workflow; independent reviewer and merge gate required |
| AEF-011 | Conduct adversarial security and real-cloud parity review | blocked | Explicit approval, isolated sandbox accounts, no production credentials, teardown and budget limits |
| AEF-012 | Record runtime, quality, and manager outcomes in canonical evidence plane | posted | Reuse existing SHE/JSONL/ATES/3L0; no second ledger |

State semantics: `done` means the repository artifact exists and its stated check was performed; `posted` means proposed work not yet validated; `blocked` means a prerequisite or authorization is missing.
