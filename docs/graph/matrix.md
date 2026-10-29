# Cross-Plane Graph — projection (additional view)

> Canonical data: `workspace/llm_map/graph/edges.jsonl` + `graph-index.json`, derived by `scripts/graph/cross_plane_link.py` from the plane indexes. This is a view over existing planes, never a source of truth; signals are research signals, never adoption orders.

Observed (repository index): `2026-10-29T10:55:52.286678Z` · Edges: **25205**

## Edges by type

- **about_topic:** 12312
- **in_domain:** 5196
- **authored_by:** 3639
- **starred:** 3185
- **owned:** 696
- **watching:** 128
- **mentions_repo:** 20
- **submitted_to:** 14
- **organizes:** 9
- **upstream:** 2
- **competes_in:** 1
- **entered_with:** 1
- **same_author_as:** 1
- **fork_of:** 1

## Challenge event field size (platform-displayed)

Tracked participant records in coordinator.json: **1** — distinct from the field sizes below.

| Event node | Participants | Projects | Status |
|---|---|---|---|
| `challenge:event:D0` | 252 | 40 | established |
| `challenge:event:D1` | 324 | 1 | partial |
| `challenge:event:D2` | 1617 | None | partial |
| `challenge:event:D3` | None | None | open_task |
| `challenge:event:D4` | 1909 | 0 | established |
| `challenge:event:D5` | None | None | open_task |
| `challenge:event:STRANDS-DECIDER` | 5917 | None | partial |

## Cross-plane / seed / challenge edges

| Src | Type | Dst | Method |
|---|---|---|---|
| `challenge:organizer:aha` | organizes | `challenge:event:D5` | organizer_role_host |
| `challenge:organizer:aws-builder-center-amazon-web-services` | organizes | `challenge:event:D0` | organizer_role_host |
| `challenge:organizer:aws-builder-center-amazon-web-services` | organizes | `challenge:event:D1` | organizer_role_host |
| `challenge:organizer:aws-builder-center-amazon-web-services` | organizes | `challenge:event:STRANDS-DECIDER` | organizer_role_host |
| `challenge:organizer:builder-io` | organizes | `challenge:event:D3` | organizer_role_host |
| `challenge:organizer:devpost` | organizes | `challenge:event:D4` | organizer_role_platform |
| `challenge:organizer:kiro` | organizes | `challenge:event:D4` | organizer_role_host |
| `challenge:organizer:lablab-ai` | organizes | `challenge:event:D2` | organizer_role_host |
| `challenge:organizer:vultr` | organizes | `challenge:event:D2` | organizer_role_sponsor |
| `challenge:participant:D1/ladder-practice-sets` | competes_in | `challenge:event:D1` | event_participants_list |
| `challenge:participant:D1/ladder-practice-sets` | entered_with | `challenge:project:D1/ladder-practice-sets-a-teacher-can-trust` | participant_project |
| `challenge:participant:D1/ladder-practice-sets` | same_author_as | `github:user:abhinavshukla152005-beep` | participant_public_links_github_explicit |
| `challenge:project:D0/delphi-oracle-weekend-challenge-completion-package` | submitted_to | `challenge:event:D0` | project_of_event |
| `challenge:project:D1/ladder-practice-sets-a-teacher-can-trust` | submitted_to | `challenge:event:D1` | project_of_event |
| `challenge:project:D1/proof-before-help` | submitted_to | `challenge:event:D1` | project_of_event |
| `challenge:project:D1/strands-rfp-response-strategy-43-kernel-first` | submitted_to | `challenge:event:D1` | project_of_event |
| `challenge:project:D1/strands-rfp-response-strategy-44-collection-first` | submitted_to | `challenge:event:D1` | project_of_event |
| `challenge:project:D1/strands-rfp-response-strategy-45-packaging-first` | submitted_to | `challenge:event:D1` | project_of_event |
| `challenge:project:D1/studysprint` | submitted_to | `challenge:event:D1` | project_of_event |
| `challenge:project:D2/web-adapter-foundry-sandboxed-browser-operating-agent` | submitted_to | `challenge:event:D2` | project_of_event |
| `challenge:project:D3/delphi-desk` | submitted_to | `challenge:event:D3` | project_of_event |
| `challenge:project:D3/listinglens` | submitted_to | `challenge:event:D3` | project_of_event |
| `challenge:project:D4/kiroween-variant-frankenstein` | submitted_to | `challenge:event:D4` | project_of_event |
| `challenge:project:D4/kiroween-variant-resurrection` | submitted_to | `challenge:event:D4` | project_of_event |
| `challenge:project:D4/kiroween-variant-skeleton-crew` | submitted_to | `challenge:event:D4` | project_of_event |
| `challenge:project:STRANDS-DECIDER/delphi-oracle-strands-decider-proposal-package` | submitted_to | `challenge:event:STRANDS-DECIDER` | project_of_event |
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
