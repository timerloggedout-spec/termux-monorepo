# Enterprise organization preservation — work items

**Proposal:** enterprise-org-preservation  
**Source:** `search-astute-ly`  
**Enterprise:** `AdAstraNeoNexus`  
**Proposed destination:** `AsAstraNeoNexus` (GitHub Free)

| ID | Work item | Acceptance evidence | State |
|---|---|---|---|
| ENT-PRES-001 | Reconstruct the deletion notice and affected organization. | GitHub Support email identifies Enterprise `AdAstraNeoNexus`, organization `search-astute-ly`, deadline 2026-12-03. | Implemented |
| ENT-PRES-002 | Inventory organization repositories and compare duplicate monorepo snapshots. | Three repositories identified; two snapshots share HEAD `6567e175ef1b1abe808fb76ca333d2f6ceeaccd8`; canonical source is 29,833 commits ahead in the compare response. | Implemented |
| ENT-PRES-003 | Capture a metadata-only pre-migration baseline. | Manual Actions run publishes `enterprise-org-state.json`; secret values and webhook URLs stay outside the artifact. | Implemented — awaiting run |
| ENT-PRES-004 | Determine whether GitHub permits direct organization removal from the expired Enterprise trial. | Enterprise Organizations settings show the available owner operation and its warnings. | Blocked — owner UI |
| ENT-PRES-005 | Establish an independent GitHub Free destination if repository transfer is required. | `AsAstraNeoNexus` exists under the personal account, reports plan `free`, and grants the operator owner access. | Pending — owner UI |
| ENT-PRES-006 | Transfer every source repository to the Free destination. | Dry-run/apply workflow verifies destination Free plan, collisions, repository IDs, source emptiness, and post-transfer inventory. | Implemented — awaiting destination and run |
| ENT-PRES-007 | Reconcile organization-level resources. | Baseline records secret/variable names, webhooks, and app installations; teams, members, projects, and packages are explicit manual follow-ups. | Partially implemented |
| ENT-PRES-008 | Verify destination Free-plan compliance and repository integrity. | Free plan, public/private visibility review, repository IDs, branches, tags, releases, workflows, settings, and integrations reconcile. | Pending |
| ENT-PRES-009 | Record final state and close the migration. | Final receipts, remaining risks, and source-account cleanup status are documented before 2026-12-03. | Pending |


| ENT-PRES-010 | Publish a reusable Enterprise organization preservation skill. | Skill documents eligibility, baseline, direct removal, Free destination, dry-run/apply transfer, resource reconciliation, and WAIT/WATCH evidence. | Implemented |

## Execution order

1. Merge the baseline and verification automation after repository gates pass.
2. Run `phase=baseline` for `search-astute-ly`; retain the Actions run ID.
3. Inspect Enterprise → Organizations and record the available removal operation.
4. If direct removal is available, execute it and verify the same organization on Free.
5. If direct removal is unavailable, create `AsAstraNeoNexus` through personal-account organization settings and select GitHub Free.
6. Run transfer workflow in `dry_run`; review the exact repository list and destination.
7. Run transfer workflow in `apply` with the exact confirmation string.
8. Recreate organization-level resources and validate the destination.
9. Retain the final receipt and finish before the deletion date.
