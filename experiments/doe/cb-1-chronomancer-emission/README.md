# cb-1-chronomancer-emission — competing build #1 (DESIGN ONLY)

`[MUSEai]@{role:{doe-mgr-live-builds}}` ⊂ doe-expert · INIT++ WO#2

**⛔ DISPATCH ∅ until doe-expert approves this DESIGN.**

**Task (identical ∀ arms):** `scripts/doe/chronomancer_emitter.py` —
read-only emitter over a `run_history` SQLite DB (schema from
`harmony_hub/workspace/agent/chronomancer.py`, read firsthand: fork
rows carry `target_file='chronomancer-fork'`, `verdict='time_loop'`,
`session_id` = new forked session). Fork + continuation = TWO
EXPERIMENT records (DOE-FAMILY mapping, #2668); unpaired fork ⇒
`pairing=pending`, ∅ fabricated continuation. Contract in DESIGN.json.

**Arms (factor = arm only; framing held = live-1 A-implement-only):**

| Arm | Route | Issue draft |
|---|---|---|
| arm-jules | issue + `jules` label (on-demand) | `issues/arm-jules.md` |
| arm-gemini | crafted issue (event-bound, #2732 proof) | `issues/arm-gemini.md` |

Review ∀ PRs: DeepSeek-CI + command-dispatch (review arms only).
Live-3 phrase assignment EXCLUDED on cb-1 PRs until verdict.

**Acceptance (deterministic):** A1 schema-valid ∀ records · A2
pairing exact, ∅ orphans · A3 fixture count = 5 · A4 byte-stable
re-run · A5 source DB hash unchanged · A6 repo gate green.
Evaluated by live-builds from test evidence + firsthand re-run.

**Rule (pre-registered):** both pass ⇒ fewer steering interventions
wins (tie: wall-clock); one passes ⇒ it wins; none ⇒ no_selection +
redesign proposal. Winner merged 🍒⛏️ = emitter-class template;
loser PR closed unmerged, records retained (🧬 culling event in
`records/SUMMARY.json`).

Allowed paths ∀ arms: `scripts/doe/chronomancer_emitter.py` +
`tests/test_chronomancer_emitter.py` only.
