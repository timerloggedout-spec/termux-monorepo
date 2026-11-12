# README Evolution — Linguist-guided, comparative

**Status:** implementing under LMP-01  
**README comparison baseline:** master snapshot at fdba31514d03101250dd276db45ff3c3414ee7c1 (README blob 107c59e30b5ae4810574ecc987ca4e37766c62d0)  
**Operator direction:** 2026-11-11  
**Implementation PR:** #5188  
**Scope:** root README and directly related Linguist/CedrLang/Grimoire projections

## Purpose

Evolve the root README incrementally while preserving its role as a readable public entry point. Each update must improve navigation, semantic mapping, or visual explanation and must remain comparable with prior versions.

The README is a **projection**, not the canonical home of subsystem detail. Canonical source documents and mapping registries remain authoritative.

## Mapping authorities — do not duplicate them

| Concern | Existing authority | Use |
|---|---|---|
| Internal Linguist mappings | docs/ops/LINGUIST-PANEL-FEED.md + scripts/linguist/linguist_panel_feed.py | Consume canonical mapping families; do not transcribe them into a second registry |
| CedrLang phrase/token mappings | workspace/compression_sandbox/cedrlang/cedrlang.py | Canonical source for MAPPINGS, SYMBOL_MAP, and STOPWORDS |
| Reversible phase codec | workspace/compression_sandbox/cedrlang/phase_codec.py | Isolated token-level variant codec |
| Grimoire vocabulary | harmony_hub/config/grimoire/1337_D1CT10N4RY.md | Human-readable vocabulary reference |
| GitHub language classification | .gitattributes + GitHub Linguist | Separate repository language/statistics mechanism |
| Visual mapping surface | apps/tribute-dashboard/linguist.html | Existing mapping-family visual explorer |

**Do not conflate** internal Linguist/CedrLang compression with GitHub Linguist language classification. Treat .gitattributes as a separate classification surface; add or change a mapping only when observed GitHub Linguist classification evidence justifies it. Do not create a new mapping authority, private-pointer dependency, or a parallel dashboard feed.

## Rate policy: micro default, macro ceiling

The operator's two candidate values are treated as different operating scales:

| Mode | Rate | Meaning |
|---|---:|---|
| Routine micro-evolution | **0.07%** | Default eligible-token review/change budget per update |
| Seeded variation | **±10% relative** | Deterministic rnd± variation by file, using the base commit SHA as seed |
| Exploratory ceiling | **7%** | Maximum budget for a justified structural or semantic pass |

The default is 0.0007 as a fraction; the ceiling is 0.07. The default rate is not a command to mutate 0.07% of text on every commit. It is a **budget and measurement target**. Small files may receive a zero-token budget after rounding.

A change that needs more than the budget to correct meaning, broken navigation, accessibility, security, or source drift may exceed it. Record the reason in the PR/commit evidence. Never truncate or distort a necessary correction to satisfy a percentage.

The historical codec value INITIAL_SUBSTITUTION_PROBABILITY = 0.70 is a separate 70% token-variant probability from PR #154. It is not the README evolution rate and must not be silently changed by this policy.

## Deterministic rnd± contract

1. Seed the pseudo-random generator with the exact base commit SHA (or an explicitly recorded seed for a controlled comparison).
2. Sort tracked eligible paths before selection.
3. Derive a separate rate for each eligible file from the seed and the configured relative jitter.
4. Group planned budgets by directory so the distribution can be inspected across the related tree.
5. Record the seed, rate, eligible token count, planned token budget, file list, and base/candidate refs.
6. The planner is **report-only**. It selects review budgets; it never rewrites content or changes a mapping.

Run:

~~~bash
python3 scripts/linguist/readme_evolution.py compare --base-ref master --candidate-ref HEAD --path README.md

python3 scripts/linguist/readme_evolution.py plan --seed "$(git rev-parse HEAD)"
~~~

The policy is machine-readable in readme-evolution-policy.json. The immutable comparison inputs and their metrics are recorded in readme-branch-census.json.

## Comparative baseline — README branch census

The following candidates were fetched from GitHub and compared with the current master README (291 lines / 26,610 UTF-8 characters at the baseline above). The delta is the symmetric LCS line-difference ratio:

100 × (base-only changed lines + candidate-only changed lines) / (base lines + candidate lines)

| Candidate branch | Commit SHA (12) | README blob SHA (12) | README lines | UTF-8 bytes | LCS line delta |
|---|---|---|---:|---:|---:|
| docs/readme-agents-link-fix | c64fd4affc66 | 3ba0805a884a | 289 | 26,647 | 2.07% |
| docs/readme-agents-reference | 05ac94d4211f | ca746df7b383 | 465 | 24,702 | 75.66% |
| docs/readme-ates-image-polish | ee0ffc2540b8 | 2e3c004f096f | 197 | 20,022 | 24.18% |
| docs/readme-upgrade-claude-entry-ates-deploy | e1d997a85cac | 1bfb11f504d8 | 212 | 21,855 | 21.27% |
| manus/readme-deepwiki-validation-integration | 79234418029b | b8429e610bee | 173 | 16,841 | 27.59% |
| studysprint-readme-currency | 1bb35e6bf75d | 3ca45334d2ea | 290 | 26,549 | 0.52% |

Full 40-character commit and blob identifiers, including the baseline, are preserved in readme-branch-census.json.

These values measure textual distance only. They are **not** rankings, quality scores, or proof that a branch is more current. Branches remain read-only historical inputs. The next version is based on the fetched master baseline, not a blind cherry-pick of an older README.

## Comparative version identity

Every published README candidate should be identifiable by this tuple:

(base_ref, base_sha, candidate_ref, candidate_sha, README_blob_sha, policy_version, seed, scope)

Record at least:

- exact base and candidate commit SHAs;
- README blob SHA;
- line/byte delta and changed-line ratio;
- headings, links, image references, and Mermaid diagrams added/removed;
- mapping-source references used;
- validation outcomes and known gaps;
- any over-budget reason.

A branch name alone is not a version identity; branches move. A commit SHA and blob SHA are immutable comparison anchors.

## Visual and semantic acceptance

- README remains readable without a private CID/pointer registry.
- Canonical mappings are linked to their existing source; no duplicate mapping tables are introduced.
- Markdown headings, links, code fences, inline code, URLs, paths, numbers, and identifiers remain intact.
- Mermaid diagrams describe actual source/flow boundaries and are not presented as runtime telemetry.
- Existing screenshots and visual assets are retained unless a replacement is verified.
- Branch comparisons are read-only; no force-push or branch overwrite.
- git diff --check, focused tests, scripts/ci/repo_gate.py, and scripts/ci/termux_smoke.py remain separate validation outcomes. Byte counts are measured from the exact UTF-8 Git blob bytes; text-mode newline normalization is not permitted.

## Scope and exclusions

Eligible related surfaces:

- README.md, .gitattributes, CLAUDE.hum.md;
- docs/linguist/, docs/ops/LINGUIST-PANEL-FEED.md;
- docs/proposals/active/notation-sets/;
- scripts/linguist/;
- workspace/compression_sandbox/cedrlang/;
- harmony_hub/config/grimoire/;
- apps/tribute-dashboard/linguist.html.

Generated feeds, session stores, caches, credentials, private pointer indexes, and unrelated application files are excluded. A file is included only when the update is directly relevant to the Linguist/README projection.

## Relationship to existing visuals

The repository already has a Linguist Panel and feed pipeline. This work links and improves the discovery path; it does not replace the panel, regenerate its data by hand, or create a competing visualization system.
