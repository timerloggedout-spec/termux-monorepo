# Proposals

**Agents: start at [`registry.yaml`](registry.yaml).**  
**Humans: start at [`PROCESS.md`](PROCESS.md).**  
**Permissions / why human still needed: [`AGENTIC-PERMISSIONS.md`](AGENTIC-PERMISSIONS.md).**

## Active

| ID | Priority | Status | Path |
|----|----------|--------|------|
| chatgpt-critical-eval | P0 | executing | [active/chatgpt-critical-eval/](active/chatgpt-critical-eval/) |
| chatgpt-initial | P2 | posted | [active/chatgpt-initial/](active/chatgpt-initial/) |
| chatgpt-droidapp | P2 | posted | [active/chatgpt-droidapp/](active/chatgpt-droidapp/) |

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
  legacy/          # optional mirrors of flat dumps
```

Flat historical files may still exist on `master`:

- `ChatGPT_Critical-Eval(TER0-15+other-branches).md`
- `ChatGPT-initial.md`
- `ChatGPT_droidApp.md`

New work uses the nested process only.
