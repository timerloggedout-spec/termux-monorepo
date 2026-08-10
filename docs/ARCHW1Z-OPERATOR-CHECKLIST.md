# Operator Checklist — Full Agentic Mode

You only need to complete items marked **HUMAN**. Everything else is agent-owned.

## One-time setup (HUMAN)

- [ ] **GitHub App permissions** on `timerloggedout-spec/termux-monorepo`:
  - [ ] Contents: Read and write
  - [ ] Pull requests: Read and write
  - [ ] Checks + Commit statuses: Read and write
  - [ ] Issues: Read and write
  - [ ] Workflows: Read and write (for maintaining gates)
  - [ ] Administration: Read (Write only if agent may edit branch protection)
- [ ] **Branch protection on `master`**: require `repo gate` + `termux smoke` checks; allow the App to merge when green
- [ ] **`master-staging`**: leave soft/unprotected so agents iterate
- [ ] **ChatGPT GitHub App** (optional): same permissions if ChatGPT should execute too
- [ ] **Connect Linear** (optional): write access for TER issue sync

## Security (HUMAN + agent)

- [ ] **HUMAN:** Rotate any credentials that appeared in tracked session/browser material
- [ ] Agent: verify tips clean via `repo_gate.py`
- [ ] **HUMAN:** Authorize history-rewrite window (comment on #3 or a tracking issue)
- [ ] Agent: execute rewrite + coordinate PR retargets under that authorization

## Ongoing (agent default)

- [x] repo-gate live
- [x] termux-smoke live
- [x] Proposal registry + PROCESS
- [x] Disposition comments on open PRs
- [x] #10 retargeted to master-staging
- [ ] Merge #10 when checks green
- [ ] #9 launcher fixes + retarget
- [ ] #5 decouple then merge
- [ ] #2/#6 remain NO-GO until itemized extractions

## Verify agentic loop

```bash
# On device or CI
python3 scripts/ci/repo_gate.py
python3 scripts/ci/termux_smoke.py --with-optional

# Agents read
cat docs/proposals/registry.yaml
```

When the **One-time setup** boxes are checked, you should not need to touch the repo for ordinary proposal execution.
