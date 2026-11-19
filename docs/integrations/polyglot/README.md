# PolyGlot / Linguist Federation Contracts

This directory defines the additive, versioned exchange boundary for PolyGlot specialists, Linguist mappings and Matrice federation.

## Contract set

- `schemas/capability.schema.json`: technology-neutral capability identity and semantics.
- `schemas/technology-target.schema.json`: reference technology and upstream provenance.
- `schemas/mapping.schema.json`: Linguist mapping and conformance coverage.
- `schemas/benchmark-result.schema.json`: reproducible Matrice observation.
- `schemas/feed-envelope.schema.json`: immutable repository feed envelope.
- `examples/`: minimal records illustrating valid relationships.

## Authority boundaries

PolyGlot specialists research reference technologies and publish evidence. Linguist owns canonical semantic representation and mappings. Matrice owns evaluation methodology and result aggregation. Repository permissions and review policy govern writes.

The contracts are metadata-only. They carry references, digests, metrics and provenance; they do not carry credentials, private source contents or executable instructions.

## Versioning

Each record declares `schema_version`. Producers pin immutable source revisions and artifact digests. Consumers validate records before aggregation. Breaking schema semantics require a major schema version; additive optional fields may be introduced compatibly.

## Validation

Run:

```sh
python3 scripts/polyglot/validate_federation.py
python3 -m unittest tests.test_polyglot_federation
```

The validator uses Python standard-library JSON and performs deterministic structural and cross-reference checks. Full JSON Schema validation may be added in a separate optional CI lane.
