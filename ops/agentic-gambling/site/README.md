# MoneyBall — Site Wallet Ledger

`wallet-ledger/v1` · append-only · the site-side balance record for MoneyBall paper|test wallets.

- **Ledger:** `wallet-ledger.jsonl` — one JSON event per line, hash-chained receipts (`payload_hash`/`prev_receipt_hash`). Balances are a derived fold of events, never a stored field; every `balance_after` is a recomputable claim.
- **Tooling:** `scripts/moneyball/wallet_ledger.py verify|fold` — chain integrity, fold == claims, genesis equality. Verify must pass before any PR appends events.
- **Wallets:** the 12 speculator wallets provisioned in `experiments/speculators/token-strategies/WALLETS.json` (`speculators-wallets/v1`, PR #4640) — that file is the provisioning record; its `balance: 0` is the provisioning snapshot. Site balances live here, by fold. Speculator class stays distinct from the gambler class at record level.
- **Genesis (seq 1–24):** main's ruling under delegated management (2026-11-03 14:25 PT, owner-adjustable): **EQUAL genesis across all 12 wallets** — 1,000 units each, 12,000 total. Unit verbatim from the token-strategies design: `soft_quota_token (observational)` (`DESIGN.json` → `wallets.unit`); the design fixes the denomination only, no numeric size — the 1,000 size was set by the Web3 seat under the equality ruling. Uniform start keeps Brier/ranking comparability clean and matches the cull-waterfall fairness shape; no wallet starts advantaged.
- **Relation to the Book:** this ledger is NOT the book ledger (`ops/agentic-gambling/book/ledger.jsonl`). Cross-links are by ref only (`position_ref`, `settlement_ref`) — either ledger verifies alone (DESIGN §4.2, moneyball repo `docs/DESIGN.md`).
- **Events:** `wallet_provisioned · faucet_issued · stake_escrowed · stake_released · payout_credited · pool_contribution · pool_distribution · cull_transferred · adjustment` (correction-only, cites prior event; nothing is ever edited or deleted).
