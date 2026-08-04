# Lean Termux Monorepo – Operating Rules

> **Purpose**: Keep the local Termux working tree small, fast, and restorable while the bulk of history, models, exports, and session data lives on GitHub + remote storage (Google Drive / rclone).

## Core Principles

1. **Local = Source + Config + Active Work only**
2. **Never commit**: models, `.venv`, `node_modules`, large session dumps, exports, binary weights
3. **Pull / cherry-pick → smoke-test → clean immediately**
4. **Heavy artefacts live on remote storage or as gitignored archives**

## Mandatory Workflow for Any Agent / Human

### Before starting work
```bash
cd "$HOME"
git status -sb
du -sh .git .cache .npm .cargo .local 2>/dev/null | sort -hr
```

### Pulling or cherry-picking a branch
```bash
# Preferred: fetch only what you need
git fetch origin <branch>
git cherry-pick <commit>          # or
git checkout -b temp/<name> origin/<branch>

# Smoke test (Termux-specific)
# … run your tests …

# Immediately after results are known:
git checkout master
git branch -D temp/<name>         # delete local branch
git reflog expire --expire=7.days.ago --all
git gc --prune=7.days.ago
```

### After every significant session
```bash
"$HOME/bin/lean-monorepo.sh"      # or the commands below
```

### Weekly / after heavy work
```bash
git reflog expire --expire=7.days.ago --all
git gc --prune=7.days.ago
rm -rf .cache/go-build .cache/node-gyp .cache/pip 2>/dev/null || true
# Optionally clear npm / cargo via termux-sync if not needed
# For aggressive pruning with immediate expiration, use:
#   git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

## Forbidden in the working tree (must be gitignored)

```
synthegration_exports/
forensic-indexer/whisper.cpp/models/
CTranslate2/                  # treat as external clone if needed
.deepcli/session_store/       # archive old sessions to Drive
.codex/cache/
*.onnx *.gguf *.pt *.safetensors *.bin
ARCHIVE_STAGING/
.venv/ venv/ node_modules/ __pycache__/
```

## Restoration Strategy

- Source of truth: `origin/master` + feature branches on GitHub
- Models / large exports / old sessions → Google Drive (or rclone)
- Submodules stay as submodules; never vendor large third-party trees
- If a tool needs a model: download on-demand into a gitignored path

## Agent Checklist (copy-paste into any agent prompt)

```
[LEAN RULES]
1. Never leave temporary branches.
2. After cherry-pick / test → delete branch + git gc --prune=now.
3. Never add model weights, session dumps, or exports to the index.
4. Run lean-monorepo.sh (or equivalent) before ending the session.
5. Prefer sparse-checkout or external clones for anything >50 MB.
```

## Quick Health Check

```bash
du -sh .git
git count-objects -vH
git status -sb
```

**Target**: `.git` < 200 MB under normal use.

---

*Last updated: 2026-08-03 – post 1.8 GB → 137 MB git cleanup*
