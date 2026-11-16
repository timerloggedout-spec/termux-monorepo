# smods — governed custom-fork integration lane

This directory is the **live custom-adapted gitlink lane** for reviewed upstream references. It is not a package cache and not a place to copy upstream source directly.

## Integration flow

```text
refTemplates/<runtime-or-research-template>/
  README.md + SOURCE.txt + integration.json
                    |
                    v
refTemplates/smods/INTEGRATIONS.json
  fork_required -> reviewed fork -> immutable pin
                    |
                    v
.gitmodules + 160000 gitlink + dual-gate evidence
```

Every integration template must record its smods disposition. A planned fork is **not** a gitlink, and a fork name in a JSON file is not evidence that the repository exists. The validator rejects a `pinned` record without both a matching `.gitmodules` entry and a 160000 gitlink.

The Vercel agent toolchain template currently records `agent-browser` as `fork_required`. No fork or submodule is asserted. Keep upstreams metadata-only until repository-specific changes are justified, license/provenance is checked, and a reviewed immutable pin is available.

## Rules

- Upstream projects are composed, not vendored.
- Fork only when repository-owned changes or a stable maintained adaptation are necessary.
- Pin immutable commit SHAs; never track a moving branch as production identity.
- Preserve upstream license and notices.
- Keep credentials, browser profiles, cookies, session stores, downloads, and raw page content outside Git.
- Full recursive submodule materialization is opt-in; CI validates gitlink metadata without initializing submodules.
- Dual-gate and task-outcome evidence remain promotion requirements.

Machine-readable index: `INTEGRATIONS.json`. Enforcement: `scripts/ci/verify_agent_tooling_templates.py`.
