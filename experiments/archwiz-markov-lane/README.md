# ArchWiz Markov Trellis Sandbox

This directory is intentionally isolated from production routing and the context-relationship graph.

## Files

- index.html — interactive canvas sandbox.
- src/markov-engine.mjs — deterministic Markov/tree/trellis model.
- src/markov-engine.test.mjs — Node-native invariant tests.
- src/archwiz-markov-trellis.jsx — React/SVG reference implementation for later UI integration.

## Model contract

The transition matrix is the source of truth. The UI consumes computed node probabilities and provenance; it does not invent weights.

Strict tree:
- each transition creates a new path occurrence.

Recombining trellis:
- equivalent (time,state) occurrences merge;
- node probability is the sum of all incoming path probabilities;
- incoming edges retain their individual contribution.

Monte-Carlo particles:
- sampled from the same transition matrix;
- deterministic tests inject a seeded/random callback.

## Run

    python3 -m http.server 4173 --directory experiments/archwiz-markov-lane

Then open http://localhost:4173/.

    node experiments/archwiz-markov-lane/src/markov-engine.test.mjs
