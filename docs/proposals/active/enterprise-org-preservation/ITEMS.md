# Enterprise organization preservation — work items

**Proposal:** enterprise-org-preservation  
**Target:** detach `search-astute-ly` from Enterprise `AdAstraNeoNexus` and retain it on GitHub Free.

| ID | Work item | Acceptance evidence | State |
|---|---|---|---|
| ENT-PRES-001 | Reconstruct the deletion notice and affected organization. | GitHub Support email identifies Enterprise `AdAstraNeoNexus`, organization `search-astute-ly`, deadline 2026-12-03. | Implemented |
| ENT-PRES-002 | Inventory organization repositories and compare the duplicate monorepo snapshots with the canonical source. | Three repositories identified; two snapshots share HEAD `6567e175ef1b1abe808fb76ca333d2f6ceeaccd8`; canonical source is 29,833 commits ahead in the compare response. | Implemented |
| ENT-PRES-003 | Capture a metadata-only pre-detachment baseline. | Manual Actions run publishes `enterprise-org-state.json`; secret values and webhook URLs stay outside the artifact. | Ready |
| ENT-PRES-004 | Remove `search-astute-ly` from the Enterprise account using the owner settings operation. | Enterprise Organizations view no longer lists the organization; organization stands alone. | Blocked — owner UI |
| ENT-PRES-005 | Verify Free plan and reconcile preserved assets against the baseline. | Verification workflow reports Free plan and zero missing baseline assets. | Pending |
| ENT-PRES-006 | Reconcile integrations and record the final state. | Actions secrets/variables names, webhooks, app installations, Pages flags, branches, tags, releases, and workflow identities are recorded. | Pending |
| ENT-PRES-007 | Decide whether a separate `AsAstraNeoNexus` organization is useful. | Separate owner decision after `search-astute-ly` preservation; new organization creation is outside the required preservation path. | Deferred |

## Execution order

1. Merge the verifier workflow after repository gates pass.
2. Run `phase=baseline` for `search-astute-ly`; retain the run ID.
3. In Enterprise settings, remove `search-astute-ly` from `AdAstraNeoNexus`.
4. Run `phase=verify` and provide the baseline run ID.
5. Resolve every missing or unverified inventory item.
6. Record the resulting Free-plan state and close the proposal.
