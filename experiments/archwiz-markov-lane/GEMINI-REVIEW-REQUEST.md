# Gemini adversarial review request

Context: ArchWiz Markov Recombining Trellis Lab, issue #966.

Review only this experimental lane. Do not propose coupling it to production routing unless a concrete boundary and migration test are specified.

## Questions
1. Are strict-tree and recombining-trellis probability semantics implemented correctly?
2. Does the recombination identity (time,state) preserve enough provenance for debugging and audit?
3. Which visual encodings are misleading or likely to create false probability interpretations?
4. What edge/node layout changes would improve large-horizon readability?
5. Where are the current performance bottlenecks for particle flow and rendering?
6. What deterministic tests are missing?
7. What accessibility or interaction problems should be addressed before any production consideration?
8. Identify the smallest high-value next improvements and any implementation risks.

Return concrete findings grouped as MUST-FIX, SHOULD-FIX, EXPERIMENT, and NO-ACTION. Cite the relevant file/path and line or symbol where possible.

This is a review/research request, not an instruction to modify production architecture.