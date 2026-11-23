# Work Items — siglary-communication-law

| ID | Work item | Status | Evidence |
|---|---|---|---|
| SIG-01 | Publish DO-first communication law; bind AGENTS/contributor guidance; add PR and commit templates. | done | PR #5339 merged as `4c77ced7`; `docs/ops/COMMUNICATION-LAW.md`. |
| SIG-02 | Update `CLAUDE.hum.md` and regenerate/verify `CLAUDE.md`; maintain AGENTS source/projection parity. | done | Canonical sources and generated projections updated; `tests.test_contact_projections` wired into repo-gate validation. |
| SIG-03 | Publish stable numbered Siglary operator registry with families, definitions, and collision rules. | done | `docs/ops/SIGLARY-OPERATOR-REGISTRY.md`; 36 stable operator IDs. |
| SIG-04 | Implement changed-file prose lint plus commit/PR metadata checks, allowlists, and machine-readable findings with DO rewrites. | in_progress | `scripts/ci/communication_lint.py`; output schema `siglary-lint/v1`. |
| SIG-05 | Test negation false positives, quoted text, code blocks, identifiers, and multilingual content. | done | 10 focused unit tests pass in local isolated test harness; CI repeats them. |
| SIG-06 | Integrate lint into CI with changed-file scope and actionable file/line diagnostics. | in_progress | `scripts/ci/repo_gate.py` HARD check + `.github/workflows/repo-gate.yml` test and metadata wiring; exact-head CI pending. |
| SIG-07 | Add bounded GitHub comment/review auditing with pagination, caching, and rate-limit/inconclusive outcomes. | todo | One-off PR #5806 snapshot: 20 bot-authored timeline comments, 0 review threads; external content advisory. Automated bounded pagination/cache remains queued. |
| SIG-08 | Document authoring, review, exception, and generated-projection workflow; run both repository gates. | in_progress | `docs/ops/COMMUNICATION-LAW.md`, `docs/ARCHW1Z-GATE.md`; exact-head repo gate and Termux smoke pending. |
