# DO Statement Contract

**Status:** additive authoring policy for the existing DO Statement Style gate.

## Accepted action forms

Natural imperatives and explicit DO statements are equivalent:

- `Create the artifact.`
- `DO: create the artifact.`

The literal `DO:` marker is optional. The gate evaluates action-first intent rather than requiring one spelling.

## Constraints and prohibitions

Negative grammatical forms can express necessary security, safety, preservation, and correctness constraints. Classify these as constraints; preserve their meaning.

Examples:

- `Do not overwrite the canonical standard.`
- `Never expose credentials.`
- `Avoid storing chat-only epistemic markers in data records.`

Rewrite a prohibition into a positive condition only when the transformation preserves its complete meaning.

## Hedging

Prefer direct action over low-agency framing when the intended action is known.

- Rewrite `We should probably update the validator.` as `Update the validator.`
- Rewrite `It might be useful to add tests.` as `Add tests.`

The checker flags a narrow set of hedged openings. It does not attempt unrestricted natural-language semantic inference.

## Commit subjects

Commit subjects retain imperative action verbs. An optional `DO:` marker after a conventional scope is accepted:

- `ci: create adaptive gate`
- `ci: DO: create adaptive gate`

## Evaluation boundaries

- Natural imperative: accepted.
- Explicit DO marker: accepted.
- Essential prohibition: accepted as a constraint.
- Narrowly detected hedging: flagged for rewrite.
- Descriptive prose: allowed unless another surface-specific policy requires an action.

This policy is a DO-style extension. Siglary taxonomy, domain registration, N∅ boundaries, receipt semantics, exemptions, and hard-gate posture remain governed by the canonical Siglary Standard.
