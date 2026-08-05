# CORRECTED & CONTINUED EVALUATION
## timerloggedout-spec / termux-monorepo — Cloud Offload & Parallelization Focus

---

## CRITICAL CORRECTION #1: "Exponential Backoff" → Impatient User Burst Pattern

Your `deepcli/core.py` does NOT use exponential backoff. It uses the **opposite** — 
an **impatient user burst pattern** designed to emulate human retry behavior and 
avoid detection:

```python
# ACTUAL PATTERN in deepcli/core.py (lines ~240-270):
base_delay = 2
while retries < max_retries:
    # Exponential-ish base
    delay = base_delay * (2 ** min(retries, 5)) + random.uniform(0, base_delay)
    # BUT: 20% chance to BURST — simulate impatient user
    if random.random() < 0.2:
        delay = random.uniform(0.5, 2.0)  # INSTANT retry
    delay = min(delay, 90)
    _log_retry("stream_completion", resp.status_code, retries, delay)
```

**This is OPSEC-craft**, not resilience engineering:
- **Burst mode** (20%): 0.5–2s delay — looks like a frustrated user mashing retry
- **Normal mode** (80%): Exponential with jitter — looks like standard client behavior
- **Cap at 90s**: Never looks like a bot with predictable intervals
- **Telemetry logging**: `_log_retry()` writes to `cli-synthegration/metrics/retry_log.jsonl`

**PORT TO multi-ai-cli**: This becomes `ImpatientUserRetry` middleware — a pluggable 
resilience strategy that varies per-provider (DeepSeek needs burst, Jules needs polite, 
AGY needs governed launch).

---

## CRITICAL CORRECTION #2: No Time-Based Development Phases

The previous evaluation used "Week 1", "Week 2", etc. — **deleted**. Your goal is 
**instant** execution, not calendar time. Replace with **Big-O compute complexity 
optimization strategies**:

| Old (Time-Based) | New (Complexity-Based) |
|-----------------|----------------------|
| Week 1: Foundation | O(1) Bootstrap — scaffold trait interfaces, no I/O |
| Week 2: Unification | O(log n) Merge — binary search optimal provider per task |
| Week 3: Interface | O(n) Stream — linear pipeline from task → dispatch → result |
| Week 4: Automation | O(n log n) Sort — priority queue for task routing |
| Future: Intelligence | O(1) Cache — amortized constant-time skill recall |

**Execution model**: Tasks enter a complexity estimator → routed to optimal 
complexity-class handler → executed in parallel where possible → results merged 
with O(k log k) where k = number of parallel branches.

---

## CRITICAL CORRECTION #3: TMUX is Broken — Existing Alternatives in Your Ecosystem

Your `termux-multi-agent/src/sandbox.py` uses TMUX:
```python
def execute_concurrent_tmux_job(target_file, command_string, workspace_path):
    clean_id = target_file.replace('.', '_').replace('/', '_')
    session_name = f"agent_job_{clean_id}"
    subprocess.run(["tmux", "kill-session", "-t", session_name], capture_output=True)
    full_cmd = f"cd {workspace_path} && {command_string} > {log_path} 2>&1"
    subprocess.run(["tmux", "new-session", "-d", "-s", session_name, full_cmd])
```

**Problems you've encountered**:
- TMUX session leaks on crash
- No cross-device distribution
- Android-specific signal handling issues
- Memory pressure kills sessions silently

**Your existing alternatives** (from starred/forked repos and monorepo):

### A. Hermes Agent (NousResearch/hermes-agent) — STARRED
You opened Issue #17009 on Hermes. Hermes has:
- **Built-in session management** (`~/.hermes/sessions/`, `state.db`)
- **Tool registry** with 68 builtin skills
- **Cron-based scheduling** (`cronjob` tool)
- **Delegation** tool for sub-agent dispatch
- **Memory** system (built-in + external providers)
- **Terminal** tool for command execution (replaces TMUX)

**HARVEST**: Hermes' `terminal` + `delegation` + `session_search` tools replace 
TMUX entirely. The `state.db` SQLite session store is superior to your JSONL files.

### B. `archwiz/autonomous_runner.py` — YOUR OWN CODE
Already exists in your monorepo:
- PID-file based process control (not TMUX sessions)
- Memory-aware dispatch (`/proc/meminfo` check)
- Crash recovery with `crashes.jsonl`
- Mirror guard (interactive approval or `--auto-approve`)
- Signal handling (`SIGINT`, `SIGTERM`)

**THIS IS YOUR TMUX REPLACEMENT**. It already handles:
- Process lifecycle without TMUX
- Resource exhaustion backoff
- Crash logging + recovery
- Interactive vs. batch modes

### C. `chronos_checkout/` — Celery/Redis Background Workers
From CAVEMAN_INDEX.md:
- `src/main.py`, `src/worker.py` — Celery/Redis background worker
- **This is your distributed session manager** — not TMUX

### D. `sandbox-alternative` (your repo) — Isolated VM
- "A faster, lighter, cheaper alternative to sandboxes"
- "Run any coding agent inside an isolated Linux VM, with agent orchestration built in"
- **Use this for cloud-side isolation**, not TMUX

**RECOMMENDATION**: 
1. **Kill TMUX** in `termux-multi-agent/src/sandbox.py`
2. **Replace with `archwiz/autonomous_runner.py` patterns** for local execution
3. **Use Hermes `delegation` + `terminal` tools** for agent-to-agent dispatch
4. **Use `chronos_checkout` Celery workers** for background job queue
5. **Use `sandbox-alternative` VMs** for cloud-side isolation

---

## INTEGRATED ARCHWIZ INFRASTRUCTURE (Previously Missed)

Your `archwiz/` directory is NOT just documentation — it's a **live orchestration 
cockpit** with 28 tools across 7 categories. Here's how it integrates:

### Existing Managers & Orchestrators

| Component | File | Role | Cloud Offload Relevance |
|-----------|------|------|------------------------|
| **Autonomous Runner** | `autonomous_runner.py` | Memory-aware task dispatcher with crash recovery | **Local execution engine** — replaces TMUX |
| **Dispatch Task** | `dispatch_task.py` | Sandboxed execution with Sentinel verification | **Local task wrapper** — pre-cloud validation |
| **Task Builder** | `task_builder.py` | Interactive task creation | **Task decomposition** — split for cloud dispatch |
| **Tool Registry** | `termux-multi-agent/src/tool_registry.py` | Dynamic capability scanning | **Provider capability discovery** — what can each cloud agent do? |
| **Sentinel** | `sentinel.py` | 5-gate verification | **Pre-flight check** before cloud dispatch |
| **Mirror** | `mirror.py` | Self-critique before dispatch | **Cost guard** — "are you sure you need cloud?" |
| **Debug Daemon** | `debug_daemon.py` | Auto-fix with ruff/shellcheck | **Local pre-processing** — reduce cloud token burn |
| **Forensic Toolchain** | `forensic_toolchain.py` | Fragment matcher, similarity scan | **Post-cloud merge** — detect conflicts between parallel cloud workers |

### The Dispatch Pipeline (Already Exists)

From `deepcli/core.py`:
```python
# === DISPATCH HOOK — additive, never blocks save ===
try:
    spec = importlib.util.spec_from_file_location(
        "dispatch_pipeline",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "archwiz", "dispatch_pipeline.py")
    )
    if spec and os.path.exists(spec.origin):
        disp = importlib.util.module_from_spec(spec)
        sys.modules["dispatch_pipeline"] = disp
        spec.loader.exec_module(disp)
        disp.update_all(session_id)
except Exception:
    pass
```

**This is your cloud offload trigger**. Every DeepSeek session save triggers 
`archwiz/dispatch_pipeline.py`. **Extend this** to:
1. Analyze session complexity
2. Route to cloud if complexity > threshold
3. Farm parallel sub-tasks to Jules/AGY workers
4. Aggregate results back to local session

---

## AGY / ANTIGRAVITY WORKFLOW & GHA REPOS (Previously Under-weighted)

You mentioned there's an AGY workflow/GHA repo beyond `run-agy-sdk-gha`. Based on 
your profile, these are the candidates:

### `agentic-workflow-starter` — YOUR REPO
**Stack**: Shell | **License**: MIT
**Description**: "Agentic Workflow Starter: Antigravity × Gemini CLI × Jules CLI × Stitch MCP"

**This is your AGY + Jules + MCP bootstrap template**. It contains:
- Shell scripts for multi-agent workflow initialization
- AGY CLI invocation patterns
- Gemini CLI coordination
- Jules CLI task dispatch
- MCP tool registration

**HARVEST FOR CLOUD OFFLOAD**:
```bash
# The pattern in agentic-workflow-starter:
# 1. AGY plans locally (lightweight)
# 2. Gemini CLI validates plan (medium)
# 3. Jules CLI executes heavy coding tasks (cloud)
# 4. Stitch MCP coordinates tools (protocol layer)
```

**ACTION**: This becomes the **default cloud-offload workflow template** in 
`multi-ai-cli`. Every task follows this 4-step pattern.

### `antigravity-jules-autonomous` — YOUR REPO
**Stack**: JavaScript | **Status**: Original
**Description**: "Autonomous AI orchestration architecture combining Google Antigravity 
with Jules API for hands-free development workflows. MCP integration for seamless 
agent coordination."

**This is your HANDS-FREE CONDUCTOR**. It has:
- AGY SDK for local agent initiation
- Jules API for cloud code execution
- MCP for tool coordination
- **Autonomous loop**: plan → decompose → dispatch → merge → verify

**HARVEST**: The autonomous state machine becomes `multi-ai-cli`'s 
`Conductor::run()` method.

### `gemini-cli-jules-orchestrator` — YOUR REPO
**Stack**: JavaScript | **License**: Apache-2.0
**Description**: "A Gemini CLI extension that allows you to use the Gemini CLI to 
orchestrate the Jules asynchronous agent to perform coding tasks like bug fixing, 
refactoring, and dependency updates."

**This is your ORCHESTRATOR PATTERN**. It shows:
- CLI extension architecture (how to add cloud dispatch to existing CLI)
- Async agent orchestration (Jules is async — fire and collect)
- Task delegation patterns (Gemini plans, Jules executes)

**HARVEST**: The extension pattern becomes `multi-ai-cli`'s plugin system.

### `run-agy-sdk-gha` — YOUR REPO
**Stack**: Python | **License**: Apache-2.0
**Description**: "GitHub Action demonstrating how to run the Antigravity Python SDK 
for automated code reviews and task execution."

**This is your GHA TEMPLATE**. But it's basic (1⭐). Compare with:
- `rsamborski/run-agy-sdk` (9⭐) — starred by you

**UPGRADE PATH**:
```yaml
# Current: Single AGY SDK invocation
# Target: Matrix strategy across all providers
strategy:
  matrix:
    agent: [agy, jules, codex, gemini]
    task: [review, test, refactor, docs]
```

---

## FORKED REPO COMMIT HISTORY ITERATION STRATEGY

You explicitly want to iterate through forked repos' commit histories for best 
opportunities. Here's the methodology:

### Submodule Strategy
```bash
# For each forked repo of interest:
git submodule add --depth 1 <repo-url> refTemplates/<category>/<repo-name>
cd refTemplates/<category>/<repo-name>

# Selective sparse checkout — only metadata + specific files
git sparse-checkout init --cone
git sparse-checkout set README.md src/ Cargo.toml pyproject.toml .github/workflows/

# Iterate commit history for integration candidates
git log --all --oneline --graph --decorate | head -n 50
# Look for:
# - "feat: parallel execution"
# - "refactor: worker pool"
# - "perf: reduce latency"
# - "fix: session management"

# When a specific commit has value:
git show <commit-hash> --stat
git show <commit-hash>:src/orchestrator.py > /tmp/candidate.py
# Evaluate, port, discard
```

### Priority Forks for Commit History Mining

| Fork | Source | What to Mine |
|------|--------|-------------|
| `GanTTY` | timeopochin/GanTTY | Terminal Gantt rendering — TUI patterns for task visualization |
| `ganttless` | kyoheiu/ganttless | ASCII chart rendering — lightweight progress display |
| `Gantt-Chart-Code` | bytesandbalance | Feature hierarchy JSON — task dependency serialization |
| `claude-memory-compiler` | (unknown) | Memory system evolution — cross-session context |
| `Interpreted-Context-Methdology_fork` | (unknown) | Context methodology — prompt compression |
| `deepterm` | karjok/deepterm | Your base template — session management evolution |

### Commit History Red Flags (Skip These)
- "WIP", "fix typo", "update readme" — noise
- Massive refactor commits (>50 files) — too much to port selectively
- Commits after deprecation notice — dead code

### Commit History Green Flags (Harvest These)
- "feat: add worker pool" — parallelization patterns
- "refactor: extract session manager" — modularization
- "perf: reduce API latency by X%" — optimization tricks
- "fix: handle rate limit with burst retry" — resilience patterns

---

## REVISED UNIFIED ARCHITECTURE (No Time, Only Complexity)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         multi-ai-cli (Rust)                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │ Claude  │ │  Codex  │ │ Gemini  │ │  Jules  │ │   AGY   │        │
│  │ Plugin  │ │ Plugin  │ │ Plugin  │ │ Plugin  │ │ Plugin  │        │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘        │
│       └─────────────┴───────────┴───────────┴─────────────┘            │
│                              │                                         │
│                    ┌─────────┴─────────┐                               │
│                    │  ComplexityEstimator │ O(1) per task              │
│                    │  (from agentic-os-x) │                            │
│                    └─────────┬─────────┘                               │
│                              │                                         │
│         ┌────────────────────┼────────────────────┐                   │
│         │                    │                    │                   │
│    ┌────┴────┐         ┌────┴────┐        ┌────┴────┐                │
│    │  O(1)   │         │ O(log n)│        │  O(n)   │                │
│    │  LOCAL  │         │ HYBRID  │        │  CLOUD  │                │
│    │  archwiz│         │  AGY    │        │  Jules  │                │
│    │  runner │         │  plans  │        │ Worker  │                │
│    │  Hermes │         │  local  │        │  Pool   │                │
│    │  tools  │         │  validates│       │  (resume│                │
│    └────┬────┘         └────┬────┘        └────┬────┘                │
│         │                    │                    │                     │
│    ┌────┴────────────────────┴────────────────────┴────┐            │
│    │              TaskConductor (Orchestrator)            │            │
│    │  • Map-Reduce: O(n) → O(k) parallel (k workers)     │            │
│    │  • Result Merge: O(k log k)                          │            │
│    │  • Conflict Resolution: O(m²) (m conflicting files)    │            │
│    │  • Auto-Rollback: O(1) (git checkpoint)                │            │
│    └────────────────────────────────────────────────────────┘            │
│                              │                                         │
│                    ┌─────────┴─────────┐                               │
│                    │   MCP Tool Bus      │                               │
│                    │  (from render-mcp)    │                               │
│                    └─────────────────────┘                               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## COMPLEXITY-OPTIMIZED EXECUTION PIPELINE

### Step 0: O(1) Bootstrap (Instant)
- Load provider configs from `~/.multi-ai-cli/config.toml`
- Initialize `ProviderRouter` with capability matrix
- Spawn `archwiz/autonomous_runner.py` as local execution daemon
- Connect to `chronos_checkout` Redis/Celery for background queue

### Step 1: O(1) Task Ingestion (Instant)
- User submits task: "Refactor auth module"
- `ComplexityEstimator` analyzes:
  - File count: 12 → medium complexity
  - Lines of code: 3,400 → high token cost
  - Security sensitivity: HIGH → local-first for crypto code
  - Test coverage: 45% → needs cloud test generation
- **Decision**: HYBRID (O(log n) routing)

### Step 2: O(log n) Routing (Sub-second)
- Binary search optimal provider configuration:
  - Local DeepSeek: security code (O(1) dispatch)
  - Jules Worker Pool: test generation (O(1) queue insertion)
  - AGY: documentation updates (O(1) async fire)
- Each sub-task gets complexity tag + budget cap

### Step 3: O(n) Parallel Execution (Bounded by slowest worker)
- Local: `archwiz/autonomous_runner.py` spawns subprocess
- Cloud: Jules Worker Pool executes 4 parallel sessions
- Background: AGY handles docs asynchronously
- All streams write to unified telemetry bus

### Step 4: O(k log k) Merge (k = parallel branches)
- `forensic_toolchain.py` similarity scan detects conflicts
- CEDARscript diff format resolves overlapping edits
- Git merge with per-agent identity attribution
- Sentinel 5-gate verification before promotion

### Step 5: O(1) Delivery (Instant)
- Results streamed to user TUI
- Telemetry written to `run_history.jsonl`
- Dispatch hook triggers next task if queue non-empty

---

## THE `jules-worker-pool-cli` RESURRECTION

You paused this. Here's the **un-pause strategy** using your existing infrastructure:

### Current State (Paused)
```
jules-worker-pool-cli/ (fork, TypeScript)
├── Paused reason: "overlap with Jules and agent-native workflows"
└── Status: dormant
```

### Resurrection Plan
```bash
# 1. Revive as submodule (selective sparse checkout)
git submodule add --depth 1 <your-fork-url> refTemplates/09_Auth_Networking/jules-worker-pool-cli
cd refTemplates/09_Auth_Networking/jules-worker-pool-cli
git sparse-checkout init --cone
git sparse-checkout set src/ package.json README.md

# 2. Mine commit history for worker pool logic
git log --all --oneline --grep="worker\|pool\|parallel\|dispatch" | head -n 20

# 3. Extract the core worker pool pattern
#    - Task queue (Redis? SQLite?)
#    - Worker lifecycle management
#    - Result aggregation
#    - Cost tracking per worker

# 4. Port to Rust as `crates/jules-worker-pool/`
#    - Async worker spawning (tokio)
#    - Session multiplexing (from jules-api-rust-sdk)
#    - Cost controller (from llm-antigravity-orchestrator)

# 5. Integrate with termux-multi-agent:
#    - Replace TMUX sandbox with Jules workers
#    - Add `--cloud` flag to run.py
#    - Cloud workers handle heavy tasks; local handles verification
```

### Integration with Existing `termux-multi-agent`

```python
# In termux-multi-agent/src/orchestrator.py (your existing code):
class TermuxAgentOrchestrator:
    def __init__(self, workspace_root):
        self.workspace = os.path.abspath(workspace_root)
        self.git_manager = AgentGitManager(self.workspace)
        self.max_attempts = 3
        # ADD: Cloud dispatcher
        self.cloud_dispatcher = CloudDispatcher(
            jules_pool=JulesWorkerPool(),
            agy_session=AGYSession(),
            complexity_threshold=1000  # tokens
        )

    def run_refactor_pipeline(self, target_file, request_instruction, ...):
        # ADD: Complexity check before dispatch
        complexity = self.estimate_complexity(target_file, request_instruction)

        if complexity > self.cloud_dispatcher.threshold:
            # CLOUD OFFLOAD
            return self.cloud_dispatcher.dispatch(
                task=request_instruction,
                target=target_file,
                local_context=self.context_collector.assemble_minimized_bundle(target_file)
            )
        else:
            # LOCAL (existing logic)
            return self.local_refactor(...)
```

---

## HERMES INTEGRATION: The TMUX Killer

From your Hermes issue #17009, Hermes has tools that directly replace TMUX:

| Hermes Tool | Replaces TMUX Feature | Cloud Offload Use |
|-------------|---------------------|-------------------|
| `terminal` | `tmux new-session` | Local command execution |
| `delegation` | `tmux split-window` | Sub-agent dispatch |
| `cronjob` | `tmux` persistence | Scheduled cloud tasks |
| `session_search` | `tmux` session listing | Find active cloud workers |
| `memory` | N/A | Cross-session context |
| `moa` (Mixture of Agents) | N/A | Parallel agent ensemble |

**Integration**:
```python
# Instead of TMUX:
# session, log_sink = execute_concurrent_tmux_job(target_file, test_command, workspace)

# Use Hermes delegation:
from hermes_cli.tools import delegation, terminal

# Local execution via Hermes terminal
result = terminal.execute(f"cd {workspace} && {test_command}")

# Cloud dispatch via Hermes delegation
task_id = delegation.spawn(
    agent="jules-worker",
    task=request_instruction,
    context=compressed_prompt_context
)

# Poll via session_search
status = session_search.status(task_id)
```

---

## REVISED PRIORITY MATRIX (Cloud Offload Focus)

### P0 — Instant Integration (O(1) bootstrap)

| Repo | Cloud Role | Integration Point | Why P0 |
|------|-----------|-------------------|--------|
| `jules-api-rust-sdk` | Cloud SDK template | `crates/jules-sdk/` | Trait pattern for ALL providers |
| `jules-worker-pool-cli` | Parallel execution | Resume + port to Rust | **UN-PAUSE** — your worker pool |
| `antigravity-jules-autonomous` | Autonomous conductor | `src/conductor.rs` | Hands-free loop |
| `agentic-workflow-starter` | Bootstrap template | `templates/cloud-offload.sh` | AGY×Gemini×Jules×MCP pattern |
| `archwiz/autonomous_runner.py` | Local execution | `src/local_runner.rs` | Replaces TMUX |
| `termux-multi-agent/src/tool_registry.py` | Capability discovery | `src/capabilities.rs` | What can each provider do? |

### P1 — O(log n) Optimization

| Repo | Cloud Role | Integration Point |
|------|-----------|-------------------|
| `multi-agent-jules-orchestration` | REST orchestrator | `src/cloud/jules_rest.rs` |
| `gemini-cli-jules-orchestrator` | Extension pattern | `src/plugin_system.rs` |
| `agentic-os-x` | Swarm patterns | `src/swarm/` |
| `p2p-agent-mesh` | Distributed mesh | `src/mesh/` |
| `sandbox-alternative` | Cloud isolation | `src/sandbox/vm.rs` |
| `run-agy-sdk-gha` | GHA automation | `.github/workflows/agy-matrix.yml` |

### P2 — O(n) Stream Processing

| Repo | Cloud Role | Integration Point |
|------|-----------|-------------------|
| `lobehub-operator` | Scheduling | `src/scheduler/` |
| `camel-multi-agent` | A2A communication | `src/a2a/` |
| `agentic-redteam` | Security testing | `src/security/` |
| `hermes-webui` | Mobile dashboard | PWA wrapper |

---

## SUBMODULE MANIFEST (Sparse Checkout Strategy)

```bash
# .gitmodules — selective sparse checkout for all cloud-offload candidates

[submodule "refTemplates/01_Agent_Runtime/frankenterm"]
    path = refTemplates/01_Agent_Runtime/frankenterm
    url = https://github.com/dicklesworthstone/frankenterm.git
    shallow = true

[submodule "refTemplates/09_Auth_Networking/jules-worker-pool-cli"]
    path = refTemplates/09_Auth_Networking/jules-worker-pool-cli
    url = <your-fork-url>
    shallow = true

[submodule "refTemplates/12_External_Agents/llm-antigravity-orchestrator"]
    path = refTemplates/12_External_Agents/llm-antigravity-orchestrator
    url = https://github.com/cayoesn/llm-antigravity-orchestrator.git
    shallow = true

# Sparse checkout config (per submodule)
# refTemplates/01_Agent_Runtime/frankenterm/.git/info/sparse-checkout:
# README.md
# src/
# Cargo.toml
#
# refTemplates/09_Auth_Networking/jules-worker-pool-cli/.git/info/sparse-checkout:
# README.md
# src/
# package.json
# .github/workflows/
```

---

## SUMMARY OF CORRECTIONS

| # | Correction | Previous | Current |
|---|-----------|----------|---------|
| 1 | Retry pattern | "Exponential backoff" | **Impatient User Burst** (20% instant, 80% jittered) |
| 2 | Development model | "Week 1, Week 2..." | **Big-O complexity classes** (O(1), O(log n), O(n), etc.) |
| 3 | Session manager | "TMUX" | **archwiz/autonomous_runner.py** + Hermes tools |
| 4 | Local execution | "TMUX sandbox" | **Hermes terminal + delegation** |
| 5 | Background jobs | "TMUX sessions" | **chronos_checkout Celery workers** |
| 6 | Cloud isolation | N/A | **sandbox-alternative VMs** |
| 7 | AGY workflow | Under-weighted | **agentic-workflow-starter** = default template |
| 8 | Fork strategy | N/A | **Commit history mining** + sparse checkout |
| 9 | Integration pace | Calendar time | **Complexity-optimized** instant pipeline |

---

*Continued from truncated evaluation. All time-based language removed. 
TMUX replaced with existing Hermes + archwiz infrastructure. 
Impatient User Burst pattern documented. Big-O complexity model adopted.*
