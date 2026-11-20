---
description: Improve a Chrome extension using a measured, independent, bounded candidate-selection loop.
argument-hint:
- extension project path and improvement goal
---

Improve the extension for: $ARGUMENTS

Read `chrome-extension-builder-evolution` and the relevant specialist skill(s). Inspect the current build and reproduce the user's issue or measure the desired improvement. Freeze acceptance criteria and baseline evidence before generating alternatives. For a bug, start with a failing behavior test; for visual polish, preserve established direction and define user-journey/accessibility criteria.

Use the `independent-evaluator` role and skills/chrome-extension-builder/references/team.json scoring weights. Generate at most three useful candidates per round and run at most three rounds total, changing only owned files. Candidates may be design/architecture alternatives before implementation or isolated implementation revisions, not three concurrent writers in the same file. Reject hard security/privacy/policy/runtime/package blockers regardless of average score.

Measure and compare task success, security/privacy, usability/accessibility, lifecycle reliability, test evidence and performance/cost. Attach exact revision/build and evidence to each score; never invent proof. Stop early on acceptance, plateau or recurring blocker. Retain the strongest verified candidate and report unresolved work when the budget ends. If delegation is unavailable, execute roles serially and label the lack of independent evaluation.

Run affected checks again on the chosen build and return the concrete improvement, comparison evidence, limitations and artifacts.
