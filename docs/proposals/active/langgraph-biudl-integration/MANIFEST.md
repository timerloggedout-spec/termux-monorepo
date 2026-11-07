# LangGraph BIUDL Integration — Manifest

**ID:** `langgraph-biudl-integration`  
**Priority:** P1  
**Status:** executing  
**Owner / executor:** ChatGPT  
**Operator authorization:** timerloggedout-spec (direct task instruction, 2026-11-06)  
**Target:** `master`  
**Branch:** `feat/langgraph-biudl-integration`

## Goal

Provision a repository-native LangGraph capability by extracting high-value practices from `vonzosten/awesome-LangGraph` and official LangChain skills, then adapting them to BIUDL, FA-ADE, existing orchestration/evidence contracts, and the Termux execution boundary.

## Scope

- Evidence-backed ecosystem reconnaissance.
- Repository-native `.agents/skills/langgraph-orchestration/SKILL.md`.
- Explicit integration boundary in `docs/ops/LANGGRAPH-BIUDL-INTEGRATION.md`.
- Mapping to existing orchestration treatment/receipt, OTEL, ATES, action/effect, evidence, Temporal, and SHE contracts.
- Skill inventory and discovery index updates.
- Follow-on runtime prototype, persistence/HITL, telemetry, and treatment comparison items.

## Out of scope for this slice

- Mandatory LangGraph dependency or production installation.
- LangSmith/LangSmith Platform requirement.
- Database, hosted service, model/provider credentials, or cloud deployment.
- Vendoring, submodules, forks, copying complete external skills, or adopting all Awesome list projects.
- Changes to existing manager routing, production workflows, or promotion authority.

## Sources

- `vonzosten/awesome-LangGraph` README blob: `e54d875ae645a03100346e2997acb8cfc43b0a14`
- `langchain-ai/langchain-skills` fundamentals blob: `adf7bff81897aa99d9505195a1196fced6047b97`
- Human-in-the-loop blob: `d762f2a170c30310b5641642af3e19ce7866a28a`
- Persistence blob: `bbcf0ea77bf2b374a99e5d08cae147c12da03e82`

## Gates

- Repository gate: `python3 scripts/ci/repo_gate.py`
- Termux smoke: `python3 scripts/ci/termux_smoke.py`
- No promotion without both gates green on the current SHA and task outcome verified.
