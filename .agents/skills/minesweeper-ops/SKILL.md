---
name: minesweeper-ops
description: Concurrent-agent PR collision. Jules/Palette/Bolt family stays EXTRACT. Never overwrite peer branches.
---

# Skill: minesweeper-ops

Family (live 2026-09-26): #65 #140 #481 #630 #672 #680 #750.

Rules:

1. Bot + files>40 → EXTRACT
2. Title tokens palette/bolt/linguist/sentinel/minesweeper → EXTRACT
3. File-set overlap with an open peer → EXTRACT, do not force-push
4. CodeRabbit / Qodo / Devin / Copilot reviews are advisory, not gates
