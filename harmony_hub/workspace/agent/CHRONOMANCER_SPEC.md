# ⏳ Chronomancer Agent Specification

## Role
The **Chronomancer** is a specialised ArchWizard that monitors session productivity metrics, identifies optimal Time‑Loop branch points, and executes forks carrying forward only validated knowledge.

## Responsibilities
- **Monitor** `session_productivity.json` and `run_history.validated` for patterns.
- **Detect** when dead‑end patches accumulate (unverified runs > verified).
- **Select** the optimal fork point: the last assistant message where all critical tools exist.
- **Execute** `branch_conversation` to fork at the chosen parent message.
- **Inject** a validated‑state summary into the new session's first prompt.
- **Log** every fork to `run_history` with a `time_loop` verdict.

## Integration
- Reads `run_history` (SQLite) for success/failure patterns.
- Uses `verify-session.py` to confirm fork ownership.
- Feeds into the **Bidder** (ELO wagering) system: Chronomancer's forks are high‑value bets.
- Coordinates with the **Linguist** to compress the injected state summary.

## Fork Selection Algorithm
1. Scan `run_history` for the last `validated=1` entry.
2. Find the session message that immediately preceded that validation.
3. Confirm all critical files (Grimoire, profiles, utility belt) exist at that point.
4. If yes → fork from that assistant message.
5. If no → walk backward until a suitable parent is found.

## CLI Incantations
| Incantation | Purpose |
|-------------|---------|
| `cast rewind --auto` | Auto‑select best fork point and branch |
| `cast rewind --session X --msg Y` | Fork from a specific message |
| `cast snapshot --save` | Save current state as named restore point |
| `cast snapshot --list` | List saved snapshots |
