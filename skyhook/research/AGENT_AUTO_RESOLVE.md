# Agent auto-resolve playbook

**Agent:** [Grok](https://x.com/grok) · Device: B160V · Credit note: Devin/Vercel may be exhausted — prefer Jules.

Reference discussion: PR #18 review thread (`discussion_r3710707215`).

## Quick matrix

| Mechanism | Who acts | Auto-apply code? |
|-----------|----------|------------------|
| Label `jules` on **issue** | Jules App | Yes (new session → PR) |
| `@jules` / `@Jules` on **PR comment** | Jules (esp. Reactive Mode) | Yes (commit to PR branch) |
| Jules UI settings: non-reactive | Jules reads review comments | Yes after 👀 |
| `google-labs-code/jules-invoke@v1` workflow | Jules API | Yes (cloud session) |
| Jules API `sessions.create` + `AUTO_CREATE_PR` | Any automation | Yes |
| `@coderabbitai autofix` | CodeRabbit | Yes (commit or stacked PR) |
| CodeRabbit Finishing Touches checkbox | CodeRabbit | Yes |
| CodeRabbit docstring / generate | CodeRabbit | Stacked PR (not on own PR) |
| Devin Review Auto-Fix | Devin | Yes when credits + enabled |
| Devin Automations (Linear/GH/CI) | Devin | Yes when credits |
| GitHub Copilot review | Copilot | Suggestions; human/agent apply |
| Grok (this agent) via PAT | Grok | Yes (push/PR) |

---

## 1. Jules — primary auto agent (preferred)

### A. Issue label (no workflow required)

1. Jules GitHub App installed on `timerloggedout-spec/termux-monorepo`.
2. Create label **`jules`** (case-insensitive).
3. Add label to an issue → Jules starts a task automatically.

### B. PR review comments (`@jules`)

From Jules changelog (Acts on PR Feedback):

- Default: Jules watches PR feedback on **its** tasks, reacts with 👀, then pushes commits.
- **Reactive Mode** (Jules UI → Settings → Pull Request): only acts when comment mentions **`@Jules` / `@jules`**.

**Practice for this repo:** always `@jules` in the comment body so behavior is predictable under Reactive Mode.

Example (merge conflicts / review fix):

```text
@jules Resolve conflicts vs master-staging. Keep 0o600/0o700 Sentinel patterns. Implements: TER-20
```

### C. GitHub Actions workflow (`jules-invoke`)

```yaml
# .github/workflows/jules-on-label.yml (template — install secret first)
name: Jules on label
on:
  issues:
    types: [labeled]
jobs:
  jules:
    if: github.event.label.name == 'jules' || github.event.label.name == 'bug'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: read
    steps:
      - uses: google-labs-code/jules-invoke@v1
        if: contains(fromJSON('["timerloggedout-spec"]'), github.event.issue.user.login)
        with:
          prompt: |
            Issue #${{ github.event.issue.number }}: ${{ github.event.issue.title }}
            ${{ github.event.issue.body }}
            Prefer base branch master-staging. Gate spine: master-staging → termux-smoke → master.
            B160V Termux: no Bun/Node as doctor deps. Agent signature: Grok coordinates; you implement.
          jules_api_key: ${{ secrets.JULES_API_KEY }}
          starting_branch: master-staging
```

Other workflow triggers from `jules-action` examples: **schedule**, **CI failure**, **issue closed** (unblocked), **workflow_dispatch**.

### D. Linear → Jules

Jules is **not** a Linear assignee user in this workspace. Pattern:

1. Linear issue with `**Agent: Jules | Grok**` at top + GitHub issue/PR link.
2. Sub-issue or linked GitHub issue labeled **`jules`**, **or**
3. Automation: Linear webhook / GHA / skyhook HTTP client → Jules API `POST .../sessions` with prompt including Linear ID (`Implements: TER-N`).

Optional: GitHub issue body contains `Implements: TER-N` and label `jules`.

### E. API (skyhook path)

`skyhook/bridge/http_client.py` + `JULES_API_KEY` — create sessions without Bun. Prefer host-side, not always-on Termux.

---

## 2. CodeRabbit — autofix suggestions

| Command / UI | Effect |
|--------------|--------|
| `@coderabbitai autofix` | Apply fixes on **current** PR branch |
| `@coderabbitai autofix stacked pr` | Open stacked PR with fixes |
| Finishing Touches **Autofix** checkbox | Same family of actions |
| Generate docstrings | Often **stacked** PR (see #26–#29) |

Config (repo root `.coderabbit.yaml`):

```yaml
reviews:
  auto_review:
    enabled: true
    drafts: false
    base_branches:
      - master
      - master-staging
  finishing_touches:
    autofix:
      enabled: true
```

**Limits:** CodeRabbit cannot edit **its own** PRs yet (noted on docstring PRs). Autofix needs write permission on the target branch.

---

## 3. Devin — when credits return

| Setting | Where |
|---------|--------|
| Auto-review repos | app.devin.ai → Settings → Review |
| **Auto-Fix** | Settings → Customization → Pull requests / Autofix; org admin |
| Respond to bot comments | Autofix settings → which bots to answer |
| Automations | Triggers: Linear label/assign, GH CI failure, PR comment `/devin` |

Without credits, **do not** assign Devin; use Jules + Grok + CodeRabbit autofix.

---

## 4. Other integrable bots / agents

| Bot | Role | Auto-resolve path |
|-----|------|-------------------|
| **google-labs-jules** | Coding agent | Label, @mention, Action, API |
| **coderabbitai** | Review + autofix + docstrings | `@coderabbitai autofix` |
| **devin-ai-integration** | Coding + review | Settings + Automations (credits) |
| **GitHub Copilot** | Review suggestions | `request_copilot_review`; apply manually or via agent |
| **Vercel** | Preview deploys | Not a code fixer |
| **ecc-tools** | ECC bundles | One-shot PRs |
| **Gitar** (seen on #18) | Auto-apply review fixes competitor | Optional third-party |
| **Sentry** | Issues → triage | Linear/Sentry hooks; agent fixes via Jules |
| **Grok** (xAI) | Orchestrator + implement via PAT | Push/PR; signature required |

---

## 5. Recommended HOME loop (credit-aware)

```
1. Open issue / Linear TER-N  →  label jules  OR  GHA jules-invoke
2. Jules opens PR → master-staging
3. CodeRabbit review → @coderabbitai autofix  (or checkbox)
4. Human/Grok: @jules for residual comments / conflicts
5. Gates → termux-smoke → master
```

**B160V:** all of the above run in **cloud**. Phone only smoke-tests.

---

## 6. Operator checklist (one-time)

- [ ] Jules App: repo access for `termux-monorepo`
- [ ] Label `jules` exists
- [ ] Secret `JULES_API_KEY` for Actions (if using `jules-invoke`)
- [ ] Jules UI: decide Reactive Mode on/off
- [ ] `.coderabbit.yaml` autofix + `master-staging` in `base_branches`
- [ ] Devin Auto-Fix: only when credits restored
- [ ] Never assign Operator except `termux-smoke` cherry-pick

Agent: Grok
Profile: https://x.com/grok
Signed-off-by: Grok <grok@x.ai>
