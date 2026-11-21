# Codex Security — adoption assessment

**Assessment date:** 2026-11-16  
**Upstream:** https://github.com/openai/codex-security  
**Observed package:** `@openai/codex-security@0.10.0`  
**License:** Apache-2.0  
**Repository lane:** `agentic-security`  
**Status:** discovered candidate; no package installed, scan executed, or adapter promoted

## Executive decision

Admit Codex Security as a **P1 research candidate** for repository vulnerability analysis. Do not install it as a default dependency, make it a required CI gate, or allow it to apply patches automatically yet.

It complements, rather than replaces, CodeQL, dependency review, existing repository checks, specialist malware/reverse-engineering lanes, and human security review.

## Verified capabilities

The upstream repository and official documentation describe:
- Standard scans of a repository or selected paths.
- Diff scans for committed changes or working-tree changes.
- Repeated deep scans with deduplicated findings.
- Validation/triage of candidate findings.
- Candidate patch generation and fix verification.
- Drafting `SECURITY.md` guidance and threat models.
- Import of selected third-party scanner findings.
- SARIF, JSON, and CSV exports.
- CLI, TypeScript SDK, Codex security workflows, and a GitHub Action.

Useful CLI patterns documented upstream:

```bash
# Scan the repository.
cs scan .

# Scan selected paths.
cs scan . --path src --path tests

# Scan committed changes relative to the fetched canonical base.
cs scan . --diff origin/master

# Run a bounded-time Standard investigation (advisory allowance).
cs scan . --max-time 15

# Apply an estimated model-cost limit to the scan and its workers.
cs scan . --max-cost 2.00
```

The `--max-time` setting is an advisory Standard investigation allowance, not a hard wall-clock or spend guarantee. The current CLI also documents `--max-cost USD`: it stops the scan/workers after estimated usage exceeds the limit, but in-flight requests can finish above it. Budget enforcement requires complete token-usage records for the scan and workers. Review the current CLI help and select a conservative ceiling before using flags in automation.

## Runtime compatibility

The current TypeScript package documents:
- Node.js 22.13+ within 22.x, or Node.js 24.x or 26.x.
- Python 3.10+ for scans and related workflows; Python 3.10 also needs `tomli`.
- macOS, Linux, and Windows as supported operating systems.

**Termux/Android ARM is not listed as a supported platform.** Do not infer compatibility merely because Node and Python are available in Termux. A separate smoke test is required before treating it as an on-device tool.

## Cost and authentication

The package is Apache-2.0, but model inference is not thereby free. The upstream CLI supports ChatGPT sign-in or `OPENAI_API_KEY` / `CODEX_API_KEY`; the SDK reports estimated model usage cost when available. Some protected cybersecurity requests and findings require Trusted Access for Cyber.

Before a pilot:
1. Establish the intended auth mode and credential scope.
2. Set an explicit model/provider and spend/time budget where supported.
3. Confirm what source context is transmitted to the selected inference provider.
4. Use `--max-cost` where supported, while accounting for in-flight requests and incomplete usage data.
5. Record actual cost as an observed value, not a marketing assumption.

## Privacy and execution boundary

Do not repeat the social post's assertion that source code never leaves the machine as an established guarantee. The official documentation confirms local execution under the caller's OS permissions and local report storage, but does not establish that model-assisted scanning is offline.

The upstream security policy makes several important points:
- Scans run with the local operating-system permissions.
- Deep-scan workers use read-only execution to avoid concurrent workspace writes.
- Read-only does **not** mean isolated or offline, and inherited MCP servers remain available.
- Reports and logs may contain source code, credentials, and vulnerability details.

Therefore:
- Use a least-privilege environment with only the required credentials.
- Keep the Codex Security state directory and reports outside the target checkout and every enclosing Git worktree.
- Never upload raw reports to public Actions artifacts.
- Redact findings before placing summaries in the canonical evidence plane.
- Keep original reports in a restricted/private location and reference them by opaque evidence ID.
- Never let scanner output execute shell commands, modify production, create public issues, or authorize its own patch.

## Worktree interaction

Codex Security documents that linked Git worktrees can share scan history and saved findings when they use the same `CODEX_SECURITY_STATE_DIR`.

That creates two useful experimental treatments:
- **Shared state:** intentionally share scan history for one repository when continuity and deduplication are desired.
- **Isolated state:** assign separate private state directories for independent model/treatment experiments to avoid cross-cohort contamination.

In both cases, state directories stay outside all worktrees. Record which treatment was used in the existing orchestration receipt's evidence references; do not add provider-specific state paths or report bodies to the canonical event schema.

## Proposed adapter contract

| Dimension | Proposed behavior |
|---|---|
| Default mode | Read-only scan |
| Scope | Selected path or PR diff before full repository |
| Output | Sanitized findings summary + opaque private report reference |
| Patching | Candidate only; separate review and verification |
| CI | Advisory pilot first; required gate only after validation |
| Evidence | Repo/base/head SHA, tool version, scope, exclusions, model/provider, estimated cost, report ID, validation result |
| Failure semantics | Distinguish tool/setup/auth failure, scan failure, no findings, incomplete coverage, and validated clean result |
| Promotion | Existing security review and repository dual gates only |

## Pilot acceptance criteria

1. Package/runtime install is reproducible on the intended runner.
2. A bounded owned diff scan completes with known inputs.
3. Findings can be traced to source evidence and independently reproduced.
4. False positives, missed paths, and exclusions are recorded.
5. Cost, latency, and retry behavior are measurable.
6. Reports remain private and outside tracked worktrees.
7. Scanner failure cannot become a false clean result.
8. Patch proposals require independent review and a separate verification scan.

## Sources

- Official repository: https://github.com/openai/codex-security
- Package metadata: https://github.com/openai/codex-security/blob/main/sdk/typescript/package.json
- CLI reference: https://github.com/openai/codex-security/blob/main/sdk/typescript/docs/cli.md
- SDK guide: https://github.com/openai/codex-security/blob/main/sdk/typescript/docs/sdk.md
- Security policy: https://github.com/openai/codex-security/blob/main/SECURITY.md
- Open-source package listing: https://www.npmjs.com/package/@openai/codex-security
- Instagram source post: https://www.instagram.com/p/DfrcNATlntx/
