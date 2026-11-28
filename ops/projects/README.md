# Project profiles and manifests

The project-scope profile family builds on the existing `ops/projects/profile.schema.json` contract and the ArchWiz Concept Map.

## Record layers

1. **Scope profile** — one JSON record under `.config/llm_map/profiles/projects/`, validated by `ops/projects/profile.schema.json`. It declares the project class, repository/issue/lane/artifact scope, safety exclusions, and bound surfaces.
2. **Project manifest** — one domain-specific YAML record under `ops/projects/manifests/`. It carries product identity, research planes, game taxonomy, specialist contexts, content pipeline, and delivery contracts.
3. **Registry** — `ops/projects/registry.yaml` maps stable project IDs to scope profiles, manifests, proposals, and repository lifecycle state.

The scan-profile family at `.config/llm_map/profiles/*.json` retains its device-workspace path-set semantics. Project profiles use the dedicated `projects/` family.

## Safety and lifecycle

- Keep scope exclusions for secret-shaped paths and private key material in every project profile.
- Keep tokens and credential values in approved secret storage; profile records carry secret names and scope metadata only.
- Bind repository and issue scope to the smallest project-owned set.
- Record external repositories as research references until their adoption scope is reviewed.
- Use versioned manifests and stable IDs for cross-repository integration. Local symlinks are optional workspace conveniences.
- Keep profile metadata plaintext and indexable; apply record-body encryption by the existing project class policy where required.
- Add profiles through reviewable branches and registry entries. Preserve prior profile revisions in Git history.

## Current project

- Reusable research store target: [Research-Astute/molecular-biology-research](https://github.com/Research-Astute/molecular-biology-research). Private-repository provisioning is tracked by workflow run 46114028269; the repository ID is recorded after its verified receipt.
- Scope profile: `.config/llm_map/profiles/projects/cell-the-living-machine.json`
- Project manifest: `ops/projects/manifests/cell-the-living-machine.yaml`
- Proposal: `docs/proposals/active/cell-the-living-machine/MANIFEST.md`
