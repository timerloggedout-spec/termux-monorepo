# DoE Taxonomy — Terminology Discipline + Design Classes

Mined 2026-10-27 from an external collaborator research export
(Perplexity, `Research_Multivariate_Testing__amp__amp__Design_Of_1_56zt.md`,
592 lines; NIST/SEMATECH e-Handbook + Microsoft experimentation sources
underneath it). **Input, not evidence**: every claim below was
cross-checked against `deepcli/deepcli/observatory/doe.py` and
`.agents/skills/multivariate-doe/SKILL.md` before landing here; the
verification status is stated per item. Family context:
`docs/ops/DOE-FAMILY.md` (#1865).

## Terminology discipline — related concepts, NOT synonyms

| Concept | What varies / is measured | Status in repo |
|---|---|---|
| DoE | The umbrella discipline: choosing informative treatments efficiently | Skill + doe.py — verified |
| MVT (multivariate testing) | Multiple **input factors** varied in combination (product/UX application of multifactor design) | Skill terminology — verified, consistent |
| Factorial experiment | Combinations of factor levels; estimates main effects + interactions | doe.py `full_factorial` — verified |
| Multivariate-**outcome** analysis | Multiple **response variables** measured per unit (multiresponse / MANOVA territory) | **Was unnamed in the skill** — the skill's outcome model is multiresponse in practice (primary + secondary outcomes) but never distinguished it from MVT. Delta landed in the skill terminology (this PR) |
| ANOVA | Analysis method partitioning response variation — **not a design** | Neither skill nor doe.py claims otherwise — verified no conflict |
| RSM (response surface methodology) | Quantitative factors + curvature; local optimization | Named nowhere in repo — candidate, see taxonomy |
| OFAT (one-factor-at-a-time) | One factor moves, rest fixed; cannot systematically identify interactions | Not named in skill — taxonomy entry only; the family's factorial practice already supersedes it |
| A/B test | Two packaged versions; establishes a package effect, not component contributions | Skill via RCT entry — consistent |

Rule the export states and the family adopts: **"multivariate" names
inputs in MVT and outputs in multivariate-outcome analysis. Never use
one for the other.** A campaign with many factors and one response is
MVT; a campaign with one treatment and many responses is a
multivariate-outcome analysis; a campaign can be both — say which.

## Design-class taxonomy (candidate family members beyond MVT)

Status key: **implemented** = generator exists in doe.py ·
**skill-named** = the skill names it, no generator · **candidate** =
neither; admission = a doe.py generator + tests, then it joins the
family's design-classes member (intake rule applies to classes too:
a named class with no generator is design-vocabulary, not a member).

| Design class | Purpose | Status |
|---|---|---|
| Full factorial | All combinations; main effects + interactions; small k only (2^k growth) | **implemented** (`full_factorial`) — used by pilot 1 |
| Fractional factorial | Structured subset under run budget; some effects aliased — resolution + assumptions must be declared | skill-named ("fractional factorial / screening") — no generator |
| Orthogonal array / Taguchi L9 | Balanced factor-level coverage, ≤4 factors × 3 levels | **implemented** (`taguchi_l9`) — note: an L9 *is* a fractional design; doe.py does not say so (doc delta noted on #1865) |
| Plackett–Burman screening | Many factors, main effects only, economical | skill-named — no generator |
| Foldover augmentation | Follow-up runs that de-alias a screening result | candidate — named in neither |
| Central composite (CCD) | Quadratic response surface after screening | candidate |
| Box–Behnken | Quadratic modeling, several quantitative factors, no corner points | candidate |
| RSM (as a program) | Screen → surface → confirm, for quantitative-factor optimization | candidate — the skill's adaptive sequence (screen → expand → replicate → validate → promote/cull) is its qualitative analogue |
| Randomized assignment | `mvt_shuffle` — an **assignment mechanism, not a design class** | **implemented** — reclassified here; DOE-FAMILY previously listed it under design classes (corrected, this PR) |
| Sequential / adaptive | Evidence-driven allocation with predeclared stopping | skill-named (adaptive design section) — no generator |
| Randomized block | Group similar units, randomize within blocks | implemented as practice (pilot 1 blocked by task family × stratum); no generator needed |
| Mixture | Proportions summing to a fixed total (e.g. quota shares) | candidate — natural fit for pilot-2-class quota-policy designs |
| Split-plot | Hard-to-change factors get a different randomization level | candidate — relevant to dispatch-topology designs (policy levels are hard to change per-run) |
| Latin hypercube | Space-filling for simulation / continuous parameter exploration | candidate — coverage ≠ factorial effect estimation; do not substitute |

## Workflow deltas from the export — verified against repo practice

1. **Assignment-integrity / SRM gate** — export §4: check observed vs
   planned allocation before trusting effects. **Already repo doctrine**:
   framework proposal §2 maps it to the #1596 reconciliation fan;
   pilot 2's design names the same gate. No delta.
2. **Replication ≠ repeated runs** — export §5: repeated executions of
   one task and independently sampled tasks answer different questions.
   Framework §3 already states it for dispatch (repeated wakes =
   repeated measures). Pilot 1's replication is across tasks (8 per
   arm); its records' cohort field carries the block, and SUMMARY now
   reports per-arm spread (`accuracy_sd`) — see delta 3.
3. **No effect claim without uncertainty** — export §3: a
   difference-of-differences is not a significance test. Pilot 1's
   SUMMARY originally reported cell means + effects only. **Delta
   landed (this PR)**: runner emits per-arm `accuracy_sd`; effects
   remain descriptive — no significance is claimed for n=8 tasks/arm.
4. **Center points / curvature budget** — export §4 (NIST): retain
   budget for center points + reruns; two-level designs cannot detect
   curvature. **Not in the skill's 12 rules and not in family
   doctrine — flagged on #1865 as a proposed rule 13**, not silently
   adopted: it binds only designs with quantitative factors, which no
   family campaign has run yet.
5. **Selection by objective** — export §2 map (compare / screen /
   interactions / optimize / proportions / parameter-space). Adopted
   as the taxonomy's organizing principle above; NIST objective-first
   selection, not tool-first.

## Conflicts found

- **C1 (minor, corrected)**: DOE-FAMILY listed `mvt_shuffle`
  (randomized assignment) among "design classes". Assignment is a
  mechanism a design uses, not a class. Corrected in DOE-FAMILY.md.
- **C2 (gap, landed)**: skill terminology conflated the two senses of
  "multivariate" by omission — multivariate-outcome analysis unnamed.
  Terminology entry added to the skill.
- **C3 (documentation)**: `taguchi_l9` docstring does not state L9 is
  a fractional orthogonal-array design with aliased interactions —
  noted here + on #1865; doe.py docstring fix is a follow-up, not
  bundled, to keep this PR docs+summary only.
- No conflict: export's MVT / factorial / ANOVA / OFAT definitions vs
  skill terminology and doe.py behavior agree everywhere else checked.
