# CEEL implementation and validation plan

**Design:** 2026-11-11-continuous-capability-evolution-lab.md  
**Proposal:** CCEL-001 through CCEL-006  
**Branch:** feat/ceel-continuous-capability-evolution-20261111

## Delivery strategy

Land a complete, reviewable foundation: proposal registration, capability graph contract and seed, deterministic validation, platform candidate records, event-path documentation, and DoE/Delphi integration map. Do not create external accounts, secrets, paid calls, production routing changes or a parallel scheduler.

## Task sequence

1. **Register and route.** Add proposal manifest/work items; register in docs/proposals/registry.yaml and docs/proposals/README.md; link from root CLAUDE.md. Validate with scripts/proposals/validate_registry.py.
2. **Add the opportunity graph.** Add strict JSON Schema and seed graph. Nodes represent four platform candidates, existing evaluators and repository capabilities. Edges represent competition, complementarity, measurement, consumption and evidence flow. Candidate nodes cannot be labeled integrated/validated without evidence. Test duplicate IDs, unresolved edges, invalid lifecycle states and malformed evidence.
3. **Register platform cohort.** Add Langfuse, PromptLayer, PostHog and Braintrust to docs/integrations/registry.json and INTEGRATION-REGISTRY.md. Update AGENT-EVALUATION-LANE-REGISTRY.md; external platforms remain observational. Do not claim connected, implemented, validated or promoted without runtime evidence.
4. **Integrate validation.** Extend existing integration-portfolio.yml to run graph validator/tests. Do not create a new cron or parallel workflow. Preserve contents: read.
5. **DoE/Delphi design.** Define four binary factors and 16 factorial combinations. Preregister cohorts, outcomes, evaluator versions, configured-instance tuple, blocking, assignment, replication and stopping rule. Use canonical experiment schema. Delphi compares proposals; EGM applies only under its stakes rule.
6. **Event-driven awareness.** Reuse PR, push, release, issue, workflow_run and repository_dispatch. Use provider webhooks when supported; otherwise bounded cursor reads. Existing integration mesh polling is recovery/reconciliation, not awareness. Add no weekly-only discovery scheduler.
7. **Validate and deliver.** Run in a full checkout:
   
   ```bash
   python3 scripts/integrations/validate_capability_graph.py
   python3 -m unittest discover -s tests -p 'test_capability_opportunity_graph.py' -v
   python3 scripts/integrations/validate_portfolio.py
   python3 scripts/proposals/validate_registry.py
   python3 scripts/ci/repo_gate.py
   python3 scripts/ci/termux_smoke.py
   ```

   Inspect diff and secret/privacy scan; open PR with Implements: CCEL-001, CCEL-002, CCEL-003, CCEL-004; WAIT for Actions; re-fetch checks/jobs/logs/artifacts; verify required gates on the same immutable head SHA; record review disposition and update ITEMS; merge/promote only under policy.

## Execution truth

GitHub object creation/retrieval is available; a local checkout and shell runner are not. CI runs are the executable validation evidence and must be observed before checks are reported passed. A successful commit or PR is not a substitute.
