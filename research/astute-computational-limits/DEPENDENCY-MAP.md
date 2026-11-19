# Cross-domain Dependency Map

## 1. Core model

The lane maps four connected but distinct structures:

1. **Prerequisite DAG:** which concepts or capabilities must be understood or available before another node can be admitted.
2. **Historical lineage:** which discoveries preceded, influenced or motivated later work.
3. **Markov state model:** how a defined system transitions among states under a specified transition matrix.
4. **Bayesian evidence model:** how observations update uncertainty about claims or hypotheses.

The structures share stable identifiers and evidence provenance. Their edges and update rules remain separately typed.

## 2. Algebra and mathematics → physics

| Mathematical domain | Immediate dependencies | Enables / connects to | Research relevance |
|---|---|---|---|
| Arithmetic and formal logic | definitions, proof rules, number systems | Boolean algebra, algorithms, formal verification | representation and correctness of computation |
| Boolean algebra | logic, set operations | logic gates, circuit design, digital computation | classical computational substrate |
| Abstract algebra | sets, binary operations, axioms | groups, rings, fields, modules | symmetry, arithmetic structures and algebraic models |
| Group theory | abstract algebra | group actions, Lie groups, representation theory | symmetries in quantum mechanics and field theory |
| Linear algebra | vector spaces, fields, matrices | eigenvalues, operators, tensor products | quantum states, observables and transformations |
| Complex analysis | complex numbers, limits, differentiation | analytic functions, amplitudes and spectral methods | quantum amplitudes and mathematical physics |
| Functional analysis | linear algebra, topology, measure/integration | Hilbert spaces, operator theory, spectral theory | rigorous quantum mechanics and quantum field theory |
| Calculus and differential equations | real analysis, algebra | dynamics, wave equations, variational methods | classical mechanics, quantum dynamics and fields |
| Probability and measure theory | set theory, integration, analysis | stochastic processes, statistical mechanics, Bayesian inference | uncertainty, measurement and ensemble descriptions |
| Information theory | probability, combinatorics, coding | entropy, channel capacity, compression, error correction | information limits and reliable computation |
| Differential geometry | calculus, linear algebra, topology | manifolds, curvature, tensor calculus | general relativity and spacetime geometry |
| Tensor algebra/calculus | multilinear algebra, differential geometry | tensors, fields, curvature | general relativity and continuum/field models |
| Graph theory | discrete mathematics, combinatorics | DAGs, networks, Markov graphs, dependency analysis | dependency maps and state-transition structures |
| Computational complexity | logic, algorithms, discrete mathematics | complexity classes, resource bounds | algorithmic limits distinct from physical limits |

### Algebra example

`abstract algebra → linear algebra → complex vector spaces → Hilbert spaces → operators → quantum mechanics`

A parallel symmetry route is:

`group theory → Lie groups / Lie algebras → representations → quantum symmetries and gauge-field structures`

A geometry route is:

`linear algebra + calculus + topology → differential geometry → tensor calculus → general relativity`

These are conceptual prerequisite chains. Specific courses, papers and derivations may require additional branches and different formal orderings.

## 3. Information and computation

| Node | Depends on | Enables / constrains |
|---|---|---|
| Boolean logic and circuits | logic, algebra, electrical engineering | classical digital computers |
| Shannon information | probability, coding theory | entropy and channel capacity |
| Statistical mechanics | probability, mechanics, thermodynamics | ensemble entropy and physical state counting |
| Landauer principle | information theory, statistical mechanics, thermodynamics | lower bounds on heat dissipation for logically irreversible erasure under stated conditions |
| Reversible computation | logic, circuit design, thermodynamics | low-dissipation computational architectures |
| Quantum computation | quantum mechanics, linear algebra, information theory | quantum gates, algorithms and quantum simulation |
| Quantum error correction | quantum information, coding theory, stabilizer algebra | fault-tolerant logical computation |
| Quantum control/readout | quantum devices, control theory, measurement science | operational quantum processors |

## 4. Quantum speed and resource limits

The Margolus–Levitin result bounds the minimum time for a quantum system with average energy above its ground state to evolve to an orthogonal state. In the standard formulation:

[
	au geq rac{pi hbar}{2(E-E_0)}
]

The associated operation-rate interpretation requires a definition of an elementary operation and the model assumptions. Jordan (2017) gives an important counterexample to treating energy alone as a universal bound on computational clock speed; locality and information-transmission assumptions matter.

Relevant dependencies:

`quantum mechanics + energy spectrum + state distinguishability → quantum speed limits`

`special relativity + locality + geometry → signal propagation constraints`

`information theory + statistical mechanics → memory/entropy constraints`

`quantum speed limits + locality + information-density assumptions → model-specific computational bounds`

## 5. Gravity, entropy and black-hole information

| Concept | Dependencies | Role in the map |
|---|---|---|
| Special relativity | spacetime, Lorentz symmetry | causal propagation and mass-energy relation |
| General relativity | differential geometry, tensor calculus, stress-energy | spacetime curvature and black-hole solutions |
| Quantum field theory | quantum mechanics, special relativity, field theory | quantum fields and particle creation |
| Quantum fields on curved spacetime | QFT + GR background | semiclassical Hawking-radiation calculation |
| Black-hole thermodynamics | GR + thermodynamics + quantum-field results | temperature, entropy and laws of black-hole mechanics |
| Bekenstein–Hawking entropy | horizon area + Planck scale | entropy proportional to horizon area |
| Bekenstein bound | quantum/statistical information + gravity assumptions | entropy bound for bounded systems under stated conditions |
| Holographic principle | black-hole entropy + quantum gravity | area scaling and boundary/bulk information relation |
| AdS/CFT | quantum field theory + string theory + gravity | concrete holographic correspondence in specified settings |
| Black-hole information problem | Hawking radiation + quantum unitarity + entropy | conflict and reconciliation research |
| Quantum gravity | GR + quantum theory | deeper microscopic account of spacetime and black holes |

The black-hole area law is a theoretical foundation. A fully controlled black-hole computer with programmable encoding, gate-level control and a verified output channel is a separate speculative proposition.

## 6. Technology path families

| Path | Demonstrated foundations | Enabling technologies | Remaining scaling questions |
|---|---|---|---|
| Advanced classical computing | CMOS, digital logic, semiconductor physics | lithography, interconnects, memory hierarchy, cooling, packaging | power density, heat removal, communication, fabrication limits |
| Reversible / low-energy computing | reversible logic theory, Landauer analysis | adiabatic circuits, low-loss devices, precise control | noise, speed, error correction, useful system-level advantage |
| Superconducting quantum processors | controlled superconducting circuits and qubits | cryogenics, microwave control, fabrication, readout | coherence, connectivity, calibration, logical error correction |
| Trapped-ion processors | ion trapping and coherent control | ultra-high vacuum, lasers, optics, stable control | gate speed, optical scale, connectivity and throughput |
| Neutral-atom processors | optical trapping and atom arrays | lasers, vacuum, imaging, atom loading and control | loss, gate fidelity, uniformity and error correction |
| Photonic quantum systems | single-photon sources/detectors and optical interference | integrated photonics, detectors, sources, networking | deterministic interactions, loss and scalable fault tolerance |
| Quantum simulation | programmable quantum/analog platforms | control, calibration, measurement and model validation | error budgets, observables and advantage over classical methods |
| Black-hole computation | theoretical limits and black-hole information research | controlled gravitational collapse, quantum-state encoding, quantum-gravity description, information recovery | every programmable and engineering interface remains speculative |

These platform families are research paths, not a single technology ladder. A black-hole-computation hypothesis does not follow automatically from improvements in present-day quantum processors.

## 7. Historical lineage anchors

- 1929 — Szilard connects information and thermodynamic reasoning through the one-molecule engine.
- 1948 — Shannon formalizes mathematical information theory.
- 1961 — Landauer relates logically irreversible information processing to heat dissipation.
- 1973 — Bekenstein proposes black-hole entropy proportional to horizon area.
- 1974–1975 — Hawking derives black-hole particle creation; black-hole thermodynamics develops.
- 1982 — Feynman motivates quantum systems as simulators of quantum physics.
- 1993–1995 — 't Hooft and Susskind formulate influential holographic-principle arguments.
- 1997–1998 — Margolus and Levitin publish a bound on the speed of dynamical evolution.
- 2000 — Lloyd synthesizes physical limits to computation, including a one-kilogram, one-litre example and black-hole limit.
- 2001–2002 — Lloyd estimates the computational capacity of the universe.
- 2017 — Jordan analyzes limitations of energy-only computational speed arguments.
- 2024 — generalized Margolus–Levitin bounds for arbitrary fidelity receive further analysis.
- 2026 — a Nature Reviews Physics review surveys black-hole thermodynamics and current open problems.

Historical precedence is recorded separately from prerequisite edges.

## 8. Key caveats

- The video is an accessible summary; the primary paper supplies the formal assumptions and derivations.
- Parallelism can improve practical wall-clock performance for suitable workloads. The resource trade-off in a fixed-energy, finite-size physical system is a more specific question.
- A quantum speed limit for state evolution is not automatically a universal benchmark for arbitrary computational architectures.
- Hawking radiation as an information-recovery channel depends on the quantum-gravity and unitarity problem; a usable engineered output interface remains speculative.
- Entropy bounds, storage capacity, operations per second and useful algorithmic throughput are different quantities.
