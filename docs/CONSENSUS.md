# Consensus & Voting Rules (ArchW1z)

Multi-agent agreement without theater. Inspired by **Raft** ideas (terms, majority, single leader per term, log as source of truth) — **not** a full Raft implementation. We do not run elections over the network; we use the metaphors for clarity.

Related: `docs/proposals/PROCESS.md` · `docs/PR-SUMMARY-PROCESS.md` · `AGENTS.md`

---

## 1. What “consensus” means here

| Concept | Raft analogue | ArchW1z meaning |
|---------|---------------|-----------------|
| **Term** | Monotonic term number | A decision window on one *subject* (one proposal item, one PR disposition, one summary version) |
| **Leader** | Elected leader | **Driver** for that term — agent or human who proposes the binding write |
| **Log** | Replicated log | GitHub PR comment / MANIFEST Review log / `PR-SUMMARY-LOG.md` / registry.yaml |
| **Commit** | Majority-replicated entry | Decision is **committed** only when written to the log *and* vote threshold met |
| **Follower** | Applies leader’s log | Other agents may ack, dissent, or stay silent per rules below |
| **Split vote** | New election | Escalate to Operator or open a new term with clearer options |

**Unposted chat is not a log entry.** Same rule as proposals.

---

## 2. Subjects & vote thresholds

Votes are **per subject**, not global popularity contests.

| Subject | Quorum (commit) | Who may vote | Silence |
|---------|-----------------|--------------|---------|
| **P0 item done** (security, credentials, history) | Driver + **≥1 distinct Reviewer accept** *or* Operator accept | Reviewer, Operator | Silence ≠ accept |
| **P0 PR body rewrite** | Driver posts draft in comment → **≥1 other** Reviewer/Operator “summary OK” → then edit body | summary-editor, Reviewer, Operator | Must not apply body before ack |
| **P1 item / PR disposition** | Driver + evidence (+ gates if merge) | Reviewer optional; 1 clear cycle then silence OK | Silence after 1 cycle ≈ no objection |
| **P2–P3 item** | Driver + evidence | Anyone on roster | Silence OK |
| **Proposal `accepted`** | ≥1 **non-author** Reviewer accept *or* Operator self-accept (logged) | Reviewer, Operator | — |
| **Proposal close** | Closer rules in PROCESS.md | Closer role | — |
| **Merge to master-staging** | Gates green + no critical unresolved threads + disposition not 🔴 | Checks are mechanical votes | Failed check = veto |
| **Merge to master** | Same + promotion intent | Operator may require extra human review | — |
| **Force-push / history rewrite** | **Operator only** (explicit issue/PR comment) | Operator | Agents never “majority” this |

### Ballot labels (use in comments)

```text
VOTE: accept     — support commit of the proposed decision
VOTE: reject     — block; must state reason
VOTE: abstain    — present but not counting toward quorum
VOTE: summary OK — ack for P0 PR body rewrite only
```

One vote per **voter id** per **term**. Changing your mind = new comment with `VOTE: …` and higher term note if needed.

---

## 3. Terms (decision windows)

```text
term = <subject-id>/<n>

Examples:
  pr-3/summary/1
  pr-12/disposition/2
  ce-13/history-rewrite/1
  proposal/chatgpt-critical-eval/accept/1
```

- Driver opens a term by posting a proposal in the **log** (PR comment or Review log) including options and recommended Status.
- Commit ends the term; further changes need `…/n+1`.
- **Leader (driver) per term:** first summary-editor or reviewer to post a well-formed term proposal *or* explicit handoff (`DRIVER: <id>`).

No parallel drivers for the same `subject/term` — second writer becomes follower and must `VOTE` or open `term+1` with rationale (Raft-style: one leader per term).

---

## 4. Raft-inspired safety (what we keep)

| Property | Practice |
|----------|----------|
| **Election safety** | At most one *committed* disposition Status per PR at a time (🟢/🟡/🔴/⚪). Conflicting statuses → new term, not silent overwrite. |
| **Leader append-only log** | Prefer appending Review log / summary log rows; do not delete prior disposition history. Body may be rewritten but log retains trail. |
| **Majority of *eligible* voters** | Eligible set is small (roster + Operator), not “everyone on the internet.” For P0, majority of {Driver, Reviewer, Operator} present in the term. |
| **Log matching** | `PR-SUMMARY-LOG.md` and MANIFEST must not contradict the PR body’s Status without a new term. |

What we **do not** implement: heartbeats, randomized election timeouts, network partitions, full log replication state machines.

---

## 5. Consecutive summary rewrites (clarified)

**Question:** Does “three consecutive PR summaries” mean the same PR or three different PRs?

**Answer: three different PRs.**

| Pattern | Allowed? |
|---------|----------|
| Same agent iterates body on **PR #12** three times (fix skills → fix status → retarget note) | **Yes** — same subject, same term or `summary/n+1` |
| Same agent rewrites **#3, then #2, then #6** (three distinct PRs in a row in the log) | Counts as **3 consecutive distinct PR rewrites** |
| Fourth **distinct** PR rewrite by same agent | Hand off to another roster agent or Operator |
| Batch pass in one session on many PRs | Counts per distinct PR number in `PR-SUMMARY-LOG.md` order |

**Iteration on one PR is encouraged** until Status/blockers are accurate. Anti-monopoly exists to force a second *mind* across the queue, not to block editing the same PR.

Log column guidance:

```text
| date | PR | editor | status | notes |
| 2026-08-02 | #12 | grok-archw1z | 🟡 | pass 1 |
| 2026-08-02 | #12 | grok-archw1z | 🟡 | pass 2 — iteration OK, same PR |
```

Same PR rows do **not** increment the consecutive-distinct counter.

---

## 6. Automated PR triage bots (explore & adopt selectively)

Bots **comment and label**; they do not by themselves commit ArchW1z dispositions unless a roster human/agent promotes their output into the log with a `VOTE`.

### Already in this repo

| Bot | Role | Trust for consensus |
|-----|------|---------------------|
| **Devin Review** | Inline findings, severity | High signal for blockers; agent may `VOTE: accept` findings into disposition |
| **CodeRabbit** | Review summaries | **Comment only** — never sole summary-editor; may inflate scope |
| **Vercel** | Deploy status | Irrelevant to Termux gates unless web surface |
| **ecc-tools** | Generated skill bundles | Author of its PRs; human/summary-editor corrects |
| **Gitar** (if installed) | Review / heal assist | Same as other AI reviewers — evidence, not vote |

### Ecosystem options (evaluate, don’t auto-install all)

| Tool | Kind | Fit for termux-monorepo |
|------|------|-------------------------|
| **GitHub native** — labels, auto-merge, merge queue, PR Inbox | First-party | Prefer for required checks = `repo gate` + `termux smoke`; agent-authored PR filters |
| **Probot family** ([googleapis/repo-automation-bots](https://github.com/googleapis/repo-automation-bots)) | auto-label, blunderbuss assign, merge-on-green, do-not-merge | Useful: `do-not-merge` label for 🔴; auto-label `security` / `gate` |
| **PR Triage Bot** (Actions marketplace) | Classify type, risk, duplicates, trust tier | Good for opening triage comment; map risk→ our 🟢🟡🔴⚪ |
| **Mergify / Graphite / merge-steward** | Merge queues, stacked PRs | Optional later; gates already define landing train via `master-staging` |
| **Pullfrog** | Agent-in-GitHub triggers | Optional; must obey `AGENTS.md` + this file |
| **PR-Agent (Codium/Qodo)** | Describe / review commands | Optional describe assist; still run through summary-editor rules |
| **GitHub agent automation controls** (Issues, preview) | Confidence + approval for issue actions | Prefer for issue triage; not a substitute for PR disposition log |

### Recommended minimal triage automation

1. **Labels:** `status:merge-candidate` · `status:conditional` · `status:no-go` · `status:draft` · `security` · `needs-operator`  
2. **Required checks** on protected branches: repo-gate + termux-smoke only (not every bot).  
3. **On PR open:** optional Action posts triage skeleton (type, risk, base branch warning if not `master-staging`).  
4. **Never** auto-merge 🔴 or P0 security without Operator.  
5. Bot comments are **proposals**; promotion path: roster agent posts `VOTE: accept` of a specific bot finding into disposition.

---

## 7. Worked examples

### Example A — Same PR iterated (OK)

```text
#12 summary/1  DRIVER: grok-archw1z  → body rewrite 🟡
#12 summary/2  DRIVER: grok-archw1z  → fix checklist after Devin  (iteration OK)
#12 summary/3  DRIVER: devin         → optional handoff after skills regen
```

### Example B — Three distinct PRs then handoff

```text
PR-SUMMARY-LOG:
  #3  grok-archw1z
  #2  grok-archw1z
  #6  grok-archw1z   ← 3 distinct; next distinct PR should be devin|chatgpt|operator
  #5  devin          ← handoff satisfied
```

### Example C — P0 body rewrite votes

```text
Comment: term=pr-3/summary/2 DRIVER: grok-archw1z
Proposed body: Status ⚪ A-only …

Comment: VOTE: summary OK — @operator
→ driver applies update_pull_request
```

### Example D — Bot finding promoted

```text
Devin: 🔴 SKILL.md fenced
Agent: VOTE: accept on Devin finding BUG_0001; disposition remains 🟡 until fixed
```

---

## 8. Quick reference

```text
Commit decision → write to log + meet threshold for subject
P0              → two minds or Operator
Same PR iterate → always OK for summary accuracy
3 distinct PRs  → hand off fourth distinct rewrite
Bots            → evidence; humans/agents commit votes
Raft            → metaphor for terms/majority/leader/log — not a cluster daemon
```
