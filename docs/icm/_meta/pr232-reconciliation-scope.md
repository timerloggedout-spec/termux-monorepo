# PR #232 Reconciliation Scope

## Operator decision

PR #232 remains the single integration vehicle for the repository-native ICM system and the directly related promotion-gate repairs required to make that work reviewable. The scope override allows focused workflow and application maintenance, but it does **not** authorize wholesale recovery of the divergent `master-staging` history.

## Classification

| Area | Decision | Basis |
|---|---|---|
| Repository gate / ICM reference Gitlinks | **Implement** | The PR adds shallow submodule Gitlinks. The gate read a Gitlink as a blob and crashed in CI; the repair preserves scanning of real files while correctly excluding mode `160000` entries. |
| Proposal-registry validation | **Implement** | `docs/proposals/active/user/` was an operator policy note, not a registered active proposal; it is reclassified outside the active-proposal tree. |
| Dependabot | **Implement** | The configuration used an invalid empty package ecosystem. It becomes a valid GitHub Actions monitor-only configuration with version-update pull requests limited to zero. |
| Devin peer review | **Retain; do not duplicate** | Current integration records Devin as a reviewer and peer reviewer; current peer-review orchestration already waits for Devin activity. No new secret, API, or Auto-Fix behavior is introduced. |
| DeepWiki / GitHub Wiki | **Retain; do not duplicate** | The tracked `wiki/` folder and `publish-wiki.yml` define the current mirror. A separate future change can improve publication only after confirming bootstrap state and desired public/private visibility. |
| Archived `master-staging` workflows and application code | **Defer by component** | The archive contains a broad divergent history. Importing it wholesale would override current-master ownership, include unrelated application changes, and evade focused validation. |
| Termux MCP / BLU B160V execution | **Out of scope** | No device transport, MCP access, or Android execution is required for the present promotion-gate fixes. |

## Current validation targets

1. `python3 scripts/ci/repo_gate.py --base origin/master` completes without dereferencing a Gitlink as a blob.
2. `python3 scripts/proposals/validate_registry.py` recognizes only genuine active proposals under `docs/proposals/active/`.
3. Dependabot accepts the tracked configuration as a valid `github-actions` entry.
4. Existing Devin and DeepWiki paths remain unchanged and attributable to their current owners.

## References

[1] [`master-rebuild-integration-evidence.md`](master-rebuild-integration-evidence.md) preserves the broader inherited material for later review.
[2] [GitHub Dependabot options reference](https://docs.github.com/code-security/reference/supply-chain-security/dependabot-options-reference) documents required configuration keys and valid package ecosystems.
