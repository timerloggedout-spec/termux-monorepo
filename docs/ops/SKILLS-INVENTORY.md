# Skills Inventory (termux-monorepo)

**Version:** 2026-09-22 · connector parity snapshot 2026-09-22  
**Primary agent entry:** [`CLAUDE.md`](../../CLAUDE.md)  
**Collaborator short entry:** [`SKILLS.md`](../../SKILLS.md)

## Collaborator access (parity)

All canonical skills are **in-repo** under `.agents/skills/` or `.github/skills/`. Local mirrors are convenience only and are not a second policy source.

| Entry | Purpose |
|-------|---------|
| [`SKILLS.md`](../../SKILLS.md) | Short collaborator pointer |
| This file | Full inventory + role matrix |
| Each `**/SKILL.md` | Executable skill body |
| [Plugin connector matrix](PLUGIN-CONNECTOR-CAPABILITY-MATRIX.md) | Live external capability snapshot |
| [Plugin integration priority](PLUGIN-INTEGRATION-PRIORITY.md) | Production multiplier ordering |

## Role load matrix

| Role | Load first | Then |
|------|------------|------|
| **Admin / Administrator** | `evidence-led-monorepo-ops` + `adaptive-wait` | `review-loop` · `plugin-connector-parity` · `help-wanted-lane` |
| **Collaborator** | `adaptive-feedback-cycle` | dual-gate · `find-skills` · `plugin-connector-parity` when external tooling is involved |
| **Oversight / external contrib** | `help-wanted-lane` | evidence-led + adaptive-wait · living status board |
| **Dashboard / Pages** | `github-pages-operator` | help-wanted-lane · deploy workflow |
| **Evaluation / DOE** | `multivariate-doe` + `blind-agent-evaluation` | `approxination-lane` · `mvt-experiment` |
| **CI / production recon** | `production-reconciliation` | `action-effectiveness-ledger` · `workflow-orchestration` · `plugin-connector-parity` |

## `.agents/skills/` (agent loadable)

Existing inventory remains authoritative; this cycle adds:

| Skill | Path |
|-------|------|
| plugin-connector-parity | `.agents/skills/plugin-connector-parity/SKILL.md` |
| loopy-api-loop-library | `.agents/skills/loopy-api-loop-library/SKILL.md` |

## `.github/skills/` (CI / production)

Existing inventory remains authoritative; this cycle adds:

| Skill | Path |
|-------|------|
| plugin-connector-parity | `.github/skills/plugin-connector-parity/SKILL.md` |

## Connector parity rule

Connector provider exposure is not equivalent to repository integration. Use:

`EXPOSED → CONNECTED → AUTHORIZED → OBSERVED → ADAPTED → INTEGRATED → VALIDATED`

The matrix records the live tool surface; the connector registry records repository-owned integrations.

## Cycle snapshot

- Live repository base was re-read before this change.
- Current ChatGPT surface observed: **88 connector providers / 2,042 connector actions / 2,052 callable tools**.
- GitHub installation for `timerloggedout-spec` is available and repository permission reports admin-level access for `termux-monorepo`.
- No secret values are recorded.
- Connector integrations are prioritized by measurable production leverage, not tool-count size.

**Agent-Identity:** Grok (Administrator)
