# Dashboard Versioning and Preview Standard

## Purpose

Every published static dashboard must be independently testable before merge and traceable after merge. A version label is an identity, not proof of equivalence: compare the exact source commit and per-page SHA-256 values.

## Required release identity

Every HTML page in a dashboard build receives the shared `versioning.js` header at build time. The header exposes:

- stable `page_unique_id` for the page;
- release version in `MAJOR.MINOR.PATCH+<12-character-source-SHA>` form;
- `production`, `preview`, or `development` channel;
- source commit prefix and navigation to every page in the generated manifest;
- a version-comparison page with preview and production links.

The generated `version-manifest.json` is the release authority. It records the full source SHA, source ref, build timestamp, stable page IDs, filenames, titles, and SHA-256 of each built HTML page. Do not treat the checked-in development manifest (whose hashes are null) as a published build attestation.

Page IDs must be unique. The builder fails closed if the registry is empty or page IDs collide. Do not label a comparison as unchanged when either content hash is absent; render the comparison as unavailable instead.

## Standard workflow

1. **Build and validate:** run the dashboard-specific regression suite and `python3 scripts/build_dashboard_manifest.py` against the exact artifact directory.
2. **Preview before merge:** from Actions, run **Help-Wanted Dashboard Preview** with the candidate branch or commit as `source_ref` and a stable isolated key such as `pr-2579`. The workflow copies the complete dashboard, uses the trusted builder from `master`, stamps the actual checked-out source SHA, and publishes under `/previews/<preview-key>/help-wanted/`. It must preserve existing Pages files (`keep_files: true`) and must not publish to the production directory.
3. **Compare and test:** open the preview and its `versioning.html` page. Verify the visible channel, version, source SHA, page registry, all navigation links, browser console, data assets, and Admin Graph validation behavior. Compare against the production manifest. Missing production metadata is a release blocker for equivalence claims, not a pass.
4. **Merge and supersede:** production deployment rebuilds from the merge commit, regenerates the manifest and content hashes, and publishes to `/help-wanted/`. The production version must use the same release prefix as preview and the merge commit's SHA, so the production identity supersedes the candidate identity without overwriting the isolated preview.
5. **Verify after merge:** inspect the production manifest and page headers; confirm `source_sha` equals the merge commit SHA, all HTML pages are listed exactly once, IDs are unique, hashes are populated, and comparison resolves the current production artifacts. Record the resulting version in the PR/release notes.

## Repository-wide adoption contract

Use this workflow as the standard for static dashboard or microsite releases in this repository, adapting only the artifact root, output path, and release prefix. Keep preview and production paths isolated, use exact source SHAs, preserve unrelated files, and make versioning-builder or workflow changes trigger the appropriate validation/deployment checks. Never claim a preview has been browser-tested unless that verification was actually performed.

## Current Help-Wanted release

The next candidate release prefix is `1.0.1`; version values are `1.0.1+<12-character-source-SHA>`. The earlier `1.0.0+551655fa6bca` preview remains a historical candidate and is not overwritten by this change.
