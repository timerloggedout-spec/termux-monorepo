# GitLab AI Hackathon — Opportunity and OSINT Source Dossier

**Observed:** 2026-11-22  
**Owning lane:** challenge-entries / Challenge OSINT  
**Disposition:** historical event family + future-cycle watchlist  
**Access boundary:** public, signed-out pages and the connected Devpost event connector  
**Owner account/onboarding state:** NOT_ESTABLISHED; this dossier records public-source observations only. Community Hackathon Devpost registration: NOT_REQUIRED.

## 1. Source interpretation

The supplied URLs identify GitLab group hierarchy:

- [GitLab AI Hackathon](https://gitlab.com/gitlab-ai-hackathon) is the public root group.
- [GitLab DevSecOps Flow Hackathon](https://gitlab.com/gitlab-ai-hackathon/gitlab-devsecops-flow-hackathon) resolves to a **subgroup** rather than a project. Its public subgroup page showed **zero child projects and zero child subgroups** at observation time. The root group listing associates it with group ID `126794830`.
- [Transcend](https://gitlab.com/gitlab-ai-hackathon/transcend) is a sibling subgroup created 2026-05-18; it is active (archived=false), with **312 public projects and zero child subgroups**. Project descriptions reference Transcend showcase workspaces, while exact event-cycle mapping remains `NOT_ESTABLISHED`. Its dated metadata snapshot is `ops/challenge/osint/gitlab-transcend-projects-2026-11-22.json`.
- [Transcend October 2026](https://gitlab.com/groups/gitlab-ai-hackathon/transcend-october-2026) is a separate archived subgroup (group ID `142538134`). It contains **1,273 participant subgroups and 1,820 public archived projects**. The owner-published group boundary keeps observability disabled at group scope and keeps secrets out of group-level settings. Dated subgroup and project indexes are `ops/challenge/osint/gitlab-transcend-october-2026-subgroups-2026-11-22.ndjson` and `ops/challenge/osint/gitlab-transcend-october-2026-projects-2026-11-22.ndjson`.
- [Project Templates](https://gitlab.com/gitlab-ai-hackathon/project-templates) is another subgroup. It contains the public [Participant Template](https://gitlab.com/gitlab-ai-hackathon/project-templates/participant-template) project (project ID `77423853`), with `agents/`, `flows/`, `LICENSE`, and `README.md`.

### Other first-level root-group children

The root group listing showed **seven subgroups and three direct projects**:

- `participants-test-lee` — subgroup with 2 child projects.
- `participants-test-mattias` — subgroup with 24 child projects.
- `test` — subgroup with one CI component test project.
- `transcend-october-2026` — archived October 2026 showcase subgroup with 1,273 child participant subgroups and 1,820 public archived projects.
- Direct project `ci` (ID `77418162`) — contains `agents/`, `.gitlab-ci.yml`, `LICENSE`, and `README.md`; its README describes CI configuration for participant projects, enforced by the Security Policies project.
- Direct project `gitlab-profile` — README points participants to the Devpost GitLab AI Hackathon page.
- Direct project `security-policies` (ID `77418381`) — contains `.gitlab/security-policies`, `LICENSE`, and `README.md`.

The participant-test groups and shared CI/security-policy projects remain distinct from both Transcend project catalogs.

### Sibling Transcend subgroup catalog snapshot — event cycle NOT_ESTABLISHED

The public GitLab REST API returned **312 unique public projects** across four pages (100 + 100 + 100 + 12); the subgroup API returned zero child subgroups. The group was created 2026-05-18 and remains active. Project descriptions reference Transcend showcase workspaces, while exact event-cycle mapping remains NOT_ESTABLISHED. The dated snapshot stores project ID, namespace path, project URL, README URL, creation/activity timestamps, star count, visibility, archive state, and default branch. Contributor/member identities are excluded.

Snapshot: `ops/challenge/osint/gitlab-transcend-projects-2026-11-22.json`. Treat it as a dated observation; refresh through bounded pagination and retain each dated snapshot for change analysis.

The supplied DevSecOps Flow URL is therefore retained as a first-class **group/subgroup source**. Its timestamped empty child listing records the observed public state; future subgroup activity and any challenge specification remain unassessed.

## 2. Distinct GitLab competition programs

Treat these as separate events/programs. Their rules, dates, registration states, and outcome records remain independent.

### 2.1 GitLab AI Hackathon — “You Orchestrate. AI Accelerates.”

- Devpost: [event](https://gitlab.devpost.com/) · [official rules](https://gitlab.devpost.com/rules) · [dates](https://gitlab.devpost.com/details/dates) · [resources](https://gitlab.devpost.com/resources) · [updates](https://gitlab.devpost.com/updates)
- Submission window: **2026-02-09 10:00 ET – 2026-03-25 14:00 ET**.
- Judging: **2026-03-30 – 2026-04-17**; winners announced **2026-04-22 14:00 ET**. The rules give the judging window as 10:00 ET start / 17:00 ET end; the connector's structured dates differ on the start instant (15:45Z). Preserve this source discrepancy for a future raw-page reconciliation.
- Current phase: **closed** (Devpost connector, fetched 2026-11-22).
- Published prize pool: **$65,000**.
- Participant count discrepancy: the public event page displayed **6,920**; the connector's search listing returned **6,922**. Preserve both source observations.
- Sponsor: GitLab; Google Cloud and Anthropic category prizes.
- Core brief: working GitLab Duo Agent Platform agent or flow that automates a specific SDLC action; chat-only responses fall outside the published requirement.
- Minimum submission shape: public project in the GitLab AI Hackathon group, working implementation, explanatory text, public demo video under three minutes, and appropriate open-source licensing.
- Original entrant work and agent configuration are subject to the MIT license and GitLab DCO 1.1; third-party components must use OSI-approved licenses with compatible notices.
- Eligibility includes age of majority; the official rules contain geographic and conflict exclusions. Use the official rules as the authority for any future-cycle eligibility decision.

The connector's prize catalogue totals $65,000. The official rules enumerate the Grand Prize, technical/impact/ease-of-use awards, honorable mentions, sustainable-design bonus, and GitLab + Google / GitLab + Anthropic category awards. Preserve each award tier separately rather than flattening the award list into one generic prize.

### 2.2 GitLab Transcend — “Life After Code” (October 2026)

- Devpost: [event](https://gitlab-transcend.devpost.com/) · [official rules](https://gitlab-transcend.devpost.com/rules).
- Registration: **2026-09-29 10:00 UTC – 2026-10-27 13:00 UTC**.
- Submissions: **2026-10-05 17:00 UTC – 2026-10-27 13:00 UTC**.
- Judging: rules state **2026-10-28 10:00 UTC – 2026-11-14 17:00 UTC**; the connector's structured date record reports **2026-10-28 09:00 UTC – 2026-11-16 23:45 UTC**.
- Devpost page displays **3,313 participants**. The October showcase group is `transcend-october-2026` (1,273 child subgroups / 1,820 public archived projects); the sibling `transcend` group has 312 active public projects with event-cycle mapping `NOT_ESTABLISHED`.
- Devpost connector reports winners announced **2026-11-18 17:00:41 UTC**; the rules text says “on or around November 16”. Preserve both judging-window and winner-date values as source discrepancies; retain each source's timestamped value.
- Current phase: **closed** (fetched 2026-11-22).
- Prize pool: **$45,000**.
- Theme: agents and flows that automate post-code DevSecOps lifecycle stages, including review, security scanning, testing, compliance, deployment, and monitoring.
- Judging criteria: Technological Implementation, Design, Potential Impact, Innovation / Idea, and Presentation.

Keep the archived `transcend-october-2026` workspace corpus as the October 2026 event source. Keep the active sibling `transcend` catalog as a separate 312-project source with event-cycle mapping NOT_ESTABLISHED.

### 2.3 GitLab Community Hackathon — October 2026 history + January 2027 upcoming edition

- Official event surface: [Contributor Platform hackathon](https://contributors.gitlab.com/hackathon) · [current rules](https://contributors.gitlab.com/docs/hackathon-rules) · [October announcement](https://forum.gitlab.com/t/our-next-gitlab-hackathon-starts-october-6th/135317).
- October 2026 edition: **2026-10-06 – 2026-10-12 UTC**; qualifying MRs merged within 31 days (cutoff Nov 12). The current page reports 76 prize winners and 636 merged MRs for that edition.
- **Next edition: January 21–28, 2027**. The page says the hackathon runs in UTC and displays a live countdown to January 21; page text supplies date-only boundaries; exact start/end clock times remain NOT_ESTABLISHED.
- Reward model: first place 200 Contributor Success store credits; second 150; third 100; 50 credits for each participant with a qualifying merged MR. Cash component: NONE_LISTED.
- Current live rules version: **2026-10-v2**; the search-index copy returned **2026-10-v1**. Preserve the version discrepancy. Requirements include maximum 20 MRs and 20 issues per day; issue assignment before MR; AI tools allowed with contributor review/testing responsibility; scripted/automated/programmatic labeling is prohibited; one typo-fix MR per project; and first-time-contributor quick-win restrictions.
- This contribution/leaderboard program is distinct from the Devpost AI-agent competition. January 2027 is **upcoming**; the owner's onboarding/registration and issue assignment remain NOT_ESTABLISHED.

## 3. Discord and onboarding sources

The official event page directs participants to the GitLab Community Discord `#ai-hackathon`, requests access to the GitLab AI Hackathon group, and links custom-agent/custom-flow tutorials plus the prompt library. Discord message content remains UNCOLLECTED; the invite and channel references are indexed. It states that group access requests closed on **2026-03-25 09:00 ET**. The event resource page links the Devpost Discord for team formation and states that office-hours scheduling is posted in Discord.

- [GitLab Discord invite](https://discord.com/invite/gitlab) — `#ai-hackathon` for the Devpost AI Hackathon; current Community Hackathon rules direct questions to `#hackathon` or `#contribute`; Transcend sample workspaces use `#transcend-hackathon`.
- [Devpost Discord](https://info.devpost.com/blog/join-the-devpost-discord).
- Office-hours schedule: posted in the relevant GitLab Discord channels; individual session dates are NOT_ESTABLISHED in this public-source pass.
- For the Community Hackathon, the official forum announcement states **Devpost registration: NOT_REQUIRED**. Entry uses Contributor Platform rule acceptance and onboarding at [contributors.gitlab.com/start](https://contributors.gitlab.com/start).
- The [Participant Template README](https://gitlab.com/gitlab-ai-hackathon/project-templates/participant-template) links to a `work_items/1` onboarding item. The public item is currently **unavailable**; its instructions remain NOT_ESTABLISHED.
- An [October 2026 Transcend workspace onboarding issue](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/621485/showcase/-/work_items/1) confirms participant subgroup/project provisioning and directs contributors to the Transcend guide, `#transcend-hackathon`, and office hours. The issue describes optional observability within each participant subgroup; the parent group's published boundary keeps observability disabled at group scope and keeps secrets out of group-level settings. The sample workspace and parent group are archived/read-only.
- The public event page links an example participant issue at [participants/621485](https://gitlab.com/gitlab-ai-hackathon/participants/621485/-/issues/1).

## 4. Reusable technical references

- [Participant Template](https://gitlab.com/gitlab-ai-hackathon/project-templates/participant-template) — public starter repository with `agents/` and `flows/` directories.
- [GitLab Duo Agent documentation](https://docs.gitlab.com/user/duo_agent_platform/agents/).
- [GitLab Duo Flow documentation](https://docs.gitlab.com/user/duo_agent_platform/flows/).
- [Agent tools documentation](https://docs.gitlab.com/user/duo_agent_platform/agents/tools/).
- [GitLab Duo prompt library](https://about.gitlab.com/gitlab-duo/prompt-library/).
- [Complete getting-started guide](https://about.gitlab.com/blog/gitlab-duo-agent-platform-complete-getting-started-guide/).
- [Flow schema reference](https://gitlab.com/gitlab-org/modelops/applied-ml/code-suggestions/ai-assist/-/blob/main/docs/flow_registry/v1.md).

The reusable template is recorded metadata-first under `refTemplates/12_External_Agents/gitlab-duo-agent-platform/`. It is a metadata-only reference; runtime pin/dependency state: absent.

## 5. Observatory and registration disposition

1. Keep the root group, supplied DevSecOps Flow subgroup, sibling Transcend subgroup, archived Transcend October 2026 subgroup, Project Templates subgroup, and Participant Template as distinct URL-addressed source nodes.
2. Keep the three competition programs above as distinct event records/watch targets.
3. Record the supplied subgroup's empty state with its observation time. Recheck its child listing on future source sweeps.
4. Use public project pages, official Devpost pages, official announcements, and public GitLab group/project pages for competitor/project OSINT. Store URL + fetch timestamp + coverage state for every populated fact.
5. Treat official event placement, directory position, displayed engagement, and internal analytical ranking as separate dimensions.
6. Keep participant/persona collection public-source-only. External participants remain observation-only; recruitment is for our own team.
7. Registration, account access, group membership, project creation, and submission are separate states. Owner onboarding, rule acceptance, group membership, project creation, and submission: **NOT_ESTABLISHED**; Community Hackathon Devpost registration: **NOT_REQUIRED**.
8. The February–March 2026 GitLab AI Hackathon and October 2026 Life After Code / Transcend edition are closed; their next-cycle dates are **NOT_ESTABLISHED**. The GitLab Community Hackathon has a published upcoming edition for **January 21–28, 2027** and is added as candidate **C17**. Owner onboarding, rule acceptance, issue assignment, and contribution state: **NOT_ESTABLISHED**; Devpost registration: **NOT_REQUIRED**.

Machine-readable URL/source inventory: [`ops/challenge/osint/gitlab-sources.json`](../../ops/challenge/osint/gitlab-sources.json).

## 6. Ownership and implementation boundary

- Challenge log and event/registration facts: challenge-entries lane, single writer.
- Public source observations and page-hash history: Challenge OSINT lane.
- Devpost event/account observations: Devpost connector; global GitLab group/project hierarchy: bounded public-page adapter.
- Cross-plane graph: derived/read-only links from canonical event and source records.
- Reference template: metadata-only `refTemplates` entry until a separately reviewed runtime dependency is justified.

The existing Devpost Observatory expansion specifies the adapter boundary and BEFORE / DURING / AFTER lifecycle. This dossier supplies the GitLab source family and a concrete hierarchy fixture. Collector, schedule, graph edge, and automated registration workflow status: UNIMPLEMENTED / UNOBSERVED.
