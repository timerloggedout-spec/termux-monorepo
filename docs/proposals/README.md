# Proposals

**Agents: start at [`registry.yaml`](registry.yaml).**  
**Humans: start at [`PROCESS.md`](PROCESS.md).**  
**Permissions: [`AGENTIC-PERMISSIONS.md`](AGENTIC-PERMISSIONS.md).**  
**Consensus tiers: [`../CONSENSUS.md`](../CONSENSUS.md).**  
**Automation: `scripts/proposals/` + `.github/workflows/proposal-lifecycle.yml`.**

## Active

| ID | Priority | Status | Path |
|----|----------|--------|------|
| chatgpt-critical-eval | P0 | executing | [active/chatgpt-critical-eval/](active/chatgpt-critical-eval/) |
| kimi-cloud-offload | P1 | posted | [active/kimi-cloud-offload/](active/kimi-cloud-offload/) |
| chatgpt-initial | P2 | posted | [active/chatgpt-initial/](active/chatgpt-initial/) |
| chatgpt-droidapp | P2 | posted | [active/chatgpt-droidapp/](active/chatgpt-droidapp/) |

## Large sources / debate branches

| Pointer on master | Full text branch | Notes |
|-------------------|------------------|-------|
| `corrected_cloud_offload_evaluation.md` | `docs/kimi-cloud-offload-evaluation` | Kimi corrections; nested as `active/kimi-cloud-offload/` |

Flat historical sources still on master:

- `ChatGPT_Critical-Eval(TER0-15+other-branches).md`
- `ChatGPT-initial.md`
- `ChatGPT_droidApp.md`

## Scripts

```bash
python3 scripts/proposals/validate_registry.py
python3 scripts/proposals/record_vote.py --proposal kimi-cloud-offload \
  --term kimi-cloud-offload/accept/1 --voter YOU --vote accept --reason "…"
python3 scripts/proposals/promote_proposal.py --id kimi-cloud-offload \
  --to accepted --evidence "VOTE accept from …"
```
