# API Impact Review Lane

## Purpose

Read-only, evidence-first API change review for pull requests. It combines a configured path detector, API Impact Mapper extraction/classification/impact-map stages, a strict repository-owned normalizer, and a PR artifact.

## Run locally

```bash
python3 -m scripts.integrations.api_impact.cli \
  --repository timerloggedout-spec/termux-monorepo \
  --base <base-sha> --head <head-sha> --pr-number <number>
```

The CLI computes changed paths with `git diff --name-only --diff-filter=ACMR -z BASE...HEAD`. Add `--mapper-input path/to/mapper-input.json` to normalize mapper results. Invalid, stale, or privacy-unsafe input exits non-zero.

## Assistant-assisted provider flow

GitHub Actions cannot call the ChatGPT MCP connector merely because it is available in an assistant session. Until a separately authenticated CI endpoint exists, use the `api-impact-review` assistant skill:

1. Re-fetch PR metadata and exact head SHA.
2. Retrieve the PR diff and relevant API contract, consumers, tests, and docs.
3. Call `extract_api_changes` with supplied diff/contract material.
4. Call `classify_breaking_changes` with the same before/after evidence.
5. Call `generate_impact_map` with source material and confirmed extraction/classification findings.
6. Preserve partial/error states, `cannot_determine`, missing fields, evidence, and limitations.
7. Build the envelope defined by [api-impact-mapper-input.schema.json](schemas/api-impact-mapper-input.schema.json). Include repository, PR, base/head SHAs, and a truthful privacy attestation. Do not include raw prompts, completions, raw diffs, tokens, cookies, or credentials.
8. Use the workflow's **Run workflow** form on the default branch, supply the PR number and JSON envelope, and download the report artifact. The normalizer rejects stale SHAs and mismatched PR identity.

The `pull_request` event emits an `analysis_required` report when API paths changed but mapper output has not been supplied. This is observation-only and is not a blocking required check.

## Report states

| State | Meaning |
|---|---|
| `not_applicable` | No configured API surface changed |
| `analysis_required` | API surface changed; no mapper result supplied for this exact PR |
| `partial` | Provider output has missing fields, errors, unresolved classifications, or incomplete evidence |
| `validated` | Report structure, identity, IDs, and evidence references validate; this is **not** compatibility approval |

## Scope and safety

- Initial paths live in `config/integrations/api-impact-paths.json`.
- The detector is intentionally path-policy based; it does not claim to find every API contract.
- Every change, classification, and impact must cite known evidence IDs.
- Duplicate IDs, dangling references, stale identity, path traversal, prohibited fields, and credential-shaped values are rejected.
- Provider output is untrusted and advisory. CI has read-only permissions and never executes returned code.
- Human review, repo-gate, Termux smoke, and promotion policy remain authoritative.

## Promotion criteria

Keep this lane advisory until false-positive/negative rates and provider result quality are observed across real PRs. A blocking required check needs a separate proposal, a CI-callable authenticated provider interface or explicit human-attested artifact workflow, and measured reliability.
