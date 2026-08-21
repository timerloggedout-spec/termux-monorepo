# TERMUX MONOREPO

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/timerloggedout-spec/termux-monorepo)

> **C×O operator guide.** Build deliberately. Preserve evidence. Keep the Android/Termux target first; treat every other environment as a simulation, review surface, or constrained support plane.

This repository is a mixed research, automation, and agentic-development monorepo. It is not a one-command product installer. Use it as an **evidence-led operating system for change**: enter through the smallest authoritative map, establish the relevant boundary, make a bounded change, and leave a validation trail.

The repository’s public language is deliberately compact, but never opaque. **Full paths, explicit ownership, reviewable commits, and human approval outrank clever abbreviations.** Internal short pointers belong only to a known local registry and must expand to an unambiguous source before they are acted upon.[1]

| Operator posture | Meaning |
|---|---|
| **Target** | Android/Termux is the intended execution environment. Linux desktops, CI, and cloud tools are support or simulation surfaces unless a current source says otherwise. |
| **Default** | Read the system map, then the owning source; do not infer runtime capability from historical artifacts, names, or external forks. |
| **Counter-culture rule** | No mystique without traceability. A compressed phrase, agent label, or short pointer must have a recoverable canonical source. |
| **Promotion rule** | Reviewable evidence and passing relevant checks precede promotion. An explicit operator override must be recorded, not implied. |

---

## 0. Fast start: choose the right map

Start with **one** of these routes. Do not load the entire repository merely because it is available.

| Need | Start here | What it owns |
|---|---|---|
| Understand a component, make a change, or assess first-order impact | [`docs/icm/CLAUDE.md`](docs/icm/CLAUDE.md) | Repository-native ICM system map, objects, processes, and impact routes. |
| Read root governance and navigation | [`AGENTS.md`](AGENTS.md) | Repository-level development guidance, architecture navigation, and constraints. |
| Maintain the ICM map itself | [`docs/icm/maintenance/CLAUDE.md`](docs/icm/maintenance/CLAUDE.md) | Inventory → human design review → verification → promotion procedure. |
| Operate or inspect the ArchWiz surface | [`archwiz/TOOL_INDEX.md`](archwiz/TOOL_INDEX.md) | Named cockpit, forensic, autonomous, verification, and knowledge tools. |
| Review open proposal governance | [`docs/proposals/`](docs/proposals/) | Registered active proposals, operator policy notes, and validation structure. |
| Review safety and tracked-state debt | [`docs/CREDENTIAL-EXPOSURE.md`](docs/CREDENTIAL-EXPOSURE.md) | Credential exposure findings and safe remediation boundary. |

The root README is an entry point, not a duplicate source of truth. When it conflicts with a maintained subsystem map, **the subsystem’s cited canonical source wins**.

---

## 1. Wiki and knowledge discovery

The repository’s Wiki surfaces have different responsibilities. They are designed to make discovery convenient without letting a provider-generated summary, an outdated snapshot, or an external page authorize a repository change.

| Surface | Primary role | Validation and write boundary |
|---|---|---|
| [GitHub Wiki](https://github.com/timerloggedout-spec/termux-monorepo/wiki) | Published reader view for approved Wiki Markdown. | Updated only by the managed publisher from reviewed in-repository `wiki/` content. |
| [Public DeepWiki](https://deepwiki.com/timerloggedout-spec/termux-monorepo) | Public discovery, repository orientation, source-linked questions, and provider-generated documentation. | Treat the displayed snapshot and its source reference as a discovery aid; verify freshness and corroborate material claims against repository source and review evidence. |
| [Devin Wiki](https://app.devin.ai/org/timerloggedout-spec/wiki/timerloggedout-spec/termux-monorepo) | Authenticated documentation-generation and research surface. | Root [`.devin/wiki.json`](.devin/wiki.json) steers coverage; Devin is not a GitHub Actions writer or a source of change authorization. |
| [`wiki/`](wiki/DeepWiki-Mirror.md) | Canonical, reviewable Markdown projection for GitHub Wiki publication. | Changes follow the normal pull-request process and are published only after merge. |

The badge above links directly to the public DeepWiki page. The current public page exposes an indexed, source-linked snapshot, while the provider’s documentation describes automatic Wiki indexing and optional root-level steering through `.devin/wiki.json`.[5] [6] That convenience does **not** establish snapshot freshness, implementation truth, or authority to write. A stale, incomplete, or drifted provider description must be rechecked against the current repository path, commit, workflow, or review record before it is adopted.

Repository-surface discovery is automated through the existing job-scoped operator-token lane. Its daily read-only reconciliation discovers repositories that the credential can actually reach—including accessible organization and collaborator repositories—and reports the managed Wiki-publisher state as `current`, `missing`, `drifted`, `unmanaged`, `excluded`, or `blocked`. A drifted or missing publisher is a review signal, not a write permission: only a manually requested `apply=true` run may create a dedicated branch and reviewable pull request; it never modifies a default branch or merges for a repository.[7]

A companion **Devin Wiki access reconciler** runs daily after repository-surface discovery. Where the existing Devin GitHub App uses selected-repository access and the established operator PAT meets GitHub’s documented requirements, it assigns newly discovered repositories to that existing App installation. This makes provider-managed Devin/DeepWiki indexing eligible, but it does not call an undocumented public DeepWiki indexing or refresh endpoint, and it does not claim an index is current until its visible source reference is verified.[8]

The validation sequence is therefore deliberate: use DeepWiki or Devin to discover context; bind material claims to primary repository evidence; bring approved documentation into `wiki/` through a pull request; and let the managed publisher project only that reviewed Markdown to GitHub Wiki. The full trust boundary, stale/drift handling, and operator runbook are maintained in [`wiki/DeepWiki-Mirror.md`](wiki/DeepWiki-Mirror.md), [`docs/agentic/repository-surface-reconciliation.md`](docs/agentic/repository-surface-reconciliation.md), and [`docs/agentic/devin-wiki-access-reconciliation.md`](docs/agentic/devin-wiki-access-reconciliation.md). The **Linguist machine-parity README enhancement is a separate proposal** and is not part of this documentation or badge change.

---

## 2. Repository-native ICM — the operating context

The [Interpretable Context Methodology](docs/icm/CONTEXT.md) is applied to **this repository itself**. It makes folders and Markdown contracts into an agent-readable control plane: each component has a purpose, source boundary, relationships, and first-order change impact. The operating workspace is `docs/icm/`; external forks are inputs, not a replacement for the repository’s own architecture.[2]

| ICM surface | Use it for | Boundary |
|---|---|---|
| [`docs/icm/CLAUDE.md`](docs/icm/CLAUDE.md) | System orientation and route selection | [`docs/icm/AGENTS.md`](docs/icm/AGENTS.md) is its byte-identical static alias. |
| [`docs/icm/routing.md`](docs/icm/routing.md) | Provider-routing evidence and proposals | It is deliberately separate from the static catalog; it does not invoke providers, store secrets, or mutate workflows. |
| [`docs/icm/effects/CONTEXT.md`](docs/icm/effects/CONTEXT.md) | “If I change X, what must I read?” | First-order impacts only; source documents own implementation detail. |
| [`docs/icm/_meta/method-coverage.md`](docs/icm/_meta/method-coverage.md) | Verify ICM form coverage and intentional omissions | Describes documentation context, not runtime behavior. |
| [`docs/ICM-ARCHITECT-INTEGRATION.md`](docs/ICM-ARCHITECT-INTEGRATION.md) | Inspect reference forks and initialization rules | All forks are shallow, reviewed, and reference-only. |

### Reference inputs: study, do not confuse with runtime

| Reference input | Repository role |
|---|---|
| `icm-architect_fork` | Compact forms, templates, and system-map guidance. |
| `interpretable-context-methodology_fork` | Full methodology, conventions, and example workspaces. |
| `content-agent-routing-promptbase_fork` | Layered routing, canonical-source, and one-way-dependency precedent. |
| `icm-cctv_fork` | File-backed visual-review and human-checkpoint pattern. |

The full initialization and update rules are maintained in the [integration guide](docs/ICM-ARCHITECT-INTEGRATION.md). A Gitlink is a reviewed reference pointer; it is **not** permission to execute, deploy, or inherit an external project’s behavior.

---

## 3. Agentic control plane — strong boundaries, no theater

This repository supports agents, CI, and review tools, but it does **not** authorize unattended self-modification. Agentic work is governed by source ownership, repository checks, peer review, explicit secrets boundaries, and the human operator.

| Actor / surface | Current role | Must not be assumed |
|---|---|---|
| Human operator | Sets scope, approves sensitive promotion or runtime access, and resolves exceptions | An always-online shell, device approval, or implicit consent. |
| GitHub Actions | Runs repository checks, lifecycle validation, review orchestration, and configured publication tasks | A substitute for runtime architecture or a blanket right to change code. |
| Devin | Peer review and review/fix participant under existing repository orchestration | A public Auto-Fix API or automatic write permission outside configured service settings. |
| Jules | Coordinated builder path through existing issue and review workflows | Unbounded scope, device access, or duplication of work already claimed by another agent. |
| Dependabot | Valid monitor configuration for GitHub Actions dependencies; version-update pull requests are limited to zero | A release manager or an approval substitute. |
| Termux / BLU B160V | Design and future execution context where currently verified | A live MCP transport, public shell, or device capability merely because historical artifacts mention one. |

The current integration markers are maintained in [`.github/connectors/integrations.yaml`](.github/connectors/integrations.yaml), and peer coordination is implemented in the relevant workflow sources. Read the current workflow before proposing a new bot loop; do not create a parallel control plane.

---

## 4. Linguist, CedrLang, and CID pointers

The repository’s Linguist work optimizes **internal** agent communication through CedrLang compression and short-pointer conventions. The current `cid.py` implementation stores mappings locally under `~/.cedar/cedar_index.json`, generates short base-36 pointers, and expands them back to full commands.[1] The merged CedrLang v2 implementation documented lossless, line-oriented handling for its intended compiler pipeline.[3]

> **README rule:** public documentation stays explicit. Use readable paths and links here. CID pointers are an internal efficiency mechanism only when the receiving context has the same trusted registry and can expand the pointer before execution.

| Surface | Purpose | Audit route |
|---|---|---|
| [`workspace/compression_sandbox/cedrlang/cid.py`](workspace/compression_sandbox/cedrlang/cid.py) | Local CedarIndex short-pointer registry and expansion behavior | Source-level implementation. |
| [`harmony_hub/workspace/agent/LINGUIST_SPEC.md`](harmony_hub/workspace/agent/LINGUIST_SPEC.md) | Linguist role, pointer conventions, and integration intent | Agent specification. |
| [PR #196](https://github.com/timerloggedout-spec/termux-monorepo/pull/196) | Merged CedrLang v2 compilation work | Historical implementation and review evidence. |
| [PR #228](https://github.com/timerloggedout-spec/termux-monorepo/pull/228) | Merged fast-path term-search optimization | Subsequent performance evidence. |

1337-style naming may be used as a **display dialect**, never as a substitute for a source path, permission boundary, or validation result. The disciplined version of “l33t” is legibility under pressure.

---

## 5. Visual review / CCTV — cards first, renderer later

The repository now owns initiated, file-backed review cards at [`docs/icm/_tv/`](docs/icm/_tv/README.md). They can mirror an approved stage or human checkpoint while leaving the source artifact canonical.

| Status | Meaning |
|---|---|
| **Initiated** | Card layout, response cage, and initial ICM integration screens exist in the repository. |
| **Not enabled by default** | No renderer, file watcher, WebSocket loop, public service, device connection, or provider polling is started by these files. |
| **Future mobile path** | A static export can later be published to a mobile browser through a separately reviewed publication change. GitHub Pages can serve static output; it is not the live renderer. |

Do not treat a dashboard card as an approval, an execution command, or a source of truth. Open the cited source card or operational document before changing runtime behavior.

---

## 6. Validation and promotion

The repository gate is designed to be cheap, portable, and usable without device access. It reads the Git index, applies hard checks to changed paths, and ratchets tracked debt instead of allowing it to grow. It now handles Git submodule Gitlinks as commit references rather than trying to read them as blobs, so the ICM reference inputs can be safely checked in CI.[4]

```bash
# From the repository root
python3 scripts/ci/repo_gate.py --base origin/master
python3 scripts/proposals/validate_registry.py
```

Use the ICM [change-and-validate process](docs/icm/processes/change-and-validate.md) to identify the relevant source, proposal, and checks. The repository’s historical `termux-smoke` topology may require separate current-source verification; never infer a runnable device path simply from a branch name or stale document.

---

## 7. Safety, recovery, and audit discipline

The monorepo contains recovered, generated, historical, and mixed-confidence material. Treat `workspace/`, session artifacts, saved outputs, and recovery-era content as evidence to classify before using—not as indisputable runtime configuration.

| Situation | Read first | Do not do |
|---|---|---|
| Credential or browser-profile concern | [`docs/CREDENTIAL-EXPOSURE.md`](docs/CREDENTIAL-EXPOSURE.md) | Copy, publish, or normalize secrets into a new artifact. |
| Workspace artifact or generated-map request | [`docs/icm/objects/knowledge/workspace-artifact-estate.md`](docs/icm/objects/knowledge/workspace-artifact-estate.md) | Delete, promote, or execute it without classification. |
| Device or service availability question | [`docs/icm/objects/platform/blu-b160v-free-services.md`](docs/icm/objects/platform/blu-b160v-free-services.md) | Infer live Termux or device access from a design constraint. |
| Reference fork update | [`docs/icm/objects/knowledge/reference-inputs.md`](docs/icm/objects/knowledge/reference-inputs.md) | Treat an external fork as an unchecked runtime dependency. |
| Broad staging-history recovery | [`docs/icm/_meta/master-rebuild-integration-evidence.md`](docs/icm/_meta/master-rebuild-integration-evidence.md) | Import the archive wholesale; review components independently. |

---

## 8. Audit trail

This README replaces a recovery-era root document with a deliberate navigation and operating guide. The immediate predecessor ICM entry-point update is preserved at [`a49efbb`](https://github.com/timerloggedout-spec/termux-monorepo/commit/a49efbb268b0847261bda65df516508fa2a11e95). The repository-native ICM delivery entered `master` through [PR #232](https://github.com/timerloggedout-spec/termux-monorepo/pull/232) at merge commit [`2b8396a`](https://github.com/timerloggedout-spec/termux-monorepo/commit/2b8396a65e65077d315c1a570b48061d903d8ce6).

The preserved pre-rebuild branch [`archive/pr232-pre-master-rebuild-20260817`](https://github.com/timerloggedout-spec/termux-monorepo/tree/archive/pr232-pre-master-rebuild-20260817) remains available as review evidence for later component-by-component workflow and application work. It is intentionally not a mandate to replay divergent history.

---

## References

[1]: https://github.com/timerloggedout-spec/termux-monorepo/blob/master/workspace/compression_sandbox/cedrlang/cid.py "CID pointer implementation"
[2]: https://github.com/timerloggedout-spec/termux-monorepo/pull/232 "Repository-native ICM integration"
[3]: https://github.com/timerloggedout-spec/termux-monorepo/pull/196 "Linguist: implement CedrLang v2 compilation"
[4]: https://github.com/timerloggedout-spec/termux-monorepo/commit/975f951bfc00dc6785bd3755b754dd9f19dc272e "Gitlink-safe repository gate repair"
[5]: https://deepwiki.com/timerloggedout-spec/termux-monorepo "Public DeepWiki page for timerloggedout-spec/termux-monorepo"
[6]: https://docs.devin.ai/work-with-devin/deepwiki "Devin DeepWiki documentation"
[7]: docs/agentic/repository-surface-reconciliation.md "Repository-surface reconciliation runbook"
[8]: docs/agentic/devin-wiki-access-reconciliation.md "Devin Wiki access reconciliation runbook"
