# Plan — optional LangGraph StateGraph proof

**Date:** 2026-11-11
**Proposal:** `langgraph-biudl-integration`
**Item:** LGB-004
**Target branch:** `feat/autonomous-escalation-master-2026-11-09`
**Status:** implementation pushed; hosted validation pending

## Outcome

Add the smallest runnable Python `StateGraph` treatment that exercises the existing deterministic escalation policy without replacing native policy, introducing provider calls, or changing authorization.

## Non-goals

- No mandatory LangGraph dependency in Termux/base runtime.
- No model/provider/MCP calls or real side effects.
- No checkpointer, database, durable replay, or telemetry (LGB-005/LGB-006).
- No human approval interrupt or authorization expansion.
- No PR promotion until the repository's current-SHA gates are green.

## Implementation tasks

1. Add `she/recovery/langgraph_treatment.py` with typed state, policy decision node, bounded conditional routes, deterministic handoff/repair stubs, and an authorization-scope verifier.
2. Add `tests/test_langgraph_treatment.py` for specialist handoff, policy denial, local repair, independent verification, missing specialist, and authorization-scope mutation.
3. Isolate the optional dependency in `requirements-langgraph-test.txt`; keep `requirements-base.txt` unchanged.
4. Add a GitHub-hosted workflow to run graph tests and existing escalation policy tests under Python 3.11.
5. Update LGB-004 status, integration documentation, and the development-run record.

## Validation contract

- Run the graph test file and `test_autonomous_escalation.py` in the dedicated hosted workflow.
- Fetch the exact current PR head and check runs after dispatch/completion.
- Require repo gate and Termux smoke on the exact current head before promotion.
- Termux is currently offline; no Termux result is inferred or substituted.
- Do not mark LGB-004 complete or promote this PR until hosted test evidence and the repository dual gates are verified.
