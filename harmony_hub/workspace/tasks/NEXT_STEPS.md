
# Immediate Tasks

## 1. Repair TUI
- Diagnose import errors (likely token path).
- Patch get_token to use token_provider_v2.
- Test TUI launch.

## 2. Activate Account2 (cookies_2.json)
- Build `token_provider_v2.py` in harmony_hub/src/.
- Support `--account primary|secondary` flag.
- Test with `termux-multi-agent` and `deepcli`.

## 3. ELO Suite Integration
- Locate existing ELO modules (`backfill_elo.py`, `sprints.py`).
- Connect them to `run_history.verdict`.
- Build bidding system (bidder.py) using ELO scores.

## 4. Nestable Entry Points
- Create `agent_task_factory.py` that loads prompt templates per role.
- Roles: refactor, review, bottleneck_detect, harvest, archive.
- Each role gets a distinct system prompt and toolset.

## 5. Logging & Pruning
- run_history.verdict already exists; populate it on each refactor.
- Build `pruner.py` that archives failed branches and keeps only successful chains.
