# Orbital Syntax — source and research basis

## User-provided design seed

The supplied screenshots describe a circular/radial layout with:
- a central focal region;
- concentric rings representing nested system/data states;
- polar partitions for peripheral scanning;
- curved/vector baselines;
- a suggested minimum inner radius of 120 px for monospaced text;
- an "optimal recognition point" (ORP) and foveal anchoring concept.

These are design hypotheses from the supplied concept, not validated ergonomic thresholds. The 120 px value is retained as a test parameter, not a normative requirement.

## Related implementation context

The repository already has:
- SHE's read-only projection model and versioned snapshots;
- a Relationships surface contract with pan/zoom, search, confidence/time/type filters, neighborhood expansion, and evidence inspection;
- an Architecture surface based on authoritative Mermaid source and generated render assets;
- a context-relationship graph with verified/candidate distinctions;
- a separate ArchWiz Markov trellis visualization proposal.

This lane does not duplicate or supersede those systems. It explores an alternative geometric encoding for selected hierarchical information.

## Inspiration consideration list

1. Envisioning.io — DefTech 2015 Foresight Radar: https://radar.envisioning.io/deftech_2015
   - Added at the user's request as a strategic/design inspiration reference, connected to their prior work with deftech.ch.
   - Consider its foresight-radar framing when exploring how to organize emerging-technology signals, categories, relationships, and time horizons. This is an inspiration prompt, not a claim that the original radar's data, methodology, or implementation has been inspected or validated for this prototype.
   - Keep this reference distinct from technical implementation sources and from any future evidence-backed data inputs.

## External technical references

1. D3 hierarchy documentation: https://d3js.org/d3-hierarchy
   - D3's hierarchy module supports tree, cluster, partition, pack, and treemap layouts.
   - D3 tree coordinates can be interpreted as angle and radius for a radial layout; radial separation can be adjusted by depth.
2. W3C SVG 2: https://www.w3.org/TR/SVG2/
   - SVG supports scalable vector geometry and text on paths through `textPath`.
   - SVG text/path rendering is a rendering primitive, not evidence that curved text improves comprehension.
3. LightSpeedRead: https://lightspeedread.com/about
   - The linked product is an RSVP speed reader that presents words sequentially at a fixed focal location.
   - It is a related but different interaction model. Orbital Syntax instead presents a persistent spatial overview of hierarchical data; it must not claim to implement RSVP or inherit its efficacy claims.

## Key distinctions

| Concept | Meaning in this proposal |
|---|---|
| Orbital hierarchy | Persistent nested information shown by depth/rings |
| Polar partition | Angular allocation of sibling groups or categories |
| Foveal anchor | A stable central focus for the selected item or primary status |
| ORP | A candidate text alignment aid; not a validated guarantee |
| RSVP | Sequential word presentation at one location; outside this prototype's scope |
| SVG textPath | A rendering option for labels, not the default for dense text |

## Hypotheses to test

- H1: For some shallow, stable hierarchies, radial rings may reduce navigation between distant groups.
- H2: A center-selected detail panel plus peripheral context may improve orientation compared with a long flat list.
- H3: Dense labels, long identifiers, and many sibling nodes may make radial layouts worse than lists or trees.
- H4: The best layout may be hybrid: radial overview + straight baseline detail/list, not curved text everywhere.

## Non-claims

- No evidence currently establishes that this layout is faster than conventional grids or lists.
- No evidence currently establishes that peripheral vision can reliably parse arbitrary tags before eye movement.
- No 120 px inner-radius rule is accepted as a universal typography constraint.
- No reading-speed, comprehension, accessibility, or eye-tracking result is claimed.

## Privacy and runtime

The prototype uses hard-coded illustrative sample data, no analytics, no remote fonts, no external JavaScript, no uploads, and no network calls. A future reader/import feature would require a separate privacy and threat-model review.
