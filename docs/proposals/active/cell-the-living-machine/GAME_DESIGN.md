# CELL: THE LIVING MACHINE — Game Design

## High concept

Explore, engineer, automate, manufacture, protect, and understand living and physical systems. The player moves from biological mechanisms and cellular networks into engineering studios, factory automation, digital twins, robotics, fabrication and professional production pathways. The game supports both scientific discovery and the creation of real concepts.

## Core loop

1. Observe a biological system and its current state.
2. Form a hypothesis about the mechanism or perturbation.
3. Select a molecular or cellular intervention.
4. Run a simulation and inspect the state transition.
5. Compare the result with source-backed evidence.
6. Refine the model, unlock tools, and investigate a wider system.

## Modes and play shape

Exploration is a first-class mode across all content. Additional modes include Arcade/Challenge, Engineering Studio, Factory/Automation, Research Lab, Simulation/Digital Twin, Collaboration and Production/Marketplace. All modes share one central player identity and creator portfolio.

## Genre and play shape

The game uses genre facets rather than a single exclusive category:

- Simulation: stateful molecular and cellular systems.
- Systems strategy: allocate energy, gradients, transport capacity, and repair resources.
- Exploration: discover components, structures, pathways, and interactions.
- Puzzle: solve constrained mechanistic scenarios.
- Educational: connect player actions to explainable scientific concepts.
- RPG progression: earn tools, capabilities, and research access through demonstrated mastery.
- Engineering/automation: design production chains, logistics, machines, controls and quality systems.
- Creator/manufacturing: convert reviewed concepts into prototype-ready design packages and approved fabrication pathways.

## Engineering and real-world making

The platform includes requirements, components, materials, tolerances, energy and material flows, production lines, automation, logistics, sensors, controls, robotics, CAD/CAE, digital twins, quality and lifecycle operations. Players can export versioned designs and route eligible concepts to approved fabrication providers or internal equipment through human-reviewed workflows.

## World and scales

The same biological world supports several linked resolutions:

- Molecular: atoms, residues, ligands, protein domains, and conformational states.
- Membrane: channels, transporters, receptors, gradients, and membrane potential.
- Organelle: energy conversion, trafficking, synthesis, and degradation.
- Cellular: signaling, homeostasis, division, stress, and repair.
- Tissue and organism: coordination, specialized cell roles, and physiological context.

## First vertical slice

A single cell membrane provides the first playable system. Three mechanisms create complementary gameplay:

1. Sodium-potassium pump — active transport, ATP use, ion gradients, and membrane potential.
2. Aquaporin — selective water transport, osmotic gradients, and permeability.
3. ATP synthase — proton motive force, rotary catalysis, and energy conversion.

The slice demonstrates the observe → manipulate → simulate → interpret loop. It includes one guided scenario, one open sandbox, source-linked mechanism cards, a parameter inspector, and a deterministic scenario replay.

## Knowledge lenses

Every lens uses the same source-backed content graph.

| Lens | Player experience | Specialist value |
|---|---|---|
| Field | Visual overview and intuitive purpose. | Fast orientation and teaching entry point. |
| Mechanism | Causal sequence and component interaction. | Mechanistic reasoning and state inspection. |
| Quantitative | Equations, rates, gradients, thermodynamics, and tunable parameters. | Mathematical modeling and parameter sensitivity. |
| Structural | Atomic coordinates, chains, residues, domains, ligands, and confidence. | Structural biology and molecular visualization. |
| Research | Papers, methods, experimental context, uncertainty, and competing models. | Specialist investigation and literature appraisal. |

Knowledge remains accessible across all lenses. Challenge profiles adjust constraints and scenario complexity independently from explanatory depth.

## Scientific integrity

Each mechanic binds to source records and declares its representation class:

- Experimental structure or measurement.
- Curated database annotation.
- Computational prediction.
- Primary literature claim.
- Educational representation.
- Gameplay abstraction.

The interface labels simplified or aggregated mechanics and links to the supporting source. Uncertainty and alternative models remain visible in specialist lenses.

## Content production

The iJEP Studio channel seeds topic discovery and visual grammar. Each candidate episode becomes a content record with timestamps, scientific entities, linked structures, literature, and rights metadata. The game creates original art and animation from approved source data and its own production pipeline. External media remains a cited reference unless its license grants the intended use.

## Prototype engine decision

The engine decision follows a short vertical-slice comparison. Evaluate Godot, Unity, Unreal, and browser-first runtime candidates against Android/web targets, molecular rendering, asset import, scripting, deterministic tests, build automation, accessibility, and license requirements. Record the selected version and export templates in the project profile.

## Initial acceptance

- A playable membrane scene exposes pump, channel, and ATP synthase state.
- Player actions change a deterministic simulation state.
- The UI explains the causal result at Field and Mechanism lenses.
- Quantitative and Structural lenses expose linked data and provenance.
- Research lens opens source records and method context.
- Accessibility review validates text alternatives, input flexibility, and motion controls.
- QA reproduces the scenario from a clean build and pinned source fixture.
