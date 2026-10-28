# Research Triggers — existing set (recon) + issue-trigger expansion

`[MUSEai]@{role:{research-triggers}}` — recon verified firsthand via the PAT
API on master (2026-10-28); expansion landed with this doc.

## Scope (owner, restored 2026-10-28)

The existing set is the research-trigger set **as a whole** — the anchors in
the table below (recon-intel-discovery, research-seeds {seed}{starter},
Repository Observatory signals, provider-recon-compound, research-registry),
not any single member. An earlier amendment narrowing the scope to the
Observatory alone was reversed by the owner the same day. The Observatory
intake wiring landed by that amendment (PR #2061: `observatory_intake.py`,
provenance `issue`) **stays** — it is the service/repository leg of this set —
but routing is the full-set routing below, not Observatory-only.

## Existing set — what fires today, on what, producing what

| Trigger | Event(s) | Input | Produces |
|---|---|---|---|
| `repository-observatory.yml` | schedule daily 04:17 UTC + `workflow_dispatch` | owner's owned/starred/watched repos, forks as role flag (`scripts/github/repository_observatory.py --watching`) | `workspace/llm_map/repositories/repository-index.json` + `docs/repositories/matrix.md`, committed to master. Starred/forked/watched = research **signals**, never adoption orders |
| `docs/repositories/research-seeds/*.json` | none (static files, written by research passes) | `{seed}{starter}` schema v1.0: `seed_id`, `canonical_upstream`, `provenance`, `classification{domains,research_value,integration_mode,adoption}`, `observed_facts`, `capability_signals`, `integration_constraints` | seed records consumed by recon/RFP passes (occupants: `getdx.json` evidence-pending, `gravitee-api-management.json`, `temporalio-temporal-set.json`) |
| `recon-intel-discovery.yml` | `pull_request` + `pull_request_target` [opened, synchronize, ready_for_review, reopened] + `workflow_dispatch` (cadence owned by quota-dispatch-tree, #1573) | PR head SHA / GitLab `master` ref | GitHub–GitLab ancestry classification + `RECON INTEL lease` check run; metadata-only, read-only, no writes |
| `provider-recon-compound.yml` | `workflow_run` (OpenRouter free catalog completed) + `workflow_dispatch` + `pull_request` (paths, tests only) | pinned upstream GitHub sources | provider-recon snapshot + Cadence plan artifacts; publisher opens one refresh PR touching only `data/model-selection-market/provider-recon.json` |
| `research-registry.yml` | `pull_request` + `push` to master (paths `docs/research/**`, digest sources, validator) | research registry files | validation only (no record produced) |
| Precedent issue triggers (same pattern, other pipelines) | `delphi-gate` via issue label `delphi:rfp` (template `delphi-rfp.yml`); `target-intake.yml` via `issues` [opened, edited, reopened] + label `target-brief` (template `target-brief.yml`); `delphi-intake.yml` via `issue_comment` marker `<!-- request-delphi-intake -->` | issue form fields / comment `key: value` lines | finished RFP issue / taxonomy dispatch-plan comment |

Gap closed here: research had **no** issue trigger — providers/services entered
only via Observatory signals, scheduled/PR recon, or a hand-written seed file.

## Expansion 1 — issue triggers (`research-intake.yml`)

Events: `issues` [opened, labeled, reopened] and `issue_comment` [created].
No `pull_request_target` (Nov-2 rules; the 8 audited fleet files are untouched).
Permissions: top-level `{}`, job `contents: read` + `issues: write` only;
trusted default-branch checkout; body treated as data, never executed.

- Label gate (fleet colon convention, cf. `delphi:rfp`): `research:provider`,
  `research:service`, or the pre-existing umbrella label `research`
  (opened/reopened, or a `research*` label being added).
- Comment command (delphi-intake precedent, marker-gated, bot-safe):
  a comment containing `<!-- request-research -->` plus `key: value` lines
  (`kind:, id:, name:, url:, upstream:, category:, signal:, quota:, auth:, evidence:`).
- Parser: `scripts/research/research_intake.py` (stdlib, deterministic, tests
  `tests/test_research_intake.py`). Emits the seed/starter record as a comment
  on the issue — the same record shape the pipelines below consume.
- Routing (full set): provider → provider-recon-compound / provider-availability /
  `ops/quota/registry.json` (+ delphi-gate if it becomes a free-tier surface);
  service → repository-observatory (incl. the #2061 intake leg) /
  `docs/repositories/research-seeds/` / research-registry /
  `docs/repositories/matrix.md`.
- Secrets: none used, none invented. The `auth` field carries an Actions
  secret **NAME** only (phantom-secrets inventory / issue #184); a value-shaped
  string refuses the intake (exit 2, refusal comment).

Labels `research:provider` + `research:service` were created on the repo with
this expansion (the umbrella `research` label pre-existed).

## Expansion 2 — issue templates (`.github/ISSUE_TEMPLATE/`)

| Template | Labels applied | Fields → pipeline inputs |
|---|---|---|
| `research-provider.yml` | `research`, `research:provider` | provider_id→`seed_id`, provider_name, category→`classification.domains`, url→`canonical_upstream` fallback, free quota→`observed_facts.free_quota`, auth→`observed_facts.auth_secret_name` (name only), capability signals, scoped question, evidence |
| `research-service.yml` | `research`, `research:service` | service_id, service_name, upstream repository→`seed_id` (`github:research-seed:<owner/repo>`, exact research-seeds schema), service URL, observatory signal→`provenance: observatory-signal:<signal>`, category, capability signals, scoped question, evidence |

Filing either template applies the label that wakes `research-intake`, so
filing an issue **is** the trigger — no cron, no manual dispatch.
