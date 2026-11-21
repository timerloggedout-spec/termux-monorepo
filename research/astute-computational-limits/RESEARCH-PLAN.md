# Research Plan — Computational Limits

**Lane:** `ultimate-computation-limits`  
**Mode:** preliminary · source-backed · phased  
**Observation date:** 2026-11-19

## Objective

Construct a traceable map from mathematical foundations to physical computation, quantum information, gravitational limits and proposed black-hole computation. Each phase produces a bounded research artifact and explicit dependency/evidence updates.

## Phase sequence

| Phase | Research scope | Required foundations | Deliverable | Admission evidence |
|---|---|---|---|---|
| P0 | Formal vocabulary and graph contracts | logic, sets, algebra, units, provenance | concept registry, edge semantics, source ledger | every node has a definition; every prerequisite edge has a rationale |
| P1 | Computation, information and thermodynamics | Boolean logic, algorithms, probability, statistical mechanics | information/entropy/energy dependency map | primary sources for Shannon, Landauer and reversible computation |
| P2 | Quantum mechanics and quantum information | complex linear algebra, Hilbert spaces, operators, probability, information theory | quantum state, gate, measurement and speed-limit map | theorem assumptions recorded; quantum information technology families separated |
| P3 | Relativity and black-hole thermodynamics | calculus, differential geometry, tensor calculus, general relativity, statistical mechanics, quantum field theory on curved spacetime | black-hole entropy, temperature, bounds and causal-scale map | equations dimension-checked; classical and semiclassical results distinguished |
| P4 | Quantum gravity and holography | quantum field theory, general relativity, quantum information, entropy bounds | information-paradox and holography research map | competing approaches and unresolved questions sourced |
| P5 | Technology and engineering paths | quantum control, materials, cryogenics, photonics, metrology, fabrication, sensing, error correction | technology dependency matrix and gap register | each capability classified as demonstrated, prototype, theoretical or speculative |
| P6 | Synthesis and scenario comparison | all admitted prior phases | versioned DAG, Markov/Bayesian scenario model, research brief | evidence provenance, assumptions, uncertainty and independent review |

Phases express research prerequisites. They do not assert that history or discovery follows one linear route. Parallel subdomains may proceed when their own prerequisites are satisfied.

## Initial work packets

### P0-A — Algebra-to-physics dependency chain

Map arithmetic and logic → algebraic structures → linear algebra and complex vector spaces → Hilbert spaces and operators → quantum mechanics. Add group theory and representation theory for symmetry; add tensor algebra and differential geometry for fields and gravitation.

### P0-B — Probability and graph semantics

Map probability theory and measure theory → statistical mechanics and quantum measurement. Map graph theory → prerequisite DAGs and Markov models. Preserve the distinction between:
- a prerequisite edge;
- a historical precedence relation;
- an explanatory/supporting relation;
- a probabilistic transition;
- a causal hypothesis.

Only prerequisite edges enter the acyclic dependency graph.

### P1-A — Information is physical

Trace Maxwell's demon and Szilard's engine, Shannon information, Landauer's principle, reversible computation and thermodynamic cost. Record the assumptions and the distinction between logically irreversible operations and reversible physical implementations.

### P2-A — Quantum speed and quantum information

Re-derive the Margolus–Levitin bound and compare it with Mandelstam–Tamm and generalized quantum speed limits. Record the 2017 Jordan counterpoint: energy-only arguments do not automatically establish a universal computational clock-speed bound without additional assumptions about locality, information density and information transmission.

### P3-A — Gravitational and entropy limits

Trace Bekenstein entropy, Hawking temperature/radiation, Bekenstein bounds, black-hole area entropy and the holographic principle. Keep semiclassical calculations distinct from a complete theory of quantum gravity.

### P4-A — Information recovery

Map Hawking's original calculation, unitarity tension, Page curve, islands and holographic approaches as research threads. Record open questions and competing assumptions rather than collapsing the field into one settled mechanism.

### P5-A — Technology paths

Compare demonstrated quantum-computing platforms and enabling subsystems: superconducting circuits, trapped ions, neutral atoms, photonics and semiconductor spin systems. Map control, readout, calibration, cryogenics/vacuum/laser requirements, fabrication, networking and quantum error correction.

Black-hole formation, controlled encoding of a computation into black-hole degrees of freedom and recovery of a chosen output remain separate speculative engineering gaps.

## Research record contract

Every claim or edge should carry:

- stable identifier;
- concise claim;
- source URI and publication date;
- source type (primary paper, review, experiment, standard, explanatory media);
- assumptions and units;
- evidence class;
- confidence rationale;
- status (supported, contested, open, superseded);
- observation timestamp;
- reviewer and revision provenance.

## Bayesian / Markov integration

Use the existing Markov trellis implementation for explicitly defined state-transition models, where a normalized transition matrix is justified. Use Bayesian updates only when priors, likelihoods, evidence identity and dependence assumptions are explicit.

The existing `scripts/bayesian_routing.py` is an engineering-routing implementation, not a ready-made scientific inference model. Adapt its provenance and posterior discipline; define domain-specific priors and likelihoods for scientific claims.

A research DAG expresses prerequisite structure. A Markov chain expresses transitions among states. A Bayesian network expresses conditional dependence. A historical timeline expresses precedence. Keep all four representations linked and typed.

## Exit conditions

A phase closes when its stated artifact exists, every admitted edge has source-backed rationale, unresolved claims are marked, graph validation passes, and a reproducible review receipt records the exact source and graph versions.
