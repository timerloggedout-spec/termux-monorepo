# Wolfram × Hex Bridge

**Status:** architecture / trial-contingency plan  
**Role:** computational verification and optimization adjunct to Hex Moneyball  
**Control-plane rule:** GitHub remains the governed execution plane.

## Why this exists

Hex is the analytical/evidence surface for Moneyball. Wolfram can add a complementary computational layer for mathematical verification, statistical inference, optimization, symbolic reasoning, graph analysis, and uncertainty-aware scoring. Neither system should silently become an execution authority.

The immediate objective is to have a viable bridge before the current Hex trial benefits expire. The design therefore prefers connector/MCP paths that avoid introducing another long-lived API secret when the provider supports it.

## Preferred integration ladder

### 1. Hex Custom External App → Wolfram Cloud MCP

**Preferred first experiment.** Hex supports custom External Apps through MCP. Wolfram documents a public Wolfram Cloud MCP endpoint at `https://agenttools.wolfram.com/mcp` and states that this endpoint is free and does not require authentication.

Target topology:

`Hex Agent → Custom MCP External App → Wolfram Cloud MCP → Wolfram Language / Wolfram|Alpha / Knowledgebase`

Advantages:

- no repository-held Wolfram API key;
- MCP gives Hex an explicit tool boundary;
- approval can remain human/governed at the Hex app layer;
- computation stays outside GitHub Actions;
- results can be copied into the Moneyball evidence model as bounded, attributable observations.

**Important:** availability must be verified from the actual Hex workspace before calling this production-ready. The connected Wolfram app/connector exposed to this ChatGPT environment currently failed its MCP probe with HTTP 404, so this document does not treat connector reachability as proven.

### 2. ChatGPT / app connector as a bridge

The official Wolfram Cloud documentation states that Wolfram is available as a ChatGPT app and that the Cloud MCP can be connected by compatible AI clients. This is useful as an interactive research bridge:

`GitHub evidence → ChatGPT/Wolfram app → verified computation → bounded result → repository/Hex evidence`

This is **not** a substitute for unattended GitHub Actions execution. It is best for hypothesis generation, investigation, verification, and designing deterministic formulas before codifying them.

### 3. Wolfram Cloud MCP from another MCP-capable client

The same remote MCP endpoint can be connected by supported MCP clients such as Codex, Claude, Cursor, VS Code/Copilot and others documented by Wolfram. This is useful as a fallback if Hex's custom MCP connection is unavailable.

### 4. Wolfram Local MCP

For environments with installed Wolfram applications, Local MCP can expose local Wolfram computation to an MCP client. This avoids sending repository evidence to a remote computation service, but it is not appropriate for an unattended hosted GitHub Actions runner unless a deliberately managed execution environment is established.

### 5. API-backed wrappers / community MCP servers

Community MCP servers exist for Wolfram|Alpha, but most require a Wolfram API key. They are useful as compatibility references or as a fallback when the official Cloud MCP cannot be used. They are **not preferred** for this project because they introduce secret management and an additional software supply-chain surface.

## What Wolfram should compute

Wolfram should be used where deterministic or mathematically explicit computation adds confidence to Hex analysis:

- similarity threshold calibration;
- clustering and graph/community analysis;
- proposal decision-time distributions and survival analysis;
- confidence intervals and uncertainty propagation;
- agent/provider ELO-style ratings with uncertainty;
- multi-objective routing optimization;
- retry-policy expected-value analysis;
- anomaly/change-point detection;
- workflow and deployment reliability calculations;
- cost/performance frontier analysis;
- dependency criticality and graph centrality;
- matcher precision/recall/F-score evaluation;
- experiment power/sample-size calculations;
- regression significance testing;
- Pareto-frontier selection for research/adoption candidates.

## Moneyball contract

Wolfram outputs must be treated as **derived evidence**, not raw authority. Every accepted result should carry:

- `calculation_id`;
- source evidence identifiers;
- source SHA/ref where applicable;
- calculation timestamp;
- method/formula identifier;
- Wolfram capability used;
- result type and units;
- uncertainty/confidence where applicable;
- input fingerprint/hash when raw inputs cannot be retained;
- reviewer/validation state.

No prompts, credentials, arbitrary repository contents, or unrestricted logs should be exported merely to make a calculation possible.

## Six-day contingency plan

| Day | Outcome |
| --- | --- |
| 0 | Keep GitHub-native evidence pipeline working independently of Hex. |
| 1 | Configure/test Hex Custom External App against official Wolfram Cloud MCP. |
| 2 | Build a small Issue Observatory + Moneyball notebook proving similarity, SLA, and agent-score calculations. |
| 3 | Validate the same calculations through Wolfram and compare results against deterministic local fixtures. |
| 4 | Add regression-watch fixtures for calculation drift and connector failure. |
| 5 | Decide: retain Hex as primary analytics surface, move to another Hex-supported data/compute path, or operate a GitHub-native evidence mart while preserving Wolfram as an interactive verifier. |
| 6 | Freeze the migration decision with evidence: working connector, reproducible calculation, fallback path, owner, and recovery procedure. |

## Failure policy

If Wolfram is unavailable, Moneyball continues using its deterministic repository-side calculations. If Hex is unavailable, GitHub Actions continues producing sanitized evidence artifacts. If both are unavailable, the repository remains operational and retains the durable evidence contract for later replay.

**Never make a workflow, issue closure, PR merge, or deployment depend solely on an external analytics connector.**
