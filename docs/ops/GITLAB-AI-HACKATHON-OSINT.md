# GitLab AI Hackathon — Opportunity and OSINT Source Dossier

**Observed:** 2026-11-22  
**Owning lane:** challenge-entries / Challenge OSINT  
**Disposition:** historical event family + future-cycle watchlist  
**Access boundary:** public, signed-out pages and the connected Devpost event connector  
**Owner registration/submission:** NOT_ESTABLISHED; this dossier records public-source observations only

## 1. Source interpretation

The supplied URLs identify GitLab group hierarchy:

- [GitLab AI Hackathon](https://gitlab.com/gitlab-ai-hackathon) is the public root group.
- [GitLab DevSecOps Flow Hackathon](https://gitlab.com/gitlab-ai-hackathon/gitlab-devsecops-flow-hackathon) resolves to a **subgroup** rather than a project. Its public subgroup page showed **zero child projects and zero child subgroups** at observation time. The root group listing associates it with group ID `126794830`.
- [Transcend](https://gitlab.com/gitlab-ai-hackathon/transcend) is a separate subgroup under the root. Its subgroup API returned **312 public project workspaces across four pages** and zero child subgroups at observation time. The dated metadata snapshot is `ops/challenge/osint/gitlab-transcend-projects-2026-11-22.json`.
- [Project Templates](https://gitlab.com/gitlab-ai-hackathon/project-templates) is another subgroup. It contains the public [Participant Template](https://gitlab.com/gitlab-ai-hackathon/project-templates/participant-template) project (project ID `77423853`), with `agents/`, `flows/`, `LICENSE`, and `README.md`.

### Transcend workspace catalog snapshot

The public GitLab REST API returned **312 unique public projects** across four pages (100 + 100 + 100 + 12); the subgroup API returned zero child subgroups. The dated snapshot stores project ID, namespace path, project URL, README URL, creation/activity timestamps, star count, visibility, archive state, and default branch. Contributor/member identities are excluded.

Snapshot: `ops/challenge/osint/gitlab-transcend-projects-2026-11-22.json`. Treat it as a dated observation; refresh through bounded pagination and retain each dated snapshot for change analysis.
- [GitLab Profile README](https://gitlab.com/gitlab-ai-hackathon/gitlab-profile/-/blob/main/README.md) points participants to the Devpost GitLab AI Hackathon page.

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
- Devpost connector reports winners announced **2026-11-18 17:00:41 UTC**; the rules text says “on or around November 16”. Preserve both judging-window and winner-date values as source discrepancies; retain each source's timestamped value.
- Current phase: **closed** (fetched 2026-11-22).
- Prize pool: **$45,000**.
- Theme: agents and flows that automate post-code DevSecOps lifecycle stages, including review, security scanning, testing, compliance, deployment, and monitoring.
- Judging criteria: Technological Implementation, Design, Potential Impact, Innovation / Idea, and Presentation.

The Transcend subgroup is related to the same GitLab AI Hackathon root but represents a distinct event program and workspace collection. Keep it separate from the February–March event record.

### 2.3 GitLab Community Hackathon — October 2026 history + January 2027 upcoming edition

- Official event surface: [Contributor Platform hackathon](https://contributors.gitlab.com/hackathon) · [current rules](https://contributors.gitlab.com/docs/hackathon-rules) · [October announcement](https://forum.gitlab.com/t/our-next-gitlab-hackathon-starts-october-6th/135317).
- October 2026 edition: **2026-10-06 – 2026-10-12 UTC**; qualifying MRs merged within 31 days (cutoff Nov 12). The current page reports 76 prize winners and 636 merged MRs for that edition.
- **Next edition: January 21–28, 2027**. The page says the hackathon runs in UTC and displays a live countdown to January 21; page text supplies date-only boundaries; exact start/end clock times remain NOT_ESTABLISHED.
- Reward model: first place 200 Contributor Success store credits; second 150; third 100; 50 credits for each participant with a qualifying merged MR. Cash component: NONE_LISTED.
- Current rules version: **2026-10-v2**. Requirements include maximum 20 MRs and 20 issues per day; issue assignment before MR; AI tools allowed with contributor review/testing responsibility; scripted/automated/programmatic labeling is prohibited; one typo-fix MR per project; and first-time-contributor quick-win restrictions.
- This contribution/leaderboard program is distinct from the Devpost AI-agent competition. January 2027 is **upcoming**; the owner's onboarding/registration and issue assignment remain NOT_ESTABLISHED.

## 3. Discord and onboarding sources

The official event page directs participants to the GitLab Community Discord `#ai-hackathon`, requests access to the GitLab AI Hackathon group, and links custom-agent/custom-flow tutorials plus the prompt library. It states that group access requests closed on **2026-03-25 09:00 ET**. The event resource page links the Devpost Discord for team formation and states that office-hours scheduling is posted in Discord.

- [GitLab Discord invite](https://discord.com/invite/gitlab) — `#ai-hackathon` for the Devpost AI Hackathon; current Community Hackathon rules direct questions to `#hackathon` or `#contribute`; Transcend sample workspaces use `#transcend-hackathon`.
- [Devpost Discord](https://info.devpost.com/blog/join-the-devpost-discord).
- Office-hours schedule: posted in the relevant GitLab Discord channels; individual session dates are NOT_ESTABLISHED in this public-source pass.
- The [Participant Template README](https://gitlab.com/gitlab-ai-hackathon/project-templates/participant-template) links to a `work_items/1` onboarding item. The public item is currently **unavailable**; its instructions remain NOT_ESTABLISHED.
- A representative [Transcend showcase workspace onboarding issue](https://gitlab.com/gitlab-ai-hackathon/transcend/27098937/-/work_items/1) directs the workspace owner to the Showcase Track guide, `#transcend-hackathon`, and office hours. This sample workspace onboarding record illustrates one Transcend workspace path; event-wide AI Hackathon registration remains governed by the official Devpost event page.
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

1. Keep the root group, supplied DevSecOps Flow subgroup, Transcend subgroup, Project Templates subgroup, and Participant Template as distinct URL-addressed source nodes.
2. Keep the three competition programs above as distinct event records/watch targets.
3. Record the supplied subgroup's empty state with its observation time. Recheck its child listing on future source sweeps.
4. Use public project pages, official Devpost pages, official announcements, and public GitLab group/project pages for competitor/project OSINT. Store URL + fetch timestamp + coverage state for every populated fact.
5. Treat official event placement, directory position, displayed engagement, and internal analytical ranking as separate dimensions.
6. Keep participant/persona collection public-source-only. External participants remain observation-only; recruitment is for our own team.
7. Registration, account access, group membership, project creation, and submission are separate states. This dossier records **none** of those owner actions as completed.
8. The February–March 2026 GitLab AI Hackathon and October 2026 Life After Code / Transcend edition are closed; their next-cycle dates are **NOT_ESTABLISHED**. The GitLab Community Hackathon has a published upcoming edition for **January 21–28, 2027** and is added as candidate **C17**. Owner onboarding, registration, issue assignment, and contribution state remain **NOT_ESTABLISHED**.

Machine-readable URL/source inventory: [`ops/challenge/osint/gitlab-sources.json`](../../ops/challenge/osint/gitlab-sources.json).

## 6. Ownership and implementation boundary

- Challenge log and event/registration facts: challenge-entries lane, single writer.
- Public source observations and page-hash history: Challenge OSINT lane.
- Devpost event/account observations: Devpost connector; global GitLab group/project hierarchy: bounded public-page adapter.
- Cross-plane graph: derived/read-only links from canonical event and source records.
- Reference template: metadata-only `refTemplates` entry until a separately reviewed runtime dependency is justified.

The existing Devpost Observatory expansion specifies the adapter boundary and BEFORE / DURING / AFTER lifecycle. This dossier supplies the GitLab source family and a concrete hierarchy fixture. Collector, schedule, graph edge, and automated registration workflow status: UNIMPLEMENTED / UNOBSERVED.
