# ITEMS — aws-free-tier-strands-delphi-oracle

| ID | Item | State | Evidence / exit condition |
|---|---|---|---|
| AWS-ORACLE-001 | Publish siloed RFP and cost/security gates | done | RFP.md committed on proposal branch |
| AWS-ORACLE-002 | Define ten falsifiable concept experiments | done | EXPERIMENT-MATRIX.md; hypotheses only, no runs claimed |
| AWS-ORACLE-003 | Define telemetry-acquired Delphi collection contract | in_review | DEBATE.md source classes, normalized envelope, and workflow states |
| AWS-ORACLE-004 | Obtain independent collaborator review | posted | Reviewer request and actual review receipt required |
| AWS-ORACLE-005 | Build local deterministic baseline and fixture corpus | in_review | `scripts/delphi/strands_oracle_mvp.py`, frozen `tests/fixtures/delphi_oracle_mvp.json`, contract tests, and CI receipt; require green exact-SHA CI before done |
| AWS-ORACLE-006 | Verify provider-batch/telemetry reuse and run independent model panel | blocked | Existing Delphi gate has model voting disabled (`DELPHI_LLM_MAX=0`); inspect and validate provider-batch reuse before dispatch; completed provider receipts required |
| AWS-ORACLE-007 | Approve account readiness and minimum AWS deployment | blocked | Explicit owner approval, eligibility check, budget controls, IAM plan, teardown |
| AWS-ORACLE-008 | Validate proposal lifecycle and repository gates | done | PR #1611 merge receipt and proposal-lifecycle/repo-gate/Termux smoke results were recorded; rerun on any changed implementation head |
