---
name: local-action-verification
description: Verify targeted GitHub Actions jobs locally with act and preserve exact-head evidence for builders and reviewers.
---

# Local Action Verification — DoE Builder and Reviewer Adaptation

## Source lineage

- Upstream fork: timerloggedout-spec/jules-skills_fork
- Source revision: 7a76d3bfcf4258ee437d65b5d12e54b51c395de5
- Upstream skill: local-action-verification
- License: Apache-2.0

This local adaptation makes act verification available to any admitted builder or reviewer. The hosted Google Jules runtime is retired; the verification capability is provider-neutral.

## Role bindings

- **builder:** run targeted local checks before handing off a candidate branch.
- **reviewer:** reproduce relevant workflow jobs against the exact candidate head.
- **steward:** preserve command, commit SHA, result, and log location in the task receipt.

## Verification sequence

1. Capture the candidate commit with git rev-parse HEAD and record the working-tree status.
2. Inspect .github/workflows/ and identify the workflow file, event, and job ID that cover the changed files.
3. Check act --version and Docker availability. Use an approved local runtime when both prerequisites are available.
4. Run the targeted job:
   - act -W .github/workflows/<workflow>.yml -j <JOB_ID>
   - For a matrix job, add the supported --matrix KEY:VALUE arguments.
   - For a workflow requiring secrets, use an approved secret file stored outside the repository and pass --secret-file <path>.
5. Preserve logs and the exact command in the task evidence directory.
6. Compare the worktree status after the run and preserve pre-existing user changes.
7. Run the authoritative GitHub Actions checks against the exact candidate head before acceptance.

## Evidence receipt

Record:
- candidate commit SHA;
- workflow path and job ID;
- act version and runtime availability;
- exact command and relevant environment configuration;
- pass/fail result and log location;
- authoritative GitHub Actions run URL and exact-head conclusion.

## Acceptance boundary

Local act output provides fast feedback. Repository GitHub Actions checks remain the acceptance authority for the exact candidate head. A local pass contributes evidence; a hosted CI result completes the validation record.
