# Plan — master-staging reconciliation

## Goal

Extract valid staging-only work onto current `master` while keeping Termux runtime validation scoped to Termux work.

## Baseline

- Master: `63a59d105b3584e6fbd1b2bc9e659e22fdaf10de`
- Master-staging: `23026f13d7ad08ac7703cef0639fd76efa874fe1`
- Merge base: `c3ea1e1c24a03b1b199e6c36521f4be9b367c733`
- Master-staging: 56 commits ahead and 31,715 behind master
- Open PRs targeting master-staging: 7
- Termux-smoke branch: `521fa1a026ea60f92f35c7831816b407352a5018`

## Work sequence

1. Inventory branches, merge bases, staging-only commits, open PRs, and Termux-only work.
2. Preserve source refs and classify each workstream.
3. Correct the scope-aware validation contract and remove unrelated tests from Termux smoke.
4. Add a dedicated bucket-headroom contract workflow.
5. Update SHE verification and promotion planners to require the repository gate universally and Termux smoke conditionally.
6. Update governance documentation and proposal templates.
7. Run focused tests and the repository gate through Actions.
8. Re-fetch the candidate SHA, jobs, steps, and artifacts.
9. Extract remaining staging workstreams in small, independent PRs.

## Guardrails

- Preserve branch history and source refs.
- Keep the staging branch intact during extraction.
- Use current master as the base for each new integration branch.
- Keep each workstream within its proposal item.
- Bind validation evidence to the exact candidate SHA.
