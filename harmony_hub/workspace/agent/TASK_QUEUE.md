# Agent Task Queue

## 1. TUI – Version Timeline Branch Visualization
**Goal**: Add a `/timeline` command that shows a visual tree of message branches over time, with timestamps on the X-axis and branch depth on the Y-axis.

## 2. TUI – Message Section Selection
**Goal**: Add ability to select a portion of a message (paragraph/sentence), copy it to `/tmp/edit_snippet.txt`, allow editing, then re-send as a branch or save.

## 3. CedrLang Integration
**Goal**: Wire `patch_router.py` into the orchestrator so that patches from the LLM can be applied via CEDARscript, sed, or raw Python depending on the patch format.

## 4. Account2 Full Activation
**Goal**: Run a refactoring task using the secondary account token, verify it logs to `run_history` with `account='secondary'`, and ensure ELO updates per-account.

## 5. Time Loop Accelerator Agentic Role
**Goal**: Extend `session_productivity.py` to trigger agent actions when productivity drops (e.g., suggest a prompt change, switch agent).
