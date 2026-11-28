# Scientific and Asset Provenance Contract

## Claim record

Every scientific claim used in a game mechanic carries:

- Stable claim ID and short statement.
- Source database, accession, canonical URL, and retrieval timestamp.
- Release, version, or immutable revision.
- Organism, cell type, construct, and experimental conditions where relevant.
- Evidence class: experimental, curated, computational prediction, literature, educational representation, or gameplay abstraction.
- Method, resolution, confidence, and uncertainty fields where applicable.
- Citation and attribution.
- Reviewer, review date, and disposition.
- Content and mechanic references that consume the claim.

## Structure record

Structure records retain PDB or EMDB accession, chain/entity identifiers, source organism, experimental method, resolution, ligand state, construct boundaries, assembly, and source revision. Predicted structures carry the model identifier, UniProt accession, model version, pLDDT/PAE context, and a visible prediction label.

## Asset record

Every image, video, 3D model, audio file, font, texture, diagram, and derived visual records:

- Creator and source URL.
- Asset identifier and checksum.
- License name and exact license text or URL.
- Attribution text and redistribution conditions.
- Derivative-work and commercial-use status.
- Permission evidence where a direct license is absent.
- Local asset path and consuming content IDs.

## iJEP Studio boundary

iJEP Studio is a topic, scientific-visualization, and visual-reference seed. The project inventory records video IDs, timestamps, descriptions, linked structures, papers, and relevant technical commentary. The project uses direct links and citations for discovery. Reproduction, adaptation, footage inclusion, model extraction, poster inclusion, or derivative use proceeds after the exact asset license and permissions are recorded.

## Review gates

1. Source identity and accession resolve.
2. Source revision and retrieval date are recorded.
3. Evidence class and uncertainty are visible in the content model.
4. Usage terms and attribution are approved for the target distribution.
5. Scientific reviewer checks the claim and its gameplay abstraction.
6. QA verifies that the implemented behavior matches the approved mechanic contract.
7. Source updates trigger revalidation for affected claims and assets.
