# ArchWiz Markov Recombining Trellis Lab

A deliberately isolated implementation/evaluation lane for the Markov visualization architecture supplied from Gemini.

## Three views

1. Strict tree — every path occurrence remains distinct; useful for path-level provenance and illustrating exponential expansion.
2. Recombining trellis — equivalent (time,state) occurrences merge; node probability is the sum of incoming path probabilities.
3. Collapsed transition graph — optional future surface for long-horizon/state-machine inspection.

## Invariants

- Transition probabilities are data, not display labels.
- Outgoing transition rows are normalized and validated.
- Path probability is the product of transitions along the path.
- Recombined node probability is the sum of all incoming path probabilities.
- Total probability per time layer is conserved for a closed stochastic system.
- Particle flow samples transitions from the same matrix used by the model.
- Provenance is retained separately from aggregate probability.

## Gemini lane

After the PR is opened, request an explicit @gemini-cli /review focused on probability semantics, tree/DAG equivalence, visualization failure modes, interaction architecture, test gaps, accessibility, and performance.

Gemini feedback is recorded as external review evidence, not runtime authority.

## Run

From the repository root:

    python3 -m http.server 4173 --directory experiments/archwiz-markov-lane

Then open http://localhost:4173/.

Run deterministic model tests:

    node experiments/archwiz-markov-lane/src/markov-engine.test.mjs
