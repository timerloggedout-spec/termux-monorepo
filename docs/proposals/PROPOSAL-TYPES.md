# QDesk proposal type registry

This document defines the controlled values for the optional `proposal_type`
field in `docs/proposals/registry.yaml`. The registry remains the source of
record; the feed and dashboard carry the value verbatim.

| Type | Use |
|---|---|
| `architecture` | System architecture, platform boundaries, and foundational design |
| `research` | Discovery, literature review, technical investigation, and research synthesis |
| `scientific_experiment` | Scientific hypothesis, design, execution, analysis, and reproducibility work |
| `scientific_experiment_system` | Capability systems, specialist roles, experiment governance, and scientific workflow infrastructure |
| `behavioral_experiment` | DO Statements, Performance Psychology, and other governed behavioral interventions |
| `measurement_validation` | Measurement models, verification, validation, quality, and assurance |
| `integration` | External services, providers, APIs, and connector integrations |
| `operations` | Operational workflows, runbooks, queue management, and reliability |
| `product` | User-facing product capabilities and experience |
| `governance` | Policy, decision rights, compliance, and stewardship |
| `security` | Security engineering, threat analysis, and defensive assurance |
| `evaluation` | Benchmarks, comparative evaluation, metrics, and performance research |

## Contract

1. `proposal_type` is optional for legacy entries. Missing values remain null/unclassified.
2. New entries should use one of the values above. Do not infer a type from a title, path, author, status, or related issue.
3. The collector preserves the source value and reports an unknown non-empty value as a feed gap; it does not silently normalize or remap it.
4. The Proposals page builds its Type filter from the emitted feed values. The UI is a projection, not a second registry.
5. The Contribution Desk remains the operational queue/traversal cockpit. Proposal identity and type remain in the proposal registry.
