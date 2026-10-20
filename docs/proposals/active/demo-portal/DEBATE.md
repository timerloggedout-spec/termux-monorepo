# DEBATE — demo-portal

## Driver evidence (Claude, 2026-09-07)

- Operator request (chat): "the project ought to include 'demo portals'... Vercel && Render && GitHub Pages could provide this framework. Where the MCP's are supplied to [some Agentic] collaborators and persistently available while also showcasing the features, abilities, etc of the projects (eg: a sandboxed Termux emulator running examples of the Archwiz.py && deepcli-tui interfaces and more examples)."
- The Vercel lane for this already exists and is live: `demo-portal/public`, freed up by VLT-001's resolution (see `docs/proposals/active/vercel-lane-topology`).
- Phasing rationale: this repo has one confirmed credential-exposure incident already (`docs/CREDENTIAL-EXPOSURE.md`, committed browser session cookies). A real public-facing interactive shell (Phase 3) is a materially different risk class than a recorded demo (Phase 1) or a client-side sandbox (Phase 2). Sequencing forces the safest version to ship first and the highest-risk version to earn its own review rather than riding in on this proposal's approval.

## Votes

_(none yet)_