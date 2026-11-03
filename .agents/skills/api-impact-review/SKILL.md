---
name: api-impact-review
description: Use for pull requests that change API contracts, client/server boundaries, protocols, schemas, or public integration surfaces; invokes API Impact Mapper and produces a SHA-bound report.
---

# API Impact Review

## Purpose

Produce an evidence-backed API evolution review for one exact PR head. The API Impact Mapper tools are assistant-session capabilities; do not claim GitHub Actions can invoke them directly.

## Required sequence

1. Read PR metadata, base SHA, head SHA, changed-file list, and diff from GitHub.
2. Check `config/integrations/api-impact-paths.json`. If no configured API surface changed, record `not_applicable`.
3. Read relevant contract definitions, server routes, clients, consumers, tests, and docs. Quote only minimum evidence needed.
4. Call `mcp__API_Impact_Mapper__extract_api_changes` with the exact supplied diff/contract material in `source_text`.
5. Call `mcp__API_Impact_Mapper__classify_breaking_changes` with the same explicit before/after evidence.
6. Call `mcp__API_Impact_Mapper__generate_impact_map` with the source material and confirmed extraction/classification items in `confirmed_items`.
7. Never invent changes, consumers, tests, docs, evidence, confidence, or provider outcomes. Keep `cannot_determine` and partial results unresolved.
8. Build the JSON envelope defined by `docs/integrations/schemas/api-impact-mapper-input.schema.json`:
   - `repository`, `pull_request`, `base_sha`, and `head_sha` must match the exact current PR.
   - Set privacy booleans to false only after inspecting the payload and confirming no raw prompts or secrets are present.
   - Include complete structured extraction, classification, and impact-map results.
   - Never include raw prompts, completions, conversation messages, raw diffs, credentials, cookies, or secret values.
9. Invoke the **API Impact Review** workflow manually from the default branch with the PR number and JSON envelope. Download its JSON/Markdown artifact.
10. Re-fetch the PR head before reporting. If it moved, discard the stale report and repeat on the new SHA.

## Interpretation

- `not_applicable`: no configured API surface changed.
- `analysis_required`: surface changed but no mapper result exists for this exact head.
- `partial`: a stage is partial/error, fields are missing, evidence is incomplete, or classification is unresolved.
- `validated`: report structure and evidence links validate; this does not certify compatibility.

## Review checklist

- [ ] Before/after contract is explicit.
- [ ] Every extracted change cites evidence.
- [ ] Every classification cites evidence and preserves uncertainty.
- [ ] Consumers, tests, and docs are grounded in repository evidence.
- [ ] Every impact references an extracted change and evidence.
- [ ] PR number and full base/head SHAs match.
- [ ] No raw prompt, completion, raw diff, credential, cookie, or private session content is included.
- [ ] Repo-gate and Termux smoke remain independent merge requirements.

## Authority boundary

The mapper is advisory. It cannot edit code, approve a review, merge, deploy, or override repository policy. A green report is not a substitute for tests or human review.
