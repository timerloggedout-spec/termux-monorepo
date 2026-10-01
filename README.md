# memory-bank

Durable read path when codespace is cold.

- bank-latest.zip — last hs-drain snapshot
- LAST-DRAIN.md   — timestamp + source
- pending/        — unreplayed writes (JSONL)

Read: `unzip bank-latest.zip -d /tmp/bank && inspect documents/*.json`.
Restore: `hs-parity2 import codespace bank-latest.zip`.
