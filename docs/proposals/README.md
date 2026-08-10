# Proposals

**Agents: start at [`registry.yaml`](registry.yaml).**
**Humans: start at [`PROCESS.md`](PROCESS.md).**
**Permissions: [`AGENTIC-PERMISSIONS.md`](AGENTIC-PERMISSIONS.md).**

## Active (on this branch base)

| ID | Priority | Status | Path |
|----|----------|--------|------|
| chatgpt-critical-eval | P0 | executing | [active/chatgpt-critical-eval/](active/chatgpt-critical-eval/) |
| chatgpt-initial | P2 | posted | [active/chatgpt-initial/](active/chatgpt-initial/) |
| chatgpt-droidapp | P2 | posted | [active/chatgpt-droidapp/](active/chatgpt-droidapp/) |

## Related process PRs (not all present on every base)

| PR | What |
|----|------|
| [#68](https://github.com/timerloggedout-spec/termux-monorepo/pull/68) | Kimi cloud-offload registry + `scripts/proposals/*` + vote/promote |
| [#69](https://github.com/timerloggedout-spec/termux-monorepo/pull/69) | Debate dock TOC + hygiene |
| [#67](https://github.com/timerloggedout-spec/termux-monorepo/pull/67) | PR scope discipline (CE-22) |
| [#70](https://github.com/timerloggedout-spec/termux-monorepo/pull/70) | Projects / milestones / connectors inventory (conditional) |

Prefer the registry on disk over comments that invent missing paths.

## Layout

```
proposals/
  PROCESS.md
  AGENTIC-PERMISSIONS.md
  registry.yaml
  README.md
  _template/MANIFEST.md
  active/<id>/{MANIFEST.md,ITEMS.md,...}
  closed/<id>/
  legacy/
```

Flat historical files may still exist on `master`:

- `ChatGPT_Critical-Eval(TER0-15+other-branches).md`
- `ChatGPT-initial.md`
- `ChatGPT_droidApp.md`

New work uses the nested process only.

Optional navigation: [`.github/PROJECTS.md`](../../.github/PROJECTS.md) when present on the branch.
