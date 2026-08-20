# ITEMS — agent-quota-loadbalancer

| ID | Work | Priority | Owner | Status | Evidence |
|----|------|----------|-------|--------|----------|
| QL-01 | Gemini quota-gate composite action | P0 | tembo | done | .github/actions/gemini-quota-gate/action.yml |
| QL-02 | Session continuation cache for gemini-review | P0 | tembo | done | .github/workflows/gemini-review.yml |
| QL-03 | Graceful skip when quota exhausted (no CI failure) | P0 | tembo | done | gemini-review.yml + gemini-triage.yml + gemini-invoke.yml |
| QL-04 | Agent load-balancer dispatch workflow | P0 | tembo | done | .github/workflows/agent-load-balancer.yml |
| QL-05 | Update gemini-dispatch to route through load balancer | P0 | tembo | done | .github/workflows/gemini-dispatch.yml |
| QL-06 | Agent capability registry stub | P1 | tembo | done | docs/schemas/agent-capabilities.yaml |
| QL-07 | .gitignore: nexuscli session_store pattern | P0 | tembo | done | .gitignore |
| QL-08 | Proposal registry + MANIFEST + ITEMS | P0 | tembo | done | docs/proposals/active/agent-quota-loadbalancer/ |
| QL-09 | Quota utilization dashboard (GHA summary) | P2 | | todo | |
| QL-10 | Multi-key rotation for Gemini (paid fallback) | P1 | | todo | |
| QL-11 | Cross-agent session handoff protocol | P1 | | todo | |
