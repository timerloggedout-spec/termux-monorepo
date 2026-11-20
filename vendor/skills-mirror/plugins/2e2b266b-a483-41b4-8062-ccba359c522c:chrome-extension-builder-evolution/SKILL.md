---
name: chrome-extension-builder-evolution
description: Improve Chrome extension UI and architecture with bounded candidate generation, independent evaluation, hard safety gates, weighted tradeoffs, selection, and regression checks.
---

# Chrome Extension Builder: Evolution

Before starting, read [shared policy boundaries](../chrome-extension-builder/references/policy-boundaries.md). Follow host safeguards, task-scoped inputs, synthetic fixtures, and the no-secrets/no-restricted-data boundary. Local tools and persistence are optional: check explicit environment access first; otherwise deliver the same role's useful sanitized findings, specification, code, or test plan in normal Markdown and mark execution unrun.

Interpret genetic/evolutionary improvement as transparent generate → evaluate → select → refine. This is bounded engineering, not globally optimal architecture or autonomous permission expansion. Read [candidate-evaluation.md](../chrome-extension-builder/references/candidate-evaluation.md).

1. Define target, baseline, candidate budget (default 3 candidates, maximum 3 rounds), stop criteria, and weights before evaluation. User constraints override defaults.
2. Generate materially different candidates for one decision: UX/context/framework/data boundary/performance strategy. Respect approved constraints. Keep review artifacts separate; do not overwrite the incumbent while comparing.
3. Reject unresolved critical/high security, covert transfers, leaked secrets, remote executable code, deceptive UI, inaccessible core flow, broken acceptance, unauthorized costs/actions, and unsupported feasibility. Hard gates precede scores.
4. Evaluate task completion, clarity/accessibility, privacy/permission burden, resilience, latency/resources, maintainability, and cost using evidence. Mark measurements, judgments, and unknowns. Material unknown gates block release-ready selection.
5. Use independent evaluation when available/authorized; otherwise perform a separate critique and disclose lack of independence. Use one rubric, explain tradeoffs, select the simplest contract-satisfying candidate. Keep incumbent on ties/unsupported improvement.
6. Refine winning weaknesses without changing safety boundaries; rerun affected behavior/security/browser checks. Stop on acceptance, measured plateau, budget exhaustion, or a material user decision. Never loop indefinitely.

Deliver `docs/candidates.md`: baseline/candidates/gates/evidence/scores, selected rationale, rejected tradeoffs, rounds, and regression result. Exit with implemented winner or concrete recommendation and decision gate; simulated scores are not production proof.

## Context and outcome handoff

Generate alternatives for this actual project from relevant [recipes/defaults](../chrome-extension-builder/references/task-recipes.md), not generic simulated candidates. Freeze acceptance and rubric before scoring; keep weights unchanged across rounds. Use actual evidence and reviewed feedback; ties retain incumbent, no self-training/global optimality claims. Preserve the canonical report destination assigned by `references/team.json`; any overview is a dated view, not a competing authority.
