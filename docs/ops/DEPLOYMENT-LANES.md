# Deployment and visual composition lanes

**Status:** documented from existing repository architecture; no new runtime dependency is introduced by this record.

## Existing architecture

The repository's SHE dashboard PRD already defines the deployment hierarchy as:

```text
GitHub corpus / Actions evidence
            │
            ▼
       SHE reducers
        ┌───┼────┐
        ▼   ▼    ▼
     Vercel Pages Hex
        │
        └──── reference/teaching lane ────┐
                                          ▼
                                      Render / n8n
```

The existing PRD explicitly says Vercel is the preferred interactive application surface, GitHub Pages is an optional static mirror, Hex is an optional research consumer, and Render/n8n is a reference/template lane unless a genuinely free, non-expiring deployment path is verified.

The same PRD defines a **drag-and-drop / visual lane** consisting of `.mmd` architecture/source diagrams, generated `.png` previews, one-to-one workflow definitions, and optional importable n8n workflow examples. The visual layer is a projection of the evidence pipeline, not a second orchestration truth.

The existing `docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd` also contains a `Render / n8n examples` node marked as reference-only. This confirms that n8n deployment was already considered near the Mermaid architecture material rather than being a newly invented lane.

## n8n frontend/deployment boundary

The intended separation is:

| Lane | Responsibility | Canonicality |
|---|---|---|
| GitHub Actions | collection, validation, reducers, evidence production | authoritative execution/evidence lane |
| Vercel | interactive SHE frontend | preferred presentation surface |
| GitHub Pages | reproducible static frontend mirror | optional presentation surface |
| Hex | research/analysis cockpit | optional consumer |
| n8n | visual automation/reference workflows | optional composition/deployment adapter |
| Render | deployment/template reference | not a required dependency |
| Mermaid `.mmd` | architecture source | canonical visual documentation |
| generated PNG | human-review preview | derived artifact |

n8n therefore may host or demonstrate workflow composition around the frontend/evidence plane, but it must not silently become the system of record or replace GitHub Actions without a separately approved architecture change.

## Current implementation evidence

- `docs/ops/SHE-DASHBOARD-PRD.md` is the deployment/visual-lane contract.
- `docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd` is the existing Mermaid architecture source.
- `docs/ops/SHE-DASHBOARD-ARCHITECTURE.png` (when generated) is a review projection, not source.
- `docs/evaluations/manus/session_metadata/connector_config.json` records n8n and Mermaid connector metadata; connector presence is not proof of deployment.

## Admission rule

A future n8n deployment should enter the same evidence model as other adapters:

```text
n8n workflow definition
       │
       ▼
versioned adapter/config
       │
       ▼
GitHub-linked evidence
       │
       ├── deployment state
       ├── workflow revision
       ├── frontend artifact/version
       └── run provenance
```

No credential, webhook URL, tunnel endpoint, or provider token belongs in this documentation or source repository.
