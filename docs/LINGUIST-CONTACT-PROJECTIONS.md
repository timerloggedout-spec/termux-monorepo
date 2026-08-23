# Linguist Contact-Document Projections

## Intent

The Linguist contact surface uses one canonical human source for each agent-facing document and two generated presentations. The first is a readable **L33t/Grimoire display projection** for public orientation. The second is a denser **machine projection** for agent contact points. Neither projection is an authority independent of its human source.

> The goal is readable symbolic compression with deterministic recovery, not encryption or a substitute for secret custody.

## Projection Rules

| Surface | Canonical human source | Generated projection | Mode |
|---|---|---|---|
| Root README | `README.hum.md` | `README.md` | Human-readable L33t/Grimoire display |
| Root agent guidance | `AGENTS.hum.md` | `AGENTS.md` | Machine L33t/Grimoire projection |
| Root Claude guidance | `CLAUDE.hum.md` | `CLAUDE.md` | Machine L33t/Grimoire projection |
| ICM contact tree | Every `*.hum.md` contact source under `docs/icm/` | Matching `.md` path | Machine L33t/Grimoire projection |

The ICM contact tree includes `AGENTS`, `CLAUDE`, `CONTEXT`, and `README` documents. The projection generator recognizes a human source named `NAME.hum.md` and writes its machine projection to `NAME.md`.

## Obfuscation Boundary

Paths, names, and values in prose and inline-code display spans are eligible for the L33t/Grimoire display transform. They are not subject to a permanent literal exemption. The generator retains only narrowly defined structural spans necessary for valid Markdown routing and safe execution: Markdown link destinations and executable fenced-code bodies. Its generated header records those structural exceptions.

A later approved private mapper may replace the public display lexicon with higher-coverage symbolic handles. The private mapper must not be committed, echoed into comments, or stored in generated repository artifacts. Raw credentials, keys, tokens, and session material remain prohibited from both canonical and generated documents.

## Deterministic Workflow

1. Edit the relevant `*.hum.md` canonical source.
2. Run `python3 scripts/cedrlang/render_contact_projections.py` to refresh projections.
3. Run `python3 scripts/cedrlang/render_contact_projections.py --check` to prove parity.
4. Run the focused projection tests and repository gates.
5. Commit the source and generated projection together.

The generator must be the only routine writer for generated projections. A failed parity check means the machine projection is stale and cannot be presented as current agent guidance.

## Legacy Evidence

Closed PRs #154 and #177 established the intended `AGENTS.hum.md` / `AGENTS.md` L33t pattern but mixed it with conflicting unrelated work. This contract retains that projection intent while making the source, generation, exceptions, and parity check explicit and reviewable.
