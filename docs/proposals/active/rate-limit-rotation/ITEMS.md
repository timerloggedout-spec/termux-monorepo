# ITEMS — rate-limit-rotation

| ID | Work | Priority | Owner | Status | Evidence |
|----|------|----------|-------|--------|----------|
| RL-01 | Model rotation registry (free-tier table) | P0 | grok | done | docs/schemas/model-rotation.yaml |
| RL-02 | model-router composite action | P0 | grok | done | .github/actions/model-router |
| RL-03 | Wire triage → Flash-Lite | P0 | grok | done | gemini-triage.yml |
| RL-04 | Wire review → Flash w/ Lite fallback | P0 | grok | done | gemini-review.yml |
| RL-05 | OpenRouter fallback path | P0 | grok | executing | #123 landed ELO+poll router; http-llm-invoke fallback still tracked |
| RL-06 | Tighten job-gate daily-limit (900→100) | P1 | grok | todo | pair with #81 |
| RL-07 | Prompt compression for agent workflows | P1 | | todo | issue #90; PR #126 |
| RL-08 | OmniRoute hub integration surface | P2 | | todo | issue #91 |
| RL-09 | Per-model Linear quota dashboard | P2 | | todo | |
| RL-10 | Merge/rebase #81 quota-gate onto master | P0 | | todo | PR #81 |
| RL-11 | Peer-review gate (wait CR/Devin/Aikido) | P0 | grok | done | peer-review-orchestrator.yml |
| RL-12 | Auto CodeRabbit autofix after CR review | P0 | grok | done | OPERATOR_GITHUB_TOKEN + github-token input |
| RL-13 | Gemini second-pass after peers only | P0 | grok | done | gemini-after-peers.yml |
| RL-14 | Devin Apply Suggestions automation | P1 | | partial | enable Auto-Fix in Devin Settings; no public click-API |
| RL-15 | Honest OpenRouter (no false route) | P0 | grok | done | model-router skip=true always when Gemini exhausted |
| RL-16 | Shared global counter (not per-branch cache) | P2 | | todo | gist/issue optimistic concurrency |
| RL-17 | Model availability polling & ELO (3L0) routing | P0 | jules | done | #123 scripts/model_router.py, model-success-matrix.yaml |
| RL-18 | DeepSeek CI peer path (no Class 3/4 cache) | P0 | jules | blocked | #134 security hold — ephemeral session only |
| RL-19 | Audit Merged Branches, Skipped Reviews & Lane Consolidation | P0 | jules | done | docs/ops/MERGED-BRANCH-AUDIT-2026.md, docs/ops/LANE_CONSOLIDATION_SSOT.md |
