# RFP: BLU View 5 Mobile-First Interface Evaluation

- Status: OPEN FOR INDEPENDENT CONSIDERATION
- Track: parallel research / design evaluation
- Target device: BLU View 5, model B160V
- Evaluation class: mobile-first, touch-first, portrait baseline
- Relationship to implementation: independent proposal; no merge or implementation authority

## 1. Purpose

Solicit independent, evidence-backed design and engineering proposals for the project's mobile interface, using the BLU View 5 (B160V) as the primary physical-device target.

This RFP runs concurrently with the existing implementation and visualization work. Its output is a comparable proposal package, not an instruction to interrupt, replace, or silently fold in the active implementation.

## 2. Priority clarification

**Mobile is the primary design target.** Keyboard and desktop-specific UI are separate surfaces and are explicitly non-priority for this evaluation. Do not optimize the information architecture around desktop keyboard navigation, keyboard shortcuts, or wide-screen layouts.

The interface must be usable by touch on a handheld phone. Desktop may remain a responsive secondary surface, but it must not drive mobile layout decisions.

## 3. Target device facts and assumptions

The BLU product page identifies the View 5 display as 6.56-inch IPS, 720 × 1612 pixels, 20:9, approximately 270 ppi; it lists 3 GB RAM and a MediaTek Helio A22 quad-core processor. The Total Wireless B160V support page independently reports 720 × 1612 resolution and device dimensions.

- Native panel: 720 × 1612 physical pixels
- Aspect ratio: 20:9 (portrait)
- Approximate logical design baseline: 360 × 806 CSS px at DPR 2, **to be verified on the actual handset/browser**
- Memory/compute: 3 GB RAM; Helio A22 class device
- Browser viewport, display cutouts, system bars, font scale, installed browser and Android version: measure on device; do not assume from panel resolution.

References:
- BLU official device specification: https://www.bluproducts.com/devices/view-5/index.html
- B160V carrier support specification: https://support.totalwireless.com/en/brands/Blu/TVBLB160VC/

Where sources differ on OS revision or other device details, report the observed handset values and cite the source; do not silently infer.

## 4. Evaluation scope

Evaluate the mobile experience for the project's relevant graph, topology, research, operational cockpit and visualization workflows, including (where present):

1. Context Relationship Graph browsing and node/edge inspection.
2. Orbital Syntax / topology visualization and navigation.
3. SHE-style status, evidence and operational summaries.
4. Research and proposal discovery.
5. Drill-down from overview to source/provenance and back.
6. Loading, partial-data, empty, error, offline/slow-network and recovery states.

The RFP does not prescribe a particular visualization library or mandate D3/SVG/canvas. Compare suitable options and explain trade-offs against the actual use cases and handset constraints.

## 5. Design and engineering requirements

### P0 — usability and correctness
- Portrait-first, touch-first information architecture.
- Critical actions reachable without precision gestures.
- Touch targets sized and spaced for reliable thumb interaction; state the chosen target standard.
- Clear hierarchy, readable labels and legible data at the target viewport.
- No essential information available only on hover, keyboard shortcut or desktop pointer behavior.
- Preserve source identity, provenance, confidence and partial/unknown semantics.
- Never render missing/unknown values as zero or imply partial data is complete.
- Provide a usable non-graph/list representation when a graph is dense, inaccessible or too expensive to render.
- Respect device safe areas, system bars and virtual navigation insets.

### P1 — performance and resilience
- Measure initial render, interaction latency, memory pressure and scroll performance on the B160V.
- Define node/edge thresholds and graceful degradation for graph density.
- Avoid unnecessary animation, continuous simulation and expensive layout recalculation.
- Consider reduced motion, low-power operation and low-bandwidth loading.
- Prefer progressive disclosure, bounded data windows and lazy detail loading.
- Keep the UI functional when optional visual enhancements or data providers fail.

### P2 — responsive extension
- Document how the mobile model extends to tablet and desktop without making desktop the design authority.
- Treat keyboard-specific navigation and desktop UI as a separate future lane, outside this RFP's priority.

## 6. Independent consideration lanes

Each reviewer/team should work independently and submit its own findings before seeing other proposals where practical.

- **Lane A — UX / interaction:** mobile information architecture, thumb reach, navigation, density and task completion.
- **Lane B — visualization engineering:** SVG vs Canvas vs WebGL vs hybrid; D3 hierarchy/layout; graph interaction, hit testing and progressive rendering.
- **Lane C — performance / device constraints:** real-device profiling on B160V, memory/CPU, thermal/battery, frame pacing and degradation.
- **Lane D — accessibility / legibility:** touch accessibility, contrast, text scaling, screen-reader semantics, reduced motion and alternatives to spatial-only graph reading.
- **Lane E — architecture / integration:** component boundaries, data contracts, provenance, URL/deep-link state, offline behavior and compatibility with existing project architecture.
- **Lane F — adversarial review:** identify hidden assumptions, failure modes, over-engineering, accessibility regressions and test gaps.

Independent lanes must not coordinate toward a single answer before their first submissions. A lane may cite another lane's work only in a clearly marked second-pass critique.

## 7. Required proposal deliverables

Each submission must include:

1. Executive recommendation and explicit non-recommendations.
2. Evidence and source links; separate measured facts from assumptions and opinions.
3. At least three mobile task journeys, with failure/empty/partial-data states.
4. Annotated mobile wireframes or implementation-neutral screen descriptions.
5. A rendering/interaction architecture recommendation with alternatives considered.
6. B160V test protocol and actual measurements where hardware is available.
7. Performance budgets and testable acceptance criteria.
8. Accessibility and data-integrity review.
9. Risks, unknowns, dependencies and implementation cost/complexity.
10. A proposed phased rollout and rollback strategy.
11. A compatibility matrix against existing project concepts and components.
12. A machine-readable comparison summary using the schema below.

### Comparison summary schema

```json
{
  "proposal_id": "lane-a-ux",
  "lane": "ux-interaction",
  "target_device": "BLU View 5 B160V",
  "viewport_css_px": {"width": null, "height": null},
  "device_measurement": false,
  "recommendation": "",
  "alternatives": [],
  "performance_evidence": [],
  "accessibility_findings": [],
  "data_integrity_findings": [],
  "risks": [],
  "confidence": "low",
  "unknowns": [],
  "compatibility": [],
  "estimated_effort": null
}
```

Do not fabricate device measurements. Use null where evidence is unavailable.

## 8. Evaluation and fold-in protocol

After independent submissions are complete, compare proposals against a common rubric:

| Dimension | Weight |
|---|---:|
| Mobile task success / usability | 25 |
| Correctness, provenance and partial-data semantics | 20 |
| Real-device performance and resilience | 20 |
| Accessibility and legibility | 15 |
| Architecture and interoperability | 10 |
| Maintainability and delivery risk | 10 |
| **Total** | **100** |

Scores must include evidence and confidence; weights are a decision aid, not an automatic acceptance threshold.

The later synthesis must classify each proposal item as:
- ADOPT — fold into active implementation with a traceable issue/PR.
- ADAPT — retain the concept but modify it for compatibility.
- EXPERIMENT — prototype behind an isolated branch/feature flag.
- DEFER — useful, but not currently justified.
- REJECT — explain the evidence and reason.

No proposal is automatically merged or promoted by its score. Quality, data correctness and user task success outrank novelty or visual complexity.

## 9. Acceptance criteria

The RFP evaluation is complete only when:
- Every lane submits a distinct, reviewable artifact or explicitly records why it could not.
- Device measurements are clearly distinguished from estimates.
- At least one proposal tests the actual B160V or documents hardware unavailability.
- Proposals address graph and non-graph representations.
- A common comparison matrix is populated.
- Conflicts and unresolved unknowns are recorded.
- A separate fold-in decision identifies exact files/components and validation needed.
- The active implementation remains undisturbed until a deliberate integration decision.

## 10. Explicit exclusions

- Desktop keyboard-first redesign.
- Keyboard shortcut optimization.
- Desktop-specific navigation as a P0 requirement.
- Unbounded graph rendering or decorative animation without task value.
- Replacing existing architecture solely for novelty.
- Treating mockup-only success as proof of B160V runtime performance.
- Automatic merging, promotion or implementation of independent recommendations.

## 11. Coordination

This RFP is a parallel consideration track. The existing mobile/visualization implementation continues independently. The trigger issue requests independent submissions and later comparison; it does not authorize destructive changes to active branches or require reviewers to converge prematurely.
