# Corrected Cloud Offload Evaluation

> **Source branch:** `docs/kimi-cloud-offload-evaluation`
> **Full text:** `docs/proposals/corrected_cloud_offload_evaluation.md` on that branch
> **Promoted:** pointer on `master` so process docs land without a 24KB mid-flight dump

## Summary of corrections

1. **Retry pattern** — not pure exponential backoff; **impatient user burst** (20% instant 0.5–2s, 80% jittered exponential, cap 90s) in deepcli.
2. **No calendar phases** — use Big-O complexity classes (O(1) bootstrap → O(log n) route → O(n) parallel → O(k log k) merge).
3. **TMUX replacement** — prefer `archwiz/autonomous_runner.py`, Hermes terminal/delegation, chronos Celery, sandbox-alternative VMs.
4. **AGY/Jules templates** — agentic-workflow-starter, antigravity-jules-autonomous, gemini-cli-jules-orchestrator as scavenge sources.
5. **jules-worker-pool-cli** — un-pause path documented on source branch.

## Action

```text
git show origin/docs/kimi-cloud-offload-evaluation:docs/proposals/corrected_cloud_offload_evaluation.md
```

Registrar may nest under `docs/proposals/active/` when itemized into ITEMS.
