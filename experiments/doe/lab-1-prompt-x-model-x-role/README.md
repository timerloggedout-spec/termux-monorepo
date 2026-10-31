# lab-1 — prompt x model x role (first live ExperimentsLab campaign)

Designed 2026-10-30 under the repo-is-the-experiment doctrine.
Factors: prompt (prompt-a strict-verbatim | prompt-b loose),
model (openrouter gpt-4o-mini | llama-3.1-8b-instruct:free),
role (triage | reviewer). Suite = pilot-1's 8 source-grounded
tasks, inherited verbatim for comparability with the offline
baseline. Settings fixed (temperature 0, explicit context,
icm-guided routing — pilot-1's winning levels).

Plan: `python3 scripts/doe/lab_runner.py plan <this dir>` →
PLAN.json (64 runs, every row instance-stamped). Execution rides
fleet provider lanes on free OpenRouter routes; results return as
results.jsonl → `lab_runner.py record` writes EXPERIMENT records
+ SUMMARY with the verdict vs the pre-registered selection rule
(top cell >= 0.80 accuracy, margin >= 0.05, else no_selection).
State until records land: admitted_design_only.

**Suite type: `control`** (owner, 2026-10-31) — fragment-style
suites are the control type, minimal use; the primary
experimental mass is active development + review as live
testing. **Provider phrases:** none established for this
campaign's two OpenRouter routes (the established sets in
`harmony_hub/workspace/prompts/prompt_engine.py` are
DeepSeek-shaped) — recorded in DESIGN.json as NOT ESTABLISHED;
when a set exists for a route, the runner composes it into the
prompt and the hash.
