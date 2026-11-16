# Schema contract

## Portable SKILL.md frontmatter
| Field | Required | Type / limits |
|---|---|---|
| name | yes | lowercase ASCII letters/digits and single hyphens; 1–64 characters; match parent directory |
| description | yes | nonempty string, at most 1024 characters; capability and triggering contexts |
| license | no | string identifying license or file |
| compatibility | no | nonempty string, at most 500 characters |
| metadata | no | mapping of string keys to string values |
| allowed-tools | no | experimental, host-dependent string; omitted in this package |

Frontmatter is YAML between opening and closing `---`; the schema validates its parsed mapping, not raw YAML text. This local schema intentionally rejects undocumented top-level fields. It does not claim to replace the official reference validator.

## Design config
`design-config.schema.json` validates structure. `doe_core.validate_config` additionally checks uniqueness, finite increasing ranges, minimum factor counts, and generator semantics. Every factor is continuous. Units are descriptive strings, not dimensional-analysis enforcement. `model` selects main effects, main plus all pairwise interactions, or a full quadratic. Generators are mappings from generated-factor names to signed products of distinct basic factors.

## Audit
`audit.schema.json` covers the documented report fields. `condition_number_scaled` is null for rank-deficient models. `release_ready` is a narrow numerical gate, not authorization or evidence of adequate power, feasibility, independence, or safety. Defining-relation signs mean I equals the signed product of named factors. Center points are outside the fraction's defining relation; relation diagnostics apply to its corner fraction.
