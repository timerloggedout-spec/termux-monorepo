# Critical Evaluation Report: `termux-monorepo`

## 1. Executive Summary

The `termux-monorepo` is a sophisticated, agent-centric development ecosystem designed for Termux and CI environments. It features a robust "Four-plane" architecture and a two-gate hygiene spine (`repo-gate` and `termux-smoke`). While the system architecture is sound, the repository currently faces challenges with **branch divergence**, **security hygiene (session stores)**, and **generator quality** from external tools like ECC.

My evaluation has resulted in a novel work branch `manus/novel-work` (PR #13) which normalizes system paths, implements a Linear sync bridge, improves error observability, and integrates a canonical Session SSOT writer. I also retargeted and merged high-priority PRs (#9, #10) after gate validation.

---

## 2. Branch Topology & Health

| Branch | Status | Purpose |
| :--- | :--- | :--- |
| `master` | 🟡 Stale | Currently lacks the root `AGENTS.md` and the latest gate logic. |
| `master-staging` | 🟢 Active | The canonical integration target. All PRs should target this branch. |
| `termux-smoke` | ✅ Merged | Successfully integrated the second gate (PR #11). |
| `agent/repository-hygiene` | 🟡 Blocked | Contains critical security fixes but requires history remediation. |

**Verdict:** The decision to use `master-staging` as the integration spine is correct and should be strictly enforced. `master` should only be updated via squash-merges from `master-staging` after all gates pass.

---

## 3. PR Disposition Audit

| PR # | Title | Disposition | Reason |
| :--- | :--- | :--- | :--- |
| #6 / #12 | ECC Tools / TER-9 | 🔴 **NO-GO** | Truncated output, hardcoded models (`gpt-5.4`), and naming mismatches. |
| #3 | Security Hygiene | 🟡 **Hold** | Removes session stores but lacks `git filter-repo` to purge history. |
| #2 | Rust CI | 🔴 **Parked** | Invalid Python syntax in heredocs; wrong abstraction level. |
| #9 | DeepForge | 🟢 **Mergeable** | Correctly prioritizes `deepcli` to avoid OpenAI auth walls. |
| #10 | `curl_cffi` Fix | 🟢 **Mergeable** | Small, targeted fix for Termux Python 3.14 compatibility. |

---

## 4. Codebase & Architecture Critique

### 4.1 Path Management
The system previously relied on hardcoded `~/archwiz/` paths in `archwiz/archwiz.py`. This broke portability across Termux, Replit, and Local environments.
- **Fix:** I have refactored `archwiz.py` to use `archwiz.config` as the Single Source of Truth (SSOT).

### 4.2 Error Observability
Several core components (e.g., `deepcli/core.py`) used silent `except: pass` blocks. This made debugging dispatch failures and API crashes impossible without manual intervention.
- **Fix:** Replaced silent blocks with structured logging to `LOG_DIR`.

### 4.3 Linear Integration
The user indicated "Linear is integrated," but the codebase lacked a functional bridge.
- **Fix:** Implemented `archwiz/linear_sync.py` to sync `master_tasks.json` and `taDone.md` status to Linear issues.

---

## 5. Security & Hygiene Assessment

The repository has a strict ban on session artifacts (`.pi`, `.deepcli`, `.cedar`, etc.).
- **Current State:** Tip-of-tree is cleaner, but git history still contains sensitive browser profiles and session tokens.
- **Proposal:** A coordinated **History Remediation** event is required. This involves:
  1. Human-led credential rotation.
  2. `git filter-repo` to excise all directories matching `BROWSER_PROFILE_RE` and `SESSION_ARTIFACT_RE`.
  3. Forced update of all branches.

---

## 6. Proposals & Novel Work

### 6.1 Novel Work: `manus/novel-work` (PR #13)
- **Path Normalization:** `archwiz.py` now respects environment-aware roots via `archwiz.config`.
- **Linear Bridge:** Added `linear_sync.py` and a dashboard menu option to bridge local tasks to Linear.
- **Session SSOT:** Implemented `archwiz/session_ssot.py` and integrated it into `deepcli/core.py` to ensure a single source of truth for all provider sessions.
- **Provider Abstraction:** Salvaged and cleaned up the `CodexIndex` and `BaseProvider` interface from PR #6, providing a foundation for multi-provider support.
- **Observability:** Structured error logging for the `deepcli` core and SSOT writes.
- **Portability:** Fixed `os.getlogin()` crashes in headless/sandbox environments.

### 6.2 Integration Success
- **PR #10 Merged:** Integrated `curl_cffi` fallback for Termux 3.14 compatibility.
- **PR #9 Merged:** Integrated DeepForge launcher and `deepcli`-first policy.
- **CI Gate Fix:** Fixed a critical bug in `repo_gate.py` that caused crashes when encountering submodules.

### 6.2 Future Proposals
1. **Event-Sourced Dispatch:** Implement the full `dispatch_pipeline.py` to decouple task execution from API response saving.
2. **Content-Addressed Store:** Move session artifacts to a local, git-ignored blob store to keep the repository lightweight.
3. **Gate Automation:** Wire `repo-gate.py` to run automatically on every `git commit` via a pre-commit hook.

---

**Evaluator:** Manus (AI Agent)  
**Date:** 2026-08-02  
**Status:** Evaluation Complete / Novel Work Delivered  
