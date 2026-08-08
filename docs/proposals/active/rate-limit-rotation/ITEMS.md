# ITEMS — rate-limit-rotation

| ID | Work | Priority | Owner | Status | Evidence |
|----|------|----------|-------|--------|----------|
| RL-01 | Model rotation registry (free-tier table) | P0 | grok | done | docs/schemas/model-rotation.yaml |
| RL-02 | model-router composite action | P0 | grok | done | .github/actions/model-router |
| RL-03 | Wire triage → Flash-Lite | P0 | grok | done | gemini-triage.yml |
| RL-04 | Wire review → Flash w/ Lite fallback | P0 | grok | done | gemini-review.yml |
| RL-05 | OpenRouter fallback path | P0 | grok | done | model-router + invoke |
| RL-06 | Tighten job-gate daily-limit (900→100) | P1 | grok | todo | pair with #81 |
| RL-07 | Prompt compression for agent workflows | P1 | | todo | issue #90 |
| RL-08 | OmniRoute hub integration surface | P2 | | todo | issue #91 |
| RL-09 | Per-model Linear quota dashboard | P2 | | todo | |
| RL-10 | Merge/rebase #81 quota-gate onto master | P0 | | todo | PR #81 |
| RL-11 | Peer-review gate (wait CR/Devin/Aikido) | P0 | grok | done | peer-review-orchestrator.yml |
| RL-12 | Auto `@coderabbitai autofix` after CR review | P0 | grok | done | peer-review-orchestrator |
| RL-13 | Gemini second-pass after peers only | P0 | grok | done | gemini-after-peers.yml |
| RL-14 | Devin Apply Suggestions automation | P1 | | partial | enable Auto-Fix in Devin Settings; no public click-API |
