# Cross-Plane Graph — projection (additional view)

> Canonical data: `workspace/llm_map/graph/edges.jsonl` + `graph-index.json`, derived by `scripts/graph/cross_plane_link.py` from the plane indexes. This is a view over existing planes, never a source of truth; signals are research signals, never adoption orders.

Observed (repository index): `2026-10-29T10:55:52.286678Z` · Edges: **25179**

## Edges by type

- **about_topic:** 12312
- **in_domain:** 5196
- **authored_by:** 3639
- **starred:** 3185
- **owned:** 696
- **watching:** 128
- **mentions_repo:** 20
- **upstream:** 2
- **fork_of:** 1

## Cross-plane / seed edges

| Src | Type | Dst | Method |
|---|---|---|---|
| `github:repository:timerloggedout-spec/gravitee-api-management_fork` | fork_of | `github:repository:gravitee-io/gravitee-api-management` | seed_local_fork+fork_parent |
| `github:research-seed:frappe/gantt` | in_domain | `domain:developer-experience` | classification_domains |
| `github:research-seed:frappe/gantt` | mentions_repo | `github:repository:frappe/gantt` | issue_intake_upstream |
| `github:research-seed:frappe/gantt` | upstream | `github:repository:frappe/gantt` | seed_canonical_upstream |
| `github:research-seed:gravitee-io/gravitee-api-management` | in_domain | `domain:api-management` | classification_domains |
| `github:research-seed:gravitee-io/gravitee-api-management` | in_domain | `domain:developer-portal` | classification_domains |
| `github:research-seed:gravitee-io/gravitee-api-management` | in_domain | `domain:gateway` | classification_domains |
| `github:research-seed:gravitee-io/gravitee-api-management` | in_domain | `domain:kubernetes` | classification_domains |
| `github:research-seed:gravitee-io/gravitee-api-management` | in_domain | `domain:platform` | classification_domains |
| `github:research-seed:gravitee-io/gravitee-api-management` | mentions_repo | `github:repository:gravitee-io/gravitee-api-management` | issue_intake_upstream |
| `github:research-seed:gravitee-io/gravitee-api-management` | upstream | `github:repository:gravitee-io/gravitee-api-management` | seed_canonical_upstream |
| `github:research-seed:temporalio/temporal-set` | in_domain | `domain:agent-infrastructure` | classification_domains |
| `github:research-seed:temporalio/temporal-set` | in_domain | `domain:durable-execution` | classification_domains |
| `github:research-seed:temporalio/temporal-set` | in_domain | `domain:workflow-orchestration` | classification_domains |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/ai-cookbook` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/ai-integrations` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/api` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/awesome-temporal` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/cli` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/cloud-operator` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/cruise-control-api` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/kube-temporal` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/nexgen` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/omes` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/pi-temporal` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/public-actions` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/skill-temporal-serverless` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/temporal` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/temporal-auto-scaled-workers` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/temporal-worker-controller` | seed_repos_list |
| `github:research-seed:temporalio/temporal-set` | mentions_repo | `github:repository:temporalio/ui` | seed_repos_list |
| `github:research-seed:timerloggedout-spec/termux-monorepo` | mentions_repo | `github:repository:timerloggedout-spec/termux-monorepo` | issue_intake_upstream |
| `research-seed:getdx` | in_domain | `domain:developer-experience` | classification_domains |
| `research-seed:getdx` | in_domain | `domain:measurement` | classification_domains |
