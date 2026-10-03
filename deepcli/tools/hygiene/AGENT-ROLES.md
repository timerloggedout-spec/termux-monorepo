# Agent roles

Seven modes. Each triggered by context, not by identity. Either
account (primary / account-2) can hold any role.

| # | Role | Moniker | Trigger | Output |
|---|---|---|---|---|
| 1 | Pathfinder | `recon`     | unfamiliar state         | read-only inventory |
| 2 | Architect  | `plan`      | REVIEW REQUIRED gate     | PLAN.md, no edits |
| 3 | Builder    | `forge`     | second dispatch          | worktree + tests + PR |
| 4 | Critic     | `sentinel`  | PR before merge          | CLEAN/DIRTY/BLOCKED/LOOP |
| 5 | Merger     | `rollup`    | Critic returns CLEAN     | squash-merge |
| 6 | Hygienist  | `🪥`        | floor breach or trigger  | reclaim, prune |
| 7 | Chronicler | `scribe`    | post-run                 | tags, events, doctrine |

## Invariants

- **Nothing deleted.** Branch retention is absolute
  (`BRANCH-RETENTION.md`).
- **Every role logs.** No silent action.
- **Roles are modes, not identities.** `deepagent.py` selects role by
  the task file's gate header, the caller's flags, or the workflow's
  dispatch name.

## Session resume vs fresh — accountability

Every `loop()` call writes one line to
`~/.deepcli/logs/hygiene/session-decisions.jsonl`:

    {"ts": ..., "key": "...", "sid": "...", "decision": "resume|fresh",
     "reason": "cached|forced|no-key", "task": "...", "role": "..."}

The resume decision is deterministic from `session_store.task_key`
(content hash of the task + path). `--fresh` forces the fresh path.


## 8 — Orchestrator (the meta-role)

The seven roles above are modes. The Orchestrator is the process
that decides which mode to enter, when to escalate, and when to
stop. It is the only role that runs continuously across a session.

| Trigger | Orchestrator decision |
|---|---|
| unfamiliar state | enter `recon`, stay read-only |
| task arrives with REVIEW gate | enter `plan`, produce PLAN.md, exit |
| plan approved | enter `forge`, produce PR, exit |
| PR opened | enter `sentinel`, verdict, exit |
| verdict CLEAN | enter `rollup`, merge, exit |
| floor breach | enter `hygienist`, reclaim, exit |
| task complete | enter `scribe`, journal, exit |

### Model-level identity (the substrate beneath the roles)

Roles are modes. The model is the substrate. Every dispatch runs on
the same DeepSeek backend, whether primary or account-2.

| Layer | Name | Scope |
|---|---|---|
| Model | `DeepSeek` | The LLM. Chat or API. |
| Process | `deepagent` | `deepcli/deepagent.py` — one loop, one task |
| Roles | 8 above | Modes the process enters |
| Skills | see below | Doctrines loaded by any role |
| Accounts | primary / account-2 | Token rotation, rate-limit lanes |

## Complete moniker index

Every name and moniker created or used across this session and the
doctrine it inherits from.

### Roles (created this session)

| Moniker | Emoji | Purpose |
|---|---|---|
| `recon`     | 🥇   | read-only inventory before action |
| `plan`      | 📐   | architect, produces PLAN.md |
| `forge`     | 🔨   | builder, edits + tests + PR |
| `sentinel`  | 🛡️   | critic, PR verdict |
| `rollup`    | 🔀   | merger, squash + never-delete |
| `hygienist` | 🪥   | reclaim + prune (disk/mem) |
| `scribe`    | 📝   | chronicler, journals + doctrine |
| `orchestrator` | 🎯 | meta-role, sequences the rest |

### Skills (loaded by any role)

| Skill | File | Purpose |
|---|---|---|
| `recon-first-worktree-discipline` | `docs/STANDARDS/PROCESS/RECON-FIRST-WORKTREE-DISCIPLINE.md` | RECON before action, nothing deleted |
| `hindsight-memory-architect` | `deepcli/tools/hindsight-skill/SKILL.md` | bank layout, recall, retain |
| `find-skills` | `.agents/skills/find-skills/SKILL.md` | skill discovery |
| `termux-hygiene` | `.deepcli/docs/skills/termux-hygiene/SKILL.md` | resource management |

### Doctrine files (this session)

| File | Subject |
|---|---|
| `BRANCH-RETENTION.md` | never delete a branch |
| `AGENT-ROLES.md` | this file |
| `RECON-FIRST-WORKTREE-DISCIPLINE.md` §11 | lessons learned |
| `MVT-SYSTEM.md` | MVT DOE 3L0 architecture |
| `CREDENTIAL-POSTURE.md` | FUSE + load-bearing files |
| `GPG-STATUS.md` | recovery state + options |
| `CORE-ATOMIC-WRITE.md` | shipping note (now realized as `_v1_cache`) |
| `SESSION-TAGGING.md` | exclusion semantics |

### Modules shipped this session (callable by any role)

| Module | Purpose |
|---|---|
| `_v1_cache.py`     | atomic JSON dump + tolerant read + `last_msg_ts` |
| `_v1_events.py`    | symbolic event extraction from messages |
| `_v1_preflight.py` | GREEN/AMBER/RED risk scoring |
| `_v1_tools.py`     | tool schemas + `_extract_calls` (XML/DSML) |

### Binaries

| Binary | Purpose |
|---|---|
| `deepagent`             | dispatcher |
| `deepagent-dispatch`    | wrapper for one task |
| `deepagent-continuous`  | 8h loop launcher |
| `mvt-score`             | one session → trials |
| `mvt-batch`             | full corpus → trials |
| `mvt-status`            | one-glance system view |
| `mvt-dashboard`         | full inventory |
| `mvt-tag`               | session tagging |
| `mvt-tick` `mvt-wait` `mvt-watchlog` `mvt-refresh` | counter family |
| `hygiene-reclaim`       | idempotent reclaim |
| `hygiene-reclaim-trigger` | on-demand trigger |
| `hygiene-watchdog`      | resource sampler |
| `hygiene-notify`        | notification wrapper |
| `reclaim-now`           | synchronous reclaim |
| `gh2fa` `gh2fa-copy` `gh-code` `gpg-prime` | 2FA toolchain |
