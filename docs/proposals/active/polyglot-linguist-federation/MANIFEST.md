# PolyGlot–Linguist Capability Federation

**Status:** proposed implementation / review required  
**Priority:** P1  
**Owner:** Termux Monorepo (initial stewardship)  
**Future organizational destination:** Research Astute (planned; migration requires explicit governance and repository-transfer approval)  
**Branch:** `feat/polyglot-linguist-federation`

## Executive summary

Establish a federated research, mapping, implementation and evaluation architecture. PolyGlot specialists study reference technologies and extract capabilities; Linguist provides canonical capability identities and language mappings; Matrice evaluates parity, performance and cross-domain advantage. A repository federation distributes work while preserving provenance, versioned contracts and reproducible evidence.

This proposal extends existing Linguist, COMMS-MATRICES, capability-opportunity graph, proposal lifecycle and Polyglot/CRG work. It does not replace those systems or establish a second canonical graph.

## Decision requested

Approve the additive architecture and its staged implementation in this repository. Keep initial maintenance in `timerloggedout-spec/termux-monorepo`. Record Research Astute as the intended future organizational home, subject to explicit transfer readiness, governance, access, secrets, CI and issue/PR continuity checks.

## Goals

1. Build a technology-neutral capability taxonomy.
2. Map competitor capabilities to canonical Linguist capabilities and implementations.
3. Cover languages, compilers, codecs, kernels, runtimes, transport, physical transmission, protocols, application delivery, agent communication and research/documentation surfaces.
4. Operate specialist PolyGlot research lanes with shared evidence contracts.
5. Federate versioned mapping and Matrice result feeds across repositories.
6. Measure capability parity separately from measured advantage.
7. Preserve upstream attribution, licenses, security boundaries and reproducibility.

## Non-goals

- Declaring Linguist superior before benchmark evidence exists.
- Treating unlike technologies as direct competitors on one undifferentiated score.
- Replacing canonical upstream repositories or copying their implementation wholesale.
- Making every PolyGlot an autonomous write authority.
- Treating a future Research Astute transfer as already approved or completed.
- Requiring network, browser, compiler or heavyweight runtime dependencies for the core metadata validator.

## Existing foundations to integrate

- `docs/proposals/active/linguist-machine-parity/`
- `docs/proposals/active/notation-sets/`
- `COMMS-MATRICES` notation and evaluation work
- capability-opportunity graph schemas and records
- Context Relationship Polyglot acceleration and its language-neutral provider boundary
- proposal registry and lifecycle automation

The canonical CRG remains authoritative for its existing graph domain. The federation adds typed references and feeds rather than silently redefining CRG semantics.

## Architecture

### 1. PolyGlot specialist lanes

A PolyGlot is a specialist research and mapping worker for one reference technology or coherent technology family. Examples include Rust, C++, C, Fortran, Zig, Go, Python, Java, Lua, Cangjie, LLVM, GCC, WebAssembly, Linux, Android, QUIC, TCP, UDP, HTTP/3, MASQUE, WebTransport, optical transport, modems, fax transmission, Base64, CBOR, Protocol Buffers, Zstandard, Brotli, arithmetic coding, ANS, A2A and MCP.

The initial competitor set is an opening cohort, not a closed catalogue. New targets enter through discovery and prioritization.

Each specialist:
- records upstream source, version, revision and license;
- extracts capabilities into stable identifiers;
- records constraints, security properties and operational assumptions;
- proposes Linguist mappings;
- supplies conformance fixtures and benchmark workloads;
- emits signed/provenanced, schema-validated result records;
- retains uncertainty and unsupported cases explicitly.

Specialists publish evidence and proposals. Repository write authority remains governed by the host repository's permissions and review process.

### 2. Canonical capability graph

Capability identity is technology-independent. A capability record describes the observable behavior, preconditions, guarantees, failure modes and conformance tests. Technology-specific implementations link to that identity.

Separate:
- capability semantics;
- source technology and version;
- Linguist expression / IR mapping;
- compiler, runtime and transport implementation;
- evidence and benchmark result.

Capability identifiers remain stable across mapping revisions. Breaking semantic changes create a new capability version or identifier according to the compatibility policy.

### 3. Linguist mapping and execution

Linguist owns canonical semantic representation and mapping contracts. Adapters translate between the canonical representation and target syntax, IR, byte formats, runtime interfaces and protocols.

Mapping classes:
- syntax mapping;
- semantic mapping;
- ABI / FFI mapping;
- compiler and IR mapping;
- codec / serialization mapping;
- runtime / kernel mapping;
- transport / protocol mapping;
- application packaging / delivery mapping;
- documentation and UI-surface rendering mapping.

A mapping declares coverage, unsupported constructs, lossy transformations, round-trip guarantees and target-version compatibility. Lossless round trips are required where semantics permit; lossy mappings explicitly identify dropped or approximated information.

### 4. Competition domains

Domains have their own benchmark suites and scorecards:

| Domain | Reference families | Evaluation examples |
|---|---|---|
| Programming languages | Rust, C++, C, Fortran, Zig, Go, Python, Java, Lua, Cangjie, Swift, Kotlin, Haskell | semantics, compile time, runtime, memory, safety, developer workflow |
| Encoding / serialization | Base64, CBOR, MessagePack, Protocol Buffers, FlatBuffers | wire size, encode/decode cost, canonicalization, schema evolution |
| Compression | Zstandard, Brotli, LZ4, LZMA, arithmetic coding, ANS | ratio, throughput, memory, model overhead, random access |
| Compiler infrastructure | LLVM, GCC, language-specific compilers, WebAssembly toolchains | optimization, portability, diagnostics, compile latency |
| Kernel / runtime | Linux, BSD, Android runtimes, WASI | syscall coverage, scheduling, memory, isolation, portability |
| Transport | fax/modem history, 14.4 kbps modem class, copper, radio, fiber/optics, Ethernet, Wi-Fi, cellular, satellite, IP, TCP, UDP, QUIC, Multipath QUIC | throughput, latency, loss recovery, congestion, energy, setup, fairness |
| Application protocols | TLS, HTTP/2, HTTP/3, WebSocket, MASQUE, WebTransport | handshake, multiplexing, proxying, security, interoperability |
| Agent communication | A2A, MCP and future protocols | discovery, negotiation, identity, message fidelity, handoff, authorization |
| Application delivery | PWA, APK, native binaries, WASM | installability, startup, permissions, distribution, update and offline behavior |
| Knowledge surfaces | GitHub comments, websites, llms.txt, browser extensions, documentation | human readability, agent discoverability, fidelity, access control, transparency |

Fax, modem, optical and network technologies belong to a layered transport research family. Their physical constraints differ; compare them using appropriate physical/link/network/application metrics rather than a single generic throughput ranking.

### 5. Transport research lane

Transport is a first-class domain, spanning physical signaling to application communication. Maintain explicit layer and dependency relationships without forcing every technology into a rigid OSI classification.

For each target, record:
- medium and physical/link assumptions;
- framing, addressing and routing;
- reliability and ordering guarantees;
- congestion and flow control;
- multiplexing and head-of-line behavior;
- encryption and identity boundaries;
- setup/handshake costs;
- mobility, multipath and proxy behavior;
- implementation maturity and standards status.

QUIC is an established transport protocol standardized by RFC 9000; HTTP/3 is specified by RFC 9114. MASQUE, WebTransport and Multipath QUIC are adjacent extensions or related work with distinct standardization and deployment states. The registry must pin exact specifications and classify each status per source date. Avoid blanket claims such as “successor” without evidence.

### 6. Matrice evaluation

Matrice uses domain-specific metrics plus shared cross-domain dimensions.

Shared dimensions:
- EXPRESS: expressiveness and capability coverage;
- EXEC: execution performance;
- COMPILE: compilation and optimization;
- MEMORY: runtime memory and resource efficiency;
- COMPRESS: representation and transmission cost;
- ADAPT: predictive adaptation and learning;
- INTEROP: cross-language/runtime/protocol compatibility;
- VERIFY: correctness, safety and reproducibility;
- DEVEX: tooling and developer productivity;
- COMPOSE: composability across capabilities and domains.

Parity is a conformance gate. Advantage is a benchmark claim supported by comparable workloads and evidence. Report confidence, variance, environment, cold/warm conditions and baseline versions. Preserve correctness as a hard gate; speed cannot compensate for incorrect reconstruction or execution.

For compression, include payload, decoder, model, dictionary, adaptation and synchronization costs. For transport, include handshake, retransmission, encryption, network and energy costs as applicable.

### 7. Repository federation

Repository roles:
1. Reference repositories: upstream specifications and implementations.
2. Specialist repositories: PolyGlot research, extraction and fixtures.
3. Integration repositories: Linguist mappings, adapters and runtime implementations.
4. Federation repository: shared taxonomy, schemas, dependency graph, Matrice aggregation and cross-domain reports.

Initial stewardship remains in Termux Monorepo. The architecture supports later repository splits and organizational migration without requiring them now.

Each repository feed declares repository identity, branch/ref, immutable commit, schema version, producer, generated time, source provenance and artifact digest. Consumers pin immutable revisions for reproducibility. Latest pointers are convenience indexes only.

### 8. Hierarchical feeds and dependency graph

Local Matrice evaluates one target/implementation. Domain Matrice compares targets within a domain. Federation Matrice aggregates domain evidence and evaluates compositions.

Feed pipeline:
`DISCOVER → EXTRACT → NORMALIZE → MAP → IMPLEMENT → TEST → BENCHMARK → PUBLISH → AGGREGATE`

A source revision change emits an impact event for dependent mappings, tests and results. Historical results remain immutable; a new evaluation creates a new record.

### 9. Publication, browser and knowledge surfaces

A canonical Linguist source may have multiple projections:
- source representation;
- public human-readable rendering;
- structured agent-readable representation;
- interactive browser overlay;
- restricted team view.

GitHub comments and webpages can expose a public Linguist reading layer through an explicit rendered block or browser extension. Preserve original text and provide a visible indication of translated/derived content. Browser integrations should respect origin permissions, CSP, authentication, accessibility and user control.

derpWiki may provide an optional collaborative discovery layer. Experimental invisible-character encodings belong only in clearly labelled, opt-in test fixtures. Public `llms.txt`, Agent Ready checks and ordinary agent discovery should use explicit, documented metadata and standards-compliant content. Baseline tests run with derpWiki features disabled and verify the ordinary published surface.

Versioned publishing includes source hash, language version, mapping version, surface ID, visibility and access policy. Private material must remain behind actual access controls; obscurity or hidden characters do not provide confidentiality.

### 10. Future Research Astute migration

Research Astute is the intended future organizational home. Migration is a future governance milestone, not part of this implementation.

Before transfer, prepare:
- repository inventory and ownership decision;
- maintainer and team permissions;
- branch protections and rulesets;
- Actions secrets, variables and environments;
- Pages/domains and deployment identities;
- webhooks, GitHub Apps and external integrations;
- issues, PRs, releases, tags and project continuity;
- package/container registries;
- license, security policy and contributor provenance;
- redirect, canonical URL and consumer update plan.

Keep the current repository as the initial source of truth until a migration decision is approved and a transfer rehearsal passes.

## Data contracts

Initial machine-readable contracts are introduced under `docs/integrations/polyglot/`:
- capability records;
- technology target records;
- mapping records;
- benchmark result records;
- feed envelopes;
- repository federation manifests.

Contracts use explicit schema versions and provenance. Unknown optional fields may be preserved; unknown required semantics must fail validation. Schema evolution follows additive changes by default, with major versions for incompatible changes.

## Security and governance

- Treat upstream source and generated research as untrusted input.
- Record licenses and attribution before copying code or fixtures.
- Keep credentials, personal data and private source out of public feeds.
- Restrict browser extensions to explicit host permissions and user-visible actions.
- Require review for generated code, repository writes, workflow changes and publication.
- Validate provenance and artifact hashes.
- Run deterministic, bounded validators on the Termux path.
- Keep heavy compilers, browser tests and network-dependent benchmarks in opt-in or remote CI lanes.

## Delivery phases and acceptance

### Phase 0 — Registry and contracts
- Add proposal, schemas, sample records and deterministic validator.
- Acceptance: JSON schema documents parse; sample records validate; duplicate identifiers and invalid references fail.

### Phase 1 — Initial PolyGlot cohort
- Register Rust, C++, Base64, Fortran and QUIC as initial research targets.
- Add transport and physical transmission domain taxonomy.
- Acceptance: each target has pinned sources, capability records, owner/status and mapping backlog.

### Phase 2 — Linguist mappings
- Connect capability records to canonical Linguist IR, adapters and conformance tests.
- Acceptance: mappings disclose coverage and loss; round-trip fixtures pass where applicable.

### Phase 3 — Matrice domain scorecards
- Define domain workloads and shared metrics.
- Acceptance: benchmark results include environment, baseline revision, variance and provenance; parity and advantage are reported separately.

### Phase 4 — Repository federation
- Publish immutable feeds and aggregate domain results.
- Acceptance: consumer validates schema and digest, pins source revisions and detects stale feeds.

### Phase 5 — Surface integrations
- Prototype GitHub rendering and browser overlay; publish derpWiki opt-in experiment.
- Acceptance: original content remains available; transformed layer is visibly identified; permissions and access policies are tested; Agent Ready baseline remains clean.

### Phase 6 — Research Astute readiness
- Produce transfer checklist and rehearsal plan.
- Acceptance: governance approval and continuity checklist complete before any ownership move.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Scope explosion | capability taxonomy, staged cohorts, WIP limits |
| False parity claims | conformance tests and explicit unsupported cases |
| Invalid comparisons | domain-specific scorecards |
| Stale upstream mappings | pinned revisions and impact events |
| Model/decoder overhead hidden | total-cost accounting |
| Cross-repository drift | versioned schemas and immutable feeds |
| Hidden-layer confusion | visible disclosure and opt-in experiments |
| Access-control leakage | explicit policy enforcement and private-feed tests |
| Premature org migration | readiness gate and transfer rehearsal |

## Open decisions

1. Final PolyGlot naming and ownership conventions.
2. Canonical location and ownership of the shared capability taxonomy.
3. Whether Matrice federation consumes signed feed artifacts or repository attestations first.
4. Browser integration implementation choice and supported surfaces.
5. Research Astute governance, transfer timing and maintainer roster.
6. Initial benchmark workload owners and baseline environments.

## References

- QUIC: RFC 9000, https://www.rfc-editor.org/rfc/rfc9000
- HTTP/3: RFC 9114, https://www.rfc-editor.org/rfc/rfc9114
- MASQUE: https://datatracker.ietf.org/wg/masque/about/
- WebTransport: https://www.w3.org/TR/webtransport/
- Multipath QUIC work: https://datatracker.ietf.org/doc/draft-ietf-quic-multipath/
- Existing repository PolyGlot/CRG acceleration: `docs/ops/CONTEXT-RELATIONSHIP-POLYGLOT-ACCELERATION.md`

External standards links are research pointers; implementation records must pin the exact revision and current status at evaluation time.
