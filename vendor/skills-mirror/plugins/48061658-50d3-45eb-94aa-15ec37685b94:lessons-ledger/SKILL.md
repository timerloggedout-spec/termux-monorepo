---
name: lessons-ledger
description: Use before starting work in an area to retrieve only the lessons that apply to it, and right after a wrong diagnosis, a defect the tests missed, or an environment trap to record one — keeps hard-won lessons in a per-project ledger indexed by code area and work type, so past mistakes reach the next session and the executors without loading everything every time.
---

# Lessons Ledger

Hard-won lessons — a wrong diagnosis, a trap the tests couldn't see, a tool that
lies about its own state — are worth more than most documentation and are the
first thing lost between sessions.

The ledger keeps them **retrievable by relevance**, not by recency. A lesson about
rollup aggregation must not load when the task is writing user documentation.
That selectivity is the whole design: a store everyone must read in full is a
store nobody reads.

Two moves: **look up before working in an area**, **record right after being
wrong.**

## The Store

```
docs/lessons/
├── INDEX.md              ← one line per lesson; the only file read by default
└── <slug>.md             ← one lesson each; opened only when the index matches
```

Keep the ledger in the project's documentation repo. When code lives in a
separate repo, the lessons still belong here — but see *Handing lessons to
executors* below, because they cannot see this repo at all.

### INDEX.md

| Bài học | Chạm | Loại việc | Móc |
|---------|------|-----------|-----|
| [tien-trinh-treo-sau-khi-xong](tien-trinh-treo-sau-khi-xong.md) | scripts/, CLI job | vận hành dữ liệu | Tiến trình còn sống ≠ việc chưa xong — canh bằng dữ liệu |
| [mock-tu-xac-nhan-cai-sai](mock-tu-xac-nhan-cai-sai.md) | signer, PDF | tích hợp bên thứ ba | Mock chép hình dạng của mã sai thì test xanh vô nghĩa |

One line each, never more. The index is loaded to decide what to open, so it must
stay cheap enough to read in full every time.

- **Chạm** — module, path, or external system. What you'd be editing.
- **Loại việc** — the kind of work: `sửa engine`, `deploy`, `tích hợp bên thứ ba`,
  `viết tài liệu`, `vận hành dữ liệu`, `dựng test`. Covers lessons that belong to
  no particular file.
- **Móc** — the rule in one clause, so an obviously irrelevant lesson can be
  skipped without opening it.

### One lesson file

```markdown
---
name: <slug>
chạm: <module / path / hệ thống ngoài>
loại việc: <loại việc>
ngày: YYYY-MM-DD · nguồn: <phase, commit, hoặc phiên>
---

# <Tên — phát biểu như một luật, không phải kể sự cố>

**Luật:** <một câu, tổng quát hoá được sang tình huống khác>

**Bằng chứng:** <số đo, log, commit — cái đã thật sự xảy ra>

**Vì sao dễ sai:** <lối suy luận đã dẫn tới kết luận sai>

**Áp dụng:** <việc cụ thể phải làm lần sau; trỏ tới phép kiểm đã khóa nó lại nếu có>
```

**State it as a rule, not as an incident.** "Rollup OOM'd on Aug 4" helps nobody;
"a process staying alive is not evidence the work is unfinished — check the data
it produces, not its process state" transfers to every long-running job. The
incident belongs in **Bằng chứng**; the transferable claim is the title.

**Evidence is mandatory.** A lesson without the numbers or output that produced it
is an opinion, and the next session cannot tell whether it still holds.

## Looking Up (before working in an area)

1. Read `INDEX.md` — this is cheap and always allowed.
2. Filter on the area you are about to touch **and** the kind of work. Both, not
   either: editing `scripts/` for a deploy is not the same as editing it to add a
   report.
3. Open **only** the matching lessons. Opening everything defeats the index.
4. If nothing matches, say so and proceed. Do not stretch an unrelated lesson to
   fit — a forced lesson is worse than none, it misdirects the work.

Do this before writing code in an unfamiliar area, before dispatching an executor
there, and before re-attempting anything that failed once.

## Getting Lessons to Executors

An executor starts from zero every dispatch, so a lesson it never sees is a
lesson it will re-learn the expensive way. Route by how widely the lesson
applies — **never by pasting the ledger into prompts**, which repeats forever and
grows with every dispatch:

| Scope of the lesson | Where it goes |
|---------------------|---------------|
| Applies to **every task** in the project | Crystallize it as a rule in the executor context file (`executor-context`). One line of imperative; the ledger keeps the evidence and reasoning. |
| Applies to **the area this task touches** | One line in this task's handoff prompt, phrased as a constraint — not the whole lesson file. |
| Applies to neither | Leave it in the ledger. It'll be found by lookup when its area comes up. |

The ledger is the archive with the "why"; the executor gets the imperative. Those
are different documents on purpose — an executor doesn't need to be convinced,
it needs to know.

## Recording (immediately, not at session end)

Write a lesson the moment one of these happens — not later, and not batched at
the end of the session:

| Trigger | What makes it a lesson |
|---------|------------------------|
| **A diagnosis turned out wrong** | Your reasoning was refuted by reality. Record the reasoning too — the next session will be tempted by the same path. |
| **Verification caught what tests missed** | Green tests plus a real defect means a class of bug the suite cannot see. |
| **An environment or tooling trap** | The tool lied: silent quota exhaustion, a command that kills itself, a job that "finished" having done nothing. |
| **End of a phase** | Review what the phase taught that the next phase would otherwise re-learn. |

Rules:

- **One lesson per file.** If it duplicates an existing one, strengthen that file
  with the new evidence instead of adding a second.
- **Add the index line in the same commit.** A lesson missing from the index does
  not exist.
- **Prune what stopped being true.** A lesson about a system that was rewritten is
  a trap of its own — delete it and say why in the commit.

### On a multi-lane project

One ledger, written by the Chief (`multi-lane-coordination`). A lane that learns a
lesson writes it as a **proposal** in its outbox, in the lesson-file format, with
the areas it touches; the Chief records it and the index line. That way a lesson
from one lane reaches the others as soon as the Chief records it, not when the
lane is next integrated. Lanes look up the ledger the normal way, filtered by their
own area.

## Boundaries

| Content | Where |
|---------|-------|
| Current state, what's half-done, next action | `pointer-handoff` |
| Conventions every task must follow | Executor context file (`executor-context`) |
| Scale, trade-off priorities, hard boundaries | `system-profile.md` (`concept-briefing`) |
| Phase structure, what unlocks what | Roadmap (`concept-briefing`) |
| Why a design was chosen | The spec for that work |
| The user's preferences, machine access, working style | Your harness's own memory store — not this ledger |

The last row matters: a harness memory store (Claude Code's `memory/`, Codex's
`memories/`) holds facts about the *user* and their environment, loads by its own
relevance rules, lives outside the repo, and is invisible to executors and
teammates. The ledger holds technical lessons about *this codebase*, lives in the
repo, gets reviewed, and travels with the branch. They are not substitutes.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll read all the lessons to be safe" | Then the index was pointless and every session pays for every lesson. Filter, open what matches. |
| "Kind of related, I'll apply it" | A forced lesson misdirects the work. No match means no match. |
| "I'll record this at the end of the session" | Record it now. The reasoning that misled you is freshest — and clearest — at the moment it's refuted. |
| "I'll paste the matching lessons into the prompt" | That repeats every dispatch and never ends. Project-wide lessons become rules in the executor context file; area lessons become one constraint line. |
| "Rollup crashed on Aug 4 — that's the lesson" | That's the evidence. The lesson is the rule that transfers to the next long-running job. |
| "I was wrong, but recording it is embarrassing" | Wrong diagnoses are the highest-value entries here. The next session repeats them otherwise. |
| "Lesson written, index later" | Later never comes and an unindexed lesson is invisible. Same commit. |
