# Accessibility Agents — Monorepo Integration

## Source and pin

The monorepo tracks the user-owned fork at `refTemplates/smods/accessibility-agents_fork`.

- Fork: <https://github.com/timerloggedout-spec/accessibility-agents_fork>
- Upstream: <https://github.com/Community-Access/accessibility-agents>
- License: MIT
- Pinned commit: `a538edc9edfb98cdd8bae96d6b79542874b478f7`

The submodule is a reproducible reference source. Review pin advances as normal dependency changes.

## Native integration

The adapter skill lives at `.agents/skills/accessibility-agents/SKILL.md`. It dispatches to the pinned source's routers and specialists by reference. The source skill tree remains intact in the submodule; the monorepo maintains its own entry point, scope governance, execution policy, and CI.

Primary source contracts:

- `skills/a11y-core/SKILL.md`: router/specialist/helper/reference tiers, dispatch boundary, findings and report contracts.
- `skills/accessibility-lead/SKILL.md`: change classification, specialist dispatch, finding merge, ship verdict.
- `skills/ci-accessibility/SKILL.md`: scanner baselines, severity thresholds, SARIF, regression gating.
- `docs/accessibility/accessibility-framework.md`: framework action tracking and evidence.
- `docs/accessibility/accessibility-testing.md`: manual and automated verification expectations.
- `skills/a11y-core/references/sources.md`: authoritative accessibility specifications.

## Routing

| Work shape | Source route |
|---|---|
| Web UI, HTML, CSS, components, templates | `accessibility-lead` |
| Whole-site or whole-app audit | `web-accessibility-wizard` |
| Word, Excel, PowerPoint, PDF, ePub | `document-accessibility-wizard` |
| Markdown documentation | `markdown-a11y-assistant` |
| Python, desktop, mobile, assistive technology, tooling | `developer-hub` and the relevant specialist |
| GitHub issues, pull requests, Actions, release workflows | `github-hub` |

Routers select the smallest adequate specialist set. Specialists return structured findings; reports preserve criterion, severity, location, description, and fix. A clean result names the specialists and checks actually run.

## Execution and CI boundaries

- Reuse monorepo proposal items, GitHub review, `repo_gate.py`, and `termux_smoke.py`.
- Treat upstream workflows as reference implementations. Do not activate the fork's package-release, docs-sync, or branch-protection workflows in this superproject.
- Scanner installation is opt-in and scoped to the relevant project/runtime. Keep heavyweight browser and document toolchains out of the default Termux smoke path.
- Use baseline-aware regression checks where a measured baseline exists. Preserve manual keyboard, screen-reader, cognitive, and document checks where automated scanners cannot establish conformance.
- Record findings and evidence with the change. A scanner pass is not proof of full accessibility.

## Framework status

The Open Source Accessibility Framework is an improvement framework, not a certification. Track each adopted action against its actual definition of done and link evidence. Mark unknown or unverified actions as pending; do not infer completion from the presence of a skill, workflow, or policy document.
