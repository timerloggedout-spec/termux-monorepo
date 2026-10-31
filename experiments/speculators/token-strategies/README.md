# Speculators — token-strategies-1

`issue #195 (Evaluations) ⇒ Multiple Token Strategies Implementations ↦ timerloggedout-spec/speculators_fork @ c13304cf3ec2 (fork ∘ vllm-project/speculators)`

## What is built

- `scripts/speculators/strategies.py` — registry ⊃ ∀ token strategies implemented in the fork (`src/speculators/models/{eagle3,peagle,dflash,dspark,mtp}` ✓ firsthand @fork tree) + `baseline` control arm (verifier-only, ∅ drafting).
- `scripts/speculators/evaluate.py` — harness, pattern ∘ `scripts/doe/lab_runner.py`: `plan` = strategies × verifiers factorial × tasks, every row stamped `treatment.instance` + `instance_key` (`scripts/doe/instance_key.py`); `record` = results.jsonl ⇒ per-cell {acceptance_rate, mean_accepted_length, mean_speedup} + verdict vs pre-registered rule (DESIGN.json).
- `tests/test_speculators.py` — registry ≡ fork model dirs, plan determinism + stamping, record metrics + selection + lossless gate.

## Strategies

| id | drafting | draft side |
|---|---|---|
| `baseline` | none | verifier generates every token (control) |
| `eagle3` | sequential | draft model ∘ auxiliary hidden states |
| `peagle` | parallel | multi-token prediction ∘ COD sampling |
| `dflash` | anchored-block | block drafting ∘ sliding-window attention |
| `dspark` | anchored-block+markov+confidence | DFlash + Markov head + confidence head |
| `mtp` | native-heads | verifier's own MTP heads, finetuned (FastMTP) |

∀ speculative rows: lossless ∵ verifier checks ∀ drafted tokens in one forward pass ∧ accepted ≡ verifier-only output. `record` enforces it: `output_match ≠ true` ⇒ cell disqualified, ¬ selected at any speed.

## State

`admitted_design_only` — plan generated (12 cells × 4 tasks = 48 runs, PLAN.json); execution (fork training + vLLM serving) rides GPU/provider lanes ⇒ results.jsonl ⇒ `record` ⇒ SUMMARY.json verdict. Harness dispatches ∅.
