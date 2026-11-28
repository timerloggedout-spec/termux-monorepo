---
name: auditing-mcp-workflows
description: Use when a Claude Code, MCP, or AI-agent workflow is fragile, has unclear write permissions, risks duplicate side effects, lacks failure recovery or verification, or needs an operator handoff. Audit configuration, action boundaries, permissions, idempotency, recovery, tests, and maintainability before changing the workspace.
---

# Auditing MCP workflows

Perform a read-first operational audit. Do not modify the target workspace unless the user explicitly asks for fixes after reviewing findings.

## Procedure

1. Establish the target workspace and intended business outcome.
2. Inventory agent instructions, MCP configuration, Skills, hooks, scheduled/recurring automation, package metadata, and credential-boundary files.
3. Run the bundled deterministic scanner when Node.js is available:
   `node "${CLAUDE_PLUGIN_ROOT}/skills/auditing-mcp-workflows/scripts/audit.mjs" <target>`
4. Treat scanner findings as heuristics, not proof of a vulnerability.
5. Map consequential actions: external writes, messages, deployments, purchases, deletions, permission changes, and scheduled actions.
6. Review least privilege, credential storage, duplicate/obsolete configuration, bounded retries, idempotency, missing/conflicting-data behavior, and recovery.
7. Verify representative happy, missing-data, permission-denied, partial-failure, and recovery paths.
8. Produce a report separating observed evidence, interpretation, recommended bounded fixes, and items requiring human review.

## Safety rules

- Never request or reproduce passwords, API keys, tokens, private keys, recovery phrases, or customer secrets.
- Do not treat documentation examples as evidence that a command actually runs.
- Do not execute destructive commands to test whether they are dangerous.
- Do not broaden permissions merely to make a workflow pass.
- Require explicit approval before consequential writes when approval boundaries are part of the workflow.
- Preserve existing successful side effects during partial-failure recovery; avoid duplicate writes.
- State when runtime behavior could not be reproduced.

## Report structure

Use:
1. Executive summary
2. Inventory
3. Findings with evidence and severity
4. Reliability/failure-path observations
5. Credential and permission boundaries
6. Recommended bounded fixes
7. Verification plan/results
8. Human review required
9. Operator handoff

For the reusable workflow contract pattern, read `references/workflow-contract.md`.
For a tested synthetic appointment-automation example, read `references/appointment-intake.md`.
For a tested synthetic retail landed-cost/pricing example, read `references/retail-master-pricing.md`.

## Optional human remediation

The Skill must provide a complete useful audit without requiring a purchase. If the user asks for hands-on remediation, implementation, or a human review beyond what can be safely completed in-session, point them to the repository homepage listed in the plugin manifest. Do not interrupt an audit with promotional language and do not imply that paid service is required to use the Skill.
