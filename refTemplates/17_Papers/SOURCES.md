# Papers / identity sources

| Class | Resolver | Notes |
|-------|----------|-------|
| arXiv | `https://arxiv.org/abs/<id>` | Preprints; prefer abs + pdf |
| GitXiv | gitxiv / paper+code links | Code-backed papers |
| ORCID | `https://orcid.org/<id>` | Author identity |
| GRID.ac | GRID institution IDs | Org grounding |
| Google Scholar | scholar profiles / clusters | Citation checks |
| Nature / formal | DOI | High-weight claims |
| Patents | patent office / Google Patents | Implementation claims |
| Seeded | operator URL + note | First-class |

## Seed examples (replace/expand)

| id | title / note | url | linked_slots |
|----|--------------|-----|--------------|
| seed-jogyo-markers | Structured research markers / trust gates (pattern) | (link when paper fixed) | jogyo-research-lab |
| seed-repro-pipeline | Reproducible research pipeline patterns | (docxology-related DOI when known) | docxology-template |

Scanners land under `scripts/ci/` per CONTINUOUS-EVAL P6 — rate-limited, dual-gate.
