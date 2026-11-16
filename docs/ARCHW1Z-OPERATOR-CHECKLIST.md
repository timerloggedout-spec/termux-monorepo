# Operator Checklist — Full Agentic Mode

You only need to complete items marked **HUMAN**. Everything else is agent-owned.

## One-time setup (HUMAN)

- [ ] **GitHub App permissions** on `timerloggedout-spec/termux-monorepo`:
  - [ ] Contents: Read and write
  - [ ] Pull requests: Read and write
  - [ ] Checks + Commit statuses: Read and write
  - [ ] Issues: Read and write
  - [ ] Workflows: Read and write
  - [ ] Administration: Read
- [ ] **Branch protection on `master`**: require `repo gate` + `termux smoke` checks; allow the App to merge when green
- [ ] **`master-staging`**: leave soft/unprotected so agents iterate
- [ ] **ChatGPT GitHub App** (optional): same permissions if ChatGPT should execute too

## Security (HUMAN + agent)

- [ ] **HUMAN:** Rotate credentials that appeared in tracked session/browser material
- [ ] Agent: verify tips clean via `repo_gate.py`
- [ ] **HUMAN:** Authorize history-rewrite window (comment on #3)
- [ ] Agent: execute rewrite under that authorization

## Ongoing (agent default)

- [x] repo-gate live
- [x] termux-smoke live
- [x] Proposal registry + PROCESS + CONSENSUS
- [x] Docs promotion branch to master
