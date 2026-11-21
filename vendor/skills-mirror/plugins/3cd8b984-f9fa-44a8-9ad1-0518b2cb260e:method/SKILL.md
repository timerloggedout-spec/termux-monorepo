---
name: method
description: Explain one of the 15 built-in JTBD methods, recommend which method fits a situation, or run a method on the knowledge base to produce a deliverable (scope, workshop brief, hypotheses, screener, discussion guide, competition map, opportunity survey, HMW statements, design brief, results narrative, positioning, post-launch survey, JTBD board). Use when the user asks how to do something with JTBD or wants one of these deliverables.
argument-hint: "[method name or number, e.g. 5 discussion guide for PM]"
---

# Method: learn and apply the JTBD methods

Before anything else, read `${CLAUDE_PLUGIN_ROOT}/reference/rules.md` (data model, scoring, rules) and `jtbd.config.yaml` at the project root (backend, IDs). If the config is missing or `backend` is empty, run `/jtbd-base:setup` first.

The 15 methods live in this skill, one file each in `${CLAUDE_SKILL_DIR}/references/NN-*.md` (NN = order). Each file gives what the method brings, its steps, and how Claude runs it; the frontmatter lists phase, roles, status (Stable or Draft), inputs and outputs. Read only the file you need. Concepts and scoring rules are in the concepts page (Notion) or `<vault_path>/concepts.md` (local), source copy in `${CLAUDE_PLUGIN_ROOT}/skills/setup/seed/concepts.md`.

Explaining or recommending a method works without a configured base. Running one needs the base (see `jtbd.config.yaml`).

## Method index

| # | Method | Phase | Deliverable |
|---|---|---|---|
| 1 | Frame the team's scope | Scope | Scope (performers, jobs, outcomes) |
| 2 | Expand the scope in a team brainstorm | Scope | Workshop brief, new hypotheses, journey map |
| 3 | Turn jobs and outcomes into hypotheses | Scope | Ranked hypothesis list |
| 4 | Recruit participants by the job they do | Discover | Screener |
| 5 | Build the interview guide from jobs and outcomes | Discover | Interview guide |
| 6 | Analyze research through the JTBD lens | Analyze | Jobs, outcomes, evidence (use jtbd-base:ingest) |
| 7 | Map the real competition for each job | Discover | Alternatives and forces per job |
| 8 | Find and rank opportunities with an importance and satisfaction survey | Prioritize | Survey, opportunity ranking |
| 9 | Prioritize features against jobs (draft) | Prioritize | Features grouped by job |
| 10 | Generate ideas with How Might We questions (draft) | Design | HMW questions |
| 11 | Design for the job, step by step | Design | Design brief, concept review |
| 12 | Share results in terms of jobs and outcomes | Deliver | Results narrative |
| 13 | Position the solution with product marketing (draft) | Deliver | Positioning and messages |
| 14 | Measure the change in satisfaction after launch | Measure | Post-launch survey, deltas |
| 15 | Keep the jobs visible throughout the project (draft) | Throughout | JTBD board |

Users may name a method by number, by title or by its old wording (for example "Evaluate and prioritize opportunities" is method 8): match by meaning.

## Three modes

**Explain.** Read the method file and explain what it brings and how to do it, in the user's language and adapted to their project. Add the relevant concept (statement grammar, scoring, forces) when it helps. Summarize, do not paste the file.

**Recommend.** From the user's situation, propose 1 to 3 methods in order, with one line each on why. Typical sequence: 1 → 2 → 4 → 5 → 6 → 7 → 8 → 10 → 11 → 12 → 14.

**Run.** Produce the deliverable from real data in the base:
1. Read the method file.
2. Load its `inputs` from the base (via jtbd-base:query patterns), for the project and performer in scope.
3. Check prerequisites. If inputs are missing (for example no satisfaction baseline for method 14), say so and propose the method that fills the gap.
4. Generate the deliverable following the steps. Tie every element back to job or outcome IDs.
5. Save it to `outputs/YYYY-MM-DD-<method>-<project>.md`. With the Notion backend, offer to also publish it as a page under the JTBD Hub.
6. If the method produces knowledge (new hypotheses, alternatives, forces, scores), propose the rows and hand off to jtbd-base:capture.

## Deliverable templates

- **Screener (4):** intro, 4 to 6 questions on doing the job recently, frequency, current alternative used, disqualifiers, target mix.
- **Interview guide (5):** warm-up; per main job: open question, then each step in order with "how do you...", "what makes it hard...", probes per outcome; discovery questions ("what are you trying to achieve", "what does success look like"); alternatives ("how do you do it today, why"); forces ("what made you start looking", "what attracted you", "what worried you", "what almost kept you where you were"); wrap-up. Mark jobs still in Hypothesis as priorities to probe.
- **Competition map (7):** per main job, the alternatives with Type, why they hire it, where it falls short, and the four forces; end each with the switch balance (Push + Pull vs Anxiety + Habit) and the forces that still lack evidence.
- **Opportunity survey (8):** two tables (importance, satisfaction) on a 1 to 7 scale, same statements in the same order, outcome statements rewritten in second person if needed, screening questions on top, target 20 to 30+ responses.
- **Hypotheses (3):** "We believe [performer] struggles to [outcome] during [step]. We will know we are right when [signal]." Ranked by Opportunity when scores exist, otherwise by evidence strength.
- **HMW (10):** "How might we help [performer] [outcome] when [step]?" plus broader and narrower variants.
- **Design brief (11):** main job, ordered steps, top outcomes per step, alternatives with their shortcomings and the Anxiety and Habit forces the solution must overcome, emotional and social jobs to honor.
- **Board (15):** performer, "could be" roles, aspiration, then per main job: emotional job, social job, ordered job steps.

## Draft methods

Methods 9, 10, 13 and 15 have status Draft. When running them, follow their "Proposed steps" and, once the user has tried them, ask whether to promote the method: edit its file in the plugin's `skills/method/references/` (a change to the plugin repo) (status Stable, steps updated from what worked).
