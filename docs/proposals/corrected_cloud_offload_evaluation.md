# Corrected Cloud Offload Evaluation

> **Registered as:** [`active/kimi-cloud-offload/`](active/kimi-cloud-offload/)  
> **Source branch (full text):** `docs/kimi-cloud-offload-evaluation`  
> **Status:** posted (not yet accepted)  
> **Priority:** P1

Master keeps this **pointer** so process docs stay navigable without a 24KB mid-flight dump.
Binding decisions live in the MANIFEST Review log + optional `DEBATE.md`.

## Summary of corrections

1. **Retry pattern** — not pure exponential backoff; **impatient user burst** (20% instant 0.5–2s, 80% jittered exponential, cap 90s) in deepcli.
2. **No calendar phases** — use Big-O complexity classes (O(1) bootstrap → O(log n) route → O(n) parallel → O(k log k) merge).
3. **TMUX replacement** — prefer `archwiz/autonomous_runner.py`, Hermes terminal/delegation, chronos Celery, sandbox-alternative VMs.
4. **AGY/Jules templates** — agentic-workflow-starter, antigravity-jules-autonomous, gemini-cli-jules-orchestrator as scavenge sources.
5. **jules-worker-pool-cli** — un-pause path documented on source branch.

## Read full text

```bash
git show origin/docs/kimi-cloud-offload-evaluation:docs/proposals/corrected_cloud_offload_evaluation.md
```

Or browse:  
https://github.com/timerloggedout-spec/termux-monorepo/blob/docs/kimi-cloud-offload-evaluation/docs/proposals/corrected_cloud_offload_evaluation.md

## Vote / promote

```bash
python3 scripts/proposals/record_vote.py --proposal kimi-cloud-offload \
  --term kimi-cloud-offload/accept/1 --voter <id> --vote accept --reason "…"
python3 scripts/proposals/promote_proposal.py --id kimi-cloud-offload \
  --to accepted --evidence "…"
```

See `docs/CONSENSUS.md` tiers and `docs/proposals/PROCESS.md`.
