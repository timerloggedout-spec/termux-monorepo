# GitReverse reconstruction — DoE candidate

**State:** proposed / not admitted. This sibling campaign compares repository-to-prompt reconstruction quality. It records no run results and makes no performance claim.

## Candidates

| Treatment | Source | Role | Evidence |
|---|---|---|---|
| Upstream GitReverse | [filiksyos/gitreverse](https://github.com/filiksyos/gitreverse) @ `e7f7d2859105aafe16ec4f39c0315c07e6b0eae3` | Current upstream repository-to-prompt implementation | MIT license verified from upstream LICENSE |
| Internal implementation | Exact repository/path and commit pending identification | Custom implementation in progress | Source recon gate |
| Structured extraction baseline | Frozen repository metadata + README + depth-1 tree | Deterministic non-generative baseline | Defined in DESIGN.json |

Upstream README describes an input surface of repository metadata, a depth-1 root tree and README, synthesized into one conversational coding prompt. The upstream snapshot is pinned independently of later changes.

## Siglary treatment

Siglary integration is an explicit experimental dimension. The campaign freezes enabled/disabled levels only if the internal implementation exposes a stable switch on one source revision. Otherwise the Siglary version, notation profile and adapter hash become treatment attributes and a separate ablation cohort is required.

## Design

See [DESIGN.json](DESIGN.json). The pre-registration specifies 8 frozen repositories × 3 treatments × 3 repetitions = 72 planned observations, blocked by repository and repetition with randomized treatment order.

Primary outcomes are source-attribution precision, requirements coverage, unsupported factual-claim rate and blind usefulness score. Every material claim must map to a frozen source location; unsupported factual claims must equal zero on the held-out set.

## Boundaries

- This campaign measures reconstruction quality, not Rust migration speed.
- The deterministic baseline measures the value added by LLM synthesis.
- Repo-history narratives and session-provenance reconstruction are distinct problem contracts; they remain separate unless an explicit mapping proves comparability.
- Existing DoE records, Actions, and promotion gates remain authoritative. No parallel scheduler or ledger is introduced.

## Admission status

Fixtures, gold annotations, internal source identity, Siglary pins, runner digest, agent identity, automation and run records remain pending.
