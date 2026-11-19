# PolyGlot / Linguist Federation Contracts

This directory defines the additive, versioned exchange boundary for PolyGlot specialists, Linguist mappings and Matrice federation.

## Contract set

- `scripts/polyglot/build_feed.py`: deterministic content-addressed feed builder.

- `schemas/capability.schema.json`: technology-neutral capability identity and semantics.
- `schemas/technology-target.schema.json`: reference technology and upstream provenance.
- `schemas/mapping.schema.json`: Linguist mapping and conformance coverage.
- `schemas/benchmark-result.schema.json`: reproducible Matrice observation.
- `schemas/feed-envelope.schema.json`: immutable repository feed envelope.
- `examples/`: minimal records illustrating valid relationships.

## Authority boundaries

PolyGlot specialists research reference technologies and publish evidence. Linguist owns canonical semantic representation and mappings. Matrice owns evaluation methodology and result aggregation. Repository permissions and review policy govern writes.

The contracts are metadata-only. They carry references, digests, metrics and provenance. Keep credentials, private source contents and executable instructions outside these records.

## Versioning

Each record declares `schema_version`. Producers pin immutable source revisions and artifact digests. Consumers validate records before aggregation. Breaking schema semantics require a major schema version; additive optional fields may be introduced compatibly.

## Validation

Run:

```sh
python3 scripts/polyglot/validate_federation.py
python3 scripts/polyglot/build_feed.py --repository timerloggedout-spec/termux-monorepo --revision <commit-sha> --generated-at 2026-11-19T00:00:00Z --output build/polyglot-feed.json
python3 -m unittest discover -s tests -p 'test_polyglot_federation.py' -v
```

The validator uses Python standard-library JSON and performs deterministic structural and cross-reference checks. Full JSON Schema validation may be added in a separate optional CI lane.

## Domain references

- [Transport domain](TRANSPORT-DOMAIN.md): physical media through application transport, with QUIC reference card and benchmark protocol.
- [Research Astute migration readiness](RESEARCH-ASTUTE-MIGRATION.md): future organizational transfer checklist; current stewardship remains in Termux Monorepo.
- [Initial technology targets](examples/technology-targets.json): Rust, C++, Base64, Fortran and QUIC opening cohort.
- [Matrice dimensions](examples/matrice-dimensions.json): shared dimensions and hierarchical aggregation policy.
- [QUIC mapping example](examples/mapping-quic-streams.json): capability-to-target mapping record.

The initial cohort is intentionally small and expandable. New language, codec, compiler, kernel, runtime, transport, protocol, physical-medium, application and knowledge-surface targets use the same contracts.
