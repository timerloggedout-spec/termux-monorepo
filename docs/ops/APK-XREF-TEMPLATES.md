# APK ↔ Repo Cross-Reference — template set + intake

`[MUSEai]@{role:{research-triggers}}` — owner directive via the Foundry lane
(a27e8da6, 2026-10-28): APK↔repo cross-reference is its own category with its
own template set. Until now the filings went in as generic Target Briefs
(the 30-app wave's `-apk` issues, #2064–#2123). The Foundry lane migrates
those onto this set from its side; the target-brief versions stand meanwhile.

## Forms — the Reverse Engineering family (`.github/ISSUE_TEMPLATE/`, label `apk-xref` on both)

Both forms stay inside the proven chooser-safe construct subset (Delphi RFP
baseline; target-brief v1 lesson, PR #1656): no emoji in `name`, no
checkboxes, no dropdown `default:`, no `placeholder:`, no explicit
`required: false` — only markdown / input / textarea / dropdown, with
`validations: { required: true }` or no validations block.

| Form | Purpose | Key fields → record (`apk-xref/v1`) |
|---|---|---|
| `apk-cross-reference.yml` | the request | target_id, paired_repo_brief (issue ref of the paired repo Target Brief), target repo URL, artifact_source [github-releases, gitea-releases, f-droid, google-play, direct-apk, other-store, none-known], artifact_version, package_id, authorization basis, scope domains, side effect, state-changing, probe budget, venue, evidence expectation, claims_to_check, submitter Role{Moniker}, notes |
| `apk-cross-reference-findings.yml` | the results | target_id, xref_issue (the request filing), package_id (`none` only for a no-artifact verdict), artifact_source, artifact_version, manifest_permissions, endpoints_observed (actually observed, not source-mentioned), claims_checked, divergences_repo_to_apk, divergences_apk_to_repo ("none found" is a valid explicit value), verdict [match, divergences-found, no-artifact-found], evidence met, submitter, notes |

Semantics (from the wave briefs + `WEB-REVERSE-ENGINEERING-CAMPAIGN.md`):
cross-validate in BOTH directions — source claims absent from the artifact
and artifact behavior absent from source are the findings; a target with no
published APK closes as no-artifact-found WITH evidence, never by
substituting another build.

## Intake (`.github/workflows/apk-xref-intake.yml`)

Event trigger, no cron, no `pull_request_target`: `issues`
[opened, reopened, edited] with label `apk-xref` — exactly one event per
filing, no `labeled`, no concurrency group (research-intake fix pattern,
PRs #2132/#2137). Parser `scripts/apk_xref/apk_xref_intake.py` (stdlib,
deterministic; tests `tests/test_apk_xref_intake.py`) validates the issue
references, package-id shape, the `Role{Moniker}` submitter pattern, the
write⇒state-changing rule, and both divergence directions, then comments
the `apk-xref/v1` record on the issue (sha256 hash marker dedupes
sequential duplicate events; an edit re-posts). Kind is derived: a filing
carrying a verdict is `findings`, otherwise `request`. Permissions: top
`{}`, job `contents: read` + `issues: write`; no provisioned secrets.

The `apk-xref` label was created with this set. It does NOT carry
`target-brief`, so target-intake does not double-fire on these filings;
the paired repo brief remains a normal Target Brief.
