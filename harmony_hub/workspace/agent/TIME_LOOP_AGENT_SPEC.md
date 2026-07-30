# 🪄 Time Loop Agent Specification

## Role
The **Chronomancer** agent monitors session productivity metrics (from `session_productivity.py`),
identifies successful patterns, and automatically forks new sessions from validated branch points
to carry forward only verified knowledge.

## Integration Points
- **ELO/Bidding**: Chronomancer wagers Mana (ELO) on which branch point will yield the best iteration.
- **Fragment Matcher**: Uses `Echo` (similarity) to detect when a code block was successfully applied.
- **Orchestrator**: Calls `branch_conversation` to fork at the chosen message, then dispatches a `Transmute` task.
- **run_history**: Logs every fork as a validated or unverified run, feeding back into ELO.

## Incantations (CLI Commands)
| Incantation | Purpose |
|-------------|---------|
| `cast rewind --session X --term Y` | Find fork points matching Y and list them |
| `cast branch --session X --parent Z` | Fork a new session from message Z |
| `cast loop --session X --from Z` | Fork and send a loop continuation prompt |
| `cast snapshot` | Save current run_history + vault state as a named snapshot |

## Auto-Fork Logic
1. Monitor `run_history.validated` for a series of successes.
2. When a pattern is confirmed (e.g., "Account 2 token extraction"), find the message ID where that success was first confirmed.
3. Fork a new session from that parent message.
4. Inject the validated state (token, orchestrator config, utility belt) as a system prompt.
5. Dispatch the next sprint objective to the new session.

## Next Steps
- [ ] Implement `cast snapshot` to save/restore state.
- [ ] Wire Chronomancer to `elo_updater.py` for bidding.
- [ ] Add `--auto` flag to `direct_task.py` for unsupervised volleys.
